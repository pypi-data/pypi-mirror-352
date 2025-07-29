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
# This file has been modified by Somayeh Ahmadkhani and Lena Szczuczko

import pytest

from pybest import filemanager
from pybest.cc import RLCCD, RLCCSD, RpCCDLCCD, RpCCDLCCSD
from pybest.exceptions import ArgumentError
from pybest.geminals.rpccd import RpCCD
from pybest.iodata import IOData
from pybest.tests.common import load_reference_data

from .common import CCMolecule

rhf_set = [
    (
        "nh3",
        "cc-pvdz",
        "krylov",
        "test/nh3_hf.txt",
    ),
]

pccd_set = [
    ("nh3", "cc-pvdz", "can", "test/nh3_hf.txt"),
    ("nh3", "cc-pvdz", "opt", "test/nh3_ap1rog.txt"),
]


pbqn_set = [
    (
        "pbqn/6/f/2",
        {
            "solver": "pbqn",
            "diis": {"diismax": 6, "diisreset": False},
            "jacobian": 2,
        },
    ),
    (
        "pbqn/6/f/1",
        {
            "solver": "pbqn",
            "diis": {"diismax": 6, "diisreset": False},
            "jacobian": 1,
        },
    ),
    (
        "pbqn/6/t/1",
        {
            "solver": "pbqn",
            "diis": {"diismax": 6, "diisreset": True},
            "jacobian": 1,
        },
    ),
    (
        "pbqn/6/t/2",
        {
            "solver": "pbqn",
            "diis": {"diismax": 6, "diisreset": True},
            "jacobian": 2,
        },
    ),
]

# test only one module, frozen core is assigned using the same code in all modules
frozen_core_set = [(RpCCDLCCSD, "nh3", "cc-pvdz", "test/nh3_ap1rog.txt")]

#
# the base code of LCCSD (on top of RHF) is also used in pCCD-LCC methods
# thus, we mark this test as slow
#


@pytest.mark.parametrize("cls", [RLCCD, RLCCSD])
@pytest.mark.parametrize("name,basis,solver,orb", rhf_set)
def test_rhflcc(cls, name, solver, orb, basis, linalg_slow):
    """Test if the LCCSD method with an RHF reference function works correctly."""
    mol_ = CCMolecule(name, basis, linalg_slow, charge=0, ncore=0)
    mol_.modify_orb(orb)

    required_keys = ["e_ref", "e_tot", "e_corr", "e_corr_d", "e_corr_s"]
    expected = load_reference_data(
        cls.__name__,
        name,
        basis,
        charge=0,
        ncore=0,
        nroot=0,
        required_keys=required_keys,
    )

    iodata = IOData(
        **{
            "orb_a": mol_.orb_a,
            "olp": mol_.olp,
            "e_core": mol_.external,
            "e_ref": expected["e_ref"],
        }
    )
    options = {"threshold_r": 1e-7, "solver": solver}
    lcc = cls(mol_.lf, mol_.occ_model)
    lcc_ = lcc(mol_.one, mol_.two, iodata, **options)
    assert abs(lcc_.e_tot - expected["e_tot"]) < 1e-6
    assert abs(lcc_.e_corr - expected["e_corr"]) < 1e-6
    assert abs(lcc_.e_corr_d - expected["e_corr_d"]) < 1e-6
    if expected["e_corr_s"] is not None:
        assert abs(lcc_.e_corr_s - expected["e_corr_s"]) < 1e-6


