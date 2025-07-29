from ewoksfluo.tasks.example_data.tasks import MosaicMeshMultiDetector
from ewoksfluo.gui.mesh_widget import OWMeshWidget

__all__ = ["OWMosaicMeshMultiDetector"]


class OWMosaicMeshMultiDetector(
    OWMeshWidget,
    ewokstaskclass=MosaicMeshMultiDetector,
):
    name = "Mosaic Mesh (multi detector)"
    description = "XRF test data of one scan with multiple detectors"

    def _init_control_area(self):
        super()._init_control_area(stack=False, multidetector=True, mosaic=True)
