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

from pybest.auxmat import get_diag_fock_matrix, get_fock_matrix
from pybest.context import context
from pybest.gbasis import (
    compute_eri,
    compute_kinetic,
    compute_nuclear,
    get_gobasis,
)
from pybest.linalg import DenseLinalgFactory


def check_get_fock_matrix(basis_str, xyz, nocc):
    #
    # Run a simple HF calculation on the given IOData in the given basis
    #

    # basis instance
    basis = get_gobasis(basis_str, xyz, print_basis=False)
    lf = DenseLinalgFactory(basis.nbasis)

    # Compute Gaussian integrals
    one = compute_kinetic(basis)
    one.iadd(compute_nuclear(basis))
    er = compute_eri(basis)

    # Reference calculation
    tmp = lf.create_three_index(one.nbasis)
    fockref = lf.create_two_index(one.nbasis)
    er.contract("abcb->abc", out=tmp, factor=2.0, clear=True, select="einsum")
    er.contract("abbc->abc", out=tmp, factor=-1.0, select="einsum")
    # Done use contract function here:
    fockref.array = np.einsum("abc->ac", tmp.array[:, :nocc, :])
    fockref.iadd(one)

    # Fock matrix using get_fock_matrix function
    fock = get_fock_matrix(lf, one, er, nocc)

    # Check for consistencies
    assert fock.nbasis == fockref.nbasis
    assert np.allclose(fock.array, fockref.array)


def check_get_diag_fock_matrix(basis_str, xyz, nocc):
    #
    # Run a simple HF calculation on the given IOData in the given basis
    #

    # basis instance
    basis = get_gobasis(basis_str, xyz, print_basis=False)
    lf = DenseLinalgFactory(basis.nbasis)

    # Compute Gaussian integrals
    one = compute_kinetic(basis)
    one.iadd(compute_nuclear(basis))
    er = compute_eri(basis)

    # Reference calculation
    tmp = lf.create_two_index(one.nbasis)
    fockref = lf.create_two_index(one.nbasis)
    er.contract("abab->ab", out=tmp, factor=2.0, clear=True, select="einsum")
    er.contract("abba->ab", out=tmp, factor=-1.0, select="einsum")
    # Done use contract function here:
    fockref.array[:] = np.einsum("ab->a", tmp.array[:, :nocc])
    fockref.array[:] += one.array.diagonal()

    # Fock matrix using get_fock_matrix function
    fock = get_diag_fock_matrix(lf, one, er, nocc)

    # Check for consistencies
    assert fock.nbasis == fockref.nbasis
    assert np.allclose(fock.array, fockref.array)


test_cases = [
    ("ne", "cc-pvdz", 5),
    ("water", "cc-pvdz", 5),
    ("2h-azirine", "cc-pvdz", 11),
]


@pytest.mark.parametrize("mol, basis, nocc", test_cases)
def test_get_fock_matrix(mol, basis, nocc):
    mol_fn = context.get_fn(f"test/{mol}.xyz")
    check_get_fock_matrix(basis, mol_fn, nocc)


@pytest.mark.parametrize("mol, basis, nocc", test_cases)
def test_get_diag_fock_matrix(mol, basis, nocc):
    mol_fn = context.get_fn(f"test/{mol}.xyz")
    check_get_diag_fock_matrix(basis, mol_fn, nocc)
