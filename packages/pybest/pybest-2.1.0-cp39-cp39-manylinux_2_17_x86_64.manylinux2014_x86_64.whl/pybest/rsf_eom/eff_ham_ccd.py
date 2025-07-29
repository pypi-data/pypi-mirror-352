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
# This file has been written by Emil Sujkowski (original version)

"""RCC Effective Hamiltonian class

Variables used in this module:
:nocc:      number of occupied orbitals in the principle configuration
:nvirt:     number of virtual orbitals in the principle configuration
:nbasis:    total number of basis functions

Indexing convention:
:i,j,k,..: occupied alpha orbitals of principle configuration
:I,J,K,..: occupied beta orbitals of principle configuration
:a,b,c,..: virtual alpha orbitals of principle configuration
"""

from __future__ import annotations

import gc
from functools import partial
from typing import Any

from pybest.cache import Cache
from pybest.cc.rcc_cache import RCCHamiltonianBlocks
from pybest.exceptions import ArgumentError, NonEmptyData
from pybest.iodata import IOData
from pybest.linalg import DenseFourIndex
from pybest.linalg.cholesky import CholeskyFourIndex
from pybest.utility import (
    check_options,
    unmask_onebody_hamiltonian,
    unmask_orb,
    unmask_twobody_hamiltonian,
)


