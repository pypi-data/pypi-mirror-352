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

from __future__ import annotations

from typing import Any

import numpy as np
import pytest

from pybest.context import context
from pybest.exceptions import ArgumentError
from pybest.gbasis import Basis, get_gobasis
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import FermiOccModel

test_fermi = [
    # basis, molecule, {charge, #unpaired electrons (alpha), ncore}
    (
        "cc-pvdz",
        "test/water.xyz",
        {"charge": 0, "alpha": 0, "ncore": 0},
        {
            # Distribution evaluated for energy values of 0 (equal occupations)
            "occ": [np.full((24), 1 / 4.8)],
            "charge": 0,
            "nel": 10,
            "nbasis": [24],
            "nact": [24],
            "nocc": [24],
            "nvirt": [0],
            "nacto": [24],
            "nactv": [0],
            "ncore": [0],
        },
    ),
    (
        "cc-pvdz",
        "test/water.xyz",
        {"charge": 0, "alpha": 0, "ncore": 0},
        {
            # Distribution evaluated for energy values of 0 (equal occupations)
            "occ": [np.full((24), 1 / 4.8)],
            "charge": 0,
            "nel": 10,
            "nbasis": [24],
            "nact": [24],
            "nocc": [24],
            "nvirt": [0],
            "nacto": [24],
            "nactv": [0],
            "ncore": [0],
        },
    ),
    (
        "cc-pvdz",
        "test/water.xyz",
        {"charge": 0, "alpha": 0, "ncore": 1},
        {
            "occ": [np.full((24), 1 / 4.8)],
            "charge": 0,
            "nel": 10,
            "nbasis": [24],
            "nact": [23],
            "nocc": [24],
            "nvirt": [0],
            "nacto": [23],
            "nactv": [0],
            "ncore": [1],
        },
    ),
    (
        "cc-pvdz",
        "test/water.xyz",
        {"charge": 1, "alpha": 1, "ncore": 0},
        {
            "occ": [np.full((24), 1 / 4.8), np.full((24), 1 / 6)],
            "charge": 1,
            "nel": 9,
            "nbasis": [24, 24],
            "nact": [24, 24],
            "nocc": [24, 24],
            "nvirt": [0, 0],
            "nacto": [24, 24],
            "nactv": [0, 0],
            "ncore": [0, 0],
        },
    ),
    (
        "cc-pvdz",
        "test/water.xyz",
        {"charge": 2, "ncore": 0, "unrestricted": True},
        {
            "occ": [np.full((24), 1 / 6), np.full((24), 1 / 6)],
            "charge": 2,
            "nel": 8,
            "nbasis": [24, 24],
            "nact": [24, 24],
            "nocc": [24, 24],
            "nvirt": [0, 0],
            "nacto": [24, 24],
            "nactv": [0, 0],
            "ncore": [0, 0],
        },
    ),
    (
        "cc-pvdz",
        "test/water.xyz",
        {"charge": 1, "ncore": 0},
        {
            "occ": [np.full((24), 1 / 4.8), np.full((24), 1 / 6)],
            "charge": 1,
            "nel": 9,
            "nbasis": [24, 24],
            "nact": [24, 24],
            "nocc": [24, 24],
            "nvirt": [0, 0],
            "nacto": [24, 24],
            "nactv": [0, 0],
            "ncore": [0, 0],
        },
    ),
    (
        "cc-pvdz",
        "test/water.xyz",
        {"charge": 1, "alpha": 1, "ncore": 1},
        {
            "occ": [np.full((24), 1 / 4.8), np.full((24), 1 / 6)],
            "charge": 1,
            "nel": 9,
            "nbasis": [24, 24],
            "nact": [23, 23],
            "nocc": [24, 24],
            "nvirt": [0, 0],
            "nacto": [23, 23],
            "nactv": [0, 0],
            "ncore": [1, 1],
        },
    ),
]

test_occ_model = [FermiOccModel]

#
# Tests for FermiOccModel
#


