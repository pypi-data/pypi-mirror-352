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

from pybest import filemanager
from pybest.exceptions import ArgumentError, MatrixShapeError
from pybest.io import load_h5
from pybest.iodata import IOData
from pybest.linalg import (
    DenseFourIndex,
    DenseOrbital,
    DenseThreeIndex,
    DenseTwoIndex,
)
from pybest.linalg.cholesky import CholeskyFourIndex, CholeskyLinalgFactory
from pybest.utility import check_options


def test_linalg_factory_constructors():
    lf = CholeskyLinalgFactory(5)
    assert lf.default_nbasis == 5
    lf = CholeskyLinalgFactory()
    assert lf.default_nbasis is None
    lf.default_nbasis = 10

    # Four-index tests
    op4 = lf.create_four_index(nvec=8)
    assert isinstance(op4, CholeskyFourIndex)
    lf.create_four_index.__check_init_args__(lf, op4, nvec=8)
    assert op4.nbasis == 10
    assert op4.nvec == 8
    assert op4.shape == (10, 10, 10, 10)
    assert not op4.is_decoupled

    op4 = lf.create_four_index(8, 4)
    lf.create_four_index.__check_init_args__(lf, op4, 8, 4)
    assert op4.nbasis == 8
    assert op4.nvec == 4
    assert not op4.is_decoupled

    array = np.random.normal(0, 1, (5, 10, 10))
    op4 = lf.create_four_index(10, array=array)
    lf.create_four_index.__check_init_args__(lf, op4, nvec=5)
    assert op4._array is array
    assert op4._array2 is array
    assert op4.nbasis == 10
    assert op4.nvec == 5
    assert not op4.is_decoupled

    array2 = np.random.normal(0, 1, (5, 10, 10))
    op4 = lf.create_four_index(10, array=array, array2=array2)
    lf.create_four_index.__check_init_args__(lf, op4, nvec=5)
    assert op4._array is array
    assert op4._array2 is array2
    assert op4.nbasis == 10
    assert op4.nvec == 5
    assert op4.is_decoupled


def test_linalg_hdf5():
    # without default nbasis
    lf1 = CholeskyLinalgFactory()
    with h5.File(
        "pybest.linalg.test.test_cholesky.test_linalg_hdf5.h5",
        driver="core",
        backing_store=False,
        mode="w",
    ) as f:
        lf1.to_hdf5(f)
        lf2 = CholeskyLinalgFactory.from_hdf5(f)
        assert isinstance(lf2, CholeskyLinalgFactory)
        assert lf2.default_nbasis is None
        lf3 = load_h5(f)
        assert isinstance(lf3, CholeskyLinalgFactory)
        assert lf3.default_nbasis is None

    # with default nbasis
    lf1 = CholeskyLinalgFactory(13)
    with h5.File(
        "pybest.linalg.test.test_cholesky.test_linalg_hdf5.h5",
        driver="core",
        backing_store=False,
        mode="w",
    ) as f:
        lf1.to_hdf5(f)
        lf2 = CholeskyLinalgFactory.from_hdf5(f)
        assert isinstance(lf2, CholeskyLinalgFactory)
        assert lf2.default_nbasis == 13
        lf3 = load_h5(f)
        assert isinstance(lf3, CholeskyLinalgFactory)
        assert lf3.default_nbasis == 13


def test_linalg_objects_del():
    lf = CholeskyLinalgFactory()
    with pytest.raises(ArgumentError):
        lf.create_four_index()


#
# Tests on the CholeskyFourIndex stuff
#


