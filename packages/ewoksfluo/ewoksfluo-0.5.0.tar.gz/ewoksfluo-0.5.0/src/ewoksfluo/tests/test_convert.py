from contextlib import contextmanager

import numpy
import h5py
import fabio
import pytest
from ewoksorange.tests.utils import execute_task

from ..io.convert import spec_to_bliss
from orangecontrib.ewoksfluo.categories.input.spec_to_bliss import OWSpecToBliss
from ewoksfluo.tasks.example_data.deadtime import apply_extendable_deadtime


def test_spec_to_bliss(tmpdir):
    with _assert_spec_to_bliss(tmpdir) as (spec_filename, bliss_filename, scans):
        spec_to_bliss(spec_filename, bliss_filename, scans, mode="w")


@pytest.mark.parametrize("fluoxas", [True, False])
def test_xia_spec_to_bliss(tmpdir, fluoxas):
    with _assert_spec_to_bliss_with_xia(tmpdir, fluoxas=fluoxas) as (
        spec_filename,
        bliss_filename,
        scans,
    ):
        spec_to_bliss(spec_filename, bliss_filename, scans, mode="w")


def test_spec_to_bliss_task(tmpdir):
    with _assert_spec_to_bliss(tmpdir) as (spec_filename, bliss_filename, scans):
        inputs = {
            "input_filename": spec_filename,
            "output_filename": bliss_filename,
            "scans": scans,
        }
        execute_task(OWSpecToBliss.ewokstaskclass, inputs)


def test_spec_to_bliss_widget(tmpdir, qtapp):
    with _assert_spec_to_bliss(tmpdir) as (spec_filename, bliss_filename, scans):
        inputs = {
            "input_filename": spec_filename,
            "output_filename": bliss_filename,
            "scans": scans,
        }
        execute_task(OWSpecToBliss, inputs, timeout=10)


@pytest.mark.parametrize("fluoxas", [True, False])
def test_xia_spec_to_bliss_task(tmpdir, fluoxas):
    with _assert_spec_to_bliss_with_xia(tmpdir, fluoxas=fluoxas) as (
        spec_filename,
        bliss_filename,
        scans,
    ):
        inputs = {
            "input_filename": spec_filename,
            "output_filename": bliss_filename,
            "scans": scans,
        }
        execute_task(OWSpecToBliss.ewokstaskclass, inputs)


@pytest.mark.parametrize("fluoxas", [True, False])
def test_xia_spec_to_bliss_widget(tmpdir, fluoxas, qtapp):
    with _assert_spec_to_bliss_with_xia(tmpdir, fluoxas=fluoxas) as (
        spec_filename,
        bliss_filename,
        scans,
    ):
        inputs = {
            "input_filename": spec_filename,
            "output_filename": bliss_filename,
            "scans": scans,
        }
        execute_task(OWSpecToBliss, inputs)


