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


import os
from itertools import repeat
from random import randrange as randrange
from random import sample as sample

import numpy as np
import pytest

import pybest.gbasis.cholesky_eri as pybest_cholesky
from pybest import filemanager
from pybest.exceptions import ArgumentError, MatrixShapeError
from pybest.linalg import (
    CholeskyFourIndex,
    DenseFourIndex,
    DenseLinalgFactory,
    DenseOneIndex,
    DenseThreeIndex,
    DenseTwoIndex,
)
from pybest.linalg.base import PYBEST_CUPY_AVAIL
from pybest.linalg.cholesky import CholeskyLinalgFactory
from pybest.linalg.contract import parse_subscripts, slice_abcd
from pybest.linalg.gpu_contract import cupy_helper

#
# Base functions
#


def check_arrays(array_a, array_b):
    error = np.math.fsum(
        np.abs(np.subtract(array_a._array, array_b._array).flatten())
    )
    print(f"\tFrobenius norm : {error:.12f}")


def get_subscripts():
    """Returns a list of all contractions used in PyBEST.
    Warning: function works properly only if this script is located in
    $PYBESTPATH/anydirectory/anydirectory/
    """
    script_dir = os.path.dirname(os.path.realpath(__file__))
    walk_dir = os.path.join(script_dir, "../../")
    contractions = []

    for root, _directories, filenames in os.walk(walk_dir):
        for filename in filenames:
            if filename[-3:] == ".py":
                path = os.path.join(root, filename)
                with open(path, encoding="utf8") as f:
                    for line in f.readlines():
                        if "select=" in line:
                            line0, _line1 = line.split("select=", 1)
                        else:
                            line0 = line
                        if (".contract" in line0) or (".slice" in line0):
                            try:
                                _str0, str1, _str2 = line0.split("'")
                                if ("," in str1) or ("->" in str1):
                                    contractions.append(str1)
                            except ValueError:
                                pass

    contractions += [
        "abcc,dc->dab",
        "abcc,cd->abd",
        "abcc,dc->dab",
        "abbc->abc",
        "abcc->bac",
        "abcc->abc",
        "abcb->abc",
        "abcd->abcd",
        "abcd->abdc",
        "abcd->cadb",
        "abcd->dacb",
        "abcd->acbd",
        "abcd->acdb",
        "abcc,cb->ab",
        "abcc,ca->ab",
        "abcc,bc->ab",
        "abcc,ac->ab",
        "abcc,ab->ab",
        "abcd,bd->ac",
        "abcd,cb->ad",
        "abcd,ec,fdbg->eafg",
        "abcd,ec,fd->eafb",
        "abcd,ec,df->eabf",
        "abcd,ec,bf->eadf",
        "abcd,eb,df->efac",
        "abcd,be->aecd",
        "abcd,eb->eadc",
        "abcd,ae->bdec",
        "abcd,ed->ebac",
        "abcd,ec->edab",
        "abcd,ec->bade",
        "abcd,ec->ebad",
        "abcd,ae->ebcd",
        "abcd,ec->abed",
        "abcd,ed->aceb",
        "abcd,ec->eadb",
        "abcd,ec->adeb",
        "abcd,de->abce",
        "abcd,ce->abed",
        "abcd,eb->aecd",
        "abcd,ae->bcde",
        "abcd,ea->ebcd",
        "abcd,ae->bedc",
        "abcd,ed->aecb",
        "abcd,aedb->ce",
        "abcd,aebd->ce",
        "abcd,ecfd->eafb",
        "abcd,efcd->efab",
        "abcd,edfc->eafb",
    ]

    return list(set(contractions))


def is_suitable_for_td(subscripts):
    """Returns True if subscript is suitable for td_helper."""

    if "->" in subscripts:
        inscripts, outscript = subscripts.split("->")
    else:
        inscripts = subscripts
        outscript = ""

    # 1. Check if inscripts contain two input arguments.
    if inscripts.count(",") != 1:
        return False

    # 2. Check if summation indices are not in outscript.
    else:
        unique_chars = [
            char
            for i, char in enumerate(inscripts.replace(",", ""))
            if char not in inscripts[:i]
        ]
        expected_outscript = ""
        counts = {}
        for char in unique_chars:
            counts[char] = inscripts.count(char)
        for char in counts:
            if counts[char] == 1:
                expected_outscript += char
        if sorted(expected_outscript) != sorted(outscript):
            return False

        # 3. Check if scripts contain double indices/slices
        else:
            scripts = inscripts.split(",")
            scripts.append(outscript)
            for item in scripts:
                if len(set(item)) != len(item):
                    return False
    return True


