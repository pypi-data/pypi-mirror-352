# TODO: copied from ewoksxrpd with a different (instrument group is not linked directly) -> extract to ewoksdata

import os
from typing import Union

import h5py
from silx.io.url import DataUrl
from blissdata.h5api import dynamic_hdf5


def create_hdf5_link(
    parent: h5py.Group,
    link_name: str,
    target: Union[h5py.Dataset, h5py.Group],
    relative: bool = True,
    raise_on_exists: bool = False,
) -> None:
    """
    :param parent: HDF5 group in which the link will be created
    :param link_name: relative HDF5 path of the link source with respect to :code:`parent`
    :param target: absolute HDF5 path of the link target
    :param relative: determines whether the external or internal link is absolute or relative.
                     Internal links that refer upwards are not supported and will always be absolute.
    :param raise_on_exists: raise exception when :code:`link_name` already exists
    """
    link = hdf5_link_object(
        _get_hdf5_filename(parent.file),
        parent.name,
        link_name,
        _get_hdf5_filename(target.file),
        target.name,
        relative=relative,
    )
    if link is None:
        # Link refers to itself
        return
    if link_name in parent and not raise_on_exists:
        # Name already exists and is not necessarily equivalent to the link we want to create
        return
    parent[link_name] = link


def _get_hdf5_filename(file_obj) -> str:
    try:
        return file_obj.filename
    except AttributeError:
        # to be fixed in blissdata
        return file_obj._retry_handler.file_obj.filename


def hdf5_link_object(
    parent_filename: str,
    parent_name: str,
    link_name: str,
    target_filename: str,
    target_name: str,
    relative: bool = True,
) -> Union[None, h5py.ExternalLink, h5py.SoftLink]:
    """
    :param parent_filename: HDF5 filename in which the link will be created
    :param parent_name: absolute HDF5 group path in :code:`parent_filename`
    :param link_name: relative HDF5 path of the link source with respect to :code:`parent_name`
    :param target_filename: HDF5 filename in which the link target is located
    :param target_name: absolute HDF5 path in :code:`target_filename` of the link target
    :param relative: determines whether the external or internal link is absolute or relative.
                     Internal links that refer upwards are not supported and will always be absolute.
    :returns: Internal or external link object to be used to create the HDF5 link.
              Returns :code:`None` when the link refers to itself.
    """
    abs_parent_filename = os.path.abspath(parent_filename)
    target_is_absolute = os.path.isabs(target_filename)
    if target_is_absolute:
        abs_target_filename = target_filename
    else:
        abs_target_filename = os.path.join(
            os.path.dirname(abs_parent_filename), target_filename
        )

    # Internal link
    if os.path.normpath(abs_parent_filename) == os.path.normpath(abs_target_filename):
        link_full_name = _normalize_hdf5_item_name(parent_name, link_name)
        target_name = _normalize_hdf5_item_name(target_name)
        if link_full_name == target_name:
            # Link refers to itself
            return
        if not relative:
            return h5py.SoftLink(target_name)
        rel_target_name = os.path.relpath(target_name, parent_name)
        if ".." in rel_target_name:
            # Internal links upwards are not supported
            return h5py.SoftLink(target_name)
        return h5py.SoftLink(rel_target_name)

    # External link
    if relative:
        target_filename = os.path.relpath(
            abs_target_filename, os.path.dirname(abs_parent_filename)
        )
    else:
        target_filename = abs_target_filename
    return h5py.ExternalLink(target_filename, target_name)


def _normalize_hdf5_item_name(*parts) -> str:
    name = "/".join([s for part in parts for s in part.split("/") if s])
    return f"/{name}"


def link_bliss_scan(
    outentry: h5py.Group, bliss_scan_url: Union[str, DataUrl], **options
):
    if isinstance(bliss_scan_url, str):
        bliss_scan_url = DataUrl(bliss_scan_url)
    file_path = bliss_scan_url.file_path()
    data_path = bliss_scan_url.data_path()
    with dynamic_hdf5.File(file_path, mode="r", **options) as root:
        inentry = root[data_path]
        # Link to the entire group
        for groupname in ("sample",):
            try:
                if groupname in outentry or groupname not in inentry:
                    continue
            except Exception:  # fixed by bliss PR !5435
                continue
            create_hdf5_link(outentry, groupname, inentry[groupname])

        # Link to all sub groups
        for groupname in ("measurement", "instrument"):
            if groupname not in inentry:
                continue
            igroup = inentry[groupname]
            if groupname in outentry:
                ogroup = outentry[groupname]
            else:
                ogroup = outentry.create_group(groupname)
                ogroup.attrs["NX_class"] = igroup.attrs["NX_class"]
            for name in igroup.keys():
                if name in ogroup:
                    continue
                if name not in ogroup:
                    create_hdf5_link(ogroup, name, igroup[name])
