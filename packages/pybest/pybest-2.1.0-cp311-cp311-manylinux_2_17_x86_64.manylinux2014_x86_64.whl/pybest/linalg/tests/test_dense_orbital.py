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


import h5py as h5
import numpy as np
import pytest
import scipy as scipy

from pybest.exceptions import MatrixShapeError
from pybest.linalg import DenseLinalgFactory, DenseOrbital
from pybest.scf.utils import compute_1dm_hf

#
# Utility functions
#


def get_forth_back(n):
    """Returns matching pair of forth and back permutation.

    **Arguments:**

    n
         The length of the permutation

    It is guaranteed that the identity permutation is never returned.
    """
    while True:
        forth = np.random.uniform(0, 1, 5).argsort()
        if (forth != np.arange(5)).all():
            break
    back = np.zeros(5, int)
    for i, j in enumerate(forth):
        back[j] = i
    return forth, back


def get_signs(n):
    """Returns an array with signs (all elements are just +1 or -1)

    **Arguments:**

    n
         The length of the signs array

    It is guaranteed that not all signs are positive.
    """
    while True:
        signs = np.random.randint(0, 2, n) * 2 - 1
        if (signs < 0).all():
            continue
        elif (signs < 0).any():
            return signs


def get_random_exp(lf):
    """Return a random expansion and an identity overlap matrix"""
    exp = lf.create_orbital()
    a = np.random.normal(0, 1, (lf.default_nbasis, lf.default_nbasis))
    a = a + a.T
    _, evecs = np.linalg.eigh(a)
    exp.coeffs[:] = evecs
    exp.occupations[: lf.default_nbasis // 2] = 1.0
    exp.energies[:] = np.random.uniform(-1, 1, lf.default_nbasis)
    exp.energies.sort()
    olp = lf.create_two_index()
    olp._array[:] = np.identity(lf.default_nbasis)
    return exp, olp


#
# DenseOrbital tests
#


def test_orbital_hdf5():
    lf = DenseLinalgFactory(5)
    for args in (None,), (4,), (6, 3):
        a = lf.create_orbital(*args)
        a.randomize()
        with h5.File(
            "pybest.linalg.test.test_dens.test_orbital_hdf5",
            driver="core",
            backing_store=False,
            mode="w",
        ) as f:
            a.to_hdf5(f)
            b = DenseOrbital.from_hdf5(f)
            assert a == b


def test_orbital_copy_new_randomize_clear_assign():
    lf = DenseLinalgFactory(5)
    for args in (None,), (4,), (6, 3):
        a = lf.create_orbital(*args)
        b = a.copy()
        b.randomize()
        assert a != b
        c = b.copy()
        c.new.__check_init_args__(c, b)
        assert b == c
        d = c.new()
        assert a == d
        b.clear()
        assert a == b
        b.assign(c)
        assert b == c


def test_orbital_copy():
    lf = DenseLinalgFactory()
    exp1 = lf.create_orbital(3, 2)
    exp1._coeffs[:] = np.random.uniform(0, 1, (3, 2))
    exp1._energies[:] = np.random.uniform(0, 1, 2)
    exp1._occupations[:] = np.random.uniform(0, 1, 2)
    exp2 = exp1.copy()
    assert (exp1._coeffs == exp2._coeffs).all()
    assert (exp1._energies == exp2._energies).all()
    assert (exp1._occupations == exp2._occupations).all()


def test_orbital_itranspose():
    lf = DenseLinalgFactory(5)
    orig = lf.create_orbital()
    orig.randomize()
    out = orig.copy()
    out.itranspose()
    assert out.coeffs[0, 1] == orig.coeffs[1, 0]
    assert out.coeffs[2, 1] == orig.coeffs[1, 2]
    assert out.coeffs[3, 2] == orig.coeffs[2, 3]
    assert out.coeffs[4, 2] == orig.coeffs[2, 4]


def test_orbital_imul():
    lf = DenseLinalgFactory(5)
    orig = lf.create_orbital()
    one = lf.create_one_index()
    orig.randomize()
    one.randomize()
    out = orig.copy()
    out.imul(one)
    assert np.allclose(out.coeffs, orig.coeffs * one._array)


def test_orbital_permute_basis():
    lf = DenseLinalgFactory(5)
    for _ in range(10):
        forth, back = get_forth_back(5)
        a = lf.create_orbital()
        a.randomize()
        b = a.copy()
        b.permute_basis(forth)
        assert a != b
        b.permute_basis(back)
        assert a == b


def test_orbital_permute_orbitals():
    lf = DenseLinalgFactory(5)
    for _ in range(10):
        forth, back = get_forth_back(5)
        a = lf.create_orbital()
        a.randomize()
        b = a.copy()
        b.permute_orbitals(forth)
        assert a != b
        b.permute_orbitals(back)
        assert a == b


def test_orbital_change_basis_signs():
    lf = DenseLinalgFactory(5)
    for _ in range(10):
        signs = get_signs(5)
        a = lf.create_orbital()
        a.randomize()
        b = a.copy()
        b.change_basis_signs(signs)
        assert a != b
        b.change_basis_signs(signs)
        assert a == b


def test_orbital_check_normalization():
    lf = DenseLinalgFactory(5)
    exp, olp = get_random_exp(lf)
    exp.check_normalization(olp)


def test_orbital_check_orthonormality():
    lf = DenseLinalgFactory(5)
    exp, olp = get_random_exp(lf)
    exp.check_orthonormality(olp)


def test_orbital_error_eigen():
    lf = DenseLinalgFactory(5)
    exp = lf.create_orbital()
    a = np.random.normal(0, 1, (5, 5))
    fock = lf.create_two_index()
    fock._array[:] = a + a.T
    evals, evecs = np.linalg.eigh(fock._array)
    exp.coeffs[:] = evecs
    exp.energies[:] = evals
    olp = lf.create_two_index()
    olp._array[:] = np.identity(5)
    assert exp.error_eigen(fock, olp) < 1e-10
    exp.coeffs[:] += np.random.normal(0, 1e-3, (5, 5))
    assert exp.error_eigen(fock, olp) > 1e-10


def test_orbital_from_fock():
    lf = DenseLinalgFactory(5)
    a = np.random.normal(0, 1, (5, 5))
    fock = lf.create_two_index()
    fock._array[:] = a + a.T
    a = np.random.normal(0, 1, (5, 5))
    olp = lf.create_two_index()
    olp._array[:] = np.dot(a, a.T)
    exp = lf.create_orbital()
    exp.from_fock(fock, olp)
    assert exp.error_eigen(fock, olp) < 1e-5


def test_orbital_from_fock_and_dm():
    natom = 5
    lf = DenseLinalgFactory(natom)

    # Use a simple Huckel-like model to construct degenerate levels
    fock = lf.create_two_index()
    olp = lf.create_two_index()
    for i in range(natom):
        fock.set_element(i, i, 0.6)
        fock.set_element(i, (i + 1) % natom, -0.2)
        olp.set_element(i, i, 1.0)
        olp.set_element(i, (i + 1) % natom, 0.2)

    # Create orbitals that will be used to construct various density matrices
    exp = lf.create_orbital()
    exp.from_fock(fock, olp)

    # Checks for every case
    def check_case(exp0):
        dm = compute_1dm_hf(exp0)
        exp1 = lf.create_orbital()
        exp1.from_fock_and_dm(fock, dm, olp)
        assert np.allclose(exp0.occupations, exp1.occupations)
        assert exp1.error_eigen(fock, olp) < 1e-5
        sds = olp.copy()
        sds.itranspose()
        sds.idot(dm)
        sds.idot(olp)
        exp1.energies[:] = exp1.occupations
        assert exp1.error_eigen(sds, olp) < 1e-5

    # Case 1: not difficult, i.e. compatible degeneracies
    exp.occupations[:] = [1, 1, 1, 0, 0]
    check_case(exp)

    # Case 2: incompatible degeneracies
    exp.occupations[:] = [2, 2, 1, 0, 0]
    check_case(exp)

    # Case 3: incompatible degeneracies and rotated degenerate orbitals
    exp.occupations[:] = [2, 1, 0, 0, 0]
    for i in range(36):
        exp.rotate_2orbitals(i * np.pi / 18.0, 1, 2)
        check_case(exp)

    # Case 4: incompatible degeneracies, fractional occupations and rotated
    # degenerate orbitals
    exp.occupations[:] = [1.5, 0.7, 0.3, 0, 0]
    for i in range(36):
        exp.rotate_2orbitals(i * np.pi / 18.0, 1, 2)
        check_case(exp)


def test_orbital_assign_dot1():
    lf = DenseLinalgFactory(2)
    exp0 = lf.create_orbital()
    exp1 = lf.create_orbital()
    tf2 = lf.create_two_index()
    exp0.randomize()
    tf2.randomize()
    exp1.assign_dot(exp0, tf2)
    assert np.allclose(exp1.coeffs, np.dot(exp0.coeffs, tf2._array))
    # exceptions
    exp3 = lf.create_orbital(nbasis=3, nfn=2)
    with pytest.raises(MatrixShapeError):
        # mismatch between exp1.nbasis and exp3.nbasis
        exp1.assign_dot(exp3, tf2)
    with pytest.raises(MatrixShapeError):
        # mismatch between exp3.nbasis and exp1.nbasis
        exp3.assign_dot(exp1, tf2)
    tf4 = lf.create_two_index(nbasis=3)
    exp5 = lf.create_orbital(nbasis=2, nfn=3)
    with pytest.raises(MatrixShapeError):
        # mismatch between exp1.nfn and tf4.shape[0]
        exp5.assign_dot(exp1, tf4)
    exp4 = lf.create_orbital(nbasis=3, nfn=3)
    with pytest.raises(MatrixShapeError):
        # mismatch between exp3.nfn and tf4.shape[1]
        exp3.assign_dot(exp4, tf4)


def test_orbital_assign_dot2():
    lf = DenseLinalgFactory(2)
    exp0 = lf.create_orbital()
    exp1 = lf.create_orbital()
    tf2 = lf.create_two_index()
    exp0.randomize()
    tf2.randomize()
    exp1.assign_dot(tf2, exp0)
    assert np.allclose(exp1.coeffs, np.dot(tf2._array, exp0.coeffs))
    # exceptions
    exp3 = lf.create_orbital(nbasis=3, nfn=2)
    with pytest.raises(MatrixShapeError):
        # mismatch between tf2.shape[1] and exp3.nbasis
        exp1.assign_dot(tf2, exp3)
    with pytest.raises(MatrixShapeError):
        # mismatch between tf2.shape[0] and exp3.nbasis
        exp3.assign_dot(tf2, exp1)
    tf4 = lf.create_two_index(nbasis=3)
    exp4 = lf.create_orbital(nbasis=3, nfn=3)
    exp5 = lf.create_orbital(nbasis=3, nfn=2)
    with pytest.raises(MatrixShapeError):
        # mismatch between exp5.nfn and exp4.nfn
        exp5.assign_dot(tf4, exp4)


def test_orbital_assign_occupations():
    lf = DenseLinalgFactory(6)
    exp0 = lf.create_orbital()
    one = lf.create_one_index()
    exp0.randomize()
    one.randomize()
    exp0.assign_occupations(one)
    assert np.allclose(exp0.occupations, one._array)


def test_orbital_rotate_random():
    lf = DenseLinalgFactory(5)
    exp0, olp = get_random_exp(lf)
    exp0.check_normalization(olp)
    exp1 = exp0.copy()
    exp1.rotate_random()
    exp1.check_normalization(olp)
    dots = np.dot(exp0.coeffs.T, exp1.coeffs)
    assert not np.allclose(dots, np.identity(5))


def test_orbital_two_index_rotate_2orbitals():
    lf = DenseLinalgFactory(4)
    exp0, olp = get_random_exp(lf)
    exp0.check_normalization(olp)
    exp1 = exp0.copy()
    exp1.rotate_2orbitals()
    exp1.check_normalization(olp)
    check = np.identity(4, float)
    dots = np.dot(exp0.coeffs.T, exp1.coeffs)
    check = np.identity(4)
    check[1, 1] = 1.0 / np.sqrt(2)
    check[1, 2] = 1.0 / np.sqrt(2)
    check[2, 1] = -1.0 / np.sqrt(2)
    check[2, 2] = 1.0 / np.sqrt(2)
    assert np.allclose(dots, check)


def test_orbital_swap_orbitals():
    lf = DenseLinalgFactory(4)
    exp0, olp = get_random_exp(lf)
    exp0.check_normalization(olp)
    exp1 = exp0.copy()
    exp1.swap_orbitals(np.array([[0, 1], [2, 3]]))
    dots = np.dot(exp0.coeffs.T, exp1.coeffs)
    check = np.zeros((4, 4))
    check[0, 1] = 1.0
    check[1, 0] = 1.0
    check[2, 3] = 1.0
    check[3, 2] = 1.0
    assert np.allclose(dots, check)


@pytest.mark.parametrize(
    "nbasis,shape,inds",
    [(4, (4, 1), (0, 1)), (4, (4, 2), (0, 2)), (4, (4, 3), (1, 4))],
)
def test_assign_coeffs_array(nbasis, shape, inds):
    """Assign only coeffs to orbitals taken from some array

    Args:
        nbasis (int): number of basis functions
        shape (tuple(ints)): begin0 and end0 of assign_coeffs function
        inds (tuple(ints)): view of final coeffs used for assert testing
    """
    lf = DenseLinalgFactory(nbasis)
    exp0, olp = get_random_exp(lf)
    exp0.check_normalization(olp)
    # Check if elements are different from 1's
    assert (exp0.coeffs != 1.0).all()
    # Simply assign 1's
    ones = np.ones(shape)
    # Reset some MOs (columns)
    exp0.assign_coeffs(ones, *inds)
    assert ((exp0.coeffs[:, inds[0] : inds[1]]) == ones).all()


@pytest.mark.parametrize(
    "nbasis,shape,inds",
    [(4, (4, 1), (0, 1)), (4, (4, 2), (0, 2)), (4, (4, 3), (1, 4))],
)
def test_assign_coeffs_two_index(nbasis, shape, inds):
    """Assign only coeffs to orbitals taken from some TwoIndex object

    Args:
        nbasis (int): number of basis functions
        shape (tuple(ints)): begin0 and end0 of assign_coeffs function
        inds (tuple(ints)): view of final coeffs used for assert testing
    """
    lf = DenseLinalgFactory(nbasis)
    exp0, olp = get_random_exp(lf)
    exp0.check_normalization(olp)
    # Check if elements are different from 1's
    assert (exp0.coeffs != 1.0).all()
    # Simply assign 1's
    ones = lf.create_two_index(*shape)
    ones.array[:] = np.ones(shape)
    # Reset some MOs (columns)
    exp0.assign_coeffs(ones, *inds)
    assert ((exp0.coeffs[:, inds[0] : inds[1]]) == ones.array).all()


@pytest.mark.parametrize(
    "nbasis,shape,inds",
    [(4, (4, 1), (0, 1)), (4, (4, 2), (0, 2)), (4, (4, 3), (1, 4))],
)
def test_assign_coeffs_dense_orbital(nbasis, shape, inds):
    """Assign only coeffs to orbitals taken from some other DenseOrbital object

    Args:
        nbasis (int): number of basis functions
        shape (tuple(ints)): begin0 and end0 of assign_coeffs function
        inds (tuple(ints)): view of final coeffs used for assert testing
    """
    lf = DenseLinalgFactory(nbasis)
    exp0, olp = get_random_exp(lf)
    exp0.check_normalization(olp)
    # Check if elements are different from 1's
    assert (exp0.coeffs != 1.0).all()
    # Simply assign 1's
    ones = lf.create_orbital(*shape)
    ones._coeffs[:] = np.ones(shape)
    # Reset some MOs (columns)
    exp0.assign_coeffs(ones, *inds)
    assert ((exp0.coeffs[:, inds[0] : inds[1]]) == ones.coeffs).all()


@pytest.mark.parametrize("nbasis", [4, 5, 40])
def test_gram_schmidt(nbasis):
    """Test GS orthonormalization procedure.
    We perturb the first column by setting it to [0.2,0,...,0], then we
    use the GS algorithm to fix the remaining columns. We only check if
    the final orbitals are normalized.

    Args:
        nbasis (int): number of basis functions
    """
    lf = DenseLinalgFactory(nbasis)
    exp0, olp = get_random_exp(lf)
    exp0.check_normalization(olp)
    # mess up first column
    exp0._coeffs[:, 0] = 0
    exp0._coeffs[0, 0] = 0.2
    with pytest.raises(AssertionError):
        exp0.check_normalization(olp)
    exp0.gram_schmidt()
    # Check normalization again
    exp0.check_normalization(olp)
    # First column has to be 1,0,...
    assert exp0.coeffs[0, 0] == 1.0
    for row in exp0.coeffs[1:, 0]:
        assert row == 0.0


def test_gram_schmidt_specific():
    """Test GS orthonormalization procedure for a specific case."""
    lf = DenseLinalgFactory(4)

    olp = lf.create_two_index()
    olp._array[:] = np.identity(lf.default_nbasis)

    exp0 = lf.create_orbital()
    exp0._coeffs[:] = np.identity(lf.default_nbasis)
    exp0._coeffs[0, 0] = 0.2
    exp0._coeffs[1, 1] = 0.5
    exp0._coeffs[2, 3] = -0.5
    exp0._coeffs[3, 2] = 0.5
    # normalize
    exp0.gram_schmidt()

    # Check normalization again
    exp0.check_normalization(olp)

    assert exp0.coeffs[0, 0] == 1.0
    assert exp0.coeffs[1, 1] == 1.0
    assert exp0.coeffs[2, 2] == np.sqrt(0.8)
    assert exp0.coeffs[3, 3] == np.sqrt(0.8)
    assert exp0.coeffs[2, 3] == -np.sqrt(0.2)
    assert exp0.coeffs[3, 2] == np.sqrt(0.2)
