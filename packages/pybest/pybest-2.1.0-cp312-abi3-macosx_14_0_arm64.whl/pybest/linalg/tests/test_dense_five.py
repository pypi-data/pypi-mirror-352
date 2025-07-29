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

from pybest.linalg import DenseFiveIndex, DenseLinalgFactory

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


#
# DenseLinalgFactory tests
#


@pytest.mark.parametrize("nb_size", [10, 2, 7])
def test_linalg_factory_constructors(nb_size):
    # Five-index tests
    lf = DenseLinalgFactory(nb_size)
    op5 = lf.create_five_index()
    assert isinstance(op5, DenseFiveIndex)
    lf.create_five_index.__check_init_args__(lf, op5)
    assert op5.nbasis == nb_size
    assert op5.shape == (nb_size, nb_size, nb_size, nb_size, nb_size)
    op5 = lf.create_five_index(nb_size)
    lf.create_five_index.__check_init_args__(lf, op5, nb_size)
    assert op5.nbasis == nb_size


def test_linalg_objects_del():
    lf = DenseLinalgFactory()
    with pytest.raises(TypeError):
        lf.create_five_index()


def test_allocate_check_output():
    # FiveIndex
    lf = DenseLinalgFactory(5)
    original_output = lf.create_five_index()
    returned_output = lf.allocate_check_output(
        original_output, (5, 5, 5, 5, 5)
    )
    assert original_output is returned_output
    returned_output = lf.allocate_check_output(None, (5, 5, 5, 5, 5))
    assert isinstance(returned_output, DenseFiveIndex)
    assert returned_output.shape == (
        5,
        5,
        5,
        5,
        5,
    )


# general five index tests


def test_five_index_einsum_index():
    dlf = DenseLinalgFactory(2)
    dense = dlf.create_five_index()
    assert dense.einsum_index("abcde") == "abcde"


def test_five_index_arrays():
    dlf = DenseLinalgFactory(2)
    dense = dlf.create_five_index()
    arrays = dense.arrays
    assert len(arrays) == 1
    assert isinstance(arrays[0], np.ndarray)


def test_five_index_hdf5(tmp_dir):
    lf = DenseLinalgFactory(5)
    a = lf.create_five_index()
    a.randomize()
    with h5.File(
        tmp_dir / "five_index.h5",
        driver="core",
        backing_store=False,
        mode="w",
    ) as f:
        a.to_hdf5(f)
        b = DenseFiveIndex.from_hdf5(f)
        assert a == b


def test_reshape():
    lf = DenseLinalgFactory()
    op_temp = lf.create_five_index(2)
    op_temp.clear()
    new_reshaped_array = op_temp.reshape((8, 4))
    assert new_reshaped_array.shape == (8, 4)
    assert op_temp._array.shape == (2, 2, 2, 2, 2)
    op_temp.set_element(0, 0, 0, 0, 0, 5)
    assert op_temp.get_element(0, 0, 0, 0, 0) == 5
    assert new_reshaped_array.get_element(0, 0) != 5


def test_assign_one_index_to_five_index():
    lf = DenseLinalgFactory()
    op_temp = lf.create_five_index(3)
    op_temp.clear()
    op5 = lf.create_five_index(3)
    op5._array[:] = np.random.uniform(0, 1, (3, 3, 3, 3, 3))
    op1 = lf.create_one_index(244)
    op1.clear()
    with pytest.raises(ValueError):
        op5.assign(op1)
    op1 = lf.create_one_index(243)
    op1.clear()
    op5.assign(op1)
    assert (op5._array == op_temp._array).all()


def test_assign_two_index_to_five_index():
    lf = DenseLinalgFactory()
    op_temp = lf.create_five_index(2)
    op_temp.clear()
    op5 = lf.create_five_index(2)
    op5._array[:] = np.random.uniform(0, 1, (2, 2, 2, 2, 2))
    op2 = lf.create_two_index(2, 16)
    op2.clear()
    op5.assign(op2)
    assert (op5._array == op_temp._array).all()
    op2 = lf.create_two_index(4, 8)
    op2.clear()
    op5.assign(op2)
    assert (op5._array == op_temp._array).all()
    op2 = lf.create_two_index(4, 9)
    op2.clear()
    with pytest.raises(ValueError):
        op5.assign(op2)


def test_assign_three_index_to_five_index():
    lf = DenseLinalgFactory()
    op_temp = lf.create_five_index(3)
    op_temp.clear()
    op5 = lf.create_five_index(3)
    op5._array[:] = np.random.uniform(0, 1, (3, 3, 3, 3, 3))

    op3 = lf.create_three_index(3, 3, 28)
    op3.clear()
    with pytest.raises(ValueError):
        op5.assign(op3)
    op3 = lf.create_three_index(3, 3, 27)
    op3.clear()
    op5.assign(op3)
    assert (op5._array == op_temp._array).all()


