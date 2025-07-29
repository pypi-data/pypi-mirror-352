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

# 2024: Original version written by Katharina Boguslawski

from __future__ import annotations

import numpy as np
import pytest

from pybest import filemanager
from pybest.exceptions import ArgumentError
from pybest.iodata import IOData
from pybest.linalg import (
    CholeskyLinalgFactory,
    DenseLinalgFactory,
    DenseOneIndex,
    OneIndex,
    TwoIndex,
)
from pybest.solvers import Davidson


#
# Some utility functions
#
def list_to_array(
    data_list: list[OneIndex], add_vector: bool = False
) -> np.ndarray:
    """Convert list of OneIndex objects to numpy array

    Args:
        data_list (list[OneIndex]): a list of vectors stored as OneIndex objects
        add_vector (bool): if True, a new random vector is added (default is False)

    Returns:
        np.ndarray: all vectors stacked into one numpy array (column-wise)
    """
    vectors = data_list[0].array
    dimension = vectors.shape[0]
    for vector in data_list[1:]:
        vectors = np.vstack((vectors, vector.array))
    if add_vector:
        # Add new random correction vector
        vector_new = np.random.normal(0, 1, (dimension,))
        vectors = np.vstack((vectors, vector_new))
    # Transpose as vectors are stacked vertically together (we need horizontally)
    return vectors.T


#
# Test Gram Schmidt orthonormalization
#


def test_gramschmidt(
    unit_vectors: list[OneIndex],
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
):
    """Check if Gram-Schmidt orthonormalization works for random vector

    Args:
        unit_vectors (list[OneIndex]): A list of unit vectors [1,0,...], ...
        linalg (list[DenseLinalgFactory] | list[DenseLinalgFactory | CholeskyLinalgFactory]): the linalg factory
    """
    vectors = unit_vectors[0]
    dimension = unit_vectors[1]
    # Instantiation
    davidson = Davidson(linalg(dimension), dimension)
    # New random vector
    random_vector = DenseOneIndex(dimension)
    random_vector.randomize()
    # Call Gram-Schmidt procedure
    # Arguments: old, new, nvector, select, norm=True, threshold=1e-4
    # if old is given, select does not have any effect
    new_vector = davidson.gramschmidt(
        vectors, random_vector, len(vectors), "anything"
    )
    # Check orthogonality to old vectors
    for old_vector in vectors:
        # Scalar product of old and new vectors
        new_dot_old = new_vector.dot(old_vector)
        # Check if orthonormal
        error_msg = "New vector not orthonormal to old ones"
        assert abs(new_dot_old) < 1e-8, error_msg
    # Check orthonormality
    # Scalar product with itself
    new_dot_new = new_vector.dot(new_vector)
    # Check if orthonormal
    error_msg = "New vector not orthonormal"
    assert (new_dot_new - 1) < 1e-8, error_msg


#
# Test read_from_disk function for each argument separately
#
# inp (np.ndarray | list | None): the list of vectors containing the vector of interest
# select (str): the name of the vector stored on disk
# ind (int): the element/root to be accessed from the list of vectors
#


def test_read_from_disk_list(
    unit_vectors: list[OneIndex],
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
):
    """Check read_from_disk method for a list in Davidson module

    Args:
        unit_vectors (list[OneIndex]): A list of unit vectors [1,0,...], ...
        linalg (list[DenseLinalgFactory] | list[DenseLinalgFactory | CholeskyLinalgFactory]): the linalg factory
    """
    vectors = unit_vectors[0]
    dimension = unit_vectors[1]
    # Ignore too small dimensions in test
    if dimension < 3:
        pass
    # Instantiation
    davidson = Davidson(linalg(dimension), dimension)
    # Read second-to-last object
    expected_vector = vectors[-2]
    # By construction, dimension=len(vectors)+1
    received_vector = davidson.read_from_disk(
        vectors, "anything", dimension - 3
    )
    # Check type
    assert isinstance(received_vector, OneIndex)
    # Check if the same
    assert np.allclose(expected_vector.array, received_vector.array)


