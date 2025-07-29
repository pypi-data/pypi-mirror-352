from typing import List, Sequence, Tuple
from ewokscore import Task


class PickScans(
    Task,
    input_names=["filenames", "scan_ranges"],
    optional_input_names=["exclude_scans"],
    output_names=["bliss_scan_uris"],
):
    """Select a multiple Bliss scan from multiple files."""

    def run(self):
        filenames: Sequence[str] = self.inputs.filenames
        scan_ranges: Sequence[Tuple[int, int]] = self.inputs.scan_ranges
        exclude_scans: Sequence[Sequence[int]] = self.get_input_value(
            "exclude_scans", []
        )
        exclude_scans += [[]] * max(0, len(filenames) - len(exclude_scans))

        bliss_scan_uris: List[str] = []
        for filename, scan_range, excluded_scans in zip(
            filenames, scan_ranges, exclude_scans
        ):
            scan_min, scan_max = scan_range
            excluded_scans = excluded_scans if excluded_scans else []
            for scan_number in range(scan_min, scan_max + 1):
                if scan_number in excluded_scans:
                    continue

                bliss_scan_uris.append(f"{filename}::/{scan_number}.1")

        self.outputs.bliss_scan_uris = bliss_scan_uris
