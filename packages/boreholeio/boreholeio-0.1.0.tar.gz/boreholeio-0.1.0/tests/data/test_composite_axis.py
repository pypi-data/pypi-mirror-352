import numpy as np

from boreholeio import data as bio


def test_construct_bind_size_coords():
    linear = bio.LinearAxis("linear", [0, 1000])
    log = bio.LogarithmicAxis("log", [0.1, 100])
    subject = bio.CompositeAxis([linear, log])
    array = np.zeros((100, 300))
    subject.bind(array, 0)

    assert linear.size == 100
    assert log.size == 100

    expected_coordinates = np.linspace(0, 1000, 100)
    assert np.array_equal(linear.coordinates, expected_coordinates)

    expected_coordinates = np.logspace(-1, 2, 100)
    assert np.array_equal(log.coordinates, expected_coordinates)


def test_slicing():
    linear = bio.LinearAxis("linear", [0, 1000])
    log = bio.LogarithmicAxis("log", [0.1, 100])
    subject = bio.CompositeAxis([linear, log])
    array = np.zeros((100, 300))
    subject.bind(array, 0)

    key = slice(25, 75)
    sliced_array = array[key]
    output = subject.slice(key)
    output.bind(sliced_array, 0)

    sliced_linear = linear.slice(key)
    sliced_linear.bind(sliced_array, 0)
    assert output.descriptors[0] == sliced_linear

    sliced_log = log.slice(key)
    sliced_log.bind(sliced_array, 0)
    assert output.descriptors[1] == sliced_log


def test_happy_equality():
    subject = bio.CompositeAxis(
        [
            bio.LinearAxis("linear", [0, 1000]),
            bio.LogarithmicAxis("log", [0.1, 100]),
        ]
    )
    array = np.zeros((100, 300))
    subject.bind(array, 0)

    other = bio.CompositeAxis(
        [
            bio.LinearAxis("linear", [0, 1000]),
            bio.LogarithmicAxis("log", [0.1, 100]),
        ]
    )
    other_array = np.zeros((100, 300))
    other.bind(other_array, 0)

    assert subject == other


def test_obvious_inequality():
    subject = bio.CompositeAxis(
        [
            bio.LinearAxis("linear", [0, 1000]),
            bio.LogarithmicAxis("log", [0.1, 100]),
        ]
    )
    array = np.zeros((100, 300))
    subject.bind(array, 0)

    assert subject != "hi"


def test_complex_inequality():
    array = np.zeros((100, 300))

    subject = bio.CompositeAxis(
        [
            bio.LinearAxis("linear", [0, 1000]),
            bio.LogarithmicAxis("log", [0.1, 100]),
        ]
    )
    subject.bind(array, 0)

    # different count
    other = bio.CompositeAxis(
        [
            bio.LinearAxis("linear", [0, 1000]),
        ]
    )
    other.bind(array, 0)
    assert subject != other

    # different order
    other = bio.CompositeAxis(
        [
            bio.LogarithmicAxis("log", [0.1, 100]),
            bio.LinearAxis("linear", [0, 1000]),
        ]
    )
    other.bind(array, 0)
    assert subject != other

    # different attributes
    other = bio.CompositeAxis(
        [
            bio.LogarithmicAxis("log", [0.2, 20]),
            bio.LinearAxis("linear", [10, 100]),
        ]
    )
    other.bind(array, 0)
    assert subject != other
