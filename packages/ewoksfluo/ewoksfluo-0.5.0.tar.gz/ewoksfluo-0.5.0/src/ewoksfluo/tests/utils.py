from typing import List, Iterator, Tuple

import numpy
import h5py

from ewoksfluo.tasks.example_data.xrf_spectra import EmissionLineGroup
from ewoksfluo.tasks.example_data.xrf_spectra import ScatterLineGroup
from ewoksfluo.tasks.example_data.xrf_spectra import xrf_spectra


def h5content(group: h5py.Group):
    info = dict()
    if group.attrs:
        info["@attrs"] = set(group.attrs)
    for name, item in group.items():
        if isinstance(item, h5py.Group):
            info[name] = h5content(item)
        else:
            if item.attrs:
                info[f"{name}@attrs"] = set(item.attrs)
            info[f"{name}@shape"] = item.shape
    return info


def generate_data(
    tmpdir,
    npoints_per_scan: int,
    energy: float,
    samefile: bool = True,
    nscans: int = 1,
    ndetectors: int = 1,
) -> Tuple[List[str], numpy.ndarray, numpy.ndarray, dict]:
    xrf_spectra_uris = list()
    parameters = dict()
    spectra = list()

    for detector in range(ndetectors):
        det_xrf_spectra_uris = list()
        xrf_spectra_uris.append(det_xrf_spectra_uris)
        det_spectra = list()
        spectra.append(det_spectra)

        for scan, filename in enumerate(
            _generate_scan_filenames(tmpdir, samefile, nscans), 1
        ):
            scan_name = f"/{scan}.1"
            spectra_name = f"{scan_name}/measurement/mca{detector:02d}"
            energy_name = f"{scan_name}/instrument/positioners_start/energy"
            with h5py.File(filename, mode="a") as h5file:
                linegroups = [
                    EmissionLineGroup(
                        "Si", "K", _generate_counts(300, npoints_per_scan, scan)
                    ),
                    EmissionLineGroup(
                        "Al", "K", _generate_counts(400, npoints_per_scan, scan)
                    ),
                    EmissionLineGroup(
                        "Cl", "K", _generate_counts(200, npoints_per_scan, scan)
                    ),
                    EmissionLineGroup(
                        "Pb", "M", _generate_counts(500, npoints_per_scan, scan)
                    ),
                    EmissionLineGroup(
                        "P", "K", _generate_counts(200, npoints_per_scan, scan)
                    ),
                    EmissionLineGroup(
                        "S", "K", _generate_counts(600, npoints_per_scan, scan)
                    ),
                    EmissionLineGroup(
                        "Ca", "K", _generate_counts(500, npoints_per_scan, scan)
                    ),
                    EmissionLineGroup(
                        "Ti", "K", _generate_counts(400, npoints_per_scan, scan)
                    ),
                    EmissionLineGroup(
                        "Ce", "L", _generate_counts(500, npoints_per_scan, scan)
                    ),
                    EmissionLineGroup(
                        "Fe", "K", _generate_counts(1000, npoints_per_scan, scan)
                    ),
                ]
                scattergroups = [
                    ScatterLineGroup(
                        "Peak000", _generate_counts(100, npoints_per_scan, scan)
                    ),
                    ScatterLineGroup(
                        "Compton000", _generate_counts(100, npoints_per_scan, scan)
                    ),
                ]
                _spectra, config = xrf_spectra(linegroups, scattergroups, energy=energy)

                h5file[spectra_name] = _spectra
                if energy_name not in h5file:
                    h5file[energy_name] = energy
                    h5file[energy_name].attrs["units"] = "keV"

                det_xrf_spectra_uris.append(f"{filename}::{spectra_name}")
                det_spectra.extend(_spectra)
                if detector == 0:
                    for group in linegroups:
                        lst = parameters.setdefault(
                            f"{group.element}_{group.name}", list()
                        )
                        lst.extend(group.counts)
                    for group in scattergroups:
                        lst = parameters.setdefault(
                            f"{group.prefix}_{group.name}", list()
                        )
                        lst.extend(group.counts)

    # For each detector: list of spectra and peak areas for all points in all scans
    spectra = numpy.asarray(spectra)
    parameters = {name: numpy.asarray(values) for name, values in parameters.items()}
    return xrf_spectra_uris, spectra, parameters, config


def _generate_scan_filenames(tmpdir, samefile: bool, nscans: int) -> Iterator[str]:
    if samefile:
        for scan in range(1, nscans + 1):
            yield str(tmpdir / "spectra.h5")
    else:
        for scan in range(1, nscans + 1):
            yield str(tmpdir / f"spectra{scan}.h5")


def _generate_counts(start_counts: int, npoints_per_scan: int, scan: int) -> List[int]:
    step = 50
    total_step = npoints_per_scan * step
    start = start_counts + (scan - 1) * total_step
    stop = start + total_step
    return list(range(start, stop, step))
