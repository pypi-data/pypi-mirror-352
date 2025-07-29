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

from pybest.io import load_h5
from pybest.linalg import (
    DenseFourIndex,
    DenseLinalgFactory,
    DenseOneIndex,
    DenseOrbital,
    DenseThreeIndex,
    DenseTwoIndex,
)

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


#
# DenseLinalgFactory tests
#


def test_linalg_factory_constructors():
    lf = DenseLinalgFactory(5)
    assert lf.default_nbasis == 5
    lf = DenseLinalgFactory()
    assert lf.default_nbasis is None
    lf.default_nbasis = 10

    # One-index tests
    op1 = lf.create_one_index()
    assert isinstance(op1, DenseOneIndex)
    lf.create_one_index.__check_init_args__(lf, op1)
    assert op1.nbasis == 10
    assert op1.shape == (10,)
    op1 = lf.create_one_index(12)
    lf.create_one_index.__check_init_args__(lf, op1, 12)
    assert op1.nbasis == 12

    # Orbital tests
    ex = lf.create_orbital()
    assert isinstance(ex, DenseOrbital)
    lf.create_orbital.__check_init_args__(lf, ex)
    assert ex.nbasis == 10
    assert ex.nfn == 10
    assert ex.coeffs.shape == (10, 10)
    assert ex.energies.shape == (10,)
    assert ex.occupations.shape == (10,)
    ex = lf.create_orbital(12)
    lf.create_orbital.__check_init_args__(lf, ex, 12)
    assert ex.nbasis == 12
    assert ex.nfn == 12
    assert ex.coeffs.shape == (12, 12)
    assert ex.energies.shape == (12,)
    assert ex.occupations.shape == (12,)
    ex = lf.create_orbital(12, 10)
    lf.create_orbital.__check_init_args__(lf, ex, 12, 10)
    assert ex.nbasis == 12
    assert ex.nfn == 10
    assert ex.coeffs.shape == (12, 10)
    assert ex.energies.shape == (10,)
    assert ex.occupations.shape == (10,)

    # Two-index tests
    op2 = lf.create_two_index()
    assert isinstance(op2, DenseTwoIndex)
    lf.create_two_index.__check_init_args__(lf, op2)
    assert op2.nbasis == 10
    assert op2.shape == (10, 10)
    assert op2.nbasis1 == 10
    op2 = lf.create_two_index(12)
    lf.create_two_index.__check_init_args__(lf, op2, 12)
    assert op2.nbasis == 12
    assert op2.shape == (12, 12)
    assert op2.nbasis1 == 12
    op2 = lf.create_two_index(10, 12)
    lf.create_two_index.__check_init_args__(lf, op2, 10, 12)
    assert op2.shape == (10, 12)
    assert op2.nbasis == 10
    assert op2.nbasis1 == 12

    # Three-index tests
    op3 = lf.create_three_index()
    assert isinstance(op3, DenseThreeIndex)
    lf.create_three_index.__check_init_args__(lf, op3)
    assert op3.nbasis == 10
    assert op3.shape == (10, 10, 10)
    op3 = lf.create_three_index(8)
    lf.create_three_index.__check_init_args__(lf, op3, 8)
    assert op3.nbasis == 8

    # Four-index tests
    op4 = lf.create_four_index()
    assert isinstance(op4, DenseFourIndex)
    lf.create_four_index.__check_init_args__(lf, op4)
    assert op4.nbasis == 10
    assert op4.shape == (10, 10, 10, 10)
    op4 = lf.create_four_index(8)
    lf.create_four_index.__check_init_args__(lf, op4, 8)
    assert op4.nbasis == 8


def test_linalg_hdf5():
    # without default nbasis
    lf1 = DenseLinalgFactory()
    with h5.File(
        "pybest.linalg.test.test_dense.test_linalg_hdf5.h5",
        driver="core",
        backing_store=False,
        mode="w",
    ) as f:
        lf1.to_hdf5(f)
        lf2 = DenseLinalgFactory.from_hdf5(f)
        assert isinstance(lf2, DenseLinalgFactory)
        assert lf2.default_nbasis is None
        lf3 = load_h5(f)
        assert isinstance(lf3, DenseLinalgFactory)
        assert lf3.default_nbasis is None

    # with default nbasis
    lf1 = DenseLinalgFactory(13)
    with h5.File(
        "pybest.linalg.test.test_dense.test_linalg_hdf5.h5",
        driver="core",
        backing_store=False,
        mode="w",
    ) as f:
        lf1.to_hdf5(f)
        lf2 = DenseLinalgFactory.from_hdf5(f)
        assert isinstance(lf2, DenseLinalgFactory)
        assert lf2.default_nbasis == 13
        lf3 = load_h5(f)
        assert isinstance(lf3, DenseLinalgFactory)
        assert lf3.default_nbasis == 13


def test_linalg_objects_del():
    lf = DenseLinalgFactory()
    with pytest.raises(TypeError):
        lf.create_one_index()
    with pytest.raises(TypeError):
        lf.create_orbital()
    with pytest.raises(TypeError):
        lf.create_two_index()
    with pytest.raises(TypeError):
        lf.create_three_index()
    with pytest.raises(TypeError):
        lf.create_four_index()


def test_allocate_check_output():
    # OneIndex
    lf = DenseLinalgFactory(5)
    op = lf.create_one_index()
    re = lf.allocate_check_output(op, (5,))
    assert op is re
    re = lf.allocate_check_output(None, (5,))
    assert isinstance(re, DenseOneIndex)
    assert re.shape == (5,)

    # TwoIndex
    lf = DenseLinalgFactory(5)
    op = lf.create_two_index()
    re = lf.allocate_check_output(op, (5, 5))
    assert op is re
    re = lf.allocate_check_output(None, (5, 5))
    assert isinstance(re, DenseTwoIndex)
    assert re.shape == (5, 5)

    # ThreeIndex
    lf = DenseLinalgFactory(5)
    op = lf.create_three_index()
    re = lf.allocate_check_output(op, (5, 5, 5))
    assert op is re
    re = lf.allocate_check_output(None, (5, 5, 5))
    assert isinstance(re, DenseThreeIndex)
    assert re.shape == (5, 5, 5)

    # FourIndex
    lf = DenseLinalgFactory(5)
    op = lf.create_four_index()
    re = lf.allocate_check_output(op, (5, 5, 5, 5))
    assert op is re
    re = lf.allocate_check_output(None, (5, 5, 5, 5))
    assert isinstance(re, DenseFourIndex)
    assert re.shape == (5, 5, 5, 5)


#
# DenseOneIndex tests
#


def test_one_index_einsum_index():
    dlf = DenseLinalgFactory(2)
    dense = dlf.create_one_index()
    assert dense.einsum_index("a") == "a"


def test_one_index_arrays():
    dlf = DenseLinalgFactory(2)
    dense = dlf.create_one_index()
    arrays = dense.arrays
    assert len(arrays) == 1, isinstance(arrays[0], np.ndarray)


def test_one_index_array_setter_set_new_array():
    new_array = np.ones(6)
    lf = DenseLinalgFactory(6)
    op = lf.create_one_index()
    op.array = new_array
    assert op.array is new_array
    assert np.allclose(op.array, new_array)


def test_one_index_array_setter_new_array_indexing():
    new_array = np.ones(6)
    lf = DenseLinalgFactory(6)
    op = lf.create_one_index()
    op.array[:] = new_array
    assert op.array is not new_array
    assert np.allclose(op.array, new_array)


def test_one_index_array_slice_setter_indexing():
    new_array = np.ones(7)
    lf = DenseLinalgFactory(5)
    op = lf.create_one_index()
    op.array[1:4] = new_array[2:5]
    assert op.array is not new_array
    assert np.allclose(op.array[1:4], new_array[2:5])


def test_one_index_hdf5():
    lf = DenseLinalgFactory(5)
    for args in (None,), (4,):
        a = lf.create_one_index(*args)
        a.randomize()
        with h5.File(
            "pybest.linalg.test.test_dens.test_one_index_hdf5",
            driver="core",
            backing_store=False,
            mode="w",
        ) as f:
            a.to_hdf5(f)
            b = DenseOneIndex.from_hdf5(f)
            assert a == b


