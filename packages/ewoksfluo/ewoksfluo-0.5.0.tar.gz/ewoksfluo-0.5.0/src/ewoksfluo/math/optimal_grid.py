import logging
from typing import Sequence, List, Optional, Tuple

import numpy
from scipy.optimize import minimize

from . import grid_utils
from . import rounding

logger = logging.getLogger(__name__)


def optimal_grid_axes(
    scatter_coordinates: Sequence[numpy.ndarray],
    fix_resolution: bool = True,
    fix_limits: bool = True,
    resolution: Optional[Sequence[float]] = None,
) -> List[numpy.ndarray]:
    """
    :param scatter_coordinates: shape `(Nscatter, Ndim)`
    :param fixed_resolution:
    :param fixed_limits:
    :param resolution:
    :returns: `Ndim` 1D arrays with length `N0`, `N1`, ...
    """
    num_data_points, Ndim = scatter_coordinates.shape

    if resolution is None:
        resolution = [resolution] * Ndim

    # Find optimal grid analytically based and estimate
    # the optimal resolution when not provided.
    start_stop_size = (
        _estimate_start_stop_size(scatter_coordinates[:, i], resolution=resolutioni)
        for i, resolutioni in enumerate(resolution)
    )
    initial_start_limits, initial_stop_limits, initial_grid_shape = zip(
        *start_stop_size
    )

    logger.debug("Initial grid shape: %s", initial_grid_shape)

    initial_start_limits = numpy.array(initial_start_limits)
    initial_stop_limits = numpy.array(initial_stop_limits)
    initial_data_range = initial_stop_limits - initial_start_limits

    min_limits = numpy.min(scatter_coordinates, axis=0)
    max_limits = numpy.max(scatter_coordinates, axis=0)
    min_limits = numpy.array(min_limits)
    max_limits = numpy.array(max_limits)
    max_data_range = max_limits - min_limits

    # Compile parameters of optimization
    initial_guess = []
    bounds = []
    fixed_limits = []
    fixed_resolution = []

    initial_resolution = initial_data_range / (numpy.array(initial_grid_shape) - 1)
    logger.info("Initial resolution: %s", tuple(initial_resolution))

    if fix_resolution:
        fixed_resolution.extend(initial_resolution)
    else:
        initial_guess.extend(initial_resolution)
        resolution_bounds = zip(max_data_range / (num_data_points - 1), max_data_range)
        bounds.extend(resolution_bounds)

    if fix_limits:
        fixed_limits.extend(initial_start_limits)
        fixed_limits.extend(initial_stop_limits)
    else:
        initial_guess.extend(initial_start_limits)
        initial_guess.extend(initial_stop_limits)
        start_limit_bounts = zip(min_limits, max_limits)
        bounds.extend(start_limit_bounts)
        stop_limit_bounts = zip(max_limits, max_limits)
        bounds.extend(stop_limit_bounts)

    if fixed_limits:
        fixed_limits = numpy.asarray(fixed_limits)
    else:
        fixed_limits = None
    if fixed_resolution:
        fixed_resolution = numpy.asarray(fixed_resolution)
    else:
        fixed_resolution = None

    # Do optimization unless all parameters are fixed
    if initial_guess:
        logger.info("Grid optimization applied")
        initial_guess = numpy.asarray(initial_guess)
        result = minimize(
            _scatter_grid_distance_measure,
            initial_guess,
            args=(scatter_coordinates, fixed_resolution, fixed_limits),
            method="Nelder-Mead",
            bounds=bounds,
        )
        fit_parameters = result.x
    else:
        logger.info("No grid optimization applied")
        fit_parameters = None

    grid_axes = _fit_parameters_to_grid_axes(
        Ndim,
        fit_parameters=fit_parameters,
        fixed_resolution=fixed_resolution,
        fixed_limits=fixed_limits,
    )

    final_grid_shape = tuple(len(arr) for arr in grid_axes)
    final_resolution = tuple(
        arr[1] - arr[0] if arr.size else numpy.nan for arr in grid_axes
    )
    logger.info("Final grid shape: %s", final_grid_shape)
    logger.info("Final resolution: %s", final_resolution)
    return grid_axes


