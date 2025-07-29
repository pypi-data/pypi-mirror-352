from ewokscore import Task

from .execute import fit_single
from .execute import fit_multi
from ..positioner_utils import get_energy


DEFAULTS = {
    "xrf_spectra_uri_template": "instrument/{}/data",
    "process_uri_template": "fit/{}",
    "energy_uri_template": "instrument/positioners_start/{}",
    "fast_fitting": True,
    "diagnostics": False,
}


class FitSingleScanSingleDetector(
    Task,
    input_names=[
        "bliss_scan_uri",
        "detector_name",
        "config",
        "output_root_uri",
    ],
    optional_input_names=[
        "xrf_spectra_uri_template",
        "process_uri_template",
        "energy_name",
        "energy_uri_template",
        "quantification",
        "energy_multiplier",
        "fast_fitting",
        "diagnostics",
        "figuresofmerit",
    ],
    output_names=[
        "xrf_results_uri",
        "bliss_scan_uri",
        "detector_name",
        "output_root_uri",
    ],
):
    """XRF fit of one scan with one detector"""

    def run(self):
        params = {**DEFAULTS, **self.get_input_values()}
        _parse_energy(params)
        xrf_results_uri, output_root_uri = fit_single(**params)
        self.outputs.xrf_results_uri = xrf_results_uri
        self.outputs.bliss_scan_uri = params["bliss_scan_uri"]
        self.outputs.detector_name = params["detector_name"]
        self.outputs.output_root_uri = output_root_uri


class FitSingleScanMultiDetector(
    Task,
    input_names=[
        "bliss_scan_uri",
        "detector_names",
        "configs",
        "output_root_uri",
    ],
    optional_input_names=[
        "xrf_spectra_uri_template",
        "process_uri_template",
        "energy_name",
        "energy_uri_template",
        "quantification",
        "energy_multiplier",
        "fast_fitting",
        "diagnostics",
        "figuresofmerit",
    ],
    output_names=[
        "xrf_results_uris",
        "bliss_scan_uri",
        "detector_names",
        "output_root_uri",
    ],
):
    """XRF fit of one scan with multiple detectors"""

    def run(self):
        params = {**DEFAULTS, **self.get_input_values()}
        bliss_scan_uri = params.pop("bliss_scan_uri")
        params["bliss_scan_uris"] = [bliss_scan_uri]
        _parse_energies(params)
        xrf_results_uris, output_root_uri = fit_multi(**params)
        self.outputs.xrf_results_uris = xrf_results_uris
        self.outputs.bliss_scan_uri = bliss_scan_uri
        self.outputs.detector_names = params["detector_names"]
        self.outputs.output_root_uri = output_root_uri


class FitStackSingleDetector(
    Task,
    input_names=[
        "bliss_scan_uris",
        "detector_name",
        "config",
        "output_root_uri",
    ],
    optional_input_names=[
        "xrf_spectra_uri_template",
        "process_uri_template",
        "energy_name",
        "energy_uri_template",
        "quantification",
        "energy_multiplier",
        "fast_fitting",
        "diagnostics",
        "figuresofmerit",
    ],
    output_names=[
        "xrf_results_uri",
        "bliss_scan_uris",
        "detector_name",
        "output_root_uri",
    ],
):
    """XRF fit of a stack of identical scan with one detector"""

    def run(self):
        params = {**DEFAULTS, **self.get_input_values()}
        detector_name = params.pop("detector_name")
        params["detector_names"] = [detector_name]
        params["configs"] = [params.pop("config")]
        _parse_energies(params)
        xrf_results_uris, output_root_uri = fit_multi(**params)
        self.outputs.xrf_results_uri = xrf_results_uris[0]
        self.outputs.bliss_scan_uris = params["bliss_scan_uris"]
        self.outputs.detector_name = detector_name
        self.outputs.output_root_uri = output_root_uri


class FitStackMultiDetector(
    Task,
    input_names=[
        "bliss_scan_uris",
        "detector_names",
        "configs",
        "output_root_uri",
    ],
    optional_input_names=[
        "xrf_spectra_uri_template",
        "process_uri_template",
        "energy_name",
        "energy_uri_template",
        "quantification",
        "energy_multiplier",
        "fast_fitting",
        "diagnostics",
        "figuresofmerit",
    ],
    output_names=[
        "xrf_results_uris",
        "bliss_scan_uris",
        "detector_names",
        "output_root_uri",
    ],
):
    """XRF fit of a stack of identical scan with multiple detectors"""

    def run(self):
        params = {**DEFAULTS, **self.get_input_values()}
        _parse_energies(params)
        xrf_results_uris, output_root_uri = fit_multi(**params)
        self.outputs.xrf_results_uris = xrf_results_uris
        self.outputs.bliss_scan_uris = params["bliss_scan_uris"]
        self.outputs.detector_names = params["detector_names"]
        self.outputs.output_root_uri = output_root_uri


def _parse_energy(params: dict) -> None:
    energy_name = params.pop("energy_name", None)
    energy_uri_template = params.pop("energy_uri_template", None)
    params["energy"] = get_energy(
        params["bliss_scan_uri"], energy_name, energy_uri_template
    )


def _parse_energies(params: dict) -> None:
    energy_name = params.pop("energy_name", None)
    energy_uri_template = params.pop("energy_uri_template", None)
    params["energies"] = [
        get_energy(bliss_scan_uri, energy_name, energy_uri_template)
        for bliss_scan_uri in params["bliss_scan_uris"]
    ]
