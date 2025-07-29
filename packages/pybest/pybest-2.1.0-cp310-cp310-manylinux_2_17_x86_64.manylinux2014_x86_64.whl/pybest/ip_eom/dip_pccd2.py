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
#
# 2025-02: unification of variables and type hints (Julian Świerczyński)

"""Double Ionization Potential Equation of Motion Coupled Cluster implementations
for a pCCD reference function and 2 unpaired electrons (S_z=1.0 components)

   Variables used in this module:
    :ncore:     number of frozen core orbitals
    :nocc:      number of occupied orbitals in the principal configuration
    :nacto:     number of active occupied orbitals in the principal configuration
    :nvirt:     number of virtual orbitals in the principal configuration
    :nactv:     number of active virtual orbitals in the principal configuration
    :nbasis:    total number of basis functions
    :nact:      total number of active orbitals (nacto+nactv)
    :e_dip:     the energy correction for IP
    :civ_dip:   the CI amplitudes from a given EOM model
    :r_ij:      2 holes operator
    :r_ijkc:    3 holes 1 particle operator (same spin)
    :r_ijKC:    3 holes 1 particle operator (opposite spin)
    :cia:       the pCCD pair amplitudes (T_p)
    :alpha:     number of unpaired electrons; for alpha=0, the spin-integrated
                equations target all possible m_s=0 states (singlet, triplet,
                quintet), for alpha=1, m_s=1/2 states are accessible (doublet,
                quartet), for alpha=2, m_s=1 states (triplet, quintet), for
                alpha=3, m_s=3/2 states (quartet), and for alpha=4, m_s=2 states
                (quintet)

   Indexing convention:
    :i,j,k,..: occupied orbitals of principal configuration
    :a,b,c,..: virtual orbitals of principal configuration
    :p,q,r,..: general indices (occupied, virtual)

Abbreviations used (if not mentioned in doc-strings; all ERI are in
physicists' notation):
 :<pq||rs>: <pq|rs>-<pq|sr>
 :2h:    2 holes (also used as index _2)
 :3h:    3 holes (also used as index _3)
 :aa:    same-spin component (ss)
 :ab:    opposite-spin component (os)
"""

from typing import Any

import numpy as np

from pybest.auxmat import get_fock_matrix
from pybest.ip_eom.dip_base import RDIPCC2
from pybest.linalg import (
    CholeskyFourIndex,
    DenseFourIndex,
    DenseOneIndex,
    DenseTwoIndex,
)
from pybest.log import timer


