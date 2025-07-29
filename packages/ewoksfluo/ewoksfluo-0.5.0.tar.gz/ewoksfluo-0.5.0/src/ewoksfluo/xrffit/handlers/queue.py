from typing import Dict, Optional, Set, Tuple, Callable
from queue import Queue, Empty
import numpy

from ...xrffit.handlers.nexus import NexusDataHandlerType, NexusOutputHandler

from ...xrffit.queue_messages import (
    DataMsg,
    DatasetMsg,
    GroupMsg,
    QueueMsg,
    StopMsg,
    is_DataMsg,
    is_DatasetMsg,
    is_GroupMsg,
    is_StopMsg,
)

from .abstract import AbstractOutputHandler
from .abstract import AbstractDataHandler


class _QueueDataHandler(AbstractDataHandler):
    def __init__(
        self,
        group: str,
        name: str,
        queue: Queue,
        sendid: int,
        destinationid: int,
        scan_index: Optional[int],
    ) -> None:
        self._queue = queue
        self._sendid = sendid
        self._destinationid = destinationid
        self._group = group
        self._name = name
        self._scan_index = scan_index

    def add_points(self, value: numpy.ndarray) -> None:
        msg = DataMsg(
            self._sendid,
            self._destinationid,
            self._group,
            self._name,
            value,
            self._scan_index,
        )
        self._queue.put(msg)


class QueueOutputHandler(AbstractOutputHandler):
    def __init__(
        self,
        queue: Queue,
        sendid: int,
        destinationid: int,
        nscans: Optional[int],
        scan_index: Optional[int],
    ):
        self._queue = queue
        self._sendid = sendid
        self._destinationid = destinationid
        self._nscans = nscans
        self._scan_index = scan_index

    def __enter__(self) -> "QueueOutputHandler":
        return self

    def __exit__(self, *args):
        stop_queue(self._queue, self._sendid)

    def create_group(self, name: str, data: dict) -> None:
        msg = GroupMsg(self._sendid, self._destinationid, name, data)
        self._queue.put(msg)

    def create_nxdata_handler(
        self,
        group_name: str,
        name: str,
        npoints: int,
        attrs: Optional[dict] = None,
    ) -> _QueueDataHandler:
        if attrs is None:
            attrs = {}
        msg = DatasetMsg(
            self._sendid,
            self._destinationid,
            group_name,
            name,
            npoints,
            attrs,
            self._nscans,
        )
        self._queue.put(msg)
        return _QueueDataHandler(
            group_name,
            name,
            self._queue,
            self._sendid,
            self._destinationid,
            self._scan_index,
        )


def consume_handler_queue(
    output_handlers: Dict[int, NexusOutputHandler],
    queue: Queue,
    all_sendids: Set[int],
    raise_on_error: Callable[[], None],
):
    datasets: Dict[Tuple[int, str, str], NexusDataHandlerType] = dict()
    stopped_sendids: Set[int] = set()
    while True:
        raise_on_error()
        try:
            msg: QueueMsg = queue.get(timeout=0.5)
        except Empty:
            continue

        if is_StopMsg(msg):
            stopped_sendids.add(msg.sendid)
            if all_sendids == stopped_sendids:
                return
            continue

        if is_GroupMsg(msg):
            destid = msg.destinationid
            output_handler = output_handlers[destid]
            output_handler.create_group(msg.group, msg.data)
            continue

        if is_DatasetMsg(msg):
            group, name, destid = msg.group, msg.name, msg.destinationid
            output_handler = output_handlers[destid]
            dataset_key = (destid, group, name)
            if dataset_key not in datasets:
                datasets[dataset_key] = output_handler.create_nxdata_handler(
                    group, name, msg.npoints, msg.attrs, msg.nscans
                )
            continue

        if is_DataMsg(msg):
            group, name, destid = msg.group, msg.name, msg.destinationid
            output_handler = output_handlers[destid]
            dataset_key = (destid, group, name)
            datasets[dataset_key].add_points(msg.value, msg.scan_index)
            continue

        raise ValueError(f"Unknown command {msg.cmd}")


def stop_queue(queue: Queue, sendid: int):
    msg = StopMsg(sendid)
    queue.put(msg)