def test_one_index_copy_new_randomize_clear_assign():
    lf = DenseLinalgFactory(5)
    for args in (None,), (4,):
        a = lf.create_one_index(*args)
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
        e = b.copy(1, 3)
        assert e._array.shape[0] == 2
        assert (e._array == b._array[1:3]).all()
        b.clear()
        b.assign(e, 1, 3)
        assert (e._array == b._array[1:3]).all()
        assert ((e._array - b._array[1:3]) == 0).all()


def test_one_index_permute_basis():
    lf = DenseLinalgFactory(5)
    for _i in range(10):
        forth, back = get_forth_back(5)
        a = lf.create_one_index()
        a.randomize()
        b = a.copy()
        b.permute_basis(forth)
        assert a != b
        b.permute_basis(back)
        assert a == b


def test_one_index_change_basis_signs():
    lf = DenseLinalgFactory(5)
    for _i in range(10):
        signs = get_signs(5)
        a = lf.create_one_index()
        a.randomize()
        b = a.copy()
        b.change_basis_signs(signs)
        assert a != b
        b.change_basis_signs(signs)
        assert a == b


def test_one_index_iadd():
    lf = DenseLinalgFactory(5)
    a = lf.create_one_index()
    a.randomize()
    b = lf.create_one_index()
    b.randomize()
    c = b.copy()
    factor = np.random.uniform(1, 2)
    c.iadd(a, factor)
    for i in range(5):
        assert factor * a.get_element(i) + b.get_element(i) == c.get_element(i)


def test_one_index_iscale():
    lf = DenseLinalgFactory()
    op = lf.create_one_index(3)
    op.randomize()
    tmp = op._array.copy()
    op.iscale(3.0)
    assert abs(op._array - 3 * tmp).max() < 1e-10


def test_one_index_norm():
    lf = DenseLinalgFactory(6)
    op = lf.create_one_index()
    op.randomize()
    norm = op.norm()
    assert (norm - np.linalg.norm(op._array)) < 1e-10


def test_one_index_get_set():
    lf = DenseLinalgFactory()
    op = lf.create_one_index(3)
    op.set_element(1, 1.2)
    assert op.get_element(1) == 1.2


def test_one_index_trace():
    lf = DenseLinalgFactory(5)
    inp = lf.create_one_index()
    inp.randomize()
    out = inp.trace()
    assert out == np.sum(inp._array)
    out = inp.trace(1, 3)
    assert out == np.sum(inp._array[1:3])


def test_one_index_get_max():
    lf = DenseLinalgFactory(5)
    inp = lf.create_one_index()
    inp.randomize()
    out = inp.get_max()
    assert out == np.max(np.abs(inp._array))


def test_one_index_sort_indices():
    lf = DenseLinalgFactory(5)
    op = lf.create_one_index()
    op.randomize()
    sortedlist = op.sort_indices(False)
    assert (
        sortedlist
        == np.argsort(op._array, axis=-1, kind="mergesort", order=None)[::-1]
    ).all()
    sortedlistreverse = op.sort_indices(True)
    assert (
        sortedlistreverse
        == np.argsort(op._array, axis=-1, kind="mergesort", order=None)
    ).all()


def test_one_index_mult():
    lf = DenseLinalgFactory(5)
    inp = lf.create_one_index()
    one = lf.create_one_index()
    inp.randomize()
    one.randomize()
    out = inp.mult(one, factor=1.3)
    assert np.allclose(out._array, 1.3 * (inp._array * one._array))
    foo = inp.mult(one, out=out, factor=1.4)
    assert foo is out
    assert np.allclose(out._array, 1.4 * (inp._array * one._array))


def test_one_index_dot():
    lf = DenseLinalgFactory(5)
    inp = lf.create_one_index()
    one = lf.create_one_index()
    inp.randomize()
    one.randomize()
    out = inp.dot(one, factor=1.3)
    assert out == 1.3 * np.dot(inp._array, one._array)


def test_one_index_divide():
    lf = DenseLinalgFactory(5)
    inp = lf.create_one_index()
    one = lf.create_one_index()
    inp.randomize()
    one.randomize()
    out = inp.divide(one, factor=1.3)
    assert np.allclose(out._array, 1.3 * np.divide(inp._array, one._array))
    foo = inp.divide(one, factor=1.4, out=out)
    assert foo is out
    assert np.allclose(out._array, 1.4 * np.divide(inp._array, one._array))


#
# DenseTwoIndex tests
#


def test_two_index_einsum_index():
    dlf = DenseLinalgFactory(2)
    dense = dlf.create_two_index()
    assert dense.einsum_index("ab") == "ab"


def test_two_index_arrays():
    dlf = DenseLinalgFactory(2)
    dense = dlf.create_two_index()
    arrays = dense.arrays
    assert len(arrays) == 1, isinstance(arrays[0], np.ndarray)


def test_two_index_array_setter():
    new_array = np.ones((6, 6))
    lf = DenseLinalgFactory(6)
    op = lf.create_two_index()
    op.array = new_array
    assert op.array is new_array
    assert np.allclose(op.array, new_array)


def test_two_index_array_setter_indexing():
    new_array = np.ones((6, 6))
    lf = DenseLinalgFactory(6)
    op = lf.create_two_index()
    op.array[:] = new_array
    assert op.array is not new_array
    assert np.allclose(op.array, new_array)


def test_two_index_array_slice_setter_indexing():
    new_array = np.ones((7, 6))
    lf = DenseLinalgFactory(5)
    op = lf.create_two_index()
    op.array[1:4, 2:5] = new_array[4:7, 3:6]
    assert op.array is not new_array
    assert np.allclose(op.array[1:4, 2:5], new_array[4:7, 3:6])


def test_two_index_hdf5():
    lf = DenseLinalgFactory(5)
    for args in (None,), (4,), (5, 6):
        a = lf.create_two_index(*args)
        a.randomize()
        with h5.File(
            "pybest.linalg.test.test_dens.test_two_index_hdf5",
            driver="core",
            backing_store=False,
            mode="w",
        ) as f:
            a.to_hdf5(f)
            b = DenseTwoIndex.from_hdf5(f)
            assert a == b


def test_two_index_copy_new_randomize_clear_assign():
    lf = DenseLinalgFactory(5)
    for args in (None,), (4,), (5, 6):
        a = lf.create_two_index(*args)
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
        e = b.copy(0, 3, 2, 4)
        assert e._array.shape[0] == 3
        assert e._array.shape[1] == 2
        assert (e._array == b._array[0:3, 2:4]).all()


def test_two_index_assign():
    lf = DenseLinalgFactory()
    op1 = lf.create_two_index(3)
    op2 = lf.create_two_index(3)
    op1._array[:] = np.random.uniform(0, 1, (3, 3))
    op2.assign(op1)
    assert (op1._array == op2._array).all()


def test_two_index_copy():
    lf = DenseLinalgFactory()
    op1 = lf.create_two_index(3)
    op1._array[:] = np.random.uniform(0, 1, (3, 3))
    op2 = op1.copy()
    assert (op1._array == op2._array).all()


def test_two_index_permute_basis():
    lf = DenseLinalgFactory(5)
    for _i in range(10):
        i0, i1 = np.random.randint(0, 5, 2)
        forth, back = get_forth_back(5)
        a = lf.create_two_index()
        a.randomize()
        b = a.copy()
        b.permute_basis(forth)
        assert a != b
        assert a.get_element(i0, i1) == b.get_element(back[i0], back[i1])
        b.permute_basis(back)
        assert a == b


def test_two_index_change_basis_signs():
    lf = DenseLinalgFactory(5)
    for _i in range(10):
        signs = get_signs(5)
        a = lf.create_two_index()
        a.randomize()
        b = a.copy()
        b.change_basis_signs(signs)
        assert a != b
        b.change_basis_signs(signs)
        assert a == b


