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
    from pybest.scalar_relativistic_hamiltonians.x2c import X2C


@pytest.mark.skipif(
    not pybest.gbasis.dense_ints.PYBEST_PVP_ENABLED,
    reason="pVp integrals not supported.",
)
def test_x2c(x2c_refs):
    """X2C test"""
    x2c_hamiltonian = X2C(x2c_refs[2])

    x2c_ints = x2c_hamiltonian()

    assert x2c_ints.nbasis == x2c_ints.nbasis1 == x2c_refs[0]

    np.testing.assert_allclose(
        x2c_ints.array, x2c_refs[1], rtol=x2c_refs[3], atol=x2c_refs[4]
    )
