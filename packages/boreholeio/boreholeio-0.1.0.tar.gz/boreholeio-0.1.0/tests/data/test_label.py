import numpy as np

from boreholeio import data as bio


def test_basics_with_no_transform():
    subject = bio.Label(name="test")
    subject.bind(np.asarray(range(10)))

    assert subject.bounds == [0, 9]


def test_transformation():
    transform = bio.PolynomialTransform((1, 2))
    subject = bio.Label(name="test", transform=transform)
    subject.bind(np.asarray(range(10)))

    assert subject.bounds == [1, 19]


def test_happy_equality():
    one = bio.Label(name="test")
    one.bind(np.asarray(range(10)))

    two = bio.Label(name="test")
    two.bind(np.asarray(range(10)))

    assert one == two


def test_obvious_inequality():
    subject = bio.Label(name="test")
    subject.bind(np.asarray(range(10)))

    assert subject != "hi"


def test_attribute_inequality():
    subject = bio.Label(name="test")
    subject.bind(np.asarray(range(10)))

    # transform differs
    other = bio.Label(name="test", transform=bio.PolynomialTransform((1, 2)))
    other.bind(np.asarray(range(10)))
    assert subject != other

    # name differs
    other = bio.Label(name="test2")
    other.bind(np.asarray(range(10)))
    assert subject != other

    # units differs
    other = bio.Label(name="test", units="different")
    other.bind(np.asarray(range(10)))
    assert subject != other
