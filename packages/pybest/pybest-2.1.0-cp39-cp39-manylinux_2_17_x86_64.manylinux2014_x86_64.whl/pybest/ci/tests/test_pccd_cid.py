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

from pybest.ci.spin_free_pccdcid import RpCCDCID
from pybest.ci.tests.common import Molecule
from pybest.geminals.roopccd import ROOpCCD
from pybest.wrappers import RHF

# Reference energies
# HF orbitals
e_ex_cid_hf_ref_sd = [-6.114030e-07, 1.332907e00, 1.654977e00, 1.869596e00]


parameters = [
    (4, e_ex_cid_hf_ref_sd),
]


@pytest.mark.parametrize("nroot, exp_result", parameters)
def test_pccd_cid(nroot, exp_result, linalg):
    mol = Molecule("h2.xyz", "cc-pvdz", linalg)

    hf = RHF(mol.lf, mol.occ_model)
    hf_output = hf(mol.kin, mol.na, mol.er, mol.external, mol.olp, mol.orb_a)

    pccd_ = ROOpCCD(mol.lf, mol.occ_model)
    # NOTE: sorting of orbitals has to be enforced, otherwise test fails
    pccd = pccd_(mol.kin, mol.na, mol.er, hf_output, sort="force")

    pccdcid = RpCCDCID(mol.lf, mol.occ_model, pairs=False)
    pccdcid_output = pccdcid(
        mol.kin, mol.na, mol.er, pccd, nroot=nroot, scc=False
    )

    for i in range(nroot):
        assert abs(pccdcid_output.e_ci[i] - exp_result[i]) < 1e-6
