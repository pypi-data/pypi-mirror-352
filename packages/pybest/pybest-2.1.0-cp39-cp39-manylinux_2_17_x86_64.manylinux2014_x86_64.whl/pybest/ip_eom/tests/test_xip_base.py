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
# 2025-02: unification of variables and type hints (Julian Świerczyński)

from __future__ import annotations

from typing import Any

import numpy as np
import pytest
from numpy.typing import NDArray
from pytest import FixtureRequest

from pybest.exceptions import ArgumentError
from pybest.ip_eom import (
    RDIPCCD,
    RDIPCCSD,
    RDIPLCCD,
    RDIPLCCSD,
    RIPCCD,
    RIPCCSD,
    RIPLCCD,
    RIPLCCSD,
    RDIPfpCCD,
    RDIPfpCCSD,
    RDIPfpLCCD,
    RDIPfpLCCSD,
    RDIPpCCD,
    RIPfpCCD,
    RIPfpCCSD,
    RIPfpLCCD,
    RIPfpLCCSD,
    RIPpCCD,
)
from pybest.ip_eom.dip_base import RDIPCC
from pybest.ip_eom.sip_base import RSIPCC
from pybest.ip_eom.sip_pccd1 import RIPpCCD1
from pybest.linalg import DenseFourIndex, DenseLinalgFactory, DenseOneIndex
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

test_ip_cls = [RSIPCC, RDIPCC]


@pytest.mark.parametrize(
    "range_,start,nbasis,nocc,ncore,expected", test_data_range
)
@pytest.mark.parametrize("cls", test_ip_cls)
def test_get_range(
    range_: str,
    start: int,
    nbasis: int,
    nocc: int,
    ncore: int,
    expected: dict[str, int],
    cls: type[RSIPCC],
):
    """Test if proper ranges are selected when cache is initialized."""
    # Some preliminaries
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=nocc * 2, ncore=ncore)
    # Initialize empty class (we cannot use abc class)
    ipcc = cls(lf, occ_model)

    assert ipcc.get_range(range_, start) == expected


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
@pytest.mark.parametrize("cls", test_ip_cls)
def test_get_size(
    size_: str | tuple[int],
    nbasis: int,
    nocc: int,
    ncore: int,
    expected: tuple[int],
    cls: type[RSIPCC],
) -> None:
    """Test if proper sizes are returned when cache is initialized."""
    # Some preliminaries
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=nocc * 2, ncore=ncore)
    # Initialize empty class (we cannot use abc class)
    ipcc = cls(lf, occ_model)

    assert ipcc.get_size(size_) == expected


#
# Fixtures for testing guess: creates various h_diags
# We always test for 11 basis functions and 10 nacto
#
@pytest.fixture(
    params=[
        np.array([1, 4, 2, 6, 8, 9, 4, 5, 7, 3]),
        np.array([1, 2, 4, 1.1, 8, 9, 4, 5, 7, 3]),
        np.array([1, 2, 4, 1.1, 8, 9, 4, 5, 7, -3]),
    ]
)
def h_diag(request: FixtureRequest) -> DenseOneIndex:
    """Create some OneDenseIndex object of shape `dim` and a numpy array as
    guess with label `h_diag`.
    """
    h_diag = DenseOneIndex(10)
    h_diag.label = "h_diag"
    h_diag.array[:] = request.param
    return h_diag


@pytest.fixture(params=[1, 2, 3, 4])
def guess_input(request: FixtureRequest, h_diag: DenseOneIndex):
    """Create some OneDenseIndex object of shape `dim` and a numpy array as
    guess with label `h_diag`.
    """
    n_guess_vectors = request.param
    guess = []
    indices = np.argsort(h_diag.array)
    for i in range(n_guess_vectors):
        guess_ = DenseOneIndex(10)
        guess_.set_element(indices[i], 1.0)
        guess.append(guess_)
    return (guess, h_diag)


def test_build_guess_vectors(
    guess_input: tuple[NDArray[np.float64], DenseOneIndex],
):
    """Test if proper guess vectors are constructed. We only test for the
    RSIPpCCD class and 1 particle operator (easiest as we have only r_a)
    as we need the dimension property attribute to be defined correctly.
    All other classes use the same function.
    """
    guess_vectors = guess_input[0]
    h_diag = guess_input[1]
    # Some preliminaries, we always test for 11 basis functions and 10 nacto
    lf = DenseLinalgFactory(11)
    occ_model = AufbauOccModel(lf, nel=20, ncore=0)
    # Initialize empty class (we cannot use abc class)
    ipcc = RIPpCCD1(lf, occ_model)
    # Write property attribute
    ipcc.nhole = 1

    nguess = len(guess_vectors)
    guessv, nguessv = ipcc.build_guess_vectors(nguess, False, h_diag)
    # check length
    assert nguessv == nguess, "wrong length of guess vector"
    # check ipch vector
    for vec_t, vec_r in zip(guessv, guess_vectors):
        assert (
            vec_t.array == vec_r.array
        ).all(), "wrong elements in guess vector"


