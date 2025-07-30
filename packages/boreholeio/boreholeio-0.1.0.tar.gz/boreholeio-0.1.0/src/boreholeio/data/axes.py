"""Module for all axes from a data handling perspective."""

from __future__ import annotations

from typing import TYPE_CHECKING, Sequence, Union

import numpy as np

from boreholeio import errors

if TYPE_CHECKING:
    from boreholeio import data


class LinearAxis:
    """LinearAxis.

    Details on all Axis more generally can be found with the rest of the borehole.io documentation.

    Parameters
    ----------
        name: The relevant name for this Axis
        extents: Data extents for this Axis
        units: The units of this Axis
        period: If the axis is periodic, the relevant period.

    .. _borehole.io Documentation: https://borehole.io/spec

    """

    def __init__(
        self,
        name: str,
        extents,
        units: str | None = None,
        period: float | None = None,
    ) -> None:
        self.name = name
        self.units = units
        self.extents = extents
        self.period = period

        self.array: data.MeasurementArray | None = None
        self.axis_index: int | None = None

    def bind(self, array: data.MeasurementArray, axis_index: int) -> None:
        """Bind axis to the underlying data.

        Parameters
        ----------
            array: The MeasurementArray being bound to
            axis_index: The corresponding axis_index for this Axis on the MeasurementArray

        """
        self.axis_index = axis_index
        self.array = array

    @property
    def size(self) -> int:
        """The size of this axis."""
        if self.array is None or self.axis_index is None:
            raise errors.UninitializedError
        return self.array.shape[self.axis_index]

    @property
    def coordinates(self) -> np.ndarray:
        """The coordinates associated with this axis."""
        return np.linspace(self.extents[0], self.extents[-1], num=self.size)

    def slice(self, key: slice) -> LinearAxis:
        """Generate a subsection of this axis.

        Returns a subset of this axis based on the associated slice key.
        Designed to work in conjunction with the MeasurementArray being sliced.

        Parameters
        ----------
            key: slice associated with this axis

        """
        new_coordinates = self.coordinates[key]
        return LinearAxis(
            name=self.name,
            extents=[new_coordinates[0], new_coordinates[-1]],
            period=self.period,
            units=self.units,
        )

    def __eq__(self, other):
        if isinstance(other, LinearAxis):
            return all(
                [
                    self.name == other.name,
                    self.extents == other.extents,
                    self.period == other.period,
                    self.units == other.units,
                    self.size == other.size,
                ]
            )
        return NotImplemented


class LogarithmicAxis:
    """LogarithmicAxis.

    Details on all Axis more generally can be found with the rest of the borehole.io documentation.

    Parameters
    ----------
        name: The relevant name for this Axis
        extents: Data extents for this Axis
        units: The units of this Axis

    .. _borehole.io Documentation: https://borehole.io/spec

    """

    def __init__(
        self,
        name: str,
        extents,
        units: str | None = None,
    ) -> None:
        self.name = name
        self.units = units
        self.extents = extents

        self.array: data.MeasurementArray | None = None
        self.axis_index: int | None = None

    def bind(self, array: data.MeasurementArray, axis_index: int) -> None:
        """Bind axis to the underlying data.

        Parameters
        ----------
            array: The MeasurementArray being bound to
            axis_index: The corresponding axis_index for this Axis on the MeasurementArray

        """
        self.axis_index = axis_index
        self.array = array

    @property
    def size(self) -> int:
        """The size of this axis."""
        if self.array is None or self.axis_index is None:
            raise errors.UninitializedError
        return self.array.shape[self.axis_index]

    @property
    def coordinates(self) -> np.ndarray:
        """The coordinates associated with this axis."""
        return np.logspace(np.log10(self.extents[0]), np.log10(self.extents[-1]), num=self.size)

    def slice(self, key: slice) -> LogarithmicAxis:
        """Generate a subsection of this axis.

        Returns a subset of this axis based on the associated slice key.
        Designed to work in conjunction with the MeasurementArray being sliced.

        Parameters
        ----------
            key: slice associated with this axis

        """
        new_coordinates = self.coordinates[key]
        first = new_coordinates[0]
        last = new_coordinates[-1]
        return LogarithmicAxis(
            name=self.name,
            extents=[first, last],
            units=self.units,
        )

    def __eq__(self, other):
        if isinstance(other, LogarithmicAxis):
            return all(
                [
                    self.name == other.name,
                    self.extents == other.extents,
                    self.units == other.units,
                    self.size == other.size,
                    self.axis_index == other.axis_index,
                ]
            )
        return NotImplemented


