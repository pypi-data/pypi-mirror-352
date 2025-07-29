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

# Detailed changelog:
#
# 12/2024: File added by Lena Szczuczko.

from pathlib import Path

import h5py as h5
import numpy as np
import pytest

from pybest.linalg import (
    DenseEightIndex,
    DenseLinalgFactory,
)

#
# Utility functions
#


def get_forth_back(n: int) -> tuple[np.ndarray, np.ndarray]:
    """Generate two arrays, forth and back, which are mutually inverse permutations.

    Args:
        n (int): The size of the basis for the forth and back permutations.

    Returns:
        tuple[np.ndarray, np.ndarray]: A tuple containing two arrays, forth and back, which are mutually inverse permutations.
    """
    while True:
        forth = np.random.uniform(0, 1, n).argsort()  # Use 'n' for the size
        if not np.array_equal(
            forth, np.arange(n)
        ):  # Identity permutation check
            break
    back = np.zeros(n, int)  # Adjust size based on 'n'
    for i, j in enumerate(forth):
        back[j] = i
    return forth, back


#
# DenseLinalgFactory tests
#


@pytest.mark.parametrize("nb_size", [10, 2, 7])
def test_linalg_factory_constructors(nb_size: int) -> None:
    """Test the constructors of DenseLinalgFactory for different sizes.

    Args:
    nb_size (int): The size of the basis for the DenseLinalgFactory.
    """
    # Eight-index tests
    lf = DenseLinalgFactory(nb_size)

    # Test creation of DenseEightIndex object
    op8 = lf.create_eight_index()
    assert isinstance(op8, DenseEightIndex)

    # Test __check_init_args__ method for validation of arguments
    op8.__check_init_args__(nb_size)  # Check args directly on the op8 instance

    # Verify the nbasis and shape of the DenseEightIndex object
    assert op8.nbasis == nb_size
    assert op8.shape == (
        nb_size,
        nb_size,
        nb_size,
        nb_size,
        nb_size,
        nb_size,
        nb_size,
        nb_size,
    )

    # Test with nbasis provided
    op8 = lf.create_eight_index(nb_size)
    op8.__check_init_args__(nb_size)  # Check args on the new op8 instance
    assert op8.nbasis == nb_size


def test_linalg_objects_del() -> None:
    """Test if __del__ method of DenseEightIndex objects is working correctly."""
    lf = DenseLinalgFactory()
    with pytest.raises(TypeError):
        lf.create_eight_index()


def test_allocate_check_output() -> None:
    """Test allocate_check_output method of DenseLinalgFactory."""
    # EightIndex
    lf = DenseLinalgFactory(5)

    # Test with existing output
    original_output = lf.create_eight_index()
    returned_output = lf.allocate_check_output(
        original_output, (5, 5, 5, 5, 5, 5, 5, 5)
    )
    assert original_output is returned_output

    # Test when no output is passed
    returned_output = lf.allocate_check_output(None, (5, 5, 5, 5, 5, 5, 5, 5))
    assert isinstance(returned_output, DenseEightIndex)
    assert returned_output.shape == (
        5,
        5,
        5,
        5,
        5,
        5,
        5,
        5,
    )


#
# General eight index tests
#


def test_eight_index_einsum_index() -> None:
    """Test the einsum_index method of DenseEightIndex."""
    dlf = DenseLinalgFactory(2)
    dense = dlf.create_eight_index()
    assert dense.einsum_index("abcdefgh") == "abcdefgh"


def test_eight_index_arrays() -> None:
    """Test the arrays property of DenseEightIndex objects."""
    dlf = DenseLinalgFactory(2)
    dense = dlf.create_eight_index()
    arrays = dense.arrays
    assert len(arrays) == 1
    assert isinstance(arrays[0], np.ndarray)


def test_eight_index_hdf5(tmp_dir: str) -> None:
    """Test the serialization and deserialization of DenseEightIndex objects to and from HDF5 files using the to_hdf5 and from_hdf5 methods.

    Args:
        tmp_dir (str): Temporary directory path for storing the HDF5 file.
    """
    lf = DenseLinalgFactory(5)
    a = lf.create_eight_index()
    a.randomize()

    # Use Path to handle paths properly
    tmp_path = Path(tmp_dir) / "eight_index.h5"

    # Serialize to HDF5 and load back to verify consistency
    with h5.File(tmp_path, driver="core", backing_store=False, mode="w") as f:
        a.to_hdf5(f)
        b = DenseEightIndex.from_hdf5(f)
        assert a == b


