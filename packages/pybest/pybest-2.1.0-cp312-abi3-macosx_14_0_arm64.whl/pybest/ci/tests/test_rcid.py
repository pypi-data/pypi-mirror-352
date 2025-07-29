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
from pybest.ci.xci import RCID
from pybest.wrappers import RHF

# Reference energies
# HF orbitals
e_ex_cid_hf_ref_sd = [
    -0.204309304931,
    0.790622460353,
    0.823213746823,
]

e_ex_cid_hf_ref_fc_sd = [
    -0.202295755701,
    0.790675953422,
    0.823269146273,
]

e_ex_cid_hf_ref_csf = [
    -0.204309296306,
    0.865455465532,
    0.895714869177,
    0.912778958217,
]

e_ex_cid_hf_ref_fc_csf = [
    -0.202295746790,
    0.865561188865,
    0.895779541830,
    0.912822135358,
]

parameters = [
    (3, 0, e_ex_cid_hf_ref_sd, False),
    (3, 1, e_ex_cid_hf_ref_fc_sd, False),
    (4, 0, e_ex_cid_hf_ref_csf, True),
    (4, 1, e_ex_cid_hf_ref_fc_csf, True),
]


#
# We can test only for Dense (use linalg_slo fixture) as the CID code is
# also used in CISD
#


@pytest.mark.parametrize("nroot,ncore,exp_result,csf", parameters)
def test_cid(nroot, ncore, exp_result, csf, linalg_slow):
    mol = Molecule("water.xyz", "cc-pvdz", linalg_slow, ncore)

    hf = RHF(mol.lf, mol.occ_model)
    hf_output = hf(mol.kin, mol.na, mol.er, mol.external, mol.olp, mol.orb_a)

    rcid = RCID(mol.lf, mol.occ_model, csf=csf)
    rcid_output = rcid(mol.kin, mol.na, mol.er, hf_output, nroot=nroot)

    for i in range(nroot):
        assert abs(rcid_output.e_ci[i] - exp_result[i]) < 5e-6
