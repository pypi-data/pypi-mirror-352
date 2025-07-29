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
from pybest.exceptions import (
    ArgumentError,
    ElectronCountError,
    LinalgFactoryError,
)
from pybest.gbasis import Basis, get_gobasis
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import FixedOccModel

#
# Tests for AufbauOccModel
#

test_fixed = [
    # basis, molecule, kwargs (charge, #unpaired electrons (alpha), ncore)
    (
        "cc-pvdz",
        "test/water.xyz",
        {"occ_a": np.array([1, 1, 1, 1, 1]), "nel": 10, "ncore": 0},
        {
            "occ": [[1, 1, 1, 1, 1]],
            "charge": 0,
            "nel": 10,
            "nbasis": [24],
            "nact": [24],
            "nocc": [5],
            "nvirt": [19],
            "nacto": [5],
            "nactv": [19],
            "ncore": [0],
            "occ_array": [np.array([1, 1, 1, 1, 1])],
            "nspin": [5],
        },
    ),
    (
        "cc-pvdz",
        "test/water.xyz",
        {"occ_a": np.array([1, 1, 1, 1, 0, 1]), "nel": 10, "ncore": 0},
        {
            "occ": [[1, 1, 1, 1, 0, 1]],
            "charge": 0,
            "nel": 10,
            "nbasis": [24],
            "nact": [24],
            "nocc": [6],
            "nvirt": [18],
            "nacto": [6],
            "nactv": [18],
            "ncore": [0],
            "occ_array": [np.array([1, 1, 1, 1, 0, 1])],
            "nspin": [5],
        },
    ),
    (
        "cc-pvdz",
        "test/water.xyz",
        {"occ_a": np.array([1, 1, 1, 1, 0, 1]), "nel": 10, "ncore": 1},
        {
            "occ": [[1, 1, 1, 1, 0, 1]],
            "charge": 0,
            "nel": 10,
            "nbasis": [24],
            "nact": [23],
            "nocc": [6],
            "nvirt": [18],
            "nacto": [5],
            "nactv": [18],
            "ncore": [1],
            "occ_array": [np.array([1, 1, 1, 1, 0, 1])],
            "nspin": [5],
        },
    ),
    (
        "cc-pvdz",
        "test/water.xyz",
        {
            "occ_a": np.array([1, 1, 1, 1, 0, 1]),
            "occ_b": np.array([1, 1, 1, 1, 0, 0, 1]),
            "nel": 10,
            "ncore": 0,
        },
        {
            "occ": [[1, 1, 1, 1, 0, 1], [1, 1, 1, 1, 0, 0, 1]],
            "charge": 0,
            "nel": 10,
            "nbasis": [24, 24],
            "nact": [24, 24],
            "nocc": [6, 7],
            "nvirt": [18, 17],
            "nacto": [6, 7],
            "nactv": [18, 17],
            "ncore": [0, 0],
            "occ_array": [
                np.array([1, 1, 1, 1, 0, 1]),
                np.array([1, 1, 1, 1, 0, 0, 1]),
            ],
            "nspin": [5, 5],
        },
    ),
]


@pytest.mark.parametrize("basis_name,mol,kwargs,expected", test_fixed)
@pytest.mark.parametrize("factory", [Basis, DenseLinalgFactory])
def test_occ_fixed(
    basis_name: str,
    mol: str,
    kwargs: dict[str, Any],
    expected: dict[str, Any],
    factory: Basis | DenseLinalgFactory,
):
    """Test Fixed AufBau model for basis, nocc_a/nocc_b, and ncore arguments as
    input."""
    fn_xyz = context.get_fn(mol)
    basis = get_gobasis(basis_name, fn_xyz, print_basis=False)
    lf = DenseLinalgFactory(basis.nbasis)
    # either restricted (alpha=0) or unrestricted orbitals (alpha>0)
    occ_b = kwargs.get("occ_b", None)
    norbs = 1 if occ_b is None else 2
    orb = [lf.create_orbital() for n in range(norbs)]

    factory_instance = basis if factory is Basis else lf
    try:
        occ_model = FixedOccModel(factory_instance, **kwargs)
    except LinalgFactoryError:
        return True

    assert isinstance(
        occ_model, FixedOccModel
    ), "Could not create FixedOccModel instance"

    occ_model.assign_occ_reference(*orb)

    for key, value in expected.items():
        if key in ["occ", "occ_array"]:
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
    (
        # nel, needed for lf tests
        {},
        ArgumentError,
    ),  # missing arguments occ_a
    (
        {"occ_b": np.array([1, 1, 1, 1, 1])},
        ArgumentError,
    ),  # missing arguments occ_a
    (
        {"occ_a": np.array([1, 1, 1, 1, 0]), "nel": 10},
        ElectronCountError,
    ),  # occ and nel do not agree
    (
        {
            "occ_a": np.array([1, 1, 1, 1, 0, 1]),
            "occ_b": np.array([1, 1, 0, 0, 0, 1]),
            "nel": 9,
            "charge": 1,
        },
        ElectronCountError,
    ),  # nocc and nel do not agree
    (
        {
            "occ_a": np.array([1, 1, 1, 1, 0, 1]),
            "nel": 9,
            "charge": 1,
        },
        ElectronCountError,
    ),  # nocc and nel do not agree
    (
        {
            "occ_a": np.array([1, 1, 1, 1, 0, 1]),
            "nel": 8,
        },
        ElectronCountError,
    ),  # nocc and nel do not agree
]


@pytest.mark.parametrize("kwargs,error", test_wrong_arguments)
@pytest.mark.parametrize("factory", [Basis, DenseLinalgFactory])
def test_occ_fixed_arguments_gobasis(
    kwargs: Any, error: Any, factory: Basis | DenseLinalgFactory
):
    """Test Fixed occupation model for basis, nocc_a/nocc_b,
    and ncore arguments as input.
    """
    fn_xyz = context.get_fn("test/water.xyz")
    basis = get_gobasis("cc-pvdz", fn_xyz, print_basis=False)
    lf = DenseLinalgFactory(basis.nbasis)

    factory_instance = basis if factory is Basis else lf

    with pytest.raises(error):
        assert isinstance(
            FixedOccModel(factory_instance, **kwargs), FixedOccModel
        ), "Could not create FixedOccModel instance"


@pytest.mark.parametrize("factory", [Basis])
def test_occ_fixed_ncore(fixed_test_ncore, factory):
    """Check if it will automatically calculate the value of frozen core orbitals for FixedOccModel"""
    basis, mol, specific, expected = fixed_test_ncore
    fn_xyz = context.get_fn(mol)
    basis = get_gobasis(basis, fn_xyz, print_basis=False)
    lf = DenseLinalgFactory(basis.nbasis)

    factory_instance = basis if factory is Basis else lf
    occ_model = FixedOccModel(factory_instance, **{"occ_a": specific})
    assert occ_model.ncore[0] == expected
