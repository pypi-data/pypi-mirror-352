from ewoksfluo.tasks.fit.tasks import FitSingleScanMultiDetector
from ewoksfluo.gui.fit_widget import OWFitWidget

__all__ = ["OWFitSingleScanMultiDetector"]


class OWFitSingleScanMultiDetector(
    OWFitWidget, ewokstaskclass=FitSingleScanMultiDetector
):
    name = "Fit scan (multi detector)"
    description = "Fit one scan with multiple detectors"

    def _init_control_area(self):
        super()._init_control_area(stack=False, multidetector=True)
