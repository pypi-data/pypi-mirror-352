import numpy as np
import pytest

from boreholeio import data as bio


def test_ravel_returns_ndarray():
    depth_axis = bio.LinearAxis(name="Depth", units="m", extents=[0, 1000])
    azimuth_axis = bio.LinearAxis(name="Azimuth", units="deg", extents=[0, 350], period=360)
    data = np.zeros((1000, 36))
    array = bio.MeasurementArray(data, axes=[depth_axis, azimuth_axis])

    output = array.ravel()

    assert isinstance(output, np.ndarray)
    assert not isinstance(output, bio.MeasurementArray)

    output = np.ravel(array)

    assert isinstance(output, np.ndarray)
    assert not isinstance(output, bio.MeasurementArray)


def test_roll_returns_ndarray():
    depth_axis = bio.LinearAxis(name="Depth", units="m", extents=[0, 1000])
    azimuth_axis = bio.LinearAxis(name="Azimuth", units="deg", extents=[0, 350], period=360)
    data = np.zeros((1000, 36))
    array = bio.MeasurementArray(data, axes=[depth_axis, azimuth_axis])

    output = np.roll(array, (1, 1))

    assert isinstance(output, np.ndarray)
    assert not isinstance(output, bio.MeasurementArray)


def test_flatten_returns_ndarray():
    depth_axis = bio.LinearAxis(name="Depth", units="m", extents=[0, 1000])
    azimuth_axis = bio.LinearAxis(name="Azimuth", units="deg", extents=[0, 350], period=360)
    data = np.zeros((1000, 36))
    array = bio.MeasurementArray(data, axes=[depth_axis, azimuth_axis])

    output = array.flatten()

    assert isinstance(output, np.ndarray)
    assert not isinstance(output, bio.MeasurementArray)


def test_slicing_returns_subclass():
    depth_axis = bio.LinearAxis(name="Depth", units="m", extents=[1, 200])
    azimuth_axis = bio.LinearAxis(name="Azimuth", units="deg", extents=[0, 350], period=360)
    data = np.zeros((1000, 36))
    array = bio.MeasurementArray(data, axes=[depth_axis, azimuth_axis])

    output = array[1:10, :]

    assert isinstance(output, np.ndarray)
    assert isinstance(output, bio.MeasurementArray)


def test_transpose_does_what_youd_think():
    depth_axis = bio.LinearAxis(name="Depth", units="m", extents=[0, 1000])
    azimuth_axis = bio.LinearAxis(name="Azimuth", units="deg", extents=[0, 350], period=360)
    data = np.zeros((1000, 36))
    array = bio.MeasurementArray(data, axes=[depth_axis, azimuth_axis])

    transposed = array.transpose()

    assert isinstance(transposed, np.ndarray)
    assert isinstance(transposed, bio.MeasurementArray)

    transposed = np.transpose(array)

    assert isinstance(transposed, np.ndarray)
    assert isinstance(transposed, bio.MeasurementArray)


def test_rot90_does_what_youd_think():
    depth_axis = bio.LinearAxis(name="Depth", units="m", extents=[0, 1000])
    azimuth_axis = bio.LinearAxis(name="Azimuth", units="deg", extents=[0, 350], period=360)
    data = np.zeros((1000, 36))
    array = bio.MeasurementArray(data, axes=[depth_axis, azimuth_axis])

    rot90d = np.rot90(array)

    assert isinstance(rot90d, np.ndarray)
    assert isinstance(rot90d, bio.MeasurementArray)


def test_flipud_does_what_youd_think():
    depth_axis = bio.LinearAxis(name="Depth", units="m", extents=[0, 1000])
    azimuth_axis = bio.LinearAxis(name="Azimuth", units="deg", extents=[0, 350], period=360)
    data = np.zeros((1000, 36))
    array = bio.MeasurementArray(data, axes=[depth_axis, azimuth_axis])

    output = np.flipud(array)

    assert isinstance(output, np.ndarray)
    assert isinstance(output, bio.MeasurementArray)

    assert len(output.axes) == 2
    assert output.axes[0].extents == [1000, 0]
    assert output.axes[1].extents == [0, 350]


def test_fliplr_does_what_youd_think():
    depth_axis = bio.LinearAxis(name="Depth", units="m", extents=[0, 1000])
    azimuth_axis = bio.LinearAxis(name="Azimuth", units="deg", extents=[0, 350], period=360)
    data = np.zeros((1000, 36))
    array = bio.MeasurementArray(data, axes=[depth_axis, azimuth_axis])

    output = np.fliplr(array)

    assert isinstance(output, np.ndarray)
    assert isinstance(output, bio.MeasurementArray)

    assert len(output.axes) == 2
    assert output.axes[0].extents == [0, 1000]
    assert output.axes[1].extents == [350, 0]