def get_operands_dense(subscripts, min_nbasis=4, max_nbasis=20):
    """Returns a list of new DenseNIndex objects with random arrays and
    empty output DenseNIndex object.

        Arguments:
            subscripts : string
                E.g. 'abcd,cd->ab' (see numpy.einsum)

        Keyword arguments:
            min_nbasis : int
                Minimum basis size.
            max_nbasis : int
                Maximum basis size.
    """

    # 1. Split subscripts.
    scripts, outscript = parse_subscripts(subscripts)
    inscripts = ",".join(scripts)
    unique_chars = [
        char
        for i, char in enumerate(inscripts.replace(",", ""))
        if char not in inscripts[:i]
    ]

    # 2. Make recipe to match shapes of operands.
    match = {}
    dim = [i + min_nbasis for i in range(max_nbasis - min_nbasis + 1)]
    dim = sample(dim, k=len(dim))  # randomize ordering of dimensions
    for i, char in enumerate(unique_chars):
        match[char] = dim[i]

    # 3. Determine shapes and create operands
    operands = []
    for script in scripts:
        shape = [match.get(char, dim[0]) for char in script]
        new = DenseLinalgFactory.allocate_check_output(None, shape)
        new.randomize()
        operands.append(new)

    # 4. Determine shape of output argument
    if outscript is None:
        counts = {}
        outscript = ""
        for char in unique_chars:
            counts[char] = inscripts.count(char)
        for char in counts:
            if counts[char] == 1:
                outscript += char
        if len(outscript) == 0:
            return operands, None
    shape = [match.get(char, dim[0]) for char in outscript]
    out = DenseLinalgFactory.allocate_check_output(None, shape)
    return operands, out


def test_contract_dense():
    """Checks if contract returns the same results as numpy.einsum."""

    def get_error_msg(arg):
        return f"NIndexObject.contract (select='{arg}') returns wrong results."

    cases = get_subscripts()
    for subscripts in cases:
        factor = np.random.rand()
        operands, out = get_operands_dense(subscripts)

        # Compute with numpy directly.
        np_operands = [op._array for op in operands]
        np_result = factor * np.einsum(subscripts, *np_operands)

        # 1. Check consistency with einsum.
        co_result = operands[0].contract(
            subscripts,
            *operands[1:],
            factor=factor,
            out=out,
            clear=True,
            select="einsum",
        )
        # Compare.
        if out is None:
            result = co_result
        else:
            result = co_result._array
        assert np.allclose(np_result, result), get_error_msg("einsum")

        # 2. Check select = 'td'
        if is_suitable_for_td(subscripts):
            # Compute with wrapper.
            co_result = operands[0].contract(
                subscripts,
                *operands[1:],
                factor=factor,
                out=out,
                clear=True,
                select="td",
            )
            # Compare.
            if out is None:
                result = co_result
            else:
                result = co_result._array
            assert np.allclose(np_result, result), get_error_msg("td")

        # 3. Check select = 'opt_einsum'
        co_result = operands[0].contract(
            subscripts,
            *operands[1:],
            factor=factor,
            out=out,
            clear=True,
            select="opt_einsum",
        )
        # Compare.
        if out is None:
            result = co_result
        else:
            result = co_result._array
        assert np.allclose(np_result, result), get_error_msg("opt_einsum")


def test_contract_dense_autoout():
    """Checks if output operand is generated automatically."""

    cases = ["abcd->abd", "abcd,dca", "abc,bc->..."]
    for subscripts in cases:
        factor = np.random.rand()
        operands, _out = get_operands_dense(subscripts)

        # Check consistency with einsum.
        # Compute with numpy directly.
        np_operands = [op._array for op in operands]
        np_result = factor * np.einsum(subscripts, *np_operands)
        # Compute with wrapper.
        op_0 = operands[0]
        co_result = op_0.contract(
            subscripts,
            *operands[1:],
            factor=factor,
            clear=True,
            select="einsum",
        )
        # Compare.
        if hasattr(co_result, "_array"):
            result = co_result._array
        else:
            result = co_result
        error = "NIndexObject.contract returns wrong automatic output."
        assert np.allclose(np_result, result), error


