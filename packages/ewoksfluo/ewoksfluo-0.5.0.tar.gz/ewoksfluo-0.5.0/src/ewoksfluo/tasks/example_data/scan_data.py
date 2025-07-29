import os
import functools
from typing import Iterator, Tuple, Optional, List, Sequence, Dict, NamedTuple

import h5py
import numpy
from silx.io import h5py_utils
from PyMca5.PyMcaIO.ConfigDict import ConfigDict

try:
    from imageio.v3 import imread
except ImportError:
    try:
        from imageio.v2 import imread
    except ImportError:
        from imageio import imread

from scipy import ndimage

from . import xrf_spectra
from .monitor import monitor_signal
from .deadtime import apply_dualchannel_signal_processing
from .. import nexus_utils


def save_2d_xrf_scans(
    filename: str,
    emission_line_groups: List[str],
    first_scan_number: int,
    shape: Tuple[int, int],
    mosaic: Tuple[int, int],
    energy: float = 12,
    flux: float = 1e7,
    expo_time: float = 0.1,
    counting_noise: bool = True,
    integral_type: bool = True,
    rois: Sequence = tuple(),
    nmcas: int = 1,
    max_deviation: float = 0,
    seed: Optional[int] = None,
) -> List[int]:
    """Simulates and saves 2D XRF scans to a NeXus file.

    :param filename: Output file path.
    :param emission_line_groups: List of emission line groups as "Element-Group".
    :param first_scan_number: Scan number of the first scan in the output file.
    :param shape: Scan shape.
    :param mosaic: Split shape in this number of blocks.
    :param energy: Incident X-ray energy in keV.
    :param flux: Incident X-ray flux in photons per second.
    :param expo_time: Exposure time per point in seconds.
    :param counting_noise: If True, adds Poisson noise to data.
    :param integral_type: If True, data represents integrated intensities.
    :param rois: Regions of interest as energy ranges.
    :param ndetectors: Number of detectors.
    :param max_deviation: Maximum deviation from a perfect grid as a fraction of the scan step size.
    :param seed: Random seed for reproducibility.

    :returns: Scan numbers as many as there are blocks in the mosaic.

    :raises ValueError: If `shape` is not 2D.
    """
    max_deviation = max(max_deviation, 0)
    rstate = numpy.random.RandomState(seed=seed)
    I0_max = int(flux * expo_time)
    emission_line_groups = [s.split("-") for s in emission_line_groups]

    specs = _amesh_specs(
        shape=shape, mosaic=mosaic, max_deviation=max_deviation, expo_time=expo_time
    )
    scan_numbers = list()
    for scan_number, amesh in enumerate(specs, start=first_scan_number):
        scan_numbers.append(scan_number)

        coordinates = _amesh_positions(amesh, rstate, max_deviation)

        # decaying I0 image
        I0 = (I0_max * monitor_signal(expo_time, amesh.size)).reshape(
            amesh.shape, order="F"
        )

        # random images with values between 0 and 1
        fluoI0fractions = list(
            _iter_amesh_data(
                amesh, coordinates, rstate, nmaps=len(emission_line_groups)
            )
        )
        scatterI0fractions = list(_iter_amesh_data(amesh, coordinates, rstate, nmaps=2))

        # Peak area counts within expo_time seconds
        linegroups = [
            xrf_spectra.EmissionLineGroup(
                element, group, (I0 * I0fraction).astype(numpy.uint32)
            )
            for I0fraction, (element, group) in zip(
                fluoI0fractions, emission_line_groups
            )
        ]
        scattergroups = [
            xrf_spectra.ScatterLineGroup(
                "Compton000", (I0 * scatterI0fractions[0]).astype(numpy.uint32)
            ),
            xrf_spectra.ScatterLineGroup(
                "Peak000", (I0 * scatterI0fractions[1]).astype(numpy.uint32)
            ),
        ]

        # Theoretical XRF spectra
        theoretical_spectra, config = xrf_spectra.xrf_spectra(
            linegroups,
            scattergroups,
            energy=energy,
            flux=flux,
            elapsed_time=expo_time,
        )

        # Measured XRF spectra
        if integral_type:
            integral_type = numpy.uint32
        else:
            integral_type = None
        measured_data = apply_dualchannel_signal_processing(
            theoretical_spectra,
            elapsed_time=expo_time,
            counting_noise=counting_noise,
            integral_type=integral_type,
        )

        # ROI data (theoretical, measured and corrected)
        roi_data_theory = dict()
        roi_data_cor = dict()  # I0 and LT corrected
        I0_reference = I0_max
        for i, roi in enumerate(rois, 1):
            roi_name = f"roi{i}"
            idx = Ellipsis, slice(*roi)

            roi_theory = theoretical_spectra[idx].sum(axis=-1) / I0 * I0_max
            roi_data_theory[roi_name] = roi_theory

            roi_meas = measured_data["spectrum"][idx].sum(axis=-1)
            measured_data[roi_name] = roi_meas

            cor = I0_reference / I0 * expo_time / measured_data["live_time"]
            roi_data_cor[roi_name] = cor * roi_meas

        _save_2d_xrf_scans(
            filename,
            scan_number,
            amesh,
            coordinates,
            energy,
            I0,
            I0_reference,
            nmcas,
            measured_data,
            roi_data_theory,
            roi_data_cor,
            linegroups,
            scattergroups,
            config,
        )
    return scan_numbers


