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

"""Unit tests for methods from rcc module and E2E tests for different CC
flavours."""

import pytest

from pybest import filemanager
from pybest.cc.rccd import RCCD
from pybest.cc.rccsd import RCCSD
from pybest.cc.rfpcc import RfpCCD, RfpCCSD
from pybest.cc.rlccd import RpCCDLCCD
from pybest.cc.rlccsd import RpCCDLCCSD
from pybest.exceptions import ArgumentError
from pybest.geminals.rpccd import RpCCD
from pybest.iodata import IOData
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel
from pybest.tests.common import load_reference_data

from .common import CCMolecule

#
#  Unit test
#


def test_read_input():
    """Check if arguments are properly interpreted by read_input method."""

    class DenseNIndexMockObject:
        """Mocks DenseNIndex instance."""

        def __init__(self, label):
            self.label = label
            self._array = None

    # Create input data
    one = DenseNIndexMockObject("one")
    eri = DenseNIndexMockObject("eri")
    orb = DenseNIndexMockObject("orb")
    iodata_ = IOData(eri=eri, orb_a=orb, e_ref="e_ref", x="x")
    # Make RCCD instance and read input
    lf = DenseLinalgFactory(2)
    # use lf to initialize OccModel
    occ_model = AufbauOccModel(lf, nel=2, ncore=0)
    solver = RCCD(lf, occ_model)
    out = solver.read_input(iodata_, orb, one=one)
    assert len(out) == 3
    assert solver.e_ref == "e_ref"
    assert not hasattr(solver, "x")
    assert isinstance(one, DenseNIndexMockObject)
    assert one.label == "one"
    assert isinstance(eri, DenseNIndexMockObject)
    assert eri.label == "eri"
    assert isinstance(orb, DenseNIndexMockObject)
    assert orb.label == "orb"


diis_parameters = [
    ({"diismax": 0, "diisstart": 0, "diisreset": False}, 0, 0, False),
    ({"diismax": 9, "diisstart": 0, "diisreset": True}, 9, 0, True),
    ({"diismax": 2, "diisstart": 0, "diisreset": False}, 2, 0, False),
    ({"diismax": 3, "diisstart": 10, "diisreset": True}, 3, 10, True),
]


@pytest.mark.parametrize("diis,diismax,diisstart,diisreset", diis_parameters)
def test_diis_setter_t(diis, diismax, diisstart, diisreset):
    """Check if DIIS (diis) is properly interpreted by read_input method."""

    class DenseNIndexMockObject:
        """Mocks DenseNIndex instance."""

        def __init__(self, label):
            self.label = label
            self._array = None

    # Create input data
    one = DenseNIndexMockObject("one")
    eri = DenseNIndexMockObject("eri")
    orb = DenseNIndexMockObject("orb")
    iodata_ = IOData(one=one, eri=eri, orb_a=orb, e_ref="e_ref", x="x")
    # Make RCCD instance and read input
    lf = DenseLinalgFactory(2)
    # use lf to initialize OccModel
    occ_model = AufbauOccModel(lf, nel=2, ncore=0)
    solver = RCCD(lf, occ_model)
    _ = solver.read_input(iodata_, diis=diis)
    assert solver.diis["diismax"] == diismax, "diismax not properly set"
    assert solver.diis["diisstart"] == diisstart, "diisstart not properly set"
    assert solver.diis["diisreset"] == diisreset, "diisreset not properly set"


@pytest.mark.parametrize("diis,diismax,diisstart,diisreset", diis_parameters)
def test_diis_setter_l(diis, diismax, diisstart, diisreset):
    """Check if DIIS (diis_l) is properly interpreted by read_input method."""

    class DenseNIndexMockObject:
        """Mocks DenseNIndex instance."""

        def __init__(self, label):
            self.label = label
            self._array = None

    # Create input data
    one = DenseNIndexMockObject("one")
    eri = DenseNIndexMockObject("eri")
    orb = DenseNIndexMockObject("orb")
    iodata_ = IOData(one=one, eri=eri, orb_a=orb, e_ref="e_ref", x="x")
    # Make RCCD instance and read input
    lf = DenseLinalgFactory(2)
    # use lf to initialize OccModel
    occ_model = AufbauOccModel(lf, nel=2, ncore=0)
    solver = RCCD(lf, occ_model)
    _ = solver.read_input(iodata_, diis_l=diis)
    assert solver.diis_l["diismax"] == diismax, "diismax not properly set"
    assert (
        solver.diis_l["diisstart"] == diisstart
    ), "diisstart not properly set"
    assert (
        solver.diis_l["diisreset"] == diisreset
    ), "diisreset not properly set"


