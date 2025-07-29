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
import pytest

from pybest.ea_eom.dea_base import RDEACC
from pybest.ea_eom.sea_base import RSEACC
from pybest.ea_eom.sea_pccd1 import REApCCD1
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel

test_data_range = [
    (
        "oovv",
        0,
        10,
        4,
        0,
        {
            "begin0": 0,
            "end0": 4,
            "begin1": 0,
            "end1": 4,
            "begin2": 4,
            "end2": 10,
            "begin3": 4,
            "end3": 10,
        },
    ),
    ("oV", 0, 10, 4, 0, {"begin0": 0, "end0": 4, "begin1": 0, "end1": 6}),
    ("nn", 0, 10, 4, 0, {"begin0": 0, "end0": 10, "begin1": 0, "end1": 10}),
    ("nn", 0, 10, 4, 1, {"begin0": 0, "end0": 9, "begin1": 0, "end1": 9}),
    ("ov", 2, 10, 4, 0, {"begin2": 0, "end2": 4, "begin3": 4, "end3": 10}),
    ("ov", 2, 10, 4, 1, {"begin2": 0, "end2": 3, "begin3": 3, "end3": 9}),
]

test_ea_cls = [RSEACC, RDEACC]


@pytest.mark.parametrize(
    "range_,start,nbasis,nocc,ncore,expected", test_data_range
)
@pytest.mark.parametrize("cls", test_ea_cls)
def test_get_range(range_, start, nbasis, nocc, ncore, expected, cls):
    """Test if proper ranges are selected when the cache is initialized."""
    # some preliminaries
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=nocc * 2, ncore=ncore)
    # Initialize empty class (we cannot use abc class)
    eacc = cls(lf, occ_model)

    assert (
        eacc.get_range(range_, start) == expected
    ), "incorrect ranges for intermediates"


test_data_size = [
    # function argument, expected
    ("ovv", 10, 4, 0, (4, 6, 6)),
    ("ovv", 10, 4, 2, (2, 6, 6)),
    ("ooov", 10, 4, 0, (4, 4, 4, 6)),
    ("ooov", 10, 4, 3, (1, 1, 1, 6)),
    ("ooovvv", 10, 4, 3, (1, 1, 1, 6, 6, 6)),
    ((3, 5, 19), 10, 4, 0, (3, 5, 19)),
    ((3, 5, 19), 10, 4, 2, (3, 5, 19)),
    ((3,), 10, 4, 2, (3,)),
    ((3, 3, 6, 6, 9), 10, 4, 2, (3, 3, 6, 6, 9)),
]


@pytest.mark.parametrize("size_,nbasis,nocc,ncore,expected", test_data_size)
@pytest.mark.parametrize("cls", test_ea_cls)
def test_get_size(size_, nbasis, nocc, ncore, expected, cls):
    """Test if proper sizes are returned when the cache is initialized."""
    # some preliminaries
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=nocc * 2, ncore=ncore)
    # Initialize empty class (we cannot use abc class)
    eacc = cls(lf, occ_model)

    assert eacc.get_size(size_) == expected, "incorrect size of intermediates"


def test_build_guess_vectors(guess_input):
    """Test if proper guess vectors are constructed. We only test for the
    EApCCD1 class and 1 particle operator (easiest as we have only r_a)
    as we need the dimension property attribute to be defined correctly.
    All other classes use the same function.
    """
    guess_vectors = guess_input[0]
    h_diag = guess_input[1]
    # some preliminaries
    lf = DenseLinalgFactory(11)
    # It does not matter what we set here
    occ_model = AufbauOccModel(lf, nel=2, ncore=0)
    # Initialize empty class (we cannot use base class)
    eacc = REApCCD1(lf, occ_model)
    # Write property attribute
    eacc.n_particle_operator = 1

    nguess = len(guess_vectors)
    guessv, nguessv = eacc.build_guess_vectors(nguess, False, h_diag)
    # check length
    assert nguessv == nguess, "incorrect length of guess vector"
    # check each vector
    for vec_t, vec_r in zip(guessv, guess_vectors):
        assert (
            vec_t.array == vec_r.array
        ).all(), "incorrect elements in guess vector"


test_data_ci_sort = [
    # h_diag_ = np.array([1,4,2,6,8,9,4,5,7,3])
    (10, 8, np.array([1, 4, 2, 6, 8, 9, 4, 5, 7, 3]), {5: 9}),
    (10, 8, -np.array([1, 4, 2, 6, 8, 9, 4, 5, 7, 3]), {5: -9}),
    (10, 3.9, np.array([1, 4, 2, 6, 8, 9, 4, 5, 7, 3]) - 5, {0: -4, 5: 4}),
    (10, 7.9, np.array([1, 4, 2, 6, 8, 9, 4, 5, 7, 3]), {5: 9, 4: 8}),
    (10, 7.9, -np.array([1, 4, 2, 6, 8, 9, 4, 5, 7, 3]), {5: -9, 4: -8}),
    (
        10,
        3.9,
        np.array([1, 4, 2, 6, 8, 9, 4, 5, 7, 3]),
        {5: 9, 4: 8, 8: 7, 3: 6, 7: 5, 1: 4, 6: 4},
    ),
]


@pytest.mark.parametrize("nbasis,threshold,ci_v,expected", test_data_ci_sort)
def test_sort_ci_vectors(nbasis, threshold, ci_v, expected):
    """Test if CI vectors are properly sorted."""
    # some preliminaries
    lf = DenseLinalgFactory(nbasis)
    # It does not matter what we set here
    occ_model = AufbauOccModel(lf, nel=2, ncore=0)
    # Initialize empty class (we cannot use abc class)
    eacc = REApCCD1(lf, occ_model)

    ci_ordered = eacc.sort_ci_vector(ci_v, threshold)
    for d_t, d_r in zip(ci_ordered.items(), expected.items()):
        assert d_t == d_r, "Sorting did not work properly"