def test_contract_dense_clear():
    """Checks if the output argument is cleared when requested."""

    subscripts = "abcd,efcd->befa"
    factor = np.random.rand()
    operands, out = get_operands_dense(subscripts)
    if out is not None:
        out.randomize()
        np_result = np.zeros(out.shape)
    else:
        np_result = 0
    for op in operands:
        op.clear()
    op_0 = operands[0]
    co_result = op_0.contract(
        subscripts,
        *operands[1:],
        factor=factor,
        out=out,
        clear=True,
        select="einsum",
    )
    if out is None:
        result = co_result
    else:
        result = co_result._array
    error = "NIndexObject.contract (clear=True) is not working."
    assert np.allclose(np_result, result), error

    # Check if clear=False works
    if out is not None:
        out.randomize()
        out_copy = out.copy()
        np_result = out_copy._array
        for op in operands:
            op.clear()
        op_0 = operands[0]
        co_result = op_0.contract(
            subscripts,
            *operands[1:],
            factor=factor,
            out=out,
            clear=False,
            select="einsum",
        )
        if out is None:
            result = co_result
        else:
            result = co_result._array
        error = "NIndexObject.contract (clear=False) is not working."
        assert np.allclose(np_result, result), error


def test_contract_outshape():
    """Checks if an error is raised when operands have mismatching shapes."""

    cases = [
        "ab,ac->bc",
        "abc,cd->abd",
        "abc,c->ab",
        "abcd,cde->abe",
        "abcd,abcd",
        "abcd,ebcd->ae",
        "abcd,efcd->abef",
    ]
    for subscripts in cases:
        factor = np.random.rand()
        operands, out = get_operands_dense(subscripts)
        if out is not None:
            old_shape = out.shape
            new_shape = [i + 1 for i in old_shape]
            new_out = DenseLinalgFactory.allocate_check_output(None, new_shape)
        else:
            new_out = DenseLinalgFactory.allocate_check_output(None, (2, 4))
        try:
            op = operands[0]
            op.contract(
                subscripts,
                operands[1],
                clear=True,
                factor=factor,
                out=new_out,
                select="einsum",
            )
            error = (
                "NIndexObject.contract does not raise any error"
                " although shape of out object is mismatched."
            )
            raise AssertionError(error)
        except (ArgumentError, ValueError):
            pass


def test_contract_begin_end():
    """Checks contraction on blocks of the operands."""

    subscripts = "abcd,efcd->abef"
    factor = np.random.rand()
    operands, _x = get_operands_dense(subscripts)

    op0 = operands[0]
    op1 = operands[1]
    shape0 = op0.shape
    shape1 = op1.shape

    b0 = int(shape0[0] / 2)
    e0 = shape0[0] - 1
    e2 = shape1[2] - 2
    b5 = shape1[1] - 3
    outshape = (e0 - b0, shape0[1], shape1[0], shape1[1] - b5)
    out = DenseLinalgFactory.allocate_check_output(None, outshape)

    # Compute with numpy directly.
    np_result = factor * np.einsum(
        subscripts, op0._array[b0:e0, :, :e2, :], op1._array[:, b5:, :e2, :]
    )
    # Compute with wrapper.
    ranges = {"begin0": b0, "end0": e0, "end2": e2, "begin5": b5, "end6": e2}
    co_result = op0.contract(
        subscripts,
        op1,
        factor=factor,
        out=out,
        clear=True,
        select="einsum",
        **ranges,
    )
    # Compare.
    error = "NIndexObject.contract(select='einsum') - ranges error."
    assert np.allclose(np_result, co_result._array), error


def test_contract_slice_output():
    """Test addition of the contraction product to block of output operands."""

    subscripts = "abcd,efcd->abef"
    factor = np.random.rand()
    operands, _x = get_operands_dense(subscripts)

    op0 = operands[0]
    op1 = operands[1]
    shape0 = op0.shape
    shape1 = op1.shape

    b0 = int(shape0[0] / 2)
    e0 = shape0[0] - 1
    e2 = shape1[2] - 2
    b5 = shape1[1] - 3
    outshape = (e0 - b0, 2 + shape0[1], shape1[0], shape1[1] - b5)
    out = DenseLinalgFactory.allocate_check_output(None, outshape)

    # Compute with numpy directly.
    np_result = factor * np.einsum(
        subscripts, op0._array[b0:e0, :, :e2, :], op1._array[:, b5:, :e2, :]
    )
    # Compute with wrapper.
    ranges = {
        "begin0": b0,
        "end0": e0,
        "end2": e2,
        "begin5": b5,
        "end6": e2,
        "begin9": 2,
    }
    co_result = op0.contract(
        subscripts,
        op1,
        factor=factor,
        out=out,
        clear=True,
        select="einsum",
        **ranges,
    )
    # Compare.
    error = "NIndexObject.contract - output slicing error."
    assert np.allclose(np_result, co_result._array[:, 2:, :, :]), error