def test_read_from_disk_array(
    unit_vectors: list[OneIndex],
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
):
    """Check read_from_disk method for a np.ndarray in Davidson module

    Args:
        unit_vectors (list[OneIndex]): A list of unit vectors [1,0,...], ...
        linalg (list[DenseLinalgFactory] | list[DenseLinalgFactory | CholeskyLinalgFactory]): the linalg factory
    """
    dimension = unit_vectors[1]
    vectors = list_to_array(unit_vectors[0])
    # Ignore too small dimensions in test
    if dimension < 3:
        pass
    # Instantiation
    davidson = Davidson(linalg(dimension), dimension)
    # Read second-to-last column
    expected_vector = vectors[:, -2]
    # By construction, dimension=vectors.shape[1]+1
    received_vector = davidson.read_from_disk(
        vectors, "anything", dimension - 3
    )
    # Check type
    assert isinstance(received_vector, np.ndarray)
    # Check if the same
    assert np.allclose(expected_vector, received_vector)


def test_read_from_disk_to_disk(
    unit_vectors: list[OneIndex],
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
):
    """Check read_from_disk method for inp = None in Davidson module

    Args:
        unit_vectors (list[OneIndex]): A list of unit vectors [1,0,...], ...
        linalg (list[DenseLinalgFactory] | list[DenseLinalgFactory | CholeskyLinalgFactory]): the linalg factory
    """
    vectors_list = unit_vectors[0]
    dimension = unit_vectors[1]
    # Ignore too small dimensions in test
    if dimension < 3:
        pass
    # Dump vector of interest to disk with name "something"
    index = dimension - 3
    fname = f"something_{index}.h5"
    filename = filemanager.temp_path(fname)
    v = IOData(vector=vectors_list[-2])
    v.to_file(filename)
    # Instantiation
    davidson = Davidson(linalg(dimension), dimension)
    # Read second-to-last column
    expected_vector = vectors_list[-2]
    # By construction, dimension=len(vectors)+1
    received_vector = davidson.read_from_disk(
        vectors_list, "something", dimension - 3
    )
    # Check type
    assert isinstance(received_vector, OneIndex)
    # Check if the same
    assert np.allclose(expected_vector.array, received_vector.array)


def test_read_from_disk_raise_error(
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
):
    """Raise ArgumentError for read_from_disk function

    Args:
        linalg (list[DenseLinalgFactory] | list[DenseLinalgFactory | CholeskyLinalgFactory]): _description_

    Raises:
        ArgumentError: Unsupported types
    """
    davidson = Davidson(linalg(5), 5)
    with pytest.raises(ArgumentError):
        # Only first argument matters
        davidson.read_from_disk("Should raise an error", None, None)


#
# Test push_vector function for each argument separately
#
# inp (np.ndarray | list | None): list of vectors to be updated
# new (np.ndarray | OneIndex): the new vector to be added
# select (str): the name of vectors stored on disk
# ind (int): the index of the new vector to be stored
#


def test_push_vector_list(
    unit_vectors: list[OneIndex],
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
):
    """Check push_vector method for a list in Davidson module

    Args:
        unit_vectors (list[OneIndex]): A list of unit vectors [1,0,...], ...
        linalg (list[DenseLinalgFactory] | list[DenseLinalgFactory | CholeskyLinalgFactory]): the linalg factory
    """
    vectors = unit_vectors[0]
    dimension = unit_vectors[1]
    old_length = len(vectors)
    # Instantiation
    davidson = Davidson(linalg(dimension), dimension)
    # Create random new vector
    new_vector = DenseOneIndex(dimension)
    new_vector.randomize()
    # Add new vector to vectors (append to the end)
    # Last two arguments are obsolete (select, ind)
    received_vector = davidson.push_vector(vectors, new_vector, None, None)
    # Check type
    assert isinstance(received_vector, list)
    # Check length
    assert len(received_vector) == old_length + 1
    # Check if new element is properly assigned
    assert np.allclose(received_vector[-1].array, new_vector.array)


def test_push_vector_array(
    unit_vectors: list[OneIndex],
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
):
    """Check push_vector method for a np.ndarray in Davidson module

    Args:
        unit_vectors (list[OneIndex]): A list of unit vectors [1,0,...], ...
        linalg (list[DenseLinalgFactory] | list[DenseLinalgFactory | CholeskyLinalgFactory]): the linalg factory
    """
    dimension = unit_vectors[1]
    vectors = list_to_array(unit_vectors[0])
    # Take number of columns
    old_length = vectors.shape[1]
    # Instantiation
    davidson = Davidson(linalg(dimension), dimension)
    # Create random new vector
    vector_new = np.random.normal(0, 1, (dimension,))
    # Replace second-to-last element
    # Third arguments is obsolete (select)
    received_vector = davidson.push_vector(
        vectors, vector_new, None, old_length - 2
    )
    # Check type
    assert isinstance(received_vector, np.ndarray)
    # Check length
    assert received_vector.shape[1] == old_length
    # Check if new element is properly assigned
    assert np.allclose(received_vector[:, -2], vector_new)


