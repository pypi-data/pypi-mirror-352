from typing import Sequence
from ewokscore import Task


class PickScan(
    Task,
    input_names=["filename", "scan_number"],
    output_names=["bliss_scan_uri"],
):
    """Select a single Bliss scan."""

    def run(self):
        filename: Sequence[str] = self.inputs.filename
        scan_number: Sequence[int] = self.inputs.scan_number
        self.outputs.bliss_scan_uri = f"{filename}::/{scan_number}.1"
