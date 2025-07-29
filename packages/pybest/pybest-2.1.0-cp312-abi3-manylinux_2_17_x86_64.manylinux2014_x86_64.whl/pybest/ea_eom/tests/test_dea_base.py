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

from __future__ import annotations

from itertools import product
from typing import Any

import pytest

from pybest.ea_eom.dea_base import RDEACC, RDEACC0, RDEACC2, RDEACC4
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel

# Test for proper shape of arrays considering with and without frozen core:
# (nocc, nbasis, ncore)
test_data_mask = [(10, 30, 0), (10, 30, 5)]
# Test for proper shape of arrays considering various values for alpha/S_z:
# alpha/S_z, same/opposite spin block, shift (1: without diagonal [same spin],
# 0: with diagonal elements [opposite spin])
test_data_sz = [
    (0, [True, False], [1, 0]),
    (2, [True, False], [1, 0]),
    (4, [True], [1]),
]


@pytest.mark.parametrize("sz,spin,shift", test_data_sz)
@pytest.mark.parametrize("occ,nbasis,ncore", test_data_mask)
def test_get_mask_shape(
    sz: int,
    spin: list[Any],
    shift: list[Any],
    occ: int,
    nbasis: int,
    ncore: int,
):
    """Test ``get_mask`` function of DEA base class:
        * shape of mask

    Purpose: return a boolean array with True values for indices that are
             non-redundant and symmetry-unique. Required to assign the proper
             elements to the dense FourIndex objects during optimization
             (avoiding for loops).

    Procedure: test for s_z = 0.0 and other s_z values separately (see comments
               in test function below).
               Small letters indicate alpha electrons, capital letters beta
               electrons (or vice versa).
    """
    # some preliminaries
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=occ * 2, ncore=ncore)
    # Initialize empty (base) class
    deacc = RDEACC(lf, occ_model)
    # We overwrite (class attribute) alpha here with an instance attribute
    # as we need the proper s_z. Namespace of instance has priority over
    # namespace of class
    deacc.alpha = sz

    mask = [deacc.get_mask(spin_) for spin_ in spin]
    nactv, nacto = occ_model.nactv[0], occ_model.nacto[0]
    # check shape
    for mask_ in mask:
        assert mask_.shape == (nactv, nactv, nactv, nacto)


@pytest.mark.parametrize("sz,spin,shift", test_data_sz)
@pytest.mark.parametrize("occ,nbasis,ncore", test_data_mask)
def test_get_mask_elements(
    sz: int,
    spin: list[Any],
    shift: list[Any],
    occ: int,
    nbasis: int,
    ncore: int,
):
    """Test ``get_mask`` function of DEA base class:
        * elements of mask

    Purpose: return a boolean array with True values for indices that are
             non-redundant and symmetry-unique. Required to assign the proper
             elements to the dense FourIndex objects during optimization
             (avoiding for loops).

    Procedure: test for s_z = 0.0 and other s_z values separately (see comments
               in test function below).
               Small letters indicate alpha electrons, capital letters beta
               electrons (or vice versa).
    """
    # some preliminaries
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=occ * 2, ncore=ncore)
    # Initialize empty (base) class
    deacc = RDEACC(lf, occ_model)
    # We overwrite (class attribute) alpha here with an instance attribute
    # as we need the proper s_z. Namespace of instance has priority over
    # namespace of class
    deacc.alpha = sz

    mask = [deacc.get_mask(spin_) for spin_ in spin]
    nacto, nactv = range(occ_model.nacto[0]), range(occ_model.nactv[0])
    # check elements
    for mask_, spin_ in zip(mask, spin):
        for a, b, c, k in product(nactv, nactv, nactv, nacto):
            if sz == 0:
                if spin_ and a < c:
                    # unique block (a)
                    assert mask_[a, b, c, k], "wrong R_aBck element for S_z=0"
                elif not spin_ and b < c:
                    # unique block (aBCK)
                    assert mask_[a, b, c, k], "wrong R_aBCK element for S_z=0"
                else:
                    # all other elements have to be False
                    assert not mask_[
                        a, b, c, k
                    ], "wrong mask element for S_z=0"
            else:
                if spin_ and a < b < c:
                    # unique block (abck) (also works for s_z = 2)
                    assert mask_[a, b, c, k], "wrong R_abck element for S_z>0"
                elif not spin_ and a < b:
                    # unique block (abCK)
                    assert mask_[a, b, c, k], "wrong R_abCK element for S_z=1"
                else:
                    # all other elements have to be False
                    assert not mask_[
                        a, b, c, k
                    ], "wrong mask element for S_z>0"