def test_push_vector_to_disk(
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
):
    """Check push_vector method for inp = None in Davidson module

    Args:
        unit_vectors (list[OneIndex]): A list of unit vectors [1,0,...], ...
        linalg (list[DenseLinalgFactory] | list[DenseLinalgFactory | CholeskyLinalgFactory]): the linalg factory
    """
    # Create random new vector
    new_vector = DenseOneIndex(10)
    new_vector.randomize()
    # Instantiation
    davidson = Davidson(linalg(10), 10)
    # Dump vector of interest to disk with name "something"
    received_vector = davidson.push_vector(
        None, new_vector, "push_something", 3
    )
    # Check type
    assert received_vector is None
    # Read vector from disk
    filename = filemanager.temp_path("push_something_3.h5")
    v = IOData.from_file(filename)
    # Check if the same (vector is stored in vector attribute)
    assert np.allclose(v.vector.array, new_vector.array)


def test_push_vector_raise_error(
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
):
    """Raise ArgumentError for push_vector function

    Args:
        linalg (list[DenseLinalgFactory] | list[DenseLinalgFactory | CholeskyLinalgFactory]): _description_

    Raises:
        ArgumentError: Unsupported types
    """
    davidson = Davidson(linalg(5), 5)
    with pytest.raises(ArgumentError):
        # Only first argument matters
        davidson.push_vector("Should raise an error", None, None, None)


#
# Test reset_vector function for each argument separately
#
# inp (np.ndarray | list | None): the list of vectors to be deleted/reset
#


def test_reset_vector_list(
    unit_vectors: list[OneIndex],
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
):
    """Check reset_vector method for a list in Davidson module

    Args:
        unit_vectors (list[OneIndex]): A list of unit vectors [1,0,...], ...
        linalg (list[DenseLinalgFactory] | list[DenseLinalgFactory | CholeskyLinalgFactory]): the linalg factory
    """
    vectors = unit_vectors[0]
    dimension = unit_vectors[1]
    # Instantiation
    davidson = Davidson(linalg(dimension), dimension)
    # Remove all vectors from list/empty list
    received_vector = davidson.reset_vector(vectors)
    # Check type
    assert isinstance(received_vector, list)
    # Check length
    assert len(received_vector) == 0


def test_reset_vector_array(
    unit_vectors: list[OneIndex],
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
):
    """Check reset_vector method for a np.ndarray in Davidson module

    Args:
        unit_vectors (list[OneIndex]): A list of unit vectors [1,0,...], ...
        linalg (list[DenseLinalgFactory] | list[DenseLinalgFactory | CholeskyLinalgFactory]): the linalg factory
    """
    dimension = unit_vectors[1]
    vectors = list_to_array(unit_vectors[0])
    # Instantiation
    davidson = Davidson(linalg(dimension), dimension)
    # Set all elements of vectors (array) to zero
    received_vector = davidson.reset_vector(vectors)
    # Check type
    assert isinstance(received_vector, np.ndarray)
    # Check if all elements are 0
    assert (received_vector == 0).all()


def test_reset_vector_to_disk(
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
):
    """Check reset_vector method for inp = None in Davidson module

    Args:
        linalg (list[DenseLinalgFactory] | list[DenseLinalgFactory | CholeskyLinalgFactory]): the linalg factory
    """
    # Instantiation
    davidson = Davidson(linalg(10), 10)
    # Do nothing (as vectors are stored on disk and will be overwritten), return None
    received_vector = davidson.reset_vector(None)
    # Check type
    assert received_vector is None


def test_reset_vector_raise_error(
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
):
    """Raise ArgumentError for reset_vector function

    Args:
        linalg (list[DenseLinalgFactory] | list[DenseLinalgFactory | CholeskyLinalgFactory]): _description_

    Raises:
        ArgumentError: Unsupported types
    """
    davidson = Davidson(linalg(5), 5)
    with pytest.raises(ArgumentError):
        # Only first argument matters
        davidson.reset_vector("Should raise an error")