@pytest.mark.parametrize("cls", [RLCCD, RLCCSD])
@pytest.mark.parametrize("name,basis,solver,orb", rhf_set)
def test_rhflcc_restart(cls, name, basis, solver, orb, linalg_slow):
    """Test if the LCCSD method with an RHF reference function can be restarted
    from a checkpoint file."""
    mol_ = CCMolecule(name, basis, linalg_slow, charge=0, ncore=0)
    mol_.modify_orb(orb)

    required_keys = ["e_ref", "e_tot", "e_corr", "e_corr_d", "e_corr_s"]
    expected = load_reference_data(
        cls.__name__,
        name,
        basis,
        charge=0,
        ncore=0,
        nroot=0,
        required_keys=required_keys,
    )

    iodata = IOData(
        **{
            "orb_a": mol_.orb_a,
            "olp": mol_.olp,
            "e_core": mol_.external,
            "e_ref": expected["e_ref"],
        }
    )
    #
    # Converge not too tight
    #
    options = {"threshold_r": 1e-2, "solver": solver}
    lcc = cls(mol_.lf, mol_.occ_model)
    lcc_ = lcc(mol_.one, mol_.two, iodata, **options)
    #
    # Test restart
    #
    lcc = cls(mol_.lf, mol_.occ_model)
    lcc_ = lcc(
        mol_.one,
        mol_.two,
        iodata,
        initguess=f"{filemanager.result_dir}/checkpoint_{cls.__name__}.h5",
        threshold_r=1e-8,
        solver=solver,
    )

    assert abs(lcc_.e_tot - expected["e_tot"]) < 1e-6
    assert abs(lcc_.e_corr - expected["e_corr"]) < 1e-6
    assert abs(lcc_.e_corr_d - expected["e_corr_d"]) < 1e-6
    if expected["e_corr_s"] is not None:
        assert abs(lcc_.e_corr_s - expected["e_corr_s"]) < 1e-6


@pytest.mark.slow
@pytest.mark.parametrize(
    "dump_cache", [True, False], ids=["dump_cache on", "dump_cache off"]
)
@pytest.mark.parametrize("cls", [RpCCDLCCD, RpCCDLCCSD])
@pytest.mark.parametrize("name,basis,orb_type,orb", pccd_set)
def test_pccdlcc(dump_cache, cls, name, basis, orb_type, orb, linalg_slow):
    """Test if the LCCSD method with a pCCD reference function works correctly."""
    mol_ = CCMolecule(name, basis, linalg_slow, charge=0, ncore=0)
    mol_.modify_orb(orb)

    required_keys = ["e_tot_pccd", "e_tot", "e_corr", "e_corr_s", "e_corr_d"]
    expected = load_reference_data(
        cls.__name__,
        name,
        basis,
        charge=0,
        ncore=0,
        nroot=0,
        orb_type=orb_type,
        required_keys=required_keys,
    )

    # Do pCCD optimization:
    pccd = RpCCD(mol_.lf, mol_.occ_model)
    pccd_ = pccd(
        mol_.one, mol_.two, mol_.orb_a, mol_.olp, e_core=mol_.external
    )
    assert abs(pccd_.e_tot - expected["e_tot_pccd"]) < 1e-6

    lcc = cls(mol_.lf, mol_.occ_model)
    lcc_ = lcc(
        mol_.one, mol_.two, pccd_, threshold_r=1e-8, dump_cache=dump_cache
    )
    assert abs(lcc_.e_tot - expected["e_tot"]) < 1e-6
    assert abs(lcc_.e_corr - expected["e_corr"]) < 1e-6
    assert abs(lcc_.e_corr_d - expected["e_corr_d"]) < 1e-6
    if expected["e_corr_s"] is not None:
        assert abs(lcc_.e_corr_s - expected["e_corr_s"]) < 1e-6


@pytest.mark.slow
@pytest.mark.parametrize("cls", [RpCCDLCCD, RpCCDLCCSD])
@pytest.mark.parametrize("name,basis,orb_type,orb", pccd_set)
def test_pccdlcc_restart(cls, name, basis, orb_type, orb, linalg_slow):
    """Test if the LCCSD method with a pCCD reference function works correctly when restarting from a checkpoint file."""
    mol_ = CCMolecule(name, basis, linalg_slow, charge=0, ncore=0)
    mol_.modify_orb(orb)

    required_keys = ["e_tot_pccd", "e_tot", "e_corr", "e_corr_s", "e_corr_d"]
    expected = load_reference_data(
        cls.__name__,
        name,
        basis,
        charge=0,
        ncore=0,
        nroot=0,
        orb_type=orb_type,
        required_keys=required_keys,
    )

    # Do pCCD optimization:
    pccd = RpCCD(mol_.lf, mol_.occ_model)
    pccd_ = pccd(
        mol_.one, mol_.two, mol_.orb_a, mol_.olp, e_core=mol_.external
    )
    assert abs(pccd_.e_tot - expected["e_tot_pccd"]) < 1e-6
    #
    # Converge not too tight
    #
    lcc = cls(mol_.lf, mol_.occ_model)
    lcc_ = lcc(mol_.one, mol_.two, pccd_, threshold_r=1e-2)
    #
    # Test restart
    #
    lcc = cls(mol_.lf, mol_.occ_model)
    lcc_ = lcc(
        mol_.one,
        mol_.two,
        pccd_,
        initguess=f"{filemanager.result_dir}/checkpoint_{cls.__name__}.h5",
        threshold_r=1e-8,
    )
    assert abs(lcc_.e_tot - expected["e_tot"]) < 1e-6
    assert abs(lcc_.e_corr - expected["e_corr"]) < 1e-6
    assert abs(lcc_.e_corr_d - expected["e_corr_d"]) < 1e-6
    if expected["e_corr_s"] is not None:
        assert abs(lcc_.e_corr_s - expected["e_corr_s"]) < 1e-6


