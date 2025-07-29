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
from pybest.occ_model import FractionalOccModel

test_fractional_aufbau = [
    # basis, molecule, charge, #unpaired electrons (alpha), ncore
    (
        "cc-pvdz",
        "test/water.xyz",
        {"nocc_a": 5.9, "nocc_b": 4.1, "ncore": 0},
        {
            "occ": [[1, 1, 1, 1, 1, 0.9], [1, 1, 1, 1, 0.1]],
            "charge": 0,
            "nel": 10,
            "nbasis": [24, 24],
            "nact": [24, 24],
            "nocc": [6, 5],
            "nvirt": [18, 19],
            "nacto": [6, 5],
            "nactv": [18, 19],
            "ncore": [0, 0],
            "nspin": [5.9, 4.1],
        },
    ),
    (
        "cc-pvdz",
        "test/water.xyz",
        {"nocc_a": 5.9, "nocc_b": 4.1, "ncore": 0},
        {
            "occ": [[1, 1, 1, 1, 1, 0.9], [1, 1, 1, 1, 0.1]],
            "charge": 0,
            "nel": 10,
            "nbasis": [24, 24],
            "nact": [24, 24],
            "nocc": [6, 5],
            "nvirt": [18, 19],
            "nacto": [6, 5],
            "nactv": [18, 19],
            "ncore": [0, 0],
            "nspin": [5.9, 4.1],
        },
    ),
    (
        "cc-pvdz",
        "test/water.xyz",
        {"nocc_a": 5.5, "nocc_b": 4.5, "ncore": 0},
        {
            "occ": [[1, 1, 1, 1, 1, 0.5], [1, 1, 1, 1, 0.5]],
            "charge": 0,
            "nel": 10,
            "nbasis": [24, 24],
            "nact": [24, 24],
            "nocc": [6, 5],
            "nvirt": [18, 19],
            "nacto": [6, 5],
            "nactv": [18, 19],
            "ncore": [0, 0],
            "nspin": [5.5, 4.5],
        },
    ),
    (
        "cc-pvdz",
        "test/water.xyz",
        {"nocc_a": 7.1, "nocc_b": 2.9, "ncore": 0},
        {
            "occ": [[1, 1, 1, 1, 1, 1, 1, 0.1], [1, 1, 0.9]],
            "charge": 0,
            "nel": 10,
            "nbasis": [24, 24],
            "nact": [24, 24],
            "nocc": [8, 3],
            "nvirt": [16, 21],
            "nacto": [8, 3],
            "nactv": [16, 21],
            "ncore": [0, 0],
            "nspin": [7.1, 2.9],
        },
    ),
    (
        "cc-pvdz",
        "test/water.xyz",
        {"nocc_a": 7.1, "nocc_b": 2.9, "ncore": 2},
        {
            "occ": [[1, 1, 1, 1, 1, 1, 1, 0.1], [1, 1, 0.9]],
            "charge": 0,
            "nel": 10,
            "nbasis": [24, 24],
            "nact": [22, 22],
            "nocc": [8, 3],
            "nvirt": [16, 21],
            "nacto": [6, 1],
            "nactv": [16, 21],
            "ncore": [2, 2],
            "nspin": [7.1, 2.9],
        },
    ),
    (
        "cc-pvdz",
        "test/no.xyz",
        {"nocc_a": 7.5, "ncore": 0},
        {
            "occ": [[1, 1, 1, 1, 1, 1, 1, 0.5]],
            "charge": 0,
            "nel": 15,
            "nbasis": [28],
            "nact": [28],
            "nocc": [8],
            "nvirt": [20],
            "nacto": [8],
            "nactv": [20],
            "ncore": [0],
            "nspin": [7.5],
        },
    ),
    (
        "cc-pvdz",
        "test/no.xyz",
        {"nocc_a": 7.5, "unrestricted": True, "ncore": 0},
        {
            "occ": [[1, 1, 1, 1, 1, 1, 1, 0.5], [1, 1, 1, 1, 1, 1, 1, 0.5]],
            "charge": 0,
            "nel": 15,
            "nbasis": [28, 28],
            "nact": [28, 28],
            "nocc": [8, 8],
            "nvirt": [20, 20],
            "nacto": [8, 8],
            "nactv": [20, 20],
            "ncore": [0, 0],
            "nspin": [7.5, 7.5],
        },
    ),
    (
        "cc-pvdz",
        "test/no.xyz",
        {"nocc_a": 7.5, "nocc_b": 7.5, "ncore": 0},
        {
            "occ": [[1, 1, 1, 1, 1, 1, 1, 0.5], [1, 1, 1, 1, 1, 1, 1, 0.5]],
            "charge": 0,
            "nel": 15,
            "nbasis": [28, 28],
            "nact": [28, 28],
            "nocc": [8, 8],
            "nvirt": [20, 20],
            "nacto": [8, 8],
            "nactv": [20, 20],
            "ncore": [0, 0],
            "nspin": [7.5, 7.5],
        },
    ),
    (
        "cc-pvdz",
        "test/no.xyz",
        {"nocc_a": 6.5, "nocc_b": 6.5, "charge": 2, "ncore": 0},
        {
            "occ": [[1, 1, 1, 1, 1, 1, 0.5], [1, 1, 1, 1, 1, 1, 0.5]],
            "charge": 2,
            "nel": 13,
            "nbasis": [28, 28],
            "nact": [28, 28],
            "nocc": [7, 7],
            "nvirt": [21, 21],
            "nacto": [7, 7],
            "nactv": [21, 21],
            "ncore": [0, 0],
            "nspin": [6.5, 6.5],
        },
    ),
]