def test_assign_one_index_to_eight_index() -> None:
    """Test assignment of a DenseOneIndex to a DenseEightIndex."""
    lf = DenseLinalgFactory()
    op_temp = lf.create_eight_index(3)
    op_temp.clear()

    # Create and assign to the eight_index
    op8 = lf.create_eight_index(3)
    op8._array[:] = np.random.uniform(0, 1, (3, 3, 3, 3, 3, 3, 3, 3))

    # Create and clear one_index
    op1 = lf.create_one_index(730)
    op1.clear()

    # Ensure error when assigning incompatible size
    with pytest.raises(ValueError):
        op8.assign(op1)

    # Assign compatible one_index and check for equality
    op1 = lf.create_one_index(6561)
    op1.clear()
    op8.assign(op1)

    # Ensure the arrays match
    assert np.all(op8._array == op_temp._array)


def test_assign_two_index_to_eight_index() -> None:
    """Test assignment of DenseTwoIndex to DenseEightIndex."""
    lf = DenseLinalgFactory()
    op_temp = lf.create_eight_index(2)
    op_temp.clear()
    op8 = lf.create_eight_index(2)
    op8._array[:] = np.random.uniform(0, 1, (2, 2, 2, 2, 2, 2, 2, 2))

    # Create a two-index object with compatible size, clear it, and assign it to the eight-index
    op2 = lf.create_two_index(16, 16)
    op2.clear()
    op8.assign(op2)
    assert np.all(op8._array == op_temp._array)

    # Create a two-index object with compatible size, clear it, and assign it to the eight-index
    op2 = lf.create_two_index(8, 32)
    op2.clear()
    op8.assign(op2)
    assert np.all(op8._array == op_temp._array)

    # Create a two-index object with incompatible size, clear it, and catch the ValueError
    op2 = lf.create_two_index(8, 10)
    op2.clear()
    with pytest.raises(ValueError):
        op8.assign(op2)


def test_assign_three_index_to_eight_index() -> None:
    """Test assignment of DenseThreeIndex to DenseEightIndex."""
    lf = DenseLinalgFactory()
    op_temp = lf.create_eight_index(3)
    op_temp.clear()
    op8 = lf.create_eight_index(3)
    op8._array[:] = np.random.uniform(0, 1, (3, 3, 3, 3, 3, 3, 3, 3))

    # Create a three-index with incompatible size
    op3 = lf.create_three_index(3, 3, 82)
    op3.clear()
    with pytest.raises(ValueError):
        op8.assign(op3)

    # Create a compatible three-index and assign
    op3 = lf.create_three_index(3, 9, 243)
    op3.clear()
    op8.assign(op3)

    # Assert the arrays match
    assert np.all(op8._array == op_temp._array)


def test_assign_four_index_to_eight_index() -> None:
    """Test assignment of DenseFourIndex to DenseEightIndex."""
    lf = DenseLinalgFactory()
    op_temp = lf.create_eight_index(2)
    op_temp.clear()
    op8 = lf.create_eight_index(2)
    op8._array[:] = np.random.uniform(0, 1, (2, 2, 2, 2, 2, 2, 2, 2))

    # Create a four-index with incompatible size
    op4 = lf.create_four_index(2, 4, 10, 8)
    op4.clear()
    with pytest.raises(ValueError):
        op8.assign(op4)

    # Create a compatible four-index and assign
    op4 = lf.create_four_index(2, 4, 4, 8)
    op4.clear()
    op8.assign(op4)

    # Assert the arrays match
    assert np.all(op8._array == op_temp._array)


def test_assign_five_index_to_eight_index() -> None:
    """Test assignment of DenseFiveIndex to DenseEightIndex."""
    lf = DenseLinalgFactory()
    op_temp = lf.create_eight_index(2)
    op_temp.clear()
    op8 = lf.create_eight_index(2)
    op8._array[:] = np.random.uniform(0, 1, (2, 2, 2, 2, 2, 2, 2, 2))

    # Create a five-index with incompatible size
    op5 = lf.create_five_index(2, 2, 2, 2, 5)
    op5.clear()
    with pytest.raises(ValueError):
        op8.assign(op5)

    # Create a compatible five-index and assign
    op5 = lf.create_five_index(2, 2, 4, 4, 4)
    op5.clear()
    op8.assign(op5)

    # Assert the arrays match
    assert np.all(op8._array == op_temp._array)