@pytest.mark.slow
@pytest.mark.parametrize("solver, solver_dict", pbqn_set)
@pytest.mark.parametrize("cls", [RpCCDLCCD, RpCCDLCCSD])
@pytest.mark.parametrize("name,basis,orb_type,orb", pccd_set)
def test_pccdlcc_solver(
    solver, solver_dict, cls, name, basis, orb_type, orb, linalg_slow
):
    """Test if the LCCSD method with a pCCD reference works correctly when using the chosen solver."""
    mol_ = CCMolecule(name, basis, linalg_slow, charge=0, ncore=0)
    mol_.modify_orb(orb)
    # Do pCCD optimization:
    pccd = RpCCD(mol_.lf, mol_.occ_model)
    pccd_ = pccd(
        mol_.one, mol_.two, mol_.orb_a, mol_.olp, e_core=mol_.external
    )

    required_keys = ["e_tot_pccd", "e_tot", "e_corr", "e_corr_s", "e_corr_d"]
    expected = load_reference_data(
        cls.__name__,
        name,
        basis,
        charge=0,
        ncore=0,
        nroot=0,
        orb_type=orb_type,
        required_keys=required_keys,
    )

    assert abs(pccd_.e_tot - expected["e_tot_pccd"]) < 1e-6

    lcc = cls(mol_.lf, mol_.occ_model)
    lcc_ = lcc(mol_.one, mol_.two, pccd_, threshold_r=1e-8, **solver_dict)
    assert abs(lcc_.e_tot - expected["e_tot"]) < 1e-6
    assert abs(lcc_.e_corr - expected["e_corr"]) < 1e-6
    assert abs(lcc_.e_corr_d - expected["e_corr_d"]) < 1e-6
    if expected["e_corr_s"] is not None:
        assert abs(lcc_.e_corr_s - expected["e_corr_s"]) < 1e-6


@pytest.mark.slow
@pytest.mark.parametrize("solver", ["pbqn", "krylov"])
@pytest.mark.parametrize("e_core", [0, 10])
@pytest.mark.parametrize("cls,name,basis,orb", frozen_core_set)
@pytest.mark.parametrize("ncore", [0, 1])
def test_pccdlcc_frozen_core(
    solver, e_core, cls, name, basis, orb, ncore, linalg_slow
):
    """Test if the LCCSD method with a pCCD reference function works correctly when using frozen core orbitals."""
    mol_ = CCMolecule(name, basis, linalg_slow, charge=0, ncore=ncore)
    mol_.modify_orb(orb)
    # Do pCCD optimization:
    pccd = RpCCD(mol_.lf, mol_.occ_model)
    pccd_ = pccd(
        mol_.one,
        mol_.two,
        mol_.orb_a,
        mol_.olp,
        e_core=(mol_.external + e_core),
    )

    required_keys = ["e_tot_pccd", "e_tot", "e_corr", "e_corr_s", "e_corr_d"]
    expected = load_reference_data(
        cls.__name__,
        name,
        basis,
        charge=0,
        ncore=ncore,
        nroot=0,
        required_keys=required_keys,
    )

    # Overwrite core energy and thus total energy
    # Can only be done in pCCD, affects only total energy
    assert abs(pccd_.e_tot - expected["e_tot_pccd"] - e_core) < 1e-6

    # Do LCC calculations with scipy.root 'krylov' solver
    lcc = cls(mol_.lf, mol_.occ_model)
    lcc_ = lcc(mol_.one, mol_.two, pccd_, threshold_r=1e-7, solver=solver)
    assert abs(lcc_.e_tot - expected["e_tot"] - e_core) < 1e-6
    assert abs(lcc_.e_corr - expected["e_corr"]) < 1e-6
    assert abs(lcc_.e_corr_d - expected["e_corr_d"]) < 1e-6
    if expected["e_corr_s"] is not None:
        assert abs(lcc_.e_corr_s - expected["e_corr_s"]) < 1e-6


