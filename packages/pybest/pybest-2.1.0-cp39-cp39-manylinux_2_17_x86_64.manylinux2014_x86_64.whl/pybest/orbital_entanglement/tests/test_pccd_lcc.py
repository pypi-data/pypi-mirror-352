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

from pybest.orbital_entanglement.orbital_entanglement import (
    OrbitalEntanglementRpCCDLCC,
)
from pybest.orbital_entanglement.tests.common import Model

s1_ref = np.array(
    [
        0.01645669276751,
        0.01963600360018,
        0.01965325872394,
        0.01965325843777,
        0.01963600411211,
        0.01645669255274,
    ]
)

mi_ref = np.array(
    [
        [
            [0.0, 0.00613942, 0.00614475, 0.00692526, 0.00691559, 0.01308797],
            [0.00613942, 0.0, 0.00360408, 0.00357657, 0.02326247, 0.00691559],
            [0.00614475, 0.00360408, 0.0, 0.02327683, 0.00357657, 0.00692526],
            [0.00692526, 0.00357657, 0.02327683, 0.0, 0.00360408, 0.00614475],
            [0.00691559, 0.02326247, 0.00357657, 0.00360408, 0.0, 0.00613942],
            [0.01308797, 0.00691559, 0.00692526, 0.00614475, 0.00613942, 0.0],
        ],
    ]
)

test_data = [
    # basis, nel, t, v, ncore
    (6, 6, -1, 0.5, 0, {"s_1": s1_ref, "I_12": mi_ref}),
    (6, 6, -1, 0.5, 1, {}),
]


@pytest.mark.parametrize("basis,nel,t,v,ncore,expected", test_data)
def test_pccd_lcc(basis, nel, t, v, ncore, expected):
    """Test pCCD-LCCSD s_i and I_ij to reference values if available. Otherwise
    only a dry run is performed."""

    hubbard = Model(basis, nel, t, v, ncore)

    # Do RHF
    hubbard.do_rhf()
    # Do pCCD
    hubbard.do_pccd()
    # pCCD-LCCSD
    hubbard.do_pccdlccsd()

    oe = OrbitalEntanglementRpCCDLCC(hubbard.lf, hubbard.pccdlccsd)
    oe_ = oe()

    for key, value in expected.items():
        assert np.allclose(value, getattr(oe_, key).array, atol=1e-4)
