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
import pytest

from .common import Molecule


#
# Define fixtures for testing: water molecule from water.xyz file
#
@pytest.fixture
def water():
    # use auto_ncore feature by setting ncore=-1
    return Molecule("cc-pvdz", "test/water.xyz", ncore=-1)


#
# Define fixtures for testing: water molecule from water_2.xyz file
#
@pytest.fixture
def water_2():
    # use auto_ncore feature by setting ncore=-1
    return Molecule("cc-pvdz", "test/water_2.xyz", ncore=-1)


#
# Define fixtures for testing: H2 molecule
#
@pytest.fixture
def h2():
    mol = Molecule("6-31G")
    mol.do_hf()
    # Store energies in an instance attribute
    mol.energies = {
        "e_tot": -1.143420629378,
        "e_el": -1.143420629378 - mol.external,
        "e_tot_scf": -1.151686291339,
    }
    return mol
