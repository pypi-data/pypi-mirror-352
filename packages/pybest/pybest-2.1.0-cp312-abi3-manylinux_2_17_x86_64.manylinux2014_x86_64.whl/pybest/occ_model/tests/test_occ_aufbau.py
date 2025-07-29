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

from pybest.context import context
from pybest.exceptions import (
    ArgumentError,
    ConsistencyError,
    ElectronCountError,
)
from pybest.gbasis import Basis, get_gobasis
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel


def test_occ_aufbau_gobasis(aufbau_test):
    """Test Aufbau model for basis, charge, alpha, ncore, nactdo, and nactdv arguments as
    input."""
    basis_name, mol, kwargs, expected = aufbau_test
    fn_xyz = context.get_fn(mol)
    basis = get_gobasis(basis_name, fn_xyz, print_basis=False)
    lf = DenseLinalgFactory(basis.nbasis)
    # either restricted (alpha=0) or unrestricted orbitals (alpha>0)
    norbs = 1 if kwargs.get("alpha") == 0 else 2
    if kwargs.get("unrestricted", False):
        norbs = 2
    orb = [lf.create_orbital() for n in range(norbs)]

    occ_model = AufbauOccModel(basis, **kwargs)
    occ_model.assign_occ_reference(*orb)

    for key, value in expected.items():
        if key == "occ":
            # check occupation numbers of each orbital (alpha, beta)
            assert len(orb) == len(value)
            for orb_, el in zip(orb, value):
                assert abs(orb_.occupations[: len(el)] - el).max() < 1e-10
        else:
            # check all other attributes
            assert getattr(occ_model, key) == value


def test_occ_aufbau_lf(aufbau_test):
    """Test Aufbau model for lf, charge, alpha, ncore, nactdo, and nactdv arguments as
    input. We have to explicitly give ``nel`` otherwise we get an error.
    """
    basis_name, mol, kwargs, expected = aufbau_test
    # construct basis only to create some lf instance
    fn_xyz = context.get_fn(mol)
    basis = get_gobasis(basis_name, fn_xyz, print_basis=False)
    lf = DenseLinalgFactory(basis.nbasis)
    # either restricted (alpha=0) or unrestricted orbitals (alpha>0)
    norbs = 1 if kwargs.get("alpha") == 0 else 2
    if kwargs.get("unrestricted", False):
        norbs = 2
    orb = [lf.create_orbital() for n in range(norbs)]

    occ_model = AufbauOccModel(lf, basis, **kwargs, nel=expected["nel"])
    occ_model.assign_occ_reference(*orb)

    for key, value in expected.items():
        if key == "occ":
            # check occupation numbers of each orbital (alpha, beta)
            assert len(orb) == len(value)
            for orb_, el in zip(orb, value):
                assert abs(orb_.occupations[: len(el)] - el).max() < 1e-10
        else:
            # check all other attributes
            assert getattr(occ_model, key) == value


def test_occ_aufbau_lf_nel(aufbau_test_lf_nel):
    """Test Aufbau model for lf, nel, and occ_a, occ_b as only input.
    Such an Aufbau model is used, for instance, in model Hamiltonians like
    Hubbard.
    """
    nbasis, nel, nocc, expected = aufbau_test_lf_nel
    # construct basis only to create some lf instance
    lf = DenseLinalgFactory(nbasis)
    orb = [lf.create_orbital()]

    occ_model = AufbauOccModel(lf, nel=nel, **nocc)
    occ_model.assign_occ_reference(*orb)

    for key, value in expected.items():
        if key == "occ":
            # check occupation numbers of each orbital (alpha, beta)
            assert len(orb) == len(value)
            for orb_, el in zip(orb, value):
                assert abs(orb_.occupations[: len(el)] - el).max() < 1e-10
        else:
            # check all other attributes
            assert getattr(occ_model, key) == value


def test_occ_aufbau_lf_nel_os(aufbau_test_lf_nel_os):
    """Test Aufbau model for lf, nel, and occ_a, occ_b as only input.
    Such an Aufbau model is used, for instance, in model Hamiltonians like
    Hubbard.
    """
    nbasis, nel, nocc, expected = aufbau_test_lf_nel_os
    # construct basis only to create some lf instance
    lf = DenseLinalgFactory(nbasis)
    orb = [lf.create_orbital(), lf.create_orbital()]

    occ_model = AufbauOccModel(lf, nel=nel, **nocc)
    occ_model.assign_occ_reference(*orb)

    for key, value in expected.items():
        if key == "occ":
            # check occupation numbers of each orbital (alpha, beta)
            assert len(orb) == len(value)
            for orb_, el in zip(orb, value):
                assert abs(orb_.occupations[: len(el)] - el).max() < 1e-10
        else:
            # check all other attributes
            assert getattr(occ_model, key) == value


#
# Invalid calls, all test should raise an error
#


