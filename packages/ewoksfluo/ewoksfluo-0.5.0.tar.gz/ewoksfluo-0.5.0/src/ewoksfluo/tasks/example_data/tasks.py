from ewokscore import Task

from .scan_data import save_2d_xrf_scans

SEED = 100
MAX_DEVIATION = 0.05  # Fraction of a single step

DEFAULTS = {
    "output_filename": "raw_data.h5",
    "emission_line_groups": ["Si-K", "Ca-K", "Ce-L", "Fe-K"],
    "energy": 12.0,
    "shape": (50, 60),
    "mosaic": (2, 3),
    "expo_time": 0.1,
    "flux": 1e7,
    "counting_noise": True,
    "rois": [(100, 200), (300, 600)],
    "integral_type": True,
    "ndetectors": 1,
    "nscans": 1,
}


class MeshSingleScanSingleDetector(
    Task,
    input_names=["output_filename"],
    optional_input_names=[
        "emission_line_groups",
        "energy",
        "shape",
        "expo_time",
        "ndetectors",
        "flux",
        "counting_noise",
        "rois",
        "integral_type",
    ],
    output_names=[
        "filename",
        "scan_number",
        "config",
        "expo_time",
        "monitor_name",
        "monitor_normalization_template",
        "detector_name",
        "detector_normalization_template",
    ],
):
    """XRF test data of one scan with one detector"""

    def run(self):
        emission_line_groups = self.get_input_value(
            "emission_line_groups", DEFAULTS["emission_line_groups"]
        )
        energy = self.get_input_value("energy", DEFAULTS["energy"])
        shape = self.get_input_value("shape", DEFAULTS["shape"])
        expo_time = self.get_input_value("expo_time", DEFAULTS["expo_time"])
        flux = self.get_input_value("flux", DEFAULTS["flux"])
        counting_noise = self.get_input_value(
            "counting_noise", DEFAULTS["counting_noise"]
        )
        rois = self.get_input_value("rois", DEFAULTS["rois"])
        integral_type = self.get_input_value("integral_type", DEFAULTS["integral_type"])

        scan_number = 1
        filename = self.inputs.output_filename

        _ = save_2d_xrf_scans(
            filename=filename,
            emission_line_groups=emission_line_groups,
            first_scan_number=scan_number,
            shape=shape,
            mosaic=(1, 1),
            energy=energy,
            flux=flux,
            expo_time=expo_time,
            counting_noise=counting_noise,
            integral_type=integral_type,
            rois=rois,
            nmcas=1,
            max_deviation=MAX_DEVIATION,
            seed=SEED,
        )

        self.outputs.filename = filename
        self.outputs.scan_number = scan_number
        self.outputs.config = f"{filename}::/{scan_number}.1/theory/configuration/data"
        self.outputs.expo_time = expo_time
        self.outputs.monitor_name = "I0"
        self.outputs.monitor_normalization_template = (
            f"{int(flux * expo_time)}/<instrument/{{}}/data>"
        )
        self.outputs.detector_name = "mca0"
        self.outputs.detector_normalization_template = (
            f"{expo_time}/<instrument/{{}}/live_time>"
        )


