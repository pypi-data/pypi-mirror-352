"""Module providing the StridedArrayFile class and any supporting code."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from mmap import ACCESS_READ, mmap
from pathlib import Path
from struct import Struct
from typing import ClassVar

from numpy import dtype, ndarray


class StridedArrayFile(Sequence):
    r"""A strided array file that can be read or written.

    A strided array file is a file that can contain multiple multi-dimensional
    arrays. The file format specification can be found in the `borehole.io
    Documentation`_.

    `StridedArrayFile` objects allow access to arrays in an existing file, or
    writing of arrays to a new file. To access arrays in an existing file, a
    `StridedArrayFile` provides a standard Python `Sequence` interface allowing
    iteration, index or slice based access. To write arrays to a new file, the
    write_ method can be used.

    File access is lazy. Creating an instance of a `StridedArrayFile` will not
    open the specified file. When writing a new file using write_, the file is
    created, data written to it and then it is immediately closed. When reading
    an existing file, the file opening is delayed until an array or file
    attribute is accessed, or open_ is called explicitly.

    Care must be taken as to when and how a strided array file is closed after
    reading. Files are memory mapped, and the array access provided uses this
    mapped data as a backing. This allows for huge arrays to be accessed without
    using any memory. Unfortunately, closing a `StridedArrayFile` while there
    are still arrays in scope relying on the mapped data will result in
    undefined and likely undesirable behaviour.

    A context manager is provided so a `StridedArrayFile` may be used
    with a `with` statement (`with StridedArrayFile('test.star') as file:`).
    The context manager will automatically close the file irrespective of what
    happens in the `with` block.

    Parameters
    ----------
    file_path : str or pathlib.Path
        The path to the strided array file to be read or written.

    Examples
    --------
    >>> a = np.arange(80).reshape((5, 2 8))
    >>> b = np.eye(10)
    >>> c = np.random.rand((1, 4, 2, 3))
    >>> data_file = StridedArrayFile("test_data.star")
    >>> data_file.write([a, b, c])

    Writes three arrays to a new strided array file.

    >>> assert np.array_equal(a, data_file[0])
    >>> assert np.array_equal(b, data_file[1])
    >>> assert np.array_equal(c, data_file[2])
    >>> data_file.close()

    Access the arrays from the file and ensure they match.

    >>> with StridedArrayFile('downloaded.star') as arrays:
    >>>     print(f"Downloaded file contains {len(arrays)} array(s).")
    >>>     for i, array in enumerate(arrays):
    >>>         print(f"Index {i}:\n{array}")
    Downloaded file contains 2 array(s).
    Index 0:
    [[1. 0. 0.]
     [0. 1. 0.]
     [0. 0. 1.]]
    Index 1:
    [0 1 2 3 4]

    .. _borehole.io Documentation: https://borehole.io/spec

    """

    @dataclass
    class Version:
        """StAr Version Struct."""

        major: int
        minor: int

    MAGIC_BYTES = b"StAr"
    CURRENT_VERSION = Version(0, 2)
    CURRENT_VERSION_BYTES = Struct("<BB").pack(CURRENT_VERSION.major, CURRENT_VERSION.minor)

    ELEMENT_TYPE_BYTES: ClassVar[dict] = {
        dtype("<b"): b"\x00",
        dtype("<B"): b"\x01",
        dtype("<i2"): b"\x02",
        dtype("<u2"): b"\x03",
        dtype("<i4"): b"\x04",
        dtype("<u4"): b"\x05",
        dtype("<i8"): b"\x06",
        dtype("<u8"): b"\x07",
        dtype("<f4"): b"\x08",
        dtype("<f8"): b"\x09",
    }
    ELEMENT_TYPE_DTYPES: ClassVar[dict] = {v: k for k, v in ELEMENT_TYPE_BYTES.items()}

    def __init__(self, file_path: str | Path):
        self.__file_path = Path(file_path)
        self.__file_pointer = None
        self.__file_mmap = None
        self.__version = None
        self.__arrays = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, value, traceback):
        self.close()

    def __getitem__(self, index: int) -> ndarray:
        if self.__arrays is None:
            self.open()
        return self.__arrays.__getitem__(index)

    def __len__(self) -> int:
        if self.__arrays is None:
            self.open()
        return self.__arrays.__len__()

    @property
    def path(self) -> Path:
        """Path to the strided array file."""
        return self.__file_path

    @property
    def version(self) -> Version:
        """Version: The file format version."""
        if self.__version is None:
            self.open()
        return self.__version

    def write(self, arrays: list[ndarray]):
        """Write a sequence of arrays to a new strided array file.

        Parameters
        ----------
        arrays : :obj:`list` of :obj:`ndarray`
            The arrays to write to the strided array file.

        """
        if self.__file_path.exists():
            message = f"File at '{self.__file_path}' already exists."
            raise FileExistsError(message)

        with open(self.__file_path, "wb") as file_pointer:
            # Write the preamble
            file_pointer.write(self.MAGIC_BYTES)
            file_pointer.write(self.CURRENT_VERSION_BYTES)
            file_pointer.write(Struct("<I").pack(len(arrays)))

            # Calculate the full header length, which will allow us to calculate
            # sensible offsets for each array.
            header_length = file_pointer.tell() + sum(13 + 16 * array.ndim for array in arrays)

            # Write array descriptors while keeping track of array start offsets.
            array_starts = []
            data_to = header_length
            for array in arrays:
                # Check the data type of the array to make sure we can handle it.
                if array.dtype not in self.ELEMENT_TYPE_BYTES:
                    message = f"Writing an array with an element data type of {array.dtype} is not supported."
                    raise ValueError(message)
                if array.dtype.alignment != array.dtype.itemsize:
                    message = "Writing an array with a non-contiguous element data type is not supported."
                    raise NotImplementedError(message)

                # Write the number of dimensions
                file_pointer.write(Struct("<I").pack(array.ndim))

                # Write element count for each dimension.
                for element_count in array.shape:
                    file_pointer.write(Struct("<Q").pack(element_count))

                # Calculate strides for a row-major, contiguous form of the array
                #
                # TODO: This doesn't currently set strides to 0 for dimensions
                # with just one element, as recommended by the spec. Should we
                # change the spec? I can't remember the reason we decided that.
                #
                # Actually, I just remembered. It was assumed that numpy did it,
                # so we should do it as well. In fact, numpy only does it when
                # you insert new dimensions via np.newaxis or via broadcasting.
                # In other cases it does not.
                contiguous_strides = [array.dtype.itemsize]
                for element_count in array.shape[-1:0:-1]:
                    contiguous_strides.append(contiguous_strides[-1] * element_count)
                contiguous_strides = contiguous_strides[::-1]

                # Write these strides into the array descriptor
                for stride in contiguous_strides:
                    file_pointer.write(Struct("<q").pack(stride))

                # Write the element data type.
                file_pointer.write(self.ELEMENT_TYPE_BYTES[array.dtype])

                # Calculate an appropriate offset, write it, add it to our list
                # of start offsets and update where data will be written to.
                array_start = (data_to + array.dtype.alignment - 1) // array.dtype.alignment * array.dtype.alignment
                file_pointer.write(Struct("<Q").pack(array_start))
                array_starts.append(array_start)
                data_to += array.size * array.itemsize

            # Finally, write the actual array data.
            for array_start, array in zip(array_starts, arrays):
                file_pointer.seek(array_start)
                array.tofile(file_pointer)

    def open(self):
        """Explicitly opens an existing strided array file.

        In general, it isn't necessary to call this method, as it is called
        automatically whenever any arrays or file attributes are accessed.
        """
        try:
            # Memory map the file in readonly mode
            self.__file_pointer = open(self.__file_path, "rb")  # noqa: SIM115
            self.__file_mmap = mmap(self.__file_pointer.fileno(), 0, access=ACCESS_READ)

            # Check the magic bytes
            if self.__file_mmap[:4] != self.MAGIC_BYTES:
                message = f"File at '{self.__file_path}' is not a valid strided array file"
                raise ValueError(message)  # noqa: TRY301

            # Check the version of the file
            self.__version = self.Version(*Struct("<BB").unpack_from(self.__file_mmap, 4))
            if self.__version != self.CURRENT_VERSION:
                message = (
                    f"Reading v{self.__version.major}.{self.__version.minor} strided array files is not supported."
                )
                raise NotImplementedError(message)  # noqa: TRY301

            # Get the number of arrays in the file
            count = Struct("<I").unpack_from(self.__file_mmap, 6)[0]

            # Read array descriptors and create views for arrays
            self.__arrays = []
            offset = 10
            for _ in range(count):
                dimensions = Struct("<I").unpack_from(self.__file_mmap, offset)[0]

                struct = Struct(f"<{dimensions}Q{dimensions}q1sQ")
                unpacked = struct.unpack_from(self.__file_mmap, offset + 4)

                shape = unpacked[:dimensions]
                strides = unpacked[dimensions:-2]
                element_type = self.ELEMENT_TYPE_DTYPES[unpacked[-2]]
                start = unpacked[-1]

                array = ndarray(shape, element_type, self.__file_mmap, start, strides)
                self.__arrays.append(array)

                offset += 4 + struct.size
        except Exception:
            self.close()
            raise

    def close(self):
        """Close a strided array file.

        This can be called multiple times without any side effects. Care should
        be taken to ensure that there are no arrays still using the data from
        the strided array file before calling this method.
        """
        if self.__version is not None:
            self.__version = None
        if self.__arrays is not None:
            self.__arrays = None
        if self.__file_mmap:
            self.__file_mmap.close()
            self.__file_mmap = None
        if self.__file_pointer:
            self.__file_pointer.close()
            self.__file_pointer = None
