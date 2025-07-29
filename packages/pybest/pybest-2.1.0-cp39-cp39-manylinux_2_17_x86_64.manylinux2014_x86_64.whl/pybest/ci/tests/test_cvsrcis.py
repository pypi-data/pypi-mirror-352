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

# Detailed changelog:
#
# 2025-01-26: created by Iulia Emilia Brumboiu


import pytest

from pybest.ci.tests.common import Molecule
from pybest.ci.xci import RCIS
from pybest.wrappers import RHF

# Reference energies
o1s_cvs_cis_ref = [
    0.00000000,
    19.90795144,
    19.94588167,
    20.24953231,
    20.27761288,
    20.31830625,
    20.34924987,
    20.47305010,
    20.49421717,
    20.51279614,
    20.51852807,
]

n1s_cvs_cis_ref = [
    0.00000000,
    15.30521078,
    15.31926402,
    15.32688307,
    15.34339637,
    15.38229483,
    15.38288074,
    15.40646148,
    15.40726275,
    15.40761586,
    15.41828733,
]

c1s_cvs_cis_ref = [
    0.00000000,
    10.77512742,
    10.79190845,
    10.85777700,
    10.90766980,
    11.05069625,
    11.05767999,
    11.08650279,
    11.10200658,
    11.15033093,
    11.15308933,
]

parameters = [
    (10, 0, 2, o1s_cvs_cis_ref, True),
    (10, 0, 2, o1s_cvs_cis_ref, False),
    (10, 2, 2, n1s_cvs_cis_ref, True),
    (10, 2, 2, n1s_cvs_cis_ref, False),
    (10, 4, 4, c1s_cvs_cis_ref, True),
    (10, 4, 4, c1s_cvs_cis_ref, False),
]


@pytest.mark.parametrize("nroot, ncore, nactc, exp_result, csf", parameters)
def test_cvs_cis(nroot, ncore, nactc, exp_result, csf, linalg_slow):
    mol = Molecule("uracil.xyz", "sto-3g", linalg_slow, ncore, nactc)

    hf = RHF(mol.lf, mol.occ_model)
    hf_output = hf(mol.kin, mol.na, mol.er, mol.external, mol.olp, mol.orb_a)

    rcis = RCIS(mol.lf, mol.occ_model, csf=csf, cvs=True)
    rcis_output = rcis(mol.kin, mol.na, mol.er, hf_output, nroot=nroot)

    for i in range(nroot):
        assert abs(rcis_output.e_ci[i] - exp_result[i]) < 1e-6
