import os
import logging
from dataclasses import dataclass
from typing import Dict, Union, Tuple, List, Any, Optional

import h5py
import numpy
from pint import Quantity
from numpy.typing import DTypeLike

from .hdf5 import join_h5url
from .hdf5 import split_h5uri
from ..units import unit_registry
from ..units import units_as_str
from ..math.expression import expression_variables
from ..math.expression import eval_expression


logger = logging.getLogger(__name__)


def concatenate_bliss_scans(
    bliss_scan_uris: List[str],
    output_root_uri: str,
    virtual_axes: Optional[Dict[str, str]] = None,
    axes_units: Optional[Dict[str, str]] = None,
    start_var: str = "<",
    end_var: str = ">",
) -> str:
    """Concatenate Bliss scans in a virtual scan that looks exactly like a Bliss scan.

    This method cannot handle scans that are interrupted, except when it is the last scan to be concatenated.

    :param bliss_scan_uris: scans to concatenate
    :param virtual_axes: virtual motors. For example `{"sy": "<samy>+<sampy>/1000", "sz": "<samz>+<sampz>/1000"}`
    :param axes_units: axis units. For example `{"samy": "mm", "sampy": "um"}`
    :param start_var: marks the start of a variable name in `virtual_axes` expressions
    :param end_var: marks the end of a variable name in `virtual_axes` expressions
    :returns: URI to the virtual concatenated scan
    """
    if axes_units is None:
        axes_units = dict()

    out_filename, out_path = split_h5uri(output_root_uri)
    if not out_path:
        out_path = "/1.1"
        output_root_uri = join_h5url(out_filename, out_path)

    # Return when out_path already exists
    with h5py.File(out_filename, mode="a") as out_root:
        if out_path in out_root:
            logger.warning("%s already exists", output_root_uri)
            return output_root_uri

    # Compile data to concatenate
    in_scan = None
    datasets = None
    for bliss_scan_uri in bliss_scan_uris:
        logger.debug("Parse %s for concatenation", bliss_scan_uri)
        in_filename, in_path = split_h5uri(bliss_scan_uri)
        with h5py.File(in_filename, mode="r", locking=False) as in_root:
            in_scani = in_root[in_path]
            if in_scan is None:
                in_scan, datasets = _parse_hdf5_group(in_scani)
            else:
                _append_H5Datasets(in_scani, datasets)

    logger.debug("Save concatenation in %s", output_root_uri)

    scalar_repeats = _trim_datasets(datasets)

    with h5py.File(out_filename, mode="a") as out_root:
        out_scan = out_root.create_group(out_path)
        _save_hdf5_group(out_scan, in_scan, scalar_repeats)

    if virtual_axes:
        virtual_axis_datasets = _add_virtual_axes(
            in_scan, virtual_axes, axes_units, start_var=start_var, end_var=end_var
        )

        with h5py.File(out_filename, mode="r") as out_root:
            out_scan = out_root[out_path]
            for item in virtual_axis_datasets:
                _resolve_virtual_axis(item, out_scan, axes_units)

        with h5py.File(out_filename, mode="a") as out_root:
            out_scan = out_root[out_path]
            _save_hdf5_group(out_scan, in_scan, scalar_repeats, skip_existing=True)

    return output_root_uri


@dataclass
class _H5SoftLink:
    path: str
    relative: bool


@dataclass
class _H5VirtualSource:
    filename: str
    data_path: str
    shape: Tuple[int]
    dtype: DTypeLike
    force_shape0: Optional[int] = None

    @property
    def layout_shape(self) -> Tuple[int]:
        if self.force_shape0 is None:
            return self.shape
        return (self.force_shape0,) + self.shape[1:]

    def get_layout_h5item(self, filename: str) -> h5py.VirtualSource:
        ext_filename = os.path.relpath(self.filename, os.path.dirname(filename))
        return h5py.VirtualSource(
            ext_filename, self.data_path, shape=self.shape, dtype=self.dtype
        )


@dataclass
class _H5Item:
    attrs: dict


@dataclass
class _H5Group(_H5Item):
    items: Dict[str, Union[_H5Item, _H5SoftLink]]


@dataclass
class _H5Dataset(_H5Item):
    value: Any


@dataclass
class _H5DatasetExpression(_H5Item):
    expression: str
    units: str
    start_var: str = "<"
    end_var: str = ">"
    result: Optional[Quantity] = None


@dataclass
class _H5ScalarDataset(_H5Item):
    values: List[numpy.number]


@dataclass
class _VirtualDataset(_H5Item):
    sources: List[_H5VirtualSource]

    @property
    def dtype(self) -> DTypeLike:
        return self.sources[0].dtype

    @property
    def shape(self) -> Tuple[int]:
        s0 = sum(source_scani.layout_shape[0] for source_scani in self.sources)
        sother = self.sources[0].layout_shape[1:]
        return (s0,) + sother

    @property
    def __len__(self) -> int:
        return self.shape[0]


