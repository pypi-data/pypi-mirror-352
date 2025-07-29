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

# 05/2025: This file has been written by Somayeh Ahmadkhani.

import pytest

from pybest.ee_eom.tests.common import FromFile
from pybest.ee_jacobian import JacobianpCCD
from pybest.geminals.rpccd import RpCCD
from pybest.tests.common import load_reference_data

test_set = [
    (
        "chplus",
        "cc-pvdz",
        {"charge": 0, "ncore": 0, "nroot": 15, "davidson": True},
    ),
    (
        "chplus",
        "cc-pvdz",
        {"charge": 0, "ncore": 0, "nroot": 15, "davidson": False},
    ),
    (
        "chplus",
        "cc-pvdz",
        {"charge": 0, "ncore": 1, "nroot": 6, "davidson": True},
    ),
    (
        "chplus",
        "cc-pvdz",
        {"charge": 0, "ncore": 1, "nroot": 6, "davidson": False},
    ),
]


@pytest.mark.parametrize("mol_f,basis,kwargs", test_set)
def test_jacobian_pccd(mol_f, basis, kwargs):
    ncore = kwargs.get("ncore")
    nroot = kwargs.get("nroot")
    charge = kwargs.get("charge")
    davidson = kwargs.get("Davidson")

    data = FromFile(
        mol_f,
        25,
        orb=f"test/{mol_f}_opt.dat",
        nocc=3,
        ncore=ncore,
    )

    expected = load_reference_data(
        method="series",
        molecule_name=mol_f,
        basis=basis,
        ncore=ncore,
        charge=charge,
        nroot=nroot,
    )

    # Solve pCCD equations:
    # pCCD
    geminal_solver = RpCCD(data.lf, data.occ_model)
    pccd = geminal_solver(data.one, data.two, data.hf)

    assert abs(pccd.e_tot - expected["e_ref_pccd"]) < 1e-6

    # Jacobian-pCCD
    jacobian = JacobianpCCD(data.lf, data.occ_model)
    jacobian_ = jacobian(data.one, data.two, pccd, nroot, davidson)

    for i, val in enumerate(jacobian_.e_ee):
        assert abs(val - expected["e_ex_pccd"][i]) < 1e-6
