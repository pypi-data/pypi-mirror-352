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

import itertools

import pytest

from pybest.ip_eom.dip_base import RDIPCC
from pybest.ip_eom.dip_pccd0 import RDIPpCCD0
from pybest.ip_eom.dip_pccd2 import RDIPpCCD2
from pybest.ip_eom.dip_pccd4 import RDIPpCCD4
from pybest.ip_eom.dip_rccd0 import (
    RDIPCCD0,
    RDIPLCCD0,
    RDIPfpCCD0,
    RDIPfpLCCD0,
)
from pybest.ip_eom.dip_rccsd0 import (
    RDIPCCSD0,
    RDIPLCCSD0,
    RDIPfpCCSD0,
    RDIPfpLCCSD0,
)
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel

test_data_mask = [(10, 30, 0), (10, 30, 5)]
test_data_sz = [
    (0, [True, False], [1, 0]),
    (2, [True, False], [1, 0]),
    (4, [True], [1]),
]


@pytest.mark.parametrize("sz, spin, shift", test_data_sz)
@pytest.mark.parametrize("occ, nbasis, ncore", test_data_mask)
def test_get_mask_shape(
    sz: int,
    spin: list[bool | int],
    shift: list[int],
    occ: int,
    nbasis: int,
    ncore: int,
) -> None:
    """Test ``get_mask`` function of DIP base class. Check shape.

    Purpose: return a boolean array with True values for indices that are
             non-redundant and symmetry-unique. Required to assign the proper
             elements to the dense FourIndex objects during optimization
             (avoiding for loops).

    Procedure: test for s_z = 0.0 and other s_z values separately (see comments
               in test function below).
               Small letters indicate alpha electrons, capital letters beta
               electrons (or vice versa).
    """
    # Some preliminaries
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=occ * 2, ncore=ncore)
    # Initialize empty (base) class
    dipcc = RDIPCC(lf, occ_model)
    dipcc.s_z = sz

    mask = [dipcc.get_mask(spin_) for spin_ in spin]
    # check shape
    nacto, nactv = occ_model.nacto[0], occ_model.nactv[0]
    for mask_ in mask:
        assert mask_.shape == (
            nacto,
            nacto,
            nacto,
            nactv,
        ), "get_mask has wrong shape"


@pytest.mark.parametrize("sz, spin, shift", test_data_sz)
@pytest.mark.parametrize("occ, nbasis, ncore", test_data_mask)
def test_get_mask_elements(
    sz: int,
    spin: list[bool | int],
    shift: list[int],
    occ: int,
    nbasis: int,
    ncore: int,
) -> None:
    """Test ``get_mask`` function of DIP base class. Check individual elements.

    Purpose: return a boolean array with True values for indices that are
             non-redundant and symmetry-unique. Required to assign the proper
             elements to the dense FourIndex objects during optimization
             (avoiding for loops).

    Procedure: test for s_z = 0.0 and other s_z values separately (see comments
               in test function below).
               Small letters indicate alpha electrons, capital letters beta
               electrons (or vice versa).
    """
    # Some preliminaries
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=occ * 2, ncore=ncore)
    # Initialize empty (base) class
    dipcc = RDIPCC(lf, occ_model)
    dipcc.s_z = sz

    mask = [dipcc.get_mask(spin_) for spin_ in spin]
    # check elements
    nacto, nactv = range(occ_model.nacto[0]), range(occ_model.nactv[0])
    for mask_, spin_ in zip(mask, spin):
        for i, j, k, c in itertools.product(nacto, nacto, nacto, nactv):
            if sz == 0:
                if spin_ and i < k:
                    # unique block (iJkc)
                    assert mask_[i, j, k, c], "wrong iJkc block for S_z = 0"
                elif not spin_ and j < k:
                    # unique block (iJKC)
                    assert mask_[i, j, k, c], "wrong iJKC block for S_z = 0"
                else:
                    # all other elements have to be False
                    assert not mask_[i, j, k, c], "wrong block for S_z = 0"
            else:
                if spin_ and i < j < k:
                    # unique block (ijkc) (also works for s_z = 2)
                    assert mask_[i, j, k, c], "wrong ijkc block for S_z = 2, 4"
                elif not spin_ and i < j:
                    # unique block (ijKC)
                    assert mask_[i, j, k, c], "wrong ijKC block for S_z = 2"
                else:
                    # all other elements have to be False
                    assert not mask_[i, j, k, c], "wrong block for S_z = 2, 4"


