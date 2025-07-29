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

"""Unit test for embeding potential"""

import numpy as np
import pytest

from pybest.wrappers.hf import RHF
from pybest.wrappers.multipole import compute_dipole_moment
from pybest.wrappers.tests.common import Molecule

ref_hf_emb = [
    (  # HF-in-DFT, (water_emb.xyz, water_emb.emb, sto-6g)
        "water_emb",
        {
            "dipole_hf_emb": [0.00000000, 0.00000000, 1.7536684],
            "emb": 0.007567109615,
            "total_hf": -75.668798794987,
        },
    ),
]


@pytest.mark.parametrize("structure,expected", ref_hf_emb)
def test_rhf_water_emb(structure, expected, linalg):
    """Test embedding potential at the HF level."""

    mol_ = Molecule(
        linalg,
        "sto-6g",
        f"test/{structure}.xyz",
        emb_fn=f"test/{structure}.emb",
    )
    mol_.do_scf(RHF)
    mol_.compute_dipole()
    dipole_check = np.array(compute_dipole_moment(mol_.dipole, mol_.scf))
    assert (
        abs(mol_.scf.e_tot - expected["total_hf"]) < 1e-6
    ), "wrong total SCF energy"
    assert (
        abs(dipole_check - expected["dipole_hf_emb"]) < 1e-3
    ).all(), "wrong dipole moment"
    assert (
        abs(mol_.scf.e_emb - expected["emb"]) < 1e-6
    ), "wrong embedding energy"