def test_two_index_iadd():
    lf = DenseLinalgFactory()
    a = lf.create_two_index(5, 5)
    a.randomize()
    b = lf.create_two_index(5, 5)
    b.randomize()
    c = b.copy()
    factor = np.random.uniform(1, 2)
    # normal usage
    c.iadd(a, factor)
    for i0 in range(5):
        for i1 in range(5):
            assert factor * a.get_element(i0, i1) + b.get_element(
                i0, i1
            ) == c.get_element(i0, i1)
    # transpose usage
    c.assign(b)
    c.iadd(a, factor, transpose=True)
    for i0 in range(5):
        for i1 in range(5):
            assert factor * a.get_element(i1, i0) + b.get_element(
                i0, i1
            ) == c.get_element(i0, i1)
    # transpose usage
    c.assign(b)
    c.iadd_t(a, factor)
    for i0 in range(5):
        for i1 in range(5):
            assert factor * a.get_element(i1, i0) + b.get_element(
                i0, i1
            ) == c.get_element(i0, i1)
    # constant
    c.assign(b)
    c.iadd(factor)
    for i0 in range(5):
        for i1 in range(5):
            assert factor + b.get_element(i0, i1) == c.get_element(i0, i1)
    # slice
    c.assign(b)
    a = lf.create_two_index(3, 3)
    a.randomize()
    c.iadd(a, factor, begin0=1, end0=4, begin1=1, end1=4)
    for i0 in range(5):
        for i1 in range(5):
            if i0 >= 1 and i0 < 4 and i1 >= 1 and i1 < 4:
                assert factor * a.get_element(i0 - 1, i1 - 1) + b.get_element(
                    i0, i1
                ) == c.get_element(i0, i1)
            else:
                assert b.get_element(i0, i1) == c.get_element(i0, i1)
    # slice and transpose
    c.assign(b)
    c.iadd(a, factor, begin0=1, end0=4, begin1=1, end1=4, transpose=True)
    for i0 in range(5):
        for i1 in range(5):
            if i0 >= 1 and i0 < 4 and i1 >= 1 and i1 < 4:
                assert factor * a.get_element(i1 - 1, i0 - 1) + b.get_element(
                    i0, i1
                ) == c.get_element(i0, i1)
            else:
                assert b.get_element(i0, i1) == c.get_element(i0, i1)


def test_two_index_iadd_slice():
    lf = DenseLinalgFactory()
    a = lf.create_two_index(5, 5)
    a.randomize()
    b = lf.create_two_index(8, 8)
    b.randomize()
    c = a.copy()
    factor = np.random.uniform(1, 2)
    # normal usage
    c.iadd(b, factor, begin2=1, end2=6, begin3=3, end3=8)
    for i0 in range(5):
        for i1 in range(5):
            assert factor * b.get_element(i0 + 1, i1 + 3) + a.get_element(
                i0, i1
            ) == c.get_element(i0, i1)


def test_two_index_iadd_one_mult():
    lf = DenseLinalgFactory()
    inp = lf.create_two_index(5, 5)
    inp.randomize()
    orig = inp.copy()
    one1 = lf.create_one_index(5)
    one1.randomize()
    one2 = lf.create_one_index(5)
    one2.randomize()
    factor = np.random.uniform(1, 2)
    # normal usage
    inp.iadd_one_mult(one1, one2, factor)
    for i0 in range(5):
        for i1 in range(5):
            assert (
                abs(
                    orig.get_element(i0, i1)
                    + factor * one1.get_element(i1) * one2.get_element(i1)
                    - inp.get_element(i0, i1)
                )
                < 1e-10
            )
    # transpose usage
    inp.assign(orig)
    inp.iadd_one_mult(one1, one2, factor, transpose0=True)
    for i0 in range(5):
        for i1 in range(5):
            assert (
                abs(
                    orig.get_element(i0, i1)
                    + factor * one1.get_element(i0) * one2.get_element(i1)
                    - inp.get_element(i0, i1)
                )
                < 1e-10
            )
    # transpose usage
    inp.assign(orig)
    inp.iadd_one_mult(one1, one2, factor, transpose1=True)
    for i0 in range(5):
        for i1 in range(5):
            assert (
                abs(
                    orig.get_element(i0, i1)
                    + factor * one1.get_element(i1) * one2.get_element(i0)
                    - inp.get_element(i0, i1)
                )
                < 1e-10
            )
    # transpose usage
    inp.assign(orig)
    inp.iadd_one_mult(one1, one2, factor, transpose0=True, transpose1=True)
    for i0 in range(5):
        for i1 in range(5):
            assert (
                abs(
                    orig.get_element(i0, i1)
                    + factor * one1.get_element(i0) * one2.get_element(i0)
                    - inp.get_element(i0, i1)
                )
                < 1e-10
            )


def test_two_index_iscale():
    lf = DenseLinalgFactory()
    op = lf.create_two_index(3)
    op.randomize()
    tmp = op._array.copy()
    op.iscale(3.0)
    assert abs(op._array - 3 * tmp).max() < 1e-10


def test_two_index_get_set():
    lf = DenseLinalgFactory()
    op = lf.create_two_index(3)
    op.set_element(0, 1, 1.2)
    assert op.get_element(0, 1) == 1.2
    assert op.get_element(1, 0) == 1.2
    op = lf.create_two_index(3, 3)
    op.set_element(0, 1, 1.2, symmetry=1)
    assert op.get_element(0, 1) == 1.2
    assert op.get_element(1, 0) == 0.0


def test_two_index_sum():
    lf = DenseLinalgFactory()
    op1 = lf.create_two_index(3)
    op1._array[:] = np.random.uniform(-1, 1, (3, 3))
    assert op1.sum() == op1._array.sum()
    assert (
        op1.sum(begin0=1, end1=2)
        == op1._array[1, 0]
        + op1._array[2, 0]
        + op1._array[1, 1]
        + op1._array[2, 1]
    )


def test_two_index_trace():
    lf = DenseLinalgFactory()
    op1 = lf.create_two_index(3)
    op1._array[:] = np.random.uniform(-1, 1, (3, 3))
    assert (
        op1.trace() == op1._array[0, 0] + op1._array[1, 1] + op1._array[2, 2]
    )
    assert op1.trace(begin0=1, end1=2) == op1._array[1, 0] + op1._array[2, 1]


def test_two_index_itranspose():
    lf = DenseLinalgFactory(8)
    for _i in range(10):
        op = lf.create_two_index()
        op.randomize()
        (
            i0,
            i1,
        ) = np.random.randint(0, 4, 2)
        x = op.get_element(i0, i1)
        op.itranspose()
        assert op.get_element(i1, i0) == x


def test_two_index_assign_dot():
    lf = DenseLinalgFactory(2)
    exp0 = lf.create_orbital()
    a = lf.create_two_index()
    tf2 = lf.create_two_index()
    exp0.randomize()
    tf2.randomize()
    a.assign_dot(exp0, tf2)
    assert np.allclose(a._array, np.dot(exp0.coeffs, tf2._array))


def test_two_index_inner():
    lf = DenseLinalgFactory(3)
    op = lf.create_two_index()
    vec0 = lf.create_one_index()
    vec1 = lf.create_one_index()
    op.randomize()
    vec0.randomize()
    vec1.randomize()
    assert (
        abs(
            op.inner(vec0, vec1)
            - np.dot(vec0._array, np.dot(op._array, vec1._array))
        )
        < 1e-10
    )
    assert (
        abs(
            op.inner(vec0._array, vec1._array)
            - np.dot(vec0._array, np.dot(op._array, vec1._array))
        )
        < 1e-10
    )


def test_two_index_sqrt():
    lf = DenseLinalgFactory(3)
    op = lf.create_two_index()
    op.randomize()
    op.imul(op)
    root = op.sqrt()
    assert np.allclose(root._array, scipy.linalg.sqrtm(op._array).real)


def test_two_index_inverse():
    a = np.array([[0.3, 0.4, 1.2], [3.0, 1.2, 0.5], [0.4, 1.4, 3.1]])
    lf = DenseLinalgFactory(3)
    op = lf.create_two_index()
    op.assign(a)
    unitm = op.new()
    unitm.assign_diagonal(1.0)
    inverse = op.inverse()
    assert np.allclose(np.dot(inverse._array, op._array), unitm._array)
    assert np.allclose(np.dot(op._array, inverse._array), unitm._array)