def test_get_range():
    "Check if method returns expected output."
    lf = DenseLinalgFactory(3)
    occ_model = AufbauOccModel(lf, nel=2, ncore=0)
    solver = RCCD(lf, occ_model)
    block = solver.get_range("ovov")
    assert block["begin0"] == 0
    assert block["begin1"] == 1
    assert block["begin2"] == 0
    assert block["begin3"] == 1
    assert block["end0"] == 1
    assert block["end1"] == 3
    assert block["end2"] == 1
    assert block["end3"] == 3


def test_get_range_frozencore():
    "Check if method returns expected output if core is frozen (not active)."
    lf = DenseLinalgFactory(5)
    occ_model = AufbauOccModel(lf, nel=4, ncore=1)
    solver = RCCD(lf, occ_model)
    block = solver.get_range("ovov")
    assert block["begin0"] == 0
    assert block["begin1"] == 1
    assert block["begin2"] == 0
    assert block["begin3"] == 1
    assert block["end0"] == 1
    assert block["end1"] == 4
    assert block["end2"] == 1
    assert block["end3"] == 4


def test_set_seniority_0():
    "Check if seniority 0 amplitudes are set to 1 while all other remain 0."
    lf = DenseLinalgFactory(5)
    four_index = lf.create_four_index(2, 3, 2, 3)
    cc_solver = RCCD(lf, AufbauOccModel(lf, nel=4, ncore=0))
    four_index = cc_solver.set_seniority_0(four_index, value=1.0)
    assert four_index.get_element(0, 0, 0, 0) == 1
    assert four_index.get_element(0, 2, 0, 2) == 1
    assert four_index.get_element(1, 0, 1, 0) == 1
    assert four_index.get_element(0, 2, 0, 0) == 0
    assert four_index.get_element(0, 0, 1, 0) == 0
    assert four_index.get_element(1, 1, 0, 0) == 0
    assert four_index.get_element(0, 1, 1, 2) == 0


def test_set_seniority_2():
    "Check if seniority 2 amplitudes are set to 1 while all other remain 0."
    lf = DenseLinalgFactory(5)
    four_index = lf.create_four_index(2, 3, 2, 3)
    cc_solver = RCCD(lf, AufbauOccModel(lf, nel=4, ncore=0))
    four_index = cc_solver.set_seniority_2(four_index, value=1.0)
    assert four_index.get_element(0, 0, 0, 0) == 0
    assert four_index.get_element(0, 2, 0, 2) == 0
    assert four_index.get_element(1, 0, 1, 0) == 0
    assert four_index.get_element(0, 2, 0, 0) == 1
    assert four_index.get_element(1, 1, 1, 0) == 1
    assert four_index.get_element(1, 1, 0, 0) == 0
    assert four_index.get_element(0, 1, 1, 2) == 0


#
# E2E tests
#

# Define default reference wave function type for different CC methods
REF_WFN = {
    RCCD: "hf",
    RCCSD: "hf",
    RfpCCD: "pccd",
    RfpCCSD: "pccd",
    RpCCDLCCD: "pccd",
    RpCCDLCCSD: "pccd",
}

test_data_h2 = [("h2", "cc-pvdz")]
test_data_hf = [("hf", "3-21g")]
test_data_h2o = [("h2o", "3-21g")]

cls_set = [RCCD, RCCSD, RfpCCD, RfpCCSD, RpCCDLCCD, RpCCDLCCSD]


@pytest.mark.parametrize("cls", cls_set)
@pytest.mark.parametrize("mol_f,basis", test_data_h2)
def test_rcc_checkpoint(cls, mol_f, basis, linalg_slow, tmp_dir):
    """Do calculations and compare energy with reference."""
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()
    if cls not in (RCCD, RCCSD):
        mol_.do_pccd(RpCCD)

    cls_instance = cls(mol_.lf, mol_.occ_model)
    result = cls_instance(
        getattr(mol_, REF_WFN[cls]),
        *mol_.hamiltonian,
        filename=f"{tmp_dir}/dumped_rcc.h5",
        threshold_r=1e-8,
    )
    assert result.converged is True
    read_rcc = IOData.from_file(f"{tmp_dir}/dumped_rcc.h5")
    # check if containers contain same attributes (reference is output data)
    for attr1 in vars(result):
        assert hasattr(read_rcc, attr1), f"attribute {attr1} not found"
    # check if common attributes are contained
    expected = [
        "e_ref",
        "e_corr",
        "e_tot",
        "method",
        "nocc",
        "nvirt",
        "nact",
        "ncore",
        "occ_model",
        "converged",
        "orb_a",
        "olp",
    ]
    for attr1 in expected:
        assert hasattr(
            result, attr1
        ), f"attribute {attr1} not found in return value"
        assert hasattr(
            read_rcc, attr1
        ), f"attribute {attr1} not found in checkpoint"


combined_test_data = test_data_h2 + test_data_hf

