from numbers import Number
from typing import Iterator, Tuple, List, Optional, Any, Union
from contextlib import contextmanager
from datetime import datetime

import numpy
from numpy.typing import DTypeLike

from ..handlers import AbstractOutputHandler


class ExternalOutputBuffer:
    """This is an output buffer of an external output handler."""

    def __init__(
        self,
        output_handler: AbstractOutputHandler,
        diagnostics: bool = False,
        figuresofmerit: bool = False,
    ):
        self._output_handler = output_handler
        self._diagnostics = diagnostics
        self._figuresofmerit = figuresofmerit
        self._groups = dict()
        self._items = dict()
        self._has_allocated_memory = False

    @property
    def xrf_results_uri(self) -> Optional[str]:
        return self._output_handler.xrf_results_uri

    @property
    def output_root_uri(self) -> Optional[str]:
        return self._output_handler.output_root_uri

    @property
    def already_existed(self) -> bool:
        return self._output_handler.already_existed

    def __setitem__(self, groupname: str, value) -> None:
        if groupname == "configuration":
            data = {
                "@NX_class": "NXnote",
                "type": "text/plain",
                "data": value.tostring(),
                "date": datetime.now().astimezone().isoformat(),
            }
            self._output_handler.create_group(groupname, data=data)
        else:
            raise NotImplementedError(f"unexpected group '{groupname}'")

    def __getitem__(self, item: str) -> Union["_StackOfDatasets", "_Dataset"]:
        return self._items[item]

    @contextmanager
    def saveContext(self, **_) -> Iterator[None]:
        yield

    @contextmanager
    def Context(self, **_) -> Iterator[None]:
        yield

    @property
    def diagnostics(self) -> bool:
        return self._diagnostics

    @property
    def saveDataDiagnostics(self) -> bool:
        return self._diagnostics

    @property
    def saveFOM(self) -> bool:
        return self._figuresofmerit

    @saveFOM.setter
    def saveFOM(self, value) -> None:
        self._figuresofmerit = value

    @property
    def saveFit(self) -> bool:
        return self._diagnostics

    @property
    def saveData(self) -> bool:
        return self._diagnostics

    @property
    def saveResiduals(self) -> bool:
        return False

    def hasAllocatedMemory(self) -> bool:
        return self._has_allocated_memory

    def allocateMemory(
        self,
        name: str,
        shape: Optional[Tuple[int]] = None,
        dtype: Optional[DTypeLike] = None,
        data: Optional[numpy.ndarray] = None,
        fill_value: Number = numpy.nan,
        group: Optional[str] = None,
        labels: Optional[List[str]] = None,
        dataAttrs: Optional[dict] = None,
        **kw,
    ) -> Union[numpy.ndarray, List[numpy.ndarray]]:
        """
        :param name: name of the dataset when `group` is specified, name of the group otherwise
        :param group: name of the group
        :param labels: dataset names when `group` is specified, not used otherwise
        :param shape: total group shape when `group` is specified, dataset shape otherwise
        """
        if shape is None:
            shape = data.shape
        if dtype is None:
            dtype = data.dtype
        self._has_allocated_memory = True

        if group:
            # Allocate one dataset of one group
            dataset_shape = shape
            groupobj = self._groups.get(group)
            if groupobj is None:
                groupobj = _StackOfDatasets(
                    self._output_handler,
                    group,
                    dataset_shape=dataset_shape,
                    dtype=dtype,
                    dataAttrs=dataAttrs,
                    signals=list(),
                    **kw,
                )

            dependencies = ("model", "data")
            if name in dependencies:
                rdestobj = self._items.get("residuals")
                if rdestobj is None:
                    rdestobj = groupobj.add_residuals(shape=dataset_shape)
                    self._items["residuals"] = rdestobj
                if name == "data":
                    rattr = "a"
                else:
                    rattr = "b"
            else:
                rdestobj = None
                rattr = None
            dsetobj = groupobj.add_dataset(
                name,
                shape=dataset_shape,
                dtype=dtype,
                data=data,
                fill_value=fill_value,
                attrs=dataAttrs,
                redirect_dataset=rdestobj,
                redirect_attribute=rattr,
            )
            self._groups[group] = groupobj
            self._items[name] = dsetobj
            return dsetobj

        # Allocate several datasets of one group
        dataset_shape = shape[1:]
        groupobj = _StackOfDatasets(
            self._output_handler,
            name,
            dataset_shape=dataset_shape,
            dtype=dtype,
            dataAttrs=dataAttrs,
            signals=labels,
            **kw,
        )
        if data is None:
            data = [None] * len(labels)
        for label, ldata in zip(labels, data):
            groupobj.add_dataset(
                label,
                shape=dataset_shape,
                dtype=dtype,
                data=ldata,
                fill_value=fill_value,
                attrs=dataAttrs,
            )
        self._groups[name] = groupobj
        self._items[name] = groupobj
        return groupobj

    def labels(self, group: str) -> List[str]:
        return self._groups[group]._dataset_names


