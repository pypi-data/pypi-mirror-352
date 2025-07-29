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


import numpy as np
import pytest

from pybest import filemanager
from pybest.exceptions import ArgumentError
from pybest.geminals.roopccd import ROOpCCD
from pybest.geminals.rpccd import RpCCD
from pybest.iodata import IOData
from pybest.utility import project_orbitals

from .common import Molecule


def test_pccd_cs(h2):
    # Do pCCD optimization:
    h2.do_pccd()
    assert abs(h2.pccd.e_tot - h2.energies["e_tot"]) < 1e-6


# multiplication factor for external attribute
testdata_external = [0.0, 1.0, 2.0]


@pytest.mark.parametrize("external", testdata_external)
def test_pccd_sp_args_external(h2, external):
    # Take only external energy from kwargs
    h2.do_pccd(e_core=external * h2.external)
    expected = h2.energies["e_el"] + external * h2.external
    assert abs(h2.pccd.e_tot - expected) < 1e-6


testdata_orbs = [
    ("orb_a", None),
    (None, "orb_a"),
    ("orb_a.copy()", "orb_a"),
    ("orb_a", "orb_a.copy()"),  # FloatingPointError, ValueError
    ("orb_a.copy()", None),  # FloatingPointError, ValueError
    (None, None),  # AttributeError
]


@pytest.mark.parametrize("orbs1,orbs2", testdata_orbs)
def test_pccd_sp_args_orbs(h2, orbs1, orbs2):
    # remove from IOData to test explicit passing
    h2.rhf.orb_a = None
    # Assign orb_a as args
    orbs1 = eval(f"h2.{orbs1}") if orbs1 is not None else orbs1
    # Assign orb_a as kwargs
    orbs2 = eval(f"h2.{orbs2}") if orbs2 is not None else orbs2
    try:
        h2.do_pccd(orbs1, orb_a=orbs2)
        assert abs(h2.pccd.e_tot - h2.energies["e_tot"]) < 1e-6
    except (AttributeError, FloatingPointError, ValueError):
        pass


def test_pccd_cs_scf(h2):
    # Do pCCD optimization:
    h2.do_oopccd(checkpoint=-1)
    assert abs(h2.oopccd.e_tot - h2.energies["e_tot_scf"]) < 1e-6


def test_pccd_cs_scf_restart(h2):
    # Redo the pCCD optimization to get checkpoints
    h2.do_oopccd()

    # Just check wether we have the proper results
    assert abs(h2.oopccd.e_tot - h2.energies["e_tot_scf"]) < 1e-6

    old = IOData.from_file(f"{filemanager.result_dir}/checkpoint_pccd.h5")

    assert hasattr(old, "olp")
    assert hasattr(old, "orb_a")
    assert hasattr(old, "e_tot")
    assert hasattr(old, "e_ref")
    assert hasattr(old, "e_core")
    assert hasattr(old, "e_corr")
    assert hasattr(old, "dm_1")
    assert hasattr(old, "dm_2")

    # Update to slightly stretch geometry of H2
    h2_stretched = Molecule("6-31G", "test/h2_2.xyz")
    h2_stretched.do_hf()

    # re-orthogonalize orbitals
    project_orbitals(old.olp, h2_stretched.olp, old.orb_a, h2_stretched.orb_a)

    # recompute
    h2_stretched.do_oopccd(checkpoint_fn="checkpoint_restart.h5")

    assert abs(h2_stretched.oopccd.e_tot - -1.150027881389) < 1e-6

    # recompute
    h2_stretched.do_oopccd(
        restart=f"{filemanager.result_dir}/checkpoint_restart.h5"
    )

    assert abs(h2_stretched.oopccd.e_tot - -1.150027881389) < 1e-6

    # recompute using only restart file
    h2_stretched.do_oopccd_restart(
        restart=f"{filemanager.result_dir}/checkpoint_restart.h5"
    )

    assert abs(h2_stretched.oopccd.e_tot - -1.150027881389) < 1e-6

    e_corr = h2_stretched.oopccd.e_corr
    e_core = h2_stretched.oopccd.e_core
    e_ref = h2_stretched.oopccd.e_ref

    # recompute with wrong core energy
    h2_stretched.do_oopccd(
        restart=f"{filemanager.result_dir}/checkpoint_restart.h5",
        e_core=10.000,
    )

    with pytest.raises(AssertionError):
        assert abs(h2_stretched.oopccd.e_tot - -1.150027881389) < 1e-6
    assert abs(e_corr - h2_stretched.oopccd.e_corr) < 1e-6
    assert (
        abs(
            e_ref
            - e_core
            - h2_stretched.oopccd.e_ref
            + h2_stretched.oopccd.e_core
        )
        < 1e-6
    )