test_diag = [
    (False, True, scipy.linalg.eigvalsh),
    (True, True, scipy.linalg.eigh),
]


# NOTE: test eig and eigvals if linalg supports complex numbers
@pytest.mark.parametrize("eigvec, eigh, method", test_diag)
def test_two_index_diagonalize(eigvec, eigh, method):
    a = np.array([[-1, 2, 2], [2, 2, -1], [2, -1, 2]])
    lf = DenseLinalgFactory(3)
    op = lf.create_two_index()
    op.assign(a)
    result = op.diagonalize(eigvec, eigh)
    ref = method(a)
    if not eigvec:
        result = [result]
        ref = [ref]
    for ref_, result_ in zip(ref, result):
        assert np.allclose(ref_, result_.array)


def test_two_index_idivide():
    a = np.array([[0.3, 0.4, 1.2], [3.0, 1.2, 0.5], [0.4, 1.4, 3.1]])
    b = np.array([[0.2, 0.1, 1.3], [1.0, 2.2, 2.5], [-0.4, -2.4, 1.1]])
    lf = DenseLinalgFactory(3)
    result = lf.create_two_index()
    result.assign(a)
    op2 = lf.create_two_index()
    op2.assign(b)
    result.idivide(op2, 1.1)
    ref = np.divide(a, b) * 1.1
    assert np.allclose(result.array, ref)


def test_two_index_divide():
    a = np.array([[0.3, 0.4, 1.2], [3.0, 1.2, 0.5], [0.4, 1.4, 3.1]])
    b = np.array([[0.2, 0.1, 1.3], [1.0, 2.2, 2.5], [-0.4, -2.4, 1.1]])
    lf = DenseLinalgFactory(3)
    op = lf.create_two_index()
    op.assign(a)
    op2 = lf.create_two_index()
    op2.assign(b)
    result = op.divide(op2, 1.1)
    ref = np.divide(a, b) * 1.1
    assert np.allclose(result._array, ref)


def test_two_index_assign_diagonal():
    lf = DenseLinalgFactory(3)
    op = lf.create_two_index()
    op.randomize()
    op.assign_diagonal(1.0)
    assert op.get_element(0, 0) == 1.0
    assert op.get_element(1, 1) == 1.0
    assert op.get_element(2, 2) == 1.0
    op.randomize()
    vec = lf.create_one_index()
    vec.randomize()
    op.assign_diagonal(vec)
    assert op.get_element(0, 0) == vec.get_element(0)
    assert op.get_element(1, 1) == vec.get_element(1)
    assert op.get_element(2, 2) == vec.get_element(2)


def test_two_index_copy_diagonal():
    lf = DenseLinalgFactory(3)
    op = lf.create_two_index()
    op.randomize()
    vec = op.copy_diagonal()
    assert op.get_element(0, 0) == vec.get_element(0)
    assert op.get_element(1, 1) == vec.get_element(1)
    assert op.get_element(2, 2) == vec.get_element(2)
    op.randomize()
    foo = op.copy_diagonal(vec)
    assert foo is vec
    assert op.get_element(0, 0) == vec.get_element(0)
    assert op.get_element(1, 1) == vec.get_element(1)
    assert op.get_element(2, 2) == vec.get_element(2)
    vec = op.copy_diagonal(begin=1)
    assert vec.shape == (2,)
    assert op.get_element(1, 1) == vec.get_element(0)
    assert op.get_element(2, 2) == vec.get_element(1)


def test_two_index_ravel():
    lf = DenseLinalgFactory(5)
    inp = lf.create_two_index()
    inp.randomize()
    ind = np.tril_indices(5, -1)
    out = inp.ravel(ind=ind)
    assert inp.get_element(1, 0) == out.get_element(0)
    assert inp.get_element(2, 0) == out.get_element(1)
    assert inp.get_element(2, 1) == out.get_element(2)
    assert inp.get_element(3, 0) == out.get_element(3)
    assert inp.get_element(3, 1) == out.get_element(4)
    assert inp.get_element(3, 2) == out.get_element(5)
    assert inp.get_element(4, 0) == out.get_element(6)
    assert inp.get_element(4, 1) == out.get_element(7)
    assert inp.get_element(4, 2) == out.get_element(8)
    assert inp.get_element(4, 3) == out.get_element(9)
    out = inp.ravel(end0=1, end1=1)
    assert out.shape == (1,)
    assert out.get_element(0) == inp.get_element(0, 0)


def test_two_index_is_symmetric():
    lf = DenseLinalgFactory(4)
    op = lf.create_two_index()
    op.set_element(2, 3, 3.1234)
    assert op.is_symmetric()
    op.set_element(2, 3, 3.1, symmetry=1)
    assert not op.is_symmetric()
    assert op.is_symmetric(1)


def test_two_index_symmetrize():
    lf = DenseLinalgFactory(3)
    op = lf.create_two_index()
    op.randomize()
    assert not op.is_symmetric()
    op.symmetrize()
    x = op.get_element(1, 2)
    op.set_element(2, 0, 0.0, symmetry=1)
    op.set_element(0, 2, 1.0, symmetry=1)
    op.symmetrize()
    op.is_symmetric()
    assert op.get_element(1, 2) == x
    assert op.get_element(0, 2) == 0.5


def test_two_index_iadd_outer():
    lf = DenseLinalgFactory(5)
    a = lf.create_two_index()
    b = lf.create_two_index()
    a.randomize()
    b.randomize()
    orig = lf.create_two_index(5 * 5)
    orig.randomize()
    out = orig.copy()
    out.iadd_outer(a, b, 2.5)
    assert (
        abs(
            out.get_element(0, 0)
            - orig.get_element(0, 0)
            - 2.5 * a.get_element(0, 0) * b.get_element(0, 0)
        )
        < 1e-8
    )
    assert (
        abs(
            out.get_element(18, 11)
            - orig.get_element(18, 11)
            - 2.5 * a.get_element(3, 3) * b.get_element(2, 1)
        )
        < 1e-8
    )


def test_two_index_iadd_kron():
    lf = DenseLinalgFactory(5)
    a = lf.create_two_index()
    b = lf.create_two_index()
    a.randomize()
    b.randomize()
    orig = lf.create_two_index(5 * 5)
    orig.randomize()
    out = orig.copy()
    out.iadd_kron(a, b, 2.5)
    assert (
        abs(
            out.get_element(0, 0)
            - orig.get_element(0, 0)
            - 2.5 * a.get_element(0, 0) * b.get_element(0, 0)
        )
        < 1e-8
    )
    assert (
        abs(
            out.get_element(18, 11)
            - orig.get_element(18, 11)
            - 2.5 * a.get_element(3, 2) * b.get_element(3, 1)
        )
        < 1e-8
    )


def test_two_index_iadd_dot_all():
    lf = DenseLinalgFactory(5)
    a = lf.create_two_index()
    b = lf.create_two_index()
    a.randomize()
    b.randomize()
    orig = lf.create_two_index()
    orig.randomize()
    out = orig.copy()
    out.iadd_dot(a, b)
    assert np.allclose(out._array, orig._array + np.dot(a._array, b._array))
    out = orig.copy()
    out.iadd_tdot(a, b)
    assert np.allclose(out._array, orig._array + np.dot(a._array.T, b._array))
    out = orig.copy()
    out.iadd_dott(a, b)
    assert np.allclose(out._array, orig._array + np.dot(a._array, b._array.T))
    # with ranges
    a = lf.create_two_index(7)
    b = lf.create_two_index(9)
    a.randomize()
    b.randomize()
    out = orig.copy()
    out.iadd_dot(
        a,
        b,
        begin1=2,
        end1=7,
        begin0=0,
        end0=5,
        begin2=3,
        end2=8,
        begin3=4,
        end3=9,
    )
    assert np.allclose(
        out._array, orig._array + np.dot(a._array[:5, 2:7], b._array[3:8, 4:9])
    )


