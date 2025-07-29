"""Read data from SPEC files"""

import os
import re
from glob import glob
from typing import Optional, Dict, Sequence, Iterator, List, Tuple

import numpy
from silx.io.specfile import SpecFile as _SpecFile

from . import types
from .zap_utils import rename_counter
from .zap_utils import iter_zap_data, get_zap_positioners


class SpecFile:
    def __init__(self, filename: str):
        self._filename = filename
        self._specfile = None

    def __enter__(self):
        self._specfile = _SpecFile(self._filename)
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        self._specfile.close()
        self._specfile = None

    def get_scans(self) -> List[Tuple[int, int]]:
        return [tuple(map(int, k.split("."))) for k in self._specfile.keys()]

    def get_number_of_subsubscans(self, scannb: int, subscan: int = 1) -> int:
        scan = self._specfile[f"{scannb}.{subscan}"]
        title = self.get_title(scannb, subscan)
        if "fXAS_scan" in title:
            return scan.data.shape[1]
        return 1

    def iter_data(
        self,
        scannb: int,
        subscan: int = 1,
        subsubscan: int = 1,
        exclude_mca_detectors: Sequence[int] = tuple(),
    ) -> Iterator[types.ScanData]:
        scan = self._specfile[f"{scannb}.{subscan}"]
        header = scan.scan_header_dict

        motor_names = [rename_counter(s) for s in scan.motor_names]
        labels = [rename_counter(s) for s in scan.labels]
        spec_data = scan.data
        title = self.get_title(scannb, subscan)

        if "fXAS_scan" in title:
            zap_info = _zap_info_from_fluoxas_scan(
                header, spec_data.shape[1], subsubscan
            )
            if zap_info:
                yield from iter_zap_data(zap_info, exclude_mca_detectors, motor_names)
        else:
            for name, data in zip(labels, spec_data):
                if name in motor_names or name in header["S"]:
                    detector_type = "positioner"
                    data_name = "value"
                else:
                    detector_type = ""
                    data_name = "data"
                yield types.ScanData(
                    group=name,
                    name=data_name,
                    detector_type=detector_type,
                    data=numpy.array(data),
                    local_alias="",
                    global_alias=name,
                )
            yield from _iter_motors_from_title(title, labels)
            zap_info = _zap_info_from_scan(header)
            if zap_info:
                yield from iter_zap_data(zap_info, exclude_mca_detectors, motor_names)

    def get_positioners(
        self, scannb: int, subscan: int = 1, subsubscan: int = 1
    ) -> Dict[str, float]:
        scan = self._specfile[f"{scannb}.{subscan}"]
        motor_names = [rename_counter(s) for s in scan.motor_names]
        title = self.get_title(scannb, subscan)
        if "fXAS_scan" in title:
            zap_info = _zap_info_from_fluoxas_scan(
                scan.scan_header_dict, scan.data.shape[1], subsubscan
            )
        else:
            zap_info = _zap_info_from_scan(scan.scan_header_dict)
        if zap_info:
            positioners = get_zap_positioners(zap_info)
        else:
            positioners = dict()
        positioners.update((zip(motor_names, scan.motor_positions)))
        return positioners

    def get_title(self, scannb: int, subscan: int = 1) -> str:
        scan = self._specfile[f"{scannb}.{subscan}"]
        title = re.split(r"\s", scan.scan_header_dict["S"])
        return " ".join([s for s in title[1:] if s]).strip()


def _zap_info_from_scan(header: Dict[str, str]) -> Optional[types.ZapInfo]:
    xia_keys = {
        "DIRECTORY": ("directory", str),
        "RADIX": ("radix", str),
        "ZAP SCAN NUMBER": ("scannb", int),
        "ZAP IMAGE NUMBER": ("zapnb", int),
    }
    info = _xia_info_from_header(header, xia_keys)
    if info is None:
        return
    return types.ZapInfo(**info)