def test_assign_six_index_to_eight_index() -> None:
    """Test assignment of DenseSixIndex to DenseEightIndex."""
    lf = DenseLinalgFactory()
    op_temp = lf.create_eight_index(3)
    op_temp.clear()
    op8 = lf.create_eight_index(3)
    op8._array[:] = np.random.uniform(0, 1, (3, 3, 3, 3, 3, 3, 3, 3))

    # Create and clear a six-index object with incompatible size
    op6 = lf.create_six_index(3)
    op6._array[:] = np.random.uniform(0, 1, (3, 3, 3, 3, 3, 3))
    op6.clear()

    with pytest.raises(ValueError):
        op8.assign(op6)

    # Create and clear a six-index object with compatible size
    op6 = lf.create_six_index(3, 3, 3, 3, 9, 9)
    op6.clear()
    op8.assign(op6)

    # Assert the arrays match
    assert np.all(op8._array == op_temp._array)


def test_assign_eight_index_to_eight_index() -> None:
    """Test assignment of DenseEightIndex to DenseEightIndex."""
    lf = DenseLinalgFactory()
    op_temp = lf.create_eight_index(4)
    op_temp.clear()
    op8 = lf.create_eight_index(4)
    op8._array[:] = np.random.uniform(0, 1, (4, 4, 4, 4, 4, 4, 4, 4))

    # Create and initialize a second eight-index object
    op8_copy = lf.create_eight_index(4)
    op8_copy._array[:] = np.random.uniform(0, 1, (4, 4, 4, 4, 4, 4, 4, 4))

    # Clear the second eight-index object and assign it to the first
    op8_copy.clear()
    op8.assign(op8_copy)

    # Assert the arrays match
    assert np.all(op8._array == op_temp._array)


def test_assign_fragment_raw_array_to_eight_index() -> None:
    """Test assigning a fragment of a raw array to an eight-index object."""
    lf = DenseLinalgFactory()
    op1 = lf.create_eight_index(2)
    op2 = lf.create_eight_index(2)
    op1.randomize()
    op2.assign(op1)

    # Create a one-index object and clear it
    op3 = lf.create_one_index(2)
    op3.clear()

    # Create indices for the diagonal of a 2x2x2x2x2x2x2x2 array
    diagonal_indices = np.diag_indices(2, 8)

    # Modify the diagonal elements of the first eight-index object
    op1._array[diagonal_indices] = 0

    # Assign fragment from one-index to eight-index using the diagonal indices
    op2.assign(op3.array, diagonal_indices)

    # Assert the arrays are the same after the assignment
    assert np.all(op1._array == op2._array)

    # Assert specific diagonal elements are set to 0
    assert (
        op2.get_element(0, 0, 0, 0, 0, 0, 0, 0) == 0
        and op2.get_element(1, 1, 1, 1, 1, 1, 1, 1) == 0
    )


def test_assign_fragment_one_index_to_eight_index() -> None:
    """Test assigning a fragment of a one-index object to an eight-index object."""
    lf = DenseLinalgFactory()
    op1 = lf.create_eight_index(2)
    op2 = lf.create_eight_index(2)
    op1.randomize()
    op2.assign(op1)

    # Create a one-index object and clear it
    op3 = lf.create_one_index(2)
    op3.clear()

    # Create indices for the diagonal of a 2x2x2x2x2x2x2x2 array
    diagonal_indices = np.diag_indices(2, 8)

    # Modify the diagonal elements of the first eight-index object
    op1._array[diagonal_indices] = 0

    # Assign fragment from one-index to eight-index using the diagonal indices
    op2.assign(op3, diagonal_indices)

    # Assert the arrays are the same after the assignment
    assert np.all(op1._array == op2._array)

    # Assert specific diagonal elements are set to 0
    assert (
        op2.get_element(0, 0, 0, 0, 0, 0, 0, 0) == 0
        and op2.get_element(1, 1, 1, 1, 1, 1, 1, 1) == 0
    )


