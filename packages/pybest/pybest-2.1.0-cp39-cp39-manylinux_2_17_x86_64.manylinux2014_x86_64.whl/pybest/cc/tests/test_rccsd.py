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

"""Unit tests for RCCSD method from rccsd module."""

import copy

import numpy as np
import pytest

from pybest import filemanager
from pybest.cache import Cache
from pybest.cc.rccd import RCCD
from pybest.cc.rccsd import RCCSD
from pybest.exceptions import ArgumentError
from pybest.iodata import IOData
from pybest.linalg import DenseFourIndex, DenseTwoIndex

from .common import CCMolecule, check_eri_in_cache, check_fock_in_cache

#
#  Unit test
#

testdata_rccd = [(RCCD, "h2", "cc-pvdz", {"ncore": 0, "charge": 0})]

testdata_iodata = [
    (RCCD, "h2", "cc-pvdz", {"ncore": 0, "charge": 0}),
    (RCCSD, "h2", "cc-pvdz", {"ncore": 0, "charge": 0}),
]

testdata_rccsd = [(RCCSD, "h2", "cc-pvdz", {"ncore": 0, "charge": 0})]

testdata_fock = [(RCCSD, "h2o", "3-21g", {"ncore": 0, "charge": 0})]


def check_guess(amplitudes):
    """Check if argument is a dictionary containing t_1 and t_2."""
    assert isinstance(amplitudes, dict)
    t_1 = amplitudes["t_1"]
    t_2 = amplitudes["t_2"]
    assert isinstance(t_1, DenseTwoIndex)
    assert isinstance(t_2, DenseFourIndex)
    assert t_1.shape == (1, 9)
    assert t_2.shape == (1, 9, 1, 9)
    assert np.allclose(t_2.array, t_2.array.transpose(2, 3, 0, 1))


@pytest.mark.parametrize("cls,mol_f,basis,kwargs", testdata_rccsd)
def test_rccsd_generate_random_guess(cls, mol_f, basis, kwargs, linalg_slow):
    """Check if generate_random_guess method returns expected output."""
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    solver = cls(mol_.lf, mol_.occ_model)
    initguess = solver.generate_random_guess()
    check_guess(initguess)


@pytest.mark.parametrize("cls,mol_f,basis,kwargs", testdata_rccsd)
def test_rccsd_generate_constant_guess(cls, mol_f, basis, kwargs, linalg_slow):
    """Check if generate_constant_guess method returns expected output."""
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    solver = cls(mol_.lf, mol_.occ_model)
    solver.initguess = "constant"
    initguess_1 = solver.generate_constant_guess(0.5)
    initguess_2 = solver.generate_guess(constant=0.5)
    check_guess(initguess_1)
    assert initguess_1["t_1"].get_element(0, 0) == 0.5
    assert initguess_1["t_2"].get_element(0, 0, 0, 0) == 0.5
    assert initguess_1["t_2"].get_element(0, 0, 0, 1) == 0.5
    check_guess(initguess_2)
    assert initguess_2["t_1"].get_element(0, 0) == 0.5
    assert initguess_2["t_2"].get_element(0, 0, 0, 0) == 0.5
    assert initguess_2["t_2"].get_element(0, 0, 0, 1) == 0.5


@pytest.mark.parametrize("cls,mol_f,basis,kwargs", testdata_rccsd)
def test_rccsd_generate_mp2_guess(cls, mol_f, basis, kwargs, linalg_slow):
    """Check if generate_mp2_guess method returns expected output."""
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()
    ccsd = cls(mol_.lf, mol_.occ_model)
    # we need to calculate the effective Hamiltonian for an MP2 guess
    ccsd.set_hamiltonian(mol_.one, mol_.two, mol_.hf.orb_a)
    check_guess(ccsd.generate_mp2_guess())