def test_two_index_iadd_mult():
    lf = DenseLinalgFactory(5)
    a = lf.create_two_index()
    b = lf.create_two_index()
    a.randomize()
    b.randomize()
    orig = lf.create_two_index()
    orig.randomize()
    out = orig.copy()
    out.iadd_mult(a, b)
    assert np.allclose(out._array, orig._array + (a._array * b._array))
    out = orig.copy()
    out.iadd_mult(a, b, transpose0=True)
    assert np.allclose(out._array, orig._array + (a._array.T * b._array))
    out = orig.copy()
    out.iadd_mult(a, b, transpose1=True)
    assert np.allclose(out._array, orig._array + (a._array * b._array.T))
    out = orig.copy()
    out.iadd_mult(a, b, transpose0=True, transpose1=True)
    assert np.allclose(out._array, orig._array + (a._array.T * b._array.T))
    # with ranges
    a = lf.create_two_index(7)
    b = lf.create_two_index(9)
    a.randomize()
    b.randomize()
    out = orig.copy()
    out.iadd_mult(
        b,
        a,
        begin3=2,
        end3=7,
        begin2=0,
        end2=5,
        begin0=3,
        end0=8,
        begin1=4,
        end1=9,
    )
    assert np.allclose(
        out._array, orig._array + (b._array[3:8, 4:9] * a._array[:5, 2:7])
    )
    out = orig.copy()
    out.iadd_mult(
        b,
        a,
        begin3=2,
        end3=7,
        begin2=0,
        end2=5,
        begin0=3,
        end0=8,
        begin1=4,
        end1=9,
        transpose0=True,
    )
    assert np.allclose(
        out._array, orig._array + (b._array[3:8, 4:9].T * a._array[:5, 2:7])
    )
    out = orig.copy()
    out.iadd_mult(
        b,
        a,
        begin3=2,
        end3=7,
        begin2=0,
        end2=5,
        begin0=3,
        end0=8,
        begin1=4,
        end1=9,
        transpose1=True,
    )
    assert np.allclose(
        out._array, orig._array + (b._array[3:8, 4:9] * a._array[:5, 2:7].T)
    )
    out = orig.copy()
    out.iadd_mult(
        b,
        a,
        begin3=2,
        end3=7,
        begin2=0,
        end2=5,
        begin0=3,
        end0=8,
        begin1=4,
        end1=9,
        transpose1=True,
        transpose0=True,
    )
    assert np.allclose(
        out._array, orig._array + (b._array[3:8, 4:9].T * a._array[:5, 2:7].T)
    )


def test_two_index_iadd_shift():
    lf = DenseLinalgFactory(5)
    orig = lf.create_two_index()
    orig.randomize()
    op = orig.copy()
    shift = 0.3
    op.iadd_shift(shift)
    assert abs(op._array.min()) >= shift
    for i in range(5):
        for j in range(5):
            if orig.get_element(i, j) < 0.0:
                assert op.get_element(i, j) == orig.get_element(i, j) - shift
            else:
                assert op.get_element(i, j) == orig.get_element(i, j) + shift


def test_two_index_idot():
    lf = DenseLinalgFactory(3)
    op1 = lf.create_two_index()
    op2 = lf.create_two_index()
    op1.randomize()
    op2.randomize()
    op3 = op2.copy()
    op2.idot(op1)
    assert np.allclose(op2._array, np.dot(op3._array, op1._array))


def test_two_index_idot_t():
    lf = DenseLinalgFactory(3)
    op1 = lf.create_two_index()
    op2 = lf.create_two_index()
    op1.randomize()
    op2.randomize()
    op3 = op2.copy()
    op2.idot_t(op1)
    assert np.allclose(op2._array, np.dot(op3._array, op1._array.T))


def test_two_index_imul():
    lf = DenseLinalgFactory(3)
    orig = lf.create_two_index()
    op2 = lf.create_two_index()
    orig.randomize()
    op2.randomize()
    op1 = orig.copy()
    op1.imul(op2, 1.3)
    assert np.allclose(op1._array, orig._array * op2._array * 1.3)
    op1 = orig.copy()
    op1.imul_t(op2, 1.3)
    assert np.allclose(op1._array, orig._array * op2._array.T * 1.3)
    # with ranges
    op2 = lf.create_two_index(5)
    op2.randomize()
    op1 = orig.copy()
    op1.imul(op2, 1.3, begin2=0, end2=3, begin3=2, end3=5)
    assert np.allclose(op1._array, orig._array * op2._array[:3, 2:5] * 1.3)
    op1 = orig.copy()
    op1.imul_t(op2, 1.3, begin2=0, end2=3, begin3=2, end3=5)
    assert np.allclose(op1._array, orig._array * op2._array[:3, 2:5].T * 1.3)
    op2 = lf.create_one_index(5)
    op2.randomize()
    op1 = orig.copy()
    op1.imul(op2, 1.3, begin2=0, end2=3)
    assert np.allclose(op1._array, orig._array * op2._array[:3] * 1.3)


def test_two_index_distance_inf():
    lf = DenseLinalgFactory(3)
    a = lf.create_two_index()
    a.randomize()
    b = a.copy()
    assert np.isclose(a.distance_inf(b), 0.0)
    b.set_element(0, 0, b.get_element(0, 0) + 0.1)
    assert np.isclose(a.distance_inf(b), 0.1)


def test_two_index_iabs():
    lf = DenseLinalgFactory(3)
    a = lf.create_two_index()
    a.randomize()
    b = a.copy()
    a.iabs()
    assert np.allclose(a._array, np.abs(b._array))


def test_two_index_assign_two_index_transform():
    lf = DenseLinalgFactory(3)
    a = lf.create_two_index()
    e0 = lf.create_orbital()
    e1 = lf.create_orbital()
    a.randomize()
    a.symmetrize()
    e0.randomize()
    e1.randomize()
    b = a.new()
    b.assign_two_index_transform(a, e0)
    assert np.allclose(b._array, b._array.T)
    assert b.is_symmetric()
    assert np.allclose(
        b._array, np.dot(e0.coeffs.T, np.dot(a._array, e0.coeffs))
    )
    b.assign_two_index_transform(a, e0, e1)
    assert not b.is_symmetric()
    assert np.allclose(
        b._array, np.dot(e0.coeffs.T, np.dot(a._array, e1.coeffs))
    )


def test_get_max_values_2index():
    lf = DenseLinalgFactory(8)
    op = lf.create_two_index()
    op.assign(0.0625)
    op.set_element(0, 6, -0.75)
    op.set_element(0, 1, 0.5)
    op.set_element(0, 4, 0.25)
    op.set_element(7, 2, 0.25)

    result = op.get_max_values(absolute=False)
    assert ((0, 1), 0.5) in result
    assert ((0, 4), 0.25) in result
    assert ((7, 2), 0.25) in result
    assert len(result) < 21

    result = op.get_max_values(limit=4, absolute=True)
    assert ((0, 1), 0.5) in result
    assert ((0, 6), -0.75) in result
    assert len(result) == 4


#
# DenseThreeIndex tests
#


def test_three_index_einsum_index():
    dlf = DenseLinalgFactory(2)
    dense = dlf.create_three_index()
    assert dense.einsum_index("abc") == "abc"


def test_three_index_arrays():
    dlf = DenseLinalgFactory(2)
    dense = dlf.create_three_index()
    arrays = dense.arrays
    assert len(arrays) == 1, isinstance(arrays[0], np.ndarray)


def test_three_index_array_setter():
    new_array = np.ones((6, 6, 6))
    lf = DenseLinalgFactory(6)
    op = lf.create_three_index()
    op.array = new_array
    assert op.array is new_array
    assert np.allclose(op.array, new_array)


def test_three_index_array_setter_indexing():
    new_array = np.ones((6, 6, 6))
    lf = DenseLinalgFactory(6)
    op = lf.create_three_index()
    op.array[:] = new_array
    assert op.array is not new_array
    assert np.allclose(op.array, new_array)


