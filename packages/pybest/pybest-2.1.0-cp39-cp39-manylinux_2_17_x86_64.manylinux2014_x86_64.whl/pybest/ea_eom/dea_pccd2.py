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
"""Double Electron Affinity Equation of Motion Coupled Cluster implementations
   for a pCCD reference function

   Variables used in this module:
    :ncore:     number of frozen core orbitals
    :nocc:      number of occupied orbitals in the principle configuration
    :nacto:     number of active occupied orbitals in the principle configuration
    :nvirt:     number of virtual orbitals in the principle configuration
    :nactv:     number of active virtual orbitals in the principle configuration
    :nbasis:    total number of basis functions
    :nact:      total number of active orbitals (nacto+nactv)
    :e_ea:      the energy correction for DEA
    :civ_ea:    the CI amplitudes from a given EOM model
    :rab:       2 particle operator
    :rabck:     1 hole 3 particle operator (same spin)
    :rabCK:     1 hole 3 particle operator (opposite spin)

    Indexing convention:
     :i,j,k,..: occupied orbitals of principal configuration (alpha spin)
     :a,b,c,..: virtual orbitals of principal configuration (alpha spin)
     :p,q,r,..: general indices (occupied, virtual; alpha spin)
     :I,J,K,..: occupied orbitals of principal configuration (beta spin)
     :A,B,C,..: virtual orbitals of principal configuration (beta spin)
     :P,Q,R,..: general indices (occupied, virtual; beta spin)

    Abbreviations used (if not mentioned in doc-strings):
     :Lpqrs: 2<pq|rs>-<pq|sr>
     :gpqrs: <pq|rs>
     :2p:    2 particles
     :3p:    3 particles
     :aa:    same-spin component (Alpha-Alpha)
     :ab:    opposite-spin component (Alpha-Beta)

This module has been written by:
2023: Katharina Boguslawski
"""

from functools import partial
from typing import Any

import numpy as np

from pybest.auxmat import get_fock_matrix
from pybest.ea_eom.dea_base import RDEACC2
from pybest.linalg import (
    CholeskyFourIndex,
    DenseFourIndex,
    DenseOneIndex,
    DenseThreeIndex,
    DenseTwoIndex,
    FourIndex,
)
from pybest.log import timer