def test_assign_fragment_two_index_to_eight_index_ravel() -> None:
    """Test assigning a fragment of a two-index object to an eight-index object."""
    lf = DenseLinalgFactory()
    op1 = lf.create_eight_index(4)
    op2 = lf.create_eight_index(4)
    op1.randomize()
    op2.assign(op1)

    # Create a two-index object and clear it
    op3 = lf.create_two_index(2)
    op3.clear()

    # Create indices for the diagonal of a 4x4x4x4x4x4x4x4 array
    diagonal_indices = np.diag_indices(4, 8)

    # Modify the diagonal elements of the first eight-index object
    op1._array[diagonal_indices] = 0

    # Assign fragment from raveled two-index to eight-index using the diagonal indices
    op2.assign(op3.ravel(), diagonal_indices)

    # Assert the arrays are the same after the assignment
    assert np.all(op1._array == op2._array)

    # Assert specific diagonal elements are set to 0
    assert (
        op2.get_element(0, 0, 0, 0, 0, 0, 0, 0) == 0
        and op2.get_element(3, 3, 3, 3, 3, 3, 3, 3) == 0
    )


def test_assign_float_to_eight_index() -> None:
    """Test assigning a float value to all elements of an eight-index object."""
    lf = DenseLinalgFactory()

    # Creating and randomizing an eight-index object
    op1 = lf.create_eight_index(2)
    op1.randomize()

    # Assign a float value to all elements
    op1.assign(1.55)

    # Check if all elements are assigned correctly
    assert np.all(op1._array == 1.55)

    # Testing with indices
    op2 = lf.create_eight_index(4)
    op2.randomize()

    # Set specific element using set_element method
    op2.set_element(3, 3, 3, 3, 3, 3, 3, 3, 10)

    # Generate indices for assignment
    indices = np.indices((2, 2, 2, 2, 2, 2, 2, 2))

    # Assign a float value to specific indices
    op2.assign(0.5, tuple(indices))

    # Check if specific elements are correctly assigned
    assert (
        op2.get_element(0, 0, 0, 0, 0, 0, 0, 0) == 0.5
        and op2.get_element(1, 0, 1, 0, 1, 1, 1, 1) == 0.5
        and op2.get_element(3, 3, 3, 3, 3, 3, 3, 3) == 10.0
    )


@pytest.mark.parametrize("args", [(None,), (4,)])
def test_eight_index_copy_new_randomize_clear_copy(args) -> None:
    """Test the behavior of copying, randomizing, clearing, and creating new eight-index objects."""
    lf = DenseLinalgFactory(5)

    # Create and randomize an eight-index object
    a = lf.create_eight_index(*args)
    b = a.copy()
    b.randomize()

    # Assert that the copy is not equal to the original after randomization
    assert a != b

    # Create another copy and check if it matches the randomized copy
    c = b.copy()
    new_instance = c.new()
    new_instance.__check_init_args__(
        b.nbasis,
        b.nbasis1,
        b.nbasis2,
        b.nbasis3,
        b.nbasis4,
        b.nbasis5,
        b.nbasis6,
        b.nbasis7,
    )
    assert b == c

    # Create a new eight-index object and assert it equals the original
    d = c.new()
    assert a == d

    # Randomize the copy again and test subarray slicing
    b.randomize()
    e = b.copy(0, 1, 2, 4, 2)
    assert np.all(e._array == b._array[:1, 2:4, 2:])

    # Create a copy and ensure it matches the randomized copy
    f = b.copy()
    assert b == f

    # Create a new object using 'new()' and ensure it matches a


@pytest.mark.parametrize("args", [(None,), (4,)])
def test_eight_index_copy_new_randomize_clear_assign(args) -> None:
    """Test the behavior of copying, randomizing, clearing, and assigning eight-index arrays."""

    # Initialize the DenseLinalgFactory with 5
    lf = DenseLinalgFactory(5)

    # Create an eight-index array with the given arguments
    a = lf.create_eight_index(*args)

    # Make a copy of the eight-index array
    b = a.copy()

    # Randomize array b and ensure it's different from a
    b.randomize()
    assert a != b

    # Create another copy of b and ensure it matches b
    c = b.copy()
    new_instance = c.new()
    new_instance.__check_init_args__(
        b.nbasis,
        b.nbasis1,
        b.nbasis2,
        b.nbasis3,
        b.nbasis4,
        b.nbasis5,
        b.nbasis6,
        b.nbasis7,
    )
    assert b == c

    # Create a new object using 'new()' and ensure it matches a
    d = c.new()
    assert a == d

    # Assign values from c to b and check for equality
    b.assign(c)
    assert b == c

    # Randomize array b again
    b.randomize()

    # Copy a specific slice of b and check that it's equal to the slice of b's array
    e = b.copy(0, 1, 2, 4, 1, 4, 3)
    assert np.all(e._array == b._array[:1, 2:4, 1:4, 3:])


