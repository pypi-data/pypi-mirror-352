from typing import Sequence, Tuple

import numpy
from sklearn.neighbors import NearestNeighbors


def expanded_grid_coordinates(grid_axes: Sequence[numpy.ndarray]) -> numpy.ndarray:
    """
    Expand grid axes to coordinates of grid nodes.

    :param grid_axes: `nDim` arrays with shape `(N0,)`, `(N1,)`, ...
    :returns: shape `(N0*N1*... , Ndim)`
    """
    grid_coords = numpy.meshgrid(*grid_axes, indexing="ij")
    return numpy.vstack([g.ravel() for g in grid_coords]).T


def closest_point(
    coordinates1: numpy.ndarray, coordinates2: numpy.ndarray
) -> Tuple[numpy.ndarray, numpy.ndarray]:
    """
    Find the closest points in `coordinates1` for each point in `coordinates2`.

    :param coordinates1: Coordinates with shape `(N1, Ndim)`
    :param coordinates2: Coordinates with shape `(N2, Ndim)`
    :returns: A tuple containing:
              - indices of the closest points in `coordinates2` for each point in `coordinates1` with shape `(N1,)`
              - distances to the closest points with shape `(N1,)`
    """
    nbrs = NearestNeighbors(n_neighbors=1, algorithm="kd_tree")
    nbrs.fit(coordinates2)
    distances, indices = nbrs.kneighbors(coordinates1)
    return indices.flatten(), distances.flatten()