class MeshSingleScanMultiDetector(
    Task,
    input_names=["output_filename"],
    optional_input_names=[
        "emission_line_groups",
        "energy",
        "shape",
        "expo_time",
        "ndetectors",
        "flux",
        "counting_noise",
        "rois",
        "integral_type",
    ],
    output_names=[
        "filename",
        "scan_number",
        "configs",
        "config",
        "expo_time",
        "monitor_name",
        "monitor_normalization_template",
        "detector_names",
        "detector_normalization_template",
    ],
):
    """XRF test data of one scan with multiple detectors"""

    def run(self):
        emission_line_groups = self.get_input_value(
            "emission_line_groups", DEFAULTS["emission_line_groups"]
        )
        energy = self.get_input_value("energy", DEFAULTS["energy"])
        shape = self.get_input_value("shape", DEFAULTS["shape"])
        expo_time = self.get_input_value("expo_time", DEFAULTS["expo_time"])
        flux = self.get_input_value("flux", DEFAULTS["flux"])
        counting_noise = self.get_input_value(
            "counting_noise", DEFAULTS["counting_noise"]
        )
        rois = self.get_input_value("rois", DEFAULTS["rois"])
        integral_type = self.get_input_value("integral_type", DEFAULTS["integral_type"])

        ndetectors = self.get_input_value("ndetectors", DEFAULTS["ndetectors"])

        scan_number = 1
        filename = self.inputs.output_filename

        _ = save_2d_xrf_scans(
            filename=filename,
            emission_line_groups=emission_line_groups,
            first_scan_number=scan_number,
            shape=shape,
            mosaic=(1, 1),
            energy=energy,
            flux=flux,
            expo_time=expo_time,
            counting_noise=counting_noise,
            integral_type=integral_type,
            rois=rois,
            nmcas=ndetectors,
            max_deviation=MAX_DEVIATION,
            seed=SEED,
        )

        self.outputs.filename = filename
        self.outputs.scan_number = scan_number
        self.outputs.configs = [
            f"{filename}::/{scan_number}.1/theory/configuration/data"
        ] * ndetectors
        self.outputs.config = f"{filename}::/{scan_number}.1/theory/configuration/data"
        self.outputs.expo_time = expo_time
        self.outputs.monitor_name = "I0"
        self.outputs.monitor_normalization_template = (
            f"{int(flux * expo_time)}/<instrument/{{}}/data>"
        )
        self.outputs.detector_names = [f"mca{i}" for i in range(ndetectors)]
        self.outputs.detector_normalization_template = (
            f"{expo_time}/<instrument/{{}}/live_time>"
        )


class MosaicMeshSingleDetector(
    Task,
    input_names=["output_filename"],
    optional_input_names=[
        "emission_line_groups",
        "energy",
        "shape",
        "mosaic",
        "expo_time",
        "ndetectors",
        "flux",
        "counting_noise",
        "rois",
        "integral_type",
    ],
    output_names=[
        "filenames",
        "scan_ranges",
        "config",
        "expo_time",
        "monitor_name",
        "monitor_normalization_template",
        "detector_name",
        "detector_normalization_template",
    ],
):
    """XRF test data of a mosaic scan with one detector"""

    def run(self):
        emission_line_groups = self.get_input_value(
            "emission_line_groups", DEFAULTS["emission_line_groups"]
        )
        energy = self.get_input_value("energy", DEFAULTS["energy"])
        shape = self.get_input_value("shape", DEFAULTS["shape"])
        mosaic = self.get_input_value("mosaic", DEFAULTS["mosaic"])
        expo_time = self.get_input_value("expo_time", DEFAULTS["expo_time"])
        flux = self.get_input_value("flux", DEFAULTS["flux"])
        counting_noise = self.get_input_value(
            "counting_noise", DEFAULTS["counting_noise"]
        )
        rois = self.get_input_value("rois", DEFAULTS["rois"])
        integral_type = self.get_input_value("integral_type", DEFAULTS["integral_type"])

        first_scan_number = 1
        filename = self.inputs.output_filename

        scan_numbers = save_2d_xrf_scans(
            filename=filename,
            emission_line_groups=emission_line_groups,
            first_scan_number=first_scan_number,
            shape=shape,
            mosaic=mosaic,
            energy=energy,
            flux=flux,
            expo_time=expo_time,
            counting_noise=counting_noise,
            integral_type=integral_type,
            rois=rois,
            nmcas=1,
            max_deviation=MAX_DEVIATION,
            seed=SEED,
        )

        self.outputs.filenames = [filename]
        self.outputs.scan_ranges = [[scan_numbers[0], scan_numbers[-1]]]
        self.outputs.config = (
            f"{filename}::/{scan_numbers[0]}.1/theory/configuration/data"
        )
        self.outputs.expo_time = expo_time
        self.outputs.monitor_name = "I0"
        self.outputs.monitor_normalization_template = (
            f"{int(flux * expo_time)}/<instrument/{{}}/data>"
        )
        self.outputs.detector_name = "mca0"
        self.outputs.detector_normalization_template = (
            f"{expo_time}/<instrument/{{}}/live_time>"
        )


