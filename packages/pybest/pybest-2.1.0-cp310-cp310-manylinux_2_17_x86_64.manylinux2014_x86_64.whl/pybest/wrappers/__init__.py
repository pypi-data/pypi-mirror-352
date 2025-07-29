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
"""Wrappers"""

# define test runner
from pybest._pytesttester import PytestTester

from .hf import RHF, UHF
from .multipole import compute_dipole_moment
from .quadrupole_moment import compute_quadrupole_moment

__all__ = ["RHF", "UHF", "compute_dipole_moment", "compute_quadrupole_moment"]

test = PytestTester(__name__)
del PytestTester