def test_three_index_array_slice_setter_indexing():
    new_array = np.ones((7, 6, 5))
    lf = DenseLinalgFactory(6)
    op = lf.create_three_index()
    op.array[1:2, 3:4, 5:6] = new_array[6:7, 4:5, 3:4]
    assert op.array is not new_array
    assert np.allclose(op.array[1:2, 3:4, 5:6], new_array[6:7, 4:5, 3:4])


def test_three_index_hdf5():
    lf = DenseLinalgFactory(5)
    a = lf.create_three_index()
    a.randomize()
    with h5.File(
        "pybest.linalg.test.test_dens.test_three_index_hdf5",
        driver="core",
        backing_store=False,
        mode="w",
    ) as f:
        a.to_hdf5(f)
        b = DenseThreeIndex.from_hdf5(f)
        assert a == b


def test_three_index_copy_new_randomize_clear_assign():
    lf = DenseLinalgFactory(5)
    for args in (None,), (4,):
        a = lf.create_three_index(*args)
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
        b.randomize()
        e = b.copy(begin0=1, end1=2, begin2=3)
        assert (e._array == b._array[1:, :2, 3:]).all()


def test_three_index_permute_basis():
    lf = DenseLinalgFactory(5)
    for _i in range(10):
        forth, back = get_forth_back(5)
        a = lf.create_three_index()
        a.randomize()
        b = a.copy()
        b.permute_basis(forth)
        assert a != b
        b.permute_basis(back)
        assert a == b


def test_three_index_change_basis_signs():
    lf = DenseLinalgFactory(5)
    for _i in range(10):
        signs = get_signs(5)
        a = lf.create_three_index()
        a.randomize()
        b = a.copy()
        b.change_basis_signs(signs)
        assert a != b
        b.change_basis_signs(signs)
        assert a == b


def test_three_index_iadd():
    lf = DenseLinalgFactory(5)
    a = lf.create_three_index()
    a.randomize()
    b = lf.create_three_index()
    b.randomize()
    c = b.copy()
    factor = np.random.uniform(1, 2)
    c.iadd(a, factor)
    for i0 in range(5):
        for i1 in range(5):
            for i2 in range(5):
                assert factor * a.get_element(i0, i1, i2) + b.get_element(
                    i0, i1, i2
                ) == c.get_element(i0, i1, i2)


def test_three_index_iadd_slice():
    lf = DenseLinalgFactory(5)
    a = lf.create_three_index(9)
    a.randomize()
    b = lf.create_three_index()
    b.randomize()
    c = b.copy()
    factor = np.random.uniform(1, 2)
    c.iadd(a, factor, begin3=0, end3=5, begin4=3, end4=8, begin5=4, end5=9)
    for i0 in range(5):
        for i1 in range(5):
            for i2 in range(5):
                assert factor * a.get_element(
                    i0, i1 + 3, i2 + 4
                ) + b.get_element(i0, i1, i2) == c.get_element(i0, i1, i2)


def test_three_index_iscale():
    lf = DenseLinalgFactory()
    op = lf.create_three_index(3)
    op.randomize()
    tmp = op._array.copy()
    op.iscale(3.0)
    assert abs(op._array - 3 * tmp).max() < 1e-10


def test_three_index_get_set():
    lf = DenseLinalgFactory()
    op = lf.create_three_index(3)
    op.set_element(0, 1, 2, 1.2)
    assert op.get_element(0, 1, 2) == 1.2


def test_three_index_expand_two_one():
    lf = DenseLinalgFactory(3)
    three = lf.create_three_index()
    two = lf.create_two_index()
    one = lf.create_one_index()
    three.randomize()
    two.randomize()
    one.randomize()
    orig = three.copy()
    two.contract("ab,c->cab", one, three, factor=0.7)
    assert np.allclose(
        three._array,
        orig._array + 0.7 * np.einsum("ab,c->cab", two._array, one._array),
    )
    orig = three.copy()
    two.contract("ab,c->acb", one, three, factor=0.7)
    assert np.allclose(
        three._array,
        orig._array + 0.7 * np.einsum("ab,c->acb", two._array, one._array),
    )


def test_three_index_expand_two_two():
    # Only test output for two cases: 'ac,bc->abc', 'cb,ac->acb'
    lf = DenseLinalgFactory(3)
    three = lf.create_three_index()
    two1 = lf.create_two_index()
    two2 = lf.create_two_index()
    three.randomize()
    two1.randomize()
    two2.randomize()
    orig = three.copy()
    two1.contract("ac,bc->abc", two2, three, factor=0.7)
    assert np.allclose(
        three._array,
        orig._array + 0.7 * np.einsum("ac,bc->abc", two1._array, two2._array),
    )
    # blind test for remaining contractions
    others = [
        "ac,bc->abc",
        "ab,bc->abc",
        "ab,ac->acb",
        "cb,ac->acb",
        "ac,ab->abc",
        "ab,ac->abc",
    ]
    for select in others:
        two1.contract(select, two2, three, factor=0.7)
    # with ranges
    two1 = lf.create_two_index(5)
    two2 = lf.create_two_index(7)
    two1.randomize()
    two2.randomize()
    orig = three.copy()
    two1.contract(
        "cb,ac->acb",
        two2,
        three,
        factor=0.7,
        begin0=2,
        end0=5,
        begin1=2,
        end2=3,
        begin3=3,
        end3=6,
    )
    assert np.allclose(
        three._array,
        orig._array
        + 0.7
        * np.einsum("cb,ac->acb", two1._array[2:5, 2:], two2._array[:3, 3:6]),
    )
    # blind test for remaining contractions
    others = [
        "ac,bc->abc",
        "ab,bc->abc",
        "ab,ac->acb",
        "cb,ac->acb",
        "ac,ab->abc",
        "ab,ac->abc",
    ]
    for select in others:
        two1.contract(
            select,
            two2,
            three,
            factor=0.7,
            begin0=2,
            end0=5,
            begin1=2,
            end2=3,
            begin3=3,
            end3=6,
        )


#
# DenseFourIndex tests
#

# FIXME: extend tests for different symmetries


def test_four_index_einsum_index():
    dlf = DenseLinalgFactory(2)
    dense = dlf.create_four_index()
    assert dense.einsum_index("abcd") == "abcd"


def test_four_index_arrays():
    dlf = DenseLinalgFactory(2)
    dense = dlf.create_four_index()
    arrays = dense.arrays
    assert len(arrays) == 1, isinstance(arrays[0], np.ndarray)


def test_four_index_hdf5():
    lf = DenseLinalgFactory(5)
    a = lf.create_four_index()
    a.randomize()
    with h5.File(
        "pybest.linalg.test.test_dens.test_four_index_hdf5",
        driver="core",
        backing_store=False,
        mode="w",
    ) as f:
        a.to_hdf5(f)
        b = DenseFourIndex.from_hdf5(f)
        assert a == b


def test_four_index_copy_new_randomize_clear_assign():
    lf = DenseLinalgFactory(5)
    for args in (None,), (4,):
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
        b.randomize()
        e = b.copy(0, 1, 2, 4, 2)
        assert (e._array == b._array[:1, 2:4, 2:]).all()


def test_four_index_permute_basis():
    lf = DenseLinalgFactory(5)
    for _i in range(10):
        forth, back = get_forth_back(5)
        a = lf.create_four_index()
        a.randomize()
        b = a.copy()
        b.permute_basis(forth)
        assert a != b
        b.permute_basis(back)
        assert a == b


def test_four_index_change_basis_signs():
    lf = DenseLinalgFactory(5)
    for _i in range(10):
        signs = get_signs(5)
        a = lf.create_four_index()
        a.randomize()
        b = a.copy()
        b.change_basis_signs(signs)
        assert a != b
        b.change_basis_signs(signs)
        assert a == b


def test_four_index_iadd():
    lf = DenseLinalgFactory(5)
    a = lf.create_four_index()
    a.randomize()
    b = lf.create_four_index()
    b.randomize()
    c = b.copy()
    factor = np.random.uniform(1, 2)
    c.iadd(a, factor)
    for i0 in range(5):
        for i1 in range(5):
            for i2 in range(5):
                for i3 in range(5):
                    assert factor * a.get_element(
                        i0, i1, i2, i3
                    ) + b.get_element(i0, i1, i2, i3) == c.get_element(
                        i0, i1, i2, i3
                    )


