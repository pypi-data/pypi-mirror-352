import os
from typing import Tuple, Union, Optional, Generator
from contextlib import contextmanager

import h5py
from silx.io.url import DataUrl
from silx.io import h5py_utils


def split_h5uri(url: str) -> Tuple[str, str]:
    obj = DataUrl(url)
    return obj.file_path(), obj.data_path() or ""


def join_h5url(root_url: str, sub_url: str) -> str:
    file_path, data_path = split_h5uri(root_url)

    while data_path.endswith("/"):
        data_path = data_path[:-1]
    while data_path.endswith("::"):
        data_path = data_path[:-2]

    while sub_url.startswith("/"):
        sub_url = sub_url[1:]
    while sub_url.endswith("/"):
        sub_url = sub_url[:-1]

    return f"{file_path}::{data_path}/{sub_url}"


class ReadHdf5File(h5py_utils.File):
    """Use in cases where you want to read something from an HDF5 which might be already open for writing."""

    def __init__(self, *args, mode: str = "r", **kwargs):
        assert mode == "r", "must be opened read-only"
        try:
            super().__init__(*args, mode=mode, **kwargs)
        except Exception:
            super().__init__(*args, mode="a", **kwargs)


@contextmanager
def retry_external_link(
    group: h5py.Group, name: str, item: Optional[Union[h5py.Group, h5py.Dataset]] = None
) -> Generator[Union[h5py.Group, h5py.Dataset], None, None]:
    """The file we save results in is opened in append mode. If we access external links to
    the raw Bliss data we might not have permission to open it in append mode (e.g. restored data).
    """
    if item is None:
        try:
            item = group[name]
        except (KeyError, ValueError):
            item = None
    if item is None:
        link = group.get(name, getlink=True)
        if not isinstance(link, h5py.ExternalLink):
            raise RuntimeError(f"Broken link '{group.name}/{name}'")

        external_filename = link.filename
        if not os.path.isabs(external_filename):
            parent_dir = os.path.dirname(group.file.filename)
            external_filename = os.path.abspath(
                os.path.normpath(os.path.join(parent_dir, external_filename))
            )

        with h5py_utils.File(external_filename, mode="r") as f:
            yield f[link.path]
    else:
        yield item
