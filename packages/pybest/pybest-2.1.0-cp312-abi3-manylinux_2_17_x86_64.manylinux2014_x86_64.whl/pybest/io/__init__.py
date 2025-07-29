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
"""Input and output routines

All input routines begin with ``load_``. All output routines begin with
``dump_``.
"""

# define test runner
from pybest._pytesttester import PytestTester
from pybest.io.coordinate import (
    check_physical_ham_coordinates,
    check_supported_atoms,
)
from pybest.io.cube import dump_cube
from pybest.io.embedding import load_embedding
from pybest.io.external_charges import load_charges
from pybest.io.internal import dump_h5, load_h5
from pybest.io.lockedh5 import LockedH5File
from pybest.io.molden import dump_molden, load_molden
from pybest.io.molekel import load_mkl
from pybest.io.molpro import dump_fcidump, load_fcidump
from pybest.io.xyz import dump_xyz, load_xyz, load_xyz_plain

__all__ = [
    "LockedH5File",
    "check_physical_ham_coordinates",
    "check_supported_atoms",
    "dump_cube",
    "dump_fcidump",
    "dump_h5",
    "dump_molden",
    "dump_xyz",
    "load_charges",
    "load_embedding",
    "load_fcidump",
    "load_h5",
    "load_mkl",
    "load_molden",
    "load_xyz",
    "load_xyz_plain",
]

test = PytestTester(__name__)
del PytestTester
