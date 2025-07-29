import os
import logging
import datetime
from contextlib import ExitStack, contextmanager
from typing import Mapping, Optional, Iterator

import h5py
from silx.io import h5py_utils
from ewoksdata.data.hdf5.dataset_writer import DatasetWriter

from .types import ScanData


logger = logging.getLogger(__name__)


def save_as_bliss_scan(
    filename: str,
    entry_name: str,
    scan_data: Iterator[ScanData],
    positioners: Optional[Mapping[str, float]] = None,
    title: Optional[str] = None,
    **openoptions,
):
    openoptions.setdefault("mode", "a")
    os.makedirs(os.path.abspath(os.path.dirname(filename)), exist_ok=True)
    with h5py_utils.File(filename, **openoptions) as f:
        if entry_name in f:
            logger.warning("%s::/%s already exists", filename, entry_name)
            return

        with ExitStack() as stack:
            entry = stack.enter_context(_writer_context(f, entry_name))
            instrument = entry.create_group("instrument")
            instrument.attrs["NX_class"] = "NXinstrument"
            measurement = entry.create_group("measurement")
            measurement.attrs["NX_class"] = "NXcollection"

            if title:
                entry["title"] = title

            if positioners:
                collection = instrument.create_group("positioners_start")
                collection.attrs["NX_class"] = "NXcollection"
                for k, v in positioners.items():
                    collection[k] = v
                positioners = dict(positioners)

            writers = dict()
            for data in scan_data:
                detector = instrument.require_group(data.group)
                if data.detector_type == "positioner":
                    detector.attrs["NX_class"] = "NXpositioner"
                    if positioners:
                        positioners[data.group] = data.data
                else:
                    detector.attrs["NX_class"] = "NXdetector"
                    if "type" not in detector and data.detector_type:
                        detector["type"] = data.detector_type

                key = data.group, data.name
                writer = writers.get(key)
                if writer is None:
                    writer = stack.enter_context(DatasetWriter(detector, data.name))
                    writers[key] = writer
                    if data.local_alias:
                        detector[data.local_alias] = h5py.SoftLink(writer.dataset_name)
                    if data.global_alias and data.global_alias not in measurement:
                        measurement[data.global_alias] = h5py.SoftLink(
                            writer.dataset_name
                        )

                writer.add_points(data.data)

        if positioners:
            collection = instrument.create_group("positioners")
            collection.attrs["NX_class"] = "NXcollection"
            for k, v in positioners.items():
                collection[k] = v


@contextmanager
def _writer_context(root: h5py.File, entry_name: str) -> Iterator[h5py.Group]:
    root.attrs["NX_class"] = "NXroot"
    root.attrs["creator"] = "ewoksfluo"
    entry = root.create_group(entry_name)
    try:
        entry.attrs["NX_class"] = "NXentry"
        entry.attrs["start_time"] = _timestamp()
        writer = entry.create_group("writer")
        writer.attrs["NX_class"] = "NXnote"
        writer["status"] = "STARTING"
        yield entry
    except Exception:
        writer["status"][()] = "FAILED"
        raise
    else:
        writer["status"][()] = "SUCCEEDED"
    finally:
        entry["end_time"] = _timestamp()


def _timestamp() -> str:
    return datetime.datetime.now().astimezone().isoformat()
