from ewoksfluo.tasks.example_data.tasks import MeshSingleScanMultiDetector
from ewoksfluo.gui.mesh_widget import OWMeshWidget

__all__ = ["OWMeshSingleScanMultiDetector"]


class OWMeshSingleScanMultiDetector(
    OWMeshWidget,
    ewokstaskclass=MeshSingleScanMultiDetector,
):
    name = "Mesh (multi detector)"
    description = "XRF test data of one scan with multiple detectors"

    def _init_control_area(self):
        super()._init_control_area(stack=False, multidetector=True, mosaic=False)
