# PyBEST: Pythonic Black-box Electronic Structure Tool
# Copyright (C) 2016-- The PyBEST Development Team
#
# This file is part of PyBEST.
#
# PyBEST is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# PyBEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
# --
#
# **Changelog:**
# - **11/2024:** File added by Lena Szczuczko.
#
# =====================================================
# Imports
# -----------------------------------------------------
from __future__ import annotations

from typing import Any

import h5py
import numpy as np  # For numerical operations with arrays and matrices.
from numpy.typing import NDArray

# PyBEST-specific imports
from pybest.exceptions import ArgumentError  # Custom exception handling.
from pybest.linalg.base import (
    EightIndex,  # Base class for eight-index tensors.
)
from pybest.log import (
    log,  # Logging utility for tracking execution and errors.
)

# Dense index classes
from .dense_five_index import DenseFiveIndex
from .dense_four_index import DenseFourIndex
from .dense_one_index import DenseOneIndex
from .dense_six_index import DenseSixIndex
from .dense_three_index import DenseThreeIndex
from .dense_two_index import DenseTwoIndex


class DenseEightIndex(EightIndex):
    """This class extends the functionality to support eight-dimensional matrices.

    Args:
        EightIndex (EightIndex): Dense matrix representation of an eight-dimensional tensor.

    Raises:
        ValueError: If the input dimensions are not consistent with the eight-index structure.
        ArgumentError: If an invalid argument is provided to a method.
        ArgumentError: If the basis sizes do not match across operations.
        ArgumentError: If the tensor dimensions are incompatible.
        ArgumentError: If the operation requested is not supported.
        ArgumentError: If the input data is malformed or incomplete.
        NotImplementedError: If a requested method is not yet implemented.
        ArgumentError: If an unsupported label is encountered.
    """

    # Identification attribute for class type detection
    dense_eight_identifier: bool = True

    # Constructor
    def __init__(
        self,
        nbasis: int,
        nbasis1: int | None = None,
        nbasis2: int | None = None,
        nbasis3: int | None = None,
        nbasis4: int | None = None,
        nbasis5: int | None = None,
        nbasis6: int | None = None,
        nbasis7: int | None = None,
        label: str = "",
    ) -> None:
        """Initialize a DenseEightIndex object.

        Args:
            nbasis (int): The number of basis functions in the first dimension.
            nbasis1-7 (int | None, optional): The number of basis functions for each dimension. Defaults to `nbasis` if not provided.
            label (str, optional): The name (label) of the instance to be created. Defaults to an empty string.

        Attributes created:
            _array (np.ndarray): The underlying NumPy array inititalized to zeros representing the eight-index tensor.
            _label (str): The label assigned to the instance.
        """
        # Default optional basis dimensions to `nbasis` if not provided
        if nbasis1 is None:
            nbasis1 = nbasis
        if nbasis2 is None:
            nbasis2 = nbasis
        if nbasis3 is None:
            nbasis3 = nbasis
        if nbasis4 is None:
            nbasis4 = nbasis
        if nbasis5 is None:
            nbasis5 = nbasis
        if nbasis6 is None:
            nbasis6 = nbasis
        if nbasis7 is None:
            nbasis7 = nbasis

        # Initialize an 8D NumPy array
        self._array: NDArray[np.float64] = np.zeros(
            (
                nbasis,
                nbasis1,
                nbasis2,
                nbasis3,
                nbasis4,
                nbasis5,
                nbasis6,
                nbasis7,
            ),
            float,
        )

        # Assign the label
        self._label: str = label

        # Log memory usage for the array
        log.mem.announce(self._array.nbytes)

    #
    # Destructor
    #
    def __del__(self) -> None:
        """Destroy an instance of the DenseEightIndex class."""
        if log is not None:
            if hasattr(self, "_array"):
                log.mem.denounce(
                    self._array.nbytes
                )  # Corrected to use self._array
        if hasattr(self, "_array"):
            del self._array

    #
    # Methods from base class
    #

    def __check_init_args__(
        self,
        nbasis: int,
        nbasis1: int | None = None,
        nbasis2: int | None = None,
        nbasis3: int | None = None,
        nbasis4: int | None = None,
        nbasis5: int | None = None,
        nbasis6: int | None = None,
        nbasis7: int | None = None,
    ) -> None:
        """Check if the current instance is compatible with the given constructor arguments.

        This method ensures that if any optional basis dimension is not
        provided, it defaults to the primary basis dimension. Additionally,
        it verifies that the initialized dimensions match the expected values
        for the current instance.

        Args:
            nbasis (int): The number of basis functions in the first dimension.
            nbasis1-7 (int, optional): The number of basis functions for each dimension. Defaults to `nbasis` if not provided.

        Procedures:
        - The method asserts that the provided `nbasis` and the corresponding arguments match the dimensions of the current instance (`self.nbasis`, `self.nbasis1`, etc.).
        - If any mismatch occurs, an `AssertionError` will be raised.
        - If the assertions pass, no action is taken, and the method returns `None`.
        """
        if nbasis1 is None:
            nbasis1 = nbasis
        if nbasis2 is None:
            nbasis2 = nbasis
        if nbasis3 is None:
            nbasis3 = nbasis
        if nbasis4 is None:
            nbasis4 = nbasis
        if nbasis5 is None:
            nbasis5 = nbasis
        if nbasis6 is None:
            nbasis6 = nbasis
        if nbasis7 is None:
            nbasis7 = nbasis

        # Ensure the dimensions of the current instance match the expected ones
        assert nbasis == self.nbasis
        assert nbasis1 == self.nbasis1
        assert nbasis2 == self.nbasis2
        assert nbasis3 == self.nbasis3
        assert nbasis4 == self.nbasis4
        assert nbasis5 == self.nbasis5
        assert nbasis6 == self.nbasis6
        assert nbasis7 == self.nbasis7

    def __eq__(self, other: Any) -> bool:
        """Check if two DenseEightIndex objects are equal

        Args:
            other (DenseEightIndex): Another object (expected to be a DenseEightIndex instance).

        Returns:
            bool: True if all basis values of both objects are equal, otherwise False.
        """
        return (
            other.nbasis
            == self.nbasis  # Check if the 'nbasis' values are equal.
            and other.nbasis1
            == self.nbasis1  # Check if the 'nbasis1' values are equal.
            and other.nbasis2
            == self.nbasis2  # Check if the 'nbasis2' values are equal.
            and other.nbasis3
            == self.nbasis3  # Check if the 'nbasis3' values are equal.
            and other.nbasis4
            == self.nbasis4  # Check if the 'nbasis4' values are equal.
            and other.nbasis5
            == self.nbasis5  # Check if the 'nbasis5' values are equal.
            and other.nbasis6
            == self.nbasis6  # Check if the 'nbasis6' values are equal.
            and other.nbasis7
            == self.nbasis7  # Check if the 'nbasis7' values are equal.
            and np.array_equal(
                other.array, self.array
            )  # Check if the 'array' values are equal.
        )

    @classmethod
    def from_hdf5(cls, grp: h5py) -> DenseEightIndex:
        """Create a DenseEightIndex instance from an HDF5 group.

        Args:
            grp (h5py): HDF5 group containing the data.

        Returns:
            DenseEightIndex: Created instance filled with data from the HDF5 group.
        """
        # Extracting dimensions from the stored data.
        nbasis = grp["array"].shape[0]
        nbasis1 = grp["array"].shape[1]
        nbasis2 = grp["array"].shape[2]
        nbasis3 = grp["array"].shape[3]
        nbasis4 = grp["array"].shape[4]
        nbasis5 = grp["array"].shape[5]
        nbasis6 = grp["array"].shape[6]
        nbasis7 = grp["array"].shape[7]

        # Extract label from the attributes.
        label = grp.attrs["label"]

        # Create the DenseEightIndex instance.
        result = cls(
            nbasis,
            nbasis1,
            nbasis2,
            nbasis3,
            nbasis4,
            nbasis5,
            nbasis6,
            nbasis7,
            label,
        )

        # Load the stored array data.
        grp["array"].read_direct(result.array)

        return result

    def to_hdf5(self, grp: h5py.Group) -> None:
        """Save the DenseEightIndex instance to an HDF5 group

        Args:
            grp (h5py.Group): HDF5 group to store the data in.

        Returns:
            None
        """
        # Store the class name as an attribute.
        grp.attrs["class"] = self.__class__.__name__

        # Store the array data.
        grp["array"] = self.array

        # Store the label attribute.
        grp.attrs["label"] = self._label

    def new(self) -> DenseEightIndex:
        """Create a new DenseEightIndex instance with the same properties.

        Returns:
            DenseEightIndex: Creates a new DenseEightIndex instance with the same properties as the current instance.
        """
        return DenseEightIndex(
            self.nbasis,
            self.nbasis1,
            self.nbasis2,
            self.nbasis3,
            self.nbasis4,
            self.nbasis5,
            self.nbasis6,
            self.nbasis7,
        )

    @staticmethod
    def einsum_index(script: str) -> str | ValueError:
        """Return indices to numpy.einsum summation.

        Args:
            script (str): A string of length 8 describing the indices for the numpy.einsum summation.

        Raises:
            ValueError: If the input script is not a string of exactly length 8,
                indicating invalid indices for the numpy.einsum summation.

        Returns:
            str | ValueError: Returns indices to numpy.einsum summation.
                If the input script is not a string of exactly length 8,
                indicating invalid indices for the numpy.einsum summation, a ValueError is raised.
        """
        if not len(script) == 8 and isinstance(script, str):
            raise ValueError("The script must be a string of length 8.")
        return script

    @property
    def nbasis(self) -> int:
        """The number of basis functions in the first dimension of the array.

        Returns:
            int: The number of basis functions in the first dimension of the array.
        """
        return self.array.shape[0]

    @property
    def nbasis1(self) -> int:
        """The number of basis functions in the second dimension of the array.

        Returns:
            int: The number of basis functions in the second dimension of the array.
        """
        return self.array.shape[1]

    @property
    def nbasis2(self) -> int:
        """The number of basis functions in the third dimension of the array.

        Returns:
            int: The number of basis functions in the third dimension of the array.
        """
        return self.array.shape[2]

    @property
    def nbasis3(self) -> int:
        """The number of basis functions in the fourth dimension of the array.

        Returns:
            int: The number of basis functions in the fourth dimension of the array.
        """
        return self.array.shape[3]

    @property
    def nbasis4(self) -> int:
        """The number of basis functions in the fifth dimension of the array.

        Returns:
            int: The number of basis functions in the fifth dimension of the array.
        """
        return self.array.shape[4]

    @property
    def nbasis5(self) -> int:
        """The number of basis functions in the sixth dimension of the array.

        Returns:
            int: The number of basis functions in the sixth dimension of the array.
        """
        return self.array.shape[5]

    @property
    def nbasis6(self) -> int:
        """The number of basis functions in the seventh dimension of the array.

        Returns:
            int: The number of basis functions in the seventh dimension of the array.
        """
        return self.array.shape[6]

    @property
    def nbasis7(self) -> int:
        """The number of basis functions in the eighth dimension of the array.

        Returns:
           int: The number of basis functions in the eighth dimension of the array.
        """
        return self.array.shape[7]

    @property
    def shape(self) -> tuple:
        """The shape of the array as a tuple.

        Returns:
            tuple: The shape of the array as a tuple.
        """
        return self.array.shape

    @property
    def array(self) -> NDArray[np.float64]:
        """The numpy array representing the data.

        Returns:
            np.ndarray: The numpy array representing the data.
        """
        return self._array

    @array.setter
    def array(self, ndarray: NDArray[np.float64]) -> None:
        """Setter for the `array` attribute, ensuring it is an 8D numpy array.

        Args:
            ndarray (np.ndarray): The 8D numpy array to be set as the data.

        Raises:
            ArgumentError: If the array is not an 8D array, the ArgumentError is raised.
        """
        if not ndarray.ndim == 8:
            raise ArgumentError("Only 8D array can be set.")
        self._array = ndarray

    @property
    def arrays(self) -> list[NDArray[np.float64]]:
        """Return a list containing the numpy array representing the data.

        Returns:
            list[NDArray[np.float64]]: A list containing the numpy array representing the data.
        """
        return [self.array]

    @property
    def label(self) -> str:
        """Return the label of the instance.

        Returns:
            str: The label of the instance.
        """
        return self._label

    @label.setter
    def label(self, label: str) -> None:
        """Set the label of the instance.

        Args:
            label (str): The label of the instance.
        """
        self._label = label

    def _check_new_init_args(self, other: EightIndex) -> None:
        """Check if the other instance has the same init arguments.

        Args:
            other (EightIndex): The other instance to compare initialization arguments with.
        """
        other.__check_init_args__(
            self.nbasis,
            self.nbasis1,
            self.nbasis2,
            self.nbasis3,
            self.nbasis4,
            self.nbasis5,
            self.nbasis6,
            self.nbasis7,
        )

    def clear(self) -> None:
        """Clear the array by setting all elements to zero."""
        self.array[:] = 0.0

    def replace_array(
        self, value: DenseEightIndex | NDArray[np.float64]
    ) -> None:
        """Replace the array with the given array.

        Args:
            value (DenseEightIndex | np.ndarray): The array to replace the data with.
                If the given value is a DenseEightIndex, it replaces the data with the array of the DenseEightIndex.
                If the given value is a numpy array, it is used as the new data.

        Raises:
            ArgumentError: If the given value is not a DenseEightIndex or a numpy array, an ArgumentError is raised.
        """
        if isinstance(value, DenseEightIndex):
            self.array = value.array
        elif isinstance(value, np.ndarray):
            self.array = value
        else:
            raise ArgumentError(
                f"Do not know how to assign object of type {type(value)}."
            )

    def copy(
        self,
        begin0: int = 0,
        end0: int | None = None,
        begin1: int = 0,
        end1: int | None = None,
        begin2: int = 0,
        end2: int | None = None,
        begin3: int = 0,
        end3: int | None = None,
        begin4: int = 0,
        end4: int | None = None,
        begin5: int = 0,
        end5: int | None = None,
        begin6: int = 0,
        end6: int | None = None,
        begin7: int = 0,
        end7: int | None = None,
    ) -> DenseEightIndex:
        """Return a copy of the current instance, possibly with sliced arrays.

        The range of the slice is given by the begin and end arguments. If an
        end argument is not given, the slice goes up to the end of the range.
        If a begin argument is not given, the slice starts at the beginning of
        the range.

        Args:
            begin0 (int, optional): The starting index for the slice along the zeroth axis. Defaults to 0.
            end0 (int | None, optional): The ending index for the slice along the zeroth axis. Defaults to None.
            begin1 (int, optional): The starting index for the slice along the first axis. Defaults to 0.
            end1 (int | None, optional): The ending index for the slice along the first axis. Defaults to None.
            begin2 (int, optional): The starting index for the slice along the second axis. Defaults to 0.
            end2 (int | None, optional): The ending index for the slice along the second axis. Defaults to None.
            begin3 (int, optional): The starting index for the slice along the third axis. Defaults to 0.
            end3 (int | None, optional): The ending index for the slice along the third axis. Defaults to None.
            begin4 (int, optional): The starting index for the slice along the fourth axis. Defaults to 0.
            end4 (int | None, optional): The ending index for the slice along the fourth axis. Defaults to None.
            begin5 (int, optional): The starting index for the slice along the fifth axis. Defaults to 0.
            end5 (int | None, optional): The ending index for the slice along the fifth axis. Defaults to None.
            begin6 (int, optional): The starting index for the slice along the sixth axis. Defaults to 0.
            end6 (int | None, optional): The ending index for the slice along the sixth axis. Defaults to None.
            begin7 (int, optional): The starting index for the slice along the seventh axis. Defaults to 0.
            end7 (int | None, optional): The ending index for the slice along the seventh axis. Defaults to None.

        Returns:
            DenseEightIndex: Copy of the current instance with possibly sliced arrays.
        """
        # Adjust the end indices if necessary to ensure they are within bounds
        end0, end1, end2, end3, end4, end5, end6, end7 = self.fix_ends(
            end0, end1, end2, end3, end4, end5, end6, end7
        )

        # If any 'endX' is None, set it to the corresponding size from the array
        end0 = end0 if end0 is not None else self.array.shape[0]
        end1 = end1 if end1 is not None else self.array.shape[1]
        end2 = end2 if end2 is not None else self.array.shape[2]
        end3 = end3 if end3 is not None else self.array.shape[3]
        end4 = end4 if end4 is not None else self.array.shape[4]
        end5 = end5 if end5 is not None else self.array.shape[5]
        end6 = end6 if end6 is not None else self.array.shape[6]
        end7 = end7 if end7 is not None else self.array.shape[7]

        # Create a new DenseEightIndex instance with the dimensions of the selected subblock
        result = DenseEightIndex(
            end0 - begin0,
            end1 - begin1,
            end2 - begin2,
            end3 - begin3,
            end4 - begin4,
            end5 - begin5,
            end6 - begin6,
            end7 - begin7,
        )

        # Copy the selected portion of the original array to the new instance
        result.array[:] = self.array[
            begin0:end0,
            begin1:end1,
            begin2:end2,
            begin3:end3,
            begin4:end4,
            begin5:end5,
            begin6:end6,
            begin7:end7,
        ]

        # Copy the label from the original instance
        result.label = self._label

        return result

    def reshape(
        self, shape: list[int]
    ) -> (
        DenseEightIndex
        | DenseSixIndex
        | DenseFiveIndex
        | DenseFourIndex
        | DenseThreeIndex
        | DenseTwoIndex
        | DenseOneIndex
    ):
        """Reshape the array to the given shape and returns a new instance with the reshaped array.

        Args:
            self (DenseEightIndex): The instance whose array is to be reshaped.
            shape (list[int]): The new shape for the array.

        Raises:
            ArgumentError: If the total number of elements in the new shape does not match the original array,
                an ArgumentError is raised.
            ArgumentError: If the shape argument is empty, an ArgumentError is raised.

        Returns:
            DenseEightIndex: A DenseEightIndex instance with the reshaped array.
        """
        # Ensure that the shape argument is not empty
        if len(shape) == 0:
            raise ArgumentError("No array shape given.")

        # Check if the total number of elements in the new shape matches the original array
        if np.prod(shape) != np.prod(self.array.shape):
            raise ArgumentError(
                "The total number of elements in the new shape must match the original array."
            )

        out: (
            DenseEightIndex
            | DenseSixIndex
            | DenseFiveIndex
            | DenseFourIndex
            | DenseThreeIndex
            | DenseTwoIndex
            | DenseOneIndex
        )

        # Create the appropriate instance based on the number of dimensions
        if len(shape) == 1:
            out = DenseOneIndex(shape[0])
        elif len(shape) == 2:
            out = DenseTwoIndex(shape[0], shape[1])
        elif len(shape) == 3:
            out = DenseThreeIndex(shape[0], shape[1], shape[2])
        elif len(shape) == 4:
            out = DenseFourIndex(shape[0], shape[1], shape[2], shape[3])
        elif len(shape) == 5:
            out = DenseFiveIndex(
                shape[0], shape[1], shape[2], shape[3], shape[4]
            )
        elif len(shape) == 6:
            out = DenseSixIndex(
                shape[0], shape[1], shape[2], shape[3], shape[4], shape[5]
            )
        elif len(shape) == 8:
            out = DenseEightIndex(
                shape[0],
                shape[1],
                shape[2],
                shape[3],
                shape[4],
                shape[5],
                shape[6],
                shape[7],
            )
        else:
            raise ArgumentError(
                f"Reshaping to {len(shape)} dimensions is not supported."
            )

        # Reshape the array using NumPy and assign it to the new instance
        out.array[:] = np.reshape(self.array, shape, order="C")

        return out

    def assign(
        self,
        other: DenseEightIndex | NDArray[np.float64] | float,
        ind: list[int] | None | tuple[np.ndarray, ...] | None = None,
        begin8: int = 0,
        end8: int | None = None,
    ) -> None:
        """Assign the value of the given object to this instance.

        Args:
            other (DenseEightIndex | np.ndarray | float): The value to assign to this instance.
                It can be a DenseEightIndex, a NumPy ndarray, or a float.
            ind (list[int] | None | tuple[np.ndarray, ...] | None, optional): The index at which to assign the value.
                It can be a list of integers, a tuple of NumPy ndarrays, or None. Defaults to None.
            begin8 (int, optional): The starting index for the assignment. Defaults to 0.
            end8 (int | None, optional): The ending index for the assignment.
                If None, the assignment goes to the end. Defaults to None.

        Raises:
            NotImplementedError: Raised if the method is not implemented.
            ArgumentError: Raised if an invalid argument is provided.
        """
        # Type validation for 'other', ensuring it's one of the supported types
        self.check_type(
            "other",
            other,
            DenseEightIndex,
            DenseSixIndex,
            DenseFiveIndex,
            DenseFourIndex,
            DenseThreeIndex,
            DenseTwoIndex,
            DenseOneIndex,
            np.ndarray,
            float,
        )

        # Case 1: 'other' is a DenseEightIndex object
        if isinstance(other, DenseEightIndex):
            if ind is not None:
                self.array[tuple(ind)] = other.array
            else:
                self.array[:] = other.array

        # Case 2: 'other' is a float
        elif isinstance(other, float):
            if ind is not None:
                self.array[tuple(ind)] = other
            else:
                self.array[:] = other

        # Case 3: 'other' is a numpy ndarray
        elif isinstance(other, np.ndarray):
            if other.shape == self.shape:
                self.array[:] = other  # Direct assignment if shapes match
            elif ind is not None:
                self.array[ind] = other  # Assignment with indices if provided
            else:
                self.array[:] = other.reshape(
                    (
                        self.nbasis,
                        self.nbasis1,
                        self.nbasis2,
                        self.nbasis3,
                        self.nbasis4,
                        self.nbasis5,
                        self.nbasis6,
                        self.nbasis7,
                    )
                )  # Reshape 'other' to match the current shape before assigning

        # Case 4: 'other' is an instance of DenseSixIndex, DenseFiveIndex, DenseFourIndex, DenseThreeIndex, or DenseTwoIndex
        elif isinstance(
            other,
            (
                DenseSixIndex,
                DenseFiveIndex,
                DenseFourIndex,
                DenseThreeIndex,
                DenseTwoIndex,
            ),
        ):
            if ind is not None:
                raise NotImplementedError(
                    "This functionality is not yet implemented"
                )
            else:
                self.array[:] = other.array.reshape(
                    (
                        self.nbasis,
                        self.nbasis1,
                        self.nbasis2,
                        self.nbasis3,
                        self.nbasis4,
                        self.nbasis5,
                        self.nbasis6,
                        self.nbasis7,
                    )
                )

        # Case 5: 'other' is a DenseOneIndex
        elif isinstance(other, DenseOneIndex):
            if ind is not None:
                self.array[ind] = other.array[begin8:end8]
            else:
                self.array[:] = other.array[begin8:end8].reshape(
                    (
                        self.nbasis,
                        self.nbasis1,
                        self.nbasis2,
                        self.nbasis3,
                        self.nbasis4,
                        self.nbasis5,
                        self.nbasis6,
                        self.nbasis7,
                    )
                )

        # Case 6: Unsupported type for 'other'
        else:
            raise ArgumentError(
                f"Do not know how to assign object of type {type(other)}."
            )

    def randomize(self) -> None:
        """Randomize the elements of the array."""
        self.array[:] = np.random.normal(0, 1, self.shape)

    def permute_basis(self, permutation: NDArray[np.integer]) -> None:
        """Permute the basis of the array according to the given permutation.

        Args:
            permutation (np.ndarray): A 1D array of indices.
        """
        self.array[:] = self.array.take(permutation, axis=0)
        self.array[:] = self.array.take(permutation, axis=1)
        self.array[:] = self.array.take(permutation, axis=2)
        self.array[:] = self.array.take(permutation, axis=3)
        self.array[:] = self.array.take(permutation, axis=4)
        self.array[:] = self.array.take(permutation, axis=5)
        self.array[:] = self.array.take(permutation, axis=6)
        self.array[:] = self.array.take(permutation, axis=7)

    def change_basis_signs(self, signs: np.ndarray) -> None:
        """Change the signs of the elements of the array according to the given signs. To be implemented.

        Args:
            signs (np.ndarray): A numpy array with sign changes indicated by +1 and -1.

        Raises:
            NotImplementedError: This method is to be implemented and will always raise an error.
        """
        raise NotImplementedError

    def iscale(self, factor: float) -> None:
        """In-place multiplication with a scalar for an eight-index array

        Args:
            factor (float): The factor by which to scale the elements of the array.
        """
        self.check_type("factor", factor, float, int)
        self.array *= factor

    def get_element(
        self, i: int, j: int, k: int, l: int, m: int, n: int, o: int, p: int
    ) -> float:
        """Return the element at the given indices.

        Args:
            i (int): The first index.
            j (int): The second index.
            k (int): The third index.
            l (int): The fourth index.
            m (int): The fifth index.
            n (int): The sixth index.
            o (int): The seventh index.
            p (int): The eighth index.


        Returns:
            float: The element at the given indices.
        """
        return self.array[i, j, k, l, m, n, o, p]

    def set_element(
        self,
        i: int,
        j: int,
        k: int,
        l: int,
        m: int,
        n: int,
        o: int,
        p: int,
        value: float,
    ) -> None:
        """Set the element at the given indices to the given value.

        Args:
            i (int): The first index.
            j (int): The second index.
            k (int): The third index.
            l (int): The fourth index.
            m (int): The fifth index.
            n (int): The sixth index.
            o (int): The seventh index.
            p (int): The eighth index.
            value (float): The value to which the element at the given indices should be set.
        """
        self.array[i, j, k, l, m, n, o, p] = value

    def itranspose(
        self,
        transpose: None
        | (tuple[int, int, int, int, int, int, int, int]) = None,
    ) -> None:
        """Transpose the array according to the specified order.

        Args:
            transpose (None | tuple[int, int, int, int, int, int, int, int], optional):
                The order to transpose the array. Defaults to None, which transposes the array
                using the default order (1, 0, 3, 2, 5, 4, 7, 6).
        """
        if transpose is None:
            transpose = (1, 0, 3, 2, 5, 4, 7, 6)
        self.array = self.array.transpose(transpose)

    def sum(self) -> float:
        """Return the sum of all elements"""
        return float(np.sum(self.array))

    def iadd_transpose(
        self,
        transpose: tuple[int],
        other: DenseEightIndex | None = None,
        factor: float = 1.0,
    ) -> None:
        """In-place addition of transpose for an eight-index array.

        Args:
            transpose (tuple[int]): The order to transpose the array.
            other (DenseEightIndex | None, optional): The other DenseEightIndex to add. Defaults to None.
            factor (float, optional): The scaling factor for the transposed array. Defaults to 1.0.
        """
        self.check_type("factor", factor, float, int)
        self.check_type("other", other, type(None), DenseEightIndex)
        if other is None:
            self.array[:] = (
                self.array + self.array.transpose(transpose) * factor
            )
        else:
            self.array[:] = (
                self.array + other.array.transpose(transpose) * factor
            )
