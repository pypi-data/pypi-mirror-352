import numpy as np

from boreholeio import data as bio


def test_construct_bind_size_coords():
    subject = bio.LogarithmicAxis("test", [0.1, 100])
    array = np.zeros((100, 300))
    subject.bind(array, 0)

    assert subject.size == 100

    expected_coordinates = np.logspace(-1, 2, 100)
    assert np.array_equal(subject.coordinates, expected_coordinates)


def test_slicing_good():
    subject = bio.LogarithmicAxis("test", [0.1, 100])
    array = np.zeros((100, 300))
    subject.bind(array, 0)

    sliced = subject.slice(slice(5, 20))

    assert sliced.extents[0] == 0.1417474162926805
    assert sliced.extents[1] == 0.3764935806792468
    # We can't assert on size of the output because that only makes sense
    # in the context of the parent also sliced array having been rebound


def test_happy_equality():
    one = bio.LogarithmicAxis("test", [0.1, 100])
    array = np.zeros((100, 300))
    one.bind(array, 0)

    two = bio.LogarithmicAxis("test", [0.1, 100])
    array = np.zeros((100, 300))
    two.bind(array, 0)

    assert one == two


def test_unhappy_equality_due_to_types():
    subject = bio.LogarithmicAxis("test", [0.1, 100])
    array = np.zeros((100, 300))
    subject.bind(array, 0)

    assert subject != "hi"


def test_unhappy_equality_due_to_attributes():
    array = np.zeros((100, 100))

    # Basic
    one = bio.LogarithmicAxis("test", [0.1, 100])
    one.bind(array, 0)

    # different index
    two = bio.LogarithmicAxis("test", [0.1, 100])
    two.bind(array, 1)

    # different name
    three = bio.LogarithmicAxis("other", [0.1, 100])
    three.bind(array, 0)

    # different extents
    four = bio.LogarithmicAxis("other", [0.1, 10])
    four.bind(array, 0)

    # different array
    five = bio.LogarithmicAxis("test", [0.1, 100])
    five.bind(np.zeros((200, 200)), 0)

    assert one != two
    assert one != three
    assert one != four
    assert one != five