cases_slice_abcd = [
    ("abcd", "a", 0, tuple([0, slice(None), slice(None), slice(None)])),
    ("abcd", "a", 5, tuple([5, slice(None), slice(None), slice(None)])),
    ("abcd", "b", 0, tuple([slice(None), 0, slice(None), slice(None)])),
    ("abcd", "b", 5, tuple([slice(None), 5, slice(None), slice(None)])),
    ("abcd", "c", 0, tuple([slice(None), slice(None), 0, slice(None)])),
    ("abcd", "c", 5, tuple([slice(None), slice(None), 5, slice(None)])),
    ("abcd", "d", 0, tuple([slice(None), slice(None), slice(None), 0])),
    ("abcd", "d", 5, tuple([slice(None), slice(None), slice(None), 5])),
]


@pytest.mark.parametrize("subscript,axis,element,ref_slice", cases_slice_abcd)
def test_contract_slice_abcd(subscript, axis, element, ref_slice):
    """Test slicing operation for 4-index object."""

    operands, _ = get_operands_dense(subscript, 6)

    op0 = operands[0].array
    slice_ = slice_abcd(subscript, element, axis)

    # Compare slices
    error = "slice_abcd - ref_slice error."
    assert slice_ == ref_slice, error
    # Compare elements
    error = "4IndexObject[slice_abcd] - 4IndexObject[ref_slice] error."
    assert np.allclose(op0[slice_], op0[ref_slice]), error


def get_operands_cholesky(subscripts, min_nbasis=2, max_nbasis=6):
    """Returns a list of new DenseNIndex objects with random arrays and
    empty output DenseNIndex object.

        Arguments:
            subscripts : string
                E.g. 'abcd,cd->ab' (see numpy.einsum)

        Keyword arguments:
            min_nbasis : int
                Minimum basis size.
            max_nbasis : int
                Maximum basis size.
    """
    # 1. Split subscripts.
    scripts, outscript = parse_subscripts(subscripts)
    inscripts = ",".join(scripts)

    # 2. Create first operand (CholeskyFourIndex) and its Dense representation.
    dense_nbasis = randrange(min_nbasis, max_nbasis - 2, 1)
    operands = []
    clf = CholeskyLinalgFactory(max_nbasis)
    chol = clf.create_four_index(nvec=10)  # Do not change!
    chol.randomize()
    dense = chol.get_dense()

    # 3. Create other Dense operands.
    for script in scripts[1:]:
        shape = tuple([dense_nbasis for char in script])
        new = DenseLinalgFactory.allocate_check_output(None, shape)
        new.randomize()
        operands.append(new)

    # 4. Determine begin and end arguments for CholeskyFourIndex.
    ranges = {}
    sum_chars = [
        char
        for char in inscripts[5:]
        if inscripts.replace(",", "").count(char) > 1
    ]
    for n, char in enumerate(scripts[0]):
        if char in sum_chars:
            begin = randrange(0, max_nbasis - dense_nbasis, 1)
            end = begin + dense_nbasis
            ranges["begin" + str(n)] = begin
            ranges["end" + str(n)] = end

    # 5. Determine shape of output argument
    if outscript == "":
        return chol, dense, operands, None, ranges
    shape = []
    for char in outscript:
        if len(inscripts) > 5 and char in inscripts[5:]:
            shape.append(dense_nbasis)
        else:
            shape.append(max_nbasis)
    out = DenseLinalgFactory.allocate_check_output(None, tuple(shape))
    return chol, dense, operands, out, ranges


def test_contract_cholesky_einsum():
    """Test if contract's numpy.einsum works properly."""

    cases = get_subscripts()
    ch_cases = list(
        filter(lambda x: x[0:4] in ["abcd", "abcc", "abcb"], cases)
    )

    for subscripts in ch_cases:
        factor = np.random.rand()
        chol, dense, operands, out, ranges = get_operands_cholesky(subscripts)
        if out is not None:
            out1 = out.copy()
        else:
            out1 = None

        # Compute with wrapper.
        de_result = dense.contract(
            subscripts,
            *operands,
            factor=factor,
            out=out,
            clear=True,
            select="einsum",
            **ranges,
        )
        # Compute with wrapper.
        ch_result = chol.contract(
            subscripts,
            *operands,
            factor=factor,
            out=out1,
            clear=True,
            select="einsum",
            **ranges,
        )
        # Compare.
        if out is not None:
            ch_result = ch_result._array
            de_result = de_result._array
        error = (
            "NIndexObject.contract(select='einsum') returns different "
            "results for Dense and Cholesky representations "
            "for subscripts ",
            subscripts,
        )
        assert np.allclose(ch_result, de_result), error


