import re
from typing import Dict, Any

import h5py
import numpy

from . import nexus_utils

_PEAKS_AREA_REGEX = [
    re.compile(r"^[a-zA-Z]+_[KLM][a-b1-5]?$"),
    re.compile(r"^Scatter_Compton[0-9]+$"),
    re.compile(r"^Scatter_Peak[0-9]+$"),
]


def is_peak_area(dset: h5py.Dataset) -> bool:
    """Checks if the dataset is a peak area."""
    if not isinstance(dset, h5py.Dataset):
        return False
    dset_name = dset.name.split("/")[-1]
    return any(regex.match(dset_name) for regex in _PEAKS_AREA_REGEX)


def save_xrf_results(
    output_root_uri: str,
    group_name: str,
    process_config: Dict[str, Any],
    parameters: Dict[str, numpy.ndarray],
    uncertainties: Dict[str, numpy.ndarray],
    massfractions: Dict[str, numpy.ndarray],
) -> str:
    start_time = nexus_utils.now()
    with nexus_utils.save_in_ewoks_process(
        output_root_uri,
        start_time,
        process_config=process_config,
        default_levels=("results", group_name),
    ) as (process_group, already_existed):
        if already_existed:
            results_group = process_group["results"]
        else:
            results_group = process_group.create_group("results")
            results_group.attrs["NX_class"] = "NXcollection"

            if parameters:
                _ = _save_nxdata(results_group, "parameters", parameters)
            if uncertainties:
                _ = _save_nxdata(results_group, "uncertainties", uncertainties)
            # if parameters and uncertainties:
            #    for name in set(param_group) & set(error_group):
            #        create_hdf5_link(param_group, f"{name}_errors", error_group[name])
            if massfractions:
                _save_nxdata(results_group, "massfractions", massfractions)
        return f"{results_group.file.filename}::{results_group.name}"


def _save_nxdata(parent: h5py.Group, name: str, group: Dict[str, numpy.ndarray]):
    nxgroup = nexus_utils.create_nxdata(parent, name)
    for name, data in group.items():
        nxgroup.create_dataset(name, data=data)
    nexus_utils.set_nxdata_signals(nxgroup, signals=list(group))
    return nxgroup


def get_xrf_result_groups(parent_nxdata: h5py.Group) -> Dict[str, h5py.Group]:
    """Most important group comes first"""
    return {
        name: parent_nxdata[name] for name in _NXDATA_ORDER if name in parent_nxdata
    }


_NXDATA_ORDER = [
    "parameters",
    "massfractions",
    "uncertainties",
    "rawcounters",
]