@contextmanager
def _assert_spec_to_bliss(tmpdir):
    spec_filename = str(tmpdir / "spec.dat")
    bliss_filename = str(tmpdir / "spec.h5")
    samx = numpy.random.randint(0, 100, size=11)
    I0 = numpy.random.randint(0, 100, size=11)
    IC = numpy.random.randint(0, 100, size=11)
    samz = numpy.arange(11)

    with open(spec_filename, mode="w") as f:
        f.write(f"#F {spec_filename}\n")
        f.write("\n")
        f.write("#O0 samx  samy\n")
        f.write("\n")
        f.write("#S 1 ascan samz 0 10 10 0.1\n")
        f.write("#P0 1.2  2.3\n")
        f.write("#N 100\n")
        f.write("#L samx  zap_p201_I0  zap_p201_IC\n")
        for line in numpy.stack([samx, I0, IC], axis=1):
            f.write("  ".join(list(map(str, line))) + "\n")

    yield spec_filename, bliss_filename, 1

    with h5py.File(bliss_filename, mode="r") as f:
        data = f["/1.1/measurement/samx"][()]
        numpy.testing.assert_array_equal(data, samx)
        data = f["/1.1/instrument/samx/value"][()]
        numpy.testing.assert_array_equal(data, samx)
        data = f["/1.1/instrument/positioners/samx"][()]
        numpy.testing.assert_array_equal(data, samx)

        data = f["/1.1/measurement/samz"][()]
        numpy.testing.assert_array_equal(data, samz)
        data = f["/1.1/instrument/samz/value"][()]
        numpy.testing.assert_array_equal(data, samz)
        data = f["/1.1/instrument/positioners/samz"][()]
        numpy.testing.assert_array_equal(data, samz)

        data = f["/1.1/measurement/I0"][()]
        numpy.testing.assert_array_equal(data, I0)
        data = f["/1.1/instrument/I0/data"][()]
        numpy.testing.assert_array_equal(data, I0)

        data = f["/1.1/measurement/IC"][()]
        numpy.testing.assert_array_equal(data, IC)
        data = f["/1.1/instrument/IC/data"][()]
        numpy.testing.assert_array_equal(data, IC)

        assert f["/1.1/instrument/positioners_start/samx"][()] == 1.2
        assert f["/1.1/instrument/positioners_start/samy"][()] == 2.3
        assert f["/1.1/instrument/positioners/samy"][()] == 2.3


