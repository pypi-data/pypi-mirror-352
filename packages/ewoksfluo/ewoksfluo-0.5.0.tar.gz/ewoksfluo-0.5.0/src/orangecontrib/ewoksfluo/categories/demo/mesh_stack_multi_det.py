from ewoksfluo.tasks.example_data.tasks import MeshStackMultiDetector
from ewoksfluo.gui.mesh_widget import OWMeshWidget

__all__ = ["OWMeshStackMultiDetector"]


class OWMeshStackMultiDetector(OWMeshWidget, ewokstaskclass=MeshStackMultiDetector):
    name = "Mesh stack (multi detector)"
    description = "XRF test data of a stack of identical scans with multiple detectors"

    def _init_control_area(self):
        super()._init_control_area(stack=True, multidetector=True, mosaic=False)
