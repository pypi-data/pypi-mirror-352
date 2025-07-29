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

from pybest import context
from pybest.iodata import IOData
from pybest.units import angstrom


def check_water(mol):
    assert mol.title == "Water"
    assert mol.atom[0] == "H"
    assert mol.atom[1] == "O"
    assert mol.atom[2] == "H"
    assert (
        abs(
            np.linalg.norm(mol.coordinates[0] - mol.coordinates[1]) / angstrom
            - 0.96
        )
        < 1e-5
    )
    assert (
        abs(
            np.linalg.norm(mol.coordinates[2] - mol.coordinates[1]) / angstrom
            - 0.96
        )
        < 1e-5
    )


def test_load_water_element():
    fn = context.get_fn("test/water_element.xyz")
    mol = IOData.from_file(fn)
    check_water(mol)
