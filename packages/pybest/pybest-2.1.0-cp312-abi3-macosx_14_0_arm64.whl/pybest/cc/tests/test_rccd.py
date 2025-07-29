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

"""Unit tests for Rcls. method from rcls. module."""

import copy

import numpy as np
import pytest

from pybest.cache import Cache
from pybest.cc import RCCD
from pybest.exceptions import ArgumentError
from pybest.iodata import IOData
from pybest.linalg import DenseFourIndex, DenseOneIndex

from .common import CCMolecule, check_eri_in_cache, check_fock_in_cache

#
#  Unit test
#


def check_guess(initguess):
    """Checks if argument is a dictionary containing t_2 amplitudes."""
    assert isinstance(initguess, dict)
    t_2 = initguess["t_2"]
    assert isinstance(t_2, DenseFourIndex)
    assert t_2.shape == (1, 9, 1, 9)
    assert np.allclose(t_2.array, t_2.array.transpose(2, 3, 0, 1))


testdata_t_2_amplitudes = [(RCCD, "h2", "cc-pvdz")]
testdata_fock = [(RCCD, "h2o", "3-21g")]


@pytest.mark.parametrize("cls,mol_f,basis", testdata_t_2_amplitudes)
def test_rccd_can_get_t_2_amplitudes_from_dict(cls, mol_f, basis, linalg_slow):
    """Checks if method get_amplitudes_from_dict works."""
    # Prepare molecule
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    cls_instance = cls(mol_.lf, mol_.occ_model)

    legit_dicts = [{"a": 0, "t_2": 2}, {"t_1": 1, "t_2": 2}, {"c_2": 2}]
    for item in legit_dicts:
        assert (
            cls_instance.get_amplitudes_from_dict(dictionary=item)["t_2"] == 2
        )
    with pytest.raises(ArgumentError):
        cls_instance.get_amplitudes_from_dict(dictionary={"ampl": "nope"})


@pytest.mark.parametrize("cls,mol_f,basis", testdata_t_2_amplitudes)
def test_rccd_can_get_t_2_amplitudes_from_iodata(
    cls, mol_f, basis, linalg_slow
):
    """Check if method get_amplitudes_from_dict works."""
    # Prepare molecule
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    cls_instance = cls(mol_.lf, mol_.occ_model)
    legit_io = [IOData(a=0, t_2=2), IOData(t_1=1, t_2=2), IOData(c_2=2)]
    for item in legit_io:
        assert cls_instance.get_amplitudes_from_iodata(iodata=item)["t_2"] == 2
    with pytest.raises(ArgumentError):
        cls_instance.get_amplitudes_from_iodata(iodata=IOData(ampl="nope"))


@pytest.mark.parametrize("cls,mol_f,basis", testdata_t_2_amplitudes)
def test_rccd_can_get_l_2_amplitudes_from_dict(cls, mol_f, basis, linalg_slow):
    """Check if method get_amplitudes_from_dict works."""
    # Prepare molecule
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    cls_instance = cls(mol_.lf, mol_.occ_model)
    legit_dicts = [{"a": 0, "l_2": 2}, {"t_2": 1, "l_2": 2}, {"l_2": 2}]
    for item in legit_dicts:
        assert (
            cls_instance.get_amplitudes_from_dict(dictionary=item, select="l")[
                "t_2"
            ]
            == 2
        )
    with pytest.raises(ArgumentError):
        cls_instance.get_amplitudes_from_dict(
            dictionary={"t_2": "nope"}, select="l"
        )


@pytest.mark.parametrize("cls,mol_f,basis", testdata_t_2_amplitudes)
def test_rccd_can_get_l_2_amplitudes_from_iodata(
    cls, mol_f, basis, linalg_slow
):
    """Check if method get_amplitudes_from_iodata works."""
    # Prepare molecule
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    cls_instance = cls(mol_.lf, mol_.occ_model)

    legit_io = [IOData(a=0, l_2=2), IOData(t_1=1, t_2=1, l_2=2), IOData(l_2=2)]
    for item in legit_io:
        assert (
            cls_instance.get_amplitudes_from_iodata(item, select="l")["t_2"]
            == 2
        )
    with pytest.raises(ArgumentError):
        cls_instance.get_amplitudes_from_iodata(IOData(ampl="nope"))


@pytest.mark.parametrize("cls,mol_f,basis", testdata_t_2_amplitudes)
def test_rccd_generate_random_guess(cls, mol_f, basis, linalg_slow):
    """Check if method generate_random_guess returns an expected output."""
    # Prepare molecule
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    cls_instance = cls(mol_.lf, mol_.occ_model)
    check_guess(cls_instance.generate_random_guess())


