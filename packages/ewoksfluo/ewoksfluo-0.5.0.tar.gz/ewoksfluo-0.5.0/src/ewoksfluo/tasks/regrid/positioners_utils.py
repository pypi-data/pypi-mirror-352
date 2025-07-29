from typing import Sequence, Tuple, List, Optional, Dict

import numpy
import h5py

from ...io.hdf5 import split_h5uri
from ...io.hdf5 import retry_external_link
from ...io.hdf5 import ReadHdf5File


def read_position_suburis(
    bliss_scan_uri: str,
    position_suburis: Sequence[str],
    axes_units: Optional[Dict[str, str]] = None,
) -> Tuple[List[numpy.ndarray], List[str], List[Optional[str]]]:
    data = [
        get_position_data(bliss_scan_uri, position_suburi)
        for position_suburi in position_suburis
    ]
    positions, units = zip(*data)
    names = [[s for s in name.split("/") if s][-1] for name in position_suburis]
    if axes_units:
        units = [
            unit if unit else axes_units.get(name) for name, unit in zip(names, units)
        ]
    return positions, names, units


def get_position_data(
    bliss_scan_uri: str, position_suburi: str
) -> Tuple[numpy.ndarray, Optional[str]]:
    """Get position data with units from HDF5"""
    scan_filename, scan_h5path = split_h5uri(bliss_scan_uri)

    with ReadHdf5File(scan_filename) as scan_file:
        scan_grp = scan_file[scan_h5path]
        assert isinstance(scan_grp, h5py.Group)
        with retry_external_link(scan_grp, position_suburi) as pos_dataset:
            assert isinstance(pos_dataset, h5py.Dataset)
            return pos_dataset[()], pos_dataset.attrs.get("units")


def get_scan_position_suburis(
    bliss_scan_uri: str, ignore_positioners: Optional[Sequence[str]] = None
) -> List[str]:
    """Get all scan sub-URI's for positioners which were scanned."""
    scan_filename, scan_h5path = split_h5uri(bliss_scan_uri)

    with ReadHdf5File(scan_filename) as scan_file:
        scan_grp = scan_file[scan_h5path]
        with retry_external_link(
            scan_grp, "instrument/positioners_start"
        ) as positioners:
            positioners = set(positioners)
            counters = set(scan_grp["measurement"])
            positioners &= counters
            if ignore_positioners:
                positioners -= set(ignore_positioners)
            # E.g. order ["sampz", "sampy"]
            # The first dimension in pymca and silx is plotted vertically
            return [f"measurement/{s}" for s in reversed(sorted(positioners))]
