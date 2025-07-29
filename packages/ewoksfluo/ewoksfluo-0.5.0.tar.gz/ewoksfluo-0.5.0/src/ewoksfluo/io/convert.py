from typing import Sequence, Union, Optional, List, Tuple

from .spec import SpecFile
from .nexus import save_as_bliss_scan


def spec_to_bliss(
    spec_filename: str,
    bliss_filename: str,
    scans: Union[int, Sequence[int], None] = None,
    subscans: Union[int, Sequence[int]] = 1,
    mode: str = "a",
    **openargs,
) -> None:
    include_scans = _parse_scan_arguments(scans, subscans)
    with SpecFile(spec_filename) as specfile:
        if include_scans is None:
            include_scans = specfile.get_scans()
        for scannb, subscan in include_scans:
            n = specfile.get_number_of_subsubscans(scannb, subscan)
            for i, (scannb, subscan) in enumerate(zip([scannb] * n, [subscan] * n)):
                subsubscan = i + 1
                osubscan = subscan + i
                save_as_bliss_scan(
                    bliss_filename,
                    f"{scannb}.{osubscan}",
                    specfile.iter_data(scannb, subscan=subscan, subsubscan=subsubscan),
                    positioners=specfile.get_positioners(scannb, subscan=subscan),
                    title=specfile.get_title(scannb, subscan=subscan),
                    mode=mode,
                    **openargs,
                )
                if mode == "w":
                    mode = "a"


def _parse_scan_arguments(
    scans: Union[int, Sequence[int], None], subscans: Union[int, Sequence[int]]
) -> Optional[List[Tuple[int, int]]]:
    if scans is None:
        return None
    if not isinstance(scans, Sequence):
        scans = [scans]
    if not isinstance(subscans, Sequence):
        subscans = [subscans]
    if len(scans) == 1:
        scans = scans * len(subscans)
    if len(subscans) == 1:
        subscans = subscans * len(scans)
    if len(scans) != len(subscans):
        raise ValueError("number of 'scans' and 'subscans' is not equal")
    return list(zip(scans, subscans))