def _parse_hdf5_group(
    parent: h5py.Group, _name_prefix_strip: int = 0
) -> Tuple[_H5Group, Dict[str, Union[_VirtualDataset, _H5ScalarDataset]]]:
    if _name_prefix_strip <= 0:
        _name_prefix_strip = len(parent.name) + 1
    filename = parent.file.filename
    items = dict()
    group = _H5Group(attrs=dict(parent.attrs), items=items)
    datasets = dict()
    for name in parent:
        link = parent.get(name, getlink=True)
        if isinstance(link, h5py.HardLink):
            child = parent.get(name)
            if isinstance(child, h5py.Dataset):
                if numpy.issubdtype(child.dtype, numpy.number):
                    if child.ndim == 0:
                        values = [child[()]]
                        dataset = _H5ScalarDataset(
                            attrs=dict(child.attrs), values=values
                        )
                    else:
                        sources = [
                            _H5VirtualSource(
                                filename=filename,
                                data_path=child.name,
                                shape=child.shape,
                                dtype=child.dtype,
                            )
                        ]
                        dataset = _VirtualDataset(
                            attrs=dict(child.attrs), sources=sources
                        )
                    key = child.name[_name_prefix_strip:]
                    datasets[key] = dataset
                    items[name] = dataset
                else:
                    value = child[()]
                    if isinstance(value, bytes):
                        value = value.decode()
                    items[name] = _H5Dataset(attrs=dict(child.attrs), value=value)
            elif isinstance(child, h5py.Group):
                if child.attrs.get("NX_class", "") == "NXdata":
                    continue
                items[name], sub_H5Datasets = _parse_hdf5_group(
                    child, _name_prefix_strip=_name_prefix_strip
                )
                datasets.update(sub_H5Datasets)
            else:
                logger.warning(
                    f"ignore HDF5 item {parent.name}/{name} for concatenation ({type(child)})"
                )
        elif isinstance(link, h5py.SoftLink):
            if link.path.startswith("/"):
                items[name] = _H5SoftLink(
                    path=link.path[_name_prefix_strip:], relative=False
                )
            else:
                items[name] = _H5SoftLink(path=link.path, relative=True)
        else:
            logger.warning(
                f"ignore HDF5 link {parent.name}/{name} for concatenation ({type(link)})"
            )
    return group, datasets


def _append_H5Datasets(
    group: h5py.Group, datasets: Dict[str, Union[_VirtualDataset, _H5ScalarDataset]]
) -> None:
    filename = group.file.filename
    for name, dataset in datasets.items():
        child = group[name]
        if isinstance(dataset, _H5ScalarDataset):
            dataset.values.append(child[()])
        else:
            dataset.sources.append(
                _H5VirtualSource(
                    filename=filename,
                    data_path=child.name,
                    shape=child.shape,
                    dtype=child.dtype,
                )
            )


def _trim_datasets(
    datasets: Dict[str, Union[_VirtualDataset, _H5ScalarDataset]],
) -> List[int]:
    dataset_names, dataset_lengths = _dataset_lengths_per_scan(datasets)

    min_dataset_lengths = list()

    for scan_index, dataset_lengths_scani in enumerate(dataset_lengths):
        min_dataset_length_scani = min(dataset_lengths_scani)
        min_dataset_lengths.append(min_dataset_length_scani)

        for dataset_name in dataset_names:
            vsource_scani = datasets[dataset_name].sources[scan_index]
            vsource_scani.force_shape0 = min_dataset_length_scani

        # Even if you have know the logic of a dataset length, for example
        #
        #   dataset_length = (nfast+1) * nslow
        #
        # I would not know how to trim it so just trim to obtain an equal number of points.

    return min_dataset_lengths


def _dataset_lengths_per_scan(
    datasets: Dict[str, Union[_VirtualDataset, _H5ScalarDataset]],
) -> Tuple[List[str], List[List[int]]]:
    """
    :returns: dataset names with shape `(ndatasets,)` and dataset lengths with shape `(nscans, ndatasets)`
    """
    dataset_lengths = list()
    dataset_names = list()
    for name, dataset in datasets.items():
        if not isinstance(dataset, _VirtualDataset):
            continue
        dataset_names.append(name)
        if dataset_lengths:
            for source_scani, dataset_lengths_scani in zip(
                dataset.sources, dataset_lengths
            ):
                dataset_lengths_scani.append(source_scani.shape[0])
        else:
            dataset_lengths = [
                [source_scani.shape[0]] for source_scani in dataset.sources
            ]
    return dataset_names, dataset_lengths