def test_flip_does_what_youd_think():
    depth_axis = bio.LinearAxis(name="Depth", units="m", extents=[0, 1000])
    azimuth_axis = bio.LinearAxis(name="Azimuth", units="deg", extents=[0, 350], period=360)
    data = np.zeros((1000, 36))
    array = bio.MeasurementArray(data, axes=[depth_axis, azimuth_axis])

    output = np.flip(array)

    assert isinstance(output, np.ndarray)
    assert isinstance(output, bio.MeasurementArray)

    assert len(output.axes) == 2
    assert output.axes[0].extents == [1000, 0]
    assert output.axes[1].extents == [350, 0]


def test_fill_retains_subclass():
    depth_axis = bio.LinearAxis(name="Depth", units="m", extents=[0, 1000])
    azimuth_axis = bio.LinearAxis(name="Azimuth", units="deg", extents=[0, 350], period=360)
    data = np.zeros((1000, 36))
    array = bio.MeasurementArray(data, axes=[depth_axis, azimuth_axis])

    array.fill(1)

    assert isinstance(array, np.ndarray)
    assert isinstance(array, bio.MeasurementArray)


def test_add_retains_subclass():
    depth_axis = bio.LinearAxis(name="Depth", units="m", extents=[0, 1000])
    azimuth_axis = bio.LinearAxis(name="Azimuth", units="deg", extents=[0, 350], period=360)
    data = np.zeros((1000, 36))

    array1 = bio.MeasurementArray(data, axes=[depth_axis, azimuth_axis])
    array1.fill(1)
    array2 = bio.MeasurementArray(data, axes=[depth_axis, azimuth_axis])
    array2.fill(2)

    array3 = array1 + array2

    assert isinstance(array3, np.ndarray)
    assert isinstance(array3, bio.MeasurementArray)


def test_add_errors_if_axis_dont_match():
    depth_axis = bio.LinearAxis(name="Depth", units="m", extents=[0, 1000])
    azimuth_axis = bio.LinearAxis(name="Azimuth", units="deg", extents=[0, 350], period=360)
    data = np.zeros((1000, 36))

    array1 = bio.MeasurementArray(data, axes=[azimuth_axis, depth_axis])
    array1.fill(1)
    array2 = bio.MeasurementArray(data, axes=[depth_axis, azimuth_axis])
    array2.fill(2)

    with pytest.raises(ValueError, match=r".*axes.*"):
        array1 + array2

    with pytest.raises(ValueError, match=r".*axes.*"):
        array2 + array1


def test_min_and_max_dont_return_subclasses():
    depth_axis = bio.LinearAxis(name="Depth", units="m", extents=[0, 1000])
    azimuth_axis = bio.LinearAxis(name="Azimuth", units="deg", extents=[0, 350], period=360)
    data = np.zeros((1000, 36))
    array = bio.MeasurementArray(data, axes=[depth_axis, azimuth_axis])

    array_min = array.min()
    array_max = array.max()
    data_min = data.min()
    data_max = data.max()

    assert not isinstance(array_min, bio.MeasurementArray)
    assert not isinstance(array_min, bio.MeasurementArray)
    assert data_min == array_min
    assert data_max == array_max


def test_out_of_bounds_slicing():
    depth_axis = bio.LinearAxis(name="Depth", units="m", extents=[0, 1000])
    azimuth_axis = bio.LinearAxis(name="Azimuth", units="deg", extents=[0, 350], period=360)
    data = np.zeros((1000, 36))
    array = bio.MeasurementArray(data, axes=[depth_axis, azimuth_axis])

    with pytest.raises(IndexError, match=r".*index.*bounds.*"):
        array[999999]


def test_ellipsis_and_many_slicing_options():
    depth_axis = bio.LinearAxis(name="Depth", units="m", extents=[0, 1000])
    azimuth_axis = bio.LinearAxis(name="Azimuth", units="deg", extents=[0, 350], period=360)
    data = np.zeros((1000, 36))
    array = bio.MeasurementArray(data, axes=[depth_axis, azimuth_axis])

    one = array[1]
    two = array[1,]
    three = array[1, :]
    four = array[1, ...]

    assert isinstance(one, bio.MeasurementArray)
    assert isinstance(two, bio.MeasurementArray)
    assert isinstance(three, bio.MeasurementArray)
    assert isinstance(four, bio.MeasurementArray)

    assert np.array_equal(one, two)
    assert np.array_equal(two, three)
    assert np.array_equal(three, four)

    assert one.axes == two.axes
    assert three.axes == two.axes
    assert three.axes == four.axes


