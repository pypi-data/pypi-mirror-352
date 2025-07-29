from typing import Generator, Tuple

import numpy
import psutil

from ..math import grid_utils


def test_closest_point():
    coordinates1 = numpy.random.rand(1000, 2)
    coordinates2 = numpy.random.rand(1001, 2)

    indices1, distances1 = grid_utils.closest_point(coordinates1, coordinates2)
    indices2, distances2 = _closest_point_brute_force(coordinates1, coordinates2)

    assert len(indices1) == len(coordinates1)
    assert len(indices2) == len(coordinates1)
    assert len(distances1) == len(coordinates1)
    assert len(distances2) == len(coordinates1)

    assert (indices1 == indices2).all()
    assert (distances1 == distances2).all()


def _closest_point_brute_force(
    coordinates1: numpy.ndarray,
    coordinates2: numpy.ndarray,
    chunk_memory_fraction: float = 0.10,
) -> Tuple[numpy.ndarray, numpy.ndarray]:
    """
    Find the closest point in `coordinates2` for each point in `coordinates1`.

    :param coordinates1: Coordinates with shape `(N1, Ndim)`
    :param coordinates2: Coordinates with shape `(N2, Ndim)`
    :param chunk_memory_fraction: Fraction of available memory to use for each batch
    :returns: A tuple containing:
            - indices of the closest points in `coordinates2` for each point in `coordinates1` with shape `(N1,)`
            - distances to the closest points with shape `(N1,)`
    """
    N1, Ndim1 = coordinates1.shape
    _, Ndim2 = coordinates2.shape
    assert Ndim1 == Ndim2

    closest_indices = numpy.empty(N1, dtype=int)
    closest_distances = numpy.empty(N1, dtype=float)

    for start, stop, differences in _iter_coordinate_differences(
        coordinates1, coordinates2, chunk_memory_fraction
    ):
        # differences: (Nchunk1i, N2, Ndim)
        distances = numpy.linalg.norm(differences, axis=2)  # (Nchunk1i, N2)
        chunk_indices = numpy.argmin(distances, axis=1)  # (Nchunk1i,)
        closest_indices[start:stop] = chunk_indices
        closest_distances[start:stop] = distances[
            list(range(len(chunk_indices))), chunk_indices
        ]

    return closest_indices, closest_distances


def _iter_coordinate_differences(
    coordinates1: numpy.ndarray,
    coordinates2: numpy.ndarray,
    chunk_memory_fraction: float = 0.10,
) -> Generator[Tuple[int, int, numpy.ndarray], None, None]:
    """
    Iterator over the difference between two sets of coordinates in chunks of the second set.

    :param coordinates1: coordinates with shape `(N1, Ndim)`
    :param coordinates2: coordinates with shape `(N2, Ndim)`
    :param chunk_memory_fraction: yielded chunks take a fraction of the currently
                                available memory at the moment of yielding
    :yields: difference between coordinates with shape `(Nchunk1i, N2, Ndim)`
            which totals to `(N1, N2, Ndim)` when concatenating all chunks
    """
    N1, Ndim1 = coordinates1.shape
    _, Ndim2 = coordinates2.shape
    assert Ndim1 == Ndim2

    coordinates2_size = coordinates2.size * coordinates2.itemsize
    coordinates2 = coordinates2[numpy.newaxis, ...]  # (1, N2, Ndim)

    start = 0
    while start < N1:
        chunk_memory = int(psutil.virtual_memory().available * chunk_memory_fraction)
        Nchunk1i = max(1, int(chunk_memory / coordinates2_size))

        stop = min(start + Nchunk1i, N1)
        chunk1 = coordinates1[start:stop, numpy.newaxis, :]  # (Nchunk1i, 1, Ndim)

        differences = numpy.abs(coordinates2 - chunk1)  # (Nchunk1i, N2, Ndim)

        yield start, stop, differences

        start += Nchunk1i
