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
     :2p:    2 particles
     :3p:    3 particles
     :aa:    same-spin component (Alpha-Alpha)
     :ab:    opposite-spin component (Alpha-Beta)

This module has been written by:
2023: Katharina Boguslawski
"""

from functools import partial
from typing import Any

from pybest.auxmat import get_fock_matrix
from pybest.ea_eom.dea_base import RDEACC0
from pybest.linalg import (
    CholeskyFourIndex,
    DenseOneIndex,
    DenseThreeIndex,
    DenseTwoIndex,
    FourIndex,
)
from pybest.log import timer


class RDEApCCD0(RDEACC0):
    """
    Restricted Double Electron Affinity Equation of Motion Coupled Cluster
    class restricted to Double EA for a pCCD reference function and 0 unpaired
    electron (m_s = 0.0)

    This class defines only the function that are unique for the DEA-pCCD model
    with 0 unpaired electron:

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
    alpha = 0

    @timer.with_section("DEApCCD0: H_diag")
    def compute_h_diag(self, *args: Any) -> DenseOneIndex:
        """Diagonal approximation to Hamiltonian for S_z=0.0 states"""
        h_diag = self.lf.create_one_index(self.dimension, "h_diag")
        cia = self.checkpoint["t_p"]
        #
        # Get effective Hamiltonian
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        xcd = self.from_cache("xcd")
        gvvoo = self.from_cache("gvvoo")
        gvvvv = self.from_cache("gvvvv")
        #
        # get ranges
        #
        end = nactv * nactv
        #
        # intermediates
        #
        xcc = xcd.copy_diagonal()
        g_ab = self.lf.create_two_index(nactv, nactv)
        g_ak = self.lf.create_two_index(nactv, nacto)
        gvvvv.contract("abab->ab", g_ab)
        gvvoo.contract("aabb->ab", g_ak)
        #
        # H_aB,aB
        #
        h_aB = self.lf.create_two_index(nactv, nactv)
        #
        # xcd(a,a) + xcd(b,b)
        #
        xcc.expand("a->ab", h_aB)
        xcc.expand("b->ab", h_aB)
        #
        # <ab|ab> + <aa|kk> cka d_ab
        #
        h_aB.iadd(g_ab)
        tmp = g_ak.contract("ab,ba->a", cia)
        h_aB.iadd_diagonal(tmp)
        del tmp
        #
        # assign
        #
        h_diag.assign(h_aB.ravel(), end0=end)
        #
        # H_aBck and H_aBCK
        #
        if self.n_particle_operator > 2:
            self.get_3_particle_h_diag(h_diag, g_ab, g_ak)

        return h_diag

    def get_3_particle_h_diag(
        self, h_diag: DenseOneIndex, g_ab: DenseTwoIndex, g_ak: DenseTwoIndex
    ) -> None:
        """Determine all contributions containing three particle operators:
            * H_aBck
            * H_aBCK

        **Arguments:**

        h_diag:
            The preconditioner used in Davidson diagonalization

        g_ab, g_ak:
            Blocks of ERI used to construct the diagonal approximations to H
            (g_ab = <ab|ab>; g_ak = <aa|kk>)
        """
        cia = self.checkpoint["t_p"]
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        #
        # Get effective Hamiltonian
        #
        xcd = self.from_cache("xcd")
        xkm = self.from_cache("xkm")
        xckdm = self.from_cache("xckdm")
        xbkDm = self.from_cache("xbkDm")
        gvvvv = self.from_cache("gvvvv")
        #
        # intermediates
        #
        xcc = xcd.copy_diagonal()
        xkk = xkm.copy_diagonal()
        xckck = xckdm.contract("abab->ab")
        xbkbk = xbkDm.contract("abab->ab")
        l_ab = g_ab.copy()
        gvvvv.contract("abba->ab", l_ab, factor=-1.0)
        #
        # H_aBck
        #
        h_abck = self.denself.create_four_index(nactv, nactv, nactv, nacto)
        end_2p = nactv * nactv
        end_3paa = end_2p + nactv * nactv * (nactv - 1) // 2 * nacto
        #
        # 0.5 xkm(k,k)
        #
        xkk.expand("d->abcd", h_abck, factor=0.5)
        #
        # xcd(c,c) + 0.5 xcd(b,b)
        #
        xcc.expand("c->abcd", h_abck)
        xcc.expand("b->abcd", h_abck, factor=0.5)
        #
        # xckdm(c,k,c,k)
        #
        xckck.expand("cd->abcd", h_abck)
        #
        # g_ab(b,c) + 0.25 l_ab(a,c)
        #
        g_ab.expand("bc->abcd", h_abck)
        l_ab.expand("ac->abcd", h_abck, factor=0.25)
        #
        # xbkDm(b,k,b,k)
        #
        xbkbk.expand("bd->abcd", h_abck, factor=0.5)
        #
        # d_bc terms
        # [<bb|mm> cmb - <bb|kk> ckb] d_bc -> (b) - (bk) -> abbk
        # (b) -> abbk
        tmp = g_ak.contract("ab,ba->a", cia)
        tmp.expand("b->abbc", h_abck)
        # (bk) -> abk -> abbk
        tmp = g_ak.contract("ab,ba->ab", cia, factor=-1.0)
        tmp_abk = self.lf.create_three_index(nactv, nactv, nacto)
        tmp.expand("bc->abc", tmp_abk)
        tmp_abk.expand("abc->abbc", h_abck)
        #
        # Permutation P(ac)
        #
        h_abck.iadd_transpose((2, 1, 0, 3), factor=1.0)
        del tmp, tmp_abk
        #
        # assign using mask
        #
        h_diag.assign(
            h_abck.array[self.get_mask(True)], begin0=end_2p, end0=end_3paa
        )
        #
        # H_aBCK = H_Back (same terms but transposed)
        #
        h_abck.itranspose((1, 0, 2, 3))
        #
        # assign using mask
        #
        h_diag.assign(h_abck.array[self.get_mask(False)], begin0=end_3paa)

    @timer.with_section("DEApCCD0: H_sub")
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
        cia = self.checkpoint["t_p"]
        #
        # Get auxiliary matrices
        #
        nactv = self.occ_model.nactv[0]
        xcd = self.from_cache("xcd")
        gvvoo = self.from_cache("gvvoo")
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
        # Assign R_aB terms
        # Final index of 2 particle terms in b vector
        end = nactv * nactv
        b_2.assign(b_vector, end2=end)
        #
        # R_aB
        #
        # (1) xcd(b,c) raC / xcd(a,c) rcB
        #
        b_2.contract("ab,cb->ac", xcd, **to_s_2)
        xcd.contract("ab,bc->ac", b_2, **to_s_2)
        #
        # (2) <ab|cd> rcD + <cd|kk> rcD cka dab
        #
        gvvvv.contract("abcd,cd->ab", b_2, **to_s_2)
        # (cka, k) -> a
        tmp_k = gvvoo.contract("abcc,ab->c", b_2)
        tmp_a = cia.contract("ab,a->b", tmp_k)
        s_2.iadd_diagonal(tmp_a)
        del tmp_a, tmp_k
        #
        # R_aBck / R_aBCK including coupling terms
        #
        if self.n_particle_operator > 2:
            self.get_3_particle_terms(b_2, s_2, b_vector, sigma)
        #
        # Assign to sigma vector
        #
        sigma.assign(s_2.ravel(), end0=end)

        return sigma

    def get_3_particle_terms(
        self,
        b_2: DenseTwoIndex,
        s_2: DenseTwoIndex,
        b_vector: DenseOneIndex,
        sigma: DenseOneIndex,
    ) -> None:
        """Determine all contributions containing three particle operators:
            * coupling terms to R_aB
            * R_aBck
            * R_aBCK

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
        end_2p = nactv * nactv
        end_3paa = end_2p + nactv * nactv * (nactv - 1) // 2 * nacto
        mask = self.get_index_of_mask(True)
        # assign
        b_3aa.assign(b_vector, ind=mask, begin4=end_2p, end4=end_3paa)
        # account for symmetry (ac)
        b_3aa.iadd_transpose((2, 1, 0, 3), factor=-1.0)
        #
        # assign R_aBCK
        #
        mask = self.get_index_of_mask(False)
        # assign
        b_3ab.assign(b_vector, ind=mask, begin4=end_3paa)
        # account for symmetry (BC)
        b_3ab.iadd_transpose((0, 2, 1, 3), factor=-1.0)
        del mask
        #
        # Coupling terms to R_aB
        #
        self.get_3_particle_r_aB_terms(b_3aa, b_3ab, s_2)
        #
        # R_aBck
        #
        self.get_3_particle_r_aBck_terms(b_2, b_3aa, b_3ab, s_3)
        # assign using mask
        sigma.assign(
            s_3.array[self.get_mask(True)], begin0=end_2p, end0=end_3paa
        )
        #
        # R_aBCK
        #
        self.get_3_particle_r_aBCK_terms(b_2, b_3aa, b_3ab, s_3)
        # assign using mask
        # s_abCK
        sigma.assign(s_3.array[self.get_mask(False)], begin0=end_3paa)

    def get_3_particle_r_aB_terms(
        self,
        b_3aa: DenseThreeIndex,
        b_3ab: DenseThreeIndex,
        s_2: DenseTwoIndex,
    ) -> None:
        """Determine all contributions containing three particle operators:
            * coupling terms to R_aB

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
        # (3) fck raBck + fck raBCK
        #
        b_3aa.contract("abcd,cd->ab", fock, **to_s_2, **vo4)
        b_3ab.contract("abcd,cd->ab", fock, **to_s_2, **vo4)
        #
        # (4) + 0.5<bl||cd> raCDL + <al|cd> rcBDL
        gvovv.contract("abcd,ecdb->ea", b_3ab, **to_s_2, factor=0.5)
        gvovv.contract("abcd,edcb->ea", b_3ab, **to_s_2, factor=-0.5)
        gvovv.contract("abcd,cedb->ae", b_3ab, **to_s_2)
        #     + 0.5<al||cd> rcBdl + <bl|cd> raCdl
        gvovv.contract("abcd,cedb->ae", b_3aa, **to_s_2, factor=0.5)
        gvovv.contract("abcd,decb->ae", b_3aa, **to_s_2, factor=-0.5)
        gvovv.contract("abcd,ecdb->ea", b_3aa, **to_s_2)

    def get_3_particle_r_aBck_terms(
        self,
        b_2: DenseTwoIndex,
        b_3aa: DenseThreeIndex,
        b_3ab: DenseThreeIndex,
        s_3: DenseOneIndex,
    ) -> None:
        """Determine all contributions containing three particle operators:
            * R_aBck

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
        gvvoo = self.from_cache("gvvoo")
        gvovv = self.from_cache("gvovv")
        gvvvv = self.from_cache("gvvvv")
        xckdm = self.from_cache("xckdm")
        xckDM = self.from_cache("xckDM")
        xbckd = self.from_cache("xbckd")
        xackd = self.from_cache("xackd")
        xbkDm = self.from_cache("xbkDm")
        #
        # Coupling to R_ab
        # (1) xbckd raD + xackd rdB
        #
        xbckd.contract("abcd,ed->eabc", b_2, **to_s_3)
        xackd.contract("abcd,de->aebc", b_2, **to_s_3)
        #
        # (3) xcd(c,d) raBdk + 0.5 xcd(b,d) raDck
        #
        b_3aa.contract("abcd,ec->abed", xcd, **to_s_3)
        b_3aa.contract("abcd,eb->aecd", xcd, **to_s_3, factor=0.5)
        #
        # (4) 0.5 xkm(k,m) raBcm
        #
        b_3aa.contract("abcd,ed->abce", xkm, **to_s_3, factor=0.5)
        #
        # (5) xckdm raBdm + xckDM raBDM + 0.5 xbkDm raDcm
        #
        b_3aa.contract("abcd,efcd->abef", xckdm, **to_s_3)
        b_3ab.contract("abcd,efcd->abef", xckDM, **to_s_3)
        b_3aa.contract("abcd,efbd->aecf", xbkDm, **to_s_3, factor=0.5)
        #
        # (6) <bc|de> raDek + 0.25 <ac||de> rdBek [+ <ed|mm> cmb raDek dcb]
        #
        gvvvv.contract("abcd,ecdf->eabf", b_3aa, **to_s_3)
        gvvvv.contract("abcd,cedf->aebf", b_3aa, **to_s_3, factor=0.25)
        gvvvv.contract("abcd,cedf->beaf", b_3aa, **to_s_3, factor=-0.25)
        #
        # d_cb terms
        #
        tmp_abk = self.lf.create_three_index(nactv, nactv, nacto)
        to_tmp = {"out": tmp_abk, "clear": False}
        #
        # (6) <de|mm> cmb raDek dcb -> (bde) raDek -> (abk)
        #
        tmp = gvvoo.contract("abcc,ce->eab", cia)
        b_3aa.contract("abcd,ebc->aed", tmp, **to_tmp)
        #
        # (2) - <ak|de> rde ckb dbc -> (ak, ckb) -> (abk)
        # tmp(a,k)
        tmp = gvovv.contract("abcd,cd->ab", b_2, factor=-1.0)
        #
        # (7) - 0.5 <de||mk> raEDM ckb dbc -> (ak, ckb) -> (abk)
        #     -     <de| mk> raEdm ckb dbc -> (ak, ckb) -> (abk)
        #
        b_3ab.contract("abcd,cbde->ae", gvvoo, tmp, factor=-0.5)
        b_3ab.contract("abcd,cbed->ae", gvvoo, tmp, factor=0.5)
        b_3aa.contract("abcd,cbde->ae", gvvoo, tmp, factor=-1.0)
        #
        # tmp_ak ckb -> (abk)
        #
        tmp.contract("ab,bc->acb", cia, tmp_abk)
        del tmp
        #
        # Expand indices (abk -> abbk)
        #
        tmp_abk.expand("abc->abbc", s_3)
        #
        # Permutation P(ac)
        #
        s_3.iadd_transpose((2, 1, 0, 3), factor=-1.0)

    def get_3_particle_r_aBCK_terms(
        self,
        b_2: DenseTwoIndex,
        b_3aa: DenseThreeIndex,
        b_3ab: DenseThreeIndex,
        s_3: DenseThreeIndex,
    ) -> None:
        """Determine all contributions containing three particle operators:
            * R_aBCK

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
        gvvoo = self.from_cache("gvvoo")
        gvovv = self.from_cache("gvovv")
        gvvvv = self.from_cache("gvvvv")
        xckdm = self.from_cache("xckdm")
        xckDM = self.from_cache("xckDM")
        xbkDm = self.from_cache("xbkDm")
        xbckd = self.from_cache("xbckd")
        xackd = self.from_cache("xackd")
        #
        # (1) xbckd(a,c,k,d) rdB + xackd(b,c,k,d) raD
        #
        xbckd.contract("abcd,de->aebc", b_2, **to_s_3)
        xackd.contract("abcd,ed->eabc", b_2, **to_s_3)
        #
        # (3) xcd(c,d) raBDK + 0.5 xcd(a,d) rdBCK
        #
        b_3ab.contract("abcd,ec->abed", xcd, **to_s_3)
        b_3ab.contract("abcd,ea->ebcd", xcd, **to_s_3, factor=0.5)
        #
        # (4) 0.5 xkm(k,m) raBCM
        #
        b_3ab.contract("abcd,ed->abce", xkm, **to_s_3, factor=0.5)
        #
        # (5) xckdm raBDM + xckDM raBdm + 0.5 xbkDm(a,k,d,m) rdBCM
        #
        b_3ab.contract("abcd,efcd->abef", xckdm, **to_s_3)
        b_3aa.contract("abcd,efcd->abef", xckDM, **to_s_3)
        b_3ab.contract("abcd,efad->ebcf", xbkDm, **to_s_3, factor=0.5)
        #
        # (6) 0.25 <bc||de> raDEK + <ac|de> rdBEK [+ <ed|mm> cma reBDK dac]
        #
        gvvvv.contract("abcd,ecdf->eabf", b_3ab, **to_s_3, factor=0.25)
        gvvvv.contract("abcd,edcf->eabf", b_3ab, **to_s_3, factor=-0.25)
        gvvvv.contract("abcd,cedf->aebf", b_3ab, **to_s_3)
        #
        # d_ac terms
        #
        tmp_abk = self.lf.create_three_index(nactv, nactv, nacto)
        to_tmp = {"out": tmp_abk, "clear": False}
        #
        # (6) <ed|mm> cma reBDK dac -> (aed) reBDK -> (abk)
        #
        tmp = gvvoo.contract("abcc,ce->eab", cia)
        b_3ab.contract("abcd,eac->ebd", tmp, **to_tmp)
        #
        # (2) - <bk|de> reD cka dac -> (cka, bk) -> (abk)
        # tmp(b,k)
        tmp = gvovv.contract("abcd,dc->ab", b_2, factor=-1.0)
        #
        # (7) - 0.5 <ed||km> reBdm cka dac -> (bk, cka) -> (abk)
        #     -     <ed| km> reBDM cka dac -> (bk, cka) -> (abk)
        #
        gvvoo.contract("abcd,aebd->ec", b_3aa, tmp, factor=-0.5)
        gvvoo.contract("abcd,aebc->ed", b_3aa, tmp, factor=0.5)
        gvvoo.contract("abcd,aebd->ec", b_3ab, tmp, factor=-1.0)
        #
        # tmp(b,k) cka -> (abk)
        #
        tmp.contract("ab,bc->cab", cia, tmp_abk)
        del tmp
        #
        # Expand indices (abk -> abak)
        #
        tmp_abk.expand("abc->abac", s_3)
        #
        # Permutation P(bc)
        #
        s_3.iadd_transpose((0, 2, 1, 3), factor=-1.0)

    @timer.with_section("DEApCCD0: H_eff")
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
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        nact = self.occ_model.nact[0]
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
        # goovv
        #
        gvvoo = self.init_cache("gvvoo", nactv, nactv, nacto, nacto)
        mo2.contract("abcd->abcd", gvvoo, **vvoo)
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
        vvov = self.get_range("vvov")
        vovv = self.get_range("vovv")
        #
        # optimize contractions
        #
        opt = "td" if isinstance(mo2, CholeskyFourIndex) else "einsum"
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
        #
        # xackd
        #
        xackd = self.init_cache("xackd", nactv, nactv, nacto, nactv)
        # 0.5 <ac||dk>
        mo2.contract("abcd->abdc", xackd, factor=0.5, **vvvo)
        mo2.contract("abcd->abcd", xackd, factor=-0.5, **vvov)
        # <ac|dk> ckc
        mo2.contract("abcd,db->abdc", cia, xackd, **vvvo)
