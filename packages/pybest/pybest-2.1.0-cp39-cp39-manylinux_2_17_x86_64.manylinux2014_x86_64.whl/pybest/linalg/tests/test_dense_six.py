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
# 2024: This file has been added by Michał Kopczyński.

import h5py as h5
import numpy as np
import pytest
import scipy as scipy

from pybest.linalg import DenseLinalgFactory, DenseSixIndex

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
    # Six-index tests
    lf = DenseLinalgFactory(nb_size)
    op6 = lf.create_six_index()
    assert isinstance(op6, DenseSixIndex)
    lf.create_six_index.__check_init_args__(lf, op6)
    assert op6.nbasis == nb_size
    assert op6.shape == (nb_size, nb_size, nb_size, nb_size, nb_size, nb_size)
    op6 = lf.create_six_index(nb_size)
    lf.create_six_index.__check_init_args__(lf, op6, nb_size)
    assert op6.nbasis == nb_size


def test_linalg_objects_del():
    lf = DenseLinalgFactory()
    with pytest.raises(TypeError):
        lf.create_six_index()


def test_allocate_check_output():
    # SixIndex
    lf = DenseLinalgFactory(5)
    original_output = lf.create_six_index()
    returned_output = lf.allocate_check_output(
        original_output, (5, 5, 5, 5, 5, 5)
    )
    assert original_output is returned_output
    returned_output = lf.allocate_check_output(None, (5, 5, 5, 5, 5, 5))
    assert isinstance(returned_output, DenseSixIndex)
    assert returned_output.shape == (
        5,
        5,
        5,
        5,
        5,
        5,
    )


# general six index tests


def test_six_index_einsum_index():
    dlf = DenseLinalgFactory(2)
    dense = dlf.create_six_index()
    assert dense.einsum_index("abcdef") == "abcdef"


def test_six_index_arrays():
    dlf = DenseLinalgFactory(2)
    dense = dlf.create_six_index()
    arrays = dense.arrays
    assert len(arrays) == 1, isinstance(arrays[0], np.ndarray)


def test_six_index_hdf5(tmp_dir):
    lf = DenseLinalgFactory(5)
    a = lf.create_six_index()
    a.randomize()
    with h5.File(
        tmp_dir / "six_index.h5",
        driver="core",
        backing_store=False,
        mode="w",
    ) as f:
        a.to_hdf5(f)
        b = DenseSixIndex.from_hdf5(f)
        assert a == b


def test_assign_one_index_to_six_index():
    lf = DenseLinalgFactory()
    op_temp = lf.create_six_index(3)
    op_temp.clear()
    op6 = lf.create_six_index(3)
    op6._array[:] = np.random.uniform(0, 1, (3, 3, 3, 3, 3, 3))
    op1 = lf.create_one_index(730)
    op1.clear()
    with pytest.raises(ValueError):
        op6.assign(op1)
    op1 = lf.create_one_index(729)
    op1.clear()
    op6.assign(op1)
    assert (op6._array == op_temp._array).all()


def test_assign_two_index_to_six_index():
    lf = DenseLinalgFactory()
    op_temp = lf.create_six_index(2)
    op_temp.clear()
    op6 = lf.create_six_index(2)
    op6._array[:] = np.random.uniform(0, 1, (2, 2, 2, 2, 2, 2))
    op2 = lf.create_two_index(4, 16)
    op2.clear()
    op6.assign(op2)
    assert (op6._array == op_temp._array).all()
    op2 = lf.create_two_index(8, 8)
    op2.clear()
    op6.assign(op2)
    assert (op6._array == op_temp._array).all()
    op2 = lf.create_two_index(8, 10)
    op2.clear()
    with pytest.raises(ValueError):
        op6.assign(
            op2
        )  # ValueError: cannot reshape array of size 80 into shape (2,2,2,2,2,2)


def test_assign_three_index_to_six_index():
    lf = DenseLinalgFactory()
    op_temp = lf.create_six_index(3)
    op_temp.clear()
    op6 = lf.create_six_index(3)
    op6._array[:] = np.random.uniform(0, 1, (3, 3, 3, 3, 3, 3))

    op3 = lf.create_three_index(3, 3, 82)  # 3*3*82 != 738 == 3^6
    op3.clear()
    with pytest.raises(ValueError):
        op6.assign(
            op3
        )  # ValueError: cannot reshape array of size 738 into shape (3,3,3,3,3,3)
    op3 = lf.create_three_index(3, 3, 81)
    op3.clear()
    op6.assign(op3)
    assert (op6._array == op_temp._array).all()