def get_four_cho_dense(nbasis=10, nvec=8, sym=8):
    """Create random 2-index Cholesky vectors and matching dense four-index object

    **Optional arguments:**

    nbasis
         The number of basis functions

    nvec
         The number of Cholesky vectors

    sym
         The amount of symmetries in the FourIndex object. See
         :ref:`dense_matrix_symmetry` for more details.
    """
    check_options("sym", sym, 1, 2, 4, 8)
    cho = CholeskyFourIndex(nbasis, nvec)
    if sym in (1, 4):
        cho.decouple_array2()
    cho.randomize()
    cho.symmetrize(sym)
    dense = DenseFourIndex(nbasis)
    dense._array[:] = np.einsum("kac,kbd->abcd", cho._array, cho._array2)
    assert dense.is_symmetric(sym)
    assert cho.is_symmetric(sym)
    return cho, dense


def test_four_index_hdf5():
    lf = CholeskyLinalgFactory(5)
    a = lf.create_four_index(5, 3)
    a.randomize()
    with h5.File(
        "pybest.linalg.test.test_cholesky.test_four_index_hdf5",
        driver="core",
        backing_store=False,
        mode="w",
    ) as f:
        a.to_hdf5(f)
        b = CholeskyFourIndex.from_hdf5(f)
        assert a == b


def test_four_index_copy_new_randomize_clear_assign():
    lf = CholeskyLinalgFactory(5)
    for args in (None, 3), (4, 3):
        a = lf.create_four_index(*args)
        b = a.copy()
        b.randomize()
        assert a != b
        c = b.copy()
        c.new.__check_init_args__(c, b)
        assert b == c
        d = c.new()
        assert a == d
        b.assign(c)
        assert b == c


def test_four_index_iscale():
    lf = CholeskyLinalgFactory()
    op = lf.create_four_index(3, 2)
    op.randomize()
    tmp = op._array.copy()
    op.iscale(3.0)
    assert abs(op._array - 3**0.5 * tmp).max() < 1e-10
    assert abs(op._array2 - 3**0.5 * tmp).max() < 1e-10
    op.decouple_array2()
    op.randomize()
    tmp = op._array.copy()
    tmp2 = op._array2.copy()
    op.iscale(3.0)
    assert abs(op._array - 3**0.5 * tmp).max() < 1e-10
    assert abs(op._array2 - 3**0.5 * tmp2).max() < 1e-10


def test_four_index_get():
    cho, dense = get_four_cho_dense(nbasis=3, sym=1)
    for i0 in range(dense.shape[0]):
        for i1 in range(dense.shape[1]):
            for i2 in range(dense.shape[2]):
                for i3 in range(dense.shape[3]):
                    assert (
                        abs(
                            cho.get_element(i0, i1, i2, i3)
                            - dense.get_element(i0, i1, i2, i3)
                        )
                        < 1e-10
                    )


def test_four_index_is_symmetric():
    for sym in 1, 2, 4, 8:
        cho = get_four_cho_dense(sym=sym)[0]
        assert cho.is_symmetric(sym)


def test_four_index_symmetrize():
    lf = CholeskyLinalgFactory(20)
    op = lf.create_four_index(nvec=8)
    for symmetry in 1, 2, 4, 8:
        op.decouple_array2()
        op.randomize()
        op.symmetrize(symmetry)
        assert op.is_symmetric(symmetry, 0, 0)


def test_four_index_symmetrize_order_of_operations():
    lf = CholeskyLinalgFactory(20)
    op = lf.create_four_index(nvec=8)
    for symmetry in 1, 2, 4, 8:
        op.decouple_array2()
        # ugly hack to have matrix elements with very different order of
        # magnitudes
        op._array[:] = 10 ** np.random.uniform(-20, 20, (8, 20, 20))
        op._array2[:] = 10 ** np.random.uniform(-20, 20, (8, 20, 20))
        op.symmetrize(symmetry)
        assert op.is_symmetric(symmetry, 0, 0)


def test_four_index_itranspose():
    for sym in 1, 2, 4, 8:
        cho = get_four_cho_dense(sym=sym)[0]
        cho.itranspose()
        assert cho.is_symmetric(sym)