@pytest.mark.parametrize("cls,mol_f,basis,kwargs", testdata_iodata)
def test_rccsd_generate_guess_iodata(cls, mol_f, basis, kwargs, linalg_slow):
    """Check if get_amplitudes_from_iodata method returns expected output."""
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    # we need first to run a calculation
    # the restart should work with either CCD or CCSD
    mol_.do_rhf()
    cc = cls(mol_.lf, mol_.occ_model)
    cc_ref = cc(*mol_.hamiltonian, mol_.hf)
    # now check restart option
    ccsd = RCCSD(mol_.lf, mol_.occ_model)
    # generate all required intermediates
    ccsd.set_hamiltonian(mol_.one, mol_.two, mol_.hf.orb_a)
    # set restart file path
    ccsd.initguess = f"{filemanager.result_dir}/checkpoint_{cls.__name__}.h5"
    # read restart file
    t_from_file = ccsd.read_guess_from_file()
    # assert if close (we restart from T_2, so T_1 does not exist)
    assert np.allclose(cc_ref.t_2.array, t_from_file["t_2"].array)
    # do a dry run
    ccsd(
        *mol_.hamiltonian,
        mol_.hf,
        initguess=f"{filemanager.result_dir}/checkpoint_{cls.__name__}.h5",
    )


@pytest.mark.parametrize("cls,mol_f,basis,kwargs", testdata_rccsd)
def test_rccsd_can_get_t_2_amplitudes_from_dict(
    cls, mol_f, basis, kwargs, linalg_slow
):
    """Check if method get_amplitudes_from_dict works."""
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    ccsd = cls(mol_.lf, mol_.occ_model)
    legit_dicts = [{"t_1": 1, "t_2": 2}]
    for item in legit_dicts:
        assert ccsd.get_amplitudes_from_dict(item)["t_1"] == 1
        assert ccsd.get_amplitudes_from_dict(item)["t_2"] == 2
    with pytest.raises(ArgumentError):
        ccsd.get_amplitudes_from_dict({"ampl": "nope"})


@pytest.mark.parametrize("cls,mol_f,basis,kwargs", testdata_rccsd)
def test_rccsd_can_get_t_2_amplitudes_from_iodata(
    cls, mol_f, basis, kwargs, linalg_slow
):
    """Check if method get_amplitudes_from_iodata works."""
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    ccsd = cls(mol_.lf, mol_.occ_model)
    legit_io = [IOData(t_1=1, t_2=2), IOData(c_2=3, t_1=1, t_2=2)]
    for item in legit_io:
        assert ccsd.get_amplitudes_from_iodata(item)["t_1"] == 1
        assert ccsd.get_amplitudes_from_iodata(item)["t_2"] == 2
    with pytest.raises(ArgumentError):
        ccsd.get_amplitudes_from_iodata(IOData(ampl="nope"))


@pytest.mark.parametrize("cls,mol_f,basis,kwargs", testdata_rccsd)
def test_rccsd_can_get_l_2_amplitudes_from_dict(
    cls, mol_f, basis, kwargs, linalg_slow
):
    """Check if method get_amplitudes_from_dict works."""
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    ccsd = cls(mol_.lf, mol_.occ_model)
    legit_dicts = [{"t_2": 4, "l_2": 3, "t_1": 1, "l_1": 0, "c_2": 5}]
    for item in legit_dicts:
        assert ccsd.get_amplitudes_from_dict(item, select="l")["t_1"] == 0
        assert ccsd.get_amplitudes_from_dict(item, select="l")["t_2"] == 3
    with pytest.raises(ArgumentError):
        ccsd.get_amplitudes_from_dict({"t_2": "nope"}, select="l")


@pytest.mark.parametrize("cls,mol_f,basis,kwargs", testdata_rccsd)
def test_rccsd_can_get_l_2_amplitudes_from_iodata(
    cls, mol_f, basis, kwargs, linalg_slow
):
    """Check if method get_amplitudes_from_iodata works."""
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    ccsd = cls(mol_.lf, mol_.occ_model)
    legit_io = [
        IOData(a=1, l_2=2, l_1=0),
        IOData(t_1=1, t_2=1, l_1=0, l_2=2),
        IOData(l_2=2, l_1=0),
    ]
    for item in legit_io:
        assert ccsd.get_amplitudes_from_iodata(item, select="l")["t_1"] == 0
        assert ccsd.get_amplitudes_from_iodata(item, select="l")["t_2"] == 2
    with pytest.raises(ArgumentError):
        ccsd.get_amplitudes_from_iodata(IOData(ampl="nope"))