@pytest.mark.parametrize("_i", range(10))
def test_eight_index_permute_basis(_i) -> None:
    """Test the permute_basis method for eight-index arrays."""
    # Initialize the DenseLinalgFactory with 5
    lf = DenseLinalgFactory(7)

    # Get the forward and backward permutations
    forth, back = get_forth_back(7)

    # Create an eight-index array
    a = lf.create_eight_index()
    a.randomize()  # Randomize the array
    b = a.copy()  # Make a copy of the array

    # Apply the forward permutation
    b.permute_basis(forth)
    assert (
        a != b
    )  # Assert that the arrays are different after the forward permutation

    # Apply the backward permutation
    b.permute_basis(back)
    assert (
        a == b
    )  # Assert that the arrays are equal after the backward permutation


def test_eight_index_iscale() -> None:
    """Test the iscale method for eight-index arrays."""
    # Initialize the DenseLinalgFactory
    lf = DenseLinalgFactory()
    op = lf.create_eight_index(3)  # Create an eight-index array
    op.randomize()  # Randomize the array
    tmp = op._array.copy()  # Copy the original array for comparison

    # Scale the array by a factor of 3
    op.iscale(3.0)
    # Assert that all elements are scaled correctly
    assert (
        abs(op._array - 3 * tmp).max() < 1e-10
    )  # Ensure the scaled array matches the expected result


def test_eight_index_get_set() -> None:
    """Test the get_element and set_element methods for eight-index arrays."""
    # Initialize the DenseLinalgFactory
    lf = DenseLinalgFactory()
    op = lf.create_eight_index(
        5
    )  # Create an eight-index array with shape (5, 5, 5, 5, 5, 5, 5, 5)

    # Set a specific element and check it
    op.set_element(
        0, 1, 2, 3, 4, 1, 1, 2, 1.2
    )  # Set element at indices (0, 1, 2, 3, 4, 1, 1, 2)
    assert (
        op.get_element(0, 1, 2, 3, 4, 1, 1, 2) == 1.2
    )  # Assert that the element was set correctly

    # Set another specific element and check it
    op.set_element(
        2, 1, 2, 3, 3, 2, 3, 4, 2.44
    )  # Set element at indices (2, 1, 2, 3, 3, 2, 3, 4)
    assert (
        op.get_element(2, 1, 2, 3, 3, 2, 3, 4) == 2.44
    )  # Assert that the element was set correctly

    # Clear the array and check if the elements are zeroed out
    op.clear()
    assert (
        op.get_element(2, 1, 0, 3, 3, 2, 1, 3) == 0.0
    )  # Assert that the element is 0 after clearing


def test_eight_index_itranspose() -> None:
    """Test the itranspose method for eight-index arrays."""

    # Initialize the DenseLinalgFactory with dimension 8
    lf = DenseLinalgFactory(8)

    # Create an eight-index array
    op = lf.create_eight_index()  # Create an eight-index array
    op.randomize()  # Randomize the array

    # Generate random indices for testing
    i0, i1, i2, i3, i4, i5, i6, i7 = np.random.randint(0, 4, 8)

    # Get an element before transpose
    x = op.get_element(i0, i1, i2, i3, i4, i5, i6, i7)

    # Perform in-place transpose without specific index order
    op.itranspose()

    # Ensure that the element is correctly transposed (i1, i0, i3, i2, i5, i4 should match x)
    assert op.get_element(i1, i0, i3, i2, i5, i4, i7, i6) == x

    # Randomize the array again for the next check
    op.randomize()

    # Retrieve element before transpose
    x = op.get_element(i0, i1, i2, i3, i4, i5, i6, i7)

    # Perform itranspose with custom index order
    op.itranspose((1, 5, 3, 2, 0, 4, 7, 6))

    # Check if the element matches the expected result after applying the custom transpose order
    assert op.get_element(i1, i5, i3, i2, i0, i4, i7, i6) == x