def test_assign_four_index_to_six_index():
    lf = DenseLinalgFactory()
    op_temp = lf.create_six_index(2)
    op_temp.clear()
    op6 = lf.create_six_index(2)
    op6._array[:] = np.random.uniform(0, 1, (2, 2, 2, 2, 2, 2))

    op4 = lf.create_four_index(2, 2, 2, 10)  # 2*2*2*10 != 64 == 2^6
    op4.clear()
    with pytest.raises(ValueError):
        op6.assign(
            op4
        )  # ValueError: cannot reshape array of size 80 into shape (2,2,2,2,2,2)
    op4 = lf.create_four_index(2, 2, 2, 8)
    op4.clear()
    op6.assign(op4)
    assert (op6._array == op_temp._array).all()


def test_assign_five_index_to_six_index():
    lf = DenseLinalgFactory()
    op_temp = lf.create_six_index(2)
    op_temp.clear()
    op6 = lf.create_six_index(2)
    op6._array[:] = np.random.uniform(0, 1, (2, 2, 2, 2, 2, 2))

    op5 = lf.create_five_index(2, 2, 2, 2, 5)
    op5.clear()
    with pytest.raises(ValueError):
        op6.assign(op5)
    op5 = lf.create_five_index(2, 2, 2, 2, 4)
    op5.clear()
    op6.assign(op5)
    assert (op6._array == op_temp._array).all()


def test_assign_six_index_to_six_index():
    lf = DenseLinalgFactory()
    op1 = lf.create_six_index(3)
    op2 = lf.create_six_index(3)
    with pytest.raises(ValueError):
        op1._array[:] = np.random.uniform(0, 1, (4, 3, 3, 3, 3, 3))
    op1._array[:] = np.random.uniform(0, 1, (3, 3, 3, 3, 3, 3))
    op2.assign(op1)
    assert (op1._array == op2._array).all()


def test_assign_fragmet_one_index_to_six_index():
    lf = DenseLinalgFactory()
    op1 = lf.create_six_index(2)
    op2 = lf.create_six_index(2)
    op1.randomize()
    op2.assign(op1)
    op3 = lf.create_one_index(2)
    op3.clear()

    # Create indices for the diagonal of a 2x2x2x2x2x2 array
    diagonal_indices = np.diag_indices(2, 6)
    op1._array[diagonal_indices] = 0
    op2.assign(op3, diagonal_indices)
    assert (op1._array == op2._array).all()
    assert (
        op2.get_element(0, 0, 0, 0, 0, 0) == 0
        and op2.get_element(1, 1, 1, 1, 1, 1) == 0
    )


def test_assign_fragmet_raw_array_to_six_index():
    lf = DenseLinalgFactory()
    op1 = lf.create_six_index(2)
    op2 = lf.create_six_index(2)
    op1.randomize()
    op2.assign(op1)
    op3 = lf.create_one_index(2)
    op3.clear()

    # Create indices for the diagonal of a 2x2x2x2x2x2 array
    diagonal_indices = np.diag_indices(2, 6)
    op1._array[diagonal_indices] = 0
    op2.assign(op3.array, diagonal_indices)
    assert (op1._array == op2._array).all()
    assert (
        op2.get_element(0, 0, 0, 0, 0, 0) == 0
        and op2.get_element(1, 1, 1, 1, 1, 1) == 0
    )


def test_assign_fragmet_two_index_to_six_index_ravel():
    lf = DenseLinalgFactory()
    op1 = lf.create_six_index(4)
    op2 = lf.create_six_index(4)
    op1.randomize()
    op2.assign(op1)
    op3 = lf.create_two_index(2)
    op3.clear()

    # Create indices for the diagonal of a 4x4x4x4x4x4 array
    diagonal_indices = np.diag_indices(4, 6)
    op1._array[diagonal_indices] = 0
    # op3.ravel() returns DenseOneIndex
    op2.assign(op3.ravel(), diagonal_indices)
    assert (op1._array == op2._array).all()
    assert (
        op2.get_element(0, 0, 0, 0, 0, 0) == 0
        and op2.get_element(3, 3, 3, 3, 3, 3) == 0
    )


def test_assign_float_to_six_index():
    lf = DenseLinalgFactory()
    op1 = lf.create_six_index(2)
    op1.randomize()

    op1.assign(1.55)

    assert (op1._array == 1.55).all()

    # Testing with indices
    op2 = lf.create_six_index(4)
    op2.randomize()
    op2.set_element(3, 3, 3, 3, 3, 3, 10)
    indices = np.indices((2, 2, 2, 2, 2, 2))
    op2.assign(0.5, tuple(indices))

    assert (
        op2.get_element(0, 0, 0, 0, 0, 0) == 0.5
        and op2.get_element(1, 0, 1, 0, 1, 1) == 0.5
        and op2.get_element(3, 3, 3, 3, 3, 3) != 0.5
    )


def test_six_index_copy_new_randomize_clear_copy():
    lf = DenseLinalgFactory(5)
    for args in (None,), (4,):
        a = lf.create_six_index(*args)
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


