from typing import List, Dict
from ewoksorange.bindings import ows_to_ewoks
from ewokscore import execute_graph

try:
    from importlib.resources import files as resource_files
except ImportError:
    from importlib_resources import files as resource_files


def test_multi_scan_multi_detector_without_qt(tmpdir):
    from orangecontrib.ewoksfluo.categories.demo import tutorials

    filename = resource_files(tutorials).joinpath("mesh_stack_multi_detector.ows")
    assert_multi_scan_multi_detector_without_qt(filename, tmpdir)


def test_multi_scan_multi_detector_with_qt(ewoks_orange_canvas, tmpdir):
    from orangecontrib.ewoksfluo.categories.demo import tutorials

    filename = resource_files(tutorials).joinpath("mesh_stack_multi_detector.ows")
    assert_multi_scan_multi_detector_with_qt(ewoks_orange_canvas, filename, tmpdir)


def assert_multi_scan_multi_detector_without_qt(filename, tmpdir):
    """Execute workflow after converting it to an ewoks workflow"""
    graph = ows_to_ewoks(filename)
    outputs = execute_graph(
        graph, inputs=get_inputs(tmpdir), outputs=[{"all": True}], merge_outputs=False
    )
    expected = get_expected_outputs(tmpdir)
    label_to_id = {
        attrs["label"]: node_id for node_id, attrs in graph.graph.nodes.items()
    }
    expected = {label_to_id[k]: v for k, v in expected.items()}
    assert outputs == expected


def assert_multi_scan_multi_detector_with_qt(ewoks_orange_canvas, filename, tmpdir):
    """Execute workflow using the Qt widgets and signals"""
    ewoks_orange_canvas.load_graph(str(filename), inputs=get_inputs(tmpdir))
    ewoks_orange_canvas.start_workflow()
    ewoks_orange_canvas.wait_widgets(timeout=30)
    outputs = dict(ewoks_orange_canvas.iter_output_values())
    assert outputs == get_expected_outputs(tmpdir)


def get_inputs(tmpdir) -> List[dict]:
    return [
        {
            "label": "Mesh stack (multi detector)",
            "name": "output_filename",
            "value": str(tmpdir / "input.h5"),
        },
        {
            "label": "Fit stack (multi detector)",
            "name": "output_root_uri",
            "value": str(tmpdir / "output.h5::/1.1"),
        },
    ]


def get_expected_outputs(tmpdir) -> Dict[str, dict]:
    bliss_scan_uris = [str(tmpdir / f"input.h5::/{i}.1") for i in range(1, 4)]
    output_root_uri = str(tmpdir / "output.h5::/1.1")
    return {
        "Mesh stack (multi detector)": {
            "config": str(tmpdir / "input.h5::/1.1/theory/configuration/data"),
            "configs": [str(tmpdir / "input.h5::/1.1/theory/configuration/data")] * 2,
            "detector_names": ["mca0", "mca1"],
            "expo_time": 0.1,
            "filenames": [str(tmpdir / "input.h5")],
            "monitor_name": "I0",
            "monitor_normalization_template": "1000000/<instrument/{}/data>",
            "detector_normalization_template": "0.1/<instrument/{}/live_time>",
            "scan_ranges": [[1, 3]],
        },
        "Pick scans": {"bliss_scan_uris": bliss_scan_uris},
        "Fit stack (multi detector)": {
            "xrf_results_uris": [
                str(tmpdir / "output.h5::/1.1/fit/mca0/results"),
                str(tmpdir / "output.h5::/1.1/fit/mca1/results"),
            ],
            "bliss_scan_uris": bliss_scan_uris,
            "detector_names": ["mca0", "mca1"],
            "output_root_uri": output_root_uri,
        },
        "Sum Fit Results Stack": {
            "xrf_results_uri": str(tmpdir / "output.h5::/1.1/sum/results"),
            "bliss_scan_uris": bliss_scan_uris,
            "output_root_uri": output_root_uri,
        },
        "Normalize Stack": {
            "xrf_results_uri": str(tmpdir / "output.h5::/1.1/norm/results"),
            "bliss_scan_uris": bliss_scan_uris,
            "output_root_uri": output_root_uri,
        },
        "Raw Counters Stack": {
            "xrf_results_uri": str(tmpdir / "output.h5::/1.1/merge/results"),
            "bliss_scan_uris": bliss_scan_uris,
            "output_root_uri": output_root_uri,
        },
        "Regrid Stack": {
            "xrf_results_uri": str(tmpdir / "output.h5::/1.1/regrid/results"),
            "bliss_scan_uris": bliss_scan_uris,
            "output_root_uri": output_root_uri,
        },
    }
