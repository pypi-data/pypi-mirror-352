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
"""Electron Affinity Equation of Motion Coupled Cluster implementations for
   a pCCD reference function

   Variables used in this module:
    :ncore:     number of frozen core orbitals
    :nocc:      number of occupied orbitals in the principle configuration
    :nacto:     number of active occupied orbitals in the principle configuration
    :nvirt:     number of virtual orbitals in the principle configuration
    :nactv:     number of active virtual orbitals in the principle configuration
    :nbasis:    total number of basis functions
    :nact:      total number of active orbitals (nacto+nactv)
    :alpha:     the number of unpaired electrons, determines s_z
    :e_ea:      the energy correction for EA
    :civ_ea:    the CI amplitudes from a EA-EOM-pCCD model

    Indexing convention:
     :i,j,k,..: occupied orbitals of principal configuration (alpha spin)
     :a,b,c,..: virtual orbitals of principal configuration (alpha spin)
     :p,q,r,..: general indices (occupied, virtual; alpha spin)
     :I,J,K,..: occupied orbitals of principal configuration (beta spin)
     :A,B,C,..: virtual orbitals of principal configuration (beta spin)
     :P,Q,R,..: general indices (occupied, virtual; beta spin)

This module has been written by:
2023: Katharina Boguslawski
"""

from functools import partial
from typing import Any

from pybest.auxmat import get_fock_matrix
from pybest.ea_eom.sea_base import RSEACC3
from pybest.linalg import (
    CholeskyFourIndex,
    DenseOneIndex,
    DenseTwoIndex,
    FourIndex,
)
from pybest.log import timer