cases_td_cholesky = [
    "abab->ab",
    "abcb->ac",
    "abcc->ab",
    "abcc->abc",
    "abcc->acb",
    "abcb->abc",
    "abcd->abdc",
    "abcd->abcd",
    "abcd->acbd",
    "abcd->dacb",
    "abcd->cadb",
    "abcd->acdb",
    "abcd->acbd",
    "abcd->acdb",
    "abcd->adcb",
    "abcd->abdc",
    "abcd->cabd",
    "abcd->badc",
    "abcd->dbac",
    "abcd,c->abd",
    "abcd,c->adb",
    "abcd,d->acb",
    "abcd,d->abc",
    "abcd,abd->c",
    "abcd,abc->d",
    "abcd,ad->cb",
    "abcd,ac->db",
    "abcd,ac->bd",
    "abcd,bd->ac",
    "abcd,ad->bc",
    "abac,bc->ac",
    "abcc,b->ac",
    "abcc,abd->cd",
    "abcd,ae->bcde",
    "abcd,ae->bdec",
    "abcd,ec->ebad",
    "abcd,ae->bedc",
    "abcd,ea->ebcd",
    "abcd,ec->adeb",
    "abcd,ce->abed",
    "abcd,eb->aecd",
    "abcd,ae->ebcd",
    "abcd,be->aecd",
    "abcd,ec->edab",
    "abcd,ed->aecb",
    "abcd,ec->bade",
    "abcd,de->abce",
    "abcd,ec->eadb",
    "abcd,ed->aceb",
    "abcd,ec->abed",
    "abcd,ed->ebac",
    "abcd,eb->eadc",
    "abcd,ac->acbd",
    "abcd,ad->adbc",
    "abcd,cdb->a",
    "abcd,dcb->a",
    "abcd,cde->abe",
    "abcd,dce->abe",
    "abcd,aebd->ce",
    "abcd,aedb->ce",
    "abcd,efcd->efab",
    "abcd,edfc->eafb",
    "abcd,cedf->aefb",
    "abcd,cedf->abfe",
    "abcd,cefd->afeb",
    "abcd,ecfd->eafb",
    "abcd,efcd->eafb",
    "abcd,befd->faec",
    "abcd,befd->feac",
    "abcd,ecfd->efab",
    "abcd,efcd->efba",
    "abcd,cefd->faeb",
    "abcd,cedf->aebf",
    "abcd,efcd->abef",
    "abcd,edaf->efbc",
    "abcd,ecdf->eabf",
    "abcd,cedf->beaf",
    "abcd,eb,df->efac",
    "abcd,ec,df->eabf",
    "abcd,ec,fd->eafb",
    "abcd,ec,bf->eadf",
    "abcd,ec,fdbg->eafg",
]


@pytest.mark.parametrize("subscripts", cases_td_cholesky)
def test_contract_cholesky_td(subscripts):
    """Test if tensordot helper works properly."""

    # Prepare the input and output
    factor = np.random.rand()
    chol, dense, operands, out, ranges = get_operands_cholesky(subscripts)

    # Compute with wrapper.
    de_result = dense.contract(
        subscripts,
        *operands,
        factor=factor,
        out=None,
        clear=True,
        select="einsum",
        **ranges,
    )
    # Compute with wrapper.
    ch_result = chol.contract(
        subscripts,
        *operands,
        factor=factor,
        out=None,
        clear=True,
        select="td",
        begin4=0,
        begin5=0,
        **ranges,
    )
    # Compare.
    if out is not None:
        ch_result = ch_result._array
        de_result = de_result._array
    error = (
        "NIndexObject.contract(select='td') returns different "
        "results for Dense and Cholesky representations. "
        f"Error occured for {subscripts}."
    )
    assert np.allclose(ch_result, de_result), error


cases_td_cholesky_special_cases = [
    "abcd,cde->abe",
    "abcd,dce->abe",
]


