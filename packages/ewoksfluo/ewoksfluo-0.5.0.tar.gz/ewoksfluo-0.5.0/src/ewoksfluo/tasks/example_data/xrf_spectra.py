from typing import Dict, NamedTuple, Sequence, Tuple, Union

import numpy
from PyMca5.PyMcaPhysics.xrf.ClassMcaTheory import McaTheory
from PyMca5.PyMcaIO.ConfigDict import ConfigDict


class EmissionLineGroup(NamedTuple):
    element: str
    name: str
    counts: Union[float, Sequence]

    @property
    def counts_asarray(self):
        return get_counts_array(self.counts)


class ScatterLineGroup(NamedTuple):
    name: str
    counts: Union[float, Sequence]
    prefix: str = "Scatter"

    @property
    def counts_asarray(self):
        return get_counts_array(self.counts)


def get_counts_array(counts: Union[float, Sequence]):
    if isinstance(counts, Sequence):
        return numpy.asarray(counts)
    return numpy.array((counts))


def xrf_spectra(
    linegroups: Sequence[EmissionLineGroup],
    scattergroups: Sequence[ScatterLineGroup],
    nchannels: int = 1024,
    energy: float = 7.5,
    angle_in: float = 62.0,
    angle_out: float = 49.0,
    flux: float = 1e10,
    elapsed_time: float = 1.0,
) -> Tuple[numpy.ndarray, ConfigDict]:
    """The returned spectra have the shape `counts.shape + (nchannels,)`"""
    peaks = {linegroup.element: linegroup.name for linegroup in linegroups}
    counts: Dict[str, numpy.ndarray] = {
        f"{group.element} {group.name}": group.counts_asarray for group in linegroups
    }
    counts.update(
        {f"Scatter {group.name}": group.counts_asarray for group in scattergroups}
    )

    # MCA parameters
    zero = 0  # keV
    max_energy = energy + 1.5  # keV
    gain = (max_energy - zero) / nchannels

    # Initialize theory
    theory = McaTheory()
    theory.setConfiguration(
        get_configuration(
            peaks,
            xmin=1,
            xmax=nchannels - 3,
            zero=zero,
            gain=gain,
            energy=energy,
            angle_in=angle_in,
            angle_out=angle_out,
            flux=flux,
            elapsed_time=elapsed_time,
        )
    )

    # Calculate emission lines
    x = numpy.arange(nchannels)
    theory.setData(x=x, y=numpy.zeros(nchannels))
    theory.enableOptimizedLinearFit()
    theory.estimate()

    # Analytical XRF spectrum
    nglobal = theory.NGLOBAL
    if counts:
        shape = next(iter(counts.values())).shape
    else:
        shape = tuple()
    y = numpy.zeros(shape + (nchannels,))
    for i, name in enumerate(theory.PARAMETERS[nglobal:], nglobal):
        normalized_group = theory.linearMcaTheoryDerivative(
            numpy.asarray(theory.parameters), i, x
        )
        assert isinstance(normalized_group, numpy.ndarray)
        if shape:
            y += counts[name][..., None] * normalized_group[None, ...]
        else:
            y += counts[name] * normalized_group

    return y, theory.config