def check_four_sum(sym):
    cho, dense = get_four_cho_dense(sym=sym)
    assert np.allclose(dense.sum(), cho.sum())


def test_four_sum_1():
    check_four_sum(1)


def test_four_sum_2():
    check_four_sum(2)


def test_four_sum_4():
    check_four_sum(4)


def test_four_sum_8():
    check_four_sum(8)


def check_four_slice(sym):
    cho, dense = get_four_cho_dense(sym=sym)

    for subscripts in "abab->ab", "aabb->ab", "abba->ab":
        # Return value
        factor = np.random.uniform(1, 2)
        assert np.allclose(
            dense.contract(
                subscripts, factor=factor, clear=True, select="einsum"
            )._array,
            cho.contract(
                subscripts, factor=factor, clear=True, select="einsum"
            )._array,
        )
        # Output argument
        dense_out = DenseTwoIndex(dense.nbasis)
        cho_out = DenseTwoIndex(cho.nbasis)
        dense.contract(
            subscripts,
            out=dense_out,
            factor=factor,
            clear=True,
            select="einsum",
        )
        cho.contract(
            subscripts, out=cho_out, factor=factor, clear=True, select="einsum"
        )
        assert np.allclose(dense_out._array, cho_out._array)
        # Output argument without clear
        factor = np.random.uniform(1, 2)
        dense.contract(
            subscripts,
            out=dense_out,
            factor=factor,
            select="einsum",
        )
        cho.contract(
            subscripts,
            out=cho_out,
            factor=factor,
            select="einsum",
        )
        assert np.allclose(dense_out._array, cho_out._array)

    for subscripts in "abcc->bac", "abcc->abc":  # , 'abcb->abc', 'abbc->abc':
        # Return value
        factor = np.random.uniform(1, 2)
        assert np.allclose(
            dense.contract(
                subscripts, factor=factor, clear=True, select="einsum"
            )._array,
            cho.contract(
                subscripts, factor=factor, clear=True, select="einsum"
            )._array,
        )
        # Output argument
        dense_out = DenseThreeIndex(dense.nbasis)
        cho_out = DenseThreeIndex(cho.nbasis)
        dense.contract(
            subscripts,
            out=dense_out,
            factor=factor,
            clear=True,
            select="einsum",
        )
        cho.contract(
            subscripts, out=cho_out, factor=factor, clear=True, select="einsum"
        )
        assert np.allclose(dense_out._array, cho_out._array)
        # Output argument without clear
        factor = np.random.uniform(1, 2)
        dense.contract(
            subscripts,
            out=dense_out,
            factor=factor,
            select="einsum",
        )
        cho.contract(
            subscripts,
            out=cho_out,
            factor=factor,
            select="einsum",
        )
        assert np.allclose(dense_out._array, cho_out._array)


@pytest.mark.parametrize("symm", [1, 2, 4, 8])
def test_four_slice(symm):
    check_four_slice(symm)


