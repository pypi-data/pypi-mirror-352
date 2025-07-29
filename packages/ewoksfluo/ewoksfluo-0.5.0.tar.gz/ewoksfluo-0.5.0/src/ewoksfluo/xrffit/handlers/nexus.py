from typing import Optional, Union
from contextlib import ExitStack

import numpy
from silx.io.dictdump import dicttonx
from ewoksdata.data.nexus import select_default_plot
from ewoksdata.data.nexus import create_nexus_group
from ewoksdata.data.hdf5.dataset_writer import DatasetWriter, StackDatasetWriter

from .abstract import AbstractOutputHandler
from .abstract import AbstractDataHandler
import importlib.metadata

version = importlib.metadata.version("ewoksfluo")


class _NexusDataHandler(AbstractDataHandler):
    def __init__(self, group: str, name: str, writer: DatasetWriter) -> None:
        self._writer = writer
        self._group = group
        self._name = name

    def add_points(
        self, value: numpy.ndarray, scan_index: Optional[int] = None
    ) -> None:
        self._writer.add_points(value)


class _NexusStackDataHandler(AbstractDataHandler):
    def __init__(self, group: str, name: str, writer: StackDatasetWriter) -> None:
        self._writer = writer
        self._group = group
        self._name = name

    def add_points(
        self, value: numpy.ndarray, stack_index: Optional[int] = None
    ) -> None:
        if stack_index is not None:
            self._writer.add_points(value, stack_index)


NexusDataHandlerType = Union[_NexusDataHandler, _NexusStackDataHandler]


class NexusOutputHandler(AbstractOutputHandler):
    def __init__(self, url: str, default_group: Optional[str] = None, **open_options):
        self._url = url
        self._open_options = open_options
        self._default_group = default_group

        # Output
        self._already_existed = False
        self._xrf_results_uri = None
        self._output_root_uri = None

        # Context parameters
        self._reset_context_parameters()

    def _reset_context_parameters(self):
        self._ctx_stack = None
        self._nxprocess = None
        self._results = None
        self._nxdata_groups = dict()

    @property
    def xrf_results_uri(self) -> Optional[str]:
        return self._xrf_results_uri

    @property
    def output_root_uri(self) -> Optional[str]:
        return self._output_root_uri

    @property
    def already_existed(self) -> bool:
        return self._already_existed

    def __enter__(self) -> "NexusOutputHandler":
        self._ctx_stack = ExitStack().__enter__()
        ctx = create_nexus_group(self._url, default_levels=("results", "fit"))
        self._nxprocess, self._already_existed = self._ctx_stack.enter_context(ctx)
        self._nxprocess.attrs["NX_class"] = "NXprocess"
        if not self._already_existed:
            self._nxprocess["program"] = "ewoksfluo"
            self._nxprocess["version"] = version
        self._xrf_results_uri = (
            f"{self._nxprocess.file.filename}::{self._nxprocess.name}/results"
        )
        entry_name = [s for s in self._nxprocess.parent.name.split("/") if s][0]
        self._output_root_uri = f"{self._nxprocess.file.filename}::/{entry_name}"
        return self

    def __exit__(self, *args) -> None:
        try:
            self._finalize()
        finally:
            try:
                return self._ctx_stack.__exit__(*args)
            finally:
                self._reset_context_parameters()

    def create_group(self, name: str, data: dict) -> None:
        is_nxdata = data["@NX_class"] == "NXdata"
        if is_nxdata:
            if self._results is None:
                self._results = self._nxprocess.create_group("results")
                self._results.attrs["NX_class"] = "NXcollection"
            parent = self._results
        else:
            parent = self._nxprocess
        if name in parent:
            return
        dicttonx(data, parent.file, h5path=f"{parent.name}/{name}")
        if is_nxdata:
            group = parent[name]
            self._nxdata_groups[name] = {"group": group, "signals": list()}
            if name == self._default_group:
                select_default_plot(group)

    def create_nxdata_handler(
        self,
        group: str,
        name: str,
        npoints: int,
        attrs: Optional[dict] = None,
        stack_depth: Optional[int] = None,
    ) -> NexusDataHandlerType:
        name = name.replace(" ", "_")
        nxdata = self._nxdata_groups[group]
        if stack_depth is None:
            ctx = DatasetWriter(
                parent=nxdata["group"],
                name=name,
                npoints=npoints,
                attrs=attrs,
            )
            nxdata["signals"].append(name)
            writer = self._ctx_stack.enter_context(ctx)
            return _NexusDataHandler(group=group, name=name, writer=writer)
        else:
            ctx = StackDatasetWriter(
                parent=nxdata["group"],
                name=name,
                npoints=npoints,
                nstack=stack_depth,
                attrs=attrs,
            )
            nxdata["signals"].append(name)
            writer = self._ctx_stack.enter_context(ctx)
            return _NexusStackDataHandler(group=group, name=name, writer=writer)

    def _finalize(self):
        for nxdata in self._nxdata_groups.values():
            group = nxdata["group"]
            if "signal" in group.attrs:
                continue
            signals = nxdata["signals"]
            group.attrs["signal"] = signals[0]
            if len(signals) > 1:
                group.attrs["auxiliary_signals"] = signals[1:]