def test_eight_index_sum() -> None:
    """Test the sum method for eight-index arrays."""

    # Initialize the DenseLinalgFactory with dimension 4
    lf = DenseLinalgFactory(4)
    op = lf.create_eight_index()  # Create an eight-index array
    op.randomize()  # Randomize the array

    # Sum the elements of the array (this is a blind test)
    op.sum()

    # Clear the array
    op.clear()

    # Ensure that the sum of the cleared array is zero
    assert op.sum() == 0  # Sum of the cleared array should be 0

    # Assign all elements of the array to 1.0 and check the sum
    op.assign(1.0)
    assert (
        op.sum() == 65536
    )  # Sum of the array with all elements as 1.0 should be 65536


def test_eight_index_slice_to_two() -> None:
    """Test contraction of an eight-index to a two-index."""
    # Initialize the DenseLinalgFactory with dimension 8
    lf = DenseLinalgFactory(8)
    # Create and randomize an eight-index array
    eight = lf.create_eight_index()
    eight.randomize()

    # Test contraction for the subscript 'abccccdd->ba'
    two = eight.contract(
        "abccccdd->ba", factor=1.3, clear=True, select="einsum"
    )
    # Verify the contracted result matches expected einsum output
    assert np.allclose(
        two._array, 1.3 * np.einsum("abccccdd->ba", eight._array)
    )

    # Contract again with different factor and check the output
    foo = eight.contract(
        "abccccdd->ba", out=two, factor=1.4, clear=True, select="einsum"
    )
    # Ensure foo and two reference the same object
    assert foo is two
    # Verify the contracted result matches expected einsum output
    assert np.allclose(
        two._array, 1.4 * np.einsum("abccccdd->ba", eight._array)
    )

    # Perform contraction without clearing, results should accumulate
    eight.contract("abccccdd->ba", out=two, factor=1.4, select="einsum")
    # Verify the accumulated result matches expected einsum output
    assert np.allclose(
        two._array, 2.8 * np.einsum("abccccdd->ba", eight._array)
    )

    # Blind test on other contraction cases
    eight.contract("abccbbad->ba", factor=1.3, clear=True, select="einsum")
    eight.contract("abccccda->ba", factor=1.3, clear=True, select="einsum")


def test_eight_index_slice_to_three() -> None:
    """Test contraction of an eight-index to a three-index."""
    # Initialize the DenseLinalgFactory with dimension 8
    lf = DenseLinalgFactory(8)

    # Create and randomize an eight-index array
    eight = lf.create_eight_index()
    eight.randomize()

    # Contract the eight-index array to a three-index using subscript 'abccccdd->bac'
    three = eight.contract(
        "abccccdd->bac", factor=1.3, clear=True, select="einsum"
    )
    # Verify the contracted result matches expected einsum output
    assert np.allclose(
        three._array, 1.3 * np.einsum("abccccdd->bac", eight._array)
    )

    # Contract again with a different factor and check the output
    foo = eight.contract(
        "abccccdd->bac", out=three, factor=1.4, clear=True, select="einsum"
    )
    # Ensure foo and three reference the same object
    assert foo is three
    # Verify the contracted result matches expected einsum output
    assert np.allclose(
        three._array, 1.4 * np.einsum("abccccdd->bac", eight._array)
    )

    # Perform contraction without clearing, results should accumulate
    eight.contract("abccccdd->bac", out=three, factor=1.4, select="einsum")
    # Verify the accumulated result matches expected einsum output
    assert np.allclose(
        three._array, 2.8 * np.einsum("abccccdd->bac", eight._array)
    )

    # Blind test on other contraction cases
    eight.contract("abccbbad->bac", factor=1.3, clear=True, select="einsum")
    eight.contract("abccccda->bac", factor=1.3, clear=True, select="einsum")


