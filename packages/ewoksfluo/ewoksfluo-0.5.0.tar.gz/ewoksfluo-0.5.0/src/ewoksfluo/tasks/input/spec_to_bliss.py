from ewokscore import Task
from ewoksfluo.io.convert import spec_to_bliss


class SpecToBliss(
    Task,
    input_names=["input_filename", "output_filename"],
    optional_input_names=["scan_numbers", "subscan_numbers"],
    output_names=["output_filename"],
):
    def run(self):
        spec_filename = self.inputs.input_filename
        bliss_filename = self.inputs.output_filename
        scans = self.get_input_value("scan_numbers", None)
        subscans = self.get_input_value("subscan_numbers", 1)
        spec_to_bliss(
            spec_filename, bliss_filename, scans=scans, subscans=subscans, mode="a"
        )
        self.outputs.output_filename = bliss_filename