def get_configuration(
    peaks: dict,
    xmin: int = 0,
    xmax: int = 0,
    zero: float = 0,
    gain: float = 0.005,
    energy: float = 0,
    angle_in: float = 62.0,
    angle_out: float = 49.0,
    flux: float = 1e10,
    elapsed_time: float = 1.0,
):
    return {
        "peaks": peaks,
        "attenuators": get_attenuators(angle_in=angle_in, angle_out=angle_out),
        "fit": get_fit_config(xmin=xmin, xmax=xmax, energy=energy),
        "concentrations": get_quantification_config(
            flux=flux, elapsed_time=elapsed_time
        ),
        "detector": get_detector(zero=zero, gain=gain),
        "peakshape": get_peak_shape(),
        "materials": {
            "SingleLayerStrategyMaterial": {
                "Comment": "Last Single Layer Strategy iteration",
                "Thickness": 0.0025,
                "Density": 1.42,
                "CompoundFraction": "",
                "CompoundList": "",
            },
            **get_materials(),
        },
        "multilayer": {
            "Layer0": [1, "Cerussite", 6.8, 0.1],
            "Layer1": [0, "-", 0.0, 0.0],
            "Layer2": [0, "-", 0.0, 0.0],
            "Layer3": [0, "-", 0.0, 0.0],
            "Layer4": [0, "-", 0.0, 0.0],
            "Layer5": [0, "-", 0.0, 0.0],
            "Layer6": [0, "-", 0.0, 0.0],
            "Layer7": [0, "-", 0.0, 0.0],
            "Layer8": [0, "-", 0.0, 0.0],
            "Layer9": [0, "-", 0.0, 0.0],
        },
        "SingleLayerStrategy": {
            "layer": "Auto",
            "iterations": 3,
            "completer": "-",
            "peaks": "",
            "materials": ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
            "flags": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
        "tube": {
            "transmission": 0,
            "voltage": 30.0,
            "anode": "Ag",
            "anodethickness": 0.0002,
            "anodedensity": 10.5,
            "window": "Be",
            "windowthickness": 0.0125,
            "windowdensity": 1.848,
            "filter1": "He",
            "filter1thickness": 0.0,
            "filter1density": 0.000118,
            "alphax": 90.0,
            "alphae": 90.0,
            "deltaplotting": 0.1,
        },
        "fisx": {},
    }


def get_quantification_config(flux: float = 1e10, elapsed_time: float = 1.0) -> dict:
    return {
        "usematrix": 0,
        "useattenuators": 1,
        "usemultilayersecondary": 0,
        "usexrfmc": 0,
        "mmolarflag": 0,
        "flux": flux,
        "time": elapsed_time,
        "area": 0.774671,
        "distance": 4.15114,
        "reference": "Auto",
        "useautotime": 0,
    }


def get_peak_shape():
    return {
        "st_arearatio": 0.0697778,
        "deltast_arearatio": 0.03,
        "fixedst_arearatio": 1,
        "st_sloperatio": 0.0105551,
        "deltast_sloperatio": 0.49,
        "fixedst_sloperatio": 1,
        "lt_arearatio": 0.1,
        "deltalt_arearatio": 0.15,
        "fixedlt_arearatio": 1,
        "lt_sloperatio": 0.1,
        "deltalt_sloperatio": 0.08,
        "fixedlt_sloperatio": 1,
        "step_heightratio": 0.1,
        "deltastep_heightratio": 5e-05,
        "fixedstep_heightratio": 1,
        "eta_factor": 0.02,
        "deltaeta_factor": 0.02,
        "fixedeta_factor": 1,
    }


def get_fit_config(xmin: int = 0, xmax: int = 0, energy: float = 0) -> dict:
    return {
        "deltaonepeak": 0.01,
        "strategy": "SingleLayerStrategy",
        "strategyflag": 0,
        "fitfunction": 0,
        "continuum": 0,
        "fitweight": 1,
        "stripalgorithm": 1,
        "linpolorder": 5,
        "exppolorder": 6,
        "stripconstant": 1.0,
        "snipwidth": 65,
        "stripiterations": 400,
        "stripwidth": 5,
        "stripfilterwidth": 7,
        "stripanchorsflag": 0,
        "maxiter": 10,
        "deltachi": 0.001,
        "xmin": xmin,
        "xmax": xmax,
        "linearfitflag": 1,
        "use_limit": 0,
        "stripflag": 1,
        "escapeflag": 0,
        "sumflag": 0,
        "scatterflag": 1,
        "hypermetflag": 1,
        "stripanchorslist": [0, 0, 0, 0],
        "energy": [energy],
        "energyweight": [1.0],
        "energyflag": [1],
        "energyscatter": [1],
    }


def get_attenuators(angle_in: float = 62.0, angle_out: float = 49.0) -> dict:
    return {
        "kapton": [1, "Mylar", 1.4, 0.0004, 1.0],
        "atmosphere": [0, "-", 0.0, 0.0, 1.0],
        "deadlayer": [0, "Si1", 2.33, 0.002, 1.0],
        "absorber": [0, "-", 1.0, 0.1, 1.0],
        "window": [1, "Be", 1.848, 0.0025, 1.0],
        "contact": [0, "moxtekAP3.3", 5.45e-05, 1.0, 1.0],
        "Filter 6": [0, "-", 0.0, 0.0, 1.0],
        "Filter 7": [0, "-", 1.0, 0.1, 1.0],
        "BeamFilter0": [0, "-", 0.0, 0.0, 1.0],
        "BeamFilter1": [0, "-", 0.0, 0.0, 1.0],
        "Detector": [1, "Si1", 2.33, 0.5, 1.0],
        "Matrix": [
            1,
            "Cerussite",
            6.8,
            0.1,
            angle_in,
            angle_out,
            0,
            angle_in + angle_out,
        ],
    }


def get_detector(zero: float = 0, gain: float = 0.005) -> dict:
    return {
        "detele": "Si",
        "nthreshold": 4,
        "zero": zero,
        "deltazero": 0.1,
        "fixedzero": 1,
        "gain": gain,
        "deltagain": 0.002,
        "fixedgain": 1,
        "noise": -0.0955892,
        "deltanoise": 0.05,
        "fixednoise": 1,
        "fano": 0.0484433,
        "deltafano": 0.114,
        "fixedfano": 1,
        "sum": 0.0,
        "deltasum": 2e-06,
        "fixedsum": 1,
        "ignoreinputcalibration": 0,
    }


def get_materials() -> dict:
    return {
        "Air": {
            "Comment": "Dry Air (Near sea level) density=0.001204790 g/cm3",
            "Thickness": 1.0,
            "Density": 0.0012048,
            "CompoundFraction": [0.000124, 0.75527, 0.23178, 0.012827, 3.2e-06],
            "CompoundList": ["C1", "N1", "O1", "Ar1", "Kr1"],
        },
        "Goethite": {
            "Comment": "Mineral FeO(OH) density from 3.3 to 4.3 density=4.3 g/cm3",
            "CompoundFraction": 1.0,
            "Thickness": 0.1,
            "Density": 4.3,
            "CompoundList": "Fe1O2H1",
        },
        "Mylar": {
            "Comment": "Mylar (Polyethylene Terephthalate) density=1.40 g/cm3",
            "Density": 1.4,
            "CompoundFraction": [0.041959, 0.625017, 0.333025],
            "CompoundList": ["H1", "C1", "O1"],
        },
        "Kapton": {
            "Comment": "Kapton 100 HN 25 micron density=1.42 g/cm3",
            "Thickness": 0.0025,
            "Density": 1.42,
            "CompoundFraction": [0.628772, 0.066659, 0.304569],
            "CompoundList": ["C1", "N1", "O1"],
        },
        "Teflon": {
            "Comment": "Teflon density=2.2 g/cm3",
            "Density": 2.2,
            "CompoundFraction": [0.240183, 0.759817],
            "CompoundList": ["C1", "F1"],
        },
        "Viton": {
            "Comment": "Viton Fluoroelastomer density=1.8 g/cm3",
            "Density": 1.8,
            "CompoundFraction": [0.009417, 0.280555, 0.710028],
            "CompoundList": ["H1", "C1", "F1"],
        },
        "Water": {
            "Comment": "Water density=1.0 g/cm3",
            "CompoundFraction": 1.0,
            "Thickness": 1.0,
            "Density": 1.0,
            "CompoundList": "H2O1",
        },
        "Gold": {
            "Comment": "Gold",
            "CompoundFraction": 1.0,
            "Thickness": 1e-06,
            "Density": 19.37,
            "CompoundList": "Au",
        },
        "Cerussite": {
            "Comment": "Mineral PbCO3",
            "CompoundFraction": 1.0,
            "Thickness": 0.1,
            "Density": 6.8,
            "CompoundList": "Pb1C1O3",
        },
        "mixture": {
            "Comment": "New Material",
            "Thickness": 1.0,
            "Density": 1.0,
            "CompoundFraction": [0.0096, 0.0234],
            "CompoundList": ["Ca1S1O6H4", "K1Cl1"],
        },
        "sample": {
            "Comment": "New Material",
            "Thickness": 1.0,
            "Density": 2.36,
            "CompoundFraction": 1.0,
            "CompoundList": "Hg1S1",
        },
        "moxtekAP3.3": {
            "Comment": "New Material",
            "Thickness": 1.0,
            "Density": 5.45e-05,
            "CompoundFraction": [0.06, 0.62, 0.055, 0.155, 0.106],
            "CompoundList": ["B", "C", "N", "O", "Al"],
        },
    }


if __name__ == "__main__":
    linegroups = [
        EmissionLineGroup("Si", "K", 300),
        EmissionLineGroup("Al", "K", 400),
        EmissionLineGroup("Cl", "K", 200),
        EmissionLineGroup("Pb", "M", 500),
        EmissionLineGroup("P", "K", 200),
        EmissionLineGroup("S", "K", 600),
        EmissionLineGroup("Ca", "K", 500),
        EmissionLineGroup("Ti", "K", 400),
        EmissionLineGroup("Ce", "L", 500),
        EmissionLineGroup("Fe", "K", 1000),
    ]
    scattergroups = [
        ScatterLineGroup("Peak000", 100),
        ScatterLineGroup("Compton000", 100),
    ]
    spectrum, config = xrf_spectra(linegroups, scattergroups)

    import matplotlib.pyplot as plt

    plt.plot(spectrum)
    plt.show()