class RDIPpCCD2(RDIPCC2):
    """
    Restricted Double Ionization Potential Equation of Motion Coupled Cluster
    class restricted to Double IP for a pCCD reference function and 2 unpaired
    electrons (S_z=1.0 components)

    This class defines only the function that are unique for the DIP-pCCD model
    with 2 unpaired electron:

        * set_hamiltonian (calculates effective Hamiltonian -- at most O(o2v2))
        * compute_h_diag (pre-conditioner used by Davidson)
        * build_subspace_hamiltonian (subspace to be diagonalized)
    """

    long_name = "Double Ionization Potential Equation of Motion pair Coupled Cluster Doubles"
    acronym = "DIP-EOM-pCCD"
    reference = "pCCD"
    order = "DIP"
    alpha = 2

    @timer.with_section("DIPpCCD2: H_diag")
    def compute_h_diag(self, *args: Any) -> DenseOneIndex:
        """Diagonal approximation to Hamiltonian for S_z=1.0 states"""
        h_diag = self.lf.create_one_index(self.dimension, label="h_diag")
        #
        # Get effective Hamiltonian terms
        #
        nacto = self.occ_model.nacto[0]
        goooo = self.from_cache("goooo")
        x1im = self.from_cache("x1im")
        #
        # Get ranges
        #
        end_2h = nacto * (nacto - 1) // 2
        #
        # Intermediates
        #
        lij = x1im.new()
        goooo.contract("abab->ab", out=lij)
        goooo.contract("abba->ab", out=lij, factor=-1.0)
        x1im_ii = x1im.copy_diagonal()
        #
        # H_ij,ij
        #
        h_ij = self.lf.create_two_index(nacto, nacto)
        #
        # x1im(i,i)
        #
        x1im_ii.expand("a->ab", h_ij)
        #
        # <ij||ij>
        #
        h_ij.iadd(lij)
        #
        # Permutation
        #
        h_ij.iadd_t(h_ij, factor=1.0)
        #
        # Assign using mask
        #
        triu = np.triu_indices(nacto, k=1)
        h_diag.assign(h_ij, end0=end_2h, ind1=triu)
        #
        # 3 hole terms
        #
        if self.nhole > 2:
            self.get_3_hole_terms_h_diag(h_diag)
        return h_diag

    def get_3_hole_terms_h_diag(self, h_diag: DenseOneIndex) -> None:
        """Determine all contributions containing three hole operators for
        the spin-dependent representation:
            * H_ijkc,ijkc
            * H_ijKC,ijKC

        **Arguments:**

        h_diag:
            The diagonal elements of the Hamiltonian
        """
        cia = self.checkpoint["t_p"]
        #
        # Get effective Hamiltonian terms
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        goooo = self.from_cache("goooo")
        x1im = self.from_cache("x1im")
        x1cd = self.from_cache("x1cd")
        xjkmN = self.from_cache("xjkmN")
        #
        # Get ranges
        #
        end_2h = nacto * (nacto - 1) // 2
        end_3h = (nacto - 1) * nacto // 2 + nacto * (nacto - 1) * (
            nacto - 2
        ) // 6 * nactv
        #
        # Intermediates
        #
        lij = x1im.new()
        goooo.contract("abab->ab", out=lij)
        goooo.contract("abba->ab", out=lij, factor=-1.0)
        x1ii = x1im.copy_diagonal()
        x1cc = x1cd.copy_diagonal()
        xkcmd = self.from_cache("xkcmd")
        xkckc = xkcmd.contract("abab->ab", out=None)
        if self.dump_cache:
            self.cache.dump("xkcmd")
        xjkjk = xjkmN.contract("abab->ab", out=None)
        xjcmD = self.from_cache("xjcmD")
        xjcjc = xjcmD.contract("abab->ab", out=None)
        if self.dump_cache:
            self.cache.dump("xjcmD")
        goovv = self.from_cache("goovv")
        gjjcc = goovv.contract("aabb->ab", out=None)
        if self.dump_cache:
            self.cache.dump("goovv")
        #
        # H_ijkc,ijkc
        #
        h_ijkc = self.denself.create_four_index(nacto, nacto, nacto, nactv)
        #
        # x1im(k,k)
        #
        x1ii.expand("c->abcd", h_ijkc, factor=1.0)
        #
        # 1/3 x1cd(c,c)
        #
        x1cc.expand("d->abcd", h_ijkc, factor=1 / 3)
        #
        # xkcmd(k,c,k,c)
        #
        xkckc.expand("cd->abcd", h_ijkc, factor=1.0)
        #
        # 0.5 lij
        #
        lij.expand("ab->abcd", h_ijkc, factor=0.5)
        #
        # Permutations
        #
        # create copy first
        tmp = h_ijkc.copy()
        # Pki (ijkc)
        h_ijkc.iadd_transpose((2, 1, 0, 3), other=tmp)
        # Pkj (ijkc)
        h_ijkc.iadd_transpose((0, 2, 1, 3), other=tmp)
        del tmp
        #
        # Assign using mask
        #
        h_diag.assign(
            h_ijkc, begin0=end_2h, end0=end_3h, ind1=self.get_mask(True)
        )
        #
        # H_ijKC,ijKC
        #
        h_ijkc.clear()
        #
        # x1im(k,k)
        #
        x1ii.expand("c->abcd", h_ijkc, factor=0.5)
        #
        # x1im(j,j)
        #
        x1ii.expand("b->abcd", h_ijkc, factor=1.0)
        #
        # 0.5 x1cd(c,c)
        #
        x1cc.expand("d->abcd", h_ijkc, factor=0.5)
        #
        # 0.5 xkcmd(k,c,k,c)
        #
        xkckc.expand("cd->abcd", h_ijkc, factor=0.5)
        #
        # xjkmN(j,k,j,k)
        #
        xjkjk.expand("bc->abcd", h_ijkc, factor=1.0)
        #
        # xjcmd(j,c,j,c)
        #
        xjcjc.expand("bd->abcd", h_ijkc, factor=1.0)
        #
        # 0.25 lij
        #
        lij.expand("ab->abcd", h_ijkc, factor=0.25)
        #
        # gjjcc cjc djk
        #
        gjjcc.imul(cia)
        # create (ijc) intermediate
        tmp_ijc = self.lf.create_three_index(nacto, nacto, nactv)
        gjjcc.expand("bc->abc", tmp_ijc)
        tmp_ijc.expand("abc->abbc", h_ijkc, factor=-1.0)
        #
        # Permutation
        #
        h_ijkc.iadd_transpose((1, 0, 2, 3), factor=1.0)
        #
        # Assign using mask
        #
        h_diag.assign(h_ijkc, begin0=end_3h, ind1=self.get_mask(False))

    @timer.with_section("DIPpCCD2: H_sub")
    def build_subspace_hamiltonian(
        self, b_vector: DenseOneIndex, h_diag: DenseOneIndex, *args: Any
    ) -> DenseOneIndex:
        """
        Used by davidson module to construct subspace Hamiltonian for S_z=1.0

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
        # Get effective Hamiltonian terms
        #
        nacto = self.occ_model.nacto[0]
        x1im = self.from_cache("x1im")
        goooo = self.from_cache("goooo")
        #
        # Calculate sigma vector = (H.b_vector)
        #
        # sigma/b_vector for 2 holes
        # output
        s_2 = self.lf.create_two_index(nacto, nacto)
        to_s_2 = {"out": s_2, "clear": False}
        sigma = self.lf.create_one_index(self.dimension)
        # Input
        b_2 = self.lf.create_two_index(nacto, nacto)
        # Final index of 2 hole terms
        end_2h = (nacto - 1) * nacto // 2
        # Assign R_ij
        triu = np.triu_indices(nacto, k=1)
        b_2.assign(b_vector, ind=triu, end2=end_2h)
        b_2.iadd_t(b_2, factor=-1.0)
        # All terms with P(ij)
        # R_ij
        #
        # (1) x1im(j,m) rim
        #
        b_2.contract("ab,cb->ac", x1im, **to_s_2)
        #
        # (2) 0.25 <ij||mn> rmn
        #
        goooo.contract("abcd,cd->ab", b_2, **to_s_2, factor=0.25)
        goooo.contract("abcd,dc->ab", b_2, **to_s_2, factor=-0.25)
        #
        # R_ijkc/R_ijKC including coupling terms
        #
        if self.nhole > 2:
            self.get_3_hole_terms(b_2, b_vector, s_2, sigma)
        #
        # Permutation P(ij)
        #
        s_2.iadd_t(s_2, factor=-1.0)
        #
        # Assign to sigma vector
        #
        sigma.assign(s_2, end0=end_2h, ind1=triu)

        return sigma

    def get_3_hole_terms(
        self,
        b_2: DenseTwoIndex,
        b_vector: DenseOneIndex,
        s_2: DenseTwoIndex,
        sigma: DenseOneIndex,
    ) -> None:
        """Determine all contributions containing three hole operators for
        the spin-dependent representation:
            * coupling terms to R_ij
            * R_ijkc
            * R_ijKC

        **Arguments:**

        b_2, b_vector:
            b vectors used in Davidson diagonalization

        s_2, sigma:
            sigma vectors used in Davidson diagonalization
        """
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        #
        # Calculate sigma vector = (H.b_vector)
        # sigma/b_vector for 3 holes
        # output
        s_3 = self.denself.create_four_index(nacto, nacto, nacto, nactv)
        # Input
        b_3aa = self.denself.create_four_index(nacto, nacto, nacto, nactv)
        b_3ab = self.denself.create_four_index(nacto, nacto, nacto, nactv)
        #
        # Final indices of 2 and 3 hole operator blocks
        #
        end_2h = (nacto - 1) * nacto // 2
        end_3h = (nacto - 1) * nacto // 2 + nacto * (nacto - 1) * (
            nacto - 2
        ) // 6 * nactv
        #
        # Assign R_ijkc
        #
        mask = self.get_index_of_mask(True)
        b_3aa.assign(b_vector, ind=mask, begin4=end_2h, end4=end_3h)
        # create tmp object to account for symmetry
        tmp = b_3aa.copy()
        b_3aa.iadd_transpose((1, 0, 2, 3), other=tmp, factor=-1.0)
        b_3aa.iadd_transpose((0, 2, 1, 3), other=tmp, factor=-1.0)
        b_3aa.iadd_transpose((2, 1, 0, 3), other=tmp, factor=-1.0)
        b_3aa.iadd_transpose((1, 2, 0, 3), other=tmp, factor=1.0)
        b_3aa.iadd_transpose((2, 0, 1, 3), other=tmp, factor=1.0)
        del tmp
        #
        # Assign R_ijKC
        #
        mask = self.get_index_of_mask(False)
        b_3ab.assign(b_vector, ind=mask, begin4=end_3h)
        # Account for symmetry
        b_3ab.iadd_transpose((1, 0, 2, 3), factor=-1.0)
        #
        # Get coupling terms to R_ij
        #
        self.get_3_hole_r_ij_terms(b_3aa, b_3ab, s_2)
        #
        # R_ijkc
        #
        self.get_3_hole_r_3ss_terms(b_2, b_3aa, b_3ab, s_3)
        # Assign to sigma vector using mask
        sigma.assign(s_3, begin0=end_2h, end0=end_3h, ind1=self.get_mask(True))
        #
        # R_ijKC
        #
        self.get_3_hole_r_3os_terms(b_2, b_3aa, b_3ab, s_3)
        # Assign to sigma vector using mask
        sigma.assign(s_3, begin0=end_3h, ind1=self.get_mask(False))

    def get_3_hole_r_ij_terms(
        self, b_3aa: DenseFourIndex, b_3ab: DenseFourIndex, s_2: DenseTwoIndex
    ) -> None:
        """Determine all contributions containing two particle operators:
            * coupling terms to R_iJ

        **Arguments:**

        b_3aa, b_3ab:
            b vectors of different R operators used in Davidson diagonalization

        s_2:
            sigma vector corresponding to R_ij used in Davidson diagonalization
        """
        to_s_2 = {"out": s_2, "clear": False}
        #
        # Get effective Hamiltonian terms
        #
        fock = self.from_cache("fock")
        gooov = self.from_cache("gooov")
        ov4 = self.get_range("ov", start=4)
        #
        # (3) 0.5 fmd (rijmd + rijMD) (factor due to P(ij))
        #
        b_3aa.contract("abcd,cd->ab", fock, **to_s_2, **ov4, factor=0.5)
        b_3ab.contract("abcd,cd->ab", fock, **to_s_2, **ov4, factor=0.5)
        #
        # (4) - 0.5 <nm||jd> rinmd - <nm|jd> rinMD
        #
        b_3aa.contract("abcd,bced->ae", gooov, **to_s_2, factor=-0.5)
        b_3aa.contract("abcd,cbed->ae", gooov, **to_s_2, factor=0.5)
        b_3ab.contract("abcd,bced->ae", gooov, **to_s_2, factor=-1.0)

    def get_3_hole_r_3ss_terms(
        self,
        b_2: DenseTwoIndex,
        b_3aa: DenseFourIndex,
        b_3ab: DenseFourIndex,
        s_3: DenseFourIndex,
    ) -> None:
        """Determine all contributions containing two particle operators:
            * R_iJkc

        **Arguments:**

        b_3aa, b_3ab:
            b vectors of different R operators used in Davidson diagonalization

        s_3:
            sigma vector corresponding to R_ijkc used in Davidson diagonalization
        """
        cia = self.checkpoint["t_p"]
        s_3.clear()
        to_s_3 = {"out": s_3, "clear": False}
        #
        # Get effective Hamiltonian terms
        #
        x1im = self.from_cache("x1im")
        x1cd = self.from_cache("x1cd")
        goooo = self.from_cache("goooo")
        gooov = self.from_cache("gooov")
        # All terms with P(k/ij)
        # (1)
        # -<ij||mc> rkm
        gooov.contract("abcd,ec->abed", b_2, **to_s_3, factor=-1.0)
        gooov.contract("abcd,ec->baed", b_2, **to_s_3, factor=1.0)
        # -<jk|mc> ckc rim
        tmp = gooov.contract("abcd,bd->abcd", cia, out=None)
        # -(jkmc) rim
        tmp.contract("abcd,ec->eabd", b_2, **to_s_3, factor=-1.0)
        # <ik|mc> ckc rjm
        # (ikmc) rjm
        tmp.contract("abcd,ec->aebd", b_2, **to_s_3, factor=1.0)
        del tmp
        #
        # (3) x1im(k,m) rijmc
        #
        b_3aa.contract("abcd,ec->abed", x1im, **to_s_3)
        #
        # (4) 1/3 rijkd x1cd
        #
        b_3aa.contract("abcd,ed->abce", x1cd, **to_s_3, factor=1 / 3)
        #
        # (5) xkcmd rijmd + xkcMD rijMD
        #
        xkcmd = self.from_cache("xkcmd")
        b_3aa.contract("abcd,efcd->abef", xkcmd, **to_s_3)
        if self.dump_cache:
            self.cache.dump("xkcmd")
        xkcMD = self.from_cache("xkcMD")
        b_3ab.contract("abcd,efcd->abef", xkcMD, **to_s_3)
        if self.dump_cache:
            self.cache.dump("xkcMD")
        #
        # (6) 0.5 <ij||mn> rmnkc
        #
        goooo.contract("abcd,cdef->abef", b_3aa, **to_s_3, factor=0.5)
        goooo.contract("abcd,dcef->abef", b_3aa, **to_s_3, factor=-0.5)
        #
        # Permutation P(k/ij)
        # create copy first
        tmp = s_3.copy()
        s_3.iadd_transpose((2, 1, 0, 3), other=tmp, factor=-1.0)
        # - Pkj (ijkc)
        s_3.iadd_transpose((0, 2, 1, 3), other=tmp, factor=-1.0)
        del tmp

    def get_3_hole_r_3os_terms(
        self,
        b_2: DenseTwoIndex,
        b_3aa: DenseFourIndex,
        b_3ab: DenseFourIndex,
        s_3: DenseFourIndex,
    ) -> None:
        """Determine all contributions containing two particle operators:
            * R_ijKC

        **Arguments:**

        b_3aa, b_3ab:
            b vectors of different R operators used in Davidson diagonalization

        s_3:
            sigma vector corresponding to R_ijKC used in Davidson diagonalization
        """
        cia = self.checkpoint["t_p"]
        s_3.clear()
        to_s_3 = {"out": s_3, "clear": False}
        #
        # Get effective Hamiltonian terms
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        x1im = self.from_cache("x1im")
        x1cd = self.from_cache("x1cd")
        goooo = self.from_cache("goooo")
        gooov = self.from_cache("gooov")
        xjkcm = self.from_cache("xjkcm")
        xjkmN = self.from_cache("xjkmN")
        # All terms with P(ij)
        # (1) xjkcm rim
        #
        b_2.contract("ab,cdeb->acde", xjkcm, **to_s_3)
        #
        # (3) 0.5 x1im(k,m) rijMC
        #
        b_3ab.contract("abcd,ec->abed", x1im, **to_s_3, factor=0.5)
        #
        # (4) 0.5 x1cd rijKD
        #
        b_3ab.contract("abcd,ed->abce", x1cd, **to_s_3, factor=0.5)
        #
        # (5) x1im(j,m) rimKC
        #
        b_3ab.contract("abcd,eb->aecd", x1im, **to_s_3)
        #
        # (6) 0.5 xkcMD rijmd + 0.5 xkcmd rijMD + xjcmD rimKD
        #
        xkcMD = self.from_cache("xkcMD")
        b_3aa.contract("abcd,efcd->abef", xkcMD, **to_s_3, factor=0.5)
        if self.dump_cache:
            self.cache.dump("xkcMD")
        xkcmd = self.from_cache("xkcmd")
        b_3ab.contract("abcd,efcd->abef", xkcmd, **to_s_3, factor=0.5)
        if self.dump_cache:
            self.cache.dump("xkcmd")
        xjcmD = self.from_cache("xjcmD")
        b_3ab.contract("abcd,efbd->aecf", xjcmD, **to_s_3)
        if self.dump_cache:
            self.cache.dump("xjcmD")
        #
        # (7) 0.25 <ij||mn> rmnKC
        #
        goooo.contract("abcd,cdef->abef", b_3ab, **to_s_3, factor=0.25)
        goooo.contract("abcd,cdef->baef", b_3ab, **to_s_3, factor=-0.25)
        #
        # (8) xjkmN rimNC
        #
        xjkmN.contract("abcd,ecdf->eabf", b_3ab, **to_s_3)
        #
        # djk terms
        #
        tmp_ic = self.lf.create_two_index(nacto, nactv)
        to_tmp = {"out": tmp_ic, "clear": False}
        #
        # (2) 0.5 <ml||ic> rml cjc djk -> (ic, cjc) -> (ijc)
        #
        gooov.contract("abcd,ab->cd", b_2, **to_tmp, factor=0.5)
        gooov.contract("abcd,ba->cd", b_2, **to_tmp, factor=-0.5)
        #
        # (9) -0.5<nm||cd> rinmd cjc dkj -> (ic, cjc) -> (ijc)
        #     -   <nm| cd> rinMD cjc dkj -> (ic, cjc) -> (ijc)
        #
        goovv = self.from_cache("goovv")
        b_3aa.contract("abcd,bced->ae", goovv, **to_tmp, factor=-0.5)
        b_3aa.contract("abcd,bcde->ae", goovv, **to_tmp, factor=0.5)
        b_3ab.contract("abcd,bced->ae", goovv, **to_tmp, factor=-1.0)
        if self.dump_cache:
            self.cache.dump("goovv")
        #
        # tmpic cjc -> (ijc)
        #
        tmp_ijc = self.lf.create_three_index(nacto, nacto, nactv)
        tmp_ic.contract("ac,bc->abc", cia, tmp_ijc)
        del tmp_ic
        #
        # Expand indices
        #
        tmp_ijc.expand("abc->abbc", s_3)
        #
        # Permutation P(ij)
        #
        s_3.iadd_transpose((1, 0, 2, 3), factor=-1.0)

    @timer.with_section("DIPpCCD2: H_eff")
    def set_hamiltonian(self, mo1: DenseTwoIndex, mo2: DenseFourIndex) -> None:
        """Derive all auxiliary matrices. Like
        fock_pq/f:     mo1_pq + sum_m(2<pm|qm> - <pm|mq>),

        **Arguments:**

        mo1, mo2
             one- and two-electron integrals.
        """
        cia = self.checkpoint["t_p"]
        nacto, nact = self.occ_model.nacto[0], self.occ_model.nact[0]
        #
        # Get ranges
        #
        oooo = self.get_range("oooo")
        oovv = self.get_range("oovv")
        # optimize contractions
        opt = "td" if isinstance(mo2, CholeskyFourIndex) else None
        #
        # Inactive Fock matrix
        #
        fock = self.init_cache("fock", nact, nact)
        get_fock_matrix(fock, mo1, mo2, nacto)
        #
        # goooo
        #
        goooo = self.init_cache("goooo", nacto, nacto, nacto, nacto)
        mo2.contract("abcd->abcd", goooo, **oooo)
        #
        # x1im
        #
        x1im = self.init_cache("x1im", nacto, nacto)
        # -fim
        x1im.iadd(fock, -1.0, end2=nacto, end3=nacto)
        # -<im|ee> cie
        mo2.contract("abcc,ac->ab", cia, x1im, factor=-1.0, select=opt, **oovv)
        #
        # 3 hole terms
        #
        if self.nhole > 2:
            self.set_hamiltonian_3_hole(fock, goooo, mo2)
        #
        # Clean up
        #
        mo1.__del__()
        mo2.__del__()

    def set_hamiltonian_3_hole(
        self, fock: DenseTwoIndex, goooo: DenseFourIndex, mo2: DenseFourIndex
    ) -> None:
        """Derive all effective Hamiltonian terms for 3 hole operators

        **Arguments:**

        fock, mo2
            Fock matrix and two-electron integrals.
        """
        cia = self.checkpoint["t_p"]
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        #
        # Get ranges
        #
        vo2 = self.get_range("vo", start=2)
        ooov = self.get_range("ooov")
        oovv = self.get_range("oovv")
        ovov = self.get_range("ovov")
        ovvo = self.get_range("ovvo")
        vovv = self.get_range("vovv")
        #
        # goovv (also used below for some contractions)
        #
        goovv = self.init_cache("goovv", nacto, nacto, nactv, nactv)
        mo2.contract("abcd->abcd", goovv, **oovv)
        if self.dump_cache:
            self.cache.dump("goovv")
        #
        # x1cd
        #
        x1cd = self.init_cache("x1cd", nactv, nactv)
        # fcd
        x1cd.iadd(fock, 1.0, begin2=nacto, begin3=nacto)
        # -<kk|cd> ckc
        tmp = mo2.contract("aabc->abc", out=None, **oovv)
        tmp.contract("abc,ab->bc", cia, x1cd, factor=-1.0)
        #
        # gooov
        #
        gooov = self.init_cache("gooov", nacto, nacto, nacto, nactv)
        mo2.contract("abcd->abcd", gooov, **ooov)
        #
        # xjkcm
        #
        xjkcm = self.init_cache("xjkcm", nacto, nacto, nactv, nacto)
        # -<jk|mc>
        mo2.contract("abcd->abdc", xjkcm, factor=-1.0, **ooov)
        # -<mk||jc> ckc
        gooov.contract("abcd,bd->cbda", cia, xjkcm, factor=-1.0)
        gooov.contract("abcd,ad->cadb", cia, xjkcm, factor=1.0)
        # <jm|kc> cjc
        gooov.contract("abcd,ad->acdb", cia, xjkcm)
        # -fcm ckc dkj
        tmp = cia.contract("ab,bc->abc", fock, out=None, factor=-1.0, **vo2)
        # -<cm|dd> ckd dkj
        mo2.contract("abcc,dc->dab", cia, tmp, factor=-1.0, **vovv)
        tmp.expand("abc->aabc", xjkcm)
        #
        # xkcmd
        #
        xkcmd = self.init_cache("xkcmd", nacto, nactv, nacto, nactv)
        # <kd||cm>
        mo2.contract("abcd->acdb", xkcmd, **ovvo)
        mo2.contract("abcd->adcb", xkcmd, factor=-1.0, **ovov)
        # <kd|cm> ckc
        mo2.contract("abcd,ac->acdb", cia, xkcmd, **ovvo)
        if self.dump_cache:
            self.cache.dump("xkcmd")
        #
        # xkcMD
        #
        xkcMD = self.init_cache("xkcMD", nacto, nactv, nacto, nactv)
        # <kd|cm>
        mo2.contract("abcd->acdb", xkcMD, **ovvo)
        # <km||cd> ckc
        mo2.contract("abcd,ac->acbd", cia, xkcMD, **oovv)
        mo2.contract("abcd,ad->adbc", cia, xkcMD, factor=-1.0, **oovv)
        if self.dump_cache:
            self.cache.dump("xkcMD")
        #
        # xjcmD
        #
        xjcmD = self.init_cache("xjcmD", nacto, nactv, nacto, nactv)
        # -<jc|md>
        mo2.contract("abcd->abcd", xjcmD, factor=-1.0, **ovov)
        # <jm|dc> cjc
        mo2.contract("abcd,ad->adbc", cia, xjcmD, **oovv)
        if self.dump_cache:
            self.cache.dump("xjcmD")
        #
        # xjkmN
        #
        xjkmN = self.init_cache("xjkmN", nacto, nacto, nacto, nacto)
        # <jk|mn>
        xjkmN.iadd(goooo, factor=1.0)
        # -<mn|dd> ckd dkj (kmn)
        tmp_abcc = mo2.contract("abcc->abc", out=None, **oovv)
        tmp = tmp_abcc.contract("abc,dc->dab", cia, out=None)
        tmp.expand("abc->aabc", xjkmN)
        del tmp, tmp_abcc