class RDEApCCD2(RDEACC2):
    """
        Restricted Double Electron Affinity Equation of Motion Coupled Cluster
    class restricted to Double EA for a pCCD reference function and 2 unpaired
    electrons (m_s = 1.0, high-spin implementation)

    This class defines only the function that are unique for the DEA-pCCD model
    with 2 unpaired electrons:

        * dimension (number of degrees of freedom)
        * unmask_args (resolve T_p amplitudes)
        * set_hamiltonian (calculates effective Hamiltonian -- at most O(o2v2))
        * compute_h_diag (pre-conditioner used by Davidson)
        * build_subspace_hamiltonian (subspace to be diagonalized)
    """

    long_name = "Double Electron Affinity Equation of Motion pair Coupled Cluster Doubles"
    acronym = "DEA-EOM-pCCD"
    reference = "pCCD"
    cluster_operator = "Tp"
    particle_hole_operator = "2p + 3p1h"
    order = "DEA"
    alpha = 2

    @timer.with_section("DEApCCD2: H_diag")
    def compute_h_diag(self, *args: Any) -> DenseOneIndex:
        """Diagonal approximation to Hamiltonian for S_z=1.0 states"""
        h_diag = self.lf.create_one_index(self.dimension, "h_diag")
        #
        # Get effective Hamiltonian
        #
        nactv = self.occ_model.nactv[0]
        gvvvv = self.from_cache("gvvvv")
        xcd = self.from_cache("xcd")
        #
        # get ranges
        #
        end = nactv * (nactv - 1) // 2
        #
        # intermediates
        #
        l_ab = xcd.new()
        gvvvv.contract("abab->ab", l_ab)
        gvvvv.contract("abba->ab", l_ab, factor=-1.0)
        xcc = xcd.copy_diagonal()
        #
        # H_ab,ab
        #
        h_ab = self.lf.create_two_index(nactv, nactv)
        #
        # xcd(b,b)
        #
        xcc.expand("b->ab", h_ab)
        #
        # 0.25 <ab||ab>
        #
        h_ab.iadd(l_ab, factor=0.25)
        #
        # Permutation
        #
        h_ab.iadd_t(h_ab, factor=1.0)
        #
        # assign using mask
        #
        triu = np.triu_indices(nactv, k=1)
        h_diag.assign(h_ab.array[triu], end0=end)
        #
        # R_abck and R_abCK
        #
        if self.n_particle_operator > 2:
            self.get_3_particle_h_diag(h_diag, l_ab)

        return h_diag

    def get_3_particle_h_diag(
        self, h_diag: DenseOneIndex, l_ab: DenseTwoIndex
    ) -> None:
        """Determine all contributions containing three particle operators:
            * H_abck
            * H_abCK

        **Arguments:**

        h_diag:
            (DenseOneIndex) contains the diagonal elements of the Hamiltonian

        l_ab:
            (DenseTwoIndex) intermediat containing <ab|ab> - <ab|ba>
        """
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        #
        # Get effective Hamiltonian
        #
        xcd = self.from_cache("xcd")
        xkm = self.from_cache("xkm")
        xckdm = self.from_cache("xckdm")
        #
        # intermediates
        #
        xcc = xcd.copy_diagonal()
        xkk = xkm.copy_diagonal()
        xckck = xckdm.contract("abab->ab")
        #
        # H_abck,abck and H_abCK,abCK
        #
        h_abck = self.denself.create_four_index(nactv, nactv, nactv, nacto)
        end_2p = nactv * (nactv - 1) // 2
        end_3p = end_2p + nactv * (nactv - 1) * (nactv - 2) // 6 * nacto
        #
        # Reuse effective Hamiltonian terms
        #
        h_eff = {"xkk": xkk, "xcc": xcc, "l_ab": l_ab, "xckck": xckck}
        #
        # H_abck
        # we do not need to check if nv > 2 as this is done in _check_n_particle_operator,
        # where we enforce n_particle_operator > nv. Thus, if n_particle_operator >= 3, nv >= 3.
        self.get_3_particle_h_diag_abck(h_abck, **h_eff)
        #
        # assign using mask
        #
        h_diag.assign(
            h_abck.array[self.get_mask(True)], begin0=end_2p, end0=end_3p
        )
        #
        # H_abCK
        #
        self.get_3_particle_h_diag_abCK(h_abck, **h_eff)
        #
        # assign using mask
        #
        h_diag.assign(h_abck.array[self.get_mask(False)], begin0=end_3p)

    @staticmethod
    def get_3_particle_h_diag_abck(
        h_abck: DenseFourIndex, **h_eff: dict[str, Any]
    ) -> None:
        """Determine all contributions containing three particle operators:
            * H_abck

        **Arguments:**

        h_abck:
            the part of the Hamiltonian matrix to be calculated

        **Keyword arguments:**

        h_eff:
            dictionary of all effective Hamiltonian terms required to calcualte
            all h_abck terms
        """
        xkk = h_eff.get("xkk")
        xcc = h_eff.get("xcc")
        l_ab = h_eff.get("l_ab")
        xckck = h_eff.get("xckck")
        # Clear to be sure it's empty
        h_abck.clear()
        #
        # xkm(k,k)
        #
        xkk.expand("d->abcd", h_abck, factor=1 / 3)
        #
        # xcd(c,c)
        #
        xcc.expand("c->abcd", h_abck)
        #
        # xckdm(c,k,c,k)
        #
        xckck.expand("cd->abcd", h_abck)
        #
        # 0.5 l_ab
        #
        l_ab.expand("ab->abcd", h_abck, factor=0.5)
        #
        # Permutations
        #
        # create copy first
        tmp = h_abck.copy()
        # Pca (abck)
        h_abck.iadd_transpose((2, 1, 0, 3), other=tmp)
        # Pcb (abck)
        h_abck.iadd_transpose((0, 2, 1, 3), other=tmp)
        del tmp

    def get_3_particle_h_diag_abCK(
        self, h_abck: DenseFourIndex, **h_eff: dict[str, Any]
    ) -> None:
        """Determine all contributions containing three particle operators:
            * H_abCK

        **Arguments:**

        h_abck:
            the part of the Hamiltonian matrix to be calculated

        **Keyword arguments:**

        h_eff:
            dictionary of all effective Hamiltonian terms required to calcualte
            all h_abck terms
        """
        cia = self.checkpoint["t_p"]
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        #
        # Get effective Hamiltonian
        #
        xkk = h_eff.get("xkk")
        xcc = h_eff.get("xcc")
        l_ab = h_eff.get("l_ab")
        xckck = h_eff.get("xckck")
        # recalculate missing terms
        xbkDm = self.from_cache("xbkDm")
        goovv = self.from_cache("goovv")
        gvvvv = self.from_cache("gvvvv")
        #
        # intermediates
        #
        xbkbk = xbkDm.contract("abab->ab")
        g_vv = gvvvv.contract("abab->ab")
        g_ov = goovv.contract("aabb->ab")
        # Clear just to be sure it's empty
        h_abck.clear()
        #
        # 0.5 xac(c,c)
        #
        xcc.expand("c->abcd", h_abck, factor=0.5)
        #
        # xac(b,b)
        #
        xcc.expand("b->abcd", h_abck)
        #
        # 0.5 xkm(k,k)
        #
        xkk.expand("d->abcd", h_abck, factor=0.5)
        #
        # 0.5 xckck(c,k,c,k)
        #
        xckck.expand("cd->abcd", h_abck, factor=0.5)
        #
        # xbkDm(b,k,b,k)
        #
        xbkbk.expand("bd->abcd", h_abck)
        #
        # <bc|bc>
        #
        g_vv.expand("bc->abcd", h_abck)
        #
        # 0.25 l_ab
        #
        l_ab.expand("ab->abcd", h_abck, factor=0.25)
        #
        #  <mm|bb> cmb d_bc
        #
        tmp = g_ov.contract("ab,ab->b", cia)
        tmp.expand("b->abbc", h_abck)
        #
        # - <kk|bb> ckb d_bc
        #
        tmp = g_ov.contract("ab,ab->ba", cia)
        # create (abk) intermediate
        tmp_abk = self.lf.create_three_index(nactv, nactv, nacto)
        tmp.expand("bc->abc", tmp_abk)
        tmp_abk.expand("abc->abbc", h_abck, factor=-1.0)
        #
        # Permutation
        #
        h_abck.iadd_transpose((1, 0, 2, 3), factor=1.0)

    @timer.with_section("DEApCCD2: H_sub")
    def build_subspace_hamiltonian(
        self, b_vector: DenseOneIndex, h_diag: DenseOneIndex, *args: Any
    ) -> DenseOneIndex:
        """
        Used by Davidson module to construct subspace Hamiltonian

        **Arguments:**

        b_vector:
            (OneIndex object) contains current approximation to CI coefficients

        h_diag:
            Diagonal Hamiltonian elements required in davidson module (not used
            here)

        args:
            Set of arguments passed by the Davidson module (not used here)
        """
        #
        # Get auxiliary matrices
        #
        nactv = self.occ_model.nactv[0]
        xcd = self.from_cache("xcd")
        gvvvv = self.from_cache("gvvvv")
        #
        # Calculate sigma vector = (H.bvector)
        #
        # output
        s_2 = self.lf.create_two_index(nactv, nactv)
        to_s_2 = {"out": s_2, "clear": False}
        sigma = self.lf.create_one_index(self.dimension)
        # input
        b_2 = self.lf.create_two_index(nactv, nactv)
        #
        # Assign R_ab terms
        # get unique indices
        triu = np.triu_indices(nactv, k=1)
        # Final index of 2 particle terms in b vector
        end = (nactv - 1) * nactv // 2
        b_2.assign(b_vector, ind=triu, end2=end)
        b_2.iadd_t(b_2, factor=-1.0)
        #
        # R_ab
        #
        # (1) xcd(b,d) rad
        #
        b_2.contract("ab,cb->ac", xcd, **to_s_2)
        #
        # (2) <ab||cd> rcd
        #
        gvvvv.contract("abcd,cd->ab", b_2, **to_s_2, factor=0.25)
        gvvvv.contract("abcd,dc->ab", b_2, **to_s_2, factor=-0.25)
        #
        # R_abck / R_abCK including coupling terms
        #
        if self.n_particle_operator > 2:
            self.get_3_particle_terms(b_2, s_2, b_vector, sigma)
        #
        # Permutation P(ab)
        #
        s_2.iadd_t(s_2, factor=-1.0)
        #
        # Assign to sigma vector
        #
        sigma.assign(s_2.array[triu], end0=end)

        return sigma

    def get_3_particle_terms(
        self,
        b_2: DenseTwoIndex,
        s_2: DenseTwoIndex,
        b_vector: DenseOneIndex,
        sigma: DenseOneIndex,
    ) -> None:
        """Determine all contributions containing three particle operators:
            * coupling terms to R_ab
            * R_abck
            * R_abCK

        **Arguments:**

        b_2, b_vector:
            b vectors used in Davidson diagonalization

        s_2, sigma:
            sigma vectors used in Davidson diagonalization
        """
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        #
        # Calculate sigma vector = (H.bvector)
        #
        # output
        s_3 = self.denself.create_four_index(nactv, nactv, nactv, nacto)
        # input
        b_3aa = self.denself.create_four_index(nactv, nactv, nactv, nacto)
        b_3ab = self.denself.create_four_index(nactv, nactv, nactv, nacto)
        #
        # assign R_abck
        #
        # Some dimensions
        end_2p = (nactv - 1) * nactv // 2
        end_3paa = (nactv - 1) * nactv // 2 + nactv * (nactv - 1) * (
            nactv - 2
        ) // 6 * nacto
        mask = self.get_index_of_mask(True)
        b_3aa.assign(b_vector, ind=mask, begin4=end_2p, end4=end_3paa)
        # create tmp object to account for symmetry
        tmp = b_3aa.copy()
        b_3aa.iadd_transpose((1, 0, 2, 3), other=tmp, factor=-1.0)
        b_3aa.iadd_transpose((0, 2, 1, 3), other=tmp, factor=-1.0)
        b_3aa.iadd_transpose((2, 1, 0, 3), other=tmp, factor=-1.0)
        b_3aa.iadd_transpose((1, 2, 0, 3), other=tmp, factor=1.0)
        b_3aa.iadd_transpose((2, 0, 1, 3), other=tmp, factor=1.0)
        del tmp
        #
        # assign R_abCK
        #
        mask = self.get_index_of_mask(False)
        b_3ab.assign(b_vector, ind=mask, begin4=end_3paa)
        # account for symmetry
        b_3ab.iadd_transpose((1, 0, 2, 3), factor=-1.0)
        del mask
        #
        # Coupling terms to R_ab
        #
        self.get_3_particle_r_ab_terms(b_3aa, b_3ab, s_2)
        #
        # R_abck
        #
        self.get_3_particle_r_abck_terms(b_2, b_3aa, b_3ab, s_3)
        # assign using mask
        sigma.assign(
            s_3.array[self.get_mask(True)], begin0=end_2p, end0=end_3paa
        )
        #
        # R_abCK
        #
        self.get_3_particle_r_abCK_terms(b_2, b_3aa, b_3ab, s_3)
        # assign using mask
        # s_abCK
        sigma.assign(s_3.array[self.get_mask(False)], begin0=end_3paa)

    def get_3_particle_r_ab_terms(
        self,
        b_3aa: DenseThreeIndex,
        b_3ab: DenseThreeIndex,
        s_2: DenseTwoIndex,
    ) -> None:
        """Determine all contributions containing three particle operators:
            * coupling terms to R_ab

        **Arguments:**

        b_3aa, b_3ab:
            b vectors of different R operators used in Davidson diagonalization

        s_2:
            sigma vector corresponding to R_ab used in Davidson diagonalization
        """
        #
        # Effective Hamiltonian
        #
        fock = self.from_cache("fock")
        gvovv = self.from_cache("gvovv")
        #
        # get ranges
        #
        vo4 = self.get_range("vo", start=4)
        to_s_2 = {"out": s_2, "clear": False}
        #
        # (3) 0.5 fdm (rabdm + rabDM)
        #
        b_3aa.contract("abcd,cd->ab", fock, **to_s_2, **vo4, factor=0.5)
        b_3ab.contract("abcd,cd->ab", fock, **to_s_2, **vo4, factor=0.5)
        #
        # (4) 0.5 <bm||cd> racdm + <bm|cd> racDM
        #
        gvovv.contract("abcd,ecdb->ea", b_3aa, **to_s_2, factor=0.5)
        gvovv.contract("abcd,edcb->ea", b_3aa, **to_s_2, factor=-0.5)
        gvovv.contract("abcd,ecdb->ea", b_3ab, **to_s_2)

    def get_3_particle_r_abck_terms(
        self,
        b_2: DenseTwoIndex,
        b_3aa: DenseThreeIndex,
        b_3ab: DenseThreeIndex,
        s_3: DenseThreeIndex,
    ) -> None:
        """Determine all contributions containing three particle operators:
            * R_abck

        **Arguments:**

        b_2, b_3aa, b_3ab:
            b vectors of different R operators used in Davidson diagonalization

        s_3:
            sigma vector corresponding to R_ab used in Davidson diagonalization
        """
        cia = self.checkpoint["t_p"]
        #
        # clear temp storage
        #
        s_3.clear()
        to_s_3 = {"out": s_3, "clear": False}
        #
        # Effective Hamiltonian
        #
        xcd = self.from_cache("xcd")
        xkm = self.from_cache("xkm")
        gvvov = self.from_cache("gvvov")
        gvovv = self.from_cache("gvovv")
        gvvvv = self.from_cache("gvvvv")
        xckdm = self.from_cache("xckdm")
        xckDM = self.from_cache("xckDM")
        # All terms with P(c/ab)
        # (1) Couplint to R_ab
        # -<ab||kd> rcd
        gvvov.contract("abcd,ed->abec", b_2, **to_s_3, factor=-1.0)
        gvvov.contract("abcd,ed->baec", b_2, **to_s_3)
        # <bk|dc> ckc rad - <ak|dc> ckc rbd
        # <bk|dc> ckc
        tmp = gvovv.contract("abcd,bd->adbc", cia)
        # (bckd) rad
        tmp.contract("abcd,ed->eabc", b_2, **to_s_3)
        # -<ak|dc> ckc rbd
        # -(ackd) rbd
        tmp.contract("abcd,ed->aebc", b_2, **to_s_3, factor=-1.0)
        del tmp
        # (2) = 0
        # (3) xcd(c,d) rabdk
        #
        b_3aa.contract("abcd,ec->abed", xcd, **to_s_3)
        #
        # (4) 1/3 rabcm xkm(k,m)
        #
        b_3aa.contract("abcd,ed->abce", xkm, **to_s_3, factor=1 / 3)
        #
        # (5) xckdm rabdm + xckDM rabDM
        #
        b_3aa.contract("abcd,efcd->abef", xckdm, **to_s_3)
        b_3ab.contract("abcd,efcd->abef", xckDM, **to_s_3)
        #
        # (6) 0.5 <ab||de> rdeck + (7) 0
        #
        gvvvv.contract("abcd,cdef->abef", b_3aa, **to_s_3, factor=0.5)
        gvvvv.contract("abcd,dcef->abef", b_3aa, **to_s_3, factor=-0.5)
        #
        # Permutation P(c/ab)
        # create copy first
        tmp = s_3.copy()
        # - Pca (abck)
        s_3.iadd_transpose((2, 1, 0, 3), other=tmp, factor=-1.0)
        # - Pcb (abck)
        s_3.iadd_transpose((0, 2, 1, 3), other=tmp, factor=-1.0)
        del tmp

    def get_3_particle_r_abCK_terms(
        self,
        b_2: DenseTwoIndex,
        b_3aa: DenseThreeIndex,
        b_3ab: DenseThreeIndex,
        s_3: DenseThreeIndex,
    ) -> None:
        """Determine all contributions containing three particle operators:
            * R_abCK

        **Arguments:**

        b_2, b_3aa, b_3ab:
            b vectors of different R operators used in Davidson diagonalization

        s_3:
            sigma vector corresponding to R_ab used in Davidson diagonalization
        """
        cia = self.checkpoint["t_p"]
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        #
        # clear temp storage
        #
        s_3.clear()
        to_s_3 = {"out": s_3, "clear": False}
        #
        # Effective Hamiltonian
        #
        xcd = self.from_cache("xcd")
        xkm = self.from_cache("xkm")
        xbckd = self.from_cache("xbckd")
        goovv = self.from_cache("goovv")
        gvovv = self.from_cache("gvovv")
        gvvvv = self.from_cache("gvvvv")
        xckdm = self.from_cache("xckdm")
        xckDM = self.from_cache("xckDM")
        xbkDm = self.from_cache("xbkDm")
        #
        # (1) xbckd rad
        #
        xbckd.contract("abcd,ed->eabc", b_2, **to_s_3)
        #
        # (3) 0.5 xcd(c,d) rabDK + xcd(b,d) radCK
        #
        b_3ab.contract("abcd,ec->abed", xcd, **to_s_3, factor=0.5)
        b_3ab.contract("abcd,eb->aecd", xcd, **to_s_3)
        #
        # (4) 0.5 xkm rabCM
        #
        b_3ab.contract("abcd,ed->abce", xkm, **to_s_3, factor=0.5)
        #
        # (5) 0.5 xckDM rabdm + 0.5 xckdm rabDM + xbkDm radCM
        #
        b_3aa.contract("abcd,efcd->abef", xckDM, **to_s_3, factor=0.5)
        b_3ab.contract("abcd,efcd->abef", xckdm, **to_s_3, factor=0.5)
        b_3ab.contract("abcd,efbd->aecf", xbkDm, **to_s_3)
        #
        # (6) <bc|de> radEK + 0.25 <ab||de> rdeCK
        #
        gvvvv.contract("abcd,ecdf->eabf", b_3ab, **to_s_3)
        gvvvv.contract("abcd,cdef->abef", b_3ab, **to_s_3, factor=0.25)
        gvvvv.contract("abcd,dcef->abef", b_3ab, **to_s_3, factor=-0.25)
        #
        # delta_bc terms
        #
        tmp_vo = self.lf.create_two_index(nactv, nacto)
        tmp_abk = self.lf.create_three_index(nactv, nactv, nacto)
        #
        # (2) -0.5 [<ak||de> rde] . ckb dbc -> (ak, ckb) -> (abk)
        #
        gvovv.contract("abcd,cd->ab", b_2, tmp_vo, factor=-0.5)
        gvovv.contract("abcd,dc->ab", b_2, tmp_vo, factor=0.5)
        #
        # (6) <mm|ed> raeDK cmb dbc -> (akm) .  cmb
        #
        tmp = goovv.contract("aabc,dbce->dea", b_3ab)
        # tmp(a,k,m) . cmb -> abk
        tmp.contract("abc,cd->adb", cia, tmp_abk)
        #
        # (7) - 0.5 <mk||de> raedm ckb dkj -> (ak, ckb) -> (abk)
        #     -     <mk| de> raeDM ckb dkj -> (ak, ckb) -> (abk)
        #
        b_3aa.contract("abcd,decb->ae", goovv, tmp_vo, factor=-0.5)
        b_3aa.contract("abcd,debc->ae", goovv, tmp_vo, factor=0.5)
        b_3ab.contract("abcd,decb->ae", goovv, tmp_vo, factor=-1.0)
        #
        # tmp_vo(a,k) ckb-> (abk)
        #
        tmp_vo.contract("ab,bc->acb", cia, tmp_abk)
        del tmp_vo
        #
        # Expand indices
        #
        tmp_abk.expand("abc->abbc", s_3)
        #
        # Permutation P(ab)
        #
        s_3.iadd_transpose((1, 0, 2, 3), factor=-1.0)

    @timer.with_section("DEApCCD2: H_eff")
    def set_hamiltonian(
        self,
        mo1: DenseTwoIndex,
        mo2: FourIndex,
    ) -> None:
        """Derive selected effective Hamiltonian elements. Like
        fock_pq:     one_pq + sum_m(2<pm|qm> - <pm|mq>),

        **Arguments:**

        mo1, mo2
             one- and two-electron integrals.
        """
        cia = self.checkpoint["t_p"]
        nacto, nactv, nact = (
            self.occ_model.nacto[0],
            self.occ_model.nactv[0],
            self.occ_model.nact[0],
        )
        #
        # get ranges
        #
        vvoo = self.get_range("vvoo")
        #
        # optimize contractions
        #
        opt = "td" if isinstance(mo2, CholeskyFourIndex) else "einsum"
        #
        # Inactive Fock matrix
        #
        fock = self.init_cache("fock", nact, nact)
        get_fock_matrix(fock, mo1, mo2, nacto)
        #
        # xcd
        #
        xcd = self.init_cache("xcd", nactv, nactv)
        # fcd
        xcd.iadd(fock, 1.0, begin2=nacto, begin3=nacto)
        # -<cd|kk> ckc
        mo2.contract("abcc,ca->ab", cia, xcd, factor=-1.0, **vvoo, select=opt)
        #
        # 3 particle terms
        #
        if self.n_particle_operator > 2:
            self.set_hamiltonian_3_particle(fock, mo2)

        #
        # 4-Index slices of ERI
        #
        def alloc(arr: FourIndex, block: str) -> tuple[partial[FourIndex]]:
            """Determines alloc keyword argument for init_cache method.
            arr: an instance of CholeskyFourIndex or DenseFourIndex
            block: (str) encoding which slices to consider using the get_range
                    method.
            """
            # Taken from CC module.
            # Non-redundant blocks are accessed as views.
            if isinstance(arr, CholeskyFourIndex):
                return (partial(arr.view, **self.get_range(block)),)
            # But we store only non-redundant blocks of DenseFourIndex
            return (partial(arr.copy, **self.get_range(block)),)

        #
        # Get blocks
        #
        slices = ["vvvv"]
        if self.n_particle_operator > 2:
            slices += ["vovv", "vvov"]
        for slice_ in slices:
            self.init_cache(f"g{slice_}", alloc=alloc(mo2, slice_))
        #
        # Clean up
        #
        mo1.__del__()
        mo2.__del__()

    def set_hamiltonian_3_particle(
        self, fock: DenseTwoIndex, mo2: FourIndex
    ) -> None:
        """Derive selected effective Hamiltonian elements for 3 particle
        operators.

        **Arguments:**

        fock:
            Fock matrix

        mo2:
            Two-electron integrals
        """
        cia = self.checkpoint["t_p"]
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        #
        # get ranges
        #
        ov2 = self.get_range("ov", start=2)
        ovoo = self.get_range("ovoo")
        oovv = self.get_range("oovv")
        voov = self.get_range("voov")
        vovo = self.get_range("vovo")
        vvoo = self.get_range("vvoo")
        vvvo = self.get_range("vvvo")
        vovv = self.get_range("vovv")
        vvvo = self.get_range("vvvo")
        #
        # optimize contractions
        #
        opt = "td" if isinstance(mo2, CholeskyFourIndex) else "einsum"
        #
        # goovv
        #
        goovv = self.init_cache("goovv", nacto, nacto, nactv, nactv)
        mo2.contract("abcd->abcd", goovv, **oovv)
        #
        # xkm
        #
        xkm = self.init_cache("xkm", nacto, nacto)
        # -fkm
        xkm.iadd(fock, -1.0, end2=nacto, end3=nacto)
        # -<km|ee> cke
        mo2.contract("abcc,ac->ab", cia, xkm, factor=-1.0, **oovv, select=opt)
        #
        # xckdm
        #
        xckdm = self.init_cache("xckdm", nactv, nacto, nactv, nacto)
        # <cm||kd>
        mo2.contract("abcd->acdb", xckdm, **voov)
        mo2.contract("abcd->adcb", xckdm, factor=-1.0, **vovo)
        # <cm|kd> ckc
        mo2.contract("abcd,ca->acdb", cia, xckdm, **voov)
        #
        # xckDM
        #
        xckDM = self.init_cache("xckDM", nactv, nacto, nactv, nacto)
        # <cm|kd>
        mo2.contract("abcd->acdb", xckDM, **voov)
        # <cd||km> ckc
        mo2.contract("abcd,ca->acbd", cia, xckDM, **vvoo)
        mo2.contract("abcd,da->adbc", cia, xckDM, factor=-1.0, **vvoo)
        #
        # xbkDm
        #
        xbkDm = self.init_cache("xbkDm", nactv, nacto, nactv, nacto)
        # -<bk|dm>
        mo2.contract("abcd->abcd", xbkDm, factor=-1.0, **vovo)
        # <bk|md> ckb
        mo2.contract("abcd,ba->abdc", cia, xbkDm, **voov)
        # Larger intermediates of size ov^3
        # xbckd
        #
        xbckd = self.init_cache("xbckd", nactv, nactv, nacto, nactv)
        # <bc|dk>
        mo2.contract("abcd->abdc", xbckd, **vvvo)
        # <bk||dc> ckc
        mo2.contract("abcd,bd->adbc", cia, xbckd, factor=1.0, **vovv)
        mo2.contract("abcd,bc->acbd", cia, xbckd, factor=-1.0, **vovv)
        # -<bd|ck> ckb
        mo2.contract("abcd,da->acdb", cia, xbckd, factor=-1.0, **vvvo)
        # -fkd ckb dbc -> (bkd)
        tmp = cia.contract("ab,ac->bac", fock, factor=-1.0, **ov2)
        # <kd|ll> clb dbc -> (bkd)
        mo2.contract("abcc,cd->dab", cia, tmp, **ovoo)
        # expand
        tmp.expand("abc->aabc", xbckd)
        del tmp
