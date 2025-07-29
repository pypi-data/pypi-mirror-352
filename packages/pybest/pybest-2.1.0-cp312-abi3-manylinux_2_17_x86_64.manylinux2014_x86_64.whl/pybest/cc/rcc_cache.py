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
"""RCCHamiltonianBlocks class"""

import gc
from functools import partial
from typing import Any

from pybest.auxmat import get_fock_matrix
from pybest.cache import Cache
from pybest.exceptions import NonEmptyData
from pybest.linalg import (
    CholeskyFourIndex,
    DenseFourIndex,
    DenseTwoIndex,
)
from pybest.utility import (
    check_options,
    split_core_active,
    transform_integrals,
)

__all__ = ["RCCHamiltonianBlocks"]


class RCCHamiltonianBlocks:
    """Construct and store non-redundant blocks of Fock matrix and electron
    repulsion integrals that are used in RCC module. All the requested blocks
    are constructed during initialization and kept in the Cache instance.

    A type of a block is denoted using "o" or "v" characters that stand for
    "occupied" or "virtual" block.

    The implemented blocks (x = o or v):
        * fock_xx - Fock matrix blocks
        * eri_xxxx - Electron repulsion integrals in MO basis blocks
        * exc_oovv - <ijab> - 2 <ijba>
        * exc_ooov = <ijka> - 2 <ikja>

    """

    def __init__(self, *args: Any) -> None:
        """Transforms and saves CC Hamiltonian blocks in cache.

        Arguments:
        blocks : list of strings
            Contains abbreviations of a block type. For example:
             - "fock_oo" for occupied-occupied block of a Fock matrix
             - "eri_ovov" for occupied-virtual-occupied-virtual block of
              electron repulsion integrals in MO basis
             - "exc_ooov" for some exchange-type electron repulsion integrals

        one_body_ham : DenseTwoIndex
            Sum over one-body elements of the electronic Hamiltonian in AO
            basis, e.g., kinetic energy, nuclei-electron attraction energy

        two_body_ham : DenseFourIndex
            Sum over all two-body elements of the electronic Hamiltonian in AO
            basis, e.g., electron repulsion integrals.

        mos : DenseOrbital
            Molecular orbitals, e.g., RHF or pCCD orbitals.

        occ_model: AufbauOccupation model
            an Aufbau occupation model
        """
        # Transform integrals
        blocks, _, _, _, occ_model = args
        ham_mo = self.transform_integrals(*args[1:])
        ham_2 = ham_mo["ham_2"]
        self.e_core = ham_mo["e_core"]
        fock = DenseTwoIndex(occ_model.nacto[0] + occ_model.nactv[0])
        fock = get_fock_matrix(
            fock, ham_mo["ham_1"], ham_2, occ_model.nacto[0]
        )
        self.cache = Cache()

        def get_range(string: str) -> dict[str, Any]:
            """Returns a dictionary with keys beginX, endX, begin(X+1), etc.

            Arguments:
                string : string
                    any sequence of "o" (occupied) and "v" (virtual)
            """
            ranges = {}
            for ind, char in enumerate(string):
                if char == "o":
                    ranges[f"begin{ind}"] = 0
                    ranges[f"end{ind}"] = occ_model.nacto[0]
                elif char == "v":
                    ranges[f"begin{ind}"] = occ_model.nacto[0]
                    ranges[f"end{ind}"] = (
                        occ_model.nacto[0] + occ_model.nactv[0]
                    )
            return ranges

        def alloc(string: str, arr: DenseFourIndex) -> tuple[partial[Any]]:
            """Determines alloc argument for cache.load method."""
            # We keep one whole CholeskyFourIndex to rule them all.
            # Non-redundant blocks are accessed as views.
            if isinstance(arr, CholeskyFourIndex):
                return (partial(arr.view, **get_range(string)),)
            # But we store only non-redundant blocks of DenseFourIndex
            return (partial(arr.copy, **get_range(string)),)

        # Blocks of the Fock matrix
        for block in [x for x in blocks if x.startswith("fock")]:
            self.init_block(block, alloc=alloc(block.split("_")[1], fock))

        # Blocks of two-body Hamiltonian
        for block in [x for x in blocks if x.startswith("eri")]:
            self.init_block(block, alloc=alloc(block.split("_")[1], ham_2))

        # Exchange-type terms from CC equations
        def alloc_exc(string: str, arr: DenseFourIndex) -> tuple[partial[Any]]:
            """Determines alloc argument for cache.load method."""
            kwargs = get_range(string)
            return (partial(arr.contract, "abcd->abcd", **kwargs),)

        exc_transpose = {"ooov": (0, 2, 1, 3), "oovv": (0, 1, 3, 2)}
        for block in [x.split("_")[1] for x in blocks if x.startswith("exc_")]:
            mat = self.init_block(
                f"exc_{block}", alloc=alloc_exc(block, ham_2)
            )
            mat.iadd_transpose(exc_transpose[block], factor=-2)

        ham_2.__del__()
        gc.collect()

    def get(self, block: Any) -> Any:
        """Get a matrix/tensor from the cache.

        **Arguments:**

        block
            (str) some object stored in the Cache.
        """
        # TODO: allow to get transpositions of blocks
        if block in self.cache:
            return self.cache.load(block)
        raise NotImplementedError

    @staticmethod
    def transform_integrals(ham_1_ao, ham_2_ao, mos, occ_model):
        """Transforms one- and two-body integrals to Fock matrix and ERI
        im MO basis.

        Arguments:
        one_body_ham : DenseTwoIndex
            Sum of one-body elements of the electronic Hamiltonian in AO
            basis, e.g., kinetic energy, nuclei-electron attraction energy

        two_body_ham : DenseFourIndex
            Sum of two-body elements of the electronic Hamiltonian in AO
            basis (electron repulsion integrals).

        mos : DenseOrbital
            Molecular orbitals, e.g., RHF or pCCD orbitals.

        occ_model: IOData
            Instance of IOData container that contains the output of coupled cluster calculation.
            Contained are occupied/virtual/active/etc. orbitals information
        """
        # TODO: delete
        nbasis = occ_model.nacto[0] + occ_model.nactv[0]
        # If we have frozen core orbitals
        if ham_1_ao.shape != (nbasis, nbasis) or occ_model.ncore[0] != 0:
            ints = split_core_active(
                ham_1_ao, ham_2_ao, mos, e_core=0.0, ncore=occ_model.ncore[0]
            )
            return {
                "ham_1": ints.one,
                "ham_2": ints.two,
                "e_core": ints.e_core,
            }
        # If there is no frozen core
        ints = transform_integrals(ham_1_ao, ham_2_ao, mos)
        return {"ham_1": ints.one[0], "ham_2": ints.two[0], "e_core": 0.0}

    def init_block(self, select: str, **kwargs: dict[str, Any]) -> Any:
        """Initialize blocks in cache

        **Arguments:**

        select

            (str) label of the auxiliary tensor

        **Keyword Arguments:**

        tags
            The tag used for storing some matrix/tensor in the Cache (default
            `h`).

        alloc
            Specify alloc function explicitly. If not defined some flavor of
            `self.lf.create_N_index` is taken depending on the length of args.

        """
        for name in kwargs:
            check_options(name, name, "tags", "alloc")
        tags = kwargs.get("tags", "h")
        alloc = kwargs.get("alloc", None)
        # load into the cache
        matrix, new = self.cache.load(select, alloc=alloc, tags=tags)
        if not new:
            raise NonEmptyData(
                f"The Cache instance {select} already exists. "
                "Call clear prior to updating the Cache instance."
            )

        return matrix

    def clear(self, **kwargs: dict[str, Any]) -> None:
        """Clear the Cache instance

        **Keyword arguments:**

        tags
             The tag used for storing some matrix/tensor in the Cache (default
             `h`).
        """
        for name in kwargs:
            check_options(name, name, "tags")
        tags = kwargs.get("tags", "h")
        self.cache.clear(tags=tags, dealloc=True)
