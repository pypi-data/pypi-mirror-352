import h5py
import pytest
from ewoksorange.tests.utils import execute_task

from orangecontrib.ewoksfluo.categories.demo.mesh_single_scan_single_det import (
    OWMeshSingleScanSingleDetector,
)
from orangecontrib.ewoksfluo.categories.demo.mesh_single_scan_multi_det import (
    OWMeshSingleScanMultiDetector,
)
from orangecontrib.ewoksfluo.categories.demo.mesh_stack_single_det import (
    OWMeshStackSingleDetector,
)
from orangecontrib.ewoksfluo.categories.demo.mesh_stack_multi_det import (
    OWMeshStackMultiDetector,
)
from orangecontrib.ewoksfluo.categories.demo.mosaic_mesh_single_det import (
    OWMosaicMeshSingleDetector,
)
from orangecontrib.ewoksfluo.categories.demo.mosaic_mesh_multi_det import (
    OWMosaicMeshMultiDetector,
)

from .. import utils

_TASK_CLASSES = {
    OWMeshSingleScanSingleDetector: {"nscans": 1, "ndetectors": 1, "mosaic": None},
    OWMeshSingleScanMultiDetector: {"nscans": 1, "ndetectors": 2, "mosaic": None},
    OWMeshStackSingleDetector: {"nscans": 2, "ndetectors": 1, "mosaic": None},
    OWMeshStackMultiDetector: {"nscans": 2, "ndetectors": 2, "mosaic": None},
    OWMosaicMeshSingleDetector: {"nscans": 1, "ndetectors": 1, "mosaic": (2, 3)},
    OWMosaicMeshMultiDetector: {"nscans": 1, "ndetectors": 2, "mosaic": (2, 3)},
}


@pytest.mark.parametrize("task_cls", _TASK_CLASSES)
def test_mesh_tasks(tmpdir, task_cls):
    _test_example_xrf_scan(tmpdir, task_cls)


@pytest.mark.parametrize("task_cls", _TASK_CLASSES)
def test_mesh_tasks_widget(tmpdir, qtapp, task_cls):
    _test_example_xrf_scan(tmpdir, task_cls, widget=True)


def _test_example_xrf_scan(tmpdir, task_cls, widget: bool = False):
    params = _TASK_CLASSES[task_cls]
    nscans = params["nscans"]
    ndetectors = params["ndetectors"]
    mosaic = params["mosaic"]

    if not widget:
        task_cls = task_cls.ewokstaskclass
    filename = str(tmpdir / "test.h5")
    inputs = {
        "output_filename": filename,
        "rois": [(100, 200), (300, 600)],
        "emission_line_groups": ["Si-K", "Ca-K", "Ce-L", "Fe-K"],
    }
    if ndetectors > 1:
        inputs["ndetectors"] = ndetectors
    if nscans > 1:
        inputs["nscans"] = nscans
    if mosaic:
        inputs["mosaic"] = mosaic
        npoints = 500  # 50//mosaic[0] * 60//mosaic[1]
        nscans_total = nscans * mosaic[0] * mosaic[1]
    else:
        npoints = 3000  # 50 * 60
        nscans_total = nscans

    for _ in range(2):  # Repeat twice to test overwrite
        outputs = execute_task(task_cls, inputs)
        assert outputs == expected_task_outputs(nscans, ndetectors, mosaic, tmpdir)

        with h5py.File(filename) as f:
            content = utils.h5content(f)

        expected_content = expected_h5content(nscans_total, npoints, ndetectors)

        assert content == expected_content