@pytest.mark.parametrize("sz, spin, shift", test_data_sz)
@pytest.mark.parametrize("occ, nbasis, ncore", test_data_mask)
def test_get_index_of_mask(
    sz: int,
    spin: list[bool | int],
    shift: list[int],
    occ: int,
    nbasis: int,
    ncore: int,
) -> None:
    """Test ``get_index_of_mask`` function of DIP base class.

    Purpose: return the indices for which the boolean array ``get_mask`` is
             True. Those contain non-redundant and symmetry-unique elements.
             Required to assign the proper elements from the dense FourIndex
             objects to the OneIndex object stored during optimization
             (avoiding for loops).

    Procedure: test for s_z = 0.0 and other s_z values separately (see comments
               in test function below).
               We test if the indices returned by the ``get_index_of_mask``
               function fulfill the symmetry requirements, like i<j, etc.
               Small letters indicate alpha electrons, capital letters beta
               electrons (or vice versa).
    """
    # Some preliminaries
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=occ * 2, ncore=ncore)
    # Initialize empty (base) class
    ipcc = RDIPCC(lf, occ_model)
    ipcc.s_z = sz

    mask = [ipcc.get_index_of_mask(spin_) for spin_ in spin]
    # check elements
    dim0 = len(mask)
    nacto, nactv = occ_model.nacto[0], occ_model.nactv[0]
    for i in range(dim0):
        dim1 = len(mask[i][0])
        for j in range(dim1):
            if sz == 0.0:
                if spin[i]:
                    # check i<k for same spin, unique block (iJkc)
                    assert mask[i][0][j] < mask[i][2][j]
                    assert mask[i][0][j] < nacto - 1
                    assert mask[i][1][j] < nacto
                else:
                    # check j<k for same spin, unique block (iJKC)
                    assert mask[i][1][j] < mask[i][2][j]
                    assert mask[i][0][j] < nacto
                    assert mask[i][1][j] < (nacto - 1)
                assert mask[i][2][j] < nacto
                assert mask[i][3][j] < nactv
            else:
                # check i<j, unique block (ijkc) and (ijKC)
                assert mask[i][0][j] < mask[i][1][j]
                if spin[i]:
                    # check j<k for same spin, unique block (ijkc) and (ijkC)
                    assert mask[i][1][j] < mask[i][2][j]
                assert mask[i][0][j] < (nacto - 1 - shift[i])
                assert mask[i][1][j] < (nacto - shift[i])
                assert mask[i][2][j] < nacto
                assert mask[i][3][j] < nactv


test_data_alpha = [
    (RDIPCC, -1),
    (RDIPpCCD0, 0),
    (RDIPpCCD2, 2),
    (RDIPpCCD4, 4),
    (RDIPCCD0, 0),
    (RDIPfpCCD0, 0),
    (RDIPfpLCCD0, 0),
    (RDIPLCCD0, 0),
    (RDIPCCSD0, 0),
    (RDIPfpCCSD0, 0),
    (RDIPfpLCCSD0, 0),
    (RDIPLCCSD0, 0),
]


@pytest.mark.parametrize("cls, expected", test_data_alpha)
def test_alpha(cls: RDIPCC, expected: int) -> None:
    """Test if class has proper alpha class instance."""
    # Some preliminaries
    lf = DenseLinalgFactory(10)
    occ_model = AufbauOccModel(lf, nel=8, ncore=0)
    # Initialize empty class
    ipcc = cls(lf, occ_model)

    assert ipcc.alpha == expected


