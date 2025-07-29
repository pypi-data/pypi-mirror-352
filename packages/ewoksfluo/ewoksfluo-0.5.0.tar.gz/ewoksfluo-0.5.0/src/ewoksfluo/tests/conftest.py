import gc
import time
import h5py
import pytest
from ewoksorange.tests.conftest import qtapp  # noqa F401
from ewoksorange.canvas.handler import OrangeCanvasHandler


@pytest.fixture(scope="session")
def ewoks_orange_canvas(qtapp):  # noqa F811
    with OrangeCanvasHandler() as handler:
        yield handler
    # _close_hdf5_files()


def _close_hdf5_files():
    # TODO: ewoksfluo.gui.data_viewer.DataViewer.closeEvent does not get
    #       called so HDF5 stay open and this can cause a SEGFAULT
    while gc.collect():
        time.sleep(0.1)
    for obj in gc.get_objects():
        try:
            b = isinstance(obj, h5py.File)
        except Exception:
            continue
        if b:
            print(f"File object {obj}: filename={obj.filename}")
        if b and obj.id:
            obj.close()