#
# Test normalize_correction_vector function for each argument separately
#
# inp (None | np.ndarray): vectors to be normalized
# dim (int): the dimension of each vector
#


def test_normalize_correction_vector_array(
    unit_vectors: list[OneIndex],
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
):
    """Check normalize_correction_vector method for a np.ndarray in Davidson module

    Args:
        unit_vectors (list[OneIndex]): A list of unit vectors [1,0,...], ...
        linalg (list[DenseLinalgFactory] | list[DenseLinalgFactory | CholeskyLinalgFactory]): the linalg factory
    """
    dimension = unit_vectors[1]
    vectors = list_to_array(unit_vectors[0], add_vector=True)
    vector_new = vectors[:, -1]
    # Instantiation
    davidson = Davidson(linalg(dimension), dimension)
    # Set all elements of vectors (array) to zero
    received_vector = davidson.normalize_correction_vector(vectors, None)
    # Check type
    assert isinstance(received_vector, np.ndarray)
    # Check if vector_new and orthonormalized solution differ
    # New vector is the last column of the return value
    vector_new_ortho = received_vector[:, -1]
    assert not np.allclose(vector_new_ortho, vector_new)
    # Check orthogonality to old vectors
    # Loop over all but last one
    for old_vector in (received_vector.T)[:-2]:
        # Scalar product of old and new vectors
        new_dot_old = np.dot(old_vector, vector_new_ortho)
        # Check if orthonormal
        error_msg = "New vector not orthonormal to old ones"
        assert abs(new_dot_old) < 1e-8, error_msg
    # Check orthonormality
    # Scalar product with itself
    new_dot_new = np.dot(vector_new_ortho, vector_new_ortho)
    # Check if orthonormal
    error_msg = "New vector not orthonormal"
    assert (new_dot_new - 1) < 1e-8, error_msg


def test_normalize_correction_vector_to_disk(
    unit_vectors: list[OneIndex],
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
):
    """Check normalize_correction_vector method for inp = None in Davidson module

    Args:
        unit_vectors (list[OneIndex]): A list of unit vectors [1,0,...], ...
        linalg (list[DenseLinalgFactory] | list[DenseLinalgFactory | CholeskyLinalgFactory]): the linalg factory
    """
    # First dump unit_vectors to disk with name residual
    vectors_list = unit_vectors[0]
    dimension = unit_vectors[1]
    # Create random new vector
    new_vector = DenseOneIndex(dimension)
    new_vector.randomize()
    # Add to vector_list
    vectors_list.append(new_vector)
    for ind, vector in enumerate(vectors_list):
        filename = filemanager.temp_path(f"residual_{ind}.h5")
        v = IOData(vector=vector)
        v.to_file(filename)
    # Instantiation
    nroot = len(vectors_list)
    davidson = Davidson(linalg(dimension), nroot)
    # Normalize all vectors (using Gramm-Schmidt)
    # New orthonormal vectors are stored to disk under residualortho_index
    received_vector = davidson.normalize_correction_vector(None, dimension)
    # Check type
    assert received_vector is None
    # Normalized vectors are stored to disk with filename residualortho_index
    vectors_ortho = []
    for ind in range(nroot):
        filename = filemanager.temp_path(f"residualortho_{ind}.h5")
        v = IOData.from_file(filename)
        vectors_ortho.append(v.vector.copy())
    # Check orthonormality using first vector
    vector_0 = vectors_ortho[0]
    for vector in vectors_ortho[1:]:
        v_0_dot_v = vector_0.dot(vector)
        # Check if orthonormal
        error_msg = "Vectors are not orthonormal"
        assert abs(v_0_dot_v) < 1e-8, error_msg
    # Check orthonormality
    # Scalar product with itself
    v_0_dot_v_0 = vector_0.dot(vector_0)
    # Check if orthonormal
    error_msg = "New vector not orthonormal"
    assert (v_0_dot_v_0 - 1) < 1e-8, error_msg


def test_normalize_correction_vector_error(
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
):
    """Raise ArgumentError for normalize_correction_vector function

    Args:
        linalg (list[DenseLinalgFactory] | list[DenseLinalgFactory | CholeskyLinalgFactory]): _description_

    Raises:
        ArgumentError: Unsupported types
    """
    davidson = Davidson(linalg(5), 5)
    with pytest.raises(ArgumentError):
        # Only first argument matters
        davidson.normalize_correction_vector("Should raise an error", None)