@pytest.mark.parametrize("cls,mol_f,basis", testdata_t_2_amplitudes)
def test_rccd_generate_constant_guess(cls, mol_f, basis, linalg_slow):
    """Check if method generate_constant_guess returns an expected output."""
    # Prepare molecule
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    cls_instance = cls(mol_.lf, mol_.occ_model)
    check_guess(cls_instance.generate_constant_guess(0.5))


@pytest.mark.parametrize("cls,mol_f,basis", testdata_t_2_amplitudes)
def test_rccd_generate_mp2_guess(cls, mol_f, basis, linalg_slow):
    """Check if method generate_mp2_guess returns an expected output."""
    # Prepare molecule
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()

    # we need to calculate the effective Hamiltonian for an MP2 guess
    cls_instance = cls(mol_.lf, mol_.occ_model)
    cls_instance.set_hamiltonian(mol_.one, mol_.two, mol_.hf.orb_a)

    check_guess(cls_instance.generate_mp2_guess())


@pytest.mark.parametrize("cls,mol_f,basis", testdata_t_2_amplitudes)
@pytest.mark.parametrize("select", ["mp2", "random", "constant"])
def test_rccd_generate_guess(select, cls, mol_f, basis, linalg_slow):
    """Check if method generate_guess returns an expected output."""
    # Prepare molecule
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()

    kwargs = {"orbital": mol_.hf.orb_a, "ao1": mol_.one, "ao2": mol_.two}
    cls_instance = cls(mol_.lf, mol_.occ_model)
    cls_instance.initguess = select
    # we need to calculate the effective Hamiltonian for an MP2 guess
    cls_instance.set_hamiltonian(mol_.one, mol_.two, mol_.hf.orb_a)
    initguess = cls_instance.generate_guess(**kwargs)
    assert isinstance(initguess, dict)
    assert isinstance(initguess["t_2"], DenseFourIndex)


@pytest.mark.parametrize("cls,mol_f,basis", testdata_t_2_amplitudes)
@pytest.mark.parametrize("solver", ["krylov", "pbqn"])
def test_rccd_ravel(solver, cls, mol_f, basis, linalg_slow):
    """Check if ravel method returns a vector with expected length."""
    # Prepare molecule
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)

    cls_instance = cls(mol_.lf, mol_.occ_model)
    initguess = cls_instance.generate_constant_guess(0.5)
    cls_instance.solver = solver
    if solver == "krylov":
        assert len(cls_instance.ravel(initguess)) == 45
    if solver == "pbqn":
        assert (cls_instance.ravel(initguess)).shape[0] == 45


@pytest.mark.parametrize("cls,mol_f,basis", testdata_t_2_amplitudes)
def test_rccd_unravel(cls, mol_f, basis, linalg_slow):
    """Check if unravel method returns DenseFourIndex inst of proper size."""
    # Prepare molecule
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)

    vector = np.ndarray(45)
    cls_instance = cls(mol_.lf, mol_.occ_model)
    amplitudes = cls_instance.unravel(vector)
    assert isinstance(amplitudes, dict)
    assert isinstance(amplitudes["t_2"], DenseFourIndex)


@pytest.mark.parametrize("cls,mol_f,basis", testdata_t_2_amplitudes)
def test_unravel_ravel(cls, mol_f, basis, linalg_slow):
    """Check if unravel(ravel(X)) = X."""
    # Prepare molecule
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)

    cls_instance = cls(mol_.lf, mol_.occ_model)
    amplitudes = cls_instance.generate_constant_guess(0.5)
    # Need to copy as we remove the arrays
    amplitudes_ = copy.deepcopy(amplitudes)
    vector = cls_instance.ravel(amplitudes)
    unraveled_amplitudes = cls_instance.unravel(vector)
    assert amplitudes_ == unraveled_amplitudes


@pytest.mark.parametrize("cls,mol_f,basis", testdata_t_2_amplitudes)
@pytest.mark.parametrize("solver", ["krylov", "pbqn"])
def test_rcc_vfunction_symmetry_and_type(
    solver, cls, mol_f, basis, linalg_slow
):
    """Check if vector function has a proper symmetry and type."""
    # Prepare molecule
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()

    cls_instance = cls(mol_.lf, mol_.occ_model)
    cls_instance.solver = solver

    cls_instance.set_hamiltonian(mol_.one, mol_.two, mol_.hf.orb_a)
    t_2 = cls_instance.generate_constant_guess(constant=0.125)
    vfunc = cls_instance.vfunction(cls_instance.ravel(t_2))
    assert isinstance(vfunc, (np.ndarray, DenseOneIndex))
    vfunc_t2 = cls_instance.unravel(vfunc)["t_2"]
    assert np.allclose(vfunc_t2.array, vfunc_t2.array.transpose(2, 3, 0, 1))