class _StackOfDatasets:
    def __init__(
        self,
        output_handler: AbstractOutputHandler,
        name: str,
        dataset_shape: Tuple[int],
        dtype: Optional[DTypeLike],
        groupAttrs: Optional[dict] = None,
        **_,
    ) -> None:
        self._output_handler = output_handler
        self._name = name

        if name in ("fit", "derivatives"):
            data = {"@NX_class": "NXdata"}
            for ax_name, ax_values, ax_attrs in groupAttrs["axes"]:
                if ax_name == "energy":
                    data["energy"] = ax_values
                    for aname, avalue in ax_attrs.items():
                        data[f"energy@{aname}"] = avalue
                    if name == "fit":
                        data["@axes"] = [".", "energy"]
                    else:
                        data["@axes"] = ["energy"]
                    break
            if name == "fit":
                data["@interpretation"] = "spectrum"
                data["@signal"] = "data"
                data["@auxiliary_signals"] = ["model", "residuals"]
        else:
            data = {"@NX_class": "NXdata"}

        self._output_handler.create_group(name, data=data)
        self._datasets: List[numpy.ndarray] = list()
        self._dataset_names: List[str] = list()
        self._shape = (0,) + dataset_shape
        self._dataset_shape = dataset_shape
        self._dataset_size = numpy.prod(dataset_shape, dtype=int)
        self._dtype = dtype

    def __str__(self) -> str:
        return f"StackOfDatasets('{self._name}', datasets={self._dataset_names})"

    @property
    def shape(self) -> Tuple[int]:
        return self._shape

    @property
    def dtype(self) -> Optional[Tuple[int]]:
        return self._dtype

    def __getitem__(self, idx) -> numpy.ndarray:
        if not isinstance(idx, Number):
            raise NotImplementedError
        return self._datasets[idx]

    def __setitem__(self, idx, value) -> None:
        if isinstance(value, Number):
            for idxg, idxd in self._iter_indices(idx):
                self._datasets[idxg][idxd] = value
        else:
            for (idxg, idxd), v in zip(self._iter_indices(idx), value):
                self._datasets[idxg][idxd] = v

    def _iter_indices(self, idx) -> Iterator[Tuple[int, Any]]:
        idxg = idx[0]
        idxd = idx[1:]
        if isinstance(idxg, slice):
            for i in range(*idxg.indices(len(self._datasets))):
                yield i, idxd
        else:
            yield idxg, idxd

    def add_dataset(
        self,
        name: str,
        shape: Tuple[int],
        dtype: DTypeLike,
        data: Optional[numpy.ndarray] = None,
        fill_value: Number = numpy.nan,
        attrs: Optional[dict] = None,
        redirect_dataset=None,
        redirect_attribute=None,
    ) -> numpy.ndarray:
        if self._name == "fit":
            scan_shape = shape[:-1]
            data_shape = shape[-1:]
        else:
            scan_shape = shape
            data_shape = tuple()
        dset = _Dataset(
            group=self._name,
            name=name,
            output_handler=self._output_handler,
            scan_shape=scan_shape,
            data_shape=data_shape,
            dtype=dtype,
            attrs=attrs,
            redirect_dataset=redirect_dataset,
            redirect_attribute=redirect_attribute,
        )

        if data is not None:
            dset[()] = data
        if not _skip_fill_value(fill_value):
            dset[()] = numpy.full(self._dataset_shape, fill_value)

        self._datasets.append(dset)
        self._dataset_names.append(name)
        self._shape = (self._shape[0] + 1,) + self._shape[1:]

        return dset

    def add_residuals(self, shape: Tuple[int]) -> "_SubtractDataset":
        npoints = numpy.prod(shape[:-1], dtype=int)
        return _SubtractDataset(
            group=self._name,
            name="residuals",
            output_handler=self._output_handler,
            npoints=npoints,
        )