# Mapping class names to corresponding reference energy keys
ref_key_map: dict[type, str] = {
    RCCD: "e_ref_ccd",
    RCCSD: "e_ref_ccsd",
    RfpCCD: "e_ref_fpccd",
    RfpCCSD: "e_ref_fpccsd",
    RpCCDLCCD: "e_ref_pccdlccd",
    RpCCDLCCSD: "e_ref_pccdlccsd",
}


@pytest.mark.parametrize("cls", [RCCD, RCCSD, RfpCCD, RfpCCSD])
@pytest.mark.parametrize("mol_f,basis", combined_test_data)
@pytest.mark.parametrize("t_solver", ["krylov", "pbqn", "mix"])
def test_rcc_energy(cls, mol_f, basis, linalg_slow, t_solver):
    """Do calculations and compare energy with reference."""
    ref_key = [ref_key_map[cls]]
    expected = load_reference_data(
        method="series",
        molecule_name=mol_f,
        basis=basis,
        charge=0,
        ncore=0,
        nroot=0,
        required_keys=ref_key,
    )
    # Prepare molecule
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()
    if cls not in (RCCD, RCCSD):
        mol_.do_pccd(RpCCD)

    cls_instance = cls(mol_.lf, mol_.occ_model)
    result = cls_instance(
        getattr(mol_, REF_WFN[cls]),
        *mol_.hamiltonian,
        solver=t_solver,
        threshold_r=1e-7,
    )
    assert isinstance(cls_instance.lf, linalg_slow)
    assert result.converged is True
    assert abs(result.e_corr - expected[ref_key[0]]) < 1e-7


@pytest.mark.parametrize("cls", [RCCD, RCCSD])
@pytest.mark.parametrize("mol_f,basis", test_data_h2o)
@pytest.mark.parametrize("ncore", [0, 1])
@pytest.mark.parametrize("t_solver", ["krylov", "pbqn", "mix"])
def test_rcc_energy_fc(cls, mol_f, basis, ncore, t_solver, linalg):
    """Do calculations and compare energy with reference."""
    ref_key = [ref_key_map[cls]]
    expected = load_reference_data(
        method="series",
        molecule_name=mol_f,
        basis=basis,
        charge=0,
        ncore=ncore,
        nroot=0,
        required_keys=ref_key,
    )
    # Prepare molecule
    mol_ = CCMolecule(mol_f, basis, linalg, charge=0, ncore=ncore)
    mol_.do_rhf()
    if cls not in (RCCD, RCCSD):
        mol_.do_pccd(RpCCD)

    cls_instance = cls(mol_.lf, mol_.occ_model)
    result = cls_instance(
        getattr(mol_, REF_WFN[cls]),
        *mol_.hamiltonian,
        solver=t_solver,
        threshold_r=1e-7,
    )
    assert isinstance(cls_instance.lf, linalg)
    assert result.converged is True
    assert abs(result.e_corr - expected[ref_key[0]]) < 1e-7


@pytest.mark.parametrize("cls", [RCCD, RCCSD, RfpCCD, RfpCCSD])
@pytest.mark.parametrize("mol_f,basis", test_data_hf)
def test_rcc_energy_hf_dump_cache(cls, mol_f, basis, linalg_slow):
    """Do calculations and compare energy with reference for dumping cache."""
    ref_key = [ref_key_map[cls]]
    expected = load_reference_data(
        method="series",
        molecule_name=mol_f,
        basis=basis,
        charge=0,
        ncore=0,
        nroot=0,
        required_keys=ref_key,
    )
    # Prepare molecule
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()
    if cls not in (RCCD, RCCSD):
        mol_.do_pccd(RpCCD)

    solver = cls(mol_.lf, mol_.occ_model)
    result = solver(
        getattr(mol_, REF_WFN[cls]),
        *mol_.hamiltonian,
        solver="pbqn",
        dump_cache=True,
        threshold_r=1e-7,
    )
    assert result.converged is True
    assert abs(result.e_corr - expected[ref_key[0]]) < 1e-7


@pytest.mark.parametrize("cls", [RpCCDLCCD, RpCCDLCCSD])
@pytest.mark.parametrize("mol_f,basis", test_data_hf)
@pytest.mark.parametrize("t_solver", ["krylov", "pbqn", "mix"])
def test_rcc_lambda_hf(linalg_slow, cls, mol_f, basis, t_solver):
    """Do calculations and compare energy with reference."""
    ref_key = [ref_key_map[cls]]
    expected = load_reference_data(
        method="series",
        molecule_name=mol_f,
        basis=basis,
        charge=0,
        ncore=0,
        nroot=0,
        required_keys=ref_key,
    )
    # Prepare molecule
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()
    mol_.do_pccd(RpCCD)

    solver = cls(mol_.lf, mol_.occ_model)
    result = solver(
        getattr(mol_, REF_WFN[cls]),
        *mol_.hamiltonian,
        solver=t_solver,
        threshold_r=1e-7,
        lambda_equations=True,
    )
    assert result.converged is True
    assert abs(result.e_corr - expected[ref_key[0]]) < 1e-7