@pytest.mark.parametrize("cls,mol_f,basis", testdata_fock)
def test_can_construct_hamiltonian_blocks(cls, mol_f, basis, linalg_slow):
    "Check if hamiltonian property contains expected blocks."
    # Prepare molecule
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()
    nbasis = mol_.occ_model.nbasis[0]
    cls_instance = cls(linalg_slow(nbasis), mol_.occ_model)
    cls_instance.set_hamiltonian(mol_.one, mol_.two, mol_.hf.orb_a)
    assert isinstance(cls_instance.cache, Cache)

    # Check Fock matrix blocks
    fock_labels = ["fock_oo", "fock_vv"]
    check_fock_in_cache(cls_instance.cache, fock_labels, nocc=5, nvirt=8)

    # Check 2-body Hamiltonian blocks and exchange blocks
    ham_2 = ["eri_oooo", "eri_oovv", "eri_ovov"]
    ham_exc = ["exchange_oovv"]
    check_eri_in_cache(cls_instance.cache, ham_2 + ham_exc, nocc=5, nvirt=8)


@pytest.mark.parametrize("cls,mol_f,basis", testdata_fock)
def test_rccd_init_fails_if_kwarg_not_recognized(
    cls, mol_f, basis, linalg_slow
):
    "Check if RCC init raises error if kwarg is not recognized."
    # Prepare molecule
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)

    with pytest.raises(ArgumentError):
        cls(mol_.lf, mol_.occ_model, badkwarg="Wrong kwarg.")


@pytest.mark.parametrize("cls,mol_f,basis", testdata_fock)
def test_rccd_call_fails_if_kwarg_not_recognized(
    cls, mol_f, basis, linalg_slow
):
    "Check if RCC init raises error if kwarg is not recognized."
    # Prepare molecule
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()
    with pytest.raises(ArgumentError):
        cls_instance = cls(mol_.lf, mol_.occ_model)
        cls_instance(
            mol_.one, mol_.two, mol_.hf.orb_a, badkwarg="Wrong kwarg."
        )


@pytest.mark.parametrize("cls,mol_f,basis", testdata_t_2_amplitudes)
def test_get_max_amplitudes(cls, mol_f, basis, linalg_slow):
    "Check if amplitudes can be converted from tensor to index-value format."
    # Prepare molecule
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()

    cls_instance = cls(mol_.lf, mol_.occ_model)
    cls_instance(
        mol_.one,
        mol_.two,
        mol_.hf.orb_a,
        initguess="constant",
        threshold_r=1e-8,
    )
    t_2 = cls_instance.get_max_amplitudes()["t_2"]
    assert t_2[0][0] == (1, 2, 1, 2), "Did not find expected index."
    assert np.isclose(t_2[0][1], -0.053531), "Did not find expected value."
    assert t_2[1][0] == (1, 4, 1, 4), "Did not find expected index."
    assert np.isclose(t_2[1][1], -0.052408), "Did not find expected value."
    assert t_2[11][0] in [
        (1, 10, 1, 4),
        (1, 4, 1, 10),
    ], "Did not find expected index."
    assert len(t_2) == 12, "The number of max amplitudes is not correct."
    t_2 = cls_instance.get_max_amplitudes(limit=4)["t_2"]
    assert t_2[0][0] == (1, 2, 1, 2), "Did not find expected index."
    assert np.isclose(t_2[0][1], -0.053531), "Did not find expected value."
    assert t_2[1][0] == (1, 4, 1, 4), "Did not find expected index."
    assert np.isclose(t_2[1][1], -0.052408), "Did not find expected value."
    assert len(t_2) == 4, "The number of max amplitudes is not correct."
    t_2 = cls_instance.get_max_amplitudes(threshold=0.05)["t_2"]
    assert t_2[0][0] == (1, 2, 1, 2), "Did not find expected index."
    assert np.isclose(t_2[0][1], -0.053531), "Did not find expected value."
    assert t_2[1][0] == (1, 4, 1, 4), "Did not find expected index."
    assert np.isclose(t_2[1][1], -0.052408), "Did not find expected value."
    assert len(t_2) == 3, "The number of max amplitudes is not correct."
