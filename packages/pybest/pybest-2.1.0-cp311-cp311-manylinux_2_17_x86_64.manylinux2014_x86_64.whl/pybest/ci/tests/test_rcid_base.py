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


import itertools

import pytest

from pybest.ci.xci import RCID
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel

# nel, nbasis, core
testdata_mask = [(6, 28, 0), (6, 28, 1)]


@pytest.mark.parametrize("nel,nbasis,ncore", testdata_mask)
def test_get_mask(nel, nbasis, ncore):
    """Tests if the get_mask function creates the proper shape of
    4-dimensional boolean np.array and checks if the boolean values are assigned
    correctly due to the restrictions on non-redundant and symmetry-unique
    elements of the CI coefficient tensor for double excitations."""
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=nel, ncore=ncore)
    rcid = RCID(lf, occ_model, csf=False)
    mask = rcid.get_mask()
    nacto = occ_model.nacto[0]
    nactv = occ_model.nactv[0]
    # check shape
    assert mask.shape == (nacto, nactv, nacto, nactv)
    # check elements
    o_max = list(range(1, nacto))
    v_max = list(range(1, nactv))
    for i, a, j, b in itertools.product(o_max, v_max, o_max, v_max):
        if i < j and a < b:
            assert mask[i, a, j, b]
        elif (i >= j) and (a >= b):
            assert not mask[i, a, j, b]


@pytest.mark.parametrize("nel,nbasis,ncore", testdata_mask)
def test_get_index_of_mask(nel, nbasis, ncore):
    """Checks if the get_index_of_mask function selects the proper indices
    imposed by non-redundant and symmetry-unique elements
    of the CI coefficient tensor for double excitations."""
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=nel, ncore=ncore)
    rcid = RCID(lf, occ_model, csf=False)

    mask = rcid.get_index_of_mask()
    dim = len(mask[0])
    for i in range(dim):
        assert mask[0][i] < mask[2][i]
        assert mask[1][i] < mask[3][i]
        assert mask[2][i] < (occ_model.nacto[0])
        assert mask[3][i] < (occ_model.nactv[0])


shift = 6 * 6 * 22 * 22
shift1 = 5 * 5 * 22 * 22

testdata_get_index_d = [
    (28, 12, 0, shift + 13, (1, 7, 2, 21)),
    (28, 12, 0, shift + 145, (1, 8, 4, 9)),
    (28, 12, 0, shift + 1156, (2, 7, 3, 9)),
    (28, 12, 0, shift + 3333, (5, 12, 6, 17)),
    (28, 12, 1, shift1 + 10, (1, 6, 2, 17)),
    (28, 12, 1, shift1 + 153, (1, 7, 5, 17)),
    (28, 12, 1, shift1 + 1053, (2, 8, 3, 15)),
    (28, 12, 1, shift1 + 2300, (4, 23, 5, 24)),
]


@pytest.mark.parametrize("nbasis,nel,ncore,ind,expected", testdata_get_index_d)
def test_get_index_d(nbasis, nel, ncore, ind, expected):
    """Checks if the get_index_d function predicts a proper set of active orbital
    indices of some doubly excited SD wavefunction in variants with and without
    frozen core"""
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=nel, ncore=ncore)
    rcid = RCID(lf, occ_model, csf=False)

    assert rcid.get_index_d(ind) == expected


#
# CSF
#
parameters = ["iajb", "iab", "iaj"]
testdata_mask = [(6, 28, 0, parameters), (6, 28, 1, parameters)]


@pytest.mark.parametrize("nel,nbasis,ncore,parameters", testdata_mask)
def test_get_mask_csf(nel, nbasis, ncore, parameters):
    """Tests if the get_mask function creates the proper shape of
    4-dimensional boolean np.array and checks if the boolean values are assigned
    correctly due to the restrictions on non-redundant and symmetry-unique
    elements of the CI coefficient tensor for double excitations."""
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=nel, ncore=ncore)
    rcid = RCID(lf, occ_model, csf=True)
    nacto = occ_model.nacto[0]
    nactv = occ_model.nactv[0]
    for select in parameters:
        mask = rcid.get_mask(select)
        # check shape
        assert mask.shape == (nacto, nactv, nacto, nactv)

        o_max = list(range(1, nacto))
        v_max = list(range(1, nactv))
        if select == "iajb":
            # check elements
            for i, a, j, b in itertools.product(o_max, v_max, o_max, v_max):
                if i < j and a < b:
                    assert mask[i, a, j, b]
                elif (i >= j) and (a >= b):
                    assert not mask[i, a, j, b]

        if select == "iab":
            # check elements
            for i, a, j, b in itertools.product(o_max, v_max, o_max, v_max):
                if i == j and a < b:
                    assert mask[i, a, j, b]
                elif (i != j) and (a >= b):
                    assert not mask[i, a, j, b]

        if select == "iaj":
            # check elements
            for i, a, j, b in itertools.product(o_max, v_max, o_max, v_max):
                if a == b and i < j:
                    assert mask[i, a, j, b]
                elif (a != b) and (i >= j):
                    assert not mask[i, a, j, b]


@pytest.mark.parametrize("nel,nbasis,ncore,parameters", testdata_mask)
def test_get_index_of_mask_csf(nel, nbasis, ncore, parameters):
    """Tests if the get_mask function creates the proper shape of
    4-dimensional boolean np.array and checks if the boolean values are assigned
    correctly due to the restrictions on non-redundant and symmetry-unique
    elements of the CI coefficient tensor for double excitations."""
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=nel, ncore=ncore)
    rcid = RCID(lf, occ_model, csf=True)

    for select in parameters:
        mask = rcid.get_index_of_mask(select)
        dim = len(mask)
        if select == "iajb":
            for i in range(dim):
                assert mask[0][i] < mask[2][i]
                assert mask[1][i] < mask[3][i]
                assert mask[2][i] < (nel - ncore)
                assert mask[3][i] < (nbasis - nel)

        if select == "iab":
            for i in range(dim):
                assert mask[0][i] == mask[2][i]
                assert mask[1][i] < mask[3][i]
                assert mask[2][i] < (nel - ncore)
                assert mask[3][i] < (nbasis - nel)

        if select == "iaj":
            for i in range(dim):
                assert mask[0][i] < mask[2][i]
                assert mask[1][i] == mask[3][i]
                assert mask[2][i] < (nel - ncore)
                assert mask[3][i] < (nbasis - nel)


testdata_get_index_d_csf = [
    (28, 12, 0, 139, (1, 7, 1, 15)),
    (28, 12, 0, 33, (2, 18, 2, 18)),
    (28, 12, 0, 475, (2, 13, 2, 15)),
    (28, 12, 0, 1650, (2, 12, 5, 12)),
    (28, 12, 0, 5181, (5, 12, 6, 17)),
    (28, 12, 0, 8313, (4, 13, 5, 20)),
]


@pytest.mark.parametrize(
    "nbasis,nel,ncore,ind,expected", testdata_get_index_d_csf
)
def test_get_index_d_csf(nbasis, nel, ncore, ind, expected):
    """Checks if the get_index_d_csf function predicts a proper set of active orbital
    indices of some doubly excited CSF wavefunction in variants with and without
    frozen core"""
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=nel, ncore=ncore)
    rcid = RCID(lf, occ_model, csf=True)
    assert rcid.get_index_d(ind) == expected