@pytest.mark.parametrize(
    "basis_name,mol,kwargs,expected", test_fractional_aufbau
)
@pytest.mark.parametrize("factory", [Basis, DenseLinalgFactory])
def test_occ_fractional_aufbau(basis_name, mol, kwargs, expected, factory):
    """Test fractional occupation model for basis, nocc_a/nocc_b, and ncore
    arguments as input."""
    fn_xyz = context.get_fn(mol)
    basis = get_gobasis(basis_name, fn_xyz, print_basis=False)
    lf = DenseLinalgFactory(basis.nbasis)
    # either restricted (alpha=0) or unrestricted orbitals (alpha>0)
    norbs = len(expected["nbasis"])
    orb = [lf.create_orbital() for n in range(norbs)]

    # maps factory class to it's fixture instance
    factory_map = {
        Basis: basis,
        DenseLinalgFactory: DenseLinalgFactory(basis.nbasis),
    }

    occ_model = FractionalOccModel(factory_map[factory], **kwargs)
    occ_model.assign_occ_reference(*orb)

    assert isinstance(occ_model, FractionalOccModel)

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
    (
        "cc-pvdz",
        "test/water.xyz",
        10,  # nel, needed for lf tests
        {},
        ArgumentError,
    ),  # missing arguments nocc_a
    (
        "cc-pvdz",
        "test/water.xyz",
        10,  # nel, needed for lf tests
        {"nocc_b": 5.1},
        ArgumentError,
    ),  # missing arguments nocc_a
    (
        "cc-pvdz",
        "test/water.xyz",
        10,  # nel, needed for lf tests
        {"nocc_a": 4.1, "nocc_b": 5.1},
        ElectronCountError,
    ),  # nocc_a < nocc_b
    (
        "cc-pvdz",
        "test/water.xyz",
        10,  # nel, needed for lf tests
        {"nocc_a": 4},
        ElectronCountError,
    ),  # nocc_a does not agree with nel
    (
        "cc-pvdz",
        "test/water.xyz",
        10,  # nel, needed for lf tests
        {"nocc_a": 5.5, "nocc_b": 5.5},
        ElectronCountError,
    ),  # nocc_a/nocc_b does not agree with nel
    (
        "cc-pvdz",
        "test/water.xyz",
        10,  # nel, needed for lf tests
        {"nocc_a": 5.5},
        ElectronCountError,
    ),  # nocc_a/nocc_b does not agree with nel
    (
        "cc-pvdz",
        "test/water.xyz",
        10,  # nel, needed for lf tests
        {"nocc_a": 5.5, "nocc_b": 4.5, "unrestricted": False, "ncore": 0},
        ConsistencyError,
    ),  # wrongly enforce restricted occupation
    (
        "cc-pvdz",
        "test/water.xyz",
        8,  # nel, needed for lf tests since charge is not used
        {"nocc_a": 5, "nocc_b": 4, "charge": 2},
        ElectronCountError,
    ),  # charge/nel does not agree with nocc_a/nocc_b
    (
        "cc-pvdz",
        "test/water.xyz",
        10,  # nel, needed for lf tests
        {"nocc_a": 5.5, "nocc_b": 4.5, "foo": False},
        ArgumentError,
    ),  # unknown kwargs
    (
        "cc-pvdz",
        "test/water.xyz",
        10,  # nel, needed for lf tests
        {"nocc_a": 5.5, "nocc_b": 4.5, "alpha": False},
        ArgumentError,
    ),  # alpha cannot be used here
]


@pytest.mark.parametrize(
    "basis_name,mol,nel,kwargs,error", test_wrong_arguments
)
def test_occ_fractional_arguments_gobasis(basis_name, mol, nel, kwargs, error):
    """Test fractional occupation model for basis, nocc_a/nocc_b, and ncore
    arguments as input.
    nel is not used here
    """
    fn_xyz = context.get_fn(mol)
    basis = get_gobasis(basis_name, fn_xyz, print_basis=False)

    with pytest.raises(error):
        assert FractionalOccModel(basis, **kwargs)


@pytest.mark.parametrize(
    "basis_name,mol,nel,kwargs,error", test_wrong_arguments
)
def test_occ_fractional_arguments_lf(basis_name, mol, nel, kwargs, error):
    """Test fractional occupation model for basis, nocc_a/nocc_b, and ncore
    arguments as input."""
    fn_xyz = context.get_fn(mol)
    basis = get_gobasis(basis_name, fn_xyz, print_basis=False)
    lf = DenseLinalgFactory(basis.nbasis)

    with pytest.raises(error):
        assert isinstance(
            FractionalOccModel(lf, **kwargs, nel=nel), FractionalOccModel
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
            "charge": 0,
            "nel": 10,
            "ncore": 0,
            "nocc_a": 5,  # also works with integer occupations
            "nocc_b": 5,
        },
    ),
]


@pytest.mark.parametrize("basis_name,mol,kwargs", test_kwargs)
@pytest.mark.parametrize("factory", [Basis, DenseLinalgFactory])
def test_occ_fractional_kwargs(basis_name, mol, kwargs, factory):
    """Test fractional occupation model for basis, nocc_a/nocc_b, and ncore arguments as
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
        FractionalOccModel(factory_map[factory], **kwargs), FractionalOccModel
    )


@pytest.mark.parametrize("factory", [Basis])
def test_fixed_ncore(ncore_test_with_atoms, factory):
    """Test: automatically computes the number of
    frozen core atomic orbitals with atoms"""

    basis_name, mol, expected = ncore_test_with_atoms
    basis = get_gobasis(basis_name, mol, print_basis=False)

    # maps factory class to it's fixture instance
    factory_map = {Basis: basis}
    (nocc_a,) = basis.atom
    occ_model = FractionalOccModel(
        factory_map[factory], **{"nocc_a": nocc_a, "nocc_b": 0}
    )
    assert occ_model.ncore[0] == expected
