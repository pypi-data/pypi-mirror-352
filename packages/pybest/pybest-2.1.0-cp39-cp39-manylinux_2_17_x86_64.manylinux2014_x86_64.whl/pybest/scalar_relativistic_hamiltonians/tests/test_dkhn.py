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

#
# Detailed changelog:
#
# 2025-05-23: scalar relativistic hamiltonians tests implementation (Kacper Cieslak)
#

import numpy as np
import pytest

import pybest

if pybest.gbasis.dense_ints.PYBEST_PVP_ENABLED:
    from pybest.scalar_relativistic_hamiltonians.dkhn import DKHN


@pytest.mark.skipif(
    not pybest.gbasis.dense_ints.PYBEST_PVP_ENABLED,
    reason="pVp integrals not supported.",
)
def test_dkhn(dkhn_refs):
    """DKH2 test"""
    dkhn_hamiltonian = DKHN(dkhn_refs[2])

    dkh2_ints = dkhn_hamiltonian()

    assert dkh2_ints.nbasis == dkh2_ints.nbasis1 == dkhn_refs[0]

    np.testing.assert_allclose(
        dkh2_ints.array, dkhn_refs[1], rtol=dkhn_refs[3], atol=dkhn_refs[4]
    )
