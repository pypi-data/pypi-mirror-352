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
# 2024-04-24: created by Katharina Boguslawski (taken from old utils.py)

"""Utility functions to obtain useful information from molecules"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pybest.iodata import IOData
from pybest.periodic import periodic

__all__ = [
    "get_com",
]


def get_com(mol: IOData) -> NDArray[np.float64]:
    """Calculate center of mass with respect to atomic numbers

    mol
        An IOData istance containing information about the molecule OR
        a PyBasis instance
    """
    summass = 0.0
    com = np.zeros((3), float)
    # Only need this for IOData container
    numbers = np.array([periodic[i].number for i in mol.atom])
    for key, i in zip(numbers, range(len(numbers))):
        mass = periodic[key].number
        summass += mass
        # Convert to np array in case of list
        com += mass * np.array(mol.coordinates[i])
    com /= summass
    return com