def test_assign_four_index_to_five_index():
    lf = DenseLinalgFactory()
    op_temp = lf.create_five_index(2)
    op_temp.clear()
    op5 = lf.create_five_index(2)
    op5._array[:] = np.random.uniform(0, 1, (2, 2, 2, 2, 2))

    op4 = lf.create_four_index(2, 2, 2, 5)
    op4.clear()
    with pytest.raises(ValueError):
        op5.assign(op4)
    op4 = lf.create_four_index(2, 2, 2, 4)
    op4.clear()
    op5.assign(op4)
    assert (op5._array == op_temp._array).all()


def test_assign_five_index_to_five_index():
    lf = DenseLinalgFactory()
    op1 = lf.create_five_index(3)
    op2 = lf.create_five_index(3)
    with pytest.raises(ValueError):
        op1._array[:] = np.random.uniform(0, 1, (4, 3, 3, 3, 3))
    op1._array[:] = np.random.uniform(0, 1, (3, 3, 3, 3, 3))
    op2.assign(op1)
    assert (op1._array == op2._array).all()


def test_assign_fragmet_one_index_to_five_index():
    lf = DenseLinalgFactory()
    op1 = lf.create_five_index(2)
    op2 = lf.create_five_index(2)
    op1.randomize()
    op2.assign(op1)
    op3 = lf.create_one_index(2)
    op3.clear()

    # Create indices for the diagonal of a 2x2x2x2x2 array
    diagonal_indices = np.diag_indices(2, 5)
    op1._array[diagonal_indices] = 0
    op2.assign(op3, diagonal_indices)
    assert (op1._array == op2._array).all()
    assert (
        op2.get_element(0, 0, 0, 0, 0) == 0
        and op2.get_element(1, 1, 1, 1, 1) == 0
    )


def test_assign_fragmet_raw_array_to_five_index():
    lf = DenseLinalgFactory()
    op1 = lf.create_five_index(2)
    op2 = lf.create_five_index(2)
    op1.randomize()
    op2.assign(op1)
    op3 = lf.create_one_index(2)
    op3.clear()

    # Create indices for the diagonal of a 2x2x2x2x2 array
    diagonal_indices = np.diag_indices(2, 5)
    op1._array[diagonal_indices] = 0
    op2.assign(op3.array, diagonal_indices)
    assert (op1._array == op2._array).all()
    assert (
        op2.get_element(0, 0, 0, 0, 0) == 0
        and op2.get_element(1, 1, 1, 1, 1) == 0
    )


def test_assign_fragmet_two_index_to_five_index_ravel():
    lf = DenseLinalgFactory()
    op1 = lf.create_five_index(4)
    op2 = lf.create_five_index(4)
    op1.randomize()
    op2.assign(op1)
    op3 = lf.create_two_index(2)
    op3.clear()

    # Create indices for the diagonal of a 4x4x4x4x4 array
    diagonal_indices = np.diag_indices(4, 5)
    op1._array[diagonal_indices] = 0
    # op3.ravel() returns DenseOneIndex
    op2.assign(op3.ravel(), diagonal_indices)
    assert (op1._array == op2._array).all()
    assert (
        op2.get_element(0, 0, 0, 0, 0) == 0
        and op2.get_element(3, 3, 3, 3, 3) == 0
    )


def test_assign_float_to_six_index():
    lf = DenseLinalgFactory()
    op1 = lf.create_five_index(2)
    op1.randomize()

    op1.assign(1.55)

    assert (op1._array == 1.55).all()

    # Testing with indices
    op2 = lf.create_five_index(4)
    op2.randomize()
    op2.set_element(3, 3, 3, 3, 3, 10)
    indices = np.indices((2, 2, 2, 2, 2))
    op2.assign(0.5, indices)

    assert (
        op2.get_element(0, 0, 0, 0, 0) == 0.5
        and op2.get_element(1, 0, 1, 0, 1) == 0.5
        and op2.get_element(3, 3, 3, 3, 3) != 0.5
        and op2.get_element(3, 3, 3, 3, 3) == 10
    )


def test_five_index_copy_new_randomize_clear_copy():
    lf = DenseLinalgFactory(5)
    for args in (None,), (4,):
        a = lf.create_five_index(*args)
        b = a.copy()
        b.randomize()
        assert a != b
        c = b.copy()
        c.new.__check_init_args__(c, b)
        assert b == c
        d = c.new()
        assert a == d
        b.randomize()
        e = b.copy(0, 1, 2, 4, 2)
        assert (e._array == b._array[:1, 2:4, 2:]).all()
        f = b.copy()
        assert b == f