@pytest.mark.parametrize("cls", [RCCD, RCCSD])
@pytest.mark.parametrize("mol_f,basis", test_data_h2)
def test_rcc_restart_h2(cls, mol_f, basis, linalg_slow):
    "Test passes if error does not occur while reading the checkpoint."
    # Prepare molecule
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()

    path = filemanager.temp_path(f"checkpoint_{cls.__name__}.h5")
    rcc = cls(mol_.lf, mol_.occ_model)
    out = rcc(
        mol_.hf,
        *mol_.hamiltonian,
    )
    out.to_file(path)
    out = rcc(mol_.hf, *mol_.hamiltonian, restart=path, maxiter=2)


@pytest.mark.parametrize("mol_f,basis", test_data_h2)
def test_rcc_rccsd_rccsd(mol_f, basis, linalg_slow):
    "Check if nothing necessary (e.g. ERI) is deleted by RCCsd."
    # Prepare molecule
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()
    rcc1 = RCCSD(mol_.lf, mol_.occ_model)
    rcc1(mol_.hf, *mol_.hamiltonian, initguess="mp2")
    rcc2 = RCCSD(mol_.lf, mol_.occ_model)
    rcc2(mol_.hf, *mol_.hamiltonian, initguess="mp2")


@pytest.mark.parametrize("cls", [RCCD, RfpCCD])
@pytest.mark.parametrize("mol_f,basis", test_data_h2)
def test_rcc_ccd_fpccd(cls, mol_f, basis, linalg_slow):
    "Check if RCCD cache is cleared."
    ref_key = [ref_key_map[cls]]
    expected = load_reference_data(
        method="series",
        molecule_name=mol_f,
        basis=basis,
        charge=0,
        ncore=0,
        nroot=0,
        required_keys=ref_key,
    )
    # Prepare molecule
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()
    if cls not in (RCCD, RCCSD):
        mol_.do_pccd(RpCCD)
    solver = cls(mol_.lf, mol_.occ_model)
    out = solver(
        getattr(mol_, REF_WFN[cls]),
        *mol_.hamiltonian,
        initguess="mp2",
        threshold_r=1e-7,
    )
    assert abs(out.e_corr - expected[ref_key[0]]) < 1e-7


@pytest.mark.parametrize("cls", [RCCD, RCCSD, RfpCCD, RfpCCSD])
@pytest.mark.parametrize("mol_f,basis", test_data_h2o)
@pytest.mark.parametrize("cache_item", ["exchange_oovv"])
def test_rcc_dump_cache(linalg_slow, cls, mol_f, basis, cache_item):
    """Test if items are properly dumped to disk."""
    # Prepare molecule
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()
    if cls not in (RCCD, RCCSD):
        mol_.do_pccd(RpCCD)

    solver = cls(mol_.lf, mol_.occ_model)
    # set some class attributes explicitly as they are set during function call
    one, two, orb = solver.read_input(mol_.one, mol_.two, mol_.hf)
    solver._dump_cache = True
    solver.set_hamiltonian(one, two, orb)

    # Check if cache has been dumped properly
    # We need to access _store directly, otherwise the load function of the
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
    amplitudes = {
        "t_1": solver.lf.create_two_index(nacto, nactv),
        "t_2": solver.denself.create_four_index(nacto, nactv, nacto, nactv),
    }
    # all elements should be loaded from the disk and dumped to the disk again
    solver.cc_residual_vector(amplitudes)
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


@pytest.mark.parametrize("cls", cls_set)
@pytest.mark.parametrize("mol_f,basis", test_data_hf)
@pytest.mark.parametrize(
    "mix_maxiter,maxiter,expected",
    [(1, 2, "krylov"), (1, 1, "pbqn"), (3, 1, "pbqn")],
)
def test_mix_solver(
    linalg_slow,
    mix_maxiter,
    maxiter,
    expected,
    cls,
    mol_f,
    basis,
):
    """Do calculations and check solver attribute."""
    # Prepare molecule
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()
    if cls not in (RCCD, RCCSD):
        mol_.do_pccd(RpCCD)

    linalg_factory = linalg_slow(mol_.lf.default_nbasis)
    solver = cls(linalg_factory, mol_.occ_model)
    solver(
        getattr(mol_, REF_WFN[cls]),
        *mol_.hamiltonian,
        solver="mix",
        maxiter=maxiter,
        mix_maxiter=mix_maxiter,
    )
    assert solver.solver == expected
