from boreholeio import data as bio


def test_happy_equality():
    one = bio.PolynomialTransform((1, 2))
    two = bio.PolynomialTransform((1, 2))

    assert one == two


def test_extended_equality():
    one = bio.PolynomialTransform((1, 2))
    two = bio.PolynomialTransform((1, 2, 0))

    # Id love for this to be true, but its not
    assert one != two


def test_unahppy_equality_simple():
    one = bio.PolynomialTransform((1, 2))
    two = bio.PolynomialTransform((2, 3))

    assert one != two


def test_unahppy_equality_complex():
    subject = bio.PolynomialTransform((1, 2))

    assert subject != "test"