def _estimate_start_stop_size(
    array: numpy.ndarray, resolution: Optional[float] = None
) -> Tuple[float, float, int]:
    """
    :params array: 1D array
    :param resolution: bin width
    :returns: start value, stop value, number of points
    """
    if len(array) == 0:
        return numpy.nan, numpy.nan, 0
    if len(array) == 1:
        return array[0], array[0], 1

    array = numpy.sort(array)

    if not resolution:
        distances = numpy.diff(array)

        min_distance = numpy.min(distances)
        mid_distance = min_distance + (numpy.max(distances) - min_distance) / 2

        mask = distances > mid_distance
        if mask.any():
            resolution = numpy.median(distances[mask])
        else:
            resolution = numpy.median(distances)
        resolution = rounding.round_to_significant(resolution)

    start, stop, nbins = rounding.round_range(array[0], array[-1], resolution)
    if nbins == 0:
        return start, stop, 0
    npoints = nbins + 1
    return start, stop, npoints


def _scatter_grid_distance_measure(
    fit_parameters: numpy.ndarray,
    scatter_coordinates: numpy.ndarray,
    fixed_resolution: Optional[numpy.ndarray] = None,
    fixed_limits: Optional[numpy.ndarray] = None,
) -> float:
    """Distance measure between scattered points and a grid with a resolution and
    start and stop limits that are either refined or fixed.

    :param fit_parameters:
    :param scatter_coordinates: `(Nscatter, Ndim)`
    :param fixed_resolution:
    :param fixed_limits:
    :returns: sum of closest distances of grid nodes with scatter_coordinates
    """
    _, Ndim = scatter_coordinates.shape

    grid_axes = _fit_parameters_to_grid_axes(
        Ndim,
        fit_parameters=fit_parameters,
        fixed_limits=fixed_limits,
        fixed_resolution=fixed_resolution,
    )  # [(N0,), (N1,), ...]

    expanded_grid_coordinates = grid_utils.expanded_grid_coordinates(
        grid_axes
    )  # (N0*N1*... , Ndim)

    # Closest grid point for each scatter point
    _, scatter_distances = grid_utils.closest_point(
        expanded_grid_coordinates, scatter_coordinates
    )
    scatter_coverage = numpy.sum(scatter_distances)

    # Closest scatter point for each grid point
    _, grid_distances = grid_utils.closest_point(
        scatter_coordinates, expanded_grid_coordinates
    )
    grid_coverage = numpy.sum(grid_distances)

    return scatter_coverage + grid_coverage


def _fit_parameters_to_grid_axes(
    Ndim: int,
    fit_parameters: Optional[numpy.ndarray] = None,
    fixed_resolution: Optional[numpy.ndarray] = None,
    fixed_limits: Optional[numpy.ndarray] = None,
) -> List[numpy.ndarray]:
    """
    :param fit_parameters:
    :param fixed_resolution:
    :param fixed_limits:
    :returns: `Ndim` arrays with shape `(N0,)`, `(N1,)`, ...
    """
    fix_resolution = fixed_resolution is not None
    fix_limits = fixed_limits is not None

    params_offset = 0

    if fix_resolution:
        grid_resolution = fixed_resolution
    else:
        grid_resolution = fit_parameters[params_offset : params_offset + Ndim]
        params_offset += Ndim

    if fix_limits:
        grid_start_limits = fixed_limits[:Ndim]
        grid_stop_limits = fixed_limits[Ndim:]
    else:
        grid_start_limits = fit_parameters[params_offset : params_offset + Ndim]
        params_offset += Ndim
        grid_stop_limits = fit_parameters[params_offset : params_offset + Ndim]
        params_offset += Ndim

    _linspace = _linspace_fixed_stop

    grid_axes = list()
    for i, (start, stop, step) in enumerate(
        zip(grid_start_limits, grid_stop_limits, grid_resolution)
    ):
        if step == 0 or not numpy.isfinite(start) or not numpy.isfinite(stop):
            raise ValueError(f"The grid along dimension {i} cannot be determined")
        grid_axes.append(_linspace(start, stop, step))
    return grid_axes


def _linspace_fixed_step(start: float, stop: float, step: float) -> numpy.ndarray:
    return numpy.arange(start, stop, step)


def _linspace_fixed_stop(start: float, stop: float, step: float) -> numpy.ndarray:
    n = max(int((stop - start) / step + 1.5), 1)
    return numpy.linspace(start, stop, n)
