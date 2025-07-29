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

from pybest.ci.tests.common import Molecule
from pybest.ci.xci import RCIS
from pybest.wrappers import RHF

# Reference energies
# HF orbitals
e_ex_cis_hf_ref = [
    0.00000000,
    0.33713109,
    0.40279938,
    0.42397873,
    0.48927984,
    0.56353471,
    0.68179610,
    0.85905279,
    0.89799226,
    0.97464748,
]

e_ex_cis_hf_ref_fc = [
    0.00000000,
    0.33713786,
    0.40280167,
    0.42398123,
    0.48930023,
    0.56354090,
    0.68179914,
    0.85905401,
    0.89800188,
    0.97467242,
]


parameters = [
    (10, 0, e_ex_cis_hf_ref, True),
    (10, 1, e_ex_cis_hf_ref_fc, True),
    (10, 0, e_ex_cis_hf_ref, False),
    (10, 1, e_ex_cis_hf_ref_fc, False),
]


@pytest.mark.parametrize("nroot,ncore,exp_result,csf", parameters)
def test_cis(nroot, ncore, exp_result, csf, linalg):
    mol = Molecule("water.xyz", "cc-pvdz", linalg, ncore)

    hf = RHF(mol.lf, mol.occ_model)
    hf_output = hf(mol.kin, mol.na, mol.er, mol.external, mol.olp, mol.orb_a)

    rcis = RCIS(mol.lf, mol.occ_model, csf=csf)
    rcis_output = rcis(mol.kin, mol.na, mol.er, hf_output, nroot=nroot)

    for i in range(nroot):
        assert abs(rcis_output.e_ci[i] - exp_result[i]) < 1e-6
