from typing import NamedTuple, Optional, Union
import numpy
from typing_extensions import TypeGuard


class StopMsg(NamedTuple):
    sendid: int
    cmd: str = "STOP"


class GroupMsg(NamedTuple):
    sendid: int
    destinationid: int
    group: str
    data: dict
    cmd: str = "GROUP"


class DatasetMsg(NamedTuple):
    sendid: int
    destinationid: int
    group: str
    name: str
    npoints: int
    attrs: dict
    nscans: Optional[int]
    cmd: str = "DATASET"


class DataMsg(NamedTuple):
    sendid: int
    destinationid: int
    group: str
    name: str
    value: numpy.ndarray
    scan_index: Optional[int]
    cmd: str = "DATA"


QueueMsg = Union[StopMsg, GroupMsg, DatasetMsg, DataMsg]


def is_StopMsg(msg: QueueMsg) -> TypeGuard[StopMsg]:
    return msg.cmd == "STOP"


def is_GroupMsg(msg: QueueMsg) -> TypeGuard[GroupMsg]:
    return msg.cmd == "GROUP"


def is_DatasetMsg(msg: QueueMsg) -> TypeGuard[DatasetMsg]:
    return msg.cmd == "DATASET"


def is_DataMsg(msg: QueueMsg) -> TypeGuard[DataMsg]:
    return msg.cmd == "DATA"
