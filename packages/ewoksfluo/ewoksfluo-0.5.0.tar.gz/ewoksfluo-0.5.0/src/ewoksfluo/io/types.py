from typing import NamedTuple
import numpy


class ScanData(NamedTuple):
    group: str
    name: str
    detector_type: str
    data: numpy.ndarray  # npoints x ...
    local_alias: str
    global_alias: str


class ZapInfo(NamedTuple):
    """SPEC zap scan information"""

    directory: str
    radix: str
    scannb: int
    zapnb: int
