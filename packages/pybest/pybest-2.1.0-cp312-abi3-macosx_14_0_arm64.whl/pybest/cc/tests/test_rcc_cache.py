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

"""Unit tests for RCCHamiltonianBlocks."""

import pytest

from pybest.cache import Cache
from pybest.cc.rcc_cache import RCCHamiltonianBlocks

from .common import CCMolecule, check_eri_in_cache, check_fock_in_cache

test_data = [(RCCHamiltonianBlocks, "h2o", "3-21g")]


@pytest.mark.parametrize("cls,mol_f,basis ", test_data)
def test_can_construct_hamiltonian_blocks(cls, mol_f, basis, linalg_slow):
    "Check if Hamiltonian property contains expected blocks."
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()

    one = mol_.one.copy()
    one.iadd(mol_.external)
    fock = ["fock_oo", "fock_ov", "fock_vv"]
    ham_eri = [
        "eri_oooo",
        "eri_ooov",
        "eri_oovv",
        "eri_ovov",
        "eri_ovvv",
        "eri_vvov",
    ]
    ham_exc = ["exc_oovv", "exc_ooov"]
    blocks = fock + ham_eri + ham_exc
    ham = cls(blocks, one, mol_.two, mol_.hf.orb_a, mol_.occ_model)
    assert isinstance(ham.cache, Cache)

    # Check the Fock matrix blocks
    check_fock_in_cache(ham.cache, fock, nocc=5, nvirt=8)
    # Check 2-body Hamiltonian Coulomb and exchange blocks
    check_eri_in_cache(ham.cache, ham_eri + ham_exc, nocc=5, nvirt=8)