class _AmeshAxis(NamedTuple):
    name: str
    start: float
    end: float
    intervals: int

    @property
    def size(self) -> int:
        return self.intervals + 1

    @property
    def coordinates(self) -> numpy.ndarray:
        return numpy.linspace(self.start, self.end, self.size)


class _Amesh(NamedTuple):
    fast: _AmeshAxis
    slow: _AmeshAxis
    expo_time: float

    def __str__(self):
        return f"amesh {self.fast.name} {self.fast.start} {self.fast.end} {self.fast.intervals} {self.slow.name} {self.slow.start} {self.slow.end} {self.slow.intervals} {self.expo_time}"

    @property
    def shape(self) -> Tuple[int]:
        return (self.fast.size, self.slow.size)

    @property
    def size(self) -> int:
        return self.fast.size * self.slow.size


@functools.lru_cache(maxsize=1)
def _scene_data() -> Tuple[numpy.ndarray, List[str]]:
    """Data in pixel coordinates on which to interpolate for create amesh data.

    :returns: array with shape `(nimages, nfast, nslow)`, fast and slow axis name (in that order)
    """
    filename = os.path.join(os.path.dirname(__file__), "ihc.png")
    scene_data = numpy.transpose(imread(filename), [2, 0, 1])
    _mark_fast_axis(scene_data)
    scene_axes = ["sampz", "sampy"]
    return scene_data, scene_axes


def _mark_fast_axis(channels: numpy.ndarray) -> None:
    """Modify the image intensities to mark the fast axis (first dimension)."""
    image_shape = channels[0].shape

    dstart = image_shape[0] // 10, image_shape[1] // 10
    dtick = dstart[0] // 4, dstart[1] // 4

    p0 = dstart[0] - dtick[0], dstart[1] - dtick[1]
    p1 = dstart[0] + dtick[0], dstart[1] + dtick[1]
    channels[:, p0[0] : p1[0], p0[1] : p1[1]] = 255

    dtick = dtick[0] // 2, dtick[1] // 2
    dend = image_shape[0] // 2, image_shape[1] // 10

    p0 = dstart[0] - dtick[0], dstart[1] - dtick[1]
    p1 = dend[0] + dtick[0], dend[1] + dtick[1]
    channels[:, p0[0] : p1[0], p0[1] : p1[1]] = 255


def _amesh_specs(
    shape: Tuple[int, int],
    mosaic: Tuple[int, int],
    max_deviation: float = 0,
    expo_time: float = 0.1,
) -> List[_Amesh]:
    """
    Generate a list of _Amesh instances based on the provided parameters.

    :param shape: Number of interpolation points along each axis (fast, slow).
    :param mosaic: Number of blocks along each axis (fast, slow).
    :param max_deviation: Maximum deviation from a perfect grid as a fraction of the scan step size.
    :param expo_time: Exposure time per point in seconds.
    :return: List of _Amesh instances.
    """
    scene_data, scene_axes = _scene_data()
    scene_shape = scene_data.shape[1:]

    fast_axes = _amesh_axes(
        scene_axes[0], scene_shape[0], shape[0], mosaic[0], max_deviation
    )
    slow_axes = _amesh_axes(
        scene_axes[1], scene_shape[1], shape[1], mosaic[1], max_deviation
    )
    amesh_list = list()
    for slow in slow_axes:
        for fast in fast_axes:
            amesh_list.append(_Amesh(fast, slow, expo_time))
    return amesh_list


