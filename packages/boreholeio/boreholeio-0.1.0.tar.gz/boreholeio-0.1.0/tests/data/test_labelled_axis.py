import numpy as np
import pytest

from boreholeio import data as bio


@pytest.fixture
def rgb_dataset():
    rows = []
    rows.append([1, 11, 101])
    rows.append([2, 12, 102])
    rows.append([3, 13, 103])
    rows.append([4, 14, 104])
    rows.append([5, 15, 105])
    rows.append([5, 15, 105])
    rows.append([6, 16, 106])
    rows.append([7, 17, 107])
    rows.append([8, 18, 108])
    rows.append([9, 19, 109])
    return np.asarray(rows)


def test_construction_and_binding_with_labels(rgb_dataset):
    r_label = bio.Label("R")
    g_label = bio.Label("G")
    b_label = bio.Label("B")

    subject = bio.LabelledAxis([r_label, g_label, b_label])
    depth_axis = bio.LinearAxis("test", [1, 100])
    _ = bio.MeasurementArray(rgb_dataset, [depth_axis, subject])

    assert r_label.bounds == [1, 9]
    assert g_label.bounds == [11, 19]
    assert b_label.bounds == [101, 109]


def test_slicing_labelled_axis(rgb_dataset):
    orig_r_label = bio.Label("R")
    orig_g_label = bio.Label("G")
    orig_b_label = bio.Label("B")

    subject = bio.LabelledAxis([orig_r_label, orig_g_label, orig_b_label])
    depth_axis = bio.LinearAxis("test", [1, 100])
    array = bio.MeasurementArray(rgb_dataset, [depth_axis, subject])

    new_array = array[3:6, 1:]

    assert len(new_array.axes) == 2
    assert len(new_array.axes[1].labels) == 2
    assert orig_r_label.bounds == [1, 9]
    assert orig_g_label.bounds == [11, 19]
    assert orig_b_label.bounds == [101, 109]

    [new_g_label, new_b_label] = new_array.axes[1].labels
    assert new_g_label.bounds == [14, 15]
    assert new_b_label.bounds == [104, 105]


def test_slicing_down_to_single_axis(rgb_dataset):
    orig_r_label = bio.Label("R")
    orig_g_label = bio.Label("G")
    orig_b_label = bio.Label("B")

    subject = bio.LabelledAxis([orig_r_label, orig_g_label, orig_b_label])
    depth_axis = bio.LinearAxis("test", [1, 100])
    array = bio.MeasurementArray(rgb_dataset, [depth_axis, subject])

    new_array = array[3:6, 1]

    assert orig_r_label.bounds == [1, 9]
    assert orig_g_label.bounds == [11, 19]
    assert orig_b_label.bounds == [101, 109]

    assert len(new_array.axes) == 1
    assert array.label is None
    assert new_array.label
    assert new_array.label.name == "G"


def test_happy_equality():
    one_a_label = bio.Label("A")
    one_b_label = bio.Label("B")
    one = bio.LabelledAxis([one_a_label, one_b_label])

    two_a_label = bio.Label("A")
    two_b_label = bio.Label("B")
    two = bio.LabelledAxis([two_a_label, two_b_label])

    assert one == two


def test_complex_inequality():
    a_label = bio.Label("A")
    b_label = bio.Label("B")
    subject = bio.LabelledAxis([a_label, b_label])

    # order differs
    other = bio.LabelledAxis([bio.Label("B"), bio.Label("A")])
    assert subject != other

    # missing label
    other = bio.LabelledAxis([bio.Label("A")])
    assert subject != other

    # label with different attributes
    other = bio.LabelledAxis([bio.Label("A", units="m"), bio.Label("B")])
    assert subject != other


def test_obvious_inequality():
    a_label = bio.Label("A")
    b_label = bio.Label("B")
    subject = bio.LabelledAxis([a_label, b_label])

    assert subject != "hi"
