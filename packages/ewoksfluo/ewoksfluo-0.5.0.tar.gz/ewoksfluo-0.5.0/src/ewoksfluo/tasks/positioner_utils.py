import logging
from typing import Dict, Optional

import h5py

from ..io.hdf5 import split_h5uri
from ..io.hdf5 import ReadHdf5File

_ENERGY_UNITS = {"kev": 1, "ev": 0.001}
_ENERGY_TEMPLATE = "instrument/positioners_start/{}"

_logger = logging.getLogger(__name__)


def get_energy_suburi(bliss_scan_uri: str) -> Optional[str]:
    return _get_unit_position_suburi(bliss_scan_uri, _ENERGY_UNITS)


def get_energy(
    bliss_scan_uri: str,
    energy_name: Optional[str] = None,
    energy_uri_template: Optional[str] = None,
) -> Optional[float]:
    if energy_name:
        if not energy_uri_template:
            energy_uri_template = _ENERGY_TEMPLATE
        try:
            return _get_template_position_value(
                bliss_scan_uri, energy_name, energy_uri_template, _ENERGY_UNITS
            )
        except KeyError:
            _logger.warning(
                "'%s' does not exist. Do not modify the primary beam energy.",
                energy_name,
            )
            return None
    return _get_unit_position_value(bliss_scan_uri, _ENERGY_UNITS)


def _get_unit_position_suburi(
    bliss_scan_uri: str, units: Dict[str, float]
) -> Optional[str]:
    """Get scan sub-URI for a positioner with specific units"""
    scan_filename, scan_h5path = split_h5uri(bliss_scan_uri)

    with ReadHdf5File(scan_filename) as nxroot:
        positioners = nxroot[f"{scan_h5path}/instrument/positioners_start"]
        name = _get_positioner_name(positioners, units)
        if name is not None:
            return f"instrument/positioners_start/{name}"


def _get_template_position_value(
    bliss_scan_uri: str,
    position_name: str,
    position_uri_template: str,
    units: Dict[str, float],
) -> float:
    """Get position value from scan"""
    scan_filename, scan_h5path = split_h5uri(bliss_scan_uri)
    suburi = position_uri_template.format(position_name)
    with ReadHdf5File(scan_filename) as nxroot:
        dset = nxroot[f"{scan_h5path}/{suburi}"]
        punits = dset.attrs.get("units", "").lower()
        return dset[()] * units.get(punits, 1)


def _get_unit_position_value(
    bliss_scan_uri: str, units: Dict[str, float]
) -> Optional[float]:
    """Get position value from scan"""
    scan_filename, scan_h5path = split_h5uri(bliss_scan_uri)
    with ReadHdf5File(scan_filename) as nxroot:
        positioners = nxroot[f"{scan_h5path}/instrument/positioners_start"]
        return _get_positioner_value(positioners, units)


def _get_positioner_value(
    positioners: h5py.Group, units: Dict[str, float]
) -> Optional[h5py.Dataset]:
    for name in positioners:
        positioner = positioners[name]
        punits = positioner.attrs.get("units", "").lower()
        if punits in units:
            return positioner[()] * units[punits]


def _get_positioner_name(
    positioners: h5py.Group, units: Dict[str, float]
) -> Optional[str]:
    for name in positioners:
        positioner = positioners[name]
        punits = positioner.attrs.get("units", "").lower()
        if punits in units:
            return name