def _amesh_axes(
    name: str, scene_size: int, total_size: int, mosaic: int, max_deviation: float
) -> List[_AmeshAxis]:
    """
    Generate a list of _AmeshAxis instances based on the provided parameters.

    :param name: Axis name.
    :param scene_size: Total of scene data points.
    :param total_size: Number of scan points.
    :param mosaic: Number of scans to span the scene.
    :param max_deviation: Maximum deviation from a perfect grid as a fraction of the scan step size.
    """
    block_size = total_size // mosaic
    block_intervals = block_size - 1

    scene_block_range = (scene_size - 1) / (
        mosaic + (2 * max_deviation / block_intervals)
    )
    interpolate_step_size = scene_block_range / block_intervals
    scan_border = max_deviation * interpolate_step_size
    scene_start = scan_border
    # scene_end = scene_size - 1 - scan_border
    # assert ((scene_end - scene_start) / scene_block_range - mosaic) < 1e-6

    axes = list()
    for i in range(mosaic):
        block_start = scene_start + i * scene_block_range
        block_end = block_start + scene_block_range

        axes.append(
            _AmeshAxis(
                name=name,
                start=block_start,
                end=block_end,
                intervals=block_intervals,
            )
        )
    return axes


def _save_2d_xrf_scans(
    filename: str,
    scan_number: int,
    amesh: _Amesh,
    coordinates: List[numpy.ndarray],
    energy: float,
    I0: numpy.ndarray,
    I0_reference: float,
    nmcas: int,
    measured_data: Dict[str, numpy.ndarray],
    roi_data_theory: Dict[str, numpy.ndarray],
    roi_data_cor: Dict[str, numpy.ndarray],
    linegroups: List[xrf_spectra.EmissionLineGroup],
    scattergroups: List[xrf_spectra.ScatterLineGroup],
    config: ConfigDict,
) -> None:
    with h5py_utils.File(filename, mode="a") as nxroot:
        scan_name = f"{scan_number}.1"
        nxroot.attrs["NX_class"] = "NXroot"
        nxroot.attrs["creator"] = "ewoksfluo"

        nxentry = nxroot.require_group(scan_name)
        nxentry.attrs["NX_class"] = "NXentry"
        if "title" in nxentry:
            del nxentry["title"]
        nxentry["title"] = str(amesh)

        nxinstrument = nxentry.require_group("instrument")
        nxinstrument.attrs["NX_class"] = "NXinstrument"

        measurement = nxentry.require_group("measurement")
        measurement.attrs["NX_class"] = "NXcollection"

        fast_coordinates = coordinates[0].flatten(order="F")
        slow_coordinates = coordinates[1].flatten(order="F")

        # Positioners
        for name in ("positioners_start", "positioners_end", "positioners"):
            group = nxinstrument.require_group(name)
            group.attrs["NX_class"] = "NXcollection"

            if "energy" in group:
                del group["energy"]
            group["energy"] = energy
            group["energy"].attrs["units"] = "keV"

            if name == "positioners":
                continue

            if name == "positioners_start":
                idx = 0
            else:
                idx = -1

            if amesh.fast.name in group:
                del group[amesh.fast.name]
            group[amesh.fast.name] = fast_coordinates[idx]
            group[amesh.fast.name].attrs["units"] = "um"

            if amesh.slow.name in group:
                del group[amesh.slow.name]
            group[amesh.slow.name] = slow_coordinates[idx]
            group[amesh.slow.name].attrs["units"] = "um"
        positioners = nxinstrument["positioners"]

        # I0 data
        nxdetector = nxinstrument.require_group("I0")
        nxdetector.attrs["NX_class"] = "NXdetector"
        if "data" in nxdetector:
            del nxdetector["data"]
        nxdetector["data"] = I0.flatten(order="F")
        if "I0" not in measurement:
            measurement["I0"] = h5py.SoftLink(nxdetector["data"].name)

        # Fast axis
        nxpositioner = nxinstrument.require_group(amesh.fast.name)
        nxpositioner.attrs["NX_class"] = "NXpositioner"
        if "value" in nxpositioner:
            del nxpositioner["value"]
        nxpositioner["value"] = fast_coordinates
        nxpositioner["value"].attrs["units"] = "um"
        if amesh.fast.name not in measurement:
            measurement[amesh.fast.name] = h5py.SoftLink(nxpositioner["value"].name)
        if amesh.fast.name not in positioners:
            positioners[amesh.fast.name] = h5py.SoftLink(nxpositioner["value"].name)

        # Slow axis
        nxpositioner = nxinstrument.require_group(amesh.slow.name)
        nxpositioner.attrs["NX_class"] = "NXpositioner"
        if "value" in nxpositioner:
            del nxpositioner["value"]
        nxpositioner["value"] = slow_coordinates
        nxpositioner["value"].attrs["units"] = "um"
        if amesh.slow.name not in measurement:
            measurement[amesh.slow.name] = h5py.SoftLink(nxpositioner["value"].name)
        if amesh.slow.name not in positioners:
            positioners[amesh.slow.name] = h5py.SoftLink(nxpositioner["value"].name)

        # MCA detector
        for i in range(nmcas):
            det_name = f"mca{i}"
            nxdetector = nxinstrument.require_group(det_name)
            nxdetector.attrs["NX_class"] = "NXdetector"
            for signal_name, signal_values in measured_data.items():
                if signal_name in nxdetector:
                    del nxdetector[signal_name]
                if signal_name == "spectrum":
                    mca_shape = (amesh.size, signal_values.shape[-1])
                    nxdetector[signal_name] = signal_values.reshape(
                        mca_shape, order="F"
                    )
                    if "data" not in nxdetector:
                        nxdetector["data"] = h5py.SoftLink("spectrum")
                    meas_name = det_name
                else:
                    nxdetector[signal_name] = signal_values.flatten(order="F")
                    meas_name = f"{det_name}_{signal_name}"
                if meas_name not in measurement:
                    measurement[meas_name] = h5py.SoftLink(nxdetector[signal_name].name)

        nxprocess = nxentry.require_group("theory")
        nxprocess.attrs["NX_class"] = "NXprocess"
        if "I0_reference" in nxprocess:
            del nxprocess["I0_reference"]
        nxprocess["I0_reference"] = I0_reference

        nxnote = nxprocess.require_group("configuration")
        nxnote.attrs["NX_class"] = "NXnote"
        if "data" in nxnote:
            del nxnote["data"]
        if "type" in nxnote:
            del nxnote["type"]
        nxnote["type"] = "application/pymca"
        nxnote["data"] = config.tostring()

        nxnote = nxprocess.require_group("description")
        nxnote.attrs["NX_class"] = "NXnote"
        if "data" in nxnote:
            del nxnote["data"]
        if "type" in nxnote:
            del nxnote["type"]
        nxnote["type"] = "text/plain"
        description = [
            "- parameters: peak areas without dead-time",
            "- parameters_norm: peak areas without dead-time and I0 normalized",
            "- rois: MCA ROI's without dead-time and I0 normalized (theoretical)",
            "- rois_norm: MCA ROI's without dead-time and I0 normalized (calculated)",
        ]
        nxnote["data"] = "\n".join(description)

        signals = {f"{g.element}-{g.name}": g.counts for g in linegroups}
        signals.update({g.name: g.counts for g in scattergroups})
        _save_nxdata(amesh, nxprocess, "parameters", signals, positioners)

        signals = {
            f"{g.element}-{g.name}": g.counts / I0 * I0_reference for g in linegroups
        }
        signals.update({g.name: g.counts / I0 * I0_reference for g in scattergroups})
        _save_nxdata(amesh, nxprocess, "parameters_norm", signals, positioners)

        if roi_data_theory:
            _save_nxdata(amesh, nxprocess, "rois", roi_data_theory, positioners)

        if roi_data_cor:
            _save_nxdata(amesh, nxprocess, "rois_norm", roi_data_cor, positioners)

        if "end_time" in nxentry:
            del nxentry["end_time"]
        nxentry["end_time"] = nexus_utils.now()