#
# Test sort_eig function for each argument separately
#
# eigval (np.ndarray): the eigenvalues to be sorted
# eigvec (np.ndarray): the eigenvectors to be sorted
#


def test_sort_eig_non_degenerate(
    unit_vectors: list[OneIndex],
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
):
    """Test sorting of eigenvectors

    Args:
        unit_vectors (list[OneIndex]): A list of unit vectors [1,0,...], ...
        linalg (list[DenseLinalgFactory] | list[DenseLinalgFactory | CholeskyLinalgFactory]): the linalg factory
    """
    dimension = unit_vectors[1]
    energies = np.array(unit_vectors[2])
    vectors = list_to_array(unit_vectors[0])
    # Instantiation
    davidson = Davidson(linalg(dimension), dimension)
    # Set all elements of vectors (array) to zero
    energies_sorted, vectors_sorted = davidson.sort_eig(energies, vectors)
    # Check type
    assert isinstance(energies_sorted, np.ndarray)
    assert isinstance(vectors_sorted, np.ndarray)
    # Check sorted values
    assert (energies_sorted != energies).any()
    for i, e_i in enumerate(energies_sorted):
        assert i == e_i
    # Check vectors (should appear in reversed order)
    for i in range(vectors_sorted.shape[1]):
        # Fix dimension as we add one more axis in the fixture
        assert (vectors_sorted[:, i] == vectors[:, dimension - 2 - i]).all()


def test_sort_eig_degenerate(
    unit_vectors: list[OneIndex],
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
):
    """Test sorting of eigenvectors

    Args:
        unit_vectors (list[OneIndex]): A list of unit vectors [1,0,...], ...
        linalg (list[DenseLinalgFactory] | list[DenseLinalgFactory | CholeskyLinalgFactory]): the linalg factory
    """
    dimension = unit_vectors[1]
    energies = unit_vectors[2]
    vectors = list_to_array(unit_vectors[0], add_vector=True)
    # Energy of new vector will be lowest (by construction energies > 0.0)
    energies.append(0)
    energies = np.array(energies)
    # Instantiation
    davidson = Davidson(linalg(dimension), dimension)
    # Set all elements of vectors (array) to zero
    energies_sorted, vectors_sorted = davidson.sort_eig(energies, vectors)
    # Check type
    assert isinstance(energies_sorted, np.ndarray)
    assert isinstance(vectors_sorted, np.ndarray)
    # Check sorted values
    assert (energies_sorted != energies).any()
    # By construction, first two elements should be 0
    assert energies_sorted[0] == energies_sorted[1] == 0
    assert (energies_sorted[2:] != 0).all()
    # Check if degenerate eigenvalues are orthonormal (we do not change any
    # other eigenvectors)
    assert np.dot(vectors_sorted[:, 0], vectors_sorted[:, 1]) < 1e-8
    assert np.dot(vectors_sorted[:, 0], vectors_sorted[:, 0]) - 1 < 1e-8
    assert np.dot(vectors_sorted[:, 1], vectors_sorted[:, 1]) - 1 < 1e-8


#
# Test build_guess_vectors function for restart option only
#


@pytest.mark.parametrize(
    "label", ["civ", "civ_ip", "civ_ea", "civ_something", "foo_civ"]
)
def test_build_guess_vectors(
    label: str,
    random_vectors: np.ndarray,
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
):
    """Test building of guess vectors from restart file

    Args:
        label (str): name of the h5 group to be read in
        random_vectors (np.ndarray): random arrays of shape (10,....)
        linalg (list[DenseLinalgFactory] | list[DenseLinalgFactory | CholeskyLinalgFactory]): the linalg factory
    """
    # Dump to disk
    filename = filemanager.temp_path("restart_tests.h5")
    v = IOData(**{label: random_vectors})
    v.to_file(filename)
    # Instantiation
    davidson = Davidson(linalg(10), 10, restart_fn=filename)
    vectors_restart = davidson.build_guess_vectors(None)
    # Check type
    assert isinstance(vectors_restart, list)
    # Check orthonormal eigenvectors are the same
    if random_vectors.ndim == 1:
        assert np.allclose(random_vectors, vectors_restart[0].array)
    else:
        # First eigenvector is orthonormal (vectors may differ by a factor of -1)
        try:
            assert np.allclose(random_vectors[:, 0], vectors_restart[0].array)
        except AssertionError:
            assert np.allclose(-random_vectors[:, 0], vectors_restart[0].array)
        # Remaining ones have to be different
        for i in range(1, random_vectors.ndim):
            assert not np.allclose(
                random_vectors[:, i], vectors_restart[i].array
            )