def expected_task_outputs(nscans, ndetectors, mosaic, tmpdir):
    filename = str(tmpdir / "test.h5")
    outputs = {
        "config": f"{filename}::/1.1/theory/configuration/data",
        "expo_time": 0.1,
        "monitor_name": "I0",
    }
    if mosaic and ndetectors == 1:
        nscans = mosaic[0] * mosaic[1]
        return {
            "detector_name": "mca0",
            "filenames": [filename],
            "scan_ranges": [[1, nscans]],
            "monitor_normalization_template": "1000000/<instrument/{}/data>",
            "detector_normalization_template": "0.1/<instrument/{}/live_time>",
            **outputs,
        }
    if mosaic and ndetectors > 1:
        nscans = mosaic[0] * mosaic[1]
        return {
            "configs": [f"{filename}::/1.1/theory/configuration/data"] * ndetectors,
            "detector_names": ["mca0", "mca1"],
            "filenames": [filename],
            "scan_ranges": [[1, nscans]],
            "monitor_normalization_template": "1000000/<instrument/{}/data>",
            "detector_normalization_template": "0.1/<instrument/{}/live_time>",
            **outputs,
        }
    if nscans == 1 and ndetectors == 1:
        return {
            "detector_name": "mca0",
            "filename": filename,
            "scan_number": 1,
            "monitor_normalization_template": "1000000/<instrument/{}/data>",
            "detector_normalization_template": "0.1/<instrument/{}/live_time>",
            **outputs,
        }
    if nscans > 1 and ndetectors == 1:
        return {
            "detector_name": "mca0",
            "filenames": [filename],
            "scan_ranges": [[1, nscans]],
            "monitor_normalization_template": "1000000/<instrument/{}/data>",
            "detector_normalization_template": "0.1/<instrument/{}/live_time>",
            **outputs,
        }
    if nscans == 1 and ndetectors > 1:
        return {
            "configs": [f"{filename}::/1.1/theory/configuration/data"] * ndetectors,
            "detector_names": ["mca0", "mca1"],
            "filename": filename,
            "scan_number": 1,
            "monitor_normalization_template": "1000000/<instrument/{}/data>",
            "detector_normalization_template": "0.1/<instrument/{}/live_time>",
            **outputs,
        }
    if nscans > 1 and ndetectors > 1:
        return {
            "configs": [f"{filename}::/1.1/theory/configuration/data"] * ndetectors,
            "detector_names": ["mca0", "mca1"],
            "filenames": [filename],
            "scan_ranges": [[1, nscans]],
            "monitor_normalization_template": "1000000/<instrument/{}/data>",
            "detector_normalization_template": "0.1/<instrument/{}/live_time>",
            **outputs,
        }