def test_four_index_iscale():
    lf = DenseLinalgFactory()
    op = lf.create_four_index(3)
    op.randomize()
    tmp = op._array.copy()
    op.iscale(3.0)
    assert abs(op._array - 3 * tmp).max() < 1e-10


def test_four_index_get_set():
    lf = DenseLinalgFactory()
    op = lf.create_four_index(4)
    op.set_element(0, 1, 2, 3, 1.2)
    assert op.get_element(0, 1, 2, 3) == 1.2
    assert op.get_element(2, 1, 0, 3) == 1.2
    assert op.get_element(0, 3, 2, 1) == 1.2
    assert op.get_element(2, 3, 0, 1) == 1.2
    assert op.get_element(1, 0, 3, 2) == 1.2
    assert op.get_element(3, 0, 1, 2) == 1.2
    assert op.get_element(1, 2, 3, 0) == 1.2
    assert op.get_element(3, 2, 1, 0) == 1.2


def test_four_index_is_symmetric():
    lf = DenseLinalgFactory(4)
    op = lf.create_four_index()
    op.set_element(0, 1, 2, 3, 1.234)
    assert op.is_symmetric(8)
    assert op.is_symmetric(4)
    assert op.is_symmetric(2)
    assert op.is_symmetric(1)
    op.set_element(0, 1, 2, 3, 1.0, symmetry=4)
    assert not op.is_symmetric(8)
    assert not op.is_symmetric(2)
    assert op.is_symmetric(4)
    assert op.is_symmetric(1)
    op.set_element(0, 1, 2, 3, 1.234)
    op.set_element(0, 1, 2, 3, 0.5, symmetry=2)
    assert not op.is_symmetric(8)
    assert not op.is_symmetric(4)
    assert op.is_symmetric(2)
    assert op.is_symmetric(1)
    op.set_element(0, 1, 2, 3, 0.3, symmetry=1)
    assert not op.is_symmetric(8)
    assert not op.is_symmetric(4)
    assert not op.is_symmetric(2)
    assert op.is_symmetric(1)


def test_four_index_symmetrize():
    lf = DenseLinalgFactory(8)
    op = lf.create_four_index()
    for symmetry in 1, 2, 4, 8:
        op.randomize()
        op.symmetrize(symmetry)
        assert op.is_symmetric(symmetry, 0, 0)


def test_four_index_symmetrize_order_of_operations():
    lf = DenseLinalgFactory(8)
    op = lf.create_four_index()
    for symmetry in 1, 2, 4, 8:
        # ugly hack to have matrix elements with very different order of
        # magnitudes
        op._array[:] = 10 ** np.random.uniform(-20, 20, (8, 8, 8, 8))
        op.symmetrize(symmetry)
        assert op.is_symmetric(symmetry, 0, 0)


def test_four_index_itranspose():
    lf = DenseLinalgFactory(8)
    for _i in range(10):
        op = lf.create_four_index()
        op.randomize()
        i0, i1, i2, i3 = np.random.randint(0, 4, 4)
        x = op.get_element(i0, i1, i2, i3)
        op.itranspose()
        assert op.get_element(i1, i0, i3, i2) == x


def test_four_index_sum():
    # Blind test
    lf = DenseLinalgFactory(4)
    op = lf.create_four_index()
    op.randomize()
    op.sum()


def test_four_index_iadd_exchange():
    # Blind test
    lf = DenseLinalgFactory(4)
    op = lf.create_four_index()
    op.randomize()
    op.symmetrize()
    op.iadd_exchange()
    op.is_symmetric()


def test_four_index_slice_to_two():
    # test in detail for aabb->ab
    lf = DenseLinalgFactory(6)
    four = lf.create_four_index()
    four.randomize()
    two = four.contract("aabb->ab", factor=1.3, clear=True, select="einsum")
    assert np.allclose(two._array, 1.3 * np.einsum("aabb->ab", four._array))
    foo = four.contract(
        "aabb->ab", out=two, factor=1.4, clear=True, select="einsum"
    )
    assert foo is two
    assert np.allclose(two._array, 1.4 * np.einsum("aabb->ab", four._array))
    four.contract("aabb->ab", out=two, factor=1.4, select="einsum")
    assert np.allclose(two._array, 2.8 * np.einsum("aabb->ab", four._array))
    # Blind test on all other cases
    four.contract("abab->ab", factor=1.3, clear=True, select="einsum")
    four.contract("abba->ab", factor=1.3, clear=True, select="einsum")
    # with ranges
    two = four.contract(
        "aabb->ab",
        factor=1.3,
        clear=True,
        select="einsum",
        end0=3,
        end1=3,
        begin2=2,
        begin3=2,
    )
    assert np.allclose(
        two._array, 1.3 * np.einsum("aabb->ab", four._array[:3, :3, 2:, 2:])
    )
    foo = four.contract(
        "aabb->ab",
        two,
        factor=1.4,
        clear=True,
        select="einsum",
        end0=3,
        end1=3,
        begin2=2,
        begin3=2,
    )
    assert foo is two
    assert np.allclose(
        two._array, 1.4 * np.einsum("aabb->ab", four._array[:3, :3, 2:, 2:])
    )
    four.contract(
        "aabb->ab",
        out=two,
        factor=1.4,
        select="einsum",
        end0=3,
        end1=3,
        begin2=2,
        begin3=2,
    )
    assert np.allclose(
        two._array, 2.8 * np.einsum("aabb->ab", four._array[:3, :3, 2:, 2:])
    )
    # Blind test on all other cases
    four.contract(
        "abab->ab",
        factor=1.3,
        clear=True,
        end0=3,
        begin1=2,
        end2=3,
        begin3=2,
        select="einsum",
    )
    four.contract(
        "abba->ab",
        factor=1.3,
        clear=True,
        end0=3,
        begin1=2,
        begin2=2,
        end3=3,
        select="einsum",
    )


def test_four_index_slice_to_three():
    # test in detail for aabb->ab
    lf = DenseLinalgFactory(4)
    four = lf.create_four_index()
    four.randomize()
    three = four.contract("abcc->bac", factor=1.3, clear=True, select="einsum")
    assert np.allclose(three._array, 1.3 * np.einsum("abcc->bac", four._array))
    foo = four.contract(
        "abcc->bac", out=three, factor=1.4, clear=True, select="einsum"
    )
    assert foo is three
    assert np.allclose(three._array, 1.4 * np.einsum("abcc->bac", four._array))
    four.contract("abcc->bac", out=three, factor=1.4, select="einsum")
    assert np.allclose(three._array, 2.8 * np.einsum("abcc->bac", four._array))
    # Blind test on all other cases
    four.contract("abcc->abc", factor=1.3, clear=True, select="einsum")
    four.contract("abcb->abc", factor=1.3, clear=True, select="einsum")
    four.contract("abbc->abc", factor=1.3, clear=True, select="einsum")


