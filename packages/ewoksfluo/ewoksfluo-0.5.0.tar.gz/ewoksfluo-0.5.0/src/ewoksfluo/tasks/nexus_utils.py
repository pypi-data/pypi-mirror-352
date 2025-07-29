import json
import logging
import contextlib
from datetime import datetime
from typing import Any, Dict, Optional, Sequence, Union, Generator, Tuple

import numpy
import h5py

from ewoksdata.data import nexus

import importlib.metadata

version = importlib.metadata.version("ewoksfluo")


logger = logging.getLogger(__name__)


def create_nxdata(
    parent: Union[h5py.File, h5py.Group],
    name: str,
    signal: Optional[str] = None,
) -> h5py.Group:
    nxdata = parent.create_group(name)
    nxdata.attrs["NX_class"] = "NXdata"
    if signal:
        nxdata.attrs["signal"] = signal
    nexus.select_default_plot(nxdata)
    return nxdata


def set_nxdata_signals(nxdata: h5py.Group, signals: Sequence[str]):
    nxdata.attrs["signal"] = signals[0]
    if len(signals) > 1:
        nxdata.attrs["auxiliary_signals"] = signals[1:]


def now() -> str:
    """NeXus-compliant format of the current time"""
    return datetime.now().astimezone().isoformat()


@contextlib.contextmanager
def save_in_ewoks_process(
    output_root_uri: str,
    start_time: str,
    process_config: Dict[str, Any],
    default_levels=("results", "process"),
    **kw,
) -> Generator[Tuple[h5py.Group, bool], None, None]:
    with nexus.create_nexus_group(
        output_root_uri, default_levels=default_levels, **kw
    ) as (
        process_group,
        already_existed,
    ):
        if already_existed:
            logger.warning(
                "%s::%s already exists", process_group.file.filename, process_group.name
            )
            yield process_group, already_existed
        else:
            entry_name = process_group.name.split("/")[1]
            entry_group = process_group.file[entry_name]
            if "start_time" not in entry_group:
                entry_group["start_time"] = start_time

            try:
                process_group.attrs["NX_class"] = "NXprocess"
                process_group["program"] = "ewoksfluo"
                process_group["version"] = version
                config_group = process_group.create_group("configuration")
                config_group.attrs["NX_class"] = "NXnote"
                config_group.create_dataset(
                    "data", data=json.dumps(process_config, cls=NumpyEncoder)
                )
                config_group.create_dataset("date", data=now())
                config_group.create_dataset("type", data="application/json")

                yield process_group, already_existed
            finally:
                if "end_time" in entry_group:
                    entry_group["end_time"][()] = now()
                else:
                    entry_group["end_time"] = now()


@contextlib.contextmanager
def save_in_ewoks_subprocess(
    output_root_uri: str,
    start_time: str,
    process_config: Dict[str, Any],
    collection_name: str = "results",
    **kw,
) -> Generator[Tuple[h5py.Group, bool], None, None]:
    with save_in_ewoks_process(output_root_uri, start_time, process_config, **kw) as (
        process_group,
        already_existed,
    ):
        if already_existed:
            results = process_group[collection_name]
        else:
            results = process_group.create_group(collection_name)
            results.attrs["NX_class"] = "NXcollection"
        yield results, already_existed


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (numpy.generic, numpy.ndarray)):
            return obj.tolist()
        return super().default(obj)
