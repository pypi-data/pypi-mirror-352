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
# 2025-03: incorporation of new molecue testing framework (Julia Szczuczko)

from __future__ import annotations

import pytest

from ...tests.common import load_reference_data
from .common import IP_EOMMolecule


#
# Define fixtures for testing: NO^{-}
#
@pytest.fixture
def no_1m(linalg: str) -> IP_EOMMolecule:
    """Returns instance of IP_EOMMolecule for NO^- that contains all information
    to perform several calculations (integrals, methods, etc.).
    """
    return IP_EOMMolecule("no", "cc-pvdz", linalg, charge=-1, ncore=0)


#
# Define fixtures for testing: C^{2-}
#
@pytest.fixture
def c_2m(linalg: str) -> IP_EOMMolecule:
    """Returns instance of IP_EOMMolecule for C^2- that contains all information
    to perform several calculations (integrals, methods, etc.).
    """
    return IP_EOMMolecule("c", "cc-pvdz", linalg, charge=-2, ncore=0)


#
# Define fixtures for testing: Be_2
#
@pytest.fixture
def be_2(
    linalg_slow: str,
) -> dict[str, IP_EOMMolecule | dict[str, float | list[float] | object]]:
    """Returns instance of IP_EOMMolecule for Be_2 that contains all information
    to perform several calculations (integrals, methods, etc.) and the
    corresponding solutions.
    """
    molecule = IP_EOMMolecule("be2", "cc-pvdz", linalg_slow, ncore=0)
    results = load_reference_data("series", "be2", "cc-pvdz")
    return {"molecule": molecule, "results": results}