def test_five_index_copy_new_randomize_clear_assign():
    lf = DenseLinalgFactory(5)
    for args in (None,), (4,):
        a = lf.create_five_index(*args)
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
        e = b.copy(0, 1, 2, 4, 1, 4, 3)
        assert (e._array == b._array[:1, 2:4, 1:4, 3:]).all()


def test_five_index_iscale():
    lf = DenseLinalgFactory()
    op = lf.create_five_index(3)
    op.randomize()
    tmp = op._array.copy()
    op.iscale(3.0)
    assert abs(op._array - 3 * tmp).max() < 1e-10


def test_five_index_get_set():
    lf = DenseLinalgFactory()
    op = lf.create_five_index(5)
    op.set_element(0, 1, 2, 3, 4, 1.2)
    assert op.get_element(0, 1, 2, 3, 4) == 1.2
    op.set_element(2, 1, 2, 3, 3, 2.44)
    assert op.get_element(2, 1, 2, 3, 3) == 2.44
    op.clear()
    assert op.get_element(2, 1, 0, 3, 3) == 0.0


def test_five_index_itranspose():
    lf = DenseLinalgFactory(8)
    for _i in range(10):
        op = lf.create_five_index()
        op.randomize()
        i0, i1, i2, i3, i4 = np.random.randint(0, 4, 5)
        x = op.get_element(i0, i1, i2, i3, i4)
        op.itranspose([1, 0, 3, 2, 4])
        assert op.get_element(i1, i0, i3, i2, i4) == x
        op.randomize()
        x = op.get_element(i0, i1, i2, i3, i4)
        op.itranspose([1, 4, 3, 2, 0])
        assert op.get_element(i1, i4, i3, i2, i0) == x


def test_five_index_sum():
    # Blind test
    lf = DenseLinalgFactory(4)
    op = lf.create_five_index()
    op.randomize()
    op.sum()
    op.clear()
    assert op.sum() == 0


def test_five_index_slice_to_two():
    # test in detail for aaabb->ab
    lf = DenseLinalgFactory(6)
    five = lf.create_five_index()
    five.randomize()
    two = five.contract("aaabb->ab", factor=1.3, clear=True, select="einsum")
    assert np.allclose(two._array, 1.3 * np.einsum("aaabb->ab", five._array))
    foo = five.contract(
        "aaabb->ab", out=two, factor=1.4, clear=True, select="einsum"
    )
    assert foo is two
    assert np.allclose(two._array, 1.4 * np.einsum("aaabb->ab", five._array))
    five.contract("aaabb->ab", out=two, factor=1.4, select="einsum")
    assert np.allclose(two._array, 2.8 * np.einsum("aaabb->ab", five._array))
    # Blind test on (some!) other cases
    five.contract("ababa->ab", factor=1.3, clear=True, select="einsum")
    five.contract("babba->ab", factor=1.3, clear=True, select="einsum")
    # with ranges
    two = five.contract(
        "aabba->ab",
        factor=1.3,
        clear=True,
        select="einsum",
        end0=3,
        begin2=2,
    )
    assert np.allclose(
        two._array,
        1.3 * np.einsum("aabba->ab", five._array[:3, :3, 2:, 2:, :3]),
    )
    foo = five.contract(
        "aabba->ab",
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
        two._array,
        1.4 * np.einsum("aabba->ab", five._array[:3, :3, 2:, 2:, :3]),
    )
    five.contract(
        "aabba->ab",
        out=two,
        factor=1.4,
        select="einsum",
        end0=3,
        end1=3,
        begin2=2,
        begin3=2,
    )
    assert np.allclose(
        two._array,
        2.8 * np.einsum("aabba->ab", five._array[:3, :3, 2:, 2:, :3]),
    )
    # Blind test on (some!) other cases
    five.contract(
        "ababb->ab",
        factor=1.3,
        clear=True,
        end0=3,
        begin1=2,
        end2=3,
        begin3=2,
        select="einsum",
    )
    five.contract(
        "abbab->ab",
        factor=1.3,
        clear=True,
        end0=3,
        begin1=2,
        begin2=2,
        end3=3,
        select="einsum",
    )
    # todo: assert