def test_ellipsis_with_many_dimensional_data():
    axis1 = bio.LinearAxis(name="axis1", extents=[0, 1000])
    axis2 = bio.LinearAxis(name="axis2", extents=[0, 1000])
    axis3 = bio.LinearAxis(name="axis3", extents=[0, 1000])
    axis4 = bio.LinearAxis(name="axis4", extents=[0, 1000])
    axis5 = bio.LinearAxis(name="axis5", extents=[0, 1000])
    data = np.zeros((10, 20, 30, 40, 50))
    array = bio.MeasurementArray(data, axes=[axis1, axis2, axis3, axis4, axis5])

    sliced_data = array[3, ..., 6]
    assert isinstance(sliced_data, bio.MeasurementArray)
    assert sliced_data.shape == (20, 30, 40)
    assert len(sliced_data.axes) == 3
    assert sliced_data.axes[0].name == "axis2"
    assert sliced_data.axes[1].name == "axis3"
    assert sliced_data.axes[2].name == "axis4"

    sliced_data = array[:, 3, ..., 6]
    assert isinstance(sliced_data, bio.MeasurementArray)
    assert sliced_data.shape == (10, 30, 40)
    assert len(sliced_data.axes) == 3
    assert sliced_data.axes[0].name == "axis1"
    assert sliced_data.axes[1].name == "axis3"
    assert sliced_data.axes[2].name == "axis4"


def test_cannot_instantiate_without_axes():
    data = np.asarray([])

    with pytest.raises(TypeError, match=r".*axes.*"):
        _ = bio.MeasurementArray(data)

    with pytest.raises(TypeError, match=r".*axes.*"):
        _ = bio.MeasurementArray(data, None)

    with pytest.raises(ValueError, match=r".*axes.*"):
        _ = bio.MeasurementArray(data, [])


def test_cannot_instantiate_with_multiple_labelled_axes():
    a_label = bio.Label("A")
    b_label = bio.Label("B")
    c_label = bio.Label("C")
    d_label = bio.Label("D")

    one = bio.LabelledAxis([a_label, b_label])
    two = bio.LabelledAxis([c_label, d_label])
    data = np.asarray([])

    with pytest.raises(NotImplementedError, match=r".*Multiple.*Labelled.*"):
        _ = bio.MeasurementArray(data, [one, two])


def test_cannot_instantiate_with_label_and_labelled_axis():
    a_label = bio.Label("A")
    b_label = bio.Label("B")
    c_label = bio.Label("C")

    axis = bio.LabelledAxis([a_label, b_label])
    data = np.asarray([])

    with pytest.raises(NotImplementedError, match=r"Label.*data.*axes.*"):
        _ = bio.MeasurementArray(data, [axis], label=c_label)


def test_we_dont_support_transforms():
    label = bio.Label("test", transform=bio.PolynomialTransform((1, 2)))
    data = np.asarray([])

    with pytest.raises(NotImplementedError, match=r"Transform.*supported.*"):
        _ = bio.MeasurementArray(data, [bio.LinearAxis("Depth", [0, 1])], label=label)

    with pytest.raises(NotImplementedError, match=r"Transform.*supported.*"):
        _ = bio.MeasurementArray(data, [bio.LabelledAxis([label])])


def test_getting_a_single_item_as_not_subclass():
    depth_axis = bio.LinearAxis(name="Depth", units="m", extents=[0, 1000])
    azimuth_axis = bio.LinearAxis(name="Azimuth", units="deg", extents=[0, 350], period=360)
    data = np.zeros((1000, 36))
    array = bio.MeasurementArray(data, axes=[depth_axis, azimuth_axis])

    output = array[10, 10]
    assert not isinstance(output, bio.MeasurementArray)
    assert output == data[10, 10]