def test_six_index_copy_new_randomize_clear_assign():
    lf = DenseLinalgFactory(5)
    for args in (None,), (4,):
        a = lf.create_six_index(*args)
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


def test_six_index_permute_basis():
    lf = DenseLinalgFactory(5)
    for _i in range(10):
        forth, back = get_forth_back(5)
        a = lf.create_six_index()
        a.randomize()
        b = a.copy()
        b.permute_basis(forth)
        assert a != b
        b.permute_basis(back)
        assert a == b


def test_six_index_iscale():
    lf = DenseLinalgFactory()
    op = lf.create_six_index(3)
    op.randomize()
    tmp = op._array.copy()
    op.iscale(3.0)
    assert abs(op._array - 3 * tmp).max() < 1e-10


def test_six_index_get_set():
    lf = DenseLinalgFactory()
    op = lf.create_six_index(5)
    op.set_element(0, 1, 2, 3, 4, 1, 1.2)
    assert op.get_element(0, 1, 2, 3, 4, 1) == 1.2
    op.set_element(2, 1, 2, 3, 3, 2, 2.44)
    assert op.get_element(2, 1, 2, 3, 3, 2) == 2.44
    op.clear()
    assert op.get_element(2, 1, 0, 3, 3, 2) == 0.0


def test_six_index_itranspose():
    lf = DenseLinalgFactory(8)
    for _i in range(10):
        op = lf.create_six_index()
        op.randomize()
        i0, i1, i2, i3, i4, i5 = np.random.randint(0, 4, 6)
        x = op.get_element(i0, i1, i2, i3, i4, i5)
        op.itranspose()
        assert op.get_element(i1, i0, i3, i2, i5, i4) == x
        op.randomize()
        x = op.get_element(i0, i1, i2, i3, i4, i5)
        op.itranspose([1, 5, 3, 2, 0, 4])
        assert op.get_element(i1, i5, i3, i2, i0, i4) == x


def test_six_index_sum():
    # Blind test
    lf = DenseLinalgFactory(4)
    op = lf.create_six_index()
    op.randomize()
    op.sum()
    op.clear()
    assert op.sum() == 0


def test_six_index_slice_to_two():
    # test in detail for aaabbb->ab
    lf = DenseLinalgFactory(6)
    six = lf.create_six_index()
    six.randomize()
    two = six.contract("aaabbb->ab", factor=1.3, clear=True, select="einsum")
    assert np.allclose(two._array, 1.3 * np.einsum("aaabbb->ab", six._array))
    foo = six.contract(
        "aaabbb->ab", out=two, factor=1.4, clear=True, select="einsum"
    )
    assert foo is two
    assert np.allclose(two._array, 1.4 * np.einsum("aaabbb->ab", six._array))
    six.contract("aaabbb->ab", out=two, factor=1.4, select="einsum")
    assert np.allclose(two._array, 2.8 * np.einsum("aaabbb->ab", six._array))
    # Blind test on (some!) other cases
    six.contract("ababab->ab", factor=1.3, clear=True, select="einsum")
    six.contract("babbaa->ab", factor=1.3, clear=True, select="einsum")
    # with ranges
    two = six.contract(
        "aabbab->ab",
        factor=1.3,
        clear=True,
        select="einsum",
        end0=3,
        end1=3,
        begin2=2,
        begin3=2,
    )
    assert np.allclose(
        two._array,
        1.3 * np.einsum("aabbab->ab", six._array[:3, :3, 2:, 2:, :3, 2:]),
    )
    foo = six.contract(
        "aabbab->ab",
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
        1.4 * np.einsum("aabbab->ab", six._array[:3, :3, 2:, 2:, :3, 2:]),
    )
    six.contract(
        "aabbab->ab",
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
        2.8 * np.einsum("aabbab->ab", six._array[:3, :3, 2:, 2:, :3, 2:]),
    )
    # Blind test on (some!) other cases
    six.contract(
        "ababba->ab",
        factor=1.3,
        clear=True,
        end0=3,
        begin1=2,
        end2=3,
        begin3=2,
        select="einsum",
    )
    six.contract(
        "abbaba->ab",
        factor=1.3,
        clear=True,
        end0=3,
        begin1=2,
        begin2=2,
        end3=3,
        select="einsum",
    )
    # todo: assert