test_data_get_index_ijkc = [
    # sz = 2, ncore = 0
    (10, 4, 0, 4, 0, (0, 1, 2, 0, None)),
    (10, 4, 0, 4, 4, (0, 1, 2, 4, None)),
    (10, 4, 0, 4, 7, (0, 1, 3, 1, None)),
    (10, 4, 0, 4, 10, (0, 1, 3, 4, None)),
    (10, 4, 0, 4, 20, (1, 2, 3, 2, None)),
    (10, 4, 0, 4, 23, (1, 2, 3, 5, None)),
    # sz = 2, ncore = 1
    (10, 4, 1, 4, 0, (0, 1, 2, 0, None)),
    (10, 4, 1, 4, 4, (0, 1, 2, 4, None)),
    (10, 4, 1, 4, 5, (0, 1, 2, 5, None)),
    # sz = 1, ncore = 0, ijkc
    (10, 4, 0, 2, 0, (0, 1, 2, 0, True)),
    (10, 4, 0, 2, 4, (0, 1, 2, 4, True)),
    (10, 4, 0, 2, 7, (0, 1, 3, 1, True)),
    (10, 4, 0, 2, 10, (0, 1, 3, 4, True)),
    (10, 4, 0, 2, 20, (1, 2, 3, 2, True)),
    (10, 4, 0, 2, 23, (1, 2, 3, 5, True)),
    # sz = 1, ncore = 0, ijKC
    (10, 4, 0, 2, 24, (0, 1, 0, 0, False)),
    (10, 4, 0, 2, 28, (0, 1, 0, 4, False)),
    (10, 4, 0, 2, 31, (0, 1, 1, 1, False)),
    (10, 4, 0, 2, 34, (0, 1, 1, 4, False)),
    (10, 4, 0, 2, 44, (0, 1, 3, 2, False)),
    (10, 4, 0, 2, 167, (2, 3, 3, 5, False)),
    # sz = 1, ncore = 1, ijkc
    (10, 4, 1, 2, 0, (0, 1, 2, 0, True)),
    (10, 4, 1, 2, 4, (0, 1, 2, 4, True)),
    (10, 4, 1, 2, 5, (0, 1, 2, 5, True)),
    # sz = 1, ncore = 1, ijKC
    (10, 4, 1, 2, 6, (0, 1, 0, 0, False)),
    (10, 4, 1, 2, 10, (0, 1, 0, 4, False)),
    (10, 4, 1, 2, 16, (0, 1, 1, 4, False)),
    (10, 4, 1, 2, 59, (1, 2, 2, 5, False)),
    # sz = 0, ncore = 0, iJkc
    (10, 4, 0, 0, 0, (0, 0, 1, 0, True)),
    (10, 4, 0, 0, 4, (0, 0, 1, 4, True)),
    (10, 4, 0, 0, 23, (0, 1, 1, 5, True)),
    (10, 4, 0, 0, 56, (0, 3, 1, 2, True)),
    (10, 4, 0, 0, 100, (1, 2, 2, 4, True)),
    (10, 4, 0, 0, 143, (2, 3, 3, 5, True)),
    # sz = 0, ncore = 0, iJKC
    (10, 4, 0, 0, 144, (0, 0, 1, 0, False)),
    (10, 4, 0, 0, 148, (0, 0, 1, 4, False)),
    (10, 4, 0, 0, 167, (0, 1, 2, 5, False)),
    (10, 4, 0, 0, 200, (1, 1, 2, 2, False)),
    (10, 4, 0, 0, 244, (2, 1, 3, 4, False)),
    (10, 4, 0, 0, 287, (3, 2, 3, 5, False)),
    # sz = 0, ncore = 1, iJkc
    (10, 4, 1, 0, 0, (0, 0, 1, 0, True)),
    (10, 4, 1, 0, 4, (0, 0, 1, 4, True)),
    (10, 4, 1, 0, 23, (0, 1, 2, 5, True)),
    # sz = 0, ncore = 1, iJKC
    (10, 4, 1, 0, 54, (0, 0, 1, 0, False)),
    (10, 4, 1, 0, 58, (0, 0, 1, 4, False)),
    (10, 4, 1, 0, 77, (1, 0, 1, 5, False)),
]


