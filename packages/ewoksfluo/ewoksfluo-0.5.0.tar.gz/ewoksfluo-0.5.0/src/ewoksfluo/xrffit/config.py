import os
import logging
from tempfile import mkstemp
from contextlib import contextmanager
from typing import Dict, Optional

import numpy
from PyMca5.PyMcaIO.ConfigDict import ConfigDict
from PyMca5.PyMcaPhysics.xrf import ClassMcaTheory


logger = logging.getLogger(__name__)


class TemporaryFilename(object):
    def __init__(self, suffix=".tmp"):
        self.tmpfilename = mkstemp(suffix)[1]

    def __enter__(self):
        return self.tmpfilename

    def __exit__(self, exc_type, exc_val, exc_tb):
        if os.path.exists(self.tmpfilename):
            os.remove(self.tmpfilename)


@contextmanager
def temp_config_filename(cfg: ConfigDict):
    with TemporaryFilename(suffix=".cfg") as filename:
        cfg.write(filename)
        yield filename


def get_as_list(cfg: dict, key: str) -> list:
    value = cfg[key]
    if isinstance(value, list):
        return value

    return [value]


def adapt_pymca_config_energy(
    cfg: ConfigDict, energy0: Optional[float], energy0_multiplier: Optional[float]
):
    if energy0 is None or not numpy.isfinite(energy0):
        return

    fit_cfg = {
        k: get_as_list(cfg["fit"], k)
        for k in ["energy", "energyweight", "energyflag", "energyscatter"]
    }

    defined_energies_indices = [
        i for i, v in enumerate(fit_cfg["energyflag"]) if v == 1
    ]
    defined_energies_length = len(defined_energies_indices)

    if defined_energies_length == 0:
        new_cfg: Dict[str, list] = {
            "energy": [energy0],
            "energyflag": [1],
            "energyweight": [1.0],
            "energyscatter": [0],
        }
    else:

        def extract_defined_energies(name: str):
            cfg_array = numpy.array(fit_cfg[name])
            return cfg_array[defined_energies_indices]

        new_cfg: Dict[str, list] = {
            "energy": [float(e) for e in extract_defined_energies("energy")],
            "energyflag": [int(e) for e in extract_defined_energies("energyflag")],
            "energyweight": [
                float(e) for e in extract_defined_energies("energyweight")
            ],
            "energyscatter": [
                int(e) for e in extract_defined_energies("energyscatter")
            ],
        }

    # Renormalize energies
    e0 = new_cfg["energy"][0]
    new_cfg["energy"] = [e * energy0 / e0 for e in new_cfg["energy"]]

    # Add faraway line at the end (with small weight to not be fitted) to be sure to include all lines in the energy range
    if energy0_multiplier and new_cfg["energy"][-1] < energy0 * energy0_multiplier:
        new_cfg["energy"].append(energy0 * energy0_multiplier)
        new_cfg["energyflag"].append(1)
        new_cfg["energyweight"].append(1e-10)
        new_cfg["energyscatter"].append(0)

    # Update config
    for k, v in new_cfg.items():
        cfg["fit"][k] = v

    # Dummy matrix (apparently needed for multi-energy)
    if cfg["attenuators"]["Matrix"][0] == 0:
        cfg["materials"]["Dummy"] = {
            "Comment": "Dummy",
            "CompoundFraction": [1],
            "CompoundList": ["H1"],
            "Density": 1.0,
            "Thickness": 0.0,
        }
        cfg["attenuators"]["Matrix"][0] = 1
        cfg["attenuators"]["Matrix"][1] = "Dummy"
        cfg["attenuators"]["Matrix"][2] = 1.0
        cfg["attenuators"]["Matrix"][3] = 0.0  # thickness in cm


def adapt_pymca_config_mlines(cfg: ConfigDict, mlines: dict):
    """
    :param dict mlines: for example `{"Pb":["M4", "M5]}}`
    """

    # Split M-lines
    # /usr/local/lib/python2.7/dist-packages/PyMca5/PyMcaPhysics/xrf/Elements.py
    # /users/opid21/.local/lib/python2.7/site-packages/PyMca5/PyMcaPhysics/xrf/Elements.py
    #
    # You need an adapted pymca version: Elements
    # ElementShellTransitions = [KShell.ElementKShellTransitions,
    #                       KShell.ElementKAlphaTransitions,
    #                       KShell.ElementKBetaTransitions,
    #                       LShell.ElementLShellTransitions,
    #                       LShell.ElementL1ShellTransitions,
    #                       LShell.ElementL2ShellTransitions,
    #                       LShell.ElementL3ShellTransitions,
    #                      [s+"*" for s in MShell.ElementMShellTransitions],
    #                       MShell.ElementM1ShellTransitions,
    #                       MShell.ElementM2ShellTransitions,
    #                       MShell.ElementM3ShellTransitions,
    #                       MShell.ElementM4ShellTransitions,
    #                       MShell.ElementM5ShellTransitions]
    # ElementShellRates = [KShell.ElementKShellRates,
    #                 KShell.ElementKAlphaRates,
    #                 KShell.ElementKBetaRates,
    #                 LShell.ElementLShellRates,
    #                 LShell.ElementL1ShellRates,
    #                 LShell.ElementL2ShellRates,
    #                 LShell.ElementL3ShellRates,
    #                 MShell.ElementMShellRates,
    #                 MShell.ElementM1ShellRates,
    #                 MShell.ElementM2ShellRates,
    #                 MShell.ElementM3ShellRates,
    #                 MShell.ElementM4ShellRates,
    #                 MShell.ElementM5ShellRates]
    # ElementXrays      = ['K xrays', 'Ka xrays', 'Kb xrays', 'L xrays','L1 xrays','L2 xrays','L3 xrays','M xrays','M1 xrays','M2 xrays','M3 xrays','M4 xrays','M5 xrays']
    if "M5 xrays" not in ClassMcaTheory.Elements.ElementXrays:
        msg = "XRF fit: PyMca5.PyMcaPhysics.xrf.Elements is not patched to supported M-line group splitting."
        logger.error(msg)
        raise ImportError(msg)
    for el in mlines:
        if el in cfg["peaks"]:
            if "M" in cfg["peaks"][el]:
                cfg["peaks"][el] = [
                    group for group in cfg["peaks"][el] if group != "M"
                ] + mlines[el]


