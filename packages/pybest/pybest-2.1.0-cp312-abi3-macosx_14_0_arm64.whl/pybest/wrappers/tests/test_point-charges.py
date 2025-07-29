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

"""Unit test for point-charges"""

import numpy as np
import pytest

from pybest.wrappers.hf import RHF
from pybest.wrappers.multipole import compute_dipole_moment
from pybest.wrappers.tests.common import Molecule

ref_hf_pc = [
    (  # HF-in-pc, (water_pc.xyz, water_pc.pc, cc-pvdz)
        "water_pc",
        {
            "dipole_hf_pc": [0.00000000, -3.7966923, 0.00000000],
            "pc": -55.396768822056,
            "total_hf": -73.999159293188,
        },
    ),
]


@pytest.mark.parametrize("structure,expected", ref_hf_pc)
def test_rhf_water_pc(structure, expected, linalg):
    """Test point charges at the HF level."""

    mol_ = Molecule(
        linalg,
        "cc-pvdz",
        f"test/{structure}.xyz",
        pc_fn=f"test/{structure}.pc",
    )
    mol_.do_scf(RHF)
    mol_.compute_dipole()
    dipole_check = np.array(compute_dipole_moment(mol_.dipole, mol_.scf))
    assert (
        abs(mol_.scf.e_tot - expected["total_hf"]) < 1e-6
    ), "wrong total SCF energy"
    assert (
        abs(dipole_check - expected["dipole_hf_pc"]) < 1e-3
    ).all(), "wrong dipole moment"
    assert (
        abs(mol_.scf.e_pc - expected["pc"]) < 1e-6
    ), "wrong point charge energy"