def _save_hdf5_group(
    group: h5py.Group,
    structure: _H5Group,
    scalar_repeats: List[int],
    skip_existing: bool = False,
    _name_prefix: str = "",
) -> None:
    filename = group.file.filename
    group.attrs.update(structure.attrs)
    if not _name_prefix:
        _name_prefix = group.name
    for name, item in structure.items.items():
        skip_item = skip_existing and name in group

        if isinstance(item, _H5Group):
            if skip_item:
                subgroup = group[name]
            else:
                subgroup = group.create_group(name)
            _save_hdf5_group(
                subgroup,
                item,
                scalar_repeats,
                skip_existing=skip_existing,
                _name_prefix=_name_prefix,
            )
            continue

        if skip_item:
            continue

        if isinstance(item, _H5SoftLink):
            if item.relative:
                group[name] = h5py.SoftLink(item.path)
            else:
                group[name] = h5py.SoftLink(f"{_name_prefix}/{item.path}")
        elif isinstance(item, _H5Dataset):
            group[name] = item.value
            group[name].attrs.update(item.attrs)
        elif isinstance(item, _H5ScalarDataset):
            if len(set(item.values)) > 1:
                # No longer a scalar dataset
                group[name] = numpy.repeat(item.values, scalar_repeats)
            else:
                group[name] = item.values[0]
            group[name].attrs.update(item.attrs)
        elif isinstance(item, _VirtualDataset):
            layout = h5py.VirtualLayout(shape=item.shape, dtype=item.dtype)
            start_index = 0
            for source_scani in item.sources:
                n = source_scani.layout_shape[0]
                vsource = source_scani.get_layout_h5item(filename)
                layout[start_index : start_index + n] = vsource[:n]
                start_index += n
            group.create_virtual_dataset(name, layout, fillvalue=numpy.nan)
            group[name].attrs.update(item.attrs)
        elif isinstance(item, _H5DatasetExpression):
            if item.result is None:
                continue
            group[name] = item.result.magnitude
            if not item.result.units.dimensionless:
                group[name].attrs["units"] = units_as_str(item.result.units)
        else:
            logger.debug(f"ignore HDF5 item {name} for saving ({type(item)})")


def _ensure_same_shape0(
    variables: Dict[str, numpy.ndarray], name_map: Dict[str, str]
) -> None:
    npoints = dict()
    for key, values in variables.items():
        if values.ndim >= 1:
            npoints[key] = len(values)
    if len(set(npoints.values())) <= 1:
        return
    npoints_min = min(npoints.values())
    for key, npoints_orig in npoints.items():
        logger.warning(
            "trim '%s' from %d points to %d", name_map[key], npoints_orig, npoints_min
        )
        variables[key] = variables[key][:npoints_min]


def _add_virtual_axes(
    group: _H5Group,
    virtual_axes: Dict[str, str],
    axes_units: Dict[str, str],
    start_var: str = "<",
    end_var: str = ">",
) -> List[_H5DatasetExpression]:
    instrument = group.items["instrument"]
    measurement = group.items["measurement"]
    positioners = instrument.items["positioners"]

    datasets = list()
    for motor_name, expression in virtual_axes.items():
        motor_value = _H5DatasetExpression(
            attrs=dict(),
            expression=expression,
            units=axes_units.get(motor_name, ""),
            start_var=start_var,
            end_var=end_var,
        )
        instrument.items[motor_name] = _H5Group(
            attrs={"NX_class": "NXpositioner"}, items={"value": motor_value}
        )
        measurement.items[motor_name] = _H5SoftLink(
            f"instrument/{motor_name}/value", relative=False
        )
        positioners.items[motor_name] = _H5SoftLink(
            f"instrument/{motor_name}/value", relative=False
        )
        datasets.append(motor_value)
    return datasets


def _resolve_virtual_axis(
    item: _H5DatasetExpression, top_group: h5py.Group, axes_units: Dict[str, str]
) -> None:
    def get_data(name: str) -> Tuple[str, Quantity]:
        return _get_moving_values(
            top_group, name, axes_units.get(name, "") if axes_units else ""
        )

    expression, variables, name_map = expression_variables(
        item.expression, get_data, start_var=item.start_var, end_var=item.end_var
    )
    _ensure_same_shape0(variables, name_map)
    quantity = eval_expression(expression, variables)
    if item.units:
        quantity = quantity.to(item.units)
    item.result = quantity


def _get_moving_values(
    scan: h5py.Group, name: str, default_units: str
) -> Tuple[str, Quantity]:
    measurement = scan["measurement"]
    if name in measurement:
        full_name = f"{measurement.name}/{name}"
        values = _get_value_with_units(measurement[name], default_units)
        return full_name, values
    instrument = scan["instrument"]
    if name in instrument:
        group = instrument[name]
        if "value" in group:
            # NXpositioner
            full_name = f"{group.name}/value"
            values = _get_value_with_units(group["value"], default_units)
            return full_name, values
        else:
            # NXdetector
            full_name = f"{group.name}/data"
            values = _get_value_with_units(group["data"], default_units)
            return full_name, values
    positioners = instrument["positioners"]
    if name in positioners:
        full_name = f"{positioners.name}/{name}"
        values = _get_value_with_units(positioners[name], default_units)
        return full_name, values
    raise RuntimeError(f"'{name}' is neither a detector nor a positioner")


def _get_value_with_units(dset: h5py.Dataset, default_units: str) -> Quantity:
    units = dset.attrs.get("units", default_units)
    ureg = unit_registry()
    return dset[()] * ureg.parse_units(units)
