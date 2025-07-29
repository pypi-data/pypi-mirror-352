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


import numpy as np

from pybest.linalg import DenseLinalgFactory
from pybest.linalg.cholesky import CholeskyLinalgFactory
from pybest.linalg.contract import (
    parse_contract_input,
    parse_subscripts,
    reduce_subscript,
    slice_output,
    td_helper,
)


def test_td_helper():
    subs = "abcd,cd->ab"
    op0 = np.random.rand(4, 5, 6, 7)
    op1 = np.random.rand(6, 7)
    op2_a = td_helper(subs, op0, op1)
    op2_b = np.einsum(subs, op0, op1)
    assert np.allclose(op2_a, op2_b)


def test_parse_contract_input():
    subs = "abcd,de->abce"
    subs_ = "xac,xbd,de->abce"
    clf = CholeskyLinalgFactory(7)
    chol = clf.create_four_index(nvec=5)
    dlf = DenseLinalgFactory(7)
    dens = dlf.create_two_index()
    inp = parse_contract_input(subs, [chol, dens], {"begin0": 0, "end5": 7})
    assert inp[0] == subs_


def test_parse_subscripts():
    test = [
        ("abcd,cd->ba", (["abcd", "cd"], "ba")),
        ("ijk,ji", (["ijk", "ji"], "k")),
        (("aabc,bd->..."), (["aabc", "bd"], "...")),
        (("abcd,abcd"), (["abcd", "abcd"], "")),
    ]
    for case in test:
        assert case[1] == parse_subscripts(case[0])


def test_reduce_subscript():
    subs = "aacd,ce->de"
    assert "acd,ce->de" == reduce_subscript(subs)


def test_slice_output():
    scripts = "abcd,cd->ba"
    kwargs = {"begin6": 1, "end7": 10}
    expected = (slice(1, None, None), slice(0, 10, None))
    assert slice_output(scripts, kwargs) == expected