def test_six_index_slice_to_three():
    # test in detail for aabb->ab
    lf = DenseLinalgFactory(4)
    six = lf.create_six_index()
    six.randomize()
    three = six.contract(
        "abccca->bac", factor=1.3, clear=True, select="einsum"
    )
    assert np.allclose(
        three._array, 1.3 * np.einsum("abccca->bac", six._array)
    )
    foo = six.contract(
        "abccca->bac", out=three, factor=1.4, clear=True, select="einsum"
    )
    assert foo is three
    assert np.allclose(
        three._array, 1.4 * np.einsum("abccca->bac", six._array)
    )
    six.contract("abccca->bac", out=three, factor=1.4, select="einsum")
    assert np.allclose(
        three._array, 2.8 * np.einsum("abccca->bac", six._array)
    )
    # Blind test on (some!) other cases
    six.contract("abccaa->abc", factor=1.3, clear=True, select="einsum")
    six.contract("abcbca->abc", factor=1.3, clear=True, select="einsum")
    six.contract("abbcab->abc", factor=1.3, clear=True, select="einsum")
    six.contract("aaccab->abc", factor=1.3, clear=True, select="einsum")


def test_six_index_slice_to_four():
    # test in detail for abcdca->bacd
    lf = DenseLinalgFactory(4)
    six = lf.create_six_index()
    six.randomize()
    four = six.contract(
        "abcdca->bacd", factor=1.3, clear=True, select="einsum"
    )
    assert np.allclose(
        four._array, 1.3 * np.einsum("abcdca->bacd", six._array)
    )
    foo = six.contract(
        "abcdca->bacd", out=four, factor=1.4, clear=True, select="einsum"
    )
    assert foo is four
    assert np.allclose(
        four._array, 1.4 * np.einsum("abcdca->bacd", six._array)
    )
    six.contract("abcdca->bacd", out=four, factor=1.4, select="einsum")
    assert np.allclose(
        four._array, 2.8 * np.einsum("abcdca->bacd", six._array)
    )
    # Blind test on (some!) other cases
    six.contract("abcdaa->abcd", factor=1.3, clear=True, select="einsum")
    six.contract("abcbcd->abcd", factor=1.3, clear=True, select="einsum")
    six.contract("abbcad->abcd", factor=1.3, clear=True, select="einsum")
    six.contract("abbcdb->abcd", factor=1.3, clear=True, select="einsum")


def test_six_index_slice_to_six():
    # test in detail for abcdef->abcdef
    lf = DenseLinalgFactory(6)
    six = lf.create_six_index()
    six.randomize()
    with pytest.raises(ValueError):
        six2 = six.contract(
            "abcde->abcdef", factor=1.3, clear=True, select="einsum"
        )
    six2 = six.contract(
        "abcdef->abcdef", factor=1.3, clear=True, select="einsum"
    )
    assert np.allclose(
        six2._array, 1.3 * np.einsum("abcdef->abcdef", six._array)
    )
    foo = six.contract(
        "abcdef->abcdef", out=six2, factor=1.4, clear=True, select="einsum"
    )
    assert foo is six2
    assert np.allclose(
        six2._array, 1.4 * np.einsum("abcdef->abcdef", six._array)
    )
    six.contract("abcdef->abcdef", out=six2, factor=1.4, select="einsum")
    assert np.allclose(
        six2._array, 2.8 * np.einsum("abcdef->abcdef", six._array)
    )
    # Blind test on (some!) other cases
    six.contract("abcdef->acbdef", factor=1.3, clear=True, select="einsum")
    six.contract("abcdef->cadbef", factor=1.3, clear=True, select="einsum")
    # with ranges
    six2 = six.contract(
        "abcdef->abcdef",
        factor=1.3,
        clear=True,
        select="einsum",
        end0=3,
        begin1=2,
        begin2=2,
        end2=5,
    )
    assert np.allclose(
        six2._array,
        1.3 * np.einsum("abcdef->abcdef", six._array[:3, 2:, 2:5, :, :, :]),
    )
    foo = six.contract(
        "abcdef->abcdef",
        out=six2,
        factor=1.4,
        clear=True,
        select="einsum",
        end0=3,
        begin1=2,
        begin2=2,
        end2=5,
    )
    assert foo is six2
    assert np.allclose(
        six2._array,
        1.4 * np.einsum("abcdef->abcdef", six._array[:3, 2:, 2:5, :, :, :]),
    )
    six.contract(
        "abcdef->abcdef",
        out=six2,
        factor=1.4,
        select="einsum",
        end0=3,
        begin1=2,
        begin2=2,
        end2=5,
    )
    assert np.allclose(
        six2._array,
        2.8 * np.einsum("abcdef->abcdef", six._array[:3, 2:, 2:5, :, :, :]),
    )
    # Blind test on (some!) other cases
    six.contract(
        "abcdef->acbdef",
        factor=1.3,
        clear=True,
        end0=3,
        begin1=2,
        begin2=2,
        end2=5,
        select="einsum",
    )
    six.contract(
        "abcdef->ecafdb",
        factor=1.3,
        clear=True,
        end0=3,
        begin1=2,
        begin2=2,
        end2=5,
        select="einsum",
    )