def _zap_info_from_fluoxas_scan(
    header: Dict[str, str], npoints: int, subsubscan: int
) -> Optional[types.ZapInfo]:
    xia_keys = {
        "DIRECTORY": ("directory", str),
    }
    info = _xia_info_from_header(header, xia_keys)
    if info is None:
        return
    directory, radix = os.path.split(info["directory"])
    radix_prefix, _, nb_stop = radix.rpartition("_")
    nb_stop = int(nb_stop)
    nb_start = nb_stop - npoints
    zapnb = 0
    nb = nb_start + subsubscan
    radix = f"{radix_prefix}_{nb:04d}"
    zap_directory = os.path.join(directory, radix)

    pattern = os.path.join(zap_directory, f"{radix}_xiast_*_{zapnb:04d}_0000.edf")
    files = glob(pattern)
    if len(files) != 1:
        return
    repattern = os.path.join(
        zap_directory, f"{radix}_xiast_([0-9]+)_{zapnb:04d}_0000.edf"
    )
    m = re.match(repattern, files[0])
    if not m:
        return
    scannb = int(m.groups()[0])
    return types.ZapInfo(
        directory=zap_directory, radix=radix, scannb=scannb, zapnb=zapnb
    )


def _xia_info_from_header(header: dict, xia_keys: dict) -> Optional[dict]:
    info = dict()
    for s in header.get("C", "").split("\n"):
        tmp = s.split(":")
        if len(tmp) != 2:
            continue
        key, value = [s.strip() for s in tmp]
        key, deserialize = xia_keys.get(key, (None, None))
        if key:
            info[key] = deserialize(value)
    if len(info) != len(xia_keys):
        return
    return info


def _iter_motors_from_title(
    title: str, exclude: Sequence[str] = tuple()
) -> Iterator[types.ScanData]:
    title = [s for s in re.split(r"\s", title) if s]
    if title[0] == "zapline":
        try:
            cmd, motfast, startfast, endfast, npixelsfast, time = title
        except ValueError:
            return
        if motfast not in exclude:
            data = _contspace(startfast, endfast, npixelsfast)
            yield types.ScanData(
                group=motfast,
                name="value",
                detector_type="positioner",
                data=data,
                local_alias="",
                global_alias=motfast,
            )
    elif title[0] == "zapimage":
        try:
            (
                cmd,
                motfast,
                startfast,
                endfast,
                npixelsfast,
                time,
                motslow,
                startslow,
                endslow,
                nstepsslow,
                zero,
            ) = title
        except ValueError:
            return
        if motfast not in exclude:
            data = numpy.tile(
                _contspace(startfast, endfast, npixelsfast),
                int(nstepsslow) + 1,
            )
            yield types.ScanData(
                group=motfast,
                name="value",
                detector_type="positioner",
                data=data,
                local_alias="",
                global_alias=motfast,
            )
        if motslow not in exclude:
            data = numpy.repeat(
                _stepspace(startslow, endslow, nstepsslow),
                int(npixelsfast),
            )
            yield types.ScanData(
                group=motslow,
                name="value",
                detector_type="positioner",
                data=data,
                local_alias="",
                global_alias=motslow,
            )
    elif title[0] == "ascan":
        try:
            cmd, motfast, startfast, endfast, nstepsfast, time = title
        except ValueError:
            return
        if motfast not in exclude:
            data = _stepspace(startfast, endfast, nstepsfast)
            yield types.ScanData(
                group=motfast,
                name="value",
                detector_type="positioner",
                data=data,
                local_alias="",
                global_alias=motfast,
            )


def _contspace(start: str, stop: str, npoints: str) -> numpy.ndarray:
    start = float(start)
    stop = float(stop)
    npoints = int(npoints)
    nsteps = npoints - 1
    half_step = (stop - start) / (2 * nsteps)
    return numpy.linspace(start + half_step, stop - half_step, npoints)


def _stepspace(start: str, stop: str, nsteps: str) -> numpy.ndarray:
    start = float(start)
    stop = float(stop)
    npoints = int(nsteps) + 1
    return numpy.linspace(start, stop, npoints)