@pytest.mark.parametrize("label", ["ci", "should_fail"])
def test_build_guess_vectors_error(
    label: str,
    random_vectors: np.ndarray,
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
):
    """Test building of guess vectors from restart file using wrong h5 groups

    Args:
        label (str): name of the h5 group to be read in
        random_vectors (np.ndarray): random arrays of shape (10,....)
        linalg (list[DenseLinalgFactory] | list[DenseLinalgFactory | CholeskyLinalgFactory]): the linalg factory
    """
    # Dump to disk
    filename = filemanager.temp_path("restart_tests.h5")
    v = IOData(**{label: random_vectors})
    v.to_file(filename)
    # Instantiation
    davidson = Davidson(linalg(10), 10, restart_fn=filename)
    # Raise ArgumentError as "civ" is not found
    with pytest.raises(ArgumentError):
        davidson.build_guess_vectors(None)


#
# Test calculate_subspace_hamiltonian function
#
# bvector: list[OneIndex] | None,
# sigmav: list[OneIndex] | None,
# hamsub: TwoIndex,
# bind: int
#


def test_calculate_subspace_hamiltonian(
    unit_vectors: list[OneIndex],
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
):
    """Test construction of subspace Hamiltonian from scratch

    Args:
        unit_vectors (list[OneIndex]): A list of unit vectors [1,0,...], ...
        linalg (list[DenseLinalgFactory] | list[DenseLinalgFactory | CholeskyLinalgFactory]): the linalg factory
    """
    bvector = unit_vectors[0]
    sigmav = unit_vectors[0]
    dimension = unit_vectors[1]
    # Instantiation
    lf = linalg(dimension)
    davidson = Davidson(lf, dimension)
    # Set parameters
    davidson.nbvector = dimension - 1
    # Determine subspace Hamiltonian from b.s
    subspace_hamiltonian = davidson.calculate_subspace_hamiltonian(
        bvector, sigmav, False, None
    )
    # Check type
    assert isinstance(subspace_hamiltonian, TwoIndex)
    # By construction, the resulting array is a unit matrix
    reference_result = lf.create_two_index(dimension - 1)
    reference_result.assign_diagonal(1.0)
    assert reference_result == subspace_hamiltonian


# dim has to be smaller than the number of unit_vectors, otherwise we need to
# add more vectors in the list unit_vectors
@pytest.mark.parametrize("dim", [1, 2, 3])
def test_calculate_subspace_hamiltonian_addition(
    dim: int,
    unit_vectors: list[OneIndex],
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
):
    """Test construction of subspace Hamiltonian by adding to existing space

    Args:
        dim (int): The dimension of the existing subspace
        unit_vectors (list[OneIndex]): A list of unit vectors [1,0,...], ...
        linalg (list[DenseLinalgFactory] | list[DenseLinalgFactory | CholeskyLinalgFactory]): the linalg factory
    """
    dimension = unit_vectors[1]
    lf = linalg(dimension)
    # Create reference data
    old_subspace = lf.create_two_index(dim)
    old_subspace.randomize()
    # By construction, the new subspace added is a unit matrix
    reference_result = lf.create_two_index(dimension - 1)
    reference_result.assign_diagonal(1.0)
    reference_result.assign(old_subspace, end0=dim, end1=dim)
    # Determine new subspace
    bvector = unit_vectors[0]
    sigmav = unit_vectors[0]
    # Instantiation
    davidson = Davidson(lf, dimension)
    # Set parameters
    davidson.nbvector = dimension - 1
    # Determine subspace Hamiltonian from b.s
    subspace_hamiltonian = davidson.calculate_subspace_hamiltonian(
        bvector, sigmav, old_subspace, dim
    )
    # Check type
    assert isinstance(subspace_hamiltonian, TwoIndex)
    assert reference_result == subspace_hamiltonian
