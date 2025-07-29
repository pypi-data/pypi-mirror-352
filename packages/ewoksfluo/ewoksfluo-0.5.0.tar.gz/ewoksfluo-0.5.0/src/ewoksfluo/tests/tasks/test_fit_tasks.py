import h5py
import pytest
from ewoksorange.tests.utils import execute_task

from orangecontrib.ewoksfluo.categories.fit.fit_single_scan_single_det import (
    OWFitSingleScanSingleDetector,
)
from orangecontrib.ewoksfluo.categories.fit.fit_single_scan_multi_det import (
    OWFitSingleScanMultiDetector,
)
from orangecontrib.ewoksfluo.categories.fit.fit_multi_scan_single_det import (
    OWFitStackSingleDetector,
)
from orangecontrib.ewoksfluo.categories.fit.fit_multi_scan_multi_det import (
    OWFitStackMultiDetector,
)

from .. import utils

TASK_CLASSES_BY_SHAPE = {
    (1, 1): OWFitSingleScanSingleDetector,
    (1, 2): OWFitSingleScanMultiDetector,
    (2, 1): OWFitStackSingleDetector,
    (2, 2): OWFitStackMultiDetector,
}


@pytest.mark.parametrize("nscans", [1, 2])
@pytest.mark.parametrize("ndetectors", [1, 2])
def test_fit_tasks(tmpdir, nscans, ndetectors):
    _test_example_xrf_scan(tmpdir, nscans, ndetectors)


@pytest.mark.parametrize("nscans", [1, 2])
@pytest.mark.parametrize("ndetectors", [1, 2])
def test_fit_tasks_widget(tmpdir, qtapp, nscans, ndetectors):
    _test_example_xrf_scan(tmpdir, nscans, ndetectors, widget=True)


def _test_example_xrf_scan(tmpdir, nscans, ndetectors, widget: bool = False):
    task_cls = TASK_CLASSES_BY_SHAPE[(nscans, ndetectors)]
    if not widget:
        task_cls = task_cls.ewokstaskclass

    _, _, _, config = utils.generate_data(
        tmpdir, 10, 8.5, nscans=nscans, ndetectors=ndetectors
    )

    filename = str(tmpdir / "output.h5")
    inputs = {
        "quantification": True,
        "fast_fitting": True,
        "diagnostics": True,
        "xrf_spectra_uri_template": "measurement/{}",
    }

    if nscans == 1 and ndetectors == 1:
        inputs["bliss_scan_uri"] = f"{str(tmpdir / 'spectra.h5')}::/1.1"
        inputs["output_root_uri"] = f"{filename}::/1.1"
        inputs["detector_name"] = "mca00"
        inputs["config"] = config
    if nscans > 1 and ndetectors == 1:
        inputs["bliss_scan_uris"] = [
            f"{str(tmpdir / 'spectra.h5')}::/{scan}.1" for scan in range(1, nscans + 1)
        ]
        inputs["output_root_uri"] = f"{filename}::/1.1"
        inputs["detector_name"] = "mca00"
        inputs["config"] = config
    if nscans == 1 and ndetectors > 1:
        inputs["bliss_scan_uri"] = f"{str(tmpdir / 'spectra.h5')}::/1.1"
        inputs["output_root_uri"] = f"{filename}::/1.1"
        inputs["detector_names"] = [
            f"mca{detector:02d}" for detector in range(ndetectors)
        ]
        inputs["configs"] = [config] * ndetectors
    if nscans >= 1 and ndetectors > 1:
        inputs["bliss_scan_uris"] = [
            f"{str(tmpdir / 'spectra.h5')}::/{scan}.1" for scan in range(1, nscans + 1)
        ]
        inputs["output_root_uri"] = f"{filename}::/1.1"
        inputs["detector_names"] = [
            f"mca{detector:02d}" for detector in range(ndetectors)
        ]
        inputs["configs"] = [config] * ndetectors

    for _ in range(2):  # Repeat twice to test overwrite
        outputs = execute_task(task_cls, inputs)
        expected = expected_task_outputs(nscans, ndetectors, tmpdir, inputs)
        assert outputs == expected

        with h5py.File(filename) as f:
            content = utils.h5content(f)

        expected = expected_h5content(nscans, ndetectors)
        assert content == expected


def expected_task_outputs(nscans, ndetectors, tmpdir, inputs):
    filename = str(tmpdir / "output.h5")
    outputs = dict()

    if ndetectors == 1:
        detector_name = inputs["detector_name"]
        outputs["xrf_results_uri"] = f"{filename}::/1.1/fit/{detector_name}/results"
        outputs["detector_name"] = detector_name
        outputs["output_root_uri"] = f"{filename}::/1.1"
    else:
        outputs["xrf_results_uris"] = [
            f"{filename}::/1.1/fit/mca{detector:02d}/results"
            for detector in range(ndetectors)
        ]
        outputs["detector_names"] = inputs["detector_names"]
        outputs["output_root_uri"] = f"{filename}::/1.1"

    if nscans == 1:
        outputs["bliss_scan_uri"] = inputs["bliss_scan_uri"]
    else:
        outputs["bliss_scan_uris"] = inputs["bliss_scan_uris"]

    return outputs