test_core = [
    (RpCCD, "water", "cc-pvdz", 0, {}, {"e_tot": -76.07225799852085}),
    (RpCCD, "water", "cc-pvdz", 1, {}, {"e_tot": -76.07210055926937}),
    (
        ROOpCCD,
        "water",
        "cc-pvdz",
        1,
        {"sort": False},
        {"e_tot": -76.0994990025405},
    ),
]


@pytest.mark.parametrize("cls,mol,basis,ncore,kwargs,result", test_core)
def test_pccd_core(cls, mol, basis, ncore, kwargs, result):
    # create molecule
    mol_ = Molecule(basis, f"test/{mol}.xyz", ncore=ncore)
    # do RHF
    mol_.do_hf()
    # do pccd
    if cls.__name__ == RpCCD.__name__:
        mol_.do_pccd(**kwargs)
        assert abs(mol_.pccd.e_tot - result["e_tot"]) < 1e-6
    elif cls.__name__ == ROOpCCD.__name__:
        mol_.do_oopccd(**kwargs)
        assert abs(mol_.oopccd.e_tot - result["e_tot"]) < 1e-6
    else:
        raise ArgumentError(f"Do not know how to handle {cls}")


test_stepsearch = [
    (
        ROOpCCD,
        "water",
        "cc-pvdz",
        "trust-region",
        {
            "stepsearch": {"method": "trust-region"},
            "thresh": {
                "energy": 5e-7,
                "gradientmax": 5e-3,
                "gradientnorm": 5e-3,
            },
            "sort": False,
        },
        {"e_tot": -76.099785827958},
    ),
    (
        ROOpCCD,
        "water",
        "cc-pvdz",
        "backtracking",
        {
            "stepsearch": {"method": "backtracking"},
            "thresh": {
                "energy": 5e-7,
                "gradientmax": 5e-3,
                "gradientnorm": 5e-3,
            },
            "sort": False,
        },
        {"e_tot": -76.099785827958},
    ),
    (
        ROOpCCD,
        "water",
        "cc-pvdz",
        "None",
        {
            "stepsearch": {"method": "None"},
            "thresh": {
                "energy": 5e-7,
                "gradientmax": 5e-3,
                "gradientnorm": 5e-3,
            },
            "sort": False,
        },
        {"e_tot": -76.099785827958},
    ),
]


@pytest.mark.parametrize(
    "cls, mol, basis, stepsearch, kwargs, result", test_stepsearch
)
def test_pccd_stepsearch(cls, mol, basis, stepsearch, kwargs, result):
    # create molecule
    mol_ = Molecule(basis, f"test/{mol}.xyz")
    # do RHF
    mol_.do_hf()
    # do pccd
    if cls.__name__ == RpCCD.__name__:
        mol_.do_pccd(**kwargs)
        assert abs(mol_.pccd.e_tot - result["e_tot"]) < 1e-6
    elif cls.__name__ == ROOpCCD.__name__:
        mol_.do_oopccd(**kwargs)
        assert abs(mol_.oopccd.e_tot - result["e_tot"]) < 1e-6
    else:
        raise ArgumentError(f"Do not know how to handle {cls}")


test_orb_copy = [
    (
        "water",
        "cc-pvdz",
    ),
]


test_pccd = [
    (RpCCD, {}),
    (ROOpCCD, {"sort": False, "maxiter": {"orbiter": 2}}),
]


@pytest.mark.parametrize("mol,basis", test_orb_copy)
@pytest.mark.parametrize("cls,kwargs", test_pccd)
def test_pccd_orbs(mol, basis, cls, kwargs):
    # create molecule
    mol_ = Molecule(basis, f"test/{mol}.xyz")
    # do RHF
    mol_.do_hf()
    # do pccd
    if cls.__name__ == RpCCD.__name__:
        mol_.do_pccd(**kwargs)
        # orbital instance should differ (occupation numbers, energies)
        assert not (mol_.rhf.orb_a == mol_.pccd.orb_a)
        # MO coefficients should be the same
        assert np.allclose(mol_.rhf.orb_a.coeffs, mol_.pccd.orb_a.coeffs)
        assert not np.allclose(
            mol_.rhf.orb_a.occupations, mol_.pccd.orb_a.occupations
        )
    elif cls.__name__ == ROOpCCD.__name__:
        mol_.do_oopccd(**kwargs)
        assert not (mol_.rhf.orb_a == mol_.oopccd.orb_a)
    else:
        raise ArgumentError(f"Do not know how to handle {cls}")
