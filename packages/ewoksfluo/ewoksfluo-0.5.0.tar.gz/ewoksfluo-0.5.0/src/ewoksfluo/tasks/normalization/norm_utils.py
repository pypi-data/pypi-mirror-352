from typing import Dict, Sequence, Tuple, Any, Optional

import h5py
import numpy

from .. import xrf_results
from ...io.hdf5 import ReadHdf5File
from ...math import pad
from ..math import eval_hdf5_expression
from ..math import format_expression_template


DEFAULTS = {
    "counter_normalization_template": "np.mean(<instrument/{}/data>)/<instrument/{}/data>",
    "detector_normalization_template": "1./<instrument/{}/live_time>",
}


def normalization_template(
    expression: Optional[str],
    counter_normalization_template: Optional[str],
    counter_name: Optional[str],
    detector_normalization_template: Optional[str],
    detector_name: Optional[str],
) -> str:

    factors = []

    if expression:
        try:
            expression.format()
        except IndexError:
            pass
        else:
            factors.append(expression)

    if detector_name:
        if not detector_normalization_template:
            detector_normalization_template = DEFAULTS[
                "detector_normalization_template"
            ]
        factors.append(
            format_expression_template(detector_normalization_template, detector_name)
        )

    if counter_name:
        if not counter_normalization_template:
            counter_normalization_template = DEFAULTS["counter_normalization_template"]
        factors.append(
            format_expression_template(counter_normalization_template, counter_name)
        )

    if not factors:
        raise ValueError(
            "specify at least one of these: 'expression_template', 'counter_name' or 'detector_name'"
        )

    return "*".join(factors)


def normalization_coefficient(
    weight_uri_root: str, normalization_expression: str
) -> numpy.ndarray:
    """
    :param weight_uri_root: HDF5 root group under which the normalization datasets can be found.
    :param normalization_expression: Arithmetic expression to calculated the normalization coefficient.
    """
    return eval_hdf5_expression(weight_uri_root, normalization_expression)


def normalization_coefficient_stack(
    weight_uri_roots: Sequence[str], normalization_expression: str
) -> numpy.ndarray:
    """
    :param weight_uri_roots: HDF5 root group under which the normalization datasets can be found.
    :param normalization_expression: Arithmetic expression to calculated the normalization coefficient.
    """
    coefficient = [
        eval_hdf5_expression(weight_uri_root, normalization_expression)
        for weight_uri_root in weight_uri_roots
    ]
    return numpy.stack(coefficient, axis=0)


def save_normalized_xrf_results(
    xrf_results_uri: str,
    coefficient: numpy.ndarray,
    output_root_uri: str,
    process_config: Dict[str, Any],
) -> str:
    """
    :param xrf_results_uri: HDF5 group that contains the "parameters", "uncertainties" and "massfractions" groups.
    :param coefficient: Coefficient with which to normalize the data.
    :param output_root_uri: Root HDF5 URL under which to save the results as NXprocess
    :returns: URI to normalized fit result group
    """
    parameters, uncertainties, massfractions = compute_normalized_xrf_results(
        xrf_results_uri, coefficient
    )
    return xrf_results.save_xrf_results(
        output_root_uri,
        "norm",
        process_config,
        parameters,
        uncertainties,
        massfractions,
    )


def compute_normalized_xrf_results(
    xrf_results_uri: str, coefficient: numpy.ndarray
) -> Tuple[
    Dict[str, numpy.ndarray], Dict[str, numpy.ndarray], Dict[str, numpy.ndarray]
]:
    r"""Compute the normalized peak areas, associated uncertainties and mass fractions.

    For elemental peak areas

    .. math::

        A(\mathrm{Fe}) = C \cdot A(\mathrm{Fe})

    For their uncertainties

    .. math::

        \sigma_{A}(\mathrm{Fe}) = C \cdot \sigma_{A}(\mathrm{Fe})  }

    :param xrf_results_uri: HDF5 group that contains the "parameters", "uncertainties" and "massfractions" groups.
    :param coefficient: Coefficient with which to normalize the data.
    :returns: normalized peak areas, associated uncertainties, normalized weight fractions
    """
    normalized_parameters = {}
    normalized_uncertainties = {}
    normalized_massfractions = {}

    fit_filename, fit_h5path = xrf_results_uri.split("::")

    with ReadHdf5File(fit_filename) as h5file:
        xrf_results_group = h5file[fit_h5path]
        assert isinstance(xrf_results_group, h5py.Group)

        massfrac_group = xrf_results_group.get("massfractions", dict())

        # Peak areas and mass fractions
        param_group = xrf_results_group["parameters"]
        assert isinstance(param_group, h5py.Group)
        for dset_name, dset in param_group.items():
            if not xrf_results.is_peak_area(dset):
                continue

            wparam_value = _normalize_dataset(dset[()], coefficient)
            normalized_parameters[dset_name] = wparam_value

            if dset_name not in massfrac_group:
                continue

            wmassfrac_value = _normalize_dataset(
                massfrac_group[dset_name][()], coefficient
            )
            normalized_massfractions[dset_name] = wmassfrac_value

        # Propagate error on peak areas
        uncertainties_group = xrf_results_group["uncertainties"]
        assert isinstance(uncertainties_group, h5py.Group)
        for dset_name, dset in uncertainties_group.items():
            if not isinstance(dset, h5py.Dataset):
                continue
            wsigma_value = _normalize_dataset(dset, coefficient)
            normalized_uncertainties[dset_name] = wsigma_value

    return normalized_parameters, normalized_uncertainties, normalized_massfractions


def _normalize_dataset(
    dset: h5py.Dataset, coefficients: numpy.ndarray
) -> numpy.ndarray:
    ndset = len(dset)
    ncoeff = len(coefficients)
    if ndset == ncoeff:
        return dset[()] * coefficients
    if ndset < ncoeff:
        return pad.pad_array(dset[()], ncoeff) * coefficients
    return dset[()] + pad.pad_array(coefficients, ndset)
