import numpy
import pytest

from ..math.regular_grid import ScatterDataInterpolator


@pytest.mark.parametrize("ndatadim", [0, 1, 2])
def test_regular_regridding(ndatadim):
    data_shape = tuple(range(10, 10 + ndatadim))

    # Plane: z = ax + by + c
    a, b, c = 3, 2, 1

    state = numpy.random.RandomState(42)
    N_points = 100
    x = state.uniform(-10, 10, N_points)
    y = state.uniform(-10, 10, N_points)
    z = a * x + b * y + c
    z = _add_data_dimensions(z, data_shape)

    interpolator = ScatterDataInterpolator(
        [x, y], ["x", "y"], ["um", "um"], method="linear"
    )
    interpolated_z = interpolator.regrid(z)

    expected_z = (
        a * interpolator.expanded_grid_coordinates[:, 0]
        + b * interpolator.expanded_grid_coordinates[:, 1]
        + c
    )
    expected_z = _add_data_dimensions(expected_z, data_shape)
    expected_z = expected_z.reshape(interpolated_z.shape)

    assert numpy.nanmax(numpy.abs(interpolated_z - expected_z)) < 1e-9


def _add_data_dimensions(array: numpy.ndarray, data_shape: tuple) -> numpy.ndarray:
    reshaped_array = array[(...,) + (numpy.newaxis,) * len(data_shape)]
    return numpy.tile(reshaped_array, data_shape)