class _Dataset:
    def __init__(
        self,
        group: str,
        name: str,
        output_handler: AbstractOutputHandler,
        scan_shape: Tuple[int],
        data_shape: Tuple[int],
        dtype: DTypeLike,
        attrs: Optional[dict] = None,
        redirect_dataset=None,
        redirect_attribute: Optional[str] = None,
    ) -> None:
        self._group = group
        self._name = name
        self._shape = scan_shape + data_shape
        self._ndim = len(self._shape)
        self._ndim_scan = len(scan_shape)
        self._ndim_data = len(data_shape)
        self._ndim_flat = self._ndim_data + 1
        self._scan_size = numpy.prod(scan_shape, dtype=int)
        self._data_size = numpy.prod(data_shape, dtype=int)
        self._scan_shape = scan_shape
        self._data_shape = data_shape
        self._dtype = dtype
        self._data_handler = output_handler.create_nxdata_handler(
            self._group, self._name, npoints=self._scan_size, attrs=attrs
        )
        self._npoints_added = 0
        self._redirect_dataset = redirect_dataset
        if redirect_dataset is not None:
            setattr(redirect_dataset, redirect_attribute, self)
        self._keep_in_memory = group == "parameters"
        if self._keep_in_memory:
            self._data = numpy.empty(self._shape, dtype=self._dtype)
        else:
            self._data = None

    def __str__(self) -> str:
        return f"Dataset('{self._group}/{self._name}')"

    @property
    def shape(self) -> Tuple[int]:
        return self._shape

    @property
    def dtype(self) -> Tuple[int]:
        return self._dtype

    @property
    def ndim(self) -> int:
        return self._ndim

    def __getitem__(self, idx: Tuple[slice]) -> numpy.ndarray:
        idx = _explicit_index(idx, self._shape)
        shape = _shape_from_index(idx)
        fidx = _flat_scan_index(idx, self._scan_shape)
        if fidx[0].stop > self._npoints_added:
            return numpy.empty(shape, dtype=self._dtype)
        raise NotImplementedError("editing allocated data is not supported")

    def __setitem__(self, idx: Union[Union[slice, Number], Number], value) -> None:
        if self._keep_in_memory:
            self._data[idx] = value

        if _skip_fill_value(value):
            # This is not the result of a fit. This is pymca filling
            # idx with empty values.
            return

        # Flatten the scan dimension
        idx = _explicit_index(idx, self._shape)
        idx = _flat_scan_index(idx, self._scan_shape)
        value = numpy.asarray(value)
        scan_slice_size = numpy.prod(value.shape[: self._ndim_scan], dtype=int)
        data_shape = value.shape[self._ndim_scan :]
        shape = (scan_slice_size,) + data_shape
        value = value.reshape(shape)

        # Add missing dimensions
        nextra = self._ndim_flat - value.ndim
        if nextra:
            value = value[(numpy.newaxis,) * nextra]

        # Pad data dimension
        if data_shape != self._data_shape:
            if numpy.issubdtype(value.dtype, numpy.integer):
                fill_value = 0
            else:
                fill_value = numpy.nan
            pad_width = [[0, 0]] + [
                [slc.start, n - slc.stop] for slc, n in zip(idx[1:], self._data_shape)
            ]
            value = numpy.pad(value, pad_width, constant_values=fill_value)

        if self._group == "derivatives":
            # Pad scan dimension, which is actually the data dimension
            if numpy.issubdtype(value.dtype, numpy.integer):
                fill_value = 0
            else:
                fill_value = numpy.nan
            assert self._ndim_data == 0
            pad_width = [[idx[0].start, self._scan_size - idx[0].stop]]
            value = numpy.pad(value, pad_width, constant_values=fill_value)
            idx0 = slice(0, self._scan_size)
        else:
            idx0 = idx[0]

        # Add data points to the writer
        if idx0.start != self._npoints_added:
            raise NotImplementedError("data from pymca must be added subsequently")
        self.add_points(value)

    def add_points(self, value: numpy.ndarray) -> None:
        self._data_handler.add_points(value)
        self._npoints_added += value.shape[0]
        if self._redirect_dataset is None:
            return
        self._redirect_dataset.add_points(value, self)

    def __lt__(self, value):
        return self._data < value

    def __rmul__(self, value):
        return self._data * value