class LabelledAxis:
    """LabelledAxis.

    Details on all Axis more generally can be found with the rest of the borehole.io documentation.

    Parameters
    ----------
        labels: The labels associated with this Axis

    .. _borehole.io Documentation: https://borehole.io/spec

    """

    def __init__(self, labels: Sequence[data.Label]) -> None:
        self.labels = labels

        self.array: data.MeasurementArray | None = None
        self.axis_index: int | None = None

    def bind(self, array: data.MeasurementArray, axis_index: int) -> None:
        """Bind axis to the underlying data.

        Also propagates the binding down through to underlying labels of this axis.

        Parameters
        ----------
            array: The MeasurementArray being bound to
            axis_index: The corresponding axis_index for this Axis on the MeasurementArray

        """
        self.axis_index = axis_index
        self.array = array

        for index, label in enumerate(self.labels):
            slice_key: list[slice | int] = [slice(None) for _ in range(len(self.array.axes))]
            slice_key[axis_index] = index
            labelled_array = self.array[*slice_key]
            label.bind(labelled_array)

    def slice(self, key: slice) -> LabelledAxis:
        """Generate a subsection of this axis.

        Returns a subset of this axis based on the associated slice key.
        Designed to work in conjunction with the MeasurementArray being sliced.

        Parameters
        ----------
            key: slice associated with this axis

        """
        return LabelledAxis([label.unbound() for label in self.labels[key]])

    def __eq__(self, other):
        if isinstance(other, LabelledAxis):
            if len(self.labels) != len(other.labels):
                return False
            for idx, label in enumerate(self.labels):
                other_label = other.labels[idx]
                if label != other_label:
                    return False
            return True
        return NotImplemented


class CoordinateAxis:
    """CoordinateAxis.

    Details on all Axis more generally can be found with the rest of the borehole.io documentation.

    Parameters
    ----------
        name: The relevant name for this Axis
        raw_coordinates: The raw coordinates for this Axis
        units: The units of this Axis
        transform: Optional PolynomialTransform to transform the Axis coordinates

    .. _borehole.io Documentation: https://borehole.io/spec

    """

    def __init__(
        self,
        name: str,
        raw_coordinates: np.ndarray,
        units: str | None = None,
        transform: data.PolynomialTransform | None = None,
    ) -> None:
        self.name = name
        self.units = units
        self.transform = transform
        self.raw_coordinates = raw_coordinates

        self.array: data.MeasurementArray | None = None
        self.axis_index: int | None = None

    def bind(self, array: data.MeasurementArray, axis_index: int) -> None:
        """Bind axis to the underlying data.

        Parameters
        ----------
            array: The MeasurementArray being bound to
            axis_index: The corresponding axis_index for this Axis on the MeasurementArray

        """
        self.axis_index = axis_index
        self.array = array

        if self.size != array.shape[axis_index]:
            error = "CoordinateAxis size mismatch with data shape"
            raise TypeError(error)

    @property
    def coordinates(self) -> np.ndarray:
        """The coordinates associated with this axis.

        After having been transformed if a transform is required.
        """
        if self.transform:
            return self.transform(self.raw_coordinates)
        return self.raw_coordinates

    @property
    def bounds(self):
        """Data bounds of this axis."""
        coordinates = self.coordinates
        return [coordinates.min(), coordinates.max()]

    @property
    def size(self) -> int:
        """The size of this axis."""
        return self.coordinates.size

    def slice(self, key: slice) -> CoordinateAxis:
        """Generate a subsection of this axis.

        Returns a subset of this axis based on the associated slice key.
        Designed to work in conjunction with the MeasurementArray being sliced.

        Parameters
        ----------
            key: slice associated with this axis

        """
        new_coordinates = self.raw_coordinates[key]
        return CoordinateAxis(
            name=self.name,
            raw_coordinates=new_coordinates,
            units=self.units,
            transform=self.transform,
        )

    def __eq__(self, other):
        if isinstance(other, CoordinateAxis):
            return all(
                [
                    self.name == other.name,
                    self.units == other.units,
                    self.transform == other.transform,
                    np.array_equal(self.raw_coordinates, other.raw_coordinates),
                ]
            )
        return NotImplemented


class CompositeAxis:
    """CompositeAxis.

    Details on all Axis more generally can be found with the rest of the borehole.io documentation.

    Parameters
    ----------
        descriptors: The underlying axes associated with this Composite Axis

    .. _borehole.io Documentation: https://borehole.io/spec

    """

    def __init__(self, descriptors: Sequence[LinearAxis | CoordinateAxis | LogarithmicAxis]) -> None:
        self.descriptors = descriptors

        self.array: data.MeasurementArray | None = None
        self.axis_index: int | None = None

    def bind(self, array: data.MeasurementArray, axis_index: int) -> None:
        """Bind axis to the underlying data.

        Propagates the bind through to the underlying descriptors on this axis.

        Parameters
        ----------
            array: The MeasurementArray being bound to
            axis_index: The corresponding axis_index for this Axis on the MeasurementArray

        """
        self.axis_index = axis_index
        self.array = array

        for descriptor in self.descriptors:
            descriptor.bind(array, axis_index)

    def slice(self, key: slice) -> CompositeAxis:
        """Generate a subsection of this axis.

        Returns a subset of this axis based on the associated slice key.
        Designed to work in conjunction with the MeasurementArray being sliced.

        Parameters
        ----------
            key: slice associated with this axis

        """
        new_axes = [axis.slice(key) for axis in self.descriptors]
        return CompositeAxis(new_axes)

    def __eq__(self, other):
        if isinstance(other, CompositeAxis):
            if len(self.descriptors) != len(other.descriptors):
                return False
            for idx, axis in enumerate(self.descriptors):
                other_axis = other.descriptors[idx]
                if axis != other_axis:
                    return False
            return True
        return NotImplemented


Axis = Union[LinearAxis, LogarithmicAxis, LabelledAxis, CoordinateAxis, CompositeAxis]