@pytest.mark.parametrize("basis_name,mol,kwargs,expected", test_fermi)
@pytest.mark.parametrize("occ_model_class", test_occ_model)
def test_occ_fermi_gobasis(basis_name, mol, kwargs, expected, occ_model_class):
    """Test Fermi Aufbau model for basis, charge, alpha, and ncore arguments
    as input."""
    fn_xyz = context.get_fn(mol)
    basis = get_gobasis(basis_name, fn_xyz, print_basis=False)
    lf = DenseLinalgFactory(basis.nbasis)
    # either restricted (alpha=0) or unrestricted orbitals (alpha>0)
    norbs = 1 if kwargs.get("alpha") == 0 else 2
    if kwargs.get("unrestricted", False):
        norbs = 2
    orb = [lf.create_orbital() for n in range(norbs)]

    occ_model = occ_model_class(basis, **kwargs)
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


@pytest.mark.parametrize("basis_name,mol,kwargs,expected", test_fermi)
@pytest.mark.parametrize("occ_model_class", test_occ_model)
def test_occ_fermi_lf(basis_name, mol, kwargs, expected, occ_model_class):
    """Test Fermi Aufbau model for lf, charge, alpha, and ncore arguments as
    input. We have to explicitly give ``nel`` otherwise we get an error.
    """
    # construct basis only to create some lf instance
    fn_xyz = context.get_fn(mol)
    basis = get_gobasis(basis_name, fn_xyz, print_basis=False)
    lf = DenseLinalgFactory(basis.nbasis)
    # either restricted (alpha=0) or unrestricted orbitals (alpha>0)
    norbs = 1 if kwargs.get("alpha") == 0 else 2
    if kwargs.get("unrestricted", False):
        norbs = 2
    orb = [lf.create_orbital() for n in range(norbs)]

    occ_model = occ_model_class(lf, **kwargs, nel=expected["nel"])
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
# Additional tests for FermiOccModel using lf instance
#

expected_lf_nel = {
    "occ": [np.full((8), 1 / 2)],
    "charge": 0,
    "nel": 8,
    "nbasis": [8],
    "nact": [8],
    "nocc": [8],
    "nvirt": [0],
    "nacto": [8],
    "nactv": [0],
    "ncore": [0],
}


test_fermi_lf_nel = [
    # nbasis, nel, kwargs
    (
        8,
        8,
        {"ncore": 0},
        expected_lf_nel,
    ),
]


@pytest.mark.parametrize("nbasis,nel,nocc,expected", test_fermi_lf_nel)
def test_occ_fermi_lf_nel(nbasis, nel, nocc, expected):
    """Test Fermi Aufbau model for lf, nel, and occ_a, occ_b as only input.
    Such an Aufbau model is used, for instance, in model Hamiltonians like
    Hubbard.
    """
    # construct basis only to create some lf instance
    lf = DenseLinalgFactory(nbasis)
    orb = [lf.create_orbital()]

    occ_model = FermiOccModel(lf, nel=nel, **nocc)
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
# Tests for unrestricted (open-shell) cases using FermiOccModel
#

expected_lf_nel_os = {
    "occ": [np.full((8), 5 / 8), np.full((8), 1 / 2)],
    "charge": 0,
    "nel": 9,
    "nbasis": [8, 8],
    "nact": [8, 8],
    "nocc": [8, 8],
    "nvirt": [0, 0],
    "nacto": [8, 8],
    "nactv": [0, 0],
    "ncore": [0, 0],
}


test_fermi_lf_nel_os = [
    # nbasis, nel, nocc (as kwargs)
    (8, 9, {"alpha": 1, "ncore": 0}, expected_lf_nel_os),
    (8, 9, {"unrestricted": True, "ncore": 0}, expected_lf_nel_os),
    (8, 9, {"ncore": 0}, expected_lf_nel_os),
]