def _save_nxdata(
    amesh: _Amesh,
    parent: h5py.Group,
    name: str,
    signals: Dict[str, numpy.ndarray],
    positioners: h5py.Group,
) -> None:
    """Saves a set of signals as NeXus data to a given parent group.

    :param amesh: Scan description.
    :param parent: The parent `h5py.Group` where the data will be saved.
    :param name: The name of the dataset to be saved under.
    :param signals: Dictionary of signal names and their corresponding data arrays.
    :param positioners: Group containing the positioners (`sampz` and `sampy`) for the scan.
    """
    nxdata = parent.require_group(name)
    nxdata.attrs["NX_class"] = "NXdata"
    # nxdata.attrs["interpretation"] = "image"
    names = list(signals.keys())
    nxdata.attrs["signal"] = names[0]
    if len(names) > 1:
        nxdata.attrs["auxiliary_signals"] = names[1:]
    for signal_name, signal_values in signals.items():
        if signal_name in nxdata:
            del nxdata[signal_name]
        nxdata[signal_name] = signal_values.flatten(order="F")
    nxdata.attrs["axes"] = [amesh.fast.name, amesh.slow.name]  # Order: fast to slow
    if amesh.fast.name not in nxdata:
        nxdata[amesh.fast.name] = h5py.SoftLink(positioners[amesh.fast.name].name)
    if amesh.slow.name not in nxdata:
        nxdata[amesh.slow.name] = h5py.SoftLink(positioners[amesh.slow.name].name)


