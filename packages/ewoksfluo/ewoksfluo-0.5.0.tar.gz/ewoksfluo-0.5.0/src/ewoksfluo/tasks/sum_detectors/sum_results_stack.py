from typing import Sequence

from ewokscore import Task

from .sum_utils import detector_weight_iterator_stack
from .sum_utils import save_summed_xrf_results
from ..math import format_expression_template


DEFAULTS = {
    "detector_normalization_template": "1./<instrument/{}/live_time>",
}


class SumXrfResultsStack(
    Task,
    input_names=[
        "xrf_results_uris",
        "bliss_scan_uris",
        "detector_names",
        "output_root_uri",
    ],
    optional_input_names=["detector_normalization_template"],
    output_names=["xrf_results_uri", "bliss_scan_uris", "output_root_uri"],
):
    """Add XRF stack results of multiple detectors"""

    def run(self) -> None:
        params = {**DEFAULTS, **self.get_input_values()}

        xrf_results_uris: Sequence[str] = params["xrf_results_uris"]
        detector_names: Sequence[str] = params["detector_names"]
        bliss_scan_uris: Sequence[str] = params["bliss_scan_uris"]
        detector_normalization_template: str = params["detector_normalization_template"]
        output_root_uri: str = params["output_root_uri"]

        if len(detector_names) < 1:
            raise ValueError("Expected at least 1 detector to sum")
        weight_expressions = [
            format_expression_template(detector_normalization_template, name)
            for name in detector_names
        ]
        detector_weights = detector_weight_iterator_stack(
            bliss_scan_uris, weight_expressions
        )

        process_config = {
            "detector_normalization_template": detector_normalization_template
        }
        self.outputs.xrf_results_uri = save_summed_xrf_results(
            xrf_results_uris, detector_weights, output_root_uri, process_config
        )
        self.outputs.bliss_scan_uris = bliss_scan_uris
        self.outputs.output_root_uri = output_root_uri
