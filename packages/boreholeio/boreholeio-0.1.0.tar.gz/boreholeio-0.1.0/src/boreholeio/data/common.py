"""Common module for shared classes in the data module."""

from __future__ import annotations

from typing import Sequence

import numpy as np
from numpy.polynomial import polynomial


class Label:
    """Data Label.

    Parameters
    ----------
        name: Label name
        units: Label units
        transform: Optional PolynomialTransform to transform the underlying data for this label

    """

    def __init__(self, name: str, units: str | None = None, transform: PolynomialTransform | None = None):
        self.name = name
        self.units = units
        self.transform = transform

        self._labelled_data: np.ndarray | None = None

    def bind(self, labelled_data: np.ndarray) -> None:
        """Bind label to underlying data.

        Required such that the label can have relevant coordinates and bounds.

        Parameters
        ----------
            labelled_data: The array view being bound to

        """
        self._labelled_data = np.asarray(labelled_data)

    def unbound(self) -> Label:
        """Generate a fresh unbound copy of the Label unbound from any data."""
        return Label(name=self.name, units=self.units, transform=self.transform)

    @property
    def _transformed(self) -> np.ndarray | None:
        """The coordinates this Label is a view over after having transformation applied if relevant."""
        if self.transform:
            return self.transform(self._labelled_data)
        return self._labelled_data

    @property
    def bounds(self):
        """Data bounds of the data this Label is a view over."""
        return [np.nanmin(self._transformed), np.nanmax(self._transformed)]

    def __eq__(self, other):
        if isinstance(other, Label):
            return all(
                [
                    self.name == other.name,
                    self.units == other.units,
                    self.transform == other.transform,
                ]
            )
        return NotImplemented


class PolynomialTransform:
    """Class representing a Polynomial Transform which is applied to data.

    This is to cater for situations where underlying data has been measured and stored such that
    a polynomial transform needs to be applied to get the actual values.

    Parameters
    ----------
        coefficients: The coefficients for the polynomial transform.

    """

    def __init__(self, coefficients: Sequence[float]):
        self.coefficients = coefficients

    def __call__(self, arg):
        """Transform values."""
        return self._polynomial(arg)

    @property
    def _polynomial(self) -> polynomial.Polynomial:
        """The actual polynomial which can be applied to data."""
        return polynomial.Polynomial(self.coefficients)

    def __eq__(self, other):
        if isinstance(other, PolynomialTransform):
            return self.coefficients == other.coefficients
        return NotImplemented