@pytest.mark.parametrize("nbasis,nel,nocc,expected", test_fermi_lf_nel_os)
def test_occ_fermi_lf_os(nbasis, nel, nocc, expected):
    """Test Fermi Aufbau model for lf, nel, and occ_a, occ_b as only input.
    Such an Aufbau model is used, for instance, in model Hamiltonians like
    Hubbard.
    """
    # construct basis only to create some lf instance
    lf = DenseLinalgFactory(nbasis)
    orb = [lf.create_orbital(), lf.create_orbital()]

    occ_model = FermiOccModel(lf, nel=nel, **nocc)
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
# Invalid calls, all test should raise an error. We only consider here
# errors raised by the FermiOccModel. Other arguments are tested if the
# AufbauOccModel
#

test_molecule = [
    (
        "cc-pvdz",
        "test/water.xyz",
    ),
]


test_wrong_arguments = [
    ({"nocc_a": 0}),  # nocc_a is not used
    ({"nocc_b": 0}),  # nocc_b is not used
    ({"temperature": 0}),  # temperature has to be grater than 0
    ({"temperature": -10}),  # temperature has to be grater than 0
    ({"delta_t": -50}),  # Delta T has to be grater than or equal to 0
    ({"eps": 0}),  # Delta T has to be grater than or equal to 0
    ({"eps": -1e-8}),  # Delta T has to be grater than or equal to 0
]


@pytest.mark.parametrize("basis_name,mol", test_molecule)
@pytest.mark.parametrize("kwargs", test_wrong_arguments)
@pytest.mark.parametrize("factory", [Basis, DenseLinalgFactory])
def test_occ_fermi_arguments_gobasis(basis_name, mol, kwargs, factory):
    """Test Fermi Aufbau model for basis, nocc_a/nocc_b, and ncore arguments
    as input.
    nel is not used here
    """
    fn_xyz = context.get_fn(mol)
    basis = get_gobasis(basis_name, fn_xyz, print_basis=False)

    # maps factory class to it's fixture instance
    factory_map = {
        Basis: basis,
        DenseLinalgFactory: DenseLinalgFactory(basis.nbasis),
    }

    with pytest.raises(ArgumentError):
        assert isinstance(
            FermiOccModel(factory_map[factory], **kwargs), FermiOccModel
        )


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
            "temperature": 300,
            "delta_t": 10,
            "method": "pfon",
            "eps": 0.1,
        },
    ),
]


@pytest.mark.parametrize("basis_name,mol,kwargs", test_kwargs)
@pytest.mark.parametrize("factory", [Basis, DenseLinalgFactory])
def test_occ_fermi_kwargs(
    basis_name: str,
    mol: str,
    kwargs: dict[str, Any],
    factory: Basis | DenseLinalgFactory,
):
    """Test Fermi model for basis, nocc_a/nocc_b, and ncore arguments as
    input.
    """
    fn_xyz = context.get_fn(mol)
    basis = get_gobasis(basis_name, fn_xyz, print_basis=False)

    # maps factory class to it's fixture instance
    factory_map = {
        Basis: basis,
        DenseLinalgFactory: DenseLinalgFactory(basis.nbasis),
    }

    assert isinstance(
        FermiOccModel(factory_map[factory], **kwargs), FermiOccModel
    )


def test_ncore_with_atoms(ncore_test_with_atoms):
    """Test: automatically computes the number of
    frozen core atomic orbitals with atoms"""
    basis_name, mol, ncore = ncore_test_with_atoms
    basis = get_gobasis(basis_name, mol, print_basis=False)
    occ_model = FermiOccModel(basis)
    assert occ_model.ncore[0] == ncore


def test_ncore_with_molecule(ncore_test_with_molecule):
    """Test: automatically computes the number of
    frozen core atomic orbitals with molecule"""
    basis_name, mol, kwargs, expected = ncore_test_with_molecule
    fn_xyz = context.get_fn(mol)
    basis = get_gobasis(basis_name, fn_xyz, print_basis=False)
    occ_model = FermiOccModel(basis, **kwargs)

    assert occ_model.ncore == expected