parameter_td_cholesky_special = [
    (2, 5, False),
    (2, 5, True),
    (4, 7, False),  # partition x
    (4, 7, True),
    (5, 8, False),  # partition x
]


@pytest.mark.parametrize("subscripts", cases_td_cholesky_special_cases)
@pytest.mark.parametrize(
    "_min,_max,save_memory", parameter_td_cholesky_special
)
def test_contract_cholesky_td_special_cases(
    subscripts, _min, _max, save_memory
):
    """Test if tensordot helper works properly."""

    # Prepare the input and output
    factor = np.random.rand()
    chol, dense, operands, out, ranges = get_operands_cholesky(
        subscripts, _min, _max
    )

    # Compute with wrapper.
    de_result = dense.contract(
        subscripts,
        *operands,
        factor=factor,
        out=None,
        clear=True,
        select="einsum",
        **ranges,
    )
    # Compute with wrapper.
    ch_result = chol.contract(
        subscripts,
        *operands,
        factor=factor,
        out=None,
        clear=True,
        select="td",
        begin4=0,
        begin5=0,
        **ranges,
        save_memory=save_memory,
    )
    # Compare.
    if out is not None:
        ch_result = ch_result._array
        de_result = de_result._array
    error = (
        "NIndexObject.contract(select='td') returns different "
        "results for Dense and Cholesky representations. "
        f"Error occured for {subscripts}."
    )
    assert np.allclose(ch_result, de_result), error


cases_save_memory = [
    "abcd,ac->acbd",
    # abcd->a...
    "abcd->abcd",
    "abcd->abdc",
    "abcd->acbd",
    "abcd->acdb",
    "abcd->adbc",
    "abcd->adcb",
    # abcd->b...
    "abcd->bacd",
    "abcd->badc",
    "abcd->bcad",
    "abcd->bcda",
    "abcd->bdac",
    "abcd->bdca",
    # abcd->c...
    "abcd->cabd",
    "abcd->cadb",
    "abcd->cbad",
    "abcd->cbda",
    "abcd->cdab",
    "abcd->cdba",
    # abcd->d...
    "abcd->dabc",
    "abcd->dacb",
    "abcd->dbac",
    "abcd->dbca",
    "abcd->dcab",
    "abcd->dcba",
]


@pytest.mark.parametrize("subscripts", cases_save_memory)
def test_contract_cholesky_td_save_memory(subscripts):
    """Test if tensordot helper works properly with save_memory flag."""

    # Prepare the input and output
    factor = np.random.rand()
    chol, dense, operands, out, ranges = get_operands_cholesky(subscripts)

    # Compute with wrapper.
    de_result = dense.contract(
        subscripts,
        *operands,
        factor=factor,
        out=None,
        clear=True,
        select="einsum",
        **ranges,
    )
    # Compute with wrapper.
    ch_result = chol.contract(
        subscripts,
        *operands,
        factor=factor,
        out=None,
        clear=True,
        select="td",
        begin4=0,
        begin5=0,
        **ranges,
        save_memory=True,
    )
    # Compare.
    if out is not None:
        ch_result = ch_result._array
        de_result = de_result._array
    error = (
        "NIndexObject.contract(select='td') returns different "
        "results for Dense and Cholesky representations. "
        f"Error occured for {subscripts}."
    )
    assert np.allclose(ch_result, de_result), error


cases_cupy_chol = [
    "abcd,ecfd->eafb",
    "abcd,ecfd->efab",
    "abcd,edfc->eafb",
    "abcd,efcd->efab",
    "abcd,efcd->efba",
    "abcd,efcd->eafb",
    "abcd,efcd->abef",
    "abcd,cefd->faeb",
    "abcd,cedf->aebf",
    "abcd,cedf->aefb",
    "abcd,cedf->abfe",
    "abcd,ecdf->efab",
    "abcd,efdc->efab",
    "abcd,cfed->afeb",
    "abcd,defc->aefb",
    "abcd,ecfd->efba",
    "abcd,cde->abe",
    "abcd,dce->abe",
    "abab->ab",  # from here only generic implementation
    "abcb->ac",
    "abcc->ab",
    "abcd->abdc",
    "abcd->abcd",
    "abcd->acbd",
    "abcd->dacb",
    "abcd->cadb",
    "abcd->acdb",
    "abcd->adcb",
    "abcd->cabd",
    "abcd->badc",
    "abcd->dbac",
    "abcd,ad->cb",
    "abcd,ac->db",
    "abcd,ac->bd",
    "abcd,bd->ac",
    "abcd,ad->bc",
    "abcd,c->abd",
    "abcd,c->adb",
    "abcd,d->acb",
    "abcd,d->abc",
    "abcd,aedb->ce",
    "abcd,aebd->ce",
    "abcd,ade->bce",
]


