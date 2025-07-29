from ewoksfluo.tasks.example_data.tasks import MeshSingleScanSingleDetector
from ewoksfluo.gui.mesh_widget import OWMeshWidget


__all__ = ["OWMeshSingleScanSingleDetector"]


class OWMeshSingleScanSingleDetector(
    OWMeshWidget, ewokstaskclass=MeshSingleScanSingleDetector
):
    name = "Mesh (single detector)"
    description = "XRF test data of one scan with one detector"

    def _init_control_area(self):
        super()._init_control_area(stack=False, multidetector=False, mosaic=False)