class _SubtractDataset:
    def __init__(
        self,
        group: str,
        name: str,
        output_handler: AbstractOutputHandler,
        npoints: int,
    ):
        self._group = group
        self._name = name
        self.a = None
        self.b = None
        self._a_data = list()
        self._b_data = list()
        self._data_handler = output_handler.create_nxdata_handler(
            self._group, self._name, npoints=npoints
        )

    def __str__(self) -> str:
        return f"SubtractDataset('{self._group}/{self._name}')"

    def add_points(self, value: numpy.ndarray, source: _Dataset) -> None:
        if source is self.a:
            self._a_data.extend(value)
        elif source is self.b:
            self._b_data.extend(value)
        else:
            raise ValueError("unknown redirect source")
        n = min(len(self._a_data), len(self._b_data))
        if not n:
            return
        self._data_handler.add_points(
            numpy.asarray(self._a_data[:n]) - numpy.asarray(self._b_data[:n])
        )
        self._a_data = self._a_data[n:]
        self._b_data = self._b_data[n:]


def _explicit_index(
    idx: Tuple[Union[slice, Number]], shape: Tuple[int]
) -> Tuple[slice]:
    """Return slices with explicit start and stop values."""
    nmissing = len(shape) - len(idx)
    idx = idx + (slice(None),) * nmissing
    return tuple(_explicit_slice(sidx, dimsize) for sidx, dimsize in zip(idx, shape))


def _explicit_slice(sidx: Union[slice, Number], dimsize: int) -> slice:
    """Returns slice with explicit start and stop values."""
    if isinstance(sidx, Number):
        return slice(sidx, sidx + 1)
    assert sidx.step in (None, 1)
    start = 0 if sidx.start is None else sidx.start
    stop = dimsize if sidx.stop is None else sidx.stop
    return slice(start, stop)


def _flat_scan_index(
    explicit_index: Tuple[slice], scan_shape: Tuple[int]
) -> Tuple[List[int], List[int]]:
    """Index after flattening the scan dimensions."""
    data_index = explicit_index[len(scan_shape) :]
    scan_corners = [
        (slc.start, slc.stop - 1) for slc in explicit_index[: len(scan_shape)]
    ]
    inds = numpy.ravel_multi_index(scan_corners, scan_shape)
    start = min(inds)
    stop = max(inds) + 1
    flat_scan_idx = (slice(start, stop),)
    return flat_scan_idx + data_index


def _skip_fill_value(fill_value: Any) -> bool:
    return isinstance(fill_value, Number) and fill_value in (0, numpy.nan)


def _shape_from_index(explicit_index: Tuple[slice]) -> Tuple[int]:
    """Convert index to shape."""
    return tuple(slc.stop - slc.start for slc in explicit_index)
