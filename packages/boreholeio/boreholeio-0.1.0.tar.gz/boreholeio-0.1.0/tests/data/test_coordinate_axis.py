import numpy as np
import pytest

from boreholeio import data as bio


def test_construct_bind_size_bounds_coords():
    coordinates = np.asarray(range(200))
    subject = bio.CoordinateAxis("test", coordinates)
    array = np.zeros((200, 300))
    subject.bind(array, 0)

    assert subject.size == 200
    assert subject.bounds == [0, 199]
    assert np.array_equal(subject.coordinates, coordinates)


def test_coordinate_dimensions_need_to_match_bound_axes():
    coordinates = np.zeros(100)
    subject = bio.CoordinateAxis("test", coordinates)
    array = np.zeros((200, 300))

    with pytest.raises(TypeError, match=r"CoordinateAxis.*size.*"):
        subject.bind(array, 0)


def test_polynomial_coordinates():
    raw_coordinates = np.asarray(range(200))
    transform = bio.PolynomialTransform([1, 2])
    subject = bio.CoordinateAxis("test", raw_coordinates, transform=transform)

    expected_coordinates = transform(raw_coordinates)
    assert np.array_equal(expected_coordinates, subject.coordinates)


def test_simple_sub_axis():
    raw_coordinates = np.asarray(range(200))
    subject = bio.CoordinateAxis("test", raw_coordinates)

    sliced_axis = subject.slice(slice(25, 75))

    expected_coordinates = np.asarray(range(25, 75))
    expected_axis = bio.CoordinateAxis("test", expected_coordinates)
    assert sliced_axis == expected_axis


def test_sub_axis_with_transform():
    raw_coordinates = np.asarray(range(200))
    transform = bio.PolynomialTransform([1, 2])
    subject = bio.CoordinateAxis("test", raw_coordinates, transform=transform)

    sliced_axis = subject.slice(slice(25, 75))

    expected_coordinates = np.asarray(range(25, 75))
    expected_axis = bio.CoordinateAxis("test", expected_coordinates, transform=bio.PolynomialTransform([1, 2]))
    assert sliced_axis == expected_axis


def test_obvious_inequality():
    raw_coordinates = np.asarray(range(200))
    subject = bio.CoordinateAxis("test", raw_coordinates)

    assert subject != "hi"


def test_complex_inequality():
    raw_coordinates = np.asarray(range(200))
    subject = bio.CoordinateAxis("test", raw_coordinates)

    # name different
    other = bio.CoordinateAxis("diff", raw_coordinates)
    assert other != subject

    # coordinates different
    other = bio.CoordinateAxis("test", np.asarray(range(10)))
    assert other != subject

    # units different
    other = bio.CoordinateAxis("test", raw_coordinates, "m")
    assert other != subject

    # transform different
    other = bio.CoordinateAxis("test", raw_coordinates, transform=bio.PolynomialTransform([1, 2]))
    assert other != subject