test_wrong_arguments = [
    ({"ncore": 0, "foo": 5}, ArgumentError),  # unknown kwargs
    ({"ncore": 0, "nocc_b": 5}, ArgumentError),  # missing arguments nocc_a
    (
        {"ncore": 0, "nocc_a": 4, "nocc_b": 5},
        ElectronCountError,
    ),  # nocc_a < nocc_b
    (
        {"ncore": 0, "nocc_a": 4, "nel": 9},
        ElectronCountError,
    ),  # nocc_a does not agree with nel
    ({"ncore": 0, "nocc_a": 5, "nocc_b": 5, "nel": 9}, ElectronCountError),
    # nel does not agree with basis information or nocc_a/nocc_b (for lf)
    ({"ncore": 0, "nocc_a": 5.5}, ConsistencyError),
    # nocc_a/nocc_b does not agree with nel
    (
        {
            "ncore": 0,
            "nocc_a": 5,
            "nocc_b": 4,
            "charge": 1,
            "nel": 8,
        },  # correct occupation and charge
        ElectronCountError,
    ),  # nocc_a/nocc_b or charge does not agree with nel
    (
        {
            "ncore": 0,
            "nocc_a": 5.1,
            "nocc_b": 3.9,
            "charge": 1,
            "nel": 9,
        },  # correct occupation and charge
        ConsistencyError,
    ),  # only integer occupations are allowed
    (
        {
            "ncore": 0,
            "charge": 1,
            "unrestricted": False,
            "nel": 9,
        },
        ConsistencyError,
    ),  # cannot enforce restricted occupation pattern
    (
        {
            "charge": 0,
            "ncore": 0,
            "nactdo": 7,
            "nactdv": 10,
            "nel": 10,
        },
        ConsistencyError,
    ),  # nactdo cannot be larger than nacto
    (
        {
            "charge": 0,
            "ncore": 0,
            "nactdo": 4,
            "nactdv": 31,
            "nel": 10,
        },
        ConsistencyError,
    ),  # nactdv cannot be larger than nactv
]

test_instance = ["basis", "lf"]


@pytest.mark.parametrize("kwargs,error", test_wrong_arguments)
@pytest.mark.parametrize("factory", [Basis, DenseLinalgFactory])
def test_occ_aufbau_arguments(kwargs, error, factory):
    """Test Aufbau model for basis, nocc_a/nocc_b, and ncore arguments as
    input.
    """
    fn_xyz = context.get_fn("test/water.xyz")
    basis = get_gobasis("cc-pvdz", fn_xyz, print_basis=False)

    factory_map = {
        Basis: basis,
        DenseLinalgFactory: DenseLinalgFactory(basis.nbasis),
    }

    with pytest.raises(error):
        assert AufbauOccModel(factory_map[factory], **kwargs)


#
# Test all valid kwargs
#

test_kwargs = [
    (
        "cc-pvdz",
        "test/water.xyz",
        {
            "unrestricted": True,
            "alpha": 0,
            "charge": 0,
            "nel": 10,
            "ncore": 0,
            "nocc_a": 5,
            "nocc_b": 5,
            "nactdo": 0,
            "nactdv": 0,
        },
    ),
]

test_instance = ["basis", "lf"]


@pytest.mark.parametrize("basis_name,mol,kwargs", test_kwargs)
@pytest.mark.parametrize("factory", [Basis, DenseLinalgFactory])
def test_occ_aufbau_kwargs(basis_name, mol, kwargs, factory):
    """Test Aufbau model for basis, nocc_a/nocc_b, ncore, nactdo, and nactdv arguments as
    input.
    """
    fn_xyz = context.get_fn(mol)
    basis = get_gobasis(basis_name, fn_xyz, print_basis=False)
    factory_map = {
        Basis: basis,
        DenseLinalgFactory: DenseLinalgFactory(basis.nbasis),
    }

    assert isinstance(
        AufbauOccModel(factory_map[factory], **kwargs), AufbauOccModel
    )


def test_ncore_with_molecule(ncore_test_with_molecule):
    """Test: automatically computes the number of
    frozen core atomic orbitals with molecule"""
    basis_name, mol, kwargs, expected = ncore_test_with_molecule
    fn_xyz = context.get_fn(mol)
    basis = get_gobasis(basis_name, fn_xyz, print_basis=False)
    occ_model = AufbauOccModel(basis, **kwargs)

    assert occ_model.ncore == expected


def test_ncore_own_args(ncore_test_with_own_args):
    """Test: automatically computes the number of
    frozen core atomic orbitals with own args"""
    tmp, num_atom, expected = ncore_test_with_own_args
    basis_name, mol, kwargs = tmp
    fn_xyz = context.get_fn(mol)
    basis = get_gobasis(basis_name, fn_xyz, print_basis=False)
    occ_model = AufbauOccModel(basis, **kwargs)
    ncore = occ_model.number_ncore(atoms=num_atom)

    assert ncore == expected


def test_ncore_with_atoms(ncore_test_with_atoms):
    """Test: automatically computes the number of
    frozen core atomic orbitals with atoms"""
    basis_name, mol, ncore = ncore_test_with_atoms
    basis = get_gobasis(basis_name, mol, print_basis=False)
    occ_model = AufbauOccModel(basis)
    assert occ_model.ncore[0] == ncore
