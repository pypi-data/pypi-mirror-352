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
# The RSF-CC sub-package has been originally written and updated by Aleksandra Leszczyk (see CHANGELOG)
# Its current version contains updates from the PyBEST developer team.
#
# 2023/24:
# This file has been updated by Emil Sujkowski
from __future__ import annotations

import pytest

from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel
from pybest.rsf_eom.rsf_ccsd4 import RSFCCSD4


@pytest.mark.parametrize(
    "nacto, nactv, exp_i, exp_a, exp_j, exp_b, index",
    [
        # nacto = 2, nactv = 4
        (2, 4, 0, 0, 1, 1, 0),
        (2, 4, 0, 0, 1, 2, 1),
        (2, 4, 0, 0, 1, 3, 2),
        (2, 4, 0, 1, 1, 2, 3),
        (2, 4, 0, 1, 1, 3, 4),
        (2, 4, 0, 2, 1, 3, 5),
        # nacto = 3, nactv = 4
        (3, 4, 0, 0, 1, 1, 0),
        (3, 4, 0, 0, 1, 2, 1),
        (3, 4, 0, 1, 1, 3, 7),
        (3, 4, 1, 0, 2, 1, 12),
        (3, 4, 1, 1, 2, 2, 15),
        (3, 4, 1, 2, 2, 3, 17),
        # nacto = 4, nactv = 5
        (4, 5, 0, 0, 1, 1, 0),
        (4, 5, 0, 0, 2, 2, 5),
        (4, 5, 0, 0, 3, 3, 10),
        (4, 5, 0, 2, 2, 3, 23),
        (4, 5, 1, 0, 2, 2, 31),
        (4, 5, 1, 1, 3, 3, 42),
        (4, 5, 1, 3, 3, 4, 49),
        (4, 5, 2, 3, 3, 4, 59),
    ],
)
def test_get_index_iajb(
    nacto: int,
    nactv: int,
    exp_i: int,
    exp_a: int,
    exp_j: int,
    exp_b: int,
    index: int,
) -> None:
    """Check if the hole-particle-hole-particle indices from composite index of CI vector are calculated correctly,
    based on the dimension i<j a<b
    """
    lf = DenseLinalgFactory(nacto + nactv)
    occ_model = AufbauOccModel(lf, nel=nacto * 2)
    eom = RSFCCSD4(lf, occ_model)

    i, a, j, b = eom.get_index_iajb(index)
    assert exp_i == i, "Index i differs from expected value"
    assert exp_a == a, "Index a differs from expected value"
    assert exp_j == j, "Index j differs from expected value"
    assert exp_b == b, "Index b differs from expected value"
