from ewoksfluo.tasks.example_data.tasks import MeshStackSingleDetector
from ewoksfluo.gui.mesh_widget import OWMeshWidget

__all__ = ["OWMeshStackSingleDetector"]


class OWMeshStackSingleDetector(OWMeshWidget, ewokstaskclass=MeshStackSingleDetector):
    name = "Mesh stack (single detector)"
    description = "XRF test data of a stack of identical scans with one detector"

    def _init_control_area(self):
        super()._init_control_area(stack=True, multidetector=False, mosaic=False)
