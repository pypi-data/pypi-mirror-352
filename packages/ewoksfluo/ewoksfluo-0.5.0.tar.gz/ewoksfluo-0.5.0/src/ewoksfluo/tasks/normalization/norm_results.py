from typing import Optional

from ewokscore import Task
from ewokscore.task import TaskInputError

from .norm_utils import normalization_template
from .norm_utils import save_normalized_xrf_results
from .norm_utils import normalization_coefficient


class NormalizeXrfResults(
    Task,
    input_names=["xrf_results_uri", "bliss_scan_uri", "output_root_uri"],
    optional_input_names=[
        "normalization_expression",
        "counter_normalization_template",
        "counter_name",
        "detector_normalization_template",
        "detector_name",
    ],
    output_names=["xrf_results_uri", "bliss_scan_uri", "output_root_uri"],
):
    """Normalize XRF results with raw scan counters.

    Typical normalizers are beam monitors and measurement (live) time.

    :param xrf_results_uri: URI to the group containing the XRF results to be corrected. Format: /path/to/file.h5::/path/to/results/group.
    :param bliss_scan_uri: URIs to the datasets to normalize the data with. Format: /path/to/file.h5::/path/to/normalizer/dataset.
    :param expression: Arithmetic expression to be used for normalization.
    :param counter_normalization_template: Arithmetic expression to be used for normalization.
    :param counter_name: To be used in :math:`counter_normalization_template`.
    :param detector_normalization_template: Arithmetic expression to be used for normalization
    :param detector_name: To be used in :math:`detector_normalization_template`.
    :param output_root_uri: URI to the HDF5 group where the results must be saved. Format: /path/to/file.h5::/entry
    :returns xrf_results_uri: URI to the nexus collection where the results were saved.
    """

    def run(self):
        params = self.get_input_values()

        output_root_uri: str = params["output_root_uri"]
        xrf_results_uri: str = params["xrf_results_uri"]
        bliss_scan_uri: str = params["bliss_scan_uri"]

        expression: Optional[str] = params.get("normalization_expression")
        detector_name: Optional[str] = params.get("detector_name")
        counter_name: Optional[str] = params.get("counter_name")
        if not (expression or detector_name or counter_name):
            raise TaskInputError(
                "at least one of these is required: 'expression_template', 'counter_name' or 'detector_name'"
            )
        counter_normalization_template: Optional[str] = params.get(
            "counter_normalization_template"
        )
        detector_normalization_template: Optional[str] = params.get(
            "detector_normalization_template"
        )

        normalization_expression = normalization_template(
            expression,
            counter_normalization_template,
            counter_name,
            detector_normalization_template,
            detector_name,
        )

        coefficient = normalization_coefficient(
            bliss_scan_uri, normalization_expression
        )

        process_config = {"normalization_expression": normalization_expression}
        self.outputs.xrf_results_uri = save_normalized_xrf_results(
            xrf_results_uri, coefficient, output_root_uri, process_config
        )
        self.outputs.bliss_scan_uri = bliss_scan_uri
        self.outputs.output_root_uri = output_root_uri