@pytest.mark.skipif(not PYBEST_CUPY_AVAIL, reason="Cupy not available.")
@pytest.mark.parametrize("subscripts", cases_cupy_chol)
def test_cupy_vs_td(subscripts):
    """Test cupy results vs tensordot helper."""

    # Prepare the input and output
    factor = np.random.rand()
    chol, _dense, operands, out, ranges = get_operands_cholesky(subscripts)

    ch_result = chol.contract(
        subscripts,
        *operands,
        factor=factor,
        out=None,
        clear=True,
        select="td",
        begin4=0,
        begin5=0,
        **ranges,
    )

    cp_result = chol.contract(
        subscripts,
        *operands,
        factor=factor,
        out=None,
        clear=True,
        select="cupy",
        begin4=0,
        begin5=0,
        **ranges,
    )

    # Compare.
    if out is not None:
        ch_result = ch_result._array
        cp_result = cp_result._array
    error = (
        "cupy returns different results than tensordot. "
        "Both in Cholesky representation. "
        f"Error occured for {subscripts}."
    )
    # set to absolute tolerance = 1e-05
    assert np.allclose(ch_result, cp_result, rtol=1e-03, atol=1e-04), error


cases_cupy_dense = [
    "sd,pqrs->pqrd",
    "rc,pqrd->pqcd",
    "qb,pqcd->pbcd",
    "pa,pbcd->abcd",
    "abab->ab",  # from here only generic implementation
    "abcb->ac",
    "abcc->ab",
    "abcc->abc",
    "abcb->abc",
    "abcd->abdc",
    "abcd->abcd",
    "abcd->acbd",
    "abcd->dacb",
    "abcd->cadb",
    "abcd->acdb",
    "abcd->acbd",
    "abcd->acdb",
    "abcd->adcb",
    "abcd->abdc",
    "abcd->cabd",
    "abcd->badc",
    "abcd->dbac",
    "abcd,ad->cb",
    "abcd,ac->db",
    "abcd,ac->bd",
    "abcd,bd->ac",
    "abcd,ad->bc",
    "bi,kbd->kid",
    "dj,kid->kij",
]


@pytest.mark.skipif(not PYBEST_CUPY_AVAIL, reason="Cupy not available.")
@pytest.mark.parametrize("subscripts", cases_cupy_dense)
def test_cupy_for_dense(subscripts):
    """Test cupy results for dense."""

    # Prepare the input and output
    factor = np.random.rand()
    operands, _out = get_operands_dense(subscripts)
    operands_dense = operands.copy()

    operands = [op._array for op in operands_dense]
    dense_result = factor * np.einsum(subscripts, *operands)
    cp_result = factor * cupy_helper(subscripts, *operands)

    error = (
        "cupy returns different results than tensordot. "
        "Both in Dense representation. "
        f"Error occurred for {subscripts}."
    )
    # set to absolute tolerance = 1e-05
    assert np.allclose(dense_result, cp_result, rtol=1e-03, atol=1e-05), error


dense_1_array = DenseOneIndex(10)
dense_1_array.randomize()
dense_1_array.label = "one"
dense_2_array = DenseTwoIndex(10, 10)
dense_2_array.randomize()
dense_2_array.label = "two"
dense_3_array = DenseThreeIndex(10, 10, 10)
dense_3_array.randomize()
dense_3_array.label = "three"
dense_4_array = DenseFourIndex(10, 10, 10, 10)
dense_4_array.randomize()
dense_4_array.label = "four"

linalg_set = [
    (DenseLinalgFactory, dense_1_array, None),
    (DenseLinalgFactory, dense_1_array, "some_other_file.h5"),
    (DenseLinalgFactory, dense_2_array, None),
    (DenseLinalgFactory, dense_3_array, None),
    (DenseLinalgFactory, dense_4_array, None),
]

if pybest_cholesky.PYBEST_CHOLESKY_ENABLED:
    chol_array = CholeskyFourIndex(10, 15)
    chol_array.randomize()
    chol_array.label = "chol"

    linalg_set += [
        (CholeskyLinalgFactory, chol_array, None),
        (CholeskyLinalgFactory, chol_array, "some_other_file.h5"),
    ]


