"""Buffers receive data from pymca."""

import os
from typing import Optional
from contextlib import contextmanager

from silx.io.url import DataUrl
from PyMca5.PyMcaPhysics.xrf.McaAdvancedFitBatch import OutputBuffer as _OutputBuffer
from ewoksdata.data.hdf5 import h5exists


class PyMcaOutputBuffer(_OutputBuffer):
    """This is the output buffer of PyMca with an internal output handler."""

    def __init__(
        self,
        output_root_uri: str,
        diagnostics: bool = False,
        figuresofmerit: bool = False,
        **open_options,
    ):
        url = DataUrl(output_root_uri)
        filename = str(url.file_path())
        h5path = [s for s in url.data_path().split("/") if s]
        nh5path = len(h5path)
        if nh5path == 0:
            h5path = "results", "fit"
        elif nh5path == 1:
            h5path.append("fit")
        else:
            h5path = h5path[:2]
        self._file_entry, self._file_process = h5path
        self._output_dir = os.path.dirname(filename)
        self._output_root = os.path.splitext(os.path.basename(filename))[0]
        super().__init__(
            outputDir=self._output_dir,
            outputRoot=self._output_root,
            fileEntry=self._file_entry,
            fileProcess=self._file_process,
            saveResiduals=diagnostics,
            saveFit=diagnostics,
            saveData=diagnostics,
            diagnostics=diagnostics,
            saveFOM=figuresofmerit,
        )
        self._open_options = open_options  # e.g. retry arguments
        open_options["mode"] = "a"
        self._newgroup = False
        self._xrf_results_uri = None

    @property
    def xrf_results_uri(self) -> Optional[str]:
        return self._xrf_results_uri

    @property
    def already_existed(self) -> bool:
        return self._newgroup

    @contextmanager
    def saveContext(self, **kw):
        filename = os.path.join(self._output_dir, self._output_root + ".h5")
        h5path = f"{self._file_entry}/{self._file_process}"
        self._newgroup = not h5exists(filename, h5path, **self._open_options)
        self._xrf_results_uri = f"{filename}::/{h5path}/results"
        with super().saveContext(**kw) as ctx:
            yield ctx
