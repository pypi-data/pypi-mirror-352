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

from pybest.context import context
from pybest.iodata import IOData
from pybest.utility.molecule import get_com

test_cases = [
    ("chplus", [0.0, 0.0, 0.0]),
    ("nh3", [0.0, 0.0, -0.3089891187736095]),
]


@pytest.mark.parametrize("mol, ref", test_cases)
def test_get_com(mol, ref):
    fn = context.get_fn(f"test/{mol}.xyz")
    mol = IOData.from_file(fn)
    com = get_com(mol)

    assert (abs(com - ref) < 1e-6).all()
