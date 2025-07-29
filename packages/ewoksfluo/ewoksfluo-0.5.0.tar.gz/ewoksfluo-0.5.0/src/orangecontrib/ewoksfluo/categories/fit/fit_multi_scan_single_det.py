from ewoksfluo.tasks.fit.tasks import FitStackSingleDetector
from ewoksfluo.gui.fit_widget import OWFitWidget

__all__ = ["OWFitStackSingleDetector"]


class OWFitStackSingleDetector(OWFitWidget, ewokstaskclass=FitStackSingleDetector):
    name = "Fit stack (single detector)"
    description = "Fit a stack of identical scans with one detector"

    def _init_control_area(self):
        super()._init_control_area(stack=True, multidetector=False)
