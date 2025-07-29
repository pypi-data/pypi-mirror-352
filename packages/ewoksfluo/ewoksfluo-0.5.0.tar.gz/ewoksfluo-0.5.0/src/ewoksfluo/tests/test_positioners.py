import h5py
import pytest

from ..tasks import positioner_utils


@pytest.fixture(scope="module")
def example_bliss_scan_uri(tmpdir_factory):
    filename = str(tmpdir_factory.mktemp("test_positioners").join("data.h5"))
    with h5py.File(filename, mode="w") as root:
        dset = root.create_dataset(
            "/1.1/instrument/positioners_start/energy", data=10.0
        )
        dset.attrs["units"] = "keV"
        dset = root.create_dataset("/1.1/instrument/other/name", data=11.0)
    return f"{filename}::/1.1"


def test_get_energy(example_bliss_scan_uri):
    assert positioner_utils.get_energy(example_bliss_scan_uri) == 10.0
    assert positioner_utils.get_energy(example_bliss_scan_uri, "energy") == 10.0
    assert (
        positioner_utils.get_energy(
            example_bliss_scan_uri, "energy", "instrument/positioners_start/{}"
        )
        == 10.0
    )
    assert (
        positioner_utils.get_energy(
            example_bliss_scan_uri, "name", "instrument/other/{}"
        )
        == 11.0
    )


def test_get_energy_suburi(example_bliss_scan_uri):
    assert (
        positioner_utils.get_energy_suburi(example_bliss_scan_uri)
        == "instrument/positioners_start/energy"
    )
