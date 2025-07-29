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

from itertools import product

import pytest

from pybest.ea_eom.sea_base import RSEACC
from pybest.ea_eom.sea_pccd1 import REApCCD1
from pybest.ea_eom.sea_pccd3 import REApCCD3
from pybest.exceptions import ArgumentError
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel

# Test for proper shape of arrays considering with and without frozen core:
# nocc, nbasis, ncore
test_data_mask = [(10, 30, 0), (10, 30, 5)]
# The current EA models do not require testing for other values of select than
# 0. The parameterization is used for future DevOps.
# alpha, select
test_data_sz = [(1, 0), (3, 0)]


@pytest.mark.parametrize("occ,nbasis,ncore", test_data_mask)
@pytest.mark.parametrize("alpha,select", test_data_sz)
def test_get_mask_shape(occ, nbasis, ncore, alpha, select):
    """Test ``get_mask`` function of EA base class:
        * shape of mask

    Purpose: return a boolean array with True values for indices that are
             non-redundant and symmetry-unique. Required to assign the proper
             elements to the dense FourIndex objects during optimization
             (avoiding for loops).

    Procedure: test for s_z = 0.5 and other s_z values separately (see comments
               in test function below).
               Small letters indicate alpha electrons, capital letters beta
               electrons (or vice versa).
    """
    # some preliminaries
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=occ * 2, ncore=ncore)
    # Initialize empty class
    eapccd = RSEACC(lf, occ_model)

    mask = eapccd.get_mask(select)
    # check shape
    assert mask.shape[0] == occ_model.nactv[0]
    assert mask.shape[1] == occ_model.nactv[0]
    assert mask.shape[2] == occ_model.nacto[0]


@pytest.mark.parametrize("occ,nbasis,ncore", test_data_mask)
@pytest.mark.parametrize("alpha,select", test_data_sz)
def test_get_mask_elements(occ, nbasis, ncore, alpha, select):
    """Test ``get_mask`` function of DEA base class:
        * elements of mask

    Purpose: return a boolean array with True values for indices that are
             non-redundant and symmetry-unique. Required to assign the proper
             elements to the dense ThreeIndex objects during optimization
             (avoiding for loops).

    Procedure: test for s_z = 0.5 and other s_z values separately (see comments
               in test function below).
               Small letters indicate alpha electrons, capital letters beta
               electrons (or vice versa).
    """
    # some preliminaries
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=occ * 2, ncore=ncore)
    # Initialize empty class
    eapccd = RSEACC(lf, occ_model)

    mask = eapccd.get_mask(select)
    # check elements
    same_spin = select == 0
    nactv, nacto = range(occ_model.nactv[0]), range(occ_model.nacto[0])
    for a, b, j in product(nactv, nactv, nacto):
        if same_spin:
            if a > b:
                assert mask[a, b, j]
            elif a <= b:
                assert not mask[a, b, j]
        else:
            raise NotImplementedError


@pytest.mark.parametrize("occ,nbasis,ncore", test_data_mask)
@pytest.mark.parametrize("alpha,select", test_data_sz)
def test_get_index_of_mask(occ, nbasis, ncore, alpha, select):
    """Test ``get_index_of_mask`` function of EA base class.

    Purpose: return the indices for which the boolean array ``get_mask`` is
             True. Those contain non-redundant and symmetry-unique elements.
             Required to assign the proper elements from the dense ThreeIndex
             objects to the OneIndex object stored during optimization
             (avoiding for loops).

    Procedure: test for s_z = 0.5 and other s_z values separately (see comments
               in test function below).
               We test if the indices returned by the ``get_index_of_mask``
               function fulfill the symmetry requirements, like a<b, etc.
               Small letters indicate alpha electrons, capital letters beta
               electrons (or vice versa).
    """
    # some preliminaries
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=occ * 2, ncore=ncore)
    # Initialize empty class
    eapccd = RSEACC(lf, occ_model)

    mask = eapccd.get_index_of_mask(select)
    # check elements
    dim = len(mask[0])
    for i in range(dim):
        assert mask[0][i] > mask[1][i]
        assert mask[0][i] < (occ_model.nactv[0])
        assert mask[1][i] < (occ_model.nactv[0] - 1)
        assert mask[2][i] < (occ_model.nacto[0])


test_data_alpha = [
    (RSEACC, -1),
    (REApCCD1, 1),
    (REApCCD3, 3),
]


@pytest.mark.parametrize("cls,expected", test_data_alpha)
def test_alpha(cls, expected):
    """Check consistency of class attributes"""
    # some preliminaries
    lf = DenseLinalgFactory(10)
    occ_model = AufbauOccModel(lf, nel=8, ncore=0)
    # Initialize empty class
    eacc = cls(lf, occ_model)

    assert eacc.alpha == expected


test_data_n_particle_operator = [
    # nbasis, nocc, n_particle_operator
    (10, 4, 2),
    (10, 8, 2),
    (10, 9, 2),
    (10, 8, 1),
    (10, 9, 1),
]


@pytest.mark.parametrize("nbasis,nocc,np", test_data_n_particle_operator)
def test_n_particle_operator_setter(nbasis, nocc, np):
    """Check consistency of class attributes"""
    # some preliminaries
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=nocc * 2, ncore=0)
    # Initialize empty class
    eacc = RSEACC(lf, occ_model)

    try:
        eacc.n_particle_operator = np
    except Exception:
        # Only ArgumemtError is valid here
        with pytest.raises(ArgumentError):
            eacc.n_particle_operator = np


test_data_get_index_abj = [
    # nbasis, nocc, ncore, ind, expected
    # abj
    (10, 4, 0, 0, (0, 1, 0, True)),
    (10, 4, 0, 4, (0, 2, 0, True)),
    (10, 4, 0, 27, (1, 3, 3, True)),
    (10, 4, 0, 59, (4, 5, 3, True)),
    # aBJ
    (10, 4, 0, 60, (0, 0, 0, False)),
    (10, 4, 0, 80, (0, 5, 0, False)),
    (10, 4, 0, 79, (0, 4, 3, False)),
    (10, 4, 0, 122, (2, 3, 2, False)),
    (10, 4, 0, 144, (3, 3, 0, False)),
    (10, 4, 0, 203, (5, 5, 3, False)),
    # ncore = 1
    (10, 4, 1, 0, (0, 1, 0, True)),
    (10, 4, 1, 4, (0, 2, 1, True)),
    (10, 4, 1, 27, (2, 3, 0, True)),
    (10, 4, 1, 44, (4, 5, 2, True)),
    (10, 4, 1, 60, (0, 5, 0, False)),
    (10, 4, 1, 80, (1, 5, 2, False)),
    (10, 4, 1, 79, (1, 5, 1, False)),
    (10, 4, 1, 122, (4, 1, 2, False)),
    (10, 4, 1, 144, (5, 3, 0, False)),
    (10, 4, 1, 152, (5, 5, 2, False)),
]


@pytest.mark.parametrize(
    "nbasis,nocc,ncore,ind,expected", test_data_get_index_abj
)
def test_get_index_abj(nbasis, nocc, ncore, ind, expected):
    """Test ``get_index_abj`` function of EA base class.

    Purpose: transform composite index (abj) of symmetry-unique elements to
             full index a,b,j or a,B,J of a dense ThreeIndex object.
    """
    # some preliminaries
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=nocc * 2, ncore=ncore)
    # Initialize empty class
    eacc = RSEACC(lf, occ_model)

    assert eacc.get_index_abj(ind) == expected