class MosaicMeshMultiDetector(
    Task,
    input_names=["output_filename"],
    optional_input_names=[
        "emission_line_groups",
        "energy",
        "shape",
        "mosaic",
        "expo_time",
        "ndetectors",
        "flux",
        "counting_noise",
        "rois",
        "integral_type",
    ],
    output_names=[
        "filenames",
        "scan_ranges",
        "configs",
        "config",
        "expo_time",
        "monitor_name",
        "monitor_normalization_template",
        "detector_names",
        "detector_normalization_template",
    ],
):
    """XRF test data of a mosaic scan with multiple detectors"""

    def run(self):
        emission_line_groups = self.get_input_value(
            "emission_line_groups", DEFAULTS["emission_line_groups"]
        )
        energy = self.get_input_value("energy", DEFAULTS["energy"])
        shape = self.get_input_value("shape", DEFAULTS["shape"])
        mosaic = self.get_input_value("mosaic", DEFAULTS["mosaic"])
        expo_time = self.get_input_value("expo_time", DEFAULTS["expo_time"])
        flux = self.get_input_value("flux", DEFAULTS["flux"])
        counting_noise = self.get_input_value(
            "counting_noise", DEFAULTS["counting_noise"]
        )
        rois = self.get_input_value("rois", DEFAULTS["rois"])
        integral_type = self.get_input_value("integral_type", DEFAULTS["integral_type"])

        ndetectors = self.get_input_value("ndetectors", DEFAULTS["ndetectors"])

        filename = self.inputs.output_filename

        scan_numbers = save_2d_xrf_scans(
            filename=filename,
            emission_line_groups=emission_line_groups,
            first_scan_number=1,
            shape=shape,
            mosaic=mosaic,
            energy=energy,
            flux=flux,
            expo_time=expo_time,
            counting_noise=counting_noise,
            integral_type=integral_type,
            rois=rois,
            nmcas=ndetectors,
            max_deviation=MAX_DEVIATION,
            seed=SEED,
        )

        self.outputs.filenames = [filename]
        self.outputs.scan_ranges = [[scan_numbers[0], scan_numbers[-1]]]
        self.outputs.configs = [
            f"{filename}::/{scan_numbers[0]}.1/theory/configuration/data"
        ] * ndetectors
        self.outputs.config = (
            f"{filename}::/{scan_numbers[0]}.1/theory/configuration/data"
        )
        self.outputs.expo_time = expo_time
        self.outputs.monitor_name = "I0"
        self.outputs.monitor_normalization_template = (
            f"{int(flux * expo_time)}/<instrument/{{}}/data>"
        )
        self.outputs.detector_names = [f"mca{i}" for i in range(ndetectors)]
        self.outputs.detector_normalization_template = (
            f"{expo_time}/<instrument/{{}}/live_time>"
        )


class MeshStackSingleDetector(
    Task,
    input_names=["output_filename"],
    optional_input_names=[
        "nscans",
        "emission_line_groups",
        "energy",
        "shape",
        "expo_time",
        "flux",
        "counting_noise",
        "rois",
        "integral_type",
    ],
    output_names=[
        "filenames",
        "scan_ranges",
        "config",
        "expo_time",
        "monitor_name",
        "monitor_normalization_template",
        "detector_name",
        "detector_normalization_template",
    ],
):
    """XRF test data of a stack of identical scans with one detector"""

    def run(self):
        emission_line_groups = self.get_input_value(
            "emission_line_groups", DEFAULTS["emission_line_groups"]
        )
        energy = self.get_input_value("energy", DEFAULTS["energy"])
        shape = self.get_input_value("shape", DEFAULTS["shape"])
        expo_time = self.get_input_value("expo_time", DEFAULTS["expo_time"])
        flux = self.get_input_value("flux", DEFAULTS["flux"])
        counting_noise = self.get_input_value(
            "counting_noise", DEFAULTS["counting_noise"]
        )
        rois = self.get_input_value("rois", DEFAULTS["rois"])
        integral_type = self.get_input_value("integral_type", DEFAULTS["integral_type"])

        nscans = self.get_input_value("nscans", DEFAULTS["nscans"])

        filename = self.inputs.output_filename
        bliss_scan_uris = list()
        scan_numbers = list(range(1, nscans + 1))
        for scan_number in scan_numbers:
            _ = save_2d_xrf_scans(
                filename=filename,
                emission_line_groups=emission_line_groups,
                first_scan_number=scan_number,
                shape=shape,
                mosaic=(1, 1),
                energy=energy,
                flux=flux,
                expo_time=expo_time,
                counting_noise=counting_noise,
                integral_type=integral_type,
                rois=rois,
                nmcas=1,
                max_deviation=MAX_DEVIATION,
                seed=SEED,
            )

            bliss_scan_uris.append(f"{filename}::/{scan_number}.1")
            energy += 0.010

        self.outputs.filenames = [filename]
        self.outputs.scan_ranges = [[scan_numbers[0], scan_numbers[-1]]]
        self.outputs.config = (
            f"{filename}::/{scan_numbers[0]}.1/theory/configuration/data"
        )
        self.outputs.monitor_name = "I0"
        self.outputs.monitor_normalization_template = (
            f"{int(flux * expo_time)}/<instrument/{{}}/data>"
        )
        self.outputs.expo_time = expo_time
        self.outputs.detector_name = "mca0"
        self.outputs.detector_normalization_template = (
            f"{expo_time}/<instrument/{{}}/live_time>"
        )