class EffectiveHamiltonianRCCD:
    """Effective Hamiltonian Restricted Coupled Cluster Doubles class"""

    def __init__(self, *args: Any) -> None:
        """Compute effective Hamiltonian term for RCCD

        Arguments:
        ham_1_ao : DenseTwoIndex
            Sum of one-body elements of the electronic Hamiltonian in AO
            basis, e.g., kinetic energy, nuclei--electron attraction energy

        ham_2_ao : DenseFourIndex
            Sum of two-body elements of the electronic Hamiltonian in AO
            basis, e.g., electron repulsion integrals.

        mos : DenseOrbital
            Molecular orbitals, e.g., RHF orbitals or pCCD orbitals.

        rcc : IOData container
        """
        orb_a = unmask_orb(*args)[0]
        ham_1_ao = unmask_onebody_hamiltonian(args)
        ham_2_ao = unmask_twobody_hamiltonian(args)
        rccd = self.unmask_rcc(args)
        self.occ_model = rccd.occ_model
        blocks = [
            "fock_oo",
            "fock_ov",
            "fock_vv",
            "eri_oooo",
            "eri_oovv",
            "eri_vovo",
            "eri_vovv",
            "eri_vvvv",
        ]

        self.cache = Cache()
        self.ham = RCCHamiltonianBlocks(
            blocks, ham_1_ao, ham_2_ao, orb_a, self.occ_model
        )

        self.build_two_body_I(rccd)
        self.build_one_body_I(rccd)
        self.ham.cache.clear(dealloc=True)
        ham_2_ao.dump_array("eri", "checkpoint_eri.h5")

    def build_one_body_I(self, rccd: IOData) -> None:
        """One-body effective Hamiltonian terms use the same intermediates,
        so we construct them in one method.
        The effective Hamiltonian blocks currently supported:
          * I_oo
          * I_VV

        Arguments:
            rccd : IOData container that contains the output of coupled cluster calculation
        """
        t_2 = rccd.t_2
        f_oo = self.ham.get("fock_oo")
        f_vv = self.ham.get("fock_vv")
        e_oovv = self.ham.get("eri_oovv")

        I_VV = self.init_block("I_VV", alloc=f_vv.copy)

        # - L<km|cd> * t_km^bd
        e_oovv.contract("abcd,aebd->ec", t_2, out=I_VV, factor=-2)
        e_oovv.contract("abdc,aebd->ec", t_2, out=I_VV)

        I_oo = self.init_block("I_oo", alloc=f_oo.copy)
        I_oo.iscale(-1)

        # - L<km|cd> * t_kj^cd
        e_oovv.contract("abcd,aced->be", t_2, out=I_oo, factor=-2)
        e_oovv.contract("abdc,aced->be", t_2, out=I_oo)

    def build_two_body_I(self, rccd: IOData) -> None:
        """Two-body effective Hamiltonian terms use the same intermediates,
        so we construct them in one method.
        The effective Hamiltonian blocks currently supported:
          * I_oooo
          * I_VVVV
          * I_VoVo

        Arguments:
            rccd : IOData container that contains the output of coupled cluster calculation
        """

        def get_range(string: str) -> dict[str, int]:
            """Returns a dictionary with keys beginX, endX, begin(X+1), etc.

            Arguments:
                string : string
                    any sequence of "o" (occupied) and "v"/"V" (virtual)
                    "v" starts with nacto,
                    "V" starts with 0, both have the same dimension
            """
            ranges = {}
            for ind, char in enumerate(string):
                if char == "o":
                    ranges[f"begin{ind}"] = 0
                    ranges[f"end{ind}"] = self.occ_model.nacto[0]
                elif char == "v":
                    ranges[f"begin{ind}"] = self.occ_model.nacto[0]
                    ranges[f"end{ind}"] = (
                        self.occ_model.nacto[0] + self.occ_model.nactv[0]
                    )
                elif char == "V":
                    ranges[f"begin{ind}"] = 0
                    ranges[f"end{ind}"] = self.occ_model.nactv[0]
            return ranges

        def alloc_cholesky(
            string: str, arr: CholeskyFourIndex
        ) -> tuple[partial[CholeskyFourIndex]]:
            """Returns a view of CholeskyFourIndex array"""
            # We keep one whole CholeskyFourIndex to rule them all.
            # Non-redundant blocks are accessed as views.
            return (partial(arr.view, **get_range(string)),)

        def alloc(
            array: DenseFourIndex, factor: int = 1
        ) -> partial[DenseFourIndex]:
            """Defines a function that allocates a DenseFourIndex object."""
            return partial(array.contract, "abcd->abcd", factor=factor)

        def dealloc_if_dense(array: DenseFourIndex, label: str) -> None:
            """Removes dense objects from cache."""
            if isinstance(array, DenseFourIndex):
                self.ham.cache.clear_item(label, dealloc=True)

        # RCCD amplitudes
        t_2 = rccd.t_2

        gc.collect()
        e_vvvv = self.ham.get("eri_vvvv")
        e_oovv = self.ham.get("eri_oovv")

        if isinstance(e_vvvv, CholeskyFourIndex):
            self.init_block("e_vvvv", alloc=alloc_cholesky("VVVV", e_vvvv))
            self.init_block(
                "e_vovv",
                alloc=alloc_cholesky("VoVV", self.ham.get("eri_vovv")),
            )
            self.init_block("e_oovv", alloc=alloc_cholesky("ooVV", e_oovv))
        else:
            I_VVVV = self.init_block("I_VVVV", alloc=alloc(e_vvvv))
            # 1/2 * <ab||cd>
            I_VVVV.iscale(0.5)
            e_vvvv.contract("abcd->abdc", out=I_VVVV, factor=-0.5)
            dealloc_if_dense(e_vvvv, "eri_vvvv")
            gc.collect()

            # 1/2 <km||cd> * t_km^ab
            e_oovv.contract("abcd,aebf->efcd", t_2, out=I_VVVV, factor=0.5)
            e_oovv.contract("abdc,aebf->efcd", t_2, out=I_VVVV, factor=-0.5)

        e_vovo = self.ham.get("eri_vovo")
        I_VoVo = self.init_block("I_VoVo", alloc=alloc(e_vovo))
        I_VoVo.iscale(-1)

        # <kc|dm> * t_jm^db => <km|dc> * t_jm^db
        e_oovv.contract("abcd,ecbf->fade", t_2, out=I_VoVo)

        e_oooo = self.ham.get("eri_oooo")
        I_oooo = self.init_block("I_oooo", alloc=alloc(e_oooo))

        # 1/2 <km||ij>
        I_oooo.iscale(0.5)
        e_oooo.contract("abcd->abdc", out=I_oooo, factor=-0.5)

        # 1/2 <km||cd> * t_ij^cd
        e_oovv.contract("abcd,ecfd->abef", t_2, out=I_oooo, factor=0.5)
        e_oovv.contract("bacd,ecfd->abef", t_2, out=I_oooo, factor=-0.5)

    def init_block(
        self, select: str, **kwargs: Any
    ) -> DenseFourIndex | CholeskyFourIndex:
        """Initialize blocks in cache

        **Arguments:**

        select

            (str) label of the auxiliary tensor

        **Keyword Arguments:**

        alloc
            Specify alloc function explicitly. If not defined some flavor of
            `self.lf.create_N_index` is taken depending on the length of args.
        """
        for name, _ in kwargs.items():
            check_options(name, name, "alloc")
        alloc = kwargs.get("alloc", None)
        matrix, new = self.cache.load(select, alloc=alloc, tags="EOM")
        if not new:
            raise NonEmptyData(
                f"The Cache instance {select} already exists. "
                "Call clear prior to updating the Cache instance."
            )
        return matrix

    def unmask_rcc(self, args: Any) -> IOData:
        """Return an instance of the IOData container that contains
        the output of coupled cluster calculation
        """
        for arg in args:
            if hasattr(arg, "amplitudes") and hasattr(arg, "e_ref"):
                self._e_ref = arg.e_ref
                return arg
            if hasattr(arg, "t_2") and hasattr(arg, "e_ref"):
                self._e_ref = arg.e_ref
                return arg
        raise ArgumentError("The RCCD amplitudes were not found!")