def _iter_amesh_data(
    amesh: _Amesh,
    coordinates: List[numpy.ndarray],
    rstate: numpy.random.RandomState,
    nmaps: int = 1,
) -> Iterator[numpy.ndarray]:
    """Yield random samples of an image scanned with `amesh`.

    :param amesh: Scan description.
    :param coordinates: Scan coordinates (fast axis first).

    :returns: signal (F-order matrix).
    """
    scene_data, scene_axes = _scene_data()
    scan_axes = [amesh.fast.name, amesh.slow.name]
    if scan_axes == scene_axes:
        pass
    elif scan_axes == scene_axes[::-1]:
        # Flip fast and slow axis
        scene_data = numpy.transpose(scene_data, [0, 2, 1])
    else:
        raise ValueError("Must be an amesh scan over 'sampy' and 'sampz'")

    flat_coordinates = [x.flatten(order="F") for x in coordinates]
    for _ in range(nmaps):
        # Random linear combination of the RGB channels which
        # results in an image with values between 0 and 1
        fractions = rstate.uniform(low=0, high=1, size=3)
        fractions /= 255 * fractions.sum()
        image = sum(fractions[:, numpy.newaxis, numpy.newaxis] * scene_data)

        # Interpolate the image (pixel coordinates) on the coordinate grid
        iimage = ndimage.map_coordinates(
            image, flat_coordinates, order=1, cval=0, mode="nearest"
        )
        yield iimage.reshape(amesh.shape, order="F")


def _amesh_positions(
    asmesh: _Amesh,
    rstate: numpy.random.RandomState,
    max_deviation: float = 0,
) -> List[numpy.ndarray]:
    """Generates motor positions for an amesh scan with optional deviations (fast axis first)."""
    positions = numpy.meshgrid(
        asmesh.fast.coordinates, asmesh.slow.coordinates, indexing="ij"
    )
    if not max_deviation:
        return positions
    deviations = [
        abs(
            max_deviation
            if axis.size <= 1
            else (axis.end - axis.start) / (axis.size - 1) * max_deviation
        )
        for axis in [asmesh.fast, asmesh.slow]
    ]
    positions = [
        values + rstate.uniform(low=-d, high=d, size=asmesh.shape)
        for values, d in zip(positions, deviations)
    ]
    return positions