class REApCCD3(RSEACC3):
    """Restricted Single Electron Affinity Equation of Motion Coupled Cluster
    class restricted to Single EA for a pCCD reference function and 3 unpaired
    electrons (m_s = 1.5)

    This class defines only the function that are unique for the EA-pCCD model
    with 1 unpaired electron:

        * set_hamiltonian (calculates effective Hamiltonian -- at most O(o2v2))
        * compute_h_diag (pre-conditioner used by Davidson)
        * build_subspace_hamiltonian (subspace to be diagonalized)
    """

    acronym = "EA-EOM-pCCD"
    long_name = "Restricted Electron Affinity Equation of Motion pair Coupled Cluster Doubles"
    cluster_operator = "Tp"
    particle_hole_operator = "2p1h"
    reference = "pCCD"
    order = "EA"
    alpha = 3

    @timer.with_section("EApCCD3: H_diag")
    def compute_h_diag(self, *args: Any) -> DenseOneIndex:
        """Used by Davidson module for pre-conditioning

        **Arguments:**

        args:
            required for Davidson module (not used here)
        """
        h_diag = self.lf.create_one_index(self.dimension, "h_diag")
        #
        # Get auxiliary matrices
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        x9bc = self.from_cache("x9bc")
        x11jk = self.from_cache("x11jk")
        gvvvv = self.from_cache("gvvvv")
        #
        # get intermediates
        #
        labab = gvvvv.contract("abab->ab")
        gvvvv.contract("abba->ab", labab, factor=-1.0)
        x8ajck = self.from_cache("x8ajck")
        x8bj = x8ajck.contract("abab->ab")
        if self.dump_cache:
            self.cache.dump("x8ajck")
        #
        # rabJ
        #
        rabJ = self.lf.create_three_index(nactv, nactv, nacto)
        #
        # x9bc(b,b)
        #
        x9bc.expand("bb->abc", rabJ)
        #
        # x11jk(j,j)
        #
        x11jk.expand("cc->abc", rabJ, factor=0.5)
        #
        # ab||ab
        #
        labab.expand("ab->abc", rabJ, factor=0.25)
        #
        # x8ajck(b,j,b,j)
        #
        x8bj.expand("bc->abc", rabJ)
        #
        # P(ab)
        rabJ.iadd_transpose((1, 0, 2))
        #
        # assign using mask
        #
        h_diag.assign(rabJ.array[self.get_mask(0)])
        return h_diag

    @timer.with_section("EApCCD3: H_sub")
    def build_subspace_hamiltonian(
        self, b_vector: DenseOneIndex, h_diag: DenseOneIndex, *args: Any
    ) -> DenseOneIndex:
        """
        Used by Davidson module to construct subspace Hamiltonian

        **Arguments:**

        b_vector:
            (OneIndex object) contains current approximation to CI coefficients

        h_diag:
            Diagonal Hamiltonian elements required in Davidson module (not used
            here)

        args:
            Set of arguments passed by the Davidson module (not used here)
        """
        #
        # Get auxiliary matrices
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        x9bc = self.from_cache("x9bc")
        x11jk = self.from_cache("x11jk")
        gvvvv = self.from_cache("gvvvv")
        #
        # Calculate sigma vector (H.bvector)_kc
        #
        # output
        s_3 = self.lf.create_three_index(nactv, nactv, nacto)
        to_s_3 = {"out": s_3, "clear": False}
        # input
        b_3 = self.lf.create_three_index(nactv, nactv, nacto)
        #
        # assign rabJ
        #
        b_3.assign(b_vector, ind0=self.get_index_of_mask(0))
        b_3.iadd_transpose((1, 0, 2), factor=-1.0)
        #
        # R_abJ
        #
        # (1) racJ x9bc
        #
        b_3.contract("abc,db->adc", x9bc, **to_s_3)
        #
        # (2) rabK x11jk
        #
        b_3.contract("abc,dc->abd", x11jk, **to_s_3, factor=0.5)
        #
        # (3) rcdJ ab||cd
        #
        gvvvv.contract("abcd,cde->abe", b_3, **to_s_3, factor=0.25)
        gvvvv.contract("abcd,dce->abe", b_3, **to_s_3, factor=-0.25)
        #
        # (4) racK x8ajck[bjck]
        #
        x8ajck = self.from_cache("x8ajck")
        x8ajck.contract("abcd,ecd->eab", b_3, **to_s_3)
        if self.dump_cache:
            self.cache.dump("x8ajck")
        #
        # P(ij)
        #
        s_3.iadd_transpose((1, 0, 2), factor=-1.0)
        #
        # Assign to sigma vector
        #
        sigma = self.lf.create_one_index(self.dimension)
        #
        # assign using mask
        #
        sigma.assign(s_3.array[self.get_mask(0)])

        return sigma

    @timer.with_section("EApCCD3: H_eff")
    def set_hamiltonian(
        self,
        mo1: DenseTwoIndex,
        mo2: FourIndex,
    ) -> None:
        """Derive selected effective Hamiltonian
        fock_pq: one_pq + sum_m(2<pm|qm> - <pm|mq>),
        lpqpq:   2<pq|pq>-<pq|qp>,
        gpqpq:   <pq|pq>,

        **Arguments:**

        mo1, mo2
             one- and two-electron integrals
        """
        cia = self.checkpoint["t_p"]
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        nact = self.occ_model.nact[0]
        #
        # Get ranges for contract
        #
        vovo = self.get_range("vovo")
        oovv = self.get_range("oovv")
        vvoo = self.get_range("vvoo")
        #
        # Inactive Fock matrix
        #
        fock = self.init_cache("fock", nact, nact)
        get_fock_matrix(fock, mo1, mo2, nacto)
        #
        # x9bc
        #
        x9bc = self.init_cache("x9bc", nactv, nactv)
        # fbc
        x9bc.iadd(fock, 1.0, begin2=nacto, begin3=nacto)
        # -<bc|kk> ckb
        mo2.contract("abcc,ca->ab", cia, x9bc, factor=-1.0, **vvoo)
        #
        # x11jk
        #
        x11jk = self.init_cache("x11jk", nacto, nacto)
        # -fjk
        x11jk.iadd(fock, -1.0, end2=nacto, end3=nacto)
        # -gjkcc jc
        mo2.contract("abcc,ac->ab", cia, x11jk, factor=-1.0, **oovv)
        #
        # x8ajck
        #
        x8ajck = self.init_cache("x8ajck", nactv, nacto, nactv, nacto)
        # gajck
        mo2.contract("abcd->abcd", x8ajck, factor=-1.0, **vovo)
        # gjkca cja
        goovv = self.denself.create_four_index(nacto, nacto, nactv, nactv)
        mo2.contract("abcd->abcd", goovv, **oovv)
        goovv.contract("abcd,ad->dacb", cia, x8ajck)
        if self.dump_cache:
            self.cache.dump("x8ajck")

        #
        # 4-Index slices of ERI
        #
        def alloc(arr: FourIndex, block: str) -> tuple[partial[FourIndex]]:
            """Determines alloc keyword argument for init_cache method.
            arr: an instance of CholeskyFourIndex or DenseFourIndex
            block: (str) encoding which slices to consider using the get_range
                    method.
            """
            # We keep one whole CholeskyFourIndex to rule them all.
            # Non-redundant blocks are accessed as views.
            if isinstance(arr, CholeskyFourIndex):
                return (partial(arr.view, **self.get_range(block)),)
            # But we store only non-redundant blocks of DenseFourIndex
            return (partial(arr.copy, **self.get_range(block)),)

        #
        # Get blocks (for the systems we can treat with Dense, it does not
        # matter that we store vvvv blocks)
        #
        slices = ["vvvv"]
        for slice_ in slices:
            self.init_cache(f"g{slice_}", alloc=alloc(mo2, slice_))
        #
        # Clean up
        #
        mo1.__del__()
        mo2.__del__()
