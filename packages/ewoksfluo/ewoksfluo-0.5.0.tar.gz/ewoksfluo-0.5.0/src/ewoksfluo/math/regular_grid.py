import h5py
from typing import Sequence, Tuple, List, Optional, Union

import numpy
from scipy.interpolate import griddata

from . import pad
from . import grid_utils
from ..units import unit_registry
from .optimal_grid import optimal_grid_axes


class ScatterDataInterpolator:
    """Interpolates scatter data on a regular grid."""

    def __init__(
        self,
        scatter_coordinates: Sequence[numpy.ndarray],
        scatter_coordinate_names: Sequence[str],
        scatter_coordinate_units: Sequence[Optional[str]],
        method: Optional[str] = None,
        fill_value=None,
        fix_resolution: bool = True,
        fix_limits: bool = True,
        resolution: Optional[
            Union[Sequence[float], Sequence[Tuple[float, str]]]
        ] = None,
        outside_resolution_fraction: float = 2.1,
    ):
        """
        :param scatter_coordinates: independent variables with shape `(Ndim, Nscatter)`.
        :param scatter_coordinate_names: independent variable names with shape `(Ndim,)`
        :param scatter_coordinate_units: independent variable units with shape `(Ndim,)`
        :param method: interpolation method.
        :param fill_value: value used for extrapolation.
        :param fix_resolution: fix the resolution.
        :param fix_limits: fix the limits.
        :param resolution: grid spacing in each dimension.
        :param outside_resolution_fraction: a grid point is concidered to be outside the space spanned by the scatter points
                                 when the closest scatter point is farther away than a fraction of the smallest resolution
                                 across all dimensions.
        """
        if method is None:
            method = "nearest"
        self._method = method
        if fill_value is None:
            fill_value = numpy.nan
        self._fill_value = fill_value
        self._axes_names = scatter_coordinate_names

        # Units
        self._units = scatter_coordinate_units[0]

        ureg = unit_registry()

        if len(set(scatter_coordinate_units)) > 1:
            # All dimensions will have the same units (self._units)
            assert not any(units is None for units in scatter_coordinate_units)

            if self._units:
                scatter_coordinates = [
                    (v * ureg.parse_units(u)).to(self._units).magnitude
                    for v, u in zip(scatter_coordinates, scatter_coordinate_units)
                ]

        if resolution and self._units:
            # Resolution must have the same units as scatter_coordinates
            resolution_correct_units = list()
            for value in resolution:
                if isinstance(value, tuple):
                    v, u = value
                    value = (v * ureg.parse_units(u)).to(self._units).magnitude
                    resolution_correct_units.append(value)
                else:
                    resolution_correct_units.append(value)
            resolution = resolution_correct_units

        # Scatter coordinates
        assert len(scatter_coordinate_names) == len(scatter_coordinates)
        assert len(scatter_coordinate_units) == len(scatter_coordinates)

        nscatter = set()
        for i, coordi in enumerate(scatter_coordinates):
            if coordi.ndim != 1:
                raise ValueError(f"Coordinate {i} must be provided as a 1D array")
            if coordi.size == 0:
                raise ValueError(f"Coordinate {i} is empty")
            nscatter.add(len(coordi))

        self._nscatter = min(nscatter)

        if len(nscatter) > 1:
            scatter_coordinates = [
                coordi[: self._nscatter] for coordi in scatter_coordinates
            ]

        self._scatter_coordinates = numpy.vstack(
            scatter_coordinates
        ).T  # (Nscatter, Ndim)

        # Grid coordinates
        self._grid_axes = optimal_grid_axes(
            self._scatter_coordinates,
            fix_resolution=fix_resolution,
            fix_limits=fix_limits,
            resolution=resolution,
        )  # [(N0,), (N1,), ...]

        self._grid_shape = tuple(len(arr) for arr in self._grid_axes)  # (N0, N1, ...)
        self._expanded_grid_coordinates = grid_utils.expanded_grid_coordinates(
            self._grid_axes
        )  # (N0*N1*..., Ndim)

        # Difference between scatter and grid coordinates
        self._closest_scatter_index, self._closest_scatter_distance = (
            grid_utils.closest_point(
                self._expanded_grid_coordinates, self._scatter_coordinates
            )
        )
        self._closest_grid_index, self._closest_grid_distance = (
            grid_utils.closest_point(
                self._scatter_coordinates, self._expanded_grid_coordinates
            )
        )
        distance_max = min(
            abs(axis[1] - axis[0]) * outside_resolution_fraction
            for axis in self._grid_axes
        )
        self._grid_coordinates_outside = self._closest_scatter_distance > distance_max

        # self._plot_coordinates()

    @property
    def scan_size(self) -> int:
        return self._nscatter

    @property
    def grid_size(self) -> int:
        return self._expanded_grid_coordinates[0]

    @property
    def grid_shape(self) -> Tuple[int]:
        """
        :returns: tuple `(N0, N1, ...)` with length: `Ndim`
        """
        return self._grid_shape

    @property
    def grid_ndim(self) -> int:
        return len(self._grid_shape)

    @property
    def axes_names(self) -> List[str]:
        return self._axes_names

    @property
    def units(self) -> Optional[str]:
        return self._units

    @property
    def grid_axes(self) -> List[numpy.ndarray]:
        """
        :returns: `Ndim` arrays with shapes `[(N0,), (N1,), ...]`
        """
        return self._grid_axes

    @property
    def expanded_grid_coordinates(self) -> numpy.ndarray:
        """
        :returns: shape `(N0*N1*..., Ndim)`
        """
        return self._expanded_grid_coordinates

    @property
    def grid_coordinates_outside(self) -> numpy.ndarray:
        """Mask for grid coordinates with shape `(N0*N1*..., )` that are outside the scatter cloud.

        :returns: shape `(N0*N1*...,)`
        """
        return self._grid_coordinates_outside

    @property
    def scatter_coordinates(self) -> numpy.ndarray:
        """
        :returns: shape `(Nscatter, Ndim)`
        """
        return self._scatter_coordinates

    def regrid(self, scatter_data: numpy.ndarray) -> numpy.ndarray:
        """
        :param scatter_data: flat list of data values `(Nscatter, M0, M1, ...)` with
                             `(M0, M1, ...)` the shape of one detector data value
        :returns: regridded data values `(N0, N1, ..., M0, M1, ...)`
        """
        if scatter_data.ndim == 0:
            raise ValueError("Data cannot be a scalar")
        if scatter_data.size == 0:
            raise ValueError("Data is empty")

        ndata = len(scatter_data)
        if ndata > self._nscatter:
            scatter_data = scatter_data[: self._nscatter]
        elif ndata < self._nscatter:
            scatter_data = pad.pad_array(scatter_data, self._nscatter)

        if scatter_data.ndim == 1:
            return self._interpolate_0d_detector(scatter_data)

        return self._interpolate_nd_detector(scatter_data)

    def _interpolate_0d_detector(self, scatter_data: numpy.ndarray) -> numpy.ndarray:
        interpolated_data = _interpolate(
            scatter_coordinates=self._scatter_coordinates,
            scatter_data=scatter_data,
            interp_coordinates=self._expanded_grid_coordinates,
            interp_coordinates_outside=self._grid_coordinates_outside,
            method=self._method,
            fill_value=self._fill_value,
        )
        return interpolated_data.reshape(*self._grid_shape)

    def _interpolate_nd_detector(self, scatter_data: numpy.ndarray) -> numpy.ndarray:
        nscatter = scatter_data.shape[0]
        data_shape = scatter_data.shape[1:]
        scatter_data_flat_detector = scatter_data.reshape((nscatter, -1))
        nscatter, data_size = scatter_data_flat_detector.shape

        interpolated_data = numpy.array(
            [
                _interpolate(
                    scatter_coordinates=self._scatter_coordinates,
                    scatter_data=scatter_data_flat_detector[:, i],
                    interp_coordinates=self._expanded_grid_coordinates,
                    interp_coordinates_outside=self._grid_coordinates_outside,
                    method=self._method,
                    fill_value=self._fill_value,
                )
                for i in range(data_size)
            ]
        ).T

        return interpolated_data.reshape(*self._grid_shape, *data_shape)

    def _plot_coordinates(self) -> None:
        import matplotlib.pyplot as plt

        outside = self.grid_coordinates_outside
        inside = ~outside

        plt.plot(
            self.scatter_coordinates[:, 1],
            self.scatter_coordinates[:, 0],
            ".",
            color="blue",
        )
        plt.plot(
            self.expanded_grid_coordinates[inside, 1],
            self.expanded_grid_coordinates[inside, 0],
            "o",
            mfc="none",
            color="green",
        )
        plt.plot(
            self.expanded_grid_coordinates[outside, 1],
            self.expanded_grid_coordinates[outside, 0],
            "o",
            mfc="none",
            color="red",
        )
        plt.xlabel(self.axes_names[1])
        plt.ylabel(self.axes_names[0])
        plt.axis("equal")
        plt.show()

    def save_coordinates_as_nxdata(self, parent: h5py.Group) -> None:
        nxcollection = parent.create_group("coordinates")
        nxcollection.attrs["NX_class"] = "NXcollection"

        nxdata = nxcollection.create_group("scatter_coordinates")
        nxdata.attrs["NX_class"] = "NXdata"
        nxdata["title"] = "Scatter coordinate indices"
        self._save_nxdata_scatter_axes(nxdata)
        signal = numpy.arange(len(self.scatter_coordinates))
        self._save_nxdata_signal(nxdata, "indices", signal, units=False)

        nxdata = nxcollection.create_group("grid_coordinates")
        nxdata.attrs["NX_class"] = "NXdata"
        nxdata["title"] = "Grid nodes that have data"
        self._save_nxdata_grid_axes(nxdata)
        signal = ~self.grid_coordinates_outside
        self._save_nxdata_signal(nxdata, "has_data", signal, units=False)

        nxdata = nxcollection.create_group("coordinates")
        nxdata.attrs["NX_class"] = "NXdata"
        nxdata["title"] = "Grid nodes (0 or 1) and Scatter coordinates (2)"
        self._save_nxdata_scatter_and_grid_axes(nxdata)
        signal = numpy.concatenate(
            (
                numpy.full((len(self.scatter_coordinates),), 2),
                ~self.grid_coordinates_outside,
            )
        )
        self._save_nxdata_signal(nxdata, "coordinate_type", signal, units=False)

        nxdata = nxcollection.create_group("closest_grid_distance")
        nxdata.attrs["NX_class"] = "NXdata"
        nxdata["title"] = "Closest grid node distance for every scatter coordinate"
        self._save_nxdata_scatter_axes(nxdata)
        signal = self._closest_grid_distance
        self._save_nxdata_signal(nxdata, "distance", signal, units=True)

        nxdata = nxcollection.create_group("closest_scatter_distance")
        nxdata.attrs["NX_class"] = "NXdata"
        nxdata["title"] = "Closest scatter coordinate distance for every grid node"
        self._save_nxdata_grid_axes(nxdata)
        signal = self._closest_scatter_distance.copy()
        signal[self._grid_coordinates_outside] = numpy.nan
        self._save_nxdata_signal(nxdata, "distance", signal, units=True)

    def _save_nxdata_signal(
        self, nxdata: h5py.Group, name: str, data: numpy.ndarray, units: bool = True
    ) -> None:
        nxdata.attrs["signal"] = name
        dset = nxdata.create_dataset(name=name, data=data)
        if units:
            self._save_nxdata_units(dset, name)

    def _save_nxdata_scatter_axes(self, nxdata: h5py.Group) -> None:
        nxdata.attrs["axes"] = self.axes_names[::-1]
        for name, values in zip(self.axes_names, self.scatter_coordinates.T):
            dset = nxdata.create_dataset(name=name, data=values)
            self._save_nxdata_units(dset, name)

    def _save_nxdata_grid_axes(self, nxdata: h5py.Group) -> None:
        nxdata.attrs["axes"] = self.axes_names[::-1]
        for name, values in zip(self.axes_names, self.expanded_grid_coordinates.T):
            dset = nxdata.create_dataset(name=name, data=values)
            self._save_nxdata_units(dset, name)

    def _save_nxdata_scatter_and_grid_axes(self, nxdata: h5py.Group) -> None:
        nxdata.attrs["axes"] = self.axes_names[::-1]
        for name, scatter_values, grid_values in zip(
            self.axes_names,
            self.scatter_coordinates.T,
            self.expanded_grid_coordinates.T,
        ):
            values = numpy.concatenate((scatter_values, grid_values))
            dset = nxdata.create_dataset(name=name, data=values)
            self._save_nxdata_units(dset, name)

    def _save_nxdata_units(self, dset: h5py.Dataset, name: str) -> None:
        if self.units is not None:
            dset.attrs["units"] = self.units
            dset.attrs["long_name"] = f"{name} ({self.units})"


def _interpolate(
    scatter_coordinates: numpy.ndarray,
    scatter_data: numpy.ndarray,
    interp_coordinates: numpy.ndarray,
    interp_coordinates_outside: numpy.ndarray,
    method: str,
    fill_value: float,
) -> numpy.ndarray:
    """
    :param scatter_coordinates: scatter coordinates with shape `(Nscatter, Ndim)`
    :param scatter_data: flat list of scatter data values `(Nscatter,)`
    :param interp_coordinates: interpolate coordinates with shape `(Ninterp, Ndim)`
    :param interp_coordinates_outside: boolean array with shape `(Ninterp,)`
    :param method:
    :param fill_value:
    :returns: interpolated data values `(Ninterp,)`
    """
    interp_data = griddata(
        scatter_coordinates,
        scatter_data,
        interp_coordinates,
        method=method,
        fill_value=fill_value,
    )
    if numpy.isnan(fill_value) and numpy.issubdtype(interp_data.dtype, numpy.integer):
        fill_value = 0
    interp_data[interp_coordinates_outside] = fill_value
    return interp_data
