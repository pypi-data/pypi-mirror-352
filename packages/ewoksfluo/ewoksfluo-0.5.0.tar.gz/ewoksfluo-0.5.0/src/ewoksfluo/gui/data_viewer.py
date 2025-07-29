import os
import sys
import logging
import tempfile
import traceback
from contextlib import contextmanager

from types import MappingProxyType
from typing import Optional, Union, Generator, Iterator, Tuple

from functools import cached_property

import h5py
import numpy

from AnyQt import QtCore
from AnyQt import QtWidgets
from AnyQt.QtCore import Qt

from silx.io import commonh5
from silx.io import h5py_utils
from silx.app.view.Viewer import Viewer as SilxViewer
from ..io.hdf5 import ReadHdf5File

_logger = logging.getLogger(__name__)


class DataViewer(SilxViewer):
    """Browse data from files supported by silx.

    To create the widget

    .. code: python

        viewer = DataViewer(parent)
        viewer.setVisible(True)
        parent.layout().addWidget(viewer)

    To close and refresh files

    .. code: python

        viewer.updateFile("/path/to/file1.h5")
        viewer.updateFile("/path/to/file2.h5")
        viewer.closeFile("/path/to/file1.h5")

    To close all files

    .. code: python

        viewer.closeAll()
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        if parent is not None:
            self.setWindowFlags(Qt.Widget)

        # We cannot handle file opening in the viewer
        # because files are also opened when synchronizing
        model = self._findHdf5TreeModel()
        model.insertFile = _insertFile.__get__(model, type(model))

    def close(self):
        if self.parent():
            self.parent().close()
        else:
            self.close()

    def closeFile(self, filename: str) -> None:
        """When the file is opened, close it."""
        _, h5file = self._getFileObject(filename)
        if h5file is None:
            return
        model = self._findHdf5TreeModel()
        model.removeH5pyObject(h5file)

    def updateFile(self, filename, **file_open_options):
        """When the file exists, append when not already appended and refresh view."""
        # Remove when non existing
        if not os.path.exists(filename):
            self.closeFile(filename)
            return

        # Append when missing
        index, h5file = self._getFileObject(filename)
        if h5file is None:
            self.appendFile(filename, **file_open_options)
            index, h5file = self._getFileObject(filename)

        # Select the file (TODO: errors)
        selection_model = self._treeview.selectionModel()
        selection_model.clearSelection()
        self._treeview.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        selection_model.select(
            index, QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Rows
        )
        self._treeview.setCurrentIndex(index)

        # Refresh the current selection
        self._Viewer__refreshAction.trigger()

    @property
    def _treeview(self):
        return self._Viewer__treeview

    def _findHdf5TreeModel(self):
        return self._treeview.findHdf5TreeModel()

    def _iterH5FileObjects(
        self,
    ) -> Iterator[Tuple[QtCore.QModelIndex, "ViewerFile"]]:
        model = self._findHdf5TreeModel()
        root_index = QtCore.QModelIndex()
        root = model.nodeFromIndex(root_index)
        for row in range(root.childCount()):
            hdf5item = root.child(row)
            index = model.index(row, 0, root_index)
            yield index, hdf5item.obj

    def _getFileObject(
        self, filename
    ) -> Tuple[Optional[QtCore.QModelIndex], Optional["ViewerFile"]]:
        filename = os.path.normpath(os.path.abspath(filename))
        for index, h5file in self._iterH5FileObjects():
            filename2 = os.path.normpath(os.path.abspath(h5file.filename))
            if filename2 == filename:
                return index, h5file
        return None, None


def _insertFile(self, filename, row=-1):
    """Open the file with the viewer proxy that does not keep the file opened."""
    try:
        h5file = ViewerFile(filename)
        if self._Hdf5TreeModel__ownFiles:
            self._Hdf5TreeModel__openedFiles.append(h5file)
        self.sigH5pyObjectLoaded.emit(h5file, filename)
        self.insertH5pyObject(h5file, row=row, filename=filename)
    except IOError:
        _logger.debug("File '%s' can't be read.", filename, exc_info=True)
        raise


class ViewerDataset(commonh5.Dataset):
    """Proxy to a HDF5 dataset that does not keep the file opened."""

    def __init__(self, name: str, parent: Union["ViewerFile", "ViewerGroup"]):
        super().__init__(name, None, parent=parent, attrs=None)

    @contextmanager
    def _h5dataset(self) -> Generator[h5py.Dataset, None, None]:
        with self.file._h5open() as h5file:
            yield h5file[self.name]

    def _get_h5attribute(self, attr: str):
        with self._h5dataset() as h5dataset:
            return getattr(h5dataset, attr)

    dtype = cached_property(lambda self: self._get_h5attribute("dtype"))
    shape = cached_property(lambda self: self._get_h5attribute("shape"))
    size = cached_property(lambda self: self._get_h5attribute("size"))
    ndim = cached_property(lambda self: self._get_h5attribute("ndim"))
    compression = cached_property(lambda self: self._get_h5attribute("compression"))
    compression_opts = cached_property(
        lambda self: self._get_h5attribute("compression_opts")
    )
    chunks = cached_property(lambda self: self._get_h5attribute("chunks"))
    is_virtual = cached_property(lambda self: self._get_h5attribute("is_virtual"))
    virtual_sources = cached_property(
        lambda self: self._get_h5attribute("virtual_sources")
    )
    external = cached_property(lambda self: self._get_h5attribute("external"))

    def __len__(self):
        with self._h5dataset() as h5dataset:
            return len(h5dataset)

    def __getitem__(self, item):
        with self._h5dataset() as h5dataset:
            return h5dataset[item]

    def __iter__(self):
        return self[()].__iter__()

    def __bool__(self):
        with self._h5dataset() as h5dataset:
            return bool(h5dataset)

    def __getattr__(self, item):
        """Proxy to underlying numpy array methods.

        Called for example when doing `numpy.array(dataset)`.
        """
        data = self[()]
        if hasattr(data, item):
            return getattr(data, item)

        raise AttributeError("Dataset has no attribute %s" % item)

    @cached_property
    def attrs(self):
        with self._h5dataset() as h5dataset:
            return MappingProxyType(dict(h5dataset.attrs))

    @property
    def value(self):
        raise NotImplementedError()  # Should not be used: h5py v2 property

    def _get_data(self):
        # All method calling this method in the base class should be overridden
        stack_trace = traceback.format_stack()
        _logger.warning(
            f"ViewerDataset._get_data should not be called\nStack trace:\n{''.join(stack_trace)}"
        )
        return self[()]


class ViewerGroup(commonh5.Group):
    """Proxy to a HDF5 group that does not keep the file opened."""

    def __init__(self, name, parent):
        with parent.file._h5open() as h5file:
            full_name = f"{parent.name}/{name}"
            h5group = h5file[full_name]
            attrs = dict(h5group.attrs)
            super().__init__(name, parent=parent, attrs=attrs)
            _add_nodes(self, h5group)


class ViewerFile(commonh5.File):
    """Proxy to a HDF5 file that does not keep the file opened."""

    def __init__(self, name: str, **file_open_options):
        self._file_open_options = file_open_options
        with ReadHdf5File(name, **self._file_open_options) as h5file:
            h5group = h5file["/"]  # for order preservation
            attrs = dict(h5group.attrs)
            super().__init__(name=name, mode="r", attrs=attrs)
            _add_nodes(self, h5group)

    @contextmanager
    def _h5open(self) -> Generator[h5py.File, None, None]:
        with ReadHdf5File(self.filename, **self._file_open_options) as h5file:
            yield h5file


def _add_nodes(
    commongroup: Union[ViewerFile, ViewerGroup], h5item: Union[h5py.Group, h5py.File]
):
    for base_name in h5item:
        if h5item.get(base_name, default=None, getclass=True) is h5py.Group:
            commongroup.add_node(ViewerGroup(base_name, commongroup))
        else:
            commongroup.add_node(ViewerDataset(base_name, commongroup))


def generate_example_data(name):
    filename = os.path.join(tempfile.gettempdir(), name)
    with h5py_utils.File(filename, mode="w") as nxroot:
        nxroot.attrs["NX_class"] = "NXroot"
        nxroot.attrs["creator"] = "test"
        nxroot.attrs["default"] = "2.1"

        # 1D data
        nxentry = nxroot.create_group("1.1")
        nxentry.attrs["NX_class"] = "NXroot"
        nxentry.attrs["default"] = "plot"
        nxentry["title"] = "ascan samx 0 3 3 0.1"

        measurement = nxentry.create_group("measurement")
        measurement.attrs["NX_class"] = "NXcollection"
        measurement["samx"] = [0, 1, 2, 3]
        measurement["diode1"] = [0, -1, -2, -3]
        measurement["diode2"] = [3, 1, 2, 0]

        nxdata = nxentry.create_group("plot")
        nxdata.attrs["NX_class"] = "NXdata"
        nxdata.attrs["signal"] = "diode1"
        nxdata.attrs["auxiliary_signals"] = ["diode2"]
        nxdata.attrs["axes"] = ["samx"]
        nxdata["samx"] = h5py.SoftLink(measurement["samx"].name)
        nxdata["diode1"] = h5py.SoftLink(measurement["diode1"].name)
        nxdata["diode2"] = h5py.SoftLink(measurement["diode2"].name)

        # 2D data
        nxentry = nxroot.create_group("2.1")
        nxentry.attrs["NX_class"] = "NXroot"
        nxentry.attrs["default"] = "plot"
        nxentry["title"] = "amesh samx 0 3 3 samy 0 4 4 0.1"

        measurement = nxentry.create_group("measurement")
        measurement.attrs["NX_class"] = "NXcollection"
        measurement["samx"] = [0, 0.1, 0.2, 0.3]
        measurement["samy"] = [0, 0.1, 0.2, 0.3, 0.4]
        measurement["diode1"] = numpy.zeros((4, 5))
        measurement["diode2"] = numpy.ones((4, 5))

        nxdata = nxentry.create_group("plot")
        nxdata.attrs["NX_class"] = "NXdata"
        nxdata.attrs["signal"] = "diode1"
        nxdata.attrs["auxiliary_signals"] = ["diode2"]
        nxdata.attrs["axes"] = ["samx", "samy"]
        nxdata["samx"] = h5py.SoftLink(measurement["samx"].name)
        nxdata["samx_indices"] = 0
        nxdata["samy"] = h5py.SoftLink(measurement["samy"].name)
        nxdata["samy_indices"] = 1
        nxdata["diode1"] = h5py.SoftLink(measurement["diode1"].name)
        nxdata["diode2"] = h5py.SoftLink(measurement["diode2"].name)

    return filename


def main(argv=None) -> Optional[int]:
    import argparse

    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(
        description="Load HDF5 files and display their structure."
    )
    parser.add_argument("files", nargs="*", help="List of HDF5 files to load.")
    parser.add_argument(
        "--example", action="store_true", help="Generate and open example data."
    )
    args = parser.parse_args(args=argv[1:])

    files = args.files
    if args.example:
        files.insert(0, generate_example_data("data_viewer_example.h5"))

    app = QtWidgets.QApplication(argv)
    dataviewer = DataViewer()
    dataviewer.resize(1300, 500)
    dataviewer._Viewer__splitter.setSizes([500, 800])
    for filename in files:
        dataviewer.appendFile(filename)
    dataviewer.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
