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
from pybest.ci.xci import RCISD
from pybest.wrappers import RHF

# Reference energies
# HF orbitals
e_ex_cisd_hf_ref_sd = [
    -0.204972411018,
    0.216276781554,
]

e_ex_cisd_hf_ref_fc_sd = [
    -0.202959092589,
    0.216578355116,
]

e_ex_cisd_hf_ref_csf = [-0.204972412326, 0.216276767787]

e_ex_cisd_hf_ref_fc_csf = [-0.202959093881, 0.216578340210]

parameters = [
    (2, 0, e_ex_cisd_hf_ref_sd, False),
    (2, 1, e_ex_cisd_hf_ref_fc_sd, False),
    (2, 0, e_ex_cisd_hf_ref_csf, True),
    (2, 1, e_ex_cisd_hf_ref_fc_csf, True),
]


@pytest.mark.parametrize("nroot,ncore,exp_result,csf", parameters)
def test_cisd(nroot, ncore, exp_result, csf, linalg):
    mol = Molecule("water.xyz", "cc-pvdz", linalg, ncore)

    hf = RHF(mol.lf, mol.occ_model)
    hf_output = hf(mol.kin, mol.na, mol.er, mol.external, mol.olp, mol.orb_a)

    rcisd = RCISD(mol.lf, mol.occ_model, csf=csf)
    rcisd_output = rcisd(
        mol.kin, mol.na, mol.er, hf_output, nroot=nroot, nguessv=20
    )

    for i in range(nroot):
        assert abs(rcisd_output.e_ci[i] - exp_result[i]) < 5e-6
