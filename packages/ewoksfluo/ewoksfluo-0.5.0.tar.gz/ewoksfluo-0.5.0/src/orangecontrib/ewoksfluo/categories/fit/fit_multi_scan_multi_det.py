from ewoksfluo.tasks.fit.tasks import FitStackMultiDetector
from ewoksfluo.gui.fit_widget import OWFitWidget

__all__ = ["OWFitStackMultiDetector"]


class OWFitStackMultiDetector(OWFitWidget, ewokstaskclass=FitStackMultiDetector):
    name = "Fit stack (multi detector)"
    description = "Fit a stack of identical scans with multiple detectors"

    def _init_control_area(self):
        super()._init_control_area(stack=True, multidetector=True)