def expected_h5content(nscans, npoints, ndetectors):
    content = {"@attrs": {"NX_class", "creator"}}

    mca_detector = {
        "@attrs": {"NX_class"},
        "data@shape": (npoints, 1024),
        "elapsed_time@shape": (npoints,),
        "event_count_rate@shape": (npoints,),
        "events@shape": (npoints,),
        "fractional_dead_time@shape": (npoints,),
        "live_time@shape": (npoints,),
        "roi1@shape": (npoints,),
        "roi2@shape": (npoints,),
        "spectrum@shape": (npoints, 1024),
        "trigger_count_rate@shape": (npoints,),
        "trigger_live_time@shape": (npoints,),
        "triggers@shape": (npoints,),
    }

    mca_meas = {
        "mca{detector}@shape": (npoints, 1024),
        "mca{detector}_elapsed_time@shape": (npoints,),
        "mca{detector}_event_count_rate@shape": (npoints,),
        "mca{detector}_events@shape": (npoints,),
        "mca{detector}_fractional_dead_time@shape": (npoints,),
        "mca{detector}_live_time@shape": (npoints,),
        "mca{detector}_roi1@shape": (npoints,),
        "mca{detector}_roi2@shape": (npoints,),
        "mca{detector}_trigger_count_rate@shape": (npoints,),
        "mca{detector}_trigger_live_time@shape": (npoints,),
        "mca{detector}_triggers@shape": (npoints,),
    }

    for scan in range(1, nscans + 1):
        scan_content = {
            "@attrs": {"NX_class"},
            "instrument": {
                "@attrs": {"NX_class"},
                "I0": {"@attrs": {"NX_class"}, "data@shape": (npoints,)},
                "positioners": {
                    "@attrs": {"NX_class"},
                    "energy@attrs": {"units"},
                    "energy@shape": (),
                    "sampy@attrs": {"units"},
                    "sampy@shape": (npoints,),
                    "sampz@attrs": {"units"},
                    "sampz@shape": (npoints,),
                },
                "positioners_start": {
                    "@attrs": {"NX_class"},
                    "energy@attrs": {"units"},
                    "energy@shape": (),
                    "sampy@attrs": {"units"},
                    "sampy@shape": (),
                    "sampz@attrs": {"units"},
                    "sampz@shape": (),
                },
                "positioners_end": {
                    "@attrs": {"NX_class"},
                    "energy@attrs": {"units"},
                    "energy@shape": (),
                    "sampy@attrs": {"units"},
                    "sampy@shape": (),
                    "sampz@attrs": {"units"},
                    "sampz@shape": (),
                },
                "sampy": {
                    "@attrs": {"NX_class"},
                    "value@attrs": {"units"},
                    "value@shape": (npoints,),
                },
                "sampz": {
                    "@attrs": {"NX_class"},
                    "value@attrs": {"units"},
                    "value@shape": (npoints,),
                },
            },
            "measurement": {
                "@attrs": {"NX_class"},
                "I0@shape": (npoints,),
                "sampy@attrs": {"units"},
                "sampy@shape": (npoints,),
                "sampz@attrs": {"units"},
                "sampz@shape": (npoints,),
            },
            "theory": {
                "@attrs": {"NX_class"},
                "configuration": {
                    "@attrs": {"NX_class"},
                    "data@shape": (),
                    "type@shape": (),
                },
                "description": {
                    "@attrs": {"NX_class"},
                    "data@shape": (),
                    "type@shape": (),
                },
                "I0_reference@shape": (),
                "parameters": {
                    "@attrs": {"NX_class", "auxiliary_signals", "axes", "signal"},
                    "Ca-K@shape": (npoints,),
                    "Ce-L@shape": (npoints,),
                    "Compton000@shape": (npoints,),
                    "Fe-K@shape": (npoints,),
                    "Peak000@shape": (npoints,),
                    "Si-K@shape": (npoints,),
                    "sampy@attrs": {"units"},
                    "sampy@shape": (npoints,),
                    "sampz@attrs": {"units"},
                    "sampz@shape": (npoints,),
                },
                "parameters_norm": {
                    "@attrs": {"NX_class", "auxiliary_signals", "axes", "signal"},
                    "Ca-K@shape": (npoints,),
                    "Ce-L@shape": (npoints,),
                    "Compton000@shape": (npoints,),
                    "Fe-K@shape": (npoints,),
                    "Peak000@shape": (npoints,),
                    "Si-K@shape": (npoints,),
                    "sampy@attrs": {"units"},
                    "sampy@shape": (npoints,),
                    "sampz@attrs": {"units"},
                    "sampz@shape": (npoints,),
                },
                "rois": {
                    "@attrs": {"NX_class", "auxiliary_signals", "axes", "signal"},
                    "roi1@shape": (npoints,),
                    "roi2@shape": (npoints,),
                    "sampy@attrs": {"units"},
                    "sampy@shape": (npoints,),
                    "sampz@attrs": {"units"},
                    "sampz@shape": (npoints,),
                },
                "rois_norm": {
                    "@attrs": {"NX_class", "auxiliary_signals", "axes", "signal"},
                    "roi1@shape": (npoints,),
                    "roi2@shape": (npoints,),
                    "sampy@attrs": {"units"},
                    "sampy@shape": (npoints,),
                    "sampz@attrs": {"units"},
                    "sampz@shape": (npoints,),
                },
            },
            "title@shape": (),
            "end_time@shape": (),
        }

        content[f"{scan}.1"] = scan_content
        for detector in range(ndetectors):
            scan_content["instrument"][f"mca{detector}"] = mca_detector
            add = {k.format(detector=detector): v for k, v in mca_meas.items()}
            scan_content["measurement"].update(add)

    return content