@pytest.mark.parametrize("sz,spin,shift", test_data_sz)
@pytest.mark.parametrize("occ,nbasis,ncore", test_data_mask)
def test_get_index_of_mask(
    sz: int,
    spin: list[Any],
    shift: list[Any],
    occ: int,
    nbasis: int,
    ncore: int,
):
    """Test ``get_index_of_mask`` function of DEA base class.

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
    # some preliminaries
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=occ * 2, ncore=ncore)
    # Initialize empty (base) class
    deacc = RDEACC(lf, occ_model)
    # We overwrite (class attribute) alpha here by an instance attribute
    # as we need the proper s_z. Namespace of instance has priority over
    # namespace of class
    deacc.alpha = sz

    mask = [deacc.get_index_of_mask(spin_) for spin_ in spin]
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
                    assert mask[i][0][j] < (nactv - 1)
                    assert mask[i][1][j] < (nactv)
                else:
                    # check j<k for same spin, unique block (iJKC)
                    assert mask[i][1][j] < mask[i][2][j]
                    assert mask[i][0][j] < (nactv)
                    assert mask[i][1][j] < (nactv - 1)
                assert mask[i][2][j] < (nactv)
                assert mask[i][3][j] < (nacto)
            else:
                # check i<j, unique block (ijkc) and (ijKC)
                assert mask[i][0][j] < mask[i][1][j]
                if spin[i]:
                    # check j<k for same spin, unique block (ijkc) and (ijkC)
                    assert mask[i][1][j] < mask[i][2][j]
                assert mask[i][0][j] < (nactv - 1 - shift[i])
                assert mask[i][1][j] < (nactv - shift[i])
                assert mask[i][2][j] < (nactv)
                assert mask[i][3][j] < (nacto)


test_data_alpha = [
    (RDEACC, -1),
    (RDEACC0, 0),
    (RDEACC2, 2),
    (RDEACC4, 4),
]


@pytest.mark.parametrize("cls,expected", test_data_alpha)
def test_alpha(cls: RDEACC | RDEACC0 | RDEACC2 | RDEACC4, expected: int):
    """Check consistency of class attributes"""
    # some preliminaries
    lf = DenseLinalgFactory(10)
    occ_model = AufbauOccModel(lf, nel=8, ncore=0)
    # Initialize empty class
    eacc = cls(lf, occ_model)

    assert eacc.alpha == expected


test_data_get_index_ab = [
    # nbasis, nocc, ncore, alpha, index, result
    # sz = 1, ncore = 0, ab
    (10, 4, 0, 2, 0, (0, 1)),
    (10, 4, 0, 2, 6, (1, 3)),
    (10, 4, 0, 2, 14, (4, 5)),
    # sz = 1, ncore = 1
    (10, 4, 1, 2, 0, (0, 1)),
    (10, 4, 1, 2, 6, (1, 3)),
    (10, 4, 1, 2, 14, (4, 5)),
    # sz = 0, ncore = 0, aB
    (10, 4, 0, 0, 0, (0, 0)),
    (10, 4, 0, 0, 6, (1, 0)),
    (10, 4, 0, 0, 14, (2, 2)),
    (10, 4, 0, 0, 27, (4, 3)),
    (10, 4, 0, 0, 35, (5, 5)),
    # sz = 0, ncore = 1
    (10, 4, 1, 0, 0, (0, 0)),
    (10, 4, 1, 0, 6, (1, 0)),
    (10, 4, 1, 0, 14, (2, 2)),
    (10, 4, 1, 0, 27, (4, 3)),
    (10, 4, 1, 0, 35, (5, 5)),
]


@pytest.mark.parametrize(
    "nbasis,nocc,ncore,alpha,ind,expected", test_data_get_index_ab
)
def test_get_index_ab(
    nbasis: int,
    nocc: int,
    ncore: int,
    alpha: int,
    ind: int,
    expected: tuple[int, int],
):
    """Test ``get_index_ab`` function of DEA base class.

    Purpose: transform composite index (ab) of symmetry-unique elements to
             full index a,b of a dense FourIndex object.
    """
    # some preliminaries
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=nocc * 2, ncore=ncore)
    # Initialize empty class
    eacc = RDEACC(lf, occ_model)
    # We overwrite (class attribute) alpha here by an instance attribute
    # as we need the proper s_z. Namespace of instance has priority over
    # namespace of class
    eacc.alpha = alpha

    # distinguish between spin-degrees-of-freedom: ab, aB
    assert eacc.get_index_ab(ind) == expected


test_data_get_index_abck = [
    # nbasis, nocc, ncore, alpha, index, result
    # sz = 2, ncore = 0
    (10, 4, 0, 4, 0, (0, 1, 2, 0, None)),
    (10, 4, 0, 4, 4, (0, 1, 3, 0, None)),
    (10, 4, 0, 4, 17, (0, 2, 3, 1, None)),
    (10, 4, 0, 4, 30, (0, 3, 4, 2, None)),
    (10, 4, 0, 4, 66, (2, 3, 4, 2, None)),
    (10, 4, 0, 4, 79, (3, 4, 5, 3, None)),
    # sz = 2, ncore = 1
    (10, 4, 1, 4, 0, (0, 1, 2, 0, None)),
    (10, 4, 1, 4, 4, (0, 1, 3, 1, None)),
    (10, 4, 1, 4, 17, (0, 2, 4, 2, None)),
    (10, 4, 1, 4, 30, (1, 2, 3, 0, None)),
    (10, 4, 1, 4, 45, (1, 4, 5, 0, None)),
    (10, 4, 1, 4, 59, (3, 4, 5, 2, None)),
    # sz = 1, ncore = 0, abck
    (10, 4, 0, 2, 0, (0, 1, 2, 0, True)),
    (10, 4, 0, 2, 4, (0, 1, 3, 0, True)),
    (10, 4, 0, 2, 17, (0, 2, 3, 1, True)),
    (10, 4, 0, 2, 30, (0, 3, 4, 2, True)),
    (10, 4, 0, 2, 66, (2, 3, 4, 2, True)),
    (10, 4, 0, 2, 79, (3, 4, 5, 3, True)),
    # sz = 1, ncore = 0, abCK
    (10, 4, 0, 2, 80, (0, 1, 0, 0, False)),
    (10, 4, 0, 2, 86, (0, 1, 1, 2, False)),
    (10, 4, 0, 2, 94, (0, 1, 3, 2, False)),
    (10, 4, 0, 2, 128, (0, 3, 0, 0, False)),
    (10, 4, 0, 2, 179, (0, 5, 0, 3, False)),
    (10, 4, 0, 2, 256, (1, 4, 2, 0, False)),
    (10, 4, 0, 2, 283, (1, 5, 2, 3, False)),
    (10, 4, 0, 2, 329, (2, 4, 2, 1, False)),
    (10, 4, 0, 2, 388, (3, 4, 5, 0, False)),
    (10, 4, 0, 2, 439, (4, 5, 5, 3, False)),
    # sz = 1, ncore = 1, abck
    (10, 4, 1, 2, 0, (0, 1, 2, 0, True)),
    (10, 4, 1, 2, 4, (0, 1, 3, 1, True)),
    (10, 4, 1, 2, 17, (0, 2, 4, 2, True)),
    (10, 4, 1, 2, 30, (1, 2, 3, 0, True)),
    (10, 4, 1, 2, 45, (1, 4, 5, 0, True)),
    (10, 4, 1, 2, 59, (3, 4, 5, 2, True)),
    # sz = 1, ncore = 1, abCK
    (10, 4, 1, 2, 60, (0, 1, 0, 0, False)),
    (10, 4, 1, 2, 64, (0, 1, 1, 1, False)),
    (10, 4, 1, 2, 77, (0, 1, 5, 2, False)),
    (10, 4, 1, 2, 90, (0, 2, 4, 0, False)),
    (10, 4, 1, 2, 105, (0, 3, 3, 0, False)),
    (10, 4, 1, 2, 135, (0, 5, 1, 0, False)),
    (10, 4, 1, 2, 149, (0, 5, 5, 2, False)),
    (10, 4, 1, 2, 187, (1, 4, 0, 1, False)),
    (10, 4, 1, 2, 249, (2, 4, 3, 0, False)),
    (10, 4, 1, 2, 300, (3, 5, 2, 0, False)),
    (10, 4, 1, 2, 329, (4, 5, 5, 2, False)),
    # sz = 0, ncore = 0, aBck
    (10, 4, 0, 0, 0, (0, 0, 1, 0, True)),
    (10, 4, 0, 0, 6, (0, 0, 2, 2, True)),
    (10, 4, 0, 0, 14, (0, 0, 4, 2, True)),
    (10, 4, 0, 0, 48, (0, 2, 3, 0, True)),
    (10, 4, 0, 0, 99, (0, 4, 5, 3, True)),
    (10, 4, 0, 0, 176, (1, 3, 4, 0, True)),
    (10, 4, 0, 0, 203, (1, 5, 2, 3, True)),
    (10, 4, 0, 0, 249, (2, 2, 5, 1, True)),
    (10, 4, 0, 0, 308, (3, 2, 5, 0, True)),
    (10, 4, 0, 0, 359, (4, 5, 5, 3, True)),
    # sz = 0, ncore = 0, aBCK
    (10, 4, 0, 0, 360, (0, 0, 1, 0, False)),
    (10, 4, 0, 0, 366, (0, 0, 2, 2, False)),
    (10, 4, 0, 0, 374, (0, 0, 4, 2, False)),
    (10, 4, 0, 0, 408, (0, 3, 4, 0, False)),
    (10, 4, 0, 0, 459, (1, 2, 3, 3, False)),
    (10, 4, 0, 0, 536, (2, 4, 5, 0, False)),
    (10, 4, 0, 0, 563, (3, 1, 2, 3, False)),
    (10, 4, 0, 0, 609, (4, 0, 3, 1, False)),
    (10, 4, 0, 0, 668, (5, 0, 3, 0, False)),
    (10, 4, 0, 0, 719, (5, 4, 5, 3, False)),
    # sz = 0, ncore = 1, aBck
    (10, 4, 1, 0, 0, (0, 0, 1, 0, True)),
    (10, 4, 1, 0, 4, (0, 0, 2, 1, True)),
    (10, 4, 1, 0, 17, (0, 1, 1, 2, True)),
    (10, 4, 1, 0, 30, (0, 2, 1, 0, True)),
    (10, 4, 1, 0, 45, (0, 3, 1, 0, True)),
    (10, 4, 1, 0, 75, (0, 5, 1, 0, True)),
    (10, 4, 1, 0, 89, (0, 5, 5, 2, True)),
    (10, 4, 1, 0, 127, (1, 3, 2, 1, True)),
    (10, 4, 1, 0, 189, (2, 3, 3, 0, True)),
    (10, 4, 1, 0, 240, (3, 4, 4, 0, True)),
    (10, 4, 1, 0, 269, (4, 5, 5, 2, True)),
    # sz = 0, ncore = 1, iJKC
    (10, 4, 1, 0, 270, (0, 0, 1, 0, False)),
    (10, 4, 1, 0, 274, (0, 0, 2, 1, False)),
    (10, 4, 1, 0, 287, (0, 1, 2, 2, False)),
    (10, 4, 1, 0, 300, (0, 2, 4, 0, False)),
    (10, 4, 1, 0, 315, (1, 0, 1, 0, False)),
    (10, 4, 1, 0, 345, (1, 2, 4, 0, False)),
    (10, 4, 1, 0, 359, (1, 4, 5, 2, False)),
    (10, 4, 1, 0, 397, (2, 3, 4, 1, False)),
    (10, 4, 1, 0, 459, (4, 0, 4, 0, False)),
    (10, 4, 1, 0, 510, (5, 1, 2, 0, False)),
    (10, 4, 1, 0, 539, (5, 4, 5, 2, False)),
]


@pytest.mark.parametrize(
    "nbasis,nocc,ncore,alpha,ind,expected", test_data_get_index_abck
)
def test_get_index_abck(
    nbasis: int,
    nocc: int,
    ncore: int,
    alpha: int,
    ind: int,
    expected: tuple[int, int, int, int, bool | None],
):
    """Test ``get_index_abck`` function of DEA base class.

    Purpose: transform composite index (abck) of symmetry-unique elements to
             full index a,b,c,k of a dense FourIndex object.
    """
    # some preliminaries
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=nocc * 2, ncore=ncore)
    # Initialize empty class
    eacc = RDEACC(lf, occ_model)
    # We overwrite (class attribute) alpha here by an instance attribute
    # as we need the proper s_z. Namespace of instance has priority over
    # namespace of class
    eacc.alpha = alpha

    # distinguish between spin-degrees-of-freedom: abck, abck, abCK, aBck, aBCK
    # return value spin indicates the same spin block: abck (True) vs. abCK (False)
    assert eacc.get_index_abck(ind) == expected


test_data_check_n_particle_operator = [
    # nbasis, nocc, ncore, n_particle_operator, expected
    # sz = 0, ncore = 0,1
    (RDEACC0, 10, 9, 0, 3, False),
    (RDEACC0, 10, 9, 0, 2, True),
    (RDEACC0, 10, 9, 1, 3, False),
    (RDEACC0, 10, 8, 1, 2, True),
    (RDEACC0, 10, 7, 0, 3, True),
    (RDEACC0, 10, 7, 0, 2, True),
    # sz = 1, ncore = 0,1
    (RDEACC2, 10, 9, 0, 3, False),
    (RDEACC2, 10, 8, 0, 3, False),
    (RDEACC2, 10, 9, 0, 2, False),
    (RDEACC2, 10, 8, 0, 2, True),
    (RDEACC2, 10, 9, 1, 2, False),
    (RDEACC2, 10, 8, 1, 3, False),
    (RDEACC2, 10, 7, 1, 2, True),
    (RDEACC2, 10, 7, 0, 2, True),
    (RDEACC2, 10, 7, 0, 3, True),
    # sz = 2, ncore = 0,1
    (RDEACC4, 10, 8, 0, 3, False),
    (RDEACC4, 10, 8, 0, 2, False),
    (RDEACC4, 10, 6, 0, 2, False),
    (RDEACC4, 10, 9, 0, 3, False),
    (RDEACC4, 10, 7, 0, 3, True),
    (RDEACC4, 10, 8, 1, 3, False),
    (RDEACC4, 10, 4, 1, 3, True),
]


@pytest.mark.parametrize(
    "cls,nbasis,nocc,ncore,n_particle_operator,expected",
    test_data_check_n_particle_operator,
)
def test_check_n_particle_operator(
    cls: RDEACC0 | RDEACC2 | RDEACC4,
    nbasis: int,
    nocc: int,
    ncore: int,
    n_particle_operator: int,
    expected: bool,
):
    """Test ``check_n_particle_operator`` function of DEA base class.

    Purpose: Check if nhole keyword argument (or default) is consistent with
             number of active occupied orbitals and spin projection.
             s_z = 0: nactv = 1, n_particle_operator = [2]
             s_z = 0: nactv > 1, n_particle_operator = [2,3]
             s_z = 1: nactv = 2, n_particle_operator = [2]
             s_z = 1: nactv > 2, n_particle_operator = [2,3]
             s_z = 2: nactv >= 3, n_particle_operator = [3]
    """
    # some preliminaries
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=nocc * 2, ncore=ncore)
    # Initialize empty class
    eacc = cls(lf, occ_model)
    # have to assign private attribute
    eacc._n_particle_operator = n_particle_operator

    assert eacc._check_n_particle_operator() == expected
