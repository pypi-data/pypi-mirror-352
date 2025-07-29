"""Read data from ZAP scans in SPEC"""

import os
import re
from glob import glob
from typing import Dict, Sequence, Iterator, Tuple

import numpy
import fabio

from .types import ScanData, ZapInfo


_REMOVE_COUNTER_PREFIXES = {"zap_p201_": "", "zap_": "", "arr_": "", "xmap_": ""}

_REMOVE_EDF_HEADER_KEYS = (
    "EDF_BinarySize",
    "EDF_HeaderSize",
    "Dim_1",
    "Dim_2",
    "Image",
    "Size",
    "xdata",
    "xnb",
    "acquisition_time",
)


_XMAP_COUNTER_PATTERN = re.compile("^xmap_(.+?)(Sum|[0-9]+)$")


def rename_counter(name: str) -> str:
    for substr, substrnew in _REMOVE_COUNTER_PREFIXES.items():
        name = name.replace(substr, substrnew)
    return name


def iter_zap_data(
    zap_info: ZapInfo, exclude_mca_detectors: Sequence[int], motor_names: Sequence[str]
) -> Iterator[ScanData]:
    """Yields MCA spectra, MCA statistics and counters from EDF files"""
    yield from _iter_xia_ctr_data(zap_info, exclude_mca_detectors, motor_names)
    static_data = dict()
    yield from _iter_xia_stats_data(zap_info, exclude_mca_detectors, static_data)
    for detnr in range(static_data.get("ndet", 0)):
        if detnr in exclude_mca_detectors:
            continue
        yield from _iter_xia_mca_data(zap_info, detnr)
    yield from _iter_lima_data(zap_info)


def get_zap_positioners(zap_info: ZapInfo) -> Dict[str, float]:
    pattern = os.path.join(
        zap_info.directory,
        f"{zap_info.radix}_xiast_{zap_info.scannb:04d}_{zap_info.zapnb:04d}_[0-9][0-9][0-9][0-9].edf",
    )
    files = sorted(glob(pattern))
    if not files:
        return dict()
    with fabio.open(files[0]) as f:
        return _get_motors_from_xia_header(f.header)


def _iter_xia_stats_data(
    zap_info: ZapInfo, exclude_mca_detectors: Sequence[int], static_data: dict
) -> Iterator[ScanData]:
    """We have one xiast file for each line in a 2D scan. The 2D data in
    each xiast file has the shape `(ncols, 6*n)` where

        * `ncols` the number of points in each line of the 2D scan
        * `n`: the number of detectors
        * `6`: the number of statistics recorded per detector

    The columns of the 2D data in each xiast file are:

    ..code:

      |DETNR1|EVENTS1|ICR1|OCR1|TLT1|DT1|...|DETNRn|EVENTSn|ICRn|OCRn|TLTn|DTn

    """
    pattern = os.path.join(
        zap_info.directory,
        f"{zap_info.radix}_xiast_{zap_info.scannb:04d}_{zap_info.zapnb:04d}_[0-9][0-9][0-9][0-9].edf",
    )
    files = sorted(glob(pattern))
    if not files:
        return 0
    for filename in files:
        nstats = 6
        with fabio.open(filename) as f:
            data = f.data
            ncols, ntotalstats = data.shape
            ndet = ntotalstats // nstats
            if not static_data:
                static_data["ndet"] = ndet

            (
                detnr,
                events,
                trigger_count_rate,
                event_count_rate,
                trigger_live_time,
                fractional_dead_time,
            ) = data.reshape((ncols, ndet, nstats)).T

            trigger_live_time = trigger_live_time / 1000
            fractional_dead_time = fractional_dead_time / 100
            triggers = trigger_count_rate * trigger_live_time
            elapsed_time = events / event_count_rate
            live_time = events / trigger_count_rate

            for i in range(ndet):
                j = detnr[i][0]
                if j in exclude_mca_detectors:
                    continue
                group = f"xia_det{j}"
                yield ScanData(
                    group=group,
                    name="events",
                    detector_type="mca",
                    data=events[i],
                    local_alias="",
                    global_alias=f"{group}_events",
                )
                yield ScanData(
                    group=group,
                    name="trigger_count_rate",
                    detector_type="mca",
                    data=trigger_count_rate[i],
                    local_alias="",
                    global_alias=f"{group}_trigger_count_rate",
                )
                yield ScanData(
                    group=group,
                    name="event_count_rate",
                    detector_type="mca",
                    data=event_count_rate[i],
                    local_alias="",
                    global_alias=f"{group}_event_count_rate",
                )
                yield ScanData(
                    group=group,
                    name="trigger_live_time",
                    detector_type="mca",
                    data=trigger_live_time[i],
                    local_alias="",
                    global_alias=f"{group}_trigger_live_time",
                )
                yield ScanData(
                    group=group,
                    name="fractional_dead_time",
                    detector_type="mca",
                    data=fractional_dead_time[i],
                    local_alias="",
                    global_alias=f"{group}_fractional_dead_time",
                )
                yield ScanData(
                    group=group,
                    name="triggers",
                    detector_type="mca",
                    data=triggers[i],
                    local_alias="",
                    global_alias=f"{group}_triggers",
                )
                yield ScanData(
                    group=group,
                    name="elapsed_time",
                    detector_type="mca",
                    data=elapsed_time[i],
                    local_alias="",
                    global_alias=f"{group}_elapsed_time",
                )
                yield ScanData(
                    group=group,
                    name="live_time",
                    detector_type="mca",
                    data=live_time[i],
                    local_alias="",
                    global_alias=f"{group}_live_time",
                )