@contextmanager
def _assert_spec_to_bliss_with_xia(tmpdir, fluoxas: bool = False):
    spec_filename = str(tmpdir / "spec.dat")
    bliss_filename = str(tmpdir / "spec.h5")

    with open(spec_filename, mode="w") as f:
        f.write(f"#F {spec_filename}\n")
        f.write("\n")
        f.write("#O0 samx  samy\n")
        f.write("\n")
        if fluoxas:
            f.write("#S 1 fXAS_scan 17.0 17.0\n")
        else:
            f.write("#S 1 zapimage  sampy 0 5 6 100 sampz 0 4 4 0\n")

        f.write("#P0 1.2  2.3\n")
        if fluoxas:
            f.write("#N 2\n")
            f.write("#L specctr1  specctr2\n")
            f.write("0 0")  # only to know how many maps in fXAS_scan
        else:
            f.write("#N 0\n")
            f.write("#L\n")
        f.write("#C \n")

        if fluoxas:
            radix = "radix_0001"
            xiadir = tmpdir / radix
            f.write(f"#C DIRECTORY        : {str(xiadir)}\n")
        else:
            radix = "radix"
            xiadir = tmpdir / "xia"
            f.write(f"#C DIRECTORY        : {str(xiadir)}\n")
            f.write(f"#C RADIX            : {radix}\n")
            f.write("#C ZAP SCAN NUMBER  : 10\n")
            f.write("#C ZAP IMAGE NUMBER : 0\n")
        xiadir.mkdir()

    nrows = 5
    ncols = 6
    ndet = 2
    nchan = 7

    # Simulate a Dual-Channel signal processor with paralyzable dead time
    photons = numpy.random.randint(1000, 5000, size=(nrows, ncols, ndet))
    elapsed_time = numpy.ones((nrows, ncols, ndet))  # seconds
    triggers = apply_extendable_deadtime(photons, elapsed_time, 0.1)
    events = apply_extendable_deadtime(photons, elapsed_time, 20)
    dt_triggers = (photons - triggers) / photons
    dt_events = (photons - events) / photons
    trigger_live_time = elapsed_time - dt_triggers * elapsed_time
    live_time = elapsed_time - dt_events * elapsed_time
    trigger_count_rate = triggers / trigger_live_time
    event_count_rate = events / elapsed_time

    # XIA stores these at unit32
    detnr = numpy.zeros((nrows, ncols, ndet), dtype=numpy.uint32)
    for det in range(ndet):
        detnr[..., det] = det
    xiast = numpy.stack(
        [
            detnr,
            events,
            (trigger_count_rate + 0.5).astype(numpy.uint32),
            (event_count_rate + 0.5).astype(numpy.uint32),
            (trigger_live_time * 1000 + 0.5).astype(numpy.uint32),
            (dt_events * 100 + 0.5).astype(numpy.uint32),
        ],
        axis=-1,
    )
    xiast = xiast.reshape((nrows, ncols, ndet * 6))

    # MCA and counters
    xiamca = numpy.random.randint(1000, 5000, size=(nrows, ndet, ncols, nchan))
    tika = numpy.random.randint(1000, 5000, size=(ndet, nrows, ncols))
    I0 = numpy.random.randint(1000, 5000, size=(nrows, ncols))
    IC = numpy.random.randint(1000, 5000, size=(nrows, ncols))
    if not fluoxas:
        sampy = numpy.tile(numpy.linspace(0.5, ncols - 1.5, ncols), nrows)
        sampz = numpy.repeat(numpy.arange(nrows), ncols)

    # Save as EDF's
    header = {"energy": 17.0}
    for line, (stdata, mcadata) in enumerate(zip(xiast, xiamca)):
        filename = str(xiadir / f"{radix}_xiast_{10:04d}_{0:04d}_{line:04d}.edf")
        _save_edf(filename, stdata, header)
        for det, data in enumerate(mcadata):
            filename = str(
                xiadir / f"{radix}_xia{det:02d}_{10:04d}_{0:04d}_{line:04d}.edf"
            )
            _save_edf(filename, data, header)
    for det, data in enumerate(tika):
        filename = str(xiadir / f"{radix}_xmap_tika{det:02d}_{10:04d}_{0:04d}.edf")
        _save_edf(filename, data)
    filename = str(xiadir / f"{radix}_zap_p201_I0_{10:04d}_{0:04d}.edf")
    _save_edf(filename, I0)
    filename = str(xiadir / f"{radix}_zap_p201_IC_{10:04d}_{0:04d}.edf")
    _save_edf(filename, IC)
    image = numpy.zeros((10, 11))
    for islow in range(nrows):
        for ifast in range(ncols):
            filename = str(
                xiadir / f"{radix}_frelon2_{10:04d}_{islow:04d}_{ifast:04d}.edf"
            )
            image[0, 0] = islow * ncols + ifast
            _save_edf(filename, image)

    # Convert to HDF5
    yield spec_filename, bliss_filename, 1

    # Validate the conversion
    with h5py.File(bliss_filename, mode="r") as f:
        assert f["/1.1/instrument/positioners_start/samx"][()] == 1.2
        assert f["/1.1/instrument/positioners_start/samy"][()] == 2.3
        assert f["/1.1/instrument/positioners_start/energy"][()] == 17.0
        assert f["/1.1/instrument/positioners/samx"][()] == 1.2
        assert f["/1.1/instrument/positioners/samy"][()] == 2.3
        assert f["/1.1/instrument/positioners/energy"][()] == 17.0

        if not fluoxas:
            data = f["/1.1/measurement/sampz"][()]
            numpy.testing.assert_array_equal(data, sampz)
            data = f["/1.1/instrument/sampz/value"][()]
            numpy.testing.assert_array_equal(data, sampz)
            data = f["/1.1/instrument/positioners/sampz"][()]
            numpy.testing.assert_array_equal(data, sampz)

            data = f["/1.1/measurement/sampy"][()]
            numpy.testing.assert_array_equal(data, sampy)
            data = f["/1.1/instrument/sampy/value"][()]
            numpy.testing.assert_array_equal(data, sampy)
            data = f["/1.1/instrument/positioners/sampy"][()]
            numpy.testing.assert_array_equal(data, sampy)

        data = f["/1.1/measurement/I0"][()]
        numpy.testing.assert_array_equal(data, I0.flatten())
        data = f["/1.1/instrument/I0/data"][()]
        numpy.testing.assert_array_equal(data, I0.flatten())

        data = f["/1.1/measurement/IC"][()]
        numpy.testing.assert_array_equal(data, IC.flatten())
        data = f["/1.1/instrument/IC/data"][()]
        numpy.testing.assert_array_equal(data, IC.flatten())

        for det, roi in enumerate(tika):
            data = f[f"/1.1/instrument/xia_det{det}/tika"][()]
            numpy.testing.assert_array_equal(data, roi.flatten())
            data = f[f"/1.1/measurement/xia_det{det}_tika"][()]
            numpy.testing.assert_array_equal(data, roi.flatten())

        for det in range(ndet):
            data = f[f"/1.1/instrument/xia_det{det}/events"][()]
            numpy.testing.assert_array_equal(data, events[..., det].flatten())
            data = f[f"/1.1/measurement/xia_det{det}_events"][()]
            numpy.testing.assert_array_equal(data, events[..., det].flatten())

            data = f[f"/1.1/instrument/xia_det{det}/triggers"][()]
            numpy.testing.assert_allclose(data, triggers[..., det].flatten(), rtol=1e-3)
            data = f[f"/1.1/measurement/xia_det{det}_triggers"][()]
            numpy.testing.assert_allclose(data, triggers[..., det].flatten(), rtol=1e-3)

            data = f[f"/1.1/instrument/xia_det{det}/event_count_rate"][()]
            numpy.testing.assert_allclose(data, event_count_rate[..., det].flatten())
            data = f[f"/1.1/measurement/xia_det{det}_event_count_rate"][()]
            numpy.testing.assert_allclose(data, event_count_rate[..., det].flatten())

            data = f[f"/1.1/instrument/xia_det{det}/trigger_count_rate"][()]
            numpy.testing.assert_allclose(
                data, trigger_count_rate[..., det].flatten(), rtol=1e-3
            )
            data = f[f"/1.1/measurement/xia_det{det}_trigger_count_rate"][()]
            numpy.testing.assert_allclose(
                data, trigger_count_rate[..., det].flatten(), rtol=1e-3
            )

            data = f[f"/1.1/instrument/xia_det{det}/live_time"][()]
            numpy.testing.assert_allclose(data, live_time[..., det].flatten())
            data = f[f"/1.1/measurement/xia_det{det}_live_time"][()]
            numpy.testing.assert_allclose(data, live_time[..., det].flatten())

            data = f[f"/1.1/instrument/xia_det{det}/trigger_live_time"][()]
            numpy.testing.assert_allclose(
                data, trigger_live_time[..., det].flatten(), rtol=1e-3
            )
            data = f[f"/1.1/measurement/xia_det{det}_trigger_live_time"][()]
            numpy.testing.assert_allclose(
                data, trigger_live_time[..., det].flatten(), rtol=1e-3
            )

            data = f[f"/1.1/instrument/xia_det{det}/elapsed_time"][()]
            numpy.testing.assert_allclose(data, elapsed_time[..., det].flatten())
            data = f[f"/1.1/measurement/xia_det{det}_elapsed_time"][()]
            numpy.testing.assert_allclose(data, elapsed_time[..., det].flatten())

            data = f[f"/1.1/instrument/xia_det{det}/fractional_dead_time"][()]
            numpy.testing.assert_allclose(
                data, dt_events[..., det].flatten(), atol=0.01
            )
            data = f[f"/1.1/measurement/xia_det{det}_fractional_dead_time"][()]
            numpy.testing.assert_allclose(
                data, dt_events[..., det].flatten(), atol=0.01
            )

        data = f["/1.1/measurement/frelon2"][()]
        numpy.testing.assert_array_equal(data[:, 0, 0], range(ncols * nrows))


def _save_edf(filename, data, header=None):
    edf = fabio.edfimage.EdfImage(data=data, header=header)
    edf.write(filename)
