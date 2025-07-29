from typing import Dict

import numpy
import h5py
import pytest

from ewoksfluo.xrffit import perform_batch_fit
from ewoksfluo.xrffit import outputbuffer_context
from ewoksfluo.io.hdf5 import split_h5uri

from .utils import generate_data


@pytest.mark.parametrize("nscans", [1, 2])
@pytest.mark.parametrize("npoints_per_scan", [1, 7, 200])
@pytest.mark.parametrize("fast", [True, False])
@pytest.mark.parametrize("output_handler", ["nexus", "pymca"])
@pytest.mark.parametrize("samefile", [True, False])
def test_single_detector_fit(
    tmpdir, nscans, npoints_per_scan, fast, output_handler, samefile
):
    if not fast and npoints_per_scan > 10:
        pytest.skip("too slow, no extra value in testing")
    if not samefile and nscans == 1:
        pytest.skip("no extra value in testing")

    diagnostics = True
    figuresofmerit = True
    quantification = True
    energy = 7.5
    energy_multiplier = 10

    # Generate data
    xrf_spectra_uris, spectra, parameters, config = generate_data(
        tmpdir, npoints_per_scan, energy, samefile=samefile, nscans=nscans
    )
    xrf_spectra_uris = xrf_spectra_uris[0]
    spectra = spectra[0]

    # Output
    output_root_uri = str(tmpdir / "output.h5::/1.1/fit")
    xrf_results_uri = str(tmpdir / "output.h5::/1.1/fit/results")

    # Configuration
    config_filename = str(tmpdir / "config.cfg")
    config.write(config_filename)

    # Perform fit
    with outputbuffer_context(
        output_root_uri,
        diagnostics=diagnostics,
        figuresofmerit=figuresofmerit,
        output_handler=output_handler,
    ) as output_buffer:
        kwargs = {
            "xrf_spectra_uris": xrf_spectra_uris,
            "cfg": config_filename,
            "output_buffer": output_buffer,
            "energy": energy,
            "energy_multiplier": energy_multiplier,
            "fast": fast,
            "quantification": quantification,
        }

        if not samefile and nscans > 1:
            with pytest.raises(
                ValueError, match="cannot handle scans in different files"
            ):
                perform_batch_fit(**kwargs)
            return

        perform_batch_fit(**kwargs)

        assert output_buffer.xrf_results_uri == xrf_results_uri

    if output_handler == "pymca":
        # The pymca output handler keeps the data dimensions
        if nscans > 1 and npoints_per_scan > 1:
            newshape = (nscans, npoints_per_scan, spectra.shape[-1])
            spectra = spectra.reshape(newshape)
        else:
            spectra = spectra[None, ...]

    _validate_results(xrf_results_uri, output_handler, fast, parameters, spectra)


def _validate_results(
    xrf_results_uri: str,
    output_handler: str,
    fast: bool,
    parameters: Dict[str, numpy.ndarray],
    spectra: numpy.ndarray,
):
    output_file, output_h5path = split_h5uri(xrf_results_uri)
    # Validate results
    with h5py.File(output_file, mode="r") as h5file:
        result_group = h5file[output_h5path]
        nparams = 12
        nobservations = 1021

        # Fit results
        if output_handler == "pymca":
            # includes *_error softlinks
            assert len(result_group["parameters"]) == 2 * nparams
        else:
            assert len(result_group["parameters"]) == nparams
        assert len(result_group["uncertainties"]) == nparams
        for name, values in parameters.items():
            _check_param_dataset(values, name, result_group)

        # Diagnostics
        if fast:
            assert set(result_group["diagnostics"]) == {
                "nFreeParameters",
                "nObservations",
            }
        else:
            assert set(result_group["diagnostics"]) == {
                "chisq",
                "nFreeParameters",
                "nObservations",
            }
        numpy.testing.assert_array_equal(
            result_group["diagnostics/nFreeParameters"][()], nparams
        )
        numpy.testing.assert_array_equal(
            result_group["diagnostics/nObservations"][()], nobservations
        )

        if fast:
            if output_handler == "pymca":
                # + channels and energy
                assert len(result_group["derivatives"]) == nparams + 2
            else:
                # + energy
                assert len(result_group["derivatives"]) == nparams + 1

        # Fit
        if output_handler == "pymca":
            expected = {
                "data",
                "model",
                "residuals",
                "energy",
                "channels",
                "dim0",
                "dim1",
            }
        else:
            expected = {"data", "model", "residuals", "energy"}
        assert set(result_group["fit"]) == expected

        spectra2 = result_group["fit/data"][()]
        if output_handler == "pymca":
            numpy.testing.assert_allclose(spectra, spectra2, atol=1e-10)
        else:
            numpy.testing.assert_array_equal(spectra, spectra2)
        model = result_group["fit/model"][()]

        residuals = result_group["fit/residuals"][()]
        residuals2 = spectra - model
        mask = ~numpy.isnan(model)
        if output_handler == "pymca":
            if not fast:
                residuals2 = -residuals2
            numpy.testing.assert_allclose(residuals[mask], residuals2[mask], atol=1e-4)
        else:
            numpy.testing.assert_allclose(residuals[mask], residuals2[mask])


def _check_param_dataset(expected_counts, dset_name, result_group):
    fit_counts = result_group[f"parameters/{dset_name}"][()]
    if expected_counts.size < 10:
        # TODO: does not always work. Weights are disabled but even when they are enabled, it does not work.
        fit_errors = 3 * result_group[f"uncertainties/{dset_name}"][()]
        diff = numpy.abs(fit_counts - expected_counts)
        assert (diff < fit_errors).all()
    diff = numpy.abs(numpy.diff(fit_counts) - 50)
    assert (diff < 5).all()