class MeshStackMultiDetector(
    Task,
    input_names=["output_filename"],
    optional_input_names=[
        "nscans",
        "emission_line_groups",
        "energy",
        "shape",
        "expo_time",
        "ndetectors",
        "flux",
        "counting_noise",
        "rois",
        "integral_type",
    ],
    output_names=[
        "filenames",
        "scan_ranges",
        "configs",
        "config",
        "expo_time",
        "monitor_name",
        "monitor_normalization_template",
        "detector_names",
        "detector_normalization_template",
    ],
):
    """XRF test data of a stack of identical scans with multiple detectors"""

    def run(self):
        emission_line_groups = self.get_input_value(
            "emission_line_groups", DEFAULTS["emission_line_groups"]
        )
        energy = self.get_input_value("energy", DEFAULTS["energy"])
        shape = self.get_input_value("shape", DEFAULTS["shape"])
        expo_time = self.get_input_value("expo_time", DEFAULTS["expo_time"])
        flux = self.get_input_value("flux", DEFAULTS["flux"])
        counting_noise = self.get_input_value(
            "counting_noise", DEFAULTS["counting_noise"]
        )
        rois = self.get_input_value("rois", DEFAULTS["rois"])
        integral_type = self.get_input_value("integral_type", DEFAULTS["integral_type"])

        nscans = self.get_input_value("nscans", DEFAULTS["nscans"])
        ndetectors = self.get_input_value("ndetectors", DEFAULTS["ndetectors"])

        filename = self.inputs.output_filename
        bliss_scan_uris = list()
        scan_numbers = list(range(1, nscans + 1))
        for scan_number in scan_numbers:
            _ = save_2d_xrf_scans(
                filename=filename,
                emission_line_groups=emission_line_groups,
                first_scan_number=scan_number,
                shape=shape,
                mosaic=(1, 1),
                energy=energy,
                flux=flux,
                expo_time=expo_time,
                counting_noise=counting_noise,
                integral_type=integral_type,
                rois=rois,
                nmcas=ndetectors,
                max_deviation=MAX_DEVIATION,
                seed=SEED,
            )

            bliss_scan_uris.append(f"{filename}::/{scan_number}.1")
            energy += 0.010

        self.outputs.filenames = [filename]
        self.outputs.scan_ranges = [[scan_numbers[0], scan_numbers[-1]]]
        self.outputs.configs = [
            f"{filename}::/{scan_numbers[0]}.1/theory/configuration/data"
        ] * ndetectors
        self.outputs.config = (
            f"{filename}::/{scan_numbers[0]}.1/theory/configuration/data"
        )
        self.outputs.monitor_name = "I0"
        self.outputs.monitor_normalization_template = (
            f"{int(flux * expo_time)}/<instrument/{{}}/data>"
        )
        self.outputs.expo_time = expo_time
        self.outputs.detector_names = [f"mca{i}" for i in range(ndetectors)]
        self.outputs.detector_normalization_template = (
            f"{expo_time}/<instrument/{{}}/live_time>"
        )
