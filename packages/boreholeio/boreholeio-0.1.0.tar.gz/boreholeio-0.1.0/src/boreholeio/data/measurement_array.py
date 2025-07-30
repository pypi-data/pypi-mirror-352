"""Module providing the MeasurementArray class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

import numpy as np

from . import axes as _axes  # noqa: TID252
from . import common as _common  # noqa: TID252

if TYPE_CHECKING:
    from boreholeio import data


class MeasurementArray(np.ndarray):
    """MeasurementArray which subclasses np.ndarray whilst providing details about the relevant axes.

    This acts as the primary class for constructing and interacting with data from borehole.io.
    It is built upon and designed to interact with all of the relevant archive and storage formats.

    Parameters
    ----------
        input_array: The relevant data array this MeasurementArray represents
        axes: The array of axes which corresponds with the data dimensions
        label: The optional label if one exists for the implicit measurement axis


    .. _borehole.io Documentation: https://borehole.io/spec

    """

    def __new__(
        cls,
        input_array,
        axes: Sequence[data.Axis],
        label: data.Label | None = None,
    ):
        """Construct a MeasurementArray instance.

        This is implemented as per np.ndarray sub-classing guidelines.

        Parameters
        ----------
            cls: The class in question
            input_array: The data in question
            axes: The axes which index the data
            label: The optional label, if one exists for the implicit measurement axis

        """
        obj = np.asarray(input_array).view(cls)
        obj.axes = axes
        obj.label = label
        return obj

    def __array_finalize__(self, obj):
        """Array finalize as per numpy subclassing rules."""
        if obj is None:
            return  # pragma: no cover
        self.axes = getattr(obj, "axes", [])
        self.label = getattr(obj, "label", None)

    def __init__(self, input_array: np.ndarray, axes: Sequence[data.Axis], label: data.Label | None = None):
        del input_array
        self.axes = axes
        self.label = label

        if self.axes is None:
            error = "Missing axes must be supplied"
            raise TypeError(error)

        if len(self.axes) == 0:
            error = "Not enough axes supplied"
            raise ValueError(error)

        labelled_axes = [axis for axis in self.axes if isinstance(axis, _axes.LabelledAxis)]
        if len(labelled_axes) > 1:
            error = "Multiple LabelledAxis not supported"
            raise NotImplementedError(error)

        if self.label and len(labelled_axes):
            error = "Label on both data and axes unsupported"
            raise NotImplementedError(error)

        if self.label and self.label.transform:
            error = "Transformations aren't supported yet"
            raise NotImplementedError(error)

        for axis in labelled_axes:
            for label in axis.labels:
                if label.transform:
                    error = "Transformations aren't supported yet"
                    raise NotImplementedError(error)

        self.bind()

    def bind(self) -> None:
        """Bind the MeasurementArray to all the relevant axes and label."""
        for index, axis in enumerate(self.axes):
            axis.bind(self, index)
        if self.label:
            self.label.bind(self)

    def transpose(self, *args) -> MeasurementArray:
        """Transpose the MeasurementArray.

        This function returns a transposed version of the MeasurementArray.
        This both transposes the data and reorders the axes such that they are correctly
        ordered for the transposed data.

        For more details, please refer to numpy.transpose documentation.
        """
        output = super().transpose(*args)

        axes_args: Sequence = args
        if len(args) == 0:
            axes_args = tuple(reversed(range(self.ndim)))
        if len(args) == 1 and isinstance(args[0], Sequence):
            axes_args = args[0]
        new_axes = [self.axes[idx] for idx in axes_args]

        return MeasurementArray(output, new_axes)

    def __getitem__(self, key):
        """Index into the MeasurementArray.

        Acts like a standard N-dimensional sequence from an indexing perspective.
        Moreover, this mimics the behaviour of np.ndarray whilst preserving MeasurementArray
        and axes as and where appropriate.

        If indexing into a single value, that value is returned rather than an array.
        This return value carries no relevant axis information if it is a single value.

        In cases where a MeasurementArray array is going to be returned, the axes are the
        remaining ones which index the remaining data.

        If a LabelledAxis is indexed such that only a single Label would remain this Label
        is set on the returned MeasurementArray rather than a LabelledAxis with one Label.

        Parameters
        ----------
            key: Indexing argument(s)

        """
        new_array = np.asarray(self)
        sliced_output = new_array[key]
        output_label = self.label

        # If we have a single output, just return
        if len(sliced_output.shape) == 0:
            return sliced_output

        # Lets turn all keys into tuple so we can handle them the same
        # Then turn into a list because we want to append to it
        axes_keys = key
        if not isinstance(key, tuple):
            axes_keys = (key,)
        axes_keys = list(axes_keys)

        # If there is no ellipsis, and the count is less than axes count
        # Append an Ellipsis which is implicit so we can handle it consistently
        if (Ellipsis not in axes_keys) and (len(axes_keys) < len(self.axes)):
            axes_keys.append(Ellipsis)

        # Now we need to "pad out" any Ellipsis into N x slice(None) to fill axes count
        if Ellipsis in axes_keys:
            index = axes_keys.index(Ellipsis)
            axes_keys[index] = slice(None)
            while len(axes_keys) < len(self.axes):
                axes_keys.insert(index, slice(None))

        # Now we can slice all axes using their relevant key
        # Assembling array of axes as we go
        new_axes = []
        for axis, axis_key in zip(self.axes, axes_keys):
            if isinstance(axis, _axes.LabelledAxis):
                label = axis.labels[axis_key]
                if isinstance(label, _common.Label):
                    output_label = label.unbound()
            if not (isinstance(axis_key, slice) or axis_key == Ellipsis):
                continue
            new_axes.append(axis.slice(axis_key))

        return MeasurementArray(
            sliced_output,
            axes=new_axes,
            label=output_label,
        )

    def __add__(self, other):
        """Magic add method.

        Preventing adding two MeasurementArray if their axes differ.
        """
        if isinstance(other, MeasurementArray) and (self.axes != other.axes):
            error = f"axes mismatch between {self.axes} and {other.axes}"
            raise ValueError(error)
        return super().__add__(other)

    def __getattribute__(self, name):
        """Magic method for all attribute lookup.

        Needed for np.ndarray compatibility to delegate relevant methods to underlying
        data directly, whilst still responding to attributes of this instance.
        """
        # Here be dragons :-)
        # This is quite confusing with if this is returning the attribute ON this instance
        # or ON this class, or ON the superclass, but running it against this instance

        # First we capture what the default output would be
        # This is running the super get attribute, but it runs it in the context of this subclass
        default_output = super().__getattribute__(name)

        # Now if either its a special case we need to early exit on
        # OR it's an attribute of this subclass directly we can return whatever the default is
        if name in ["view", "__dict__", "__class__"] or name in vars(self):
            return default_output

        # If the method or attribute is not defined on this class we need to delegate it to the
        # underlying view of the ndarray so that we get out whatever ndarray would. This is to
        # handle the cases where a MeasurementArray doesn't make sense as an output and we can't
        # compute an appropriate set of axes for it.
        if name not in self.__class__.__dict__:
            return self.view(np.ndarray).__getattribute__(name)

        # Then lastly, if it is defined locally on the class we return the default output
        return default_output

    # This is essentially lifted straight out of the numpy docs
    def __array_ufunc__(self, ufunc, method, *inputs, out=None, **kwargs):  # pragma: no cover
        """np.ndarray subclassing compatibility.

        Ensures ufunc return MeasurementArray if they were MeasurementArray.
        Impl from examples on np.ndarray for subclassing whilst keeping ufunc compatibility.
        """
        args = []
        in_no = []
        for idx, input_ in enumerate(inputs):
            if isinstance(input_, MeasurementArray):
                in_no.append(idx)
                args.append(input_.view(np.ndarray))
            else:
                args.append(input_)

        outputs = out
        out_no = []
        if outputs:
            out_args = []
            for j, output in enumerate(outputs):
                if isinstance(output, MeasurementArray):
                    out_no.append(j)
                    out_args.append(output.view(np.ndarray))
                else:
                    out_args.append(output)
            kwargs["out"] = tuple(out_args)
        else:
            outputs = (None,) * ufunc.nout

        results = super().__array_ufunc__(ufunc, method, *args, **kwargs)
        if results is NotImplemented:
            return NotImplemented

        if method == "at":
            return

        if ufunc.nout == 1:
            results = (results,)

        results = tuple(
            (np.asarray(result).view(MeasurementArray) if output is None else output)
            for result, output in zip(results, outputs)
        )

        return results[0] if len(results) == 1 else results

    def __array_wrap__(self, out_arr, context=None, return_scalar=False):  # noqa: FBT002
        """np.ndarray subclassing compatibility."""
        return super().__array_wrap__(self, out_arr, context, return_scalar)
