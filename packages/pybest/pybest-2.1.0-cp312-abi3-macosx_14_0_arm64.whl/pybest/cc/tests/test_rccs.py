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
# 03/2025:
# This file has been modified by Somayeh Ahmadkhani and Lena Szczuczk

import pytest

from pybest.cc import RCCS, RpCCDCCS
from pybest.geminals.rpccd import RpCCD
from pybest.iodata import IOData
from pybest.tests.common import load_reference_data

from .common import CCMolecule

core_set_hf = [(RCCS, "hf", "cc-pvdz", "test/hf_ap1rog.txt")]
core_set_pccd = [(RpCCDCCS, "hf", "cc-pvdz", "test/hf_ap1rog.txt")]


solver_set = [
    ("krylov", {}),
    ("pbqn", {"jacobian": 1}),
    ("pbqn", {"jacobian": 2}),
]


@pytest.mark.parametrize("ncore", [0, 1])
@pytest.mark.parametrize("cls,name,basis,orb", core_set_hf)
@pytest.mark.parametrize("solver, jacobian", solver_set)
def test_ccs(ncore, cls, name, basis, orb, solver, jacobian, linalg_slow):
    mol_ = CCMolecule(name, basis, linalg_slow, charge=0, ncore=ncore)
    mol_.modify_orb(orb)

    required_keys = ["e_ref", "e_tot"]
    expected = load_reference_data(
        cls.__name__,
        name,
        basis,
        charge=0,
        ncore=ncore,
        nroot=0,
        required_keys=required_keys,
    )

    iodata = IOData(
        **{
            "orb_a": mol_.orb_a,
            "olp": mol_.olp,
            "e_ref": expected["e_ref"],
            "e_core": mol_.external,
        }
    )
    options = {"solver": solver, "threshold_r": 1e-7}
    ccs = cls(mol_.lf, mol_.occ_model)
    ccs_ = ccs(mol_.one, mol_.two, iodata, **options, **jacobian)
    assert abs(ccs_.e_tot - expected["e_tot"]) < 1e-6


@pytest.mark.parametrize("ncore", [0, 1])
@pytest.mark.parametrize("cls,name,basis,orb", core_set_pccd)
@pytest.mark.parametrize("solver,jacobian", solver_set)
def test_pccd_ccs(ncore, cls, name, basis, orb, solver, jacobian, linalg_slow):
    mol_ = CCMolecule(name, basis, linalg_slow, charge=0, ncore=ncore)
    mol_.modify_orb(orb)

    required_keys = ["e_ref", "e_tot"]
    expected = load_reference_data(
        cls.__name__,
        name,
        basis,
        charge=0,
        ncore=ncore,
        nroot=0,
        required_keys=required_keys,
    )

    mol_.do_pccd(RpCCD, False)
    pccd_ = mol_.pccd
    assert abs(pccd_.e_tot - expected["e_ref"]) < 1e-6

    options = {"solver": solver, "threshold_r": 1e-7}

    ccs = cls(mol_.lf, mol_.occ_model)
    ccs_ = ccs(mol_.one, mol_.two, pccd_, **options, **jacobian)

    assert abs(ccs_.e_tot - expected["e_tot"]) < 1e-6


@pytest.mark.parametrize("ncore", [0, 1])
@pytest.mark.parametrize("cls,name,basis,orb", core_set_hf)
def test_rccs_compute_t1_diagnostic(ncore, cls, name, basis, orb, linalg_slow):
    """Compares T1 diagnostic with reference data."""
    mol_ = CCMolecule(name, basis, linalg_slow, charge=0, ncore=ncore)
    mol_.modify_orb(orb)

    required_keys = ["e_ref", "e_tot", "t1_diagnostic"]
    expected = load_reference_data(
        cls.__name__,
        name,
        basis,
        charge=0,
        ncore=ncore,
        nroot=0,
        required_keys=required_keys,
    )
    iodata = IOData(
        **{
            "orb_a": mol_.orb_a,
            "olp": mol_.olp,
            "e_ref": expected["e_ref"],
            "e_core": mol_.external,
        }
    )
    ccs = cls(mol_.lf, mol_.occ_model)
    ccs_ = ccs(mol_.one, mol_.two, iodata, threshold_r=1e-8)
    assert abs(ccs_.e_tot - expected["e_tot"]) < 1e-6

    t1_diag = ccs.compute_t1_diagnostic(ccs_.t_1, ccs.occ_model.nacto[0])
    assert abs(t1_diag - expected["t1_diagnostic"]) < 1e-8
