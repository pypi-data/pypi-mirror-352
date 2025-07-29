from typing import Sequence, List, Optional, Dict

import h5py
from ewokscore import Task

from . import positioners_utils
from .. import nexus_utils
from ...io.hdf5 import ReadHdf5File
from ...io.hdf5 import split_h5uri
from ..xrf_results import get_xrf_result_groups
from ..positioner_utils import get_energy_suburi
from ...math.regular_grid import ScatterDataInterpolator
from ...math.rounding import round_to_significant


class RegridXrfResultsStack(
    Task,
    input_names=["xrf_results_uri", "bliss_scan_uris", "output_root_uri"],
    optional_input_names=[
        "stack_positioner",
        "positioners",
        "ignore_positioners",
        "positioner_uri_template",
        "interpolate",
        "resolution",
        "axes_units",
    ],
    output_names=["xrf_results_uri", "bliss_scan_uris", "output_root_uri"],
):
    """Regrid XRF stack results on a regular grid by interpolation."""

    def run(self):
        start_time = nexus_utils.now()
        bliss_scan_uris: Sequence[str] = self.inputs.bliss_scan_uris
        output_root_uri: str = self.inputs.output_root_uri

        with nexus_utils.save_in_ewoks_subprocess(
            output_root_uri, start_time, {}, default_levels=("results", "regrid")
        ) as (regrid_results, already_existed):
            if not already_existed:
                self._regrid(regrid_results)

            self.outputs.xrf_results_uri = (
                f"{regrid_results.file.filename}::{regrid_results.name}"
            )
        self.outputs.bliss_scan_uris = bliss_scan_uris
        self.outputs.output_root_uri = output_root_uri

    def _regrid(self, regrid_results):
        bliss_scan_uris: Sequence[str] = self.inputs.bliss_scan_uris
        xrf_results_uri: str = self.inputs.xrf_results_uri
        ignore_positioners: Optional[Sequence[str]] = self.get_input_value(
            "ignore_positioners", None
        )
        position_suburis = self._get_position_suburis(
            bliss_scan_uris, ignore_positioners=ignore_positioners
        )
        stack_suburi = self._get_stack_suburi(bliss_scan_uris)
        interpolate: str = self.get_input_value("interpolate", "nearest") or "nearest"
        resolution: Optional[dict] = self.get_input_value("resolution", None)
        axes_units: Optional[Dict[str, str]] = self.get_input_value("axes_units", None)

        xrf_results_filename, xrf_results_h5path = split_h5uri(xrf_results_uri)

        with ReadHdf5File(xrf_results_filename) as xrf_results_file:
            xrf_results_grp = xrf_results_file[xrf_results_h5path]
            if not isinstance(xrf_results_grp, h5py.Group):
                raise TypeError(f"'{xrf_results_h5path}' must be a group")

            nxdata_groups = get_xrf_result_groups(xrf_results_grp)

            coordinates, grid_names, grid_units = (
                positioners_utils.read_position_suburis(
                    bliss_scan_uris[0], position_suburis, axes_units=axes_units
                )
            )
            if resolution:
                resolution = [resolution[name] for name in grid_names]
            else:
                resolution = None
            interpolator = ScatterDataInterpolator(
                coordinates,
                grid_names,
                grid_units,
                method=interpolate,
                resolution=resolution,
            )

            axes_names = [
                stack_suburi.split("/")[-1],
                *grid_names,
            ]

            # Get fit result datasets (inputs) and output dataset information
            input_datasets = list()
            output_info = list()
            output_grps = list()
            for group_name in reversed(list(nxdata_groups)):
                input_grp = xrf_results_grp[group_name]

                output_grp = nexus_utils.create_nxdata(regrid_results, group_name)
                output_grps.append(output_grp)

                signals = list()
                for dset_name, dset in input_grp.items():
                    if not isinstance(dset, h5py.Dataset) or dset_name in axes_names:
                        continue
                    key = group_name, dset_name
                    input_datasets.append(dset)
                    output_info.append((output_grp, group_name, dset_name))
                    signals.append(dset_name)

                nexus_utils.set_nxdata_signals(output_grp, signals=signals)

            # NXdata signals
            nscans = len(bliss_scan_uris)
            output_datasets = dict()
            stack_axis_data = list()
            for scan_index, (bliss_scan_uri, *input_data) in enumerate(
                zip(bliss_scan_uris, *input_datasets)
            ):
                stack_axis_data.append(
                    positioners_utils.get_position_data(bliss_scan_uri, stack_suburi)
                )
                for (output_grp, group_name, dset_name), data in zip(
                    output_info, input_data
                ):
                    data = interpolator.regrid(data)
                    key = group_name, dset_name
                    dset = output_datasets.get(key)
                    if dset is None:
                        stack_shape = (nscans,) + data.shape
                        dset = output_grp.create_dataset(
                            dset_name, shape=stack_shape, dtype=data.dtype
                        )
                        output_datasets[key] = dset
                    dset[scan_index] = data
            stack_axis_values, stack_axis_units = zip(*stack_axis_data)
            stack_axis_units = list(set(stack_axis_units))[0]

            # NXdata axes
            axes_data = [stack_axis_values] + interpolator.grid_axes
            _axes_units = [stack_axis_units] + [
                interpolator.units
            ] * interpolator.grid_ndim
            title_parts = list()
            for iaxis, (axisname, arr, units) in enumerate(
                zip(axes_names, axes_data, _axes_units)
            ):
                title_parts.append(
                    (
                        axisname,
                        len(arr),
                        round_to_significant(abs(arr[1] - arr[0])),
                        units,
                    )
                )
                for output_grp in output_grps:
                    dset = output_grp.create_dataset(axisname, data=arr)
                    if units is not None:
                        dset.attrs["units"] = units
                        dset.attrs["long_name"] = f"{axisname} ({units})"
                    output_grp.create_dataset(f"{axisname}_indices", data=iaxis)
                    output_grp.attrs["axes"] = axes_names

            interpolator.save_coordinates_as_nxdata(regrid_results)

            title = [
                f"{axisname} ({size} x {resolution} {units})"
                for axisname, size, resolution, units in title_parts
            ]
            regrid_results["title"] = " x ".join(title)

    def _get_position_suburis(
        self,
        bliss_scan_uris: Sequence[str],
        ignore_positioners: Optional[Sequence[str]] = None,
    ) -> List[str]:
        positioners = self.get_input_value("positioners", None)
        if not positioners:
            return positioners_utils.get_scan_position_suburis(
                bliss_scan_uris[0], ignore_positioners=ignore_positioners
            )
        if isinstance(positioners, str):
            positioners = [positioners]
        template = self._get_positioner_uri_template()
        return [template.format(s) for s in positioners]

    def _get_stack_suburi(self, bliss_scan_uris: Sequence[str]) -> str:
        stack_positioner = self.get_input_value("stack_positioner", None)
        if stack_positioner:
            template = self._get_positioner_uri_template()
            return template.format(stack_positioner)
        suburi = get_energy_suburi(bliss_scan_uris[0])
        if not suburi:
            raise RuntimeError("Cannot find energy positioner")
        return suburi

    def _get_positioner_uri_template(self) -> str:
        return self.get_input_value("positioner_uri_template", "measurement/{}")
