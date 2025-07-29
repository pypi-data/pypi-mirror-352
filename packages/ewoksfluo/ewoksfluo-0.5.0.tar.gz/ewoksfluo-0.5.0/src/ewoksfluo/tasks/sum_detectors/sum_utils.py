import itertools
from typing import Dict, Sequence, Tuple, Iterator, Generator, Any

import h5py
import numpy

from .. import xrf_results
from ...io.hdf5 import ReadHdf5File
from ..math import eval_hdf5_expression


def detector_weight_iterator(
    weight_uri_root: str, weight_expressions: Sequence[str]
) -> Generator[numpy.ndarray, None, None]:
    """
    :param weight_uri_root: HDF5 root group under which the detector weight datasets can be found.
    :param weight_expressions: Arithmetic expression for each detector to calculated the weight for addition from HDF5 datasets.
    """
    for weight_expression in weight_expressions:
        yield eval_hdf5_expression(weight_uri_root, weight_expression)


def detector_weight_iterator_stack(
    weight_uri_roots: Sequence[str], weight_expressions: Sequence[str]
) -> Generator[numpy.ndarray, None, None]:
    """
    :param weight_uri_roots: HDF5 root group under which the detector weight datasets can be found.
    :param weight_expressions: Arithmetic expression for each detector to calculated the weight for addition from HDF5 datasets.
    """
    for weight_expression in weight_expressions:
        detector_weight = [
            eval_hdf5_expression(weight_uri_root, weight_expression)
            for weight_uri_root in weight_uri_roots
        ]
        yield numpy.stack(detector_weight, axis=0)


def save_summed_xrf_results(
    xrf_results_uris: Sequence[str],
    detector_weights: Iterator[numpy.ndarray],
    output_root_uri: str,
    process_config: Dict[str, Any],
) -> str:
    """
    :param xrf_results_uris: HDF5 group for each detector that contains the "parameters", "uncertainties" and "massfractions" groups.
    :param detector_weights: Weights for each detector.
    :param output_root_uri: Root HDF5 URL under which to save the results as NXprocess
    :returns: URI to summed fit result group
    """
    parameters, uncertainties, massfractions = compute_summed_xrf_results(
        xrf_results_uris, detector_weights
    )
    return xrf_results.save_xrf_results(
        output_root_uri,
        "sum",
        process_config,
        parameters,
        uncertainties,
        massfractions,
    )


def compute_summed_xrf_results(
    xrf_results_uris: Sequence[str], detector_weights: Iterator[numpy.ndarray]
) -> Tuple[
    Dict[str, numpy.ndarray], Dict[str, numpy.ndarray], Dict[str, numpy.ndarray]
]:
    r"""Compute the weighted sum of the peak areas, associated uncertainties and mass fractions for several detectors.

    For elemental peak areas

    .. math::

        A(\mathrm{Fe}) = \sum_i{\left[ W_i A_i(\mathrm{Fe}) \right] }

    For their uncertainties

    .. math::

        \sigma_{A}(\mathrm{Fe}) = \sqrt{ \sum_i\left[ W_i^2 \sigma_{A_i}^2(\mathrm{Fe}) \right] }

    For elemental mass fractions, in addition to the detector weight we also weight for the peak area

    .. math::

        M(\mathrm{Fe}) = \sum_i{\left[ W_i M_i(\mathrm{Fe}) \frac{W_i A_i(\mathrm{Fe})}{A(\mathrm{Fe})} \right] }

    The variable :math:`W_i` is the weight for detector :math:`i` which is typically the inverse of the live time.

    :param xrf_results_uris: HDF5 group for each detector that contains the "parameters", "uncertainties" and "massfractions" groups.
    :param detector_weights: Weights for each detector.
    :returns: summed peak areas, associated uncertainties, averaged weight fractions
    """
    summed_parameters = {}
    summed_variances = {}
    averaged_massfractions = {}

    for xrf_results_uri, detector_weight in itertools.zip_longest(
        xrf_results_uris, detector_weights, fillvalue=None
    ):
        if xrf_results_uri is None or detector_weight is None:
            raise ValueError(
                "The number of arithmetic expressions but be equal to the number of detectors"
            )

        fit_filename, fit_h5path = xrf_results_uri.split("::")

        with ReadHdf5File(fit_filename) as h5file:
            xrf_results_group = h5file[fit_h5path]
            assert isinstance(xrf_results_group, h5py.Group)

            # Sum the peak areas and average mass fractions
            param_group = xrf_results_group["parameters"]
            assert isinstance(param_group, h5py.Group)
            massfrac_group = xrf_results_group.get("massfractions", dict())
            for dset_name, dset in param_group.items():
                if not xrf_results.is_peak_area(dset):
                    continue

                wparam_value = dset[()] * detector_weight
                if dset_name in summed_parameters:
                    summed_parameters[dset_name] += wparam_value
                else:
                    summed_parameters[dset_name] = wparam_value

                if dset_name not in massfrac_group:
                    continue

                wmassfrac_value = massfrac_group[dset_name][()] * detector_weight
                wmassfrac_num = wparam_value * wmassfrac_value
                if dset_name in averaged_massfractions:
                    averaged_massfractions[dset_name] += wmassfrac_num
                else:
                    averaged_massfractions[dset_name] = wmassfrac_num

            # Propagate error on peak areas
            uncertainties_group = xrf_results_group["uncertainties"]
            assert isinstance(uncertainties_group, h5py.Group)
            for dset_name, dset in uncertainties_group.items():
                if not isinstance(dset, h5py.Dataset):
                    continue
                wvar_value = dset[()] ** 2 * detector_weight**2
                if dset_name in summed_variances:
                    summed_variances[dset_name] += wvar_value
                else:
                    summed_variances[dset_name] = wvar_value

    summed_uncertainties = {k: numpy.sqrt(v) for k, v in summed_variances.items()}

    if averaged_massfractions:
        averaged_massfractions = {
            k: v / summed_parameters[k] for k, v in averaged_massfractions.items()
        }

    return summed_parameters, summed_uncertainties, averaged_massfractions