def test_four_index_slice_to_four():
    # test in detail for abcd->abcd'
    lf = DenseLinalgFactory(6)
    four = lf.create_four_index()
    four.randomize()
    four2 = four.contract(
        "abcd->abcd", factor=1.3, clear=True, select="einsum"
    )
    assert np.allclose(
        four2._array, 1.3 * np.einsum("abcd->abcd", four._array)
    )
    foo = four.contract(
        "abcd->abcd", out=four2, factor=1.4, clear=True, select="einsum"
    )
    assert foo is four2
    assert np.allclose(
        four2._array, 1.4 * np.einsum("abcd->abcd", four._array)
    )
    four.contract("abcd->abcd", out=four2, factor=1.4, select="einsum")
    assert np.allclose(
        four2._array, 2.8 * np.einsum("abcd->abcd", four._array)
    )
    # Blind test on all other cases
    four.contract("abcd->acbd", factor=1.3, clear=True, select="einsum")
    four.contract("abcd->cadb", factor=1.3, clear=True, select="einsum")
    # with ranges
    four2 = four.contract(
        "abcd->abcd",
        factor=1.3,
        clear=True,
        select="einsum",
        end0=3,
        begin1=2,
        begin2=2,
        end2=5,
    )
    assert np.allclose(
        four2._array,
        1.3 * np.einsum("abcd->abcd", four._array[:3, 2:, 2:5, :]),
    )
    foo = four.contract(
        "abcd->abcd",
        out=four2,
        factor=1.4,
        clear=True,
        select="einsum",
        end0=3,
        begin1=2,
        begin2=2,
        end2=5,
    )
    assert foo is four2
    assert np.allclose(
        four2._array,
        1.4 * np.einsum("abcd->abcd", four._array[:3, 2:, 2:5, :]),
    )
    four.contract(
        "abcd->abcd",
        out=four2,
        factor=1.4,
        select="einsum",
        end0=3,
        begin1=2,
        begin2=2,
        end2=5,
    )
    assert np.allclose(
        four2._array,
        2.8 * np.einsum("abcd->abcd", four._array[:3, 2:, 2:5, :]),
    )
    # Blind test on all other cases
    four.contract(
        "abcd->acbd",
        factor=1.3,
        clear=True,
        end0=3,
        begin1=2,
        begin2=2,
        end2=5,
        select="einsum",
    )
    four.contract(
        "abcd->cadb",
        factor=1.3,
        clear=True,
        end0=3,
        begin1=2,
        begin2=2,
        end2=5,
        select="einsum",
    )


# The C++ implementation only supports restricted orbitals
four_index_flavors_restricted = [
    "tensordot",
    "einsum",
    "opt_einsum",
    "einsum_naive",
]
four_index_flavors_general = [
    "tensordot",
    "einsum",
    "opt_einsum",
    "einsum_naive",
]
four_index_flavors_optimize = ["einsum", "einsum_naive"]
optimize = [False, True, "greedy", "optimal"]


@pytest.mark.parametrize("method", four_index_flavors_restricted)
def test_four_index_assign_four_index_transform_symmetry_restricted(method):
    """Check only symmetry of transformed integrals for the restricted case
    (only one set of orbitals)."""
    lf = DenseLinalgFactory(5)
    a = lf.create_four_index()
    # random but symmetric ERI
    a.randomize()
    a.symmetrize()
    # random orbitals
    e0 = lf.create_orbital()
    e0.randomize()
    # transformed ints
    t_i = a.new()
    t_i.assign_four_index_transform(a, e0, method=method)
    # Check symmetry
    assert np.allclose(t_i.array, t_i.array.transpose(1, 0, 3, 2))
    assert np.allclose(t_i.array, t_i.array.transpose(2, 3, 0, 1))
    assert np.allclose(t_i.array, t_i.array.transpose(1, 2, 3, 0))


@pytest.mark.parametrize("method", four_index_flavors_general)
def test_four_index_assign_four_index_transform_symmetry_general(method):
    """Check only symmetry of transformed integrals for the general case
    (four different sets of orbitals)."""
    lf = DenseLinalgFactory(5)
    # random but symmetric ERI
    a = lf.create_four_index()
    a.randomize()
    a.symmetrize()
    # random orbitals
    e0 = lf.create_orbital()
    e1 = lf.create_orbital()
    e2 = lf.create_orbital()
    e3 = lf.create_orbital()
    e0.randomize()
    e1.randomize()
    e2.randomize()
    e3.randomize()
    # transformed ints
    t_i = a.new()
    t_i.assign_four_index_transform(a, e0, e1, e2, e3, method=method)
    # Check symmetry
    assert not np.allclose(t_i.array, t_i.array.transpose(1, 0, 3, 2))
    assert not np.allclose(t_i.array, t_i.array.transpose(2, 3, 0, 1))
    assert not np.allclose(t_i.array, t_i.array.transpose(1, 2, 3, 0))


@pytest.mark.parametrize("method", four_index_flavors_general)
def test_four_index_assign_four_index_transform_consistency_general(method):
    """Compare all 4-index transformation to each other. Here, we compare
    all methods to the naive brute-force implementation of np.einsum using
    random orbitals and ERI."""
    lf = DenseLinalgFactory(3)
    # random ERI
    a = lf.create_four_index()
    a.randomize()
    # random orbitals
    e0 = lf.create_orbital()
    e1 = lf.create_orbital()
    e2 = lf.create_orbital()
    e3 = lf.create_orbital()
    e0.randomize()
    e1.randomize()
    e2.randomize()
    e3.randomize()
    # transformations
    ref = a.new()
    ref.assign_four_index_transform(a, e0, e1, e2, e3, method="einsum_naive")
    test = a.new()
    test.assign_four_index_transform(a, e0, e1, e2, e3, method=method)
    assert np.allclose(test.array, ref.array)


@pytest.mark.parametrize("method", four_index_flavors_restricted)
def test_four_index_assign_four_index_transform_consistency_restricted(method):
    """Compare all 4-index transformation to each other. Here, we compare
    all methods to the naive brute-force implementation of np.einsum using
    symmetric integrals and restricted orbitals."""
    lf = DenseLinalgFactory(3)
    # random but symmetric ERI
    a = lf.create_four_index()
    a.randomize()
    a.symmetrize()
    # random orbitals
    e0 = lf.create_orbital()
    # transformations
    ref = a.new()
    ref.assign_four_index_transform(a, e0, method="einsum_naive")
    test = a.new()
    test.assign_four_index_transform(a, e0, method=method)
    assert np.allclose(test.array, ref.array)


@pytest.mark.parametrize("method", four_index_flavors_optimize)
@pytest.mark.parametrize("optimize", optimize)
def test_four_index_assign_four_index_transform_optimize(method, optimize):
    """Compare all np.einsum 4-index transformation to each other using different
    optimization flags. Here, we compare all methods to the naive brute-force
    implementation of np.einsum using symmetric integrals and restricted orbitals.
    """
    lf = DenseLinalgFactory(3)
    # random but symmetric ERI
    a = lf.create_four_index()
    a.randomize()
    a.symmetrize()
    # random orbitals
    e0 = lf.create_orbital()
    # transformations
    ref = a.new()
    ref.assign_four_index_transform(
        a, e0, method="einsum_naive", optimize=False
    )
    test = a.new()
    test.assign_four_index_transform(a, e0, method=method, optimize=optimize)
    assert np.allclose(test.array, ref.array)


def test_get_max_values_4index():
    lf = DenseLinalgFactory(8)
    op = lf.create_four_index()
    op.assign(0.0625)
    op.set_element(0, 7, 2, 3, -0.75)
    op.set_element(0, 1, 2, 3, 0.5)
    op.set_element(0, 6, 2, 3, 0.25)

    result = op.get_max_values(absolute=False)
    assert ((0, 1, 2, 3), 0.5) in result
    assert ((0, 6, 2, 3), 0.25) in result
    assert len(result) < 21

    result = op.get_max_values(limit=16, absolute=True)
    assert ((0, 1, 2, 3), 0.5) in result
    assert ((0, 7, 2, 3), -0.75) in result
    assert len(result) == 16


def test_four_index_array_setter():
    new_array = np.ones((6, 6, 6, 6))
    lf = DenseLinalgFactory(6)
    op = lf.create_four_index()
    op.array = new_array
    assert op.array is new_array
    assert np.allclose(op.array, new_array)


def test_four_index_array_setter_indexing():
    new_array = np.ones((6, 6, 6, 6))
    lf = DenseLinalgFactory(6)
    op = lf.create_four_index()
    op.array[:] = new_array
    assert op.array is not new_array
    assert np.allclose(op.array, new_array)


def test_four_index_array_slice_setter_indexing():
    new_array = np.ones((7, 6, 5, 4))
    lf = DenseLinalgFactory(6)
    op = lf.create_four_index()
    op.array[:, :, :5, :4] = new_array[:6, :, :, :]
    assert op.array is not new_array
    assert np.allclose(op.array[:, :, :5, :4], new_array[:6, :, :, :])