def test_five_index_slice_to_three():
    # test in detail for abccc->ab
    lf = DenseLinalgFactory(4)
    five = lf.create_five_index()
    five.randomize()
    three = five.contract(
        "abccc->bac", factor=1.3, clear=True, select="einsum"
    )
    assert np.allclose(
        three._array, 1.3 * np.einsum("abccc->bac", five._array)
    )
    foo = five.contract(
        "abccc->bac", out=three, factor=1.4, clear=True, select="einsum"
    )
    assert foo is three
    assert np.allclose(
        three._array, 1.4 * np.einsum("abccc->bac", five._array)
    )
    five.contract("abccc->bac", out=three, factor=1.4, select="einsum")
    assert np.allclose(
        three._array, 2.8 * np.einsum("abccc->bac", five._array)
    )
    # Blind test on (some!) other cases
    five.contract("abcca->abc", factor=1.3, clear=True, select="einsum")
    five.contract("abcbc->abc", factor=1.3, clear=True, select="einsum")
    five.contract("abbca->abc", factor=1.3, clear=True, select="einsum")
    five.contract("aabbc->acb", factor=1.3, clear=True, select="einsum")


def test_five_index_slice_to_four():
    # test in detail for abcdc->bacd
    lf = DenseLinalgFactory(4)
    five = lf.create_five_index()
    five.randomize()
    four = five.contract(
        "abcdc->bacd", factor=1.3, clear=True, select="einsum"
    )
    assert np.allclose(
        four._array, 1.3 * np.einsum("abcdc->bacd", five._array)
    )
    foo = five.contract(
        "abcdc->bacd", out=four, factor=1.4, clear=True, select="einsum"
    )
    assert foo is four
    assert np.allclose(
        four._array, 1.4 * np.einsum("abcdc->bacd", five._array)
    )
    five.contract("abcdc->bacd", out=four, factor=1.4, select="einsum")
    assert np.allclose(
        four._array, 2.8 * np.einsum("abcdc->bacd", five._array)
    )
    # Blind test on (some!) other cases
    five.contract("abcda->abcd", factor=1.3, clear=True, select="einsum")
    five.contract("abcbd->abcd", factor=1.3, clear=True, select="einsum")
    five.contract("abcad->abcd", factor=1.3, clear=True, select="einsum")
    five.contract("abbcd->abcd", factor=1.3, clear=True, select="einsum")


def test_five_index_slice_to_five():
    # test in detail for abcdef->abcdef
    lf = DenseLinalgFactory(6)
    five = lf.create_five_index()
    five.randomize()
    with pytest.raises(ValueError):
        five2 = five.contract(
            "abcd->abcde", factor=1.3, clear=True, select="einsum"
        )
    five2 = five.contract(
        "abcde->abcde", factor=1.3, clear=True, select="einsum"
    )
    assert np.allclose(
        five2._array, 1.3 * np.einsum("abcde->abcde", five._array)
    )
    foo = five.contract(
        "abcde->abcde", out=five2, factor=1.4, clear=True, select="einsum"
    )
    assert foo is five2
    assert np.allclose(
        five2._array, 1.4 * np.einsum("abcde->abcde", five._array)
    )
    five.contract("abcde->abcde", out=five2, factor=1.4, select="einsum")
    assert np.allclose(
        five2._array, 2.8 * np.einsum("abcde->abcde", five._array)
    )
    # Blind test on (some!) other cases
    five.contract("abcde->acbde", factor=1.3, clear=True, select="einsum")
    five.contract("abcde->cadbe", factor=1.3, clear=True, select="einsum")
    # with ranges
    five2 = five.contract(
        "abcde->abcde",
        factor=1.3,
        clear=True,
        select="einsum",
        end0=3,
        begin1=2,
        begin2=2,
        end2=5,
    )
    assert np.allclose(
        five2._array,
        1.3 * np.einsum("abcde->abcde", five._array[:3, 2:, 2:5, :, :]),
    )
    foo = five.contract(
        "abcde->abcde",
        out=five2,
        factor=1.4,
        clear=True,
        select="einsum",
        end0=3,
        begin1=2,
        begin2=2,
        end2=5,
    )
    assert foo is five2
    assert np.allclose(
        five2._array,
        1.4 * np.einsum("abcde->abcde", five._array[:3, 2:, 2:5, :, :]),
    )
    five.contract(
        "abcde->abcde",
        out=five2,
        factor=1.4,
        select="einsum",
        end0=3,
        begin1=2,
        begin2=2,
        end2=5,
    )
    assert np.allclose(
        five2._array,
        2.8 * np.einsum("abcde->abcde", five._array[:3, 2:, 2:5, :, :]),
    )
    # Blind test on (some!) other cases
    five.contract(
        "abcde->acbde",
        factor=1.3,
        clear=True,
        end0=3,
        begin1=2,
        begin2=2,
        end2=5,
        select="einsum",
    )
    five.contract(
        "abcde->ecadb",
        factor=1.3,
        clear=True,
        end0=3,
        begin1=2,
        begin2=2,
        end2=5,
        select="einsum",
    )