def test_eight_index_slice_to_four() -> None:
    """Test contraction of an eight-index to a four-index."""
    # Initialize the DenseLinalgFactory with dimension 8
    lf = DenseLinalgFactory(8)

    # Create and randomize an eight-index array
    eight = lf.create_eight_index()
    eight.randomize()

    # Contract the eight-index array to a four-index using subscript 'abcdcdcd->bacd'
    four = eight.contract(
        "abcdcdcd->bacd", factor=1.3, clear=True, select="einsum"
    )
    # Verify the contracted result matches expected einsum output
    assert np.allclose(
        four._array, 1.3 * np.einsum("abcdcdcd->bacd", eight._array)
    )

    # Contract again with a different factor and check the output
    foo = eight.contract(
        "abcdcdcd->bacd", out=four, factor=1.4, clear=True, select="einsum"
    )
    # Ensure foo and four reference the same object
    assert foo is four
    # Verify the contracted result matches expected einsum output
    assert np.allclose(
        four._array, 1.4 * np.einsum("abcdcdcd->bacd", eight._array)
    )

    # Perform contraction without clearing, results should accumulate
    eight.contract("abcdcdcd->bacd", out=four, factor=1.4, select="einsum")
    # Verify the accumulated result matches expected einsum output
    assert np.allclose(
        four._array, 2.8 * np.einsum("abcdcdcd->bacd", eight._array)
    )

    # Blind test on other contraction cases
    eight.contract("abcdcdab->bacd", factor=1.3, clear=True, select="einsum")
    eight.contract("abcdabdc->bacd", factor=1.3, clear=True, select="einsum")


def test_eight_index_slice_to_six() -> None:
    """Test contraction of an eight-index to a six-index."""
    lf = DenseLinalgFactory(8)
    eight = lf.create_eight_index()
    eight.randomize()
    six = eight.contract(
        "abcdefgh->abcdef", factor=1.3, clear=True, select="einsum"
    )
    assert np.allclose(
        six._array, 1.3 * np.einsum("abcdefgh->abcdef", eight._array)
    )


def test_eight_index_slice_to_five() -> None:
    """Test contraction of an eight-index to a five-index."""
    lf = DenseLinalgFactory(8)
    eight = lf.create_eight_index()
    eight.randomize()
    five = eight.contract(
        "abcdefgh->abcde", factor=1.3, clear=True, select="einsum"
    )
    assert np.allclose(
        five._array, 1.3 * np.einsum("abcdefgh->abcde", eight._array)
    )


def test_eight_index_slice_to_eight() -> None:
    """Test identity contraction of an eight-index."""
    # Create and randomize eight-index array
    lf = DenseLinalgFactory(8)
    eight = lf.create_eight_index()
    eight.randomize()

    # Perform contraction with factor 1.3
    eight2 = eight.contract(
        "abcdefgh->abcdefgh", factor=1.3, clear=True, select="einsum"
    )
    # Verify result with numpy einsum
    assert np.allclose(
        eight2._array, 1.3 * np.einsum("abcdefgh->abcdefgh", eight._array)
    )

    # Contract again onto the same object with different factor
    foo = eight.contract(
        "abcdefgh->abcdefgh",
        out=eight2,
        factor=1.4,
        clear=True,
        select="einsum",
    )
    # Ensure foo and eight2 reference the same object
    assert foo is eight2
    # Verify the contracted result matches expected einsum output
    assert np.allclose(
        eight2._array, 1.4 * np.einsum("abcdefgh->abcdefgh", eight._array)
    )

    # Perform contraction without clearing, results should accumulate
    eight.contract(
        "abcdefgh->abcdefgh", out=eight2, factor=1.4, select="einsum"
    )
    # Verify the accumulated result matches expected einsum output
    assert np.allclose(
        eight2._array, 2.8 * np.einsum("abcdefgh->abcdefgh", eight._array)
    )

    # Blind test on other contraction cases with permutations
    eight.contract(
        "abcdefgh->bacdefgh", factor=1.3, clear=True, select="einsum"
    )
    eight.contract(
        "abcdefgh->ghabcdef", factor=1.3, clear=True, select="einsum"
    )

    # Test contraction with specified slicing ranges
    eight2 = eight.contract(
        "abcdefgh->abcdefgh",
        factor=1.3,
        clear=True,
        select="einsum",
        end0=4,
        begin1=2,
        end2=5,
        begin3=1,
    )
    # Verify the sliced contraction matches expected einsum output
    assert np.allclose(
        eight2._array,
        1.3
        * np.einsum(
            "abcdefgh->abcdefgh", eight._array[:4, 2:, :5, 1:, :, :, :, :]
        ),
    )
