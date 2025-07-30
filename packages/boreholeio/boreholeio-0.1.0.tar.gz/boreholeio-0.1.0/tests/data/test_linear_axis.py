from boreholeio import data as bio


def test_equality_with_other_random_things():
    subject = bio.LinearAxis("test", [0, 1])

    assert subject != "hi"