test_data_ci_sort = [
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
def test_sort_ci_vectors(
    nbasis: int,
    threshold: float,
    ci_v: NDArray[np.float64],
    expected: dict[int, int],
) -> None:
    """Test if CI vectors are properly sorted."""
    # Some preliminaries
    lf = DenseLinalgFactory(nbasis)
    # It does not matter what we set here
    occ_model = AufbauOccModel(lf, nel=2, ncore=0)
    # Initialize empty class (we cannot use abc class)
    ipcc = RIPpCCD1(lf, occ_model)

    ci_ordered = ipcc.sort_ci_vector(ci_v, threshold)
    for d_t, d_r in zip(ci_ordered.items(), expected.items()):
        assert d_t == d_r, "sorting did not work properly"


test_ip_cls_resolve_t = [
    # t_1 and t_p can be anything, t_2 has to be a 4-index object
    (RIPpCCD, {"alpha": 1}, {"t_p": 1}),
    (RIPpCCD, {"alpha": 3}, {"t_p": 1}),
    (RDIPpCCD, {"alpha": 0}, {"t_p": 1}),
    (RDIPpCCD, {"alpha": 2}, {"t_p": 1}),
    (RDIPpCCD, {"alpha": 4}, {"t_p": 1}),
    (RIPCCD, {"alpha": 1}, {"t_2": DenseFourIndex(2, 4, 2, 4)}),
    (RIPCCSD, {"alpha": 1}, {"t_1": 1, "t_2": DenseFourIndex(2, 4, 2, 4)}),
    (RIPLCCD, {"alpha": 1}, {"t_2": DenseFourIndex(2, 4, 2, 4)}),
    (RIPLCCSD, {"alpha": 1}, {"t_1": 1, "t_2": DenseFourIndex(2, 4, 2, 4)}),
    (RIPfpCCD, {"alpha": 1}, {"t_2": DenseFourIndex(2, 4, 2, 4)}),
    (RIPfpCCSD, {"alpha": 1}, {"t_1": 1, "t_2": DenseFourIndex(2, 4, 2, 4)}),
    (RIPfpLCCD, {"alpha": 1}, {"t_p": 1, "t_2": DenseFourIndex(2, 4, 2, 4)}),
    (
        RIPfpLCCSD,
        {"alpha": 1},
        {"t_1": 1, "t_p": 1, "t_2": DenseFourIndex(2, 4, 2, 4)},
    ),
    (
        RIPCCD,
        {"alpha": 1, "spinfree": True},
        {"t_2": DenseFourIndex(2, 4, 2, 4)},
    ),
    (
        RIPCCSD,
        {"alpha": 1, "spinfree": True},
        {"t_1": 1, "t_2": DenseFourIndex(2, 4, 2, 4)},
    ),
    (
        RIPLCCD,
        {"alpha": 1, "spinfree": True},
        {"t_2": DenseFourIndex(2, 4, 2, 4)},
    ),
    (
        RIPLCCSD,
        {"alpha": 1, "spinfree": True},
        {"t_1": 1, "t_2": DenseFourIndex(2, 4, 2, 4)},
    ),
    (
        RIPfpCCD,
        {"alpha": 1, "spinfree": True},
        {"t_2": DenseFourIndex(2, 4, 2, 4)},
    ),
    (
        RIPfpCCSD,
        {"alpha": 1, "spinfree": True},
        {"t_1": 1, "t_2": DenseFourIndex(2, 4, 2, 4)},
    ),
    (
        RIPfpLCCD,
        {"alpha": 1, "spinfree": True},
        {"t_p": 1, "t_2": DenseFourIndex(2, 4, 2, 4)},
    ),
    (
        RIPfpLCCSD,
        {"alpha": 1, "spinfree": True},
        {"t_1": 1, "t_p": 1, "t_2": DenseFourIndex(2, 4, 2, 4)},
    ),
    (RDIPCCD, {"alpha": 0}, {"t_2": DenseFourIndex(2, 4, 2, 4)}),
    (RDIPCCSD, {"alpha": 0}, {"t_1": 1, "t_2": DenseFourIndex(2, 4, 2, 4)}),
    (RDIPLCCD, {"alpha": 0}, {"t_2": DenseFourIndex(2, 4, 2, 4)}),
    (RDIPLCCSD, {"alpha": 0}, {"t_1": 1, "t_2": DenseFourIndex(2, 4, 2, 4)}),
    (RDIPfpCCD, {"alpha": 0}, {"t_2": DenseFourIndex(2, 4, 2, 4)}),
    (RDIPfpCCSD, {"alpha": 0}, {"t_1": 1, "t_2": DenseFourIndex(2, 4, 2, 4)}),
    (RDIPfpLCCD, {"alpha": 0}, {"t_p": 1, "t_2": DenseFourIndex(2, 4, 2, 4)}),
    (
        RDIPfpLCCSD,
        {"alpha": 0},
        {"t_1": 1, "t_p": 1, "t_2": DenseFourIndex(2, 4, 2, 4)},
    ),
]


@pytest.mark.parametrize("cls,kwargs,t_args", test_ip_cls_resolve_t)
def test_resolve_t(
    cls: RIPCCD,
    kwargs: dict[str, int | bool],
    t_args: dict[str, DenseFourIndex | int],
) -> None:
    """Test if T amplitudes are properly resolved from arguments"""
    # Some preliminaries
    lf = DenseLinalgFactory(10)
    occ_model = AufbauOccModel(lf, nel=4 * 2, ncore=0)
    # Initialize empty class (we cannot use abc class)
    ipcc = cls(lf, occ_model, **kwargs)
    # Dry run, if it fails a KeyError will be raised
    ipcc.resolve_t(t_args)
    # Check items
    for key, item in t_args.items():
        assert ipcc.checkpoint[key] == item, "wrong item stored in container"


test_ip_cls_resolve_t_error = [
    (RIPpCCD, {"alpha": 1}, {"t_1": 1}, KeyError),
    (RIPpCCD, {"alpha": 3}, {"t_1": 1}, KeyError),
    (RDIPpCCD, {"alpha": 0}, {"t_1": 1}, KeyError),
    (RDIPpCCD, {"alpha": 2}, {"t_1": 1}, KeyError),
    (RDIPpCCD, {"alpha": 4}, {"t_1": 1}, KeyError),
    (RIPpCCD, {"alpha": 1}, {"t_p": None}, ArgumentError),
    (RIPpCCD, {"alpha": 3}, {"t_p": None}, ArgumentError),
    (RDIPpCCD, {"alpha": 0}, {"t_p": None}, ArgumentError),
    (RDIPpCCD, {"alpha": 2}, {"t_p": None}, ArgumentError),
    (RDIPpCCD, {"alpha": 4}, {"t_p": None}, ArgumentError),
    (RIPCCD, {"alpha": 1}, {"t_2": None}, ArgumentError),
    (RIPCCSD, {"alpha": 1}, {"t_1": 1}, KeyError),
    (RIPCCSD, {"alpha": 1}, {"t_1": None}, ArgumentError),
    (RIPLCCD, {"alpha": 1}, {"t_2": None}, ArgumentError),
    (RIPLCCD, {"alpha": 1}, {}, KeyError),
    (RIPLCCD, {"alpha": 1}, {"t_2": None}, ArgumentError),
    (RIPLCCSD, {"alpha": 1}, {}, KeyError),
    (RIPLCCSD, {"alpha": 1}, {"t_1": None}, ArgumentError),
    (RIPLCCSD, {"alpha": 1}, {"t_1": 1}, KeyError),
    (RIPfpCCD, {"alpha": 1}, {}, KeyError),
    (RIPfpCCD, {"alpha": 1}, {"t_2": 1}, AttributeError),
    (RIPfpCCD, {"alpha": 1}, {"t_2": None}, ArgumentError),
    (RIPfpCCSD, {"alpha": 1}, {"t_1": 1}, KeyError),
    (RIPfpCCSD, {"alpha": 1}, {"t_1": 1, "t_2": None}, ArgumentError),
    (RIPfpCCSD, {"alpha": 1}, {"t_1": None}, ArgumentError),
    (RIPfpCCSD, {"alpha": 1}, {}, KeyError),
    (RIPfpLCCD, {"alpha": 1}, {}, KeyError),
    (RIPfpLCCD, {"alpha": 1}, {"t_2": None}, KeyError),
    (RIPfpLCCD, {"alpha": 1}, {"t_p": None, "t_2": None}, ArgumentError),
    (RIPfpLCCD, {"alpha": 1}, {"t_2": 1}, KeyError),
    (RIPfpLCCSD, {"alpha": 1}, {}, KeyError),
    (RIPfpLCCSD, {"alpha": 1}, {"t_p": None, "t_2": None}, KeyError),
    (RIPfpLCCSD, {"alpha": 1}, {"t_1": 1, "t_2": None}, KeyError),
    (RIPfpLCCSD, {"alpha": 1}, {"t_1": 1, "t_p": 1}, KeyError),
    (
        RIPfpLCCSD,
        {"alpha": 1},
        {"t_1": None, "t_p": None, "t_2": None},
        ArgumentError,
    ),
    (RDIPCCD, {"alpha": 0}, {"t_2": None}, ArgumentError),
    (RDIPCCSD, {"alpha": 0}, {"t_1": 1}, KeyError),
    (RDIPCCSD, {"alpha": 0}, {"t_1": None}, ArgumentError),
    (RDIPLCCD, {"alpha": 0}, {"t_2": None}, ArgumentError),
    (RDIPLCCD, {"alpha": 0}, {}, KeyError),
    (RDIPLCCD, {"alpha": 0}, {"t_2": None}, ArgumentError),
    (RDIPLCCSD, {"alpha": 0}, {}, KeyError),
    (RDIPLCCSD, {"alpha": 0}, {"t_1": None}, ArgumentError),
    (RDIPLCCSD, {"alpha": 0}, {"t_1": 1}, KeyError),
    (RDIPfpCCD, {"alpha": 0}, {}, KeyError),
    (RDIPfpCCD, {"alpha": 0}, {"t_2": 1}, AttributeError),
    (RDIPfpCCD, {"alpha": 0}, {"t_2": None}, ArgumentError),
    (RDIPfpCCSD, {"alpha": 0}, {"t_1": 1}, KeyError),
    (RDIPfpCCSD, {"alpha": 0}, {"t_1": 1, "t_2": None}, ArgumentError),
    (RDIPfpCCSD, {"alpha": 0}, {"t_1": None}, ArgumentError),
    (RDIPfpCCSD, {"alpha": 0}, {}, KeyError),
    (RDIPfpLCCD, {"alpha": 0}, {}, KeyError),
    (RDIPfpLCCD, {"alpha": 0}, {"t_2": None}, KeyError),
    (RDIPfpLCCD, {"alpha": 0}, {"t_p": None, "t_2": None}, ArgumentError),
    (RDIPfpLCCD, {"alpha": 0}, {"t_2": 1}, KeyError),
    (RDIPfpLCCSD, {"alpha": 0}, {}, KeyError),
    (RDIPfpLCCSD, {"alpha": 0}, {"t_p": None, "t_2": None}, KeyError),
    (RDIPfpLCCSD, {"alpha": 0}, {"t_1": 1, "t_2": None}, KeyError),
    (RDIPfpLCCSD, {"alpha": 0}, {"t_1": 1, "t_p": 1}, KeyError),
    (
        RDIPfpLCCSD,
        {"alpha": 0},
        {"t_1": None, "t_p": None, "t_2": None},
        ArgumentError,
    ),
]


@pytest.mark.parametrize(
    "cls,kwargs,t_args,error", test_ip_cls_resolve_t_error
)
def test_resolve_t_error(
    cls: RIPCCD,
    kwargs: dict[str, int | bool],
    t_args: dict[str, int | None],
    error: type[Exception],
) -> None:
    """Test if an error is raised when missing T amplitudes are resolved from
    arguments. We have to access the corresponding IP CC flavours directly
    as they store the proper `reference` class attribute used in the
    `resolve_t` function."""
    # Some preliminaries
    lf = DenseLinalgFactory(10)
    occ_model = AufbauOccModel(lf, nel=4 * 2, ncore=0)
    # Initialize empty class (we cannot use abc class)
    ipcc = cls(lf, occ_model, **kwargs)

    with pytest.raises(error):
        ipcc.resolve_t(t_args)


test_unmask_error = [
    # no olp
    ((), ArgumentError),
    # no orb
    (("olp",), ArgumentError),
    # no t
    (("olp", "orb"), ArgumentError),
    # no two
    (("t_p", "olp", "orb"), UnboundLocalError),
]


@pytest.mark.parametrize("cls", test_ip_cls)
@pytest.mark.parametrize("args,raised_error", test_unmask_error)
def test_ip_pccd_unmask_raise_error(
    cls: RIPCCD,
    args: tuple[str],
    raised_error: Any,
    no_1m: Any,
) -> None:
    """Test unmask_arg function by passing insufficient arguments"""
    # Create IPCC instance
    ippccd = cls(no_1m.lf, no_1m.occ_model)

    # resolve args
    args_ = []
    for arg in args:
        if arg == "orb":
            args_.append(*getattr(no_1m, arg))
        else:
            args_.append(getattr(no_1m, arg))
    # raise error as arguments are incomplete
    with pytest.raises(raised_error):
        # Overwrite with dummy attribute
        ippccd.reference = "pCCD"
        assert ippccd.unmask_args(*args_)