@pytest.mark.parametrize("cls,mol_f,basis,kwargs", testdata_rccsd)
@pytest.mark.parametrize("select", ["mp2", "random", "constant"])
def test_rcc_generate_guess(cls, mol_f, basis, kwargs, linalg_slow, select):
    """Check if generate_guess method returns expected output."""
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()
    kwargs = {"orbital": mol_.hf.orb_a, "ao1": mol_.one, "ao2": mol_.two}
    solver = cls(mol_.lf, mol_.occ_model)
    solver.initguess = select
    # we need to calculate the effective Hamiltonian for an MP2 guess
    solver.set_hamiltonian(mol_.one, mol_.two, mol_.hf.orb_a)
    amplitudes = solver.generate_guess(**kwargs)
    assert isinstance(amplitudes["t_2"], DenseFourIndex)
    assert isinstance(amplitudes["t_1"], DenseTwoIndex)


@pytest.mark.parametrize("cls,mol_f,basis,kwargs", testdata_rccsd)
@pytest.mark.parametrize("solver", ["krylov", "pbqn"])
def test_rccsd_ravel(cls, mol_f, basis, kwargs, linalg_slow, solver):
    """Check if ravel method returns a vector with expected length."""
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    cc_solver = cls(mol_.lf, mol_.occ_model)
    initguess = cc_solver.generate_constant_guess(0.5)
    cc_solver.solver = solver
    if solver == "krylov":
        assert len(cc_solver.ravel(initguess)) == 54
    if solver == "pbqn":
        assert (cc_solver.ravel(initguess)).shape[0] == 54


@pytest.mark.parametrize("cls,mol_f,basis,kwargs", testdata_rccsd)
def test_rccsd_unravel(cls, mol_f, basis, kwargs, linalg_slow):
    """Check if ravel method returns t_1 and t_2 amplitudes."""
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    vector = np.ndarray(54)
    solver = cls(mol_.lf, mol_.occ_model)
    amplitudes = solver.unravel(vector)
    assert isinstance(amplitudes, dict)
    assert isinstance(amplitudes["t_1"], DenseTwoIndex)
    assert isinstance(amplitudes["t_2"], DenseFourIndex)


@pytest.mark.parametrize("cls,mol_f,basis,kwargs", testdata_rccsd)
def test_unravel_ravel(cls, mol_f, basis, kwargs, linalg_slow):
    """Check if unravel(ravel(X)) = X."""
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    ccd = cls(mol_.lf, mol_.occ_model)
    amplitudes = ccd.generate_constant_guess(0.5)
    # Need to copy as we remove the arrays
    amplitudes_ = copy.deepcopy(amplitudes)
    vector = ccd.ravel(amplitudes)
    unraveled_amplitudes = ccd.unravel(vector)
    assert amplitudes_ == unraveled_amplitudes


@pytest.mark.parametrize("cls,mol_f,basis,kwargs", testdata_rccsd)
def test_rccsd_vfunction(cls, mol_f, basis, kwargs, linalg_slow):
    """Check if vector fucntion has a proper symmetry."""
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()
    solver = cls(mol_.lf, mol_.occ_model)
    solver.set_hamiltonian(mol_.one, mol_.two, mol_.hf.orb_a)
    initguess = solver.generate_constant_guess(constant=0.125)
    vfunc = solver.vfunction(solver.ravel(initguess))
    amplitudes = solver.unravel(vfunc)
    assert "t_1" in amplitudes
    assert "t_2" in amplitudes
    vfunc_t2 = amplitudes["t_2"]
    assert np.allclose(vfunc_t2.array, vfunc_t2.array.transpose(2, 3, 0, 1))