def test_transpose_with_complex_3d_axes_and_labelled_axes_is_fine():
    depth_axis = bio.LinearAxis(name="Depth", units="m", extents=[0, 1000])
    azimuth_axis = bio.LinearAxis(name="Azimuth", units="deg", extents=[0, 270], period=360)
    r_label = bio.Label("R")
    g_label = bio.Label("G")
    b_label = bio.Label("B")
    labelled_axis = bio.LabelledAxis([r_label, g_label, b_label])

    data = np.zeros((5, 4, 3))
    data[0][0] = [1, 2, 3]
    data[-1][0] = [11, 22, 33]
    data[0][-1] = [111, 122, 133]
    data[-1][-1] = [211, 222, 233]

    array = bio.MeasurementArray(data, [depth_axis, azimuth_axis, labelled_axis])

    weird_transposed = array.transpose()
    assert isinstance(weird_transposed, bio.MeasurementArray)
    assert weird_transposed.shape == (3, 4, 5)
    assert weird_transposed[0, 0, 0] == 1
    assert weird_transposed[0, -1, 0] == 111
    assert weird_transposed[0, 0, -1] == 11
    assert weird_transposed[0, -1, -1] == 211
    assert weird_transposed[1, 0, 0] == 2
    assert weird_transposed[1, -1, 0] == 122
    assert weird_transposed[1, 0, -1] == 22
    assert weird_transposed[1, -1, -1] == 222
    assert weird_transposed[2, 0, 0] == 3
    assert weird_transposed[2, -1, 0] == 133
    assert weird_transposed[2, 0, -1] == 33
    assert weird_transposed[2, -1, -1] == 233
    assert len(weird_transposed.axes) == 3
    assert isinstance(weird_transposed.axes[0], bio.LabelledAxis)
    assert len(weird_transposed.axes[0].labels) == 3
    assert weird_transposed.axes[0].labels[0].name == "R"
    assert weird_transposed.axes[0].labels[1].name == "G"
    assert weird_transposed.axes[0].labels[2].name == "B"
    assert isinstance(weird_transposed.axes[1], bio.LinearAxis)
    weird_transposed.axes[1].name = "Azimuth"
    assert isinstance(weird_transposed.axes[2], bio.LinearAxis)
    weird_transposed.axes[2].name = "Depth"

    transposed_image = array.transpose((1, 0, 2))
    assert isinstance(transposed_image, bio.MeasurementArray)
    assert transposed_image.shape == (4, 5, 3)
    assert transposed_image[0, 0, 0] == 1
    assert transposed_image[0, 0, 1] == 2
    assert transposed_image[0, 0, 2] == 3
    assert transposed_image[-1, 0, 0] == 111
    assert transposed_image[-1, 0, 1] == 122
    assert transposed_image[-1, 0, 2] == 133
    assert transposed_image[0, -1, 0] == 11
    assert transposed_image[0, -1, 1] == 22
    assert transposed_image[0, -1, 2] == 33
    assert transposed_image[-1, -1, 0] == 211
    assert transposed_image[-1, -1, 1] == 222
    assert transposed_image[-1, -1, 2] == 233
    assert len(transposed_image.axes) == 3
    assert isinstance(transposed_image.axes[0], bio.LinearAxis)
    transposed_image.axes[0].name = "Azimuth"
    assert isinstance(transposed_image.axes[1], bio.LinearAxis)
    transposed_image.axes[1].name = "Depth"
    assert isinstance(transposed_image.axes[2], bio.LabelledAxis)
    assert len(transposed_image.axes[2].labels) == 3
    assert transposed_image.axes[2].labels[0].name == "R"
    assert transposed_image.axes[2].labels[1].name == "G"
    assert transposed_image.axes[2].labels[2].name == "B"

    transposed_image_again = array.transpose(1, 0, 2)
    assert isinstance(transposed_image_again, bio.MeasurementArray)
    assert np.array_equal(transposed_image_again, transposed_image)
    assert transposed_image_again.axes == transposed_image.axes


def test_transposing_1d_array():
    depth_axis = bio.LinearAxis(name="Depth", units="m", extents=[0, 1000])
    data = np.zeros(100)

    array = bio.MeasurementArray(data, [depth_axis])

    output = array.transpose()
    assert isinstance(output, bio.MeasurementArray)
    assert output.shape == array.shape
    assert output.axes == array.axes
    assert np.array_equal(array, output)

    output = array.transpose(0)
    assert isinstance(output, bio.MeasurementArray)
    assert output.shape == array.shape
    assert output.axes == array.axes
    assert np.array_equal(array, output)


def test_transposing_4d_array():
    a_axis = bio.LinearAxis(name="a", extents=[0, 10])
    b_axis = bio.LinearAxis(name="b", extents=[0, 10])
    c_axis = bio.LinearAxis(name="c", extents=[0, 10])
    d_axis = bio.LinearAxis(name="d", extents=[0, 10])
    data = np.zeros((10, 10, 10, 10))

    array = bio.MeasurementArray(data, [a_axis, b_axis, c_axis, d_axis])

    output = array.transpose()
    assert isinstance(output, bio.MeasurementArray)
    assert ["d", "c", "b", "a"] == [axis.name for axis in output.axes]

    output = array.transpose((3, 0, 1, 2))
    assert isinstance(output, bio.MeasurementArray)
    assert ["d", "a", "b", "c"] == [axis.name for axis in output.axes]

    output2 = array.transpose(3, 0, 1, 2)
    assert isinstance(output2, bio.MeasurementArray)
    assert ["d", "a", "b", "c"] == [axis.name for axis in output.axes]

    output = array.transpose([3, 0, 1, 2])
    assert isinstance(output, bio.MeasurementArray)
    assert ["d", "a", "b", "c"] == [axis.name for axis in output.axes]
