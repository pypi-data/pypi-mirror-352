from ewoksfluo.tasks.example_data.tasks import MosaicMeshSingleDetector
from ewoksfluo.gui.mesh_widget import OWMeshWidget


__all__ = ["OWMosaicMeshSingleDetector"]


class OWMosaicMeshSingleDetector(OWMeshWidget, ewokstaskclass=MosaicMeshSingleDetector):
    name = "Mosaic Mesh (single detector)"
    description = "XRF test data of one scan with one detector"

    def _init_control_area(self):
        super()._init_control_area(stack=False, multidetector=False, mosaic=True)