def check_four_index_transform(sym_in, sym_exp, method):
    """Test driver for four-index transform

    **Arguments:**

    sym_in
         The symmetry of the four-index object in the AO basis.

    sym_exp
         The symmetry of the orbitals used for the four-index transform.

    method
         'tensordot' or 'einsum'
    """
    cho, dense = get_four_cho_dense(sym=sym_in)
    dense_mo = dense.new()
    cho_mo = cho.new()
    if sym_exp == 8:
        exp0 = DenseOrbital(dense.nbasis)
        exp0.randomize()
        try:
            dense_mo.assign_four_index_transform(dense, exp0, method=method)
        except Exception:
            dense_mo.assign_four_index_transform(dense, exp0)
        cho_mo.assign_four_index_transform(cho, exp0, method=method)
        assert cho_mo.is_decoupled == cho.is_decoupled
    elif sym_exp == 4:
        exp0 = DenseOrbital(dense.nbasis)
        exp0.randomize()
        exp1 = DenseOrbital(dense.nbasis)
        exp1.randomize()
        dense_mo.assign_four_index_transform(dense, exp0, exp1, method=method)
        cho_mo.assign_four_index_transform(cho, exp0, exp1, method=method)
        assert cho_mo.is_decoupled
    elif sym_exp == 2:
        exp0 = DenseOrbital(dense.nbasis)
        exp0.randomize()
        exp2 = DenseOrbital(dense.nbasis)
        exp2.randomize()
        dense_mo.assign_four_index_transform(
            dense, exp0, exp2=exp2, method=method
        )
        cho_mo.assign_four_index_transform(cho, exp0, exp2=exp2, method=method)
        assert cho_mo.is_decoupled == cho.is_decoupled
    elif sym_exp == 1:
        exp0 = DenseOrbital(dense.nbasis)
        exp0.randomize()
        exp1 = DenseOrbital(dense.nbasis)
        exp1.randomize()
        exp2 = DenseOrbital(dense.nbasis)
        exp2.randomize()
        exp3 = DenseOrbital(dense.nbasis)
        exp3.randomize()
        dense_mo.assign_four_index_transform(
            dense, exp0, exp1, exp2, exp3, method=method
        )
        cho_mo.assign_four_index_transform(
            cho, exp0, exp1, exp2, exp3, method=method
        )
        assert cho_mo.is_decoupled
    else:
        raise ValueError
    assert np.allclose(dense_mo._array, cho_mo.get_dense()._array)
    sym_and = symmetry_and(sym_in, sym_exp)
    assert cho_mo.is_symmetric(sym_and)
    assert dense_mo.is_symmetric(sym_and)


def symmetry_and(sym1, sym2):
    def to_mask(sym):
        return {1: 0, 2: 1, 4: 2, 8: 3}[sym]

    def from_mask(mask):
        return {0: 1, 1: 2, 2: 4, 3: 8}[mask]

    return from_mask(to_mask(sym1) & to_mask(sym2))


@pytest.mark.parametrize("sym1", [1, 2, 4, 8])
@pytest.mark.parametrize("sym2", [1, 2, 4, 8])
@pytest.mark.parametrize("select", ["tensordot", "einsum", "cupy"])
def test_four_index_transform(sym1, sym2, select):
    check_four_index_transform(sym1, sym2, select)


def test_cholesky_einsum_index():
    examples = [("abcd", "xac,xbd"), ("xoxo", "ixx,ioo"), ("hejk", "xhj,xek")]
    clf = CholeskyLinalgFactory(2)
    cholesky = clf.create_four_index(nvec=10)
    for example in examples:
        assert cholesky.einsum_index(example[0]) == example[1]


def test_cholesky_arrays():
    clf = CholeskyLinalgFactory(2)
    cholesky = clf.create_four_index(nvec=10)
    arrays = cholesky.arrays
    assert len(arrays) == 2, isinstance(arrays[0], np.ndarray)


def test_cholesky_dump():
    clf = CholeskyLinalgFactory(5)
    cholesky = clf.create_four_index(nvec=10, label="cd-eri")
    cholesky.randomize()

    dump = IOData(eri=cholesky)
    dump.to_file(f"{filemanager.temp_dir}/checkpoint_eri.h5")

    er_ = IOData.from_file(f"{filemanager.temp_dir}/checkpoint_eri.h5")
    eri = er_.eri

    assert eri == cholesky
    # Test extra for label as it is not checked by default
    assert eri.label == cholesky.label
    assert eri.label == "cd-eri"


def test_cholesky_from_array():
    """Checks if Cholesky instance has expected shape."""
    cholesky = CholeskyFourIndex(10, 2)
    array = np.ones((2, 3, 4))
    array2 = np.random.rand(2, 5, 6)
    cholesky.from_array(array, array2=array2)
    assert cholesky.shape == (3, 5, 4, 6)
    assert cholesky.array.shape == (2, 3, 4)
    assert cholesky.array2.shape == (2, 5, 6)