test_data = [("h2o", "3-21g")]


@pytest.mark.parametrize("cls", [RpCCDLCCD, RpCCDLCCSD])
@pytest.mark.parametrize("name, basis", test_data)
@pytest.mark.parametrize("cache_item", ["govvo"])
def test_rcc_dump_cache(cls, linalg_slow, cache_item, name, basis):
    """Test if items are properly dumped to disk."""
    mol_ = CCMolecule(name, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()
    mol_.do_pccd(RpCCD)
    solver = cls(mol_.lf, mol_.occ_model)
    # set some class attributes explicitly as they are set during function call
    one, two, orb = solver.read_input(mol_.one, mol_.two, mol_.pccd)
    solver._dump_cache = True
    solver.set_hamiltonian(one, two, orb)

    # Check if cache has been dumped properly
    # We need to access _store directly otherwise the load function of the
    # Cache class is called and test will fail by construction
    #
    # 1) Check set_hamiltonian
    try:
        assert not hasattr(solver.cache._store[cache_item]._value, "_array"), (
            f"Cache element {cache_item} not properly dumped to disk in "
            "set_hamiltonian"
        )
    except KeyError:
        pass
    # 2) Check cc_residual_vector
    nacto = solver.occ_model.nacto[0]
    nactv = solver.occ_model.nactv[0]
    unknowns = int(nacto * nactv * (nacto * nactv + 1) / 2)
    if solver.acronym == "RpCCDLCCSD":
        unknowns += nacto * nactv
    amplitudes = solver.lf.create_one_index(unknowns)
    # all elements should be loaded from the disk and dumped to the disk again
    solver.vfunction(amplitudes)
    try:
        with pytest.raises(ArgumentError):
            assert not hasattr(
                solver.cache._store[cache_item].value, "_array"
            ), (
                f"Cache element {cache_item} not properly dumped to disk in "
                "build_subspace_hamiltonian"
            )
    except KeyError:
        pass


#
# Cholesky tests
#


@pytest.mark.parametrize("cls,name,basis,orb", frozen_core_set)
@pytest.mark.parametrize("ncore", [0, 1])
def test_pccdlcc_frozen_core_cholesky(cls, name, basis, orb, ncore, linalg):
    """Test if the LCCSD method with a pCCD reference works correctly using Cholesky with the frozen core orbitals."""
    mol_ = CCMolecule(name, basis, linalg, charge=0, ncore=ncore)
    mol_.modify_orb(orb)

    required_keys = ["e_tot_pccd", "e_tot", "e_corr", "e_corr_s", "e_corr_d"]
    expected = load_reference_data(
        cls.__name__,
        name,
        basis,
        charge=0,
        ncore=ncore,
        nroot=0,
        required_keys=required_keys,
    )

    # Do pCCD optimization:
    pccd = RpCCD(mol_.lf, mol_.occ_model)
    # Overwrite core energy and thus total energy
    # Can only be done in pCCD, affects only total energy
    pccd_ = pccd(
        mol_.one, mol_.two, mol_.orb_a, mol_.olp, e_core=mol_.external
    )
    assert abs(pccd_.e_tot - expected["e_tot_pccd"]) < 1e-6

    # Do LCC calculations with PyBEST's Quasi-Newton solver
    lcc = cls(mol_.lf, mol_.occ_model)
    lcc_ = lcc(mol_.one, mol_.two, pccd_, threshold_r=1e-5, solver="pbqn")
    assert abs(lcc_.e_tot - expected["e_tot"]) < 1e-6
    assert abs(lcc_.e_corr - expected["e_corr"]) < 1e-6
    assert abs(lcc_.e_corr_d - expected["e_corr_d"]) < 1e-6
    if expected["e_corr_s"] is not None:
        assert abs(lcc_.e_corr_s - expected["e_corr_s"]) < 1e-6
