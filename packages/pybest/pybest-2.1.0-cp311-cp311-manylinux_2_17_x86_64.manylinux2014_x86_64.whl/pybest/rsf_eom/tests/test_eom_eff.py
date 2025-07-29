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
# The RSF-CC sub-package has been originally written and updated by Aleksandra Leszczyk (see CHANGELOG)
# Its current version contains updates from the PyBEST developer team.
#
# 2023/24:
# This file has been updated by Emil Sujkowski

"""Unit tests for RCCHamiltonianBlocks."""

from __future__ import annotations

import numpy as np

from pybest.cache import Cache
from pybest.cc import RCCSD
from pybest.linalg import (
    CholeskyLinalgFactory,
    DenseLinalgFactory,
    DenseTwoIndex,
    FourIndex,
)
from pybest.rsf_eom.eff_ham_ccsd import EffectiveHamiltonianRCCSD
from pybest.rsf_eom.tests.common import RSF_EOM_CCMolecule


def check_one_in_cache(
    cache: Cache, labels: str, nocc: int = 5, nvirt: int = 8
) -> None:
    "Checks if labels correspond to Fock matrix blocks in cache."
    dim = {"o": nocc, "V": nvirt}
    for label in labels:
        msg = f"{label} block in cc.hamiltonian: \n"
        matrix = cache.load(label)
        assert isinstance(matrix, DenseTwoIndex), msg + "incorrect type"
        assert matrix.shape[0] == dim[label[-2]], msg + "incorrect size"
        assert matrix.shape[1] == dim[label[-1]], msg + "incorrect size"
        # occupied-virtual block for RHF orbitals is zeros by nature
        if not label == "fock_ov":
            is_zeros = np.allclose(matrix.array, np.zeros(matrix.shape))
            assert not is_zeros, msg + " is filled with zeros!"


def check_two_in_cache(
    cache: Cache, labels: str, nocc: int = 5, nvirt: int = 8
) -> None:
    "Checks if labels correspond to 2-body CC Hamiltonian blocks in cache."
    dim = {"o": nocc, "V": nvirt}
    for label in labels:
        msg = f"Checking {label} block in cc.hamiltonian...\n"
        matrix = cache.load(label)
        assert isinstance(matrix, FourIndex), msg + "wrong type!"
        for i in range(4):
            assert matrix.shape[i] == dim[label[i - 4]], msg + "incorrect size"
        assert not np.allclose(matrix.array, np.zeros(matrix.array.shape))
        assert not np.isnan(matrix.array).any()


def test_can_construct_effective_hamiltonian_blocks(
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
) -> None:
    "Check if Hamiltonian property contains expected blocks."

    mol_f = "h2o"
    basis = "3-21g"

    mol_ = RSF_EOM_CCMolecule(mol_f, basis, linalg, ncore=0)
    mol_.do_rhf()
    mol_.do_rxcc([RCCSD], "pbqn")

    blocks = ["I_oo", "I_VV", "I_VVVV", "I_VoVo", "I_oooo"]
    if isinstance(mol_.lf, CholeskyLinalgFactory):
        blocks.pop(2)
    ham = EffectiveHamiltonianRCCSD(mol_.one, mol_.two, mol_.orb[0], mol_.cc)
    assert isinstance(ham.cache, Cache)

    # Check Fock matrix blocks
    check_one_in_cache(ham.cache, blocks[:2], nocc=5, nvirt=8)
    # Check 2-body Hamiltonian blocks and exchange blocks
    check_two_in_cache(ham.cache, blocks[2:], nocc=5, nvirt=8)