def test_cholesky_from_nbasis():
    """Checks if Cholesky instance has expected shape."""
    cholesky = CholeskyFourIndex(10, 2)
    cholesky.from_nbasis(10, 2, nbasis1=3, nbasis2=4, nbasis3=5)
    assert cholesky.shape == (2, 3, 4, 5)
    assert cholesky.array.shape == (10, 2, 4)
    assert cholesky.array2.shape == (10, 3, 5)


def test_cholesky_init_irregular():
    """Tests if irregular-shaped decomposed matrix can be initialized."""
    clf = CholeskyLinalgFactory(5)
    kwargs = {"nvec": 10, "nbasis": 1, "nbasis1": 2, "nbasis2": 3}
    cholesky = clf.create_four_index(**kwargs)
    cholesky.randomize()
    assert isinstance(cholesky, CholeskyFourIndex)
    assert cholesky.shape == (1, 2, 3, 1)
    assert cholesky.nvec == 10


def test_cholesky_assign_irregular_block():
    """Tests if irregular-shaped decomposed matrix can be assigned."""
    clf = CholeskyLinalgFactory(5)
    chol_0 = clf.create_four_index(3, nvec=5)
    chol_0.randomize()
    kwargs = {"nvec": 5, "nbasis": 3, "nbasis1": 2, "nbasis2": 1}
    chol_1 = clf.create_four_index(**kwargs)
    assert chol_0.shape == (3, 3, 3, 3)
    assert chol_1.shape == (3, 2, 1, 3)
    # Check if we can assign values from chol_0 to chol_1
    chol_1.assign(chol_0, begin5=1, end6=1)
    assert chol_1.array is not chol_1.array2
    assert chol_0.shape == (3, 3, 3, 3)
    assert chol_1.shape == (3, 2, 1, 3)
    assert chol_1.nvec == 5
    assert np.allclose(chol_1.array[:, :, :], chol_0.array[:, :, :1])
    assert np.allclose(chol_1.array2[:, :, :], chol_0.array2[:, 1:, :])


def test_cholesky_assign_irregular_block_v2():
    """Tests if irregular-shaped decomposed matrix can be assigned."""
    clf = CholeskyLinalgFactory(5)
    chol_0 = clf.create_four_index(3, nvec=5)
    chol_0.randomize()
    kwargs = {"nvec": 5, "nbasis": 3, "nbasis1": 2, "nbasis2": 1}
    chol_1 = clf.create_four_index(**kwargs)
    # Check if we can assign values from chol_0 to chol_1
    with pytest.raises(MatrixShapeError):
        chol_1.assign(chol_0, begin5=0, end6=1)


def test_cholesky_copy_irregular_block():
    """Tests if block of Cholesky can be copied."""
    clf = CholeskyLinalgFactory(5)
    array = np.arange(1.0, 7.0).reshape((3, 1, 2))
    cholesky = clf.create_four_index(array=array)
    block = cholesky.copy(begin2=1, end3=2)
    assert isinstance(block, CholeskyFourIndex)
    assert block.shape == (1, 1, 1, 2)
    assert block.nvec == 3
    assert block.array[0, 0, 0] == 2.0
    assert block.array2[0, 0, 0] == 1.0
    block.get_dense(select="einsum")
    assert np.allclose(block.array[:, :, :], cholesky.array[:, :, 1:])
    assert np.allclose(block.array2[:, :, :], cholesky.array2[:, :3, :])


