from typing import Optional, List

import numpy
import h5py
from ewokscore import Task

from .. import nexus_utils
from .. import hdf5_utils
from ...io.hdf5 import split_h5uri
from ...io.hdf5 import ReadHdf5File


class ExtractRawCountersStack(
    Task,
    input_names=["bliss_scan_uris", "output_root_uri"],
    optional_input_names=["xrf_results_uri"],
    output_names=["xrf_results_uri", "bliss_scan_uris", "output_root_uri"],
):
    """Extract raw stack counters and save them like XRF results."""

    def run(self):
        start_time = nexus_utils.now()
        bliss_scan_uris: List[str] = self.inputs.bliss_scan_uris
        output_root_uri: str = self.inputs.output_root_uri
        previous_xrf_results_uri: Optional[str] = self.get_input_value(
            "xrf_results_uri", None
        )

        input_file0, scan_h5path0 = split_h5uri(bliss_scan_uris[0])
        if previous_xrf_results_uri:
            default_nprocess_name = "merge"
        else:
            default_nprocess_name = "raw"

        with nexus_utils.save_in_ewoks_process(
            output_root_uri,
            start_time,
            process_config=dict(),
            default_levels=(
                scan_h5path0,  # TODO: what should the default be?
                default_nprocess_name,
            ),
        ) as (process_group, already_existed):
            if already_existed:
                merged_xrf_results = process_group["results"]
            else:
                merged_xrf_results = process_group.create_group("results")
                merged_xrf_results.attrs["NX_class"] = "NXcollection"

                with ReadHdf5File(input_file0) as h5file0:
                    _link_raw_counters(
                        h5file0[scan_h5path0],
                        bliss_scan_uris,
                        merged_xrf_results,
                        "rawcounters",
                    )

                if previous_xrf_results_uri:
                    input_file, parent_path = split_h5uri(previous_xrf_results_uri)
                    with ReadHdf5File(input_file) as h5file:
                        _link_xrf_results(h5file[parent_path], merged_xrf_results)

            self.outputs.xrf_results_uri = (
                f"{merged_xrf_results.file.filename}::{merged_xrf_results.name}"
            )

        self.outputs.bliss_scan_uris = bliss_scan_uris
        self.outputs.output_root_uri = output_root_uri


def _link_raw_counters(
    raw_scan0: h5py.Group,
    bliss_scan_uris: List[str],
    process_group: h5py.Group,
    name: str,
) -> None:
    destination = nexus_utils.create_nxdata(process_group, name)
    measurement = raw_scan0["measurement"]

    nscans = len(bliss_scan_uris)
    layouts = dict()
    for name, dset in measurement.items():
        if dset.ndim == 1:
            layout = h5py.VirtualLayout(shape=(nscans, dset.size), dtype=dset.dtype)
            vsource_shape = (dset.size,)
            layouts[name] = layout, vsource_shape

    for i, bliss_scan_uri in enumerate(bliss_scan_uris):
        filename, scan_h5path = split_h5uri(bliss_scan_uri)
        for name, (layout, vsource_shape) in layouts.items():
            layout[i] = h5py.VirtualSource(
                filename, f"{scan_h5path}/measurement/{name}", shape=vsource_shape
            )

    for name, (layout, _) in layouts.items():
        destination.create_virtual_dataset(name, layout, fillvalue=numpy.nan)

    nexus_utils.set_nxdata_signals(destination, signals=list(layouts))


def _link_xrf_results(xrf_results: h5py.Group, process_group: h5py.Group) -> None:
    for name, group in xrf_results.items():
        hdf5_utils.create_hdf5_link(process_group, name, group)