@pytest.mark.parametrize("lf, data, filename", linalg_set)
def test_dump_array(lf, data, filename):
    # first copy data or otherwise test will break
    data_ = data.copy()
    data_.dump_array(data_.label, filename)

    filename = filename or f"checkpoint_{data_.label}.h5"
    filename = filemanager.temp_path(filename)
    # check if file exists
    assert filename.exists()
    # check if data is deleted
    assert not hasattr(data_, "_array")
    assert not hasattr(data_, "_array2")
    # check if original data is still there
    assert hasattr(data, "_array")
    if isinstance(lf, CholeskyLinalgFactory):
        assert hasattr(data, "_array2")


@pytest.mark.parametrize("lf, data, filename", linalg_set)
def test_load_array(lf, data, filename):
    # first copy data or otherwise test will break
    data_ = data.copy()
    # first dump so that we can read them again
    data_.dump_array(data_.label, filename)
    # check if data is deleted
    assert not hasattr(data_, "_array")
    if isinstance(lf, CholeskyLinalgFactory):
        assert not hasattr(data_, "_array2")

    # now load
    data_.load_array(data_.label, filename)
    # check if data is loaded
    assert hasattr(data_, "_array")
    if isinstance(lf, CholeskyLinalgFactory):
        assert hasattr(data_, "_array2")

    # check if data agrees with original data
    assert data == data_


label_set = ["one", "two", "three", "four", "chol", "dummy"]


@pytest.mark.parametrize("lf, data, filename", linalg_set)
@pytest.mark.parametrize("label", label_set)
def test_load_array_label(lf, data, filename, label):
    # first copy data or otherwise test will break
    data_ = data.copy()
    # first dump so that we can read them again
    data_.dump_array(data_.label, filename)

    # now load
    if data_.label == label:
        data_.load_array(label, filename)
    else:
        with pytest.raises(ArgumentError):
            data_.load_array(label, filename)


label_1_array = DenseOneIndex(10)
label_1_array.randomize()
label_2_array = DenseTwoIndex(10, 10)
label_2_array.randomize()
label_3_array = DenseThreeIndex(10, 10, 10)
label_3_array.randomize()
label_4_array = DenseFourIndex(10, 10, 10, 10)
label_4_array.randomize()

label_set = [
    (DenseLinalgFactory, label_1_array),
    (DenseLinalgFactory, label_2_array),
    (DenseLinalgFactory, label_3_array),
    (DenseLinalgFactory, label_4_array),
]

if pybest_cholesky.PYBEST_CHOLESKY_ENABLED:
    label_chol = CholeskyFourIndex(10, 15)
    label_chol.randomize()

    label_set += [
        (CholeskyLinalgFactory, label_chol),
    ]


@pytest.mark.parametrize("lf, data", label_set)
def test_dump_array_empty_label(lf, data):
    # first copy data or otherwise test will break
    data_ = data.copy()
    data_.dump_array("array")

    # self.label has been changed
    assert data_.label
    # check if file has been dumped properly using self.label
    filename = f"checkpoint_{data_.label}.h5"
    filename = filemanager.temp_path(filename)
    # check if file exists
    assert filename.exists()


fix_ends_set = [(0), (1), (None)]


@pytest.mark.parametrize("end", fix_ends_set)
def test_fix_ends(dense_object, end):
    """Test fix_ends for proper behaviour"""
    # create ends args of proper length (shape of NIndex object)
    ends = tuple(end for i in range(len(dense_object.shape)))

    # generate reference values
    ref_ends = tuple(
        i if end is None else end
        for i in repeat(dense_object.nbasis, len(dense_object.shape))
    )

    test_ends = dense_object.fix_ends(*ends)
    assert test_ends == ref_ends, f"wrong fix_end output for {end}"


# test parameters for 4Index object with nbasis=10
fix_ends_set_special = [
    (tuple((0, 2, 6, None)), tuple((0, 2, 6, 10))),
    (tuple((None, 2, 6, None)), tuple((10, 2, 6, 10))),
    (tuple((None, 2, 6)), tuple((10, 2, 6))),  # raise MatrixShapeError
]


@pytest.mark.parametrize("ends, expected", fix_ends_set_special)
def test_fix_ends_special_casae(ends, expected):
    """Test fix_ends for proper behavior for 4Index object with different ends"""
    dense4index = DenseFourIndex(10)

    try:
        test_ends = dense4index.fix_ends(*ends)
    except MatrixShapeError:
        test_ends = expected
    assert test_ends == expected, f"wrong fix_end output for {ends}"
