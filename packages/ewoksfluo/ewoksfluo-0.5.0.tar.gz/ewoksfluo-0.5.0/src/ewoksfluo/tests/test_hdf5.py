from ewoksfluo.io import hdf5


def test_join_h5url():
    assert hdf5.join_h5url("filename.h5", "") == "filename.h5::/"
    assert hdf5.join_h5url("filename.h5::/", "/") == "filename.h5::/"

    assert hdf5.join_h5url("filename.h5", "1.1") == "filename.h5::/1.1"
    assert hdf5.join_h5url("filename.h5::/", "/1.1/") == "filename.h5::/1.1"