def test_cholesky_view_irregular_block():
    """Tests if block of Cholesky can be copied."""
    clf = CholeskyLinalgFactory(5)
    array = np.arange(1, 7).reshape((3, 1, 2))
    cholesky = clf.create_four_index(array=array)
    block = cholesky.view(begin2=1, end3=2)
    assert isinstance(block, CholeskyFourIndex)
    assert block.shape == (1, 1, 1, 2)
    assert block.nvec == 3
    assert np.allclose(block.array[:, :, :], cholesky.array[:, :, 1:])
    assert np.allclose(block.array2[:, :, :], cholesky.array2[:, :, :3])
    assert np.shares_memory(cholesky.array, block.array)
    assert np.shares_memory(cholesky.array2, block.array2)


def test_cholesky_array_setter_creates_view():
    clf = CholeskyLinalgFactory(3)
    cholesky = clf.create_four_index(nvec=4)
    new_array = np.arange(1, 37).reshape((4, 3, 3))
    cholesky.array = new_array
    assert cholesky.array is new_array


def test_cholesky_array_setter_sets_array2():
    clf = CholeskyLinalgFactory(3)
    cholesky = clf.create_four_index(nvec=4)
    new_array = np.arange(1, 37).reshape((4, 3, 3))
    cholesky.array = new_array
    assert cholesky.array is new_array
    assert cholesky.array2 is cholesky.array


def test_cholesky_array_setter_creates_copy():
    clf = CholeskyLinalgFactory(3)
    cholesky = clf.create_four_index(nvec=4)
    new_array = np.arange(2, 38).reshape((4, 3, 3))
    cholesky.array[:] = new_array
    assert cholesky.array is not new_array
    assert np.allclose(cholesky.array, new_array)


def test_cholesky_array_setter_raises_error_if_wrong_shape():
    clf = CholeskyLinalgFactory(3)
    cholesky = clf.create_four_index(nvec=4)
    array_with_wrong_shape = np.arange(1, 10).reshape((3, 3))
    with pytest.raises(ArgumentError):
        cholesky.array = array_with_wrong_shape


def test_cholesky_array_setter_raises_error_if_different_nvec():
    clf = CholeskyLinalgFactory(3)
    cholesky = clf.create_four_index(nvec=4)
    array_with_wrong_nvec = np.arange(1, 28).reshape((3, 3, 3))
    with pytest.raises(ArgumentError):
        cholesky.array = array_with_wrong_nvec


def test_cholesky_array2_setter_creates_view():
    clf = CholeskyLinalgFactory(3)
    cholesky = clf.create_four_index(nvec=4)
    new_array = np.arange(1, 37).reshape((4, 3, 3))
    cholesky.array2 = new_array
    assert cholesky.array2 is new_array


def test_cholesky_array2_setter_does_not_set_array():
    clf = CholeskyLinalgFactory(3)
    cholesky = clf.create_four_index(nvec=4)
    new_array = np.arange(1, 37).reshape((4, 3, 3))
    cholesky.array2 = new_array
    assert cholesky.array is not cholesky.array2
    assert not np.allclose(cholesky.array, cholesky.array2)


def test_cholesky_array2_setter_creates_a_copy():
    clf = CholeskyLinalgFactory(3)
    cholesky = clf.create_four_index(nvec=4)
    new_array = np.arange(1, 37).reshape((4, 3, 3))
    cholesky.array2[:] = new_array
    assert cholesky.array is not new_array
    assert np.allclose(cholesky.array2, new_array)


def test_cholesky_array2_setter_raises_error_if_wrong_shape():
    clf = CholeskyLinalgFactory(3)
    cholesky = clf.create_four_index(nvec=4)
    array_with_wrong_shape = np.arange(1, 10).reshape((3, 3))
    with pytest.raises(ArgumentError):
        cholesky.array2 = array_with_wrong_shape


def test_cholesky_array2_setter_raises_error_if_different_nvec():
    clf = CholeskyLinalgFactory(3)
    cholesky = clf.create_four_index(nvec=4)
    array_with_wrong_nvec = np.arange(1, 28).reshape((3, 3, 3))
    with pytest.raises(ArgumentError):
        cholesky.array2 = array_with_wrong_nvec