@pytest.mark.parametrize(
    "nbasis, nocc, ncore, sz, ind, expected", test_data_get_index_ijkc
)
def test_get_index_ijkc(
    nbasis: int,
    nocc: int,
    ncore: int,
    sz: int,
    ind: int,
    expected: tuple[int, int, int, int, bool],
) -> None:
    """Test ``get_index_ijkc`` function of DIP base class.

    Purpose: transform composite index (ijkc) of symmetry-unique elements to
             full index i,j,k,c of a dense FourIndex object.
    """
    # Some preliminaries
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=nocc * 2, ncore=ncore)
    # Initialize empty class
    ipcc = RDIPCC(lf, occ_model)
    ipcc.s_z = sz

    # distinguish between spin-degrees-of-freedom: ijkc, iJkc, iJKC, ijKC, ijkC
    # return value spin indicates the same spin block: ijkc (True) vs. ijKC (False)
    assert ipcc.get_index_ijkc(ind) == expected


test_data_check_nhole = [
    # nbasis, nocc, ncore, sz, nhole expected
    # sz = 0, ncore = 0,1
    (RDIPpCCD0, 10, 1, 0, 0, 3, False),
    (RDIPpCCD0, 10, 1, 0, 0, 2, True),
    (RDIPpCCD0, 10, 2, 1, 0, 3, False),
    (RDIPpCCD0, 10, 2, 1, 0, 2, True),
    (RDIPpCCD0, 10, 4, 0, 0, 3, True),
    (RDIPpCCD0, 10, 4, 0, 0, 2, True),
    (RDIPCCD0, 10, 1, 0, 0, 3, False),
    (RDIPCCD0, 10, 1, 0, 0, 2, True),
    (RDIPCCD0, 10, 2, 1, 0, 3, False),
    (RDIPCCD0, 10, 2, 1, 0, 2, True),
    (RDIPCCD0, 10, 4, 0, 0, 3, True),
    (RDIPCCD0, 10, 4, 0, 0, 2, True),
    (RDIPLCCD0, 10, 1, 0, 0, 3, False),
    (RDIPLCCD0, 10, 1, 0, 0, 2, True),
    (RDIPLCCD0, 10, 2, 1, 0, 3, False),
    (RDIPLCCD0, 10, 2, 1, 0, 2, True),
    (RDIPLCCD0, 10, 4, 0, 0, 3, True),
    (RDIPLCCD0, 10, 4, 0, 0, 2, True),
    (RDIPfpCCD0, 10, 1, 0, 0, 3, False),
    (RDIPfpCCD0, 10, 1, 0, 0, 2, True),
    (RDIPfpCCD0, 10, 2, 1, 0, 3, False),
    (RDIPfpCCD0, 10, 2, 1, 0, 2, True),
    (RDIPfpCCD0, 10, 4, 0, 0, 3, True),
    (RDIPfpCCD0, 10, 4, 0, 0, 2, True),
    (RDIPfpLCCD0, 10, 1, 0, 0, 3, False),
    (RDIPfpLCCD0, 10, 1, 0, 0, 2, True),
    (RDIPfpLCCD0, 10, 2, 1, 0, 3, False),
    (RDIPfpLCCD0, 10, 2, 1, 0, 2, True),
    (RDIPfpLCCD0, 10, 4, 0, 0, 3, True),
    (RDIPfpLCCD0, 10, 4, 0, 0, 2, True),
    (RDIPCCSD0, 10, 1, 0, 0, 3, False),
    (RDIPCCSD0, 10, 1, 0, 0, 2, True),
    (RDIPCCSD0, 10, 2, 1, 0, 3, False),
    (RDIPCCSD0, 10, 2, 1, 0, 2, True),
    (RDIPCCSD0, 10, 4, 0, 0, 3, True),
    (RDIPCCSD0, 10, 4, 0, 0, 2, True),
    (RDIPLCCSD0, 10, 1, 0, 0, 3, False),
    (RDIPLCCSD0, 10, 1, 0, 0, 2, True),
    (RDIPLCCSD0, 10, 2, 1, 0, 3, False),
    (RDIPLCCSD0, 10, 2, 1, 0, 2, True),
    (RDIPLCCSD0, 10, 4, 0, 0, 3, True),
    (RDIPLCCSD0, 10, 4, 0, 0, 2, True),
    (RDIPfpCCSD0, 10, 1, 0, 0, 3, False),
    (RDIPfpCCSD0, 10, 1, 0, 0, 2, True),
    (RDIPfpCCSD0, 10, 2, 1, 0, 3, False),
    (RDIPfpCCSD0, 10, 2, 1, 0, 2, True),
    (RDIPfpCCSD0, 10, 4, 0, 0, 3, True),
    (RDIPfpCCSD0, 10, 4, 0, 0, 2, True),
    (RDIPfpLCCSD0, 10, 1, 0, 0, 3, False),
    (RDIPfpLCCSD0, 10, 1, 0, 0, 2, True),
    (RDIPfpLCCSD0, 10, 2, 1, 0, 3, False),
    (RDIPfpLCCSD0, 10, 2, 1, 0, 2, True),
    (RDIPfpLCCSD0, 10, 4, 0, 0, 3, True),
    (RDIPfpLCCSD0, 10, 4, 0, 0, 2, True),
    # sz = 1, ncore = 0,1
    (RDIPpCCD2, 10, 1, 0, 2, 3, False),
    (RDIPpCCD2, 10, 1, 0, 2, 2, False),
    (RDIPpCCD2, 10, 2, 0, 2, 2, True),
    (RDIPpCCD2, 10, 2, 1, 2, 2, False),
    (RDIPpCCD2, 10, 2, 1, 2, 3, False),
    (RDIPpCCD2, 10, 3, 1, 2, 3, False),
    (RDIPpCCD2, 10, 3, 1, 2, 2, True),
    (RDIPpCCD2, 10, 4, 0, 2, 2, True),
    (RDIPpCCD2, 10, 4, 0, 2, 3, True),
    # sz = 2, ncore = 0,1
    (RDIPpCCD4, 10, 1, 0, 4, 3, False),
    (RDIPpCCD4, 10, 1, 0, 4, 2, False),
    (RDIPpCCD4, 10, 2, 0, 4, 2, False),
    (RDIPpCCD4, 10, 2, 0, 4, 3, False),
    (RDIPpCCD4, 10, 3, 0, 4, 2, False),
    (RDIPpCCD4, 10, 3, 0, 4, 3, True),
    (RDIPpCCD4, 10, 3, 1, 4, 3, False),
    (RDIPpCCD4, 10, 4, 1, 4, 3, True),
]


@pytest.mark.parametrize(
    "cls, nbasis, nocc, ncore, sz, nhole, expected", test_data_check_nhole
)
def test_check_nhole(
    cls: RDIPCC,
    nbasis: int,
    nocc: int,
    ncore: int,
    sz: int,
    nhole: int,
    expected: bool,
) -> None:
    """Test ``check_nhole`` function of DIP base class.

    Purpose: Check if nhole keyword argument (or default) is consistent with
             number of active occupied orbitals and spin projection.
             DIPpCCD:
             s_z = 0: nacto = 1, nhole = [2]
             s_z = 0: nacto > 1, nhole = [2,3]
             s_z = 1: nacto = 2, nhole = [2]
             s_z = 1: nacto > 2, nhole = [2,3]
             s_z = 2: nacto >= 3, nhole = [3]
    """
    # Some preliminaries
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=nocc * 2, ncore=ncore)
    # Initialize empty class
    ipcc = cls(lf, occ_model)
    ipcc.s_z = sz
    # have to assign private attribute
    ipcc._nhole = nhole

    assert ipcc._check_nhole() == expected
