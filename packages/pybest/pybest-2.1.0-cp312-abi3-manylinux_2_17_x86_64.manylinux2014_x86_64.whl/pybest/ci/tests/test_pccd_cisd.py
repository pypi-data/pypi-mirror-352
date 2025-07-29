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

from pybest.ci.spin_free_pccdcisd import RpCCDCISD
from pybest.ci.tests.common import Molecule
from pybest.geminals.roopccd import ROOpCCD
from pybest.wrappers import RHF

# Reference energies
# HF orbitals
e_ex_cisd_hf_ref_sd = [
    -6.149755e-07,
    5.109901e-01,
    8.039584e-01,
    1.137945e00,
]


parameters = [
    (4, e_ex_cisd_hf_ref_sd),
]


@pytest.mark.parametrize("nroot, exp_result", parameters)
def test_pccd_cid(nroot, exp_result, linalg):
    mol = Molecule("h2.xyz", "cc-pvdz", linalg)

    hf = RHF(mol.lf, mol.occ_model)
    hf_output = hf(mol.kin, mol.na, mol.er, mol.external, mol.olp, mol.orb_a)

    pccd_ = ROOpCCD(mol.lf, mol.occ_model)
    pccd = pccd_(mol.kin, mol.na, mol.er, hf_output)

    pccdcisd = RpCCDCISD(mol.lf, mol.occ_model, pairs=False)
    pccdcisd_output = pccdcisd(
        mol.kin, mol.na, mol.er, pccd, nroot=nroot, scc=False
    )

    for i in range(nroot):
        assert abs(pccdcisd_output.e_ci[i] - exp_result[i]) < 1e-6