def expected_h5content(nscans, ndetectors):
    content = {"@attrs": {"NX_class", "default"}}
    fit = {"@attrs": {"NX_class", "default"}}
    entry = {"@attrs": {"NX_class", "default"}, "fit": fit}
    if nscans > 1:
        scan_shape = (2,)
    else:
        scan_shape = tuple()
    content["1.1"] = entry

    nxprocess_content = {
        "@attrs": {"NX_class", "default"},
        "configuration": {
            "@attrs": {"NX_class"},
            "data@shape": (),
            "date@shape": (),
            "type@shape": (),
        },
        "program@shape": (),
        "version@shape": (),
        "results": {
            "@attrs": {"NX_class", "default"},
            "derivatives": {
                "@attrs": {"NX_class", "auxiliary_signals", "axes", "signal"},
                "Al_K@shape": scan_shape + (1024,),
                "Ca_K@shape": scan_shape + (1024,),
                "Ce_L@shape": scan_shape + (1024,),
                "Cl_K@shape": scan_shape + (1024,),
                "Fe_K@shape": scan_shape + (1024,),
                "P_K@shape": scan_shape + (1024,),
                "Pb_M@shape": scan_shape + (1024,),
                "S_K@shape": scan_shape + (1024,),
                "Scatter_Compton000@shape": scan_shape + (1024,),
                "Scatter_Peak000@shape": scan_shape + (1024,),
                "Si_K@shape": scan_shape + (1024,),
                "Ti_K@shape": scan_shape + (1024,),
                "energy@attrs": {"units"},
                "energy@shape": (1024,),
            },
            "diagnostics": {
                "@attrs": {"NX_class", "auxiliary_signals", "signal"},
                "nFreeParameters@shape": scan_shape + (10,),
                "nObservations@shape": scan_shape + (10,),
            },
            "fit": {
                "@attrs": {
                    "NX_class",
                    "auxiliary_signals",
                    "axes",
                    "interpretation",
                    "signal",
                },
                "data@shape": scan_shape + (10, 1024),
                "energy@attrs": {"units"},
                "energy@shape": (1024,),
                "model@shape": scan_shape + (10, 1024),
                "residuals@shape": scan_shape + (10, 1024),
            },
            "massfractions": {
                "@attrs": {"NX_class", "auxiliary_signals", "signal"},
                "Al_K@shape": scan_shape + (10,),
                "Ca_K@shape": scan_shape + (10,),
                "Ce_L@shape": scan_shape + (10,),
                "Cl_K@shape": scan_shape + (10,),
                "Fe_K@shape": scan_shape + (10,),
                "P_K@shape": scan_shape + (10,),
                "Pb_M@shape": scan_shape + (10,),
                "S_K@shape": scan_shape + (10,),
                "Si_K@shape": scan_shape + (10,),
                "Ti_K@shape": scan_shape + (10,),
            },
            "parameters": {
                "@attrs": {"NX_class", "auxiliary_signals", "signal"},
                "Al_K@shape": scan_shape + (10,),
                "Ca_K@shape": scan_shape + (10,),
                "Ce_L@shape": scan_shape + (10,),
                "Cl_K@shape": scan_shape + (10,),
                "Fe_K@shape": scan_shape + (10,),
                "P_K@shape": scan_shape + (10,),
                "Pb_M@shape": scan_shape + (10,),
                "S_K@shape": scan_shape + (10,),
                "Scatter_Compton000@shape": scan_shape + (10,),
                "Scatter_Peak000@shape": scan_shape + (10,),
                "Si_K@shape": scan_shape + (10,),
                "Ti_K@shape": scan_shape + (10,),
            },
            "uncertainties": {
                "@attrs": {"NX_class", "auxiliary_signals", "signal"},
                "Al_K@shape": scan_shape + (10,),
                "Ca_K@shape": scan_shape + (10,),
                "Ce_L@shape": scan_shape + (10,),
                "Cl_K@shape": scan_shape + (10,),
                "Fe_K@shape": scan_shape + (10,),
                "P_K@shape": scan_shape + (10,),
                "Pb_M@shape": scan_shape + (10,),
                "S_K@shape": scan_shape + (10,),
                "Scatter_Compton000@shape": scan_shape + (10,),
                "Scatter_Peak000@shape": scan_shape + (10,),
                "Si_K@shape": scan_shape + (10,),
                "Ti_K@shape": scan_shape + (10,),
            },
        },
    }
    for detector in range(ndetectors):
        fit[f"mca{detector:02d}"] = nxprocess_content
    return content