def _iter_xia_mca_data(zap_info: ZapInfo, detnr: int) -> Iterator[ScanData]:
    """We have one xiaXX file for each detector and each line in a 2D scan. The 2D data in
    each xiaXX file has the shape `(ncols, nchan)` where

        * `ncols` the number of points in each line of a 2D scan
        * `nchan`: the number of MCA channels
    """
    pattern = os.path.join(
        zap_info.directory,
        f"{zap_info.radix}_xia{detnr:02d}_{zap_info.scannb:04d}_{zap_info.zapnb:04d}_[0-9][0-9][0-9][0-9].edf",
    )
    files = sorted(glob(pattern))
    for filename in files:
        with fabio.open(filename) as f:
            yield ScanData(
                group=f"xia_det{detnr}",
                name="spectrum",
                detector_type="mca",
                data=f.data,
                local_alias="data",
                global_alias=f"xia_det{detnr}",
            )


def _iter_lima_data(zap_info: ZapInfo) -> Iterator[ScanData]:
    """We have one lima file for each detector and for each point in a 2D scan."""
    pattern = os.path.join(
        zap_info.directory,
        f"{zap_info.radix}_*_{zap_info.scannb:04d}_[0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9].edf",
    )
    files = {_detector_key(filename): filename for filename in glob(pattern)}
    for (camera, *_), filename in sorted(files.items()):
        if camera.startswith("xia"):
            continue
        with fabio.open(filename) as f:
            data = f.data
            if data.ndim != 2:
                continue
            yield ScanData(
                group=camera,
                name="image",
                detector_type="lima",
                data=data[numpy.newaxis, ...],
                local_alias="data",
                global_alias=camera,
            )


def _detector_key(filename: str) -> Tuple[str, int, int]:
    parts = os.path.splitext(os.path.basename(filename))[0].split("_")
    camera, _, slownr, fastnr = parts[-4:]
    return camera, int(slownr), int(fastnr)


def _iter_xia_ctr_data(
    zap_info: Dict[str, numpy.ndarray],
    exclude_mca_detectors: Sequence[int],
    motor_names: Sequence[str],
) -> Iterator[ScanData]:
    """We have one file for each counter with the shape `(nrows, ncols)` where

    * `nrows` the number of lines in a 2D scan
    * `ncols` the number of points in each line of a 2D scan
    """
    pattern = os.path.join(
        zap_info.directory,
        f"{zap_info.radix}_*_{zap_info.scannb:04d}_{zap_info.zapnb:04d}.edf",
    )
    files = glob(pattern)
    if not files:
        return

    before, _, after = pattern.partition("*")
    nbefore = len(before)
    nafter = len(after)
    raw_camera_names = set()

    for filename in files:
        raw_ctr_name = filename[nbefore:-nafter]
        if raw_ctr_name in raw_camera_names:
            continue
        is_xmap_counter = _XMAP_COUNTER_PATTERN.match(raw_ctr_name)
        if is_xmap_counter:
            roi, detnr = is_xmap_counter.groups()
            if detnr == "Sum":
                continue
            detnr = int(detnr)
            if detnr in exclude_mca_detectors:
                continue
            group = f"xia_det{detnr}"
            name = rename_counter(roi)
            detector_type = "mca"
            global_alias = f"{group}_{name}"
        else:
            group = rename_counter(raw_ctr_name)
            name = "data"
            global_alias = group
            if group in motor_names:
                detector_type = "positioner"
            else:
                detector_type = ""

        with fabio.open(filename) as f:
            if "ccd_expo_time" in f.header:
                raw_camera_names.add(raw_ctr_name)
                continue
            yield ScanData(
                group=group,
                name=name,
                detector_type=detector_type,
                data=f.data.flatten(),
                local_alias="",
                global_alias=global_alias,
            )


def _get_motors_from_xia_header(header: Dict[str, str]) -> Dict[str, float]:
    motors = dict()
    for name, value in header.items():
        if name in _REMOVE_EDF_HEADER_KEYS:
            continue
        try:
            value = float(value)
        except ValueError:
            continue
        motors[name] = value
    return motors
