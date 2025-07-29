from ewokscore import Task
from ewoksfluo.io.blissconcat import concatenate_bliss_scans


class ConcatBliss(
    Task,
    input_names=["bliss_scan_uris", "bliss_scan_uri"],
    optional_input_names=["virtual_axes", "axes_units"],
    output_names=["bliss_scan_uri"],
):
    """Concatenate Bliss scans."""

    def run(self):
        self.outputs.bliss_scan_uri = concatenate_bliss_scans(
            self.inputs.bliss_scan_uris,
            self.inputs.bliss_scan_uri,
            virtual_axes=self.get_input_value("virtual_axes"),
            axes_units=self.get_input_value("axes_units"),
        )