@pytest.mark.parametrize("cls,mol_f,basis,kwargs", testdata_fock)
def test_can_construct_hamiltonian_blocks(
    linalg_slow, cls, mol_f, basis, kwargs
):
    "Check if hamiltonian property contains expected blocks."
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()
    rcc = cls(linalg_slow(mol_.lf.default_nbasis), mol_.occ_model)
    one = mol_.one.copy()
    rcc.set_hamiltonian(one, mol_.two, mol_.hf.orb_a)
    assert isinstance(rcc.cache, Cache)

    # Check Fock matrix blocks
    fock_labels = ["fock_oo", "fock_ov", "fock_vv"]

    check_fock_in_cache(rcc.cache, fock_labels, nocc=5, nvirt=8)

    # Check 2-body Hamiltonian blocks and exchange blocks
    ham_2 = ["eri_oooo", "eri_ooov", "eri_oovv", "eri_ovov", "eri_ovvv"]
    ham_exc = ["exchange_oovv", "exchange_ooov"]
    check_eri_in_cache(rcc.cache, ham_2 + ham_exc, nocc=5, nvirt=8)


@pytest.mark.parametrize("cls,mol_f,basis,kwargs", testdata_rccsd)
def test_rccsd_compute_t1_diagnostic(cls, mol_f, basis, kwargs, linalg_slow):
    """Compare T1 diagnostic with reference data."""
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()
    solver = cls(mol_.lf, mol_.occ_model)
    out = solver(mol_.one, mol_.two, mol_.hf.orb_a, threshold_r=1e-8)
    t1_diag = solver.compute_t1_diagnostic(out.t_1, out.nocc)
    assert abs(out.e_tot + 0.034709514) < 1e-8
    assert abs(t1_diag - 0.00518216985) < 1e-8


@pytest.mark.parametrize("cls,mol_f,basis,kwargs", testdata_rccsd)
def test_rccsd_compute_d1_diagnostic(cls, mol_f, basis, kwargs, linalg_slow):
    """Compare D1 diagnostic with reference data."""
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()
    solver = cls(mol_.lf, mol_.occ_model)
    out = solver(mol_.one, mol_.two, mol_.hf.orb_a, threshold_r=1e-8)
    d1_diag = solver.compute_d1_diagnostic(out.t_1)

    assert abs(d1_diag - 0.007328693479) < 1e-8


@pytest.mark.parametrize("cls,mol_f,basis,kwargs", testdata_rccsd)
def test_get_max_amplitudes(cls, mol_f, basis, kwargs, linalg_slow):
    "Check if amplitudes can be converted from tensor to index-value format."
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()
    ccsd = cls(mol_.lf, mol_.occ_model)
    out = ccsd(
        *mol_.hamiltonian,
        mol_.hf.orb_a,
        initguess="constant",
        threshold_r=1e-8,
    )

    assert np.isclose(out.e_corr, -0.034709514282981926, atol=1e-7)
    t_1 = ccsd.get_max_amplitudes(threshold=1e-3)["t_1"]
    t_2 = ccsd.get_max_amplitudes(threshold=5e-2)["t_2"]
    # Check single-excitation amplitudes.
    assert t_1[0][0] == (1, 3), "Did not find expected index."
    assert t_1[1][0] == (1, 7), "Did not find expected index."
    assert len(t_1) == 2, "The number of max amplitudes is not correct."
    # Check double-excitation amplitudes
    assert t_2[0][0] == (1, 2, 1, 2), "Did not find expected index."
    assert np.isclose(t_2[0][1], -0.053721), "Did not find expected value."
    assert t_2[1][0] == (1, 4, 1, 4), "Did not find expected index."
    assert np.isclose(t_2[1][1], -0.053181), "Did not find expected value."
    assert t_2[2][0] == (1, 3, 1, 3), "Did not find expected index."
    assert len(t_2) == 3, "The number of max amplitudes is not correct."