def adapt_pymca_config_quant(cfg: ConfigDict, quant: dict):
    if "flux" in quant:
        cfg["concentrations"]["flux"] = quant["flux"]
    if "time" in quant:
        cfg["concentrations"]["time"] = quant["time"]
    if "area" in quant:
        cfg["concentrations"]["area"] = quant["area"]
    if "distance" in quant:
        cfg["concentrations"]["distance"] = quant["distance"]
    if "anglein" in quant:
        cfg["attenuators"]["Matrix"][4] = quant["anglein"]
    if "angleout" in quant:
        cfg["attenuators"]["Matrix"][5] = quant["angleout"]
    if "anglein" in quant or "angleout" in quant:
        cfg["attenuators"]["Matrix"][7] = (
            cfg["attenuators"]["Matrix"][4] + cfg["attenuators"]["Matrix"][5]
        )


def adapt_pymca_config_fast(cfg: ConfigDict):
    if cfg["fit"]["linearfitflag"] == 0:
        cfg["fit"]["linearfitflag"] = 1

    if "strategyflag" not in cfg["fit"]:
        cfg["fit"]["strategyflag"] = 0
    elif cfg["fit"]["strategyflag"]:
        cfg["fit"]["strategyflag"] = 0

    cfg["fit"]["fitweight"] = 0


def adapt_pymca_config_forcebatch(cfg: ConfigDict):
    # Force no weights (for spectra with low counts):
    cfg["fit"]["fitweight"] = 0


def log_config_adaptation(cfg: ConfigDict, quant: Optional[dict], fast: bool):
    ind = numpy.array(cfg["fit"]["energyflag"]).astype(bool)
    _energy = numpy.array(cfg["fit"]["energy"])[ind]
    _weights = numpy.array(cfg["fit"]["energyweight"])[ind]
    _weights = _weights / _weights.sum() * 100
    _scatter = numpy.array(cfg["fit"]["energyscatter"])[ind]

    info = "\n ".join(
        [
            "{} keV (Rate = {:.2f}%, Scatter {})".format(en, w, "ON" if scat else "OFF")
            for en, w, scat in zip(_energy, _weights, _scatter)
        ]
    )
    if quant:
        info += "\n flux = {:e} ph/sec\n time = {} s\n active area = {} cm^2\n sample-detector distance = {} cm\n angle IN = {} deg\n angle OUT = {} deg".format(
            cfg["concentrations"]["flux"],
            cfg["concentrations"]["time"],
            cfg["concentrations"]["area"],
            cfg["concentrations"]["distance"],
            cfg["attenuators"]["Matrix"][4],
            cfg["attenuators"]["Matrix"][5],
        )

    if cfg["attenuators"]["Matrix"][0] == 0:
        info += "\n Matrix = None"
    else:
        info += "\n Matrix = {}".format(cfg["attenuators"]["Matrix"][1])
    info += "\n Linear = {}".format("YES" if cfg["fit"]["linearfitflag"] else "NO")
    info += "\n Fast fitting = {}".format("YES" if fast else "NO")
    info += "\n Error propagation = {}".format(
        "Poisson" if cfg["fit"]["fitweight"] else "OFF"
    )
    info += "\n Matrix adjustment = {}".format(
        "ON" if cfg["fit"]["strategyflag"] else "OFF"
    )

    logger.info("XRF fit configuration adapted:\n {}".format(info))


def adapt_pymca_config(
    cfg: ConfigDict,
    energy: Optional[float],
    energy_multiplier: Optional[float],
    mlines: Optional[dict] = None,
    quant: Optional[dict] = None,
    fast: bool = False,
) -> None:
    """
    :param cfg: pymca configuration
    :param energy: primary beam energy in keV
    :param energy_multiplier: add high primary energy with given multiplier with very low weight
    :param mlines: elements (keys) which M line group must be replaced by some M subgroups (values)
    :param quant:
    """
    adapt_pymca_config_energy(cfg, energy, energy_multiplier)
    if mlines:
        adapt_pymca_config_mlines(cfg, mlines)
    if quant and isinstance(quant, dict):
        adapt_pymca_config_quant(cfg, quant)
    if fast:
        adapt_pymca_config_fast(cfg)
    adapt_pymca_config_forcebatch(cfg)
    log_config_adaptation(cfg, quant, fast)
