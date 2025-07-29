from typing import Dict, Sequence, Union

import numpy

from ewoksfluo.xrffit.config import adapt_pymca_config_energy
from PyMca5.PyMcaIO.ConfigDict import ConfigDict


def generate_pymca_config(fit_config: Dict[str, Sequence[Union[float, int]]]):
    return ConfigDict(
        initdict={
            "fit": fit_config,
            "attenuators": {"Matrix": [1, "Cerussite", 6.8, 0.1, 62.0, 49, 0, 111.0]},
            "materials": {},
        }
    )


def test_replace_energy():
    cfg = generate_pymca_config(
        {
            "energy": [2, 5, 10, 20, 50],
            "energyflag": [1, 0, 1, 0, 0],
            "energyscatter": [1, 0, 0, 1, 0],
            "energyweight": [1.0, 0.25, 0.2, 0.1, 0.1],
        }
    )
    energy = 2.5
    energy_multiplier = 10

    adapt_pymca_config_energy(cfg, energy, energy_multiplier)

    numpy.testing.assert_allclose(cfg["fit"]["energy"], numpy.array([2.5, 12.5, 25]))
    numpy.testing.assert_equal(cfg["fit"]["energyflag"], numpy.array([1, 1, 1]))
    numpy.testing.assert_equal(cfg["fit"]["energyscatter"], numpy.array([1, 0, 0]))
    numpy.testing.assert_allclose(
        cfg["fit"]["energyweight"], numpy.array([1.0, 0.2, 1e-10])
    )


def test_replace_energy_all_defined():
    cfg = generate_pymca_config(
        {
            "energy": [2],
            "energyflag": [1],
            "energyscatter": [1],
            "energyweight": [1.0],
        }
    )
    energy = 4
    energy_multiplier = 10

    adapt_pymca_config_energy(cfg, energy, energy_multiplier)

    numpy.testing.assert_allclose(cfg["fit"]["energy"], numpy.array([4, 40]))
    numpy.testing.assert_equal(cfg["fit"]["energyflag"], numpy.array([1, 1]))
    numpy.testing.assert_equal(cfg["fit"]["energyscatter"], numpy.array([1, 0]))
    numpy.testing.assert_allclose(cfg["fit"]["energyweight"], numpy.array([1.0, 1e-10]))


def test_replace_energy_no_multiplier():
    cfg = generate_pymca_config(
        {
            "energy": [2, 5, 10, 20, 50],
            "energyflag": [1, 0, 1, 0, 0],
            "energyscatter": [1, 0, 0, 1, 0],
            "energyweight": [1.0, 0.25, 0.2, 0.1, 0.1],
        }
    )
    energy = 2.5
    energy_multiplier = 0

    adapt_pymca_config_energy(cfg, energy, energy_multiplier)

    numpy.testing.assert_allclose(cfg["fit"]["energy"], numpy.array([2.5, 12.5]))
    numpy.testing.assert_equal(cfg["fit"]["energyflag"], numpy.array([1, 1]))
    numpy.testing.assert_equal(cfg["fit"]["energyscatter"], numpy.array([1, 0]))
    numpy.testing.assert_allclose(cfg["fit"]["energyweight"], numpy.array([1.0, 0.2]))


def test_replace_energy_not_defined():
    cfg = generate_pymca_config(
        {
            "energy": [2, 5, 10, 20, 50],
            "energyflag": [0, 0, 0, 0, 0],
            "energyscatter": [1, 0, 0, 1, 0],
            "energyweight": [1.0, 0.25, 0.2, 0.1, 0.1],
        }
    )
    energy = 6
    energy_multiplier = 3

    adapt_pymca_config_energy(cfg, energy, energy_multiplier)

    numpy.testing.assert_allclose(
        cfg["fit"]["energy"], numpy.array([energy, energy_multiplier * energy])
    )
    numpy.testing.assert_equal(cfg["fit"]["energyflag"], numpy.array([1, 1]))
    numpy.testing.assert_equal(cfg["fit"]["energyscatter"], numpy.array([0, 0]))
    numpy.testing.assert_allclose(cfg["fit"]["energyweight"], numpy.array([1.0, 1e-10]))


def test_replace_energy_not_defined_no_multiplier():
    cfg = generate_pymca_config(
        {
            "energy": [2, 5, 10, 20, 50],
            "energyflag": [0, 0, 0, 0, 0],
            "energyscatter": [1, 0, 0, 1, 0],
            "energyweight": [1.0, 0.25, 0.2, 0.1, 0.1],
        }
    )
    energy = 7.1
    energy_multiplier = 0

    adapt_pymca_config_energy(cfg, energy, energy_multiplier)

    numpy.testing.assert_allclose(cfg["fit"]["energy"], numpy.array([energy]))
    numpy.testing.assert_equal(cfg["fit"]["energyflag"], numpy.array([1]))
    numpy.testing.assert_equal(cfg["fit"]["energyscatter"], numpy.array([0]))
    numpy.testing.assert_allclose(cfg["fit"]["energyweight"], numpy.array([1.0]))
