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

"""Double Ionization Potential Equation of Motion Coupled Cluster implementations for
a CCD reference function

Variables used in this module:
:ncore:     number of frozen core orbitals
:nocc:      number of occupied orbitals in the principal configuration
:nacto:     number of active occupied orbitals in the principal configuration
:nvirt:     number of virtual orbitals in the principal configuration
:nactv:     number of active virtual orbitals in the principal configuration
:nbasis:    total number of basis functions
:nact:      total number of active orbitals (nacto+nactv)
:e_ip:      the energy correction for DIP
:civ_ip:    the CI amplitudes from a given EOM model
:alpha:     number of unpaired electrons; for alpha=0, the spin-integrated
equations target all possible m_s=0 states (singlet, triplet,
quintet), for alpha=1, m_s=1/2 states are accessible (doublet,
quartet), for alpha=2, m_s=1 states (triplet, quintet), for
alpha=3, m_s=3/2 states (quartet), and for alpha=4, m_s=2 states
(quintet)
:cia:       the pCCD pair amplitudes (T_p)

Indexing convention:
:i,j,k,..: occupied orbitals of principal configuration
:a,b,c,..: virtual orbitals of principal configuration
:p,q,r,..: general indices (occupied, virtual)

Abbreviations used (if not mentioned in doc-strings; all ERI are in
physicists' notation):
:<pq||rs>: <pq|rs>-<pq|sr>
"""

from functools import partial
from typing import Any

import numpy as np

from pybest.auxmat import get_fock_matrix
from pybest.ip_eom.dip_base import RDIPCC0
from pybest.linalg import (
    CholeskyFourIndex,
    DenseFourIndex,
    DenseOneIndex,
    DenseTwoIndex,
)
from pybest.log import timer


class RDIPCCD0(RDIPCC0):
    """
    Restricted Double Ionization Potential Equation of Motion Coupled Cluster
    class restricted to Double IP for a CCD reference function and (0,2,4)
    unpaired electron(s) (S_z = 0.0)

    This class defines only the function that are universal for the DIP-CCD model
    with (0,2,4) unpaired electron(s):

        * set_hamiltonian (calculates effective Hamiltonian -- at most O(o2v2))
        * compute_h_diag (pre-conditioner used by Davidson)
        * build_subspace_hamiltonian (subspace to be diagonalized)

    Note that the R_ijb and R_iJB blocks are considered together. Thus, setting
    the number of hole operators equal to 2, requires at least 2 active
    occupied orbitals.
    """

    long_name = "Double Ionization Potential Equation of Motion Coupled Cluster Doubles"
    acronym = "DIP-EOM-CCD"
    reference = "CCD"
    order = "DIP"
    alpha = 0
    disconnected_t1 = False

    @timer.with_section("DIPCCD0: H_diag")
    def compute_h_diag(self, *args: Any) -> DenseOneIndex:
        """Used by the Davidson module for pre-conditioning

        **Arguments:**

        args:
            required for the Davidson module (not used here)
        """
        h_diag = self.lf.create_one_index(self.dimension, label="h_diag")
        #
        # Get effective Hamiltonian terms
        #
        nacto = self.occ_model.nacto[0]
        x1im = self.from_cache("x1im")
        xiJmN = self.from_cache("xiJmN")
        #
        # Intermediates
        #
        x1im_diag = x1im.copy_diagonal()
        xiJiJ = xiJmN.contract("abab->ab", out=None)
        #
        # H_iJ,iJ
        #
        h_iJ = self.lf.create_two_index(nacto, nacto)
        #
        # x1im(i,i)
        #
        x1im_diag.expand("a->ab", h_iJ)
        x1im_diag.expand("b->ab", h_iJ)
        #
        # xiJmn(i,j)
        #
        h_iJ.iadd(xiJiJ)
        #
        # Assign using mask
        #
        h_diag.assign(h_iJ.ravel(), end0=nacto * nacto)
        #
        # H_iJkc,iJkc and H_iJKC,iJKC
        #
        if self.nhole > 2:
            self.get_3_hole_terms_h_diag(h_diag)
        return h_diag

    def get_3_hole_terms_h_diag(self, h_diag: DenseOneIndex) -> None:
        """Determine all contributions containing three hole operators for
        the spin-dependent representation:
            * H_iJkc,iJkc
            * H_iJKC,iJKC

        **Arguments:**

        h_diag:
            The diagonal elements of the Hamiltonian
        """
        t_2 = self.checkpoint["t_2"]
        #
        # Get effective Hamiltonian terms
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        x1im = self.from_cache("x1im")
        x4bd = self.from_cache("x4bd")
        xiklm = self.from_cache("xiklm")
        xiJmN = self.from_cache("xiJmN")
        #
        # Intermediates
        #
        x1im_diag = x1im.copy_diagonal()
        x4bd_diag = x4bd.copy_diagonal()
        xijij = xiklm.contract("abab->ab")
        xkcMD = self.from_cache("xkcMD")
        xjbjb = xkcMD.contract("abab->ab")
        if self.dump_cache:
            self.cache.dump("xkcMD")
        xiCmD = self.from_cache("xiCmD")
        xiCmD.contract("abab->ab", xjbjb)
        xibib = xiCmD.contract("abab->ab")
        if self.dump_cache:
            self.cache.dump("xiCmD")
        xiJiJ = xiJmN.contract("abab->ab")
        #
        # Get ranges
        #
        end_2h = nacto * nacto
        end_3h = end_2h + nacto * (nacto - 1) // 2 * nacto * nactv
        #
        # H_iJkc,iJkc
        #
        H_iJkc = self.denself.create_four_index(nacto, nacto, nacto, nactv)
        #
        # x1im(k,k)
        #
        x1im_diag.expand("c->abcd", H_iJkc, factor=1.0)
        #
        # 0.5 x1im(j,j)
        #
        x1im_diag.expand("b->abcd", H_iJkc, factor=0.5)
        #
        # 0.5 x1cd(c,c)
        #
        x4bd_diag.expand("d->abcd", H_iJkc, factor=0.5)
        #
        # xiCmD(k,c,k,c) + xkcMD(k,c,k,c)
        #
        xjbjb.expand("cd->abcd", H_iJkc, factor=1.0)
        #
        # 0.5 xiCmD(j,c,j,c)
        #
        xibib.expand("bd->abcd", H_iJkc, factor=0.5)
        #
        # xiJmN(i,j,i,j)
        #
        xiJiJ.expand("ab->abcd", H_iJkc, factor=1.0)
        #
        # xiklm(i,k,i,k)
        #
        xijij.expand("ac->abcd", H_iJkc, factor=1.0)
        #
        # - <Jk| Ec> tjekc - 0.25 <ik||ec> (tiekc-tkeic)
        # (jkc) + (ikc)
        goovv = self.from_cache("goovv")
        tmp = goovv.contract("abcd,acbd->abd", t_2)
        tmp.expand("bcd->abcd", H_iJkc, factor=-1.0)
        goovv.contract("abcd,adbc->abc", t_2, tmp, factor=-1.0)
        goovv.contract("abcd,bcad->abd", t_2, tmp, factor=-1.0)
        goovv.contract("abcd,bdac->abc", t_2, tmp, factor=1.0)
        tmp.expand("acd->abcd", H_iJkc, factor=-0.25)
        # Do not dump the Cholesky object as it is stored as a view
        if self.dump_cache and not isinstance(goovv, CholeskyFourIndex):
            self.cache.dump("goovv")
        #
        # Pki (ijkc)
        #
        H_iJkc.iadd_transpose((2, 1, 0, 3))
        #
        # Assign using mask
        #
        h_diag.assign(
            H_iJkc, begin0=end_2h, end0=end_3h, ind1=self.get_mask(True)
        )
        #
        # H_iJKC,iJKC
        #
        H_iJkc.clear()
        #
        # x1im(k,k)
        #
        x1im_diag.expand("c->abcd", H_iJkc, factor=1.0)
        #
        # 0.5 x1im(i,i)
        #
        x1im_diag.expand("a->abcd", H_iJkc, factor=0.5)
        #
        # 0.5 x1cd(c,c)
        #
        x4bd_diag.expand("d->abcd", H_iJkc, factor=0.5)
        #
        # xiCmD(k,c,k,c) + xkcMD(k,c,k,c)
        #
        xjbjb.expand("cd->abcd", H_iJkc, factor=1.0)
        #
        # 0.5 xiCmD(i,c,i,c)
        #
        xibib.expand("ad->abcd", H_iJkc, factor=0.5)
        #
        # xiJmN(i,j,i,j)
        #
        xiJiJ.expand("ab->abcd", H_iJkc, factor=1.0)
        #
        # xiklm(j,k,j,k)
        #
        xijij.expand("bc->abcd", H_iJkc, factor=1.0)
        #
        # - <ik| Ec> tiekc - 0.25 <jk||ec> (tjekc-tkejc)
        # (ikc) + (jkc)
        goovv = self.from_cache("goovv")
        tmp = goovv.contract("abcd,acbd->abd", t_2)
        tmp.expand("acd->abcd", H_iJkc, factor=-1.0)
        goovv.contract("abcd,adbc->abc", t_2, tmp, factor=-1.0)
        goovv.contract("abcd,bcad->abd", t_2, tmp, factor=-1.0)
        goovv.contract("abcd,bdac->abc", t_2, tmp, factor=1.0)
        tmp.expand("bcd->abcd", H_iJkc, factor=-0.25)
        # Do not dump the Cholesky object as it is stored as a view
        if self.dump_cache and not isinstance(goovv, CholeskyFourIndex):
            self.cache.dump("goovv")
        #
        # Permutation (kj)
        #
        H_iJkc.iadd_transpose((0, 2, 1, 3), factor=1.0)
        #
        # Assign using mask
        #
        h_diag.assign(H_iJkc, begin0=end_3h, ind1=self.get_mask(False))

    @timer.with_section("DIPCCD0: H_sub")
    def build_subspace_hamiltonian(
        self, b_vector: DenseOneIndex, h_diag: DenseOneIndex, *args: Any
    ) -> DenseOneIndex:
        """
        Used by the Davidson module to construct subspace Hamiltonian

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
        # Get effective Hamiltonian terms
        # We load only arrays of a maximum size of o3v, everything bigger than
        # o2v2 is dumped/loaded to/from disk if self.dump_cache = True
        #
        nacto = self.occ_model.nacto[0]
        #
        # Final index of 2 hole terms
        #
        end_2h = nacto * nacto
        #
        # Calculate sigma vector = (H.b_vector)
        #
        # sigma/b_vector for 2 holes
        # output
        s_2 = self.lf.create_two_index(nacto, nacto)
        to_s_2 = {"out": s_2, "clear": False}
        sigma = self.lf.create_one_index(self.dimension)
        # Input, assign R_iJ
        b_2 = self.lf.create_two_index(nacto, nacto)
        b_2.assign(b_vector, end2=end_2h)
        #
        # R_iJ
        #
        # (1) x1im(i,m) rmJ / rim x1im(j,m)
        #
        x1im = self.from_cache("x1im")
        x1im.contract("ab,bc->ac", b_2, **to_s_2)
        b_2.contract("ab,cb->ac", x1im, **to_s_2)
        #
        # (2) xiJmN rmN
        #
        xiJmN = self.from_cache("xiJmN")
        xiJmN.contract("abcd,cd->ab", b_2, **to_s_2)
        #
        # R_iJkc/R_iJKC including coupling terms
        #
        if self.nhole > 2:
            self.get_3_hole_terms(b_2, b_vector, s_2, sigma)
        #
        # Assign to sigma vector
        #
        sigma.assign(s_2.ravel(), end0=end_2h)
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
            * coupling terms to R_iJ
            * R_iJkc
            * R_iJKC

        **Arguments:**

        b_2, b_vector:
            b vectors used in Davidson diagonalization

        s_2, sigma:
            sigma vectors used in Davidson diagonalization
        """
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        #
        # Calculate sigma vector = (H.b_vector)_kc
        # sigma/b_vector for 3 holes
        # output
        s_3 = self.denself.create_four_index(nacto, nacto, nacto, nactv)
        # Input
        b_3aa = self.denself.create_four_index(nacto, nacto, nacto, nactv)
        b_3ab = self.denself.create_four_index(nacto, nacto, nacto, nactv)
        #
        # Final indices of 2 and 3 hole operator blocks
        #
        end_2h = nacto * nacto
        end_3h = end_2h + nacto * nacto * (nacto - 1) // 2 * nactv
        #
        # Assign R_iJkc
        #
        mask = self.get_index_of_mask(True)
        b_3aa.assign(b_vector, ind=mask, begin4=end_2h, end4=end_3h)
        # Account for symmetry (ik)
        b_3aa.iadd_transpose((2, 1, 0, 3), factor=-1.0)
        #
        # Assign R_iJKC
        #
        mask = self.get_index_of_mask(False)
        b_3ab.assign(b_vector, ind=mask, begin4=end_3h)
        # Account for symmetry (JK)
        b_3ab.iadd_transpose((0, 2, 1, 3), factor=-1.0)
        #
        # Get coupling terms to R_iJ
        #
        self.get_3_hole_r_iJ_terms(b_3aa, b_3ab, s_2)
        #
        # R_iJkc
        #
        self.get_3_hole_r_3ss_terms(b_2, b_3aa, b_3ab, s_3)
        # Assign to sigma vector using mask
        sigma.assign(s_3, begin0=end_2h, end0=end_3h, ind1=self.get_mask(True))
        #
        # R_iJKC
        #
        self.get_3_hole_r_3os_terms(b_2, b_3aa, b_3ab, s_3)
        # Assign to sigma vector using mask
        sigma.assign(s_3, begin0=end_3h, ind1=self.get_mask(False))

    def get_3_hole_r_iJ_terms(
        self, b_3aa: DenseFourIndex, b_3ab: DenseFourIndex, s_2: DenseTwoIndex
    ) -> None:
        """Determine all contributions containing three hole operators:
            * coupling terms to R_iJ

        **Arguments:**

        b_3aa, b_3ab:
            b vectors of different R operators used in the Davidson diagonalization

        s_2:
            sigma vector corresponding to R_iJ used in the Davidson diagonalization
        """
        to_s_2 = {"out": s_2, "clear": False}
        #
        # Get effective Hamiltonian terms
        #
        xkc = self.from_cache("xkc")
        ximkc = self.from_cache("ximkc")
        ximKC = self.from_cache("ximKC")
        #
        # (3) rijmd xkc(m,d) + riJMD xkc(m,d)
        #
        b_3aa.contract("abcd,cd->ab", xkc, **to_s_2)
        b_3ab.contract("abcd,cd->ab", xkc, **to_s_2)
        #
        # (4)
        # riMkc ximKC(j,m,k,c)
        b_3aa.contract("abcd,ebcd->ae", ximKC, **to_s_2)
        # riMKC ximkc(j,m,k,c)
        b_3ab.contract("abcd,ebcd->ae", ximkc, **to_s_2)
        # ximkc rmJkc
        ximkc.contract("abcd,becd->ae", b_3aa, **to_s_2)
        # ximKC rmJKC
        ximKC.contract("abcd,becd->ae", b_3ab, **to_s_2)

    def get_3_hole_r_3ss_terms(
        self,
        b_2: DenseTwoIndex,
        b_3aa: DenseFourIndex,
        b_3ab: DenseFourIndex,
        s_3: DenseFourIndex,
    ) -> None:
        """Determine all contributions containing three hole operators:
            * R_iJkc

        **Arguments:**

        b_3aa, b_3ab:
            b vectors of different R operators used in Davidson diagonalization

        s_3:
            sigma vector corresponding to R_iJkc used in Davidson diagonalization
        """
        s_3.clear()
        to_s_3 = {"out": s_3, "clear": False}
        t_2 = self.checkpoint["t_2"]
        #
        # Get effective Hamiltonian terms
        #
        x1im = self.from_cache("x1im")
        xJkcM = self.from_cache("xJkcM")
        xikcm = self.from_cache("xikcm")
        x4bd = self.from_cache("x4bd")
        xiklm = self.from_cache("xiklm")
        xiJmN = self.from_cache("xiJmN")
        gooov = self.from_cache("gooov")
        # All terms with P(ik)
        # (1) xJkcM(j,k,c,m) riM + xikcm(i,k,c,m) rmJ
        #
        xJkcM.contract("abcd,ed->eabc", b_2, **to_s_3)
        xikcm.contract("abcd,de->aebc", b_2, **to_s_3)
        #
        # (2) rlM [
        #   + <lM|iD> tkcJD     + 0.5 <lM|dJ> (tidkc - tkdic)
        # ]
        #
        # (id) = <lM|iD> rlM
        tmp = gooov.contract("abcd,ab->cd", b_2)
        # (id) tkcJD
        t_2.contract("abcd,ed->ecab", tmp, **to_s_3)
        # (jd) <Ml|Jd> rlM
        tmp = gooov.contract("abcd,ba->cd", b_2)
        # 0.5 (jd) (tidkc - tkdic)
        t_2.contract("abcd,eb->aecd", tmp, **to_s_3, factor=0.5)
        t_2.contract("abcd,eb->cead", tmp, **to_s_3, factor=-0.5)
        #
        # (3+5) x1im(k,m) riJmc + 0.5 x1im(j,m) riMkc
        #
        b_3aa.contract("abcd,ec->abed", x1im, **to_s_3)
        b_3aa.contract("abcd,eb->aecd", x1im, **to_s_3, factor=0.5)
        #
        # (4) 0.5 x4bd(c,d) riJkd
        #
        b_3aa.contract("abcd,ed->abce", x4bd, **to_s_3, factor=0.5)
        #
        # (6) (xiCmD+xkcMD)(k,c,m,d) riJmd + xkcMD(k,c,M,D) riJMD + 0.5 xiCmD(j,c,m,d) riMkd
        #
        xiCmD = self.from_cache("xiCmD")
        b_3aa.contract("abcd,efcd->abef", xiCmD, **to_s_3)
        b_3aa.contract("abcd,efbd->aecf", xiCmD, **to_s_3, factor=0.5)
        if self.dump_cache:
            self.cache.dump("xiCmD")
        xkcMD = self.from_cache("xkcMD")
        b_3aa.contract("abcd,efcd->abef", xkcMD, **to_s_3)
        b_3ab.contract("abcd,efcd->abef", xkcMD, **to_s_3)
        if self.dump_cache:
            self.cache.dump("xkcMD")
        #
        # (7+8) xiJmN(i,j,l,m) rlMkc + xiklm(i,k,l,m) rlJmc
        #
        xiJmN.contract("abcd,cdef->abef", b_3aa, **to_s_3)
        xiklm.contract("abcd,cedf->aebf", b_3aa, **to_s_3)
        #
        # (9) -0.5<ml||ed> riMLD tkcJE  - 0.25 <ml||ed> rmJld (tiekc - tkeic)
        #     -   <ml| ed> riMld tkcJE  - 0.5  <ml| ed> rmJLD (tiekc - tkeic)
        #
        goovv = self.from_cache("goovv")
        # tmp(ie) = -0.5<ml||ed> riMLD - <ml|ed> riMld
        tmp = b_3ab.contract("abcd,bced->ae", goovv, factor=-0.5)
        b_3ab.contract("abcd,bcde->ae", goovv, tmp, factor=0.5)
        b_3aa.contract("abcd,bced->ae", goovv, tmp, factor=-1.0)
        # tmp(ie) tkcJE
        t_2.contract("abcd,ed->ecab", tmp, **to_s_3)
        # tmp(je) = -0.25<ml||ed> rmJld - 0.5 <ml|ed> rmJLD
        tmp = b_3aa.contract("abcd,aced->be", goovv, factor=-0.25)
        b_3aa.contract("abcd,acde->be", goovv, tmp, factor=0.25)
        b_3ab.contract("abcd,aced->be", goovv, tmp, factor=-0.5)
        # Do not dump the Cholesky object as it is stored as a view
        if self.dump_cache and not isinstance(goovv, CholeskyFourIndex):
            self.cache.dump("goovv")
        # tmp(je) (tiekc - tkeic)
        t_2.contract("abcd,eb->aecd", tmp, **to_s_3)
        t_2.contract("abcd,eb->cead", tmp, **to_s_3, factor=-1.0)
        #
        # Permutation P(ki)
        #
        s_3.iadd_transpose((2, 1, 0, 3), factor=-1.0)

    def get_3_hole_r_3os_terms(
        self,
        b_2: DenseTwoIndex,
        b_3aa: DenseFourIndex,
        b_3ab: DenseFourIndex,
        s_3: DenseFourIndex,
    ) -> None:
        """Determine all contributions containing three hole operators:
            * R_iJKC

        **Arguments:**

        b_3aa, b_3ab:
            b vectors of different R operators used in Davidson diagonalization

        s_3:
            sigma vector corresponding to R_iJKC used in Davidson diagonalization
        """
        s_3.clear()
        to_s_3 = {"out": s_3, "clear": False}
        t_2 = self.checkpoint["t_2"]
        #
        # Get effective Hamiltonian terms
        #
        x1im = self.from_cache("x1im")
        xJkcM = self.from_cache("xJkcM")
        xikcm = self.from_cache("xikcm")
        x4bd = self.from_cache("x4bd")
        xiklm = self.from_cache("xiklm")
        xiJmN = self.from_cache("xiJmN")
        gooov = self.from_cache("gooov")
        # All terms with P(jk)
        # (1) xikcm(j,k,c,m) riM + xJkcM(i,k,c,m) rmJ
        #
        xikcm.contract("abcd,ed->eabc", b_2, **to_s_3)
        xJkcM.contract("abcd,de->aebc", b_2, **to_s_3)
        #
        # (2) rlM [
        #   + 0.5 <lM|iD> (tkcjd - tjckd)     + <lM|dJ> tidKC
        # ]
        #
        # (id) = <lM|iD> rlM
        tmp = gooov.contract("abcd,ab->cd", b_2)
        # 0.5 (id) (tkcjd - tjckd)
        t_2.contract("abcd,ed->ecab", tmp, **to_s_3, factor=0.5)
        t_2.contract("abcd,ed->eacb", tmp, **to_s_3, factor=-0.5)
        # (jd) <Ml|jD> rlM
        tmp = gooov.contract("abcd,ba->cd", b_2)
        # (jd) tidKC
        t_2.contract("abcd,eb->aecd", tmp, **to_s_3)
        #
        # (3+5) x1im(k,m) riJMC + 0.5 x1im(i,m) rmJKC
        #
        b_3ab.contract("abcd,ec->abed", x1im, **to_s_3)
        b_3ab.contract("abcd,ea->ebcd", x1im, **to_s_3, factor=0.5)
        #
        # (4) 0.5 x4bd(c,d) riJKD
        #
        b_3ab.contract("abcd,ed->abce", x4bd, **to_s_3, factor=0.5)
        #
        # (6) xkcMD(k,c,m,d) riJmd + (xiCmD + xkcMD)(k,c,M,D) riJMD + 0.5 xiCmD(i,c,m,d) rmJKD
        #
        xkcMD = self.from_cache("xkcMD")
        b_3aa.contract("abcd,efcd->abef", xkcMD, **to_s_3)
        b_3ab.contract("abcd,efcd->abef", xkcMD, **to_s_3)
        if self.dump_cache:
            self.cache.dump("xkcMD")
        xiCmD = self.from_cache("xiCmD")
        b_3ab.contract("abcd,efcd->abef", xiCmD, **to_s_3)
        b_3ab.contract("abcd,efad->ebcf", xiCmD, **to_s_3, factor=0.5)
        if self.dump_cache:
            self.cache.dump("xiCmD")
        #
        # (7+8) xiJmN(i,j,l,m) rlMKC + xiklm(j,k,l,m) riLMC
        #
        xiJmN.contract("abcd,cdef->abef", b_3ab, **to_s_3)
        xiklm.contract("abcd,ecdf->eabf", b_3ab, **to_s_3)
        #
        # (9) -0.5<ml||ed> rmJld tieKC  - 0.25 <ml||ed> riMLD (tjekc - tkejc)
        #     -   <ml| ed> rmJLD tieKC  - 0.5  <ml| ed> riMld (tjekc - tkejc)
        #
        goovv = self.from_cache("goovv")
        # tmp(je) = -0.5<ml||ed> rmJld - <ml|ed> rmJLD
        tmp = b_3aa.contract("abcd,aced->be", goovv, factor=-0.5)
        b_3aa.contract("abcd,acde->be", goovv, tmp, factor=0.5)
        b_3ab.contract("abcd,aced->be", goovv, tmp, factor=-1.0)
        # tmp(je) tieKC
        t_2.contract("abcd,eb->aecd", tmp, **to_s_3)
        # tmp(ie) = -0.25<ml||ed> riMLD - 0.5 <ml|ed> riMld
        tmp = b_3ab.contract("abcd,bced->ae", goovv, factor=-0.25)
        b_3ab.contract("abcd,bcde->ae", goovv, tmp, factor=0.25)
        b_3aa.contract("abcd,bced->ae", goovv, tmp, factor=-0.5)
        # Do not dump the Cholesky object as it is stored as a view
        if self.dump_cache and not isinstance(goovv, CholeskyFourIndex):
            self.cache.dump("goovv")
        # tmp(ie) (tjekc - tkejc)
        t_2.contract("abcd,eb->eacd", tmp, **to_s_3)
        t_2.contract("abcd,eb->ecad", tmp, **to_s_3, factor=-1.0)
        #
        # Permutation P(kj)
        #
        s_3.iadd_transpose((0, 2, 1, 3), factor=-1.0)

    @timer.with_section("DIPCCD0: H_eff")
    def set_hamiltonian(self, mo1: DenseTwoIndex, mo2: DenseFourIndex) -> None:
        """Derive all effective Hamiltonian terms. Like
        fock_pq/f:     mo1_pq + sum_m(2<pm|qm> - <pm|mq>),

        **Arguments:**

        mo1, mo2
             one- and two-electron integrals.
        """
        #
        # Get ranges
        #
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        nact = self.occ_model.nact[0]
        #
        # Inactive Fock matrix
        #
        fock = self.init_cache("fock", nact, nact)
        get_fock_matrix(fock, mo1, mo2, nacto)
        #
        # x1im
        #
        self.set_hamiltonian_x1im(fock, mo2)
        #
        # Intermediates used to construct others: goooo and gooov
        #
        oooo = self.get_range("oooo")
        ooov = self.get_range("ooov")
        gooov = self.denself.create_four_index(nacto, nacto, nacto, nactv)
        mo2.contract("abcd->abcd", out=gooov, **ooov)
        goooo = self.denself.create_four_index(nacto, nacto, nacto, nacto)
        mo2.contract("abcd->abcd", goooo, **oooo)
        #
        # xiJmN
        #
        self.set_hamiltonian_xiJmN(goooo, mo2)
        #
        # 3 hole terms
        #
        if self.nhole >= 3:
            self.set_hamiltonian_3_hole(fock, goooo, gooov, mo2)
        #
        # Clean up
        #
        mo1.__del__()
        mo2.__del__()

    def set_hamiltonian_3_hole(
        self,
        fock: DenseTwoIndex,
        goooo: DenseFourIndex,
        gooov: DenseFourIndex,
        mo2: DenseFourIndex,
    ) -> None:
        """Derive all effective Hamiltonian terms for three hole operators

        **Arguments:**

        fock, mo2
            Fock matrix and two-electron integrals.
        """
        #
        # xkc
        #
        self.set_hamiltonian_xkc(fock)
        #
        # x4bd
        #
        self.set_hamiltonian_x4bd(fock, mo2)
        #
        # ximKC
        #
        self.set_hamiltonian_ximKC(gooov)
        #
        # ximkc
        #
        self.set_hamiltonian_ximkc(gooov)
        #
        # xJkcM
        #
        self.set_hamiltonian_xJkcM(fock, gooov, mo2)
        #
        # xikcm
        #
        self.set_hamiltonian_xikcm(fock, gooov, mo2)
        #
        # xiklm
        #
        self.set_hamiltonian_xiklm(goooo, mo2)
        #
        # xkcMD
        #
        self.set_hamiltonian_xkcMD(mo2)
        #
        # xiCmD
        #
        self.set_hamiltonian_xiCmD(mo2)

        #
        # 4-Index slices of ERI
        # goovv
        #
        def alloc(arr, block):
            """Determines alloc keyword argument for init_cache method."""
            # We keep one whole CholeskyFourIndex to rule them all.
            # Non-redundant blocks are accessed as views.
            if isinstance(arr, CholeskyFourIndex):
                return (partial(arr.view, **self.get_range(block)),)
            # But we store only non-redundant blocks of DenseFourIndex
            return (partial(arr.copy, **self.get_range(block)),)

        #
        # Get blocks (for the systems we can treat with Dense, it does not
        # matter that we store both the vvoo and oovv blocks)
        #
        slices = ["oovv"]
        for slice_ in slices:
            self.init_cache(f"g{slice_}", alloc=alloc(mo2, slice_))
        #
        # Store also gooov
        #
        self.init_cache("gooov", alloc=alloc(gooov, "oooV"))

    def set_hamiltonian_x1im(
        self, fock: DenseTwoIndex, mo2: DenseFourIndex
    ) -> None:
        """Derive effective Hamiltonian term for x1im intermediate

        **Arguments:**

        fock, mo2
            Fock matrix and two-electron integrals for specific blocks.
        """
        #
        # Get ranges
        #
        nacto = self.occ_model.nacto[0]
        oovv = self.get_range("oovv")
        oovv = self.get_range("oovv")
        t_2 = self.checkpoint["t_2"]
        #
        # Effective Hamiltonian element x1im
        #
        x1im = self.init_cache("x1im", nacto, nacto)
        # 1) -fim
        x1im.iadd(fock, factor=-1.0, end2=nacto, end3=nacto)
        #
        # a) connected terms
        # 4) - 0.5 (<mk|dc> - <mk|cd>) (tidkc - tickd)
        # simplify to - <mk||cd> tidkc
        mo2.contract("abcd,ecbd->ea", t_2, x1im, factor=-0.5, **oovv)
        mo2.contract("abcd,edbc->ea", t_2, x1im, factor=0.5, **oovv)
        mo2.contract("abcd,edbc->ea", t_2, x1im, factor=0.5, **oovv)
        mo2.contract("abcd,ecbd->ea", t_2, x1im, factor=-0.5, **oovv)
        # 4) - <mk|dc> tidkc
        mo2.contract("abcd,ecbd->ea", t_2, x1im, factor=-1.0, **oovv)

    def set_hamiltonian_xkc(self, fock: DenseTwoIndex) -> None:
        """Derive effective Hamiltonian term for xkc intermediate

        **Arguments:**

        fock
            Fock matrix and two-electron integrals for specific blocks.
        """
        #
        # Get ranges
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        #
        # Effective Hamiltonian element xkc
        #
        xkc = self.init_cache("xkc", nacto, nactv)
        # fkc
        xkc.iadd(fock, 1.0, end2=nacto, begin3=nacto)

    def set_hamiltonian_x4bd(
        self, fock: DenseTwoIndex, mo2: DenseFourIndex
    ) -> None:
        """Derive effective Hamiltonian term for x4bd intermediate

        **Arguments:**

        fock, mo2
            Fock matrix and two-electron integrals for specific blocks.
        """
        #
        # Get ranges
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        vvoo = self.get_range("vvoo")
        t_2 = self.checkpoint["t_2"]
        #
        # Effective Hamiltonian element x4bd
        #
        x4bd = self.init_cache("x4bd", nactv, nactv)
        #
        # a) connected terms
        # fbd
        x4bd.iadd(fock, 1.0, begin2=nacto, begin3=nacto)
        # - 0.5 <mk||dc> (tmbkc - tkbmc) -> -1.0 <dc|mk>/<dc|km> tmbkc
        mo2.contract("abcd,cedb->ea", t_2, x4bd, factor=-1.0, **vvoo)
        mo2.contract("abcd,decb->ea", t_2, x4bd, factor=1.0, **vvoo)
        # - <mk|dc> tmbkc
        mo2.contract("abcd,cedb->ea", t_2, x4bd, factor=-1.0, **vvoo)

    def set_hamiltonian_xJkcM(
        self, fock: DenseTwoIndex, gooov: DenseFourIndex, mo2: DenseFourIndex
    ) -> None:
        """Derive effective Hamiltonian term for xJkcM intermediate

        **Arguments:**

        fock, gooov, mo2
            Fock matrix and two-electron integrals for specific blocks.
        """
        #
        # Get ranges
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        ov4 = self.get_range("ov", start=4)
        ovvv = self.get_range("ovvv")
        t_2 = self.checkpoint["t_2"]
        #
        # Effective Hamiltonian elements
        #
        xJkcM = self.init_cache("xJkcM", nacto, nacto, nactv, nacto)
        #
        # a) connected terms
        # 1-1) -<jk|mc>
        gooov.contract("abcd->abdc", xJkcM, factor=-1.0)
        # 1-6) -fmd tjdkc
        t_2.contract("abcd,eb->acde", fock, xJkcM, factor=-1.0, **ov4)
        # 1-7) -<ml||jd> tkcld
        gooov.contract("abcd,efbd->cefa", t_2, xJkcM, factor=-1.0)
        gooov.contract("abcd,efad->cefb", t_2, xJkcM)
        # 1-7) - <ml|jd> (tkcld - tlckd)
        gooov.contract("abcd,efbd->cefa", t_2, xJkcM, factor=-1.0)
        gooov.contract("abcd,edbf->cefa", t_2, xJkcM, factor=1.0)
        # 1-7') <km|ld> tjdlc
        gooov.contract("abcd,edcf->eafb", t_2, xJkcM)
        # 1-8) -<mc|de> tjdke
        mo2.contract("abcd,ecfd->efba", t_2, xJkcM, factor=-1.0, **ovvv)

    def set_hamiltonian_xikcm(
        self, fock: DenseTwoIndex, gooov: DenseFourIndex, mo2: DenseFourIndex
    ) -> None:
        """Derive effective Hamiltonian term for xikcm intermediate

        **Arguments:**

        fock, gooov, mo2
            Fock matrix and two-electron integrals for specific blocks.
        """
        #
        # Get ranges
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        ov4 = self.get_range("ov", start=4)
        vovv = self.get_range("vovv")
        ovvv = self.get_range("ovvv")
        t_2 = self.checkpoint["t_2"]
        #
        # xikcm
        #
        xikcm = self.init_cache("xikcm", nacto, nacto, nactv, nacto)
        # 1-1) -0.5 <ij||mb> -> <ij|mb>/<ji|mb>
        gooov.contract("abcd->abdc", xikcm, factor=-0.5)
        gooov.contract("abcd->badc", xikcm, factor=0.5)
        # 1-6) -0.5 fmc (ticjb - tjcib)
        t_2.contract("abcd,eb->acde", fock, xikcm, factor=-0.5, **ov4)
        t_2.contract("abcd,eb->cade", fock, xikcm, factor=0.5, **ov4)
        # 1-7) -<mk||ic> (tjbkc - tjckb)
        gooov.contract("abcd,efbd->cefa", t_2, xikcm, factor=-1.0)
        gooov.contract("abcd,efad->cefb", t_2, xikcm, factor=1.0)
        gooov.contract("abcd,edbf->cefa", t_2, xikcm, factor=1.0)
        gooov.contract("abcd,edaf->cefb", t_2, xikcm, factor=-1.0)
        # 1-7) - <mk|ic> tjbkc
        gooov.contract("abcd,efbd->cefa", t_2, xikcm, factor=-1.0)
        # 1-8) -0.25 <mb||cd> (ticjd - tidjc) -> -0.5 <mb||cd> ticjd
        mo2.contract("abcd,ecfd->efba", t_2, xikcm, factor=-0.5, **ovvv)
        mo2.contract("abcd,ecfd->efab", t_2, xikcm, factor=0.5, **vovv)

    def set_hamiltonian_ximKC(self, gooov):
        """Derive effective Hamiltonian term for ximKC intermediate

        **Arguments:**

        gooov
            two-electron integrals for specific blocks
        """
        #
        # Get ranges
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        #
        # Effective Hamiltonian element ximKC
        #
        ximKC = self.init_cache("ximKC", nacto, nacto, nacto, nactv)
        # -<mk|ic>
        gooov.contract("abcd->cabd", ximKC, factor=-1.0)

    def set_hamiltonian_ximkc(self, gooov: DenseFourIndex) -> None:
        """Derive effective Hamiltonian term for ximkc intermediate

        **Arguments:**

        gooov
            two-electron integrals for specific blocks.
        """
        #
        # Get ranges
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        #
        # Effective Hamiltonian element ximkc
        #
        ximkc = self.init_cache("ximkc", nacto, nacto, nacto, nactv)
        # -0.5 <mk||ic>
        gooov.contract("abcd->cabd", ximkc, factor=-0.5)
        gooov.contract("abcd->cbad", ximkc, factor=0.5)

    def set_hamiltonian_xiJmN(
        self, goooo: DenseFourIndex, mo2: DenseFourIndex
    ) -> None:
        """Derive effective Hamiltonian term for xiJmN intermediate

        **Arguments:**

        goooo, mo2
            two-electron integrals for specific blocks.
        """
        #
        # Get ranges
        #
        nacto = self.occ_model.nacto[0]
        oovv = self.get_range("oovv")
        t_2 = self.checkpoint["t_2"]
        #
        # Effective Hamiltonian element xiJmN
        #
        xiJmN = self.init_cache("xiJmN", nacto, nacto, nacto, nacto)
        # 1) <ij|mn>
        goooo.contract("abcd->abcd", xiJmN)
        # <mn|cd> ticjd
        mo2.contract("abcd,ecfd->efab", t_2, xiJmN, **oovv)

    def set_hamiltonian_xiklm(
        self, goooo: DenseFourIndex, mo2: DenseFourIndex
    ) -> None:
        """Derive effective Hamiltonian term for xiklm intermediate

        **Arguments:**

        goooo, mo2
            two-electron integrals for specific blocks.
        """
        #
        # Get ranges
        #
        nacto = self.occ_model.nacto[0]
        oovv = self.get_range("oovv")
        t_2 = self.checkpoint["t_2"]
        #
        # Effective Hamiltonian element xiklm
        #
        xiklm = self.init_cache("xiklm", nacto, nacto, nacto, nacto)
        # 5) 0.25 <ik||lm>
        goooo.contract("abcd->abcd", xiklm, factor=0.25)
        goooo.contract("abcd->abdc", xiklm, factor=-0.25)
        # 6) 0.125 <lm||de> (tiekd - tkeid) -> 0.25 <lm||de> tiekd
        mo2.contract("abcd,ecfd->efab", t_2, xiklm, factor=0.25, **oovv)
        mo2.contract("abcd,ecfd->efba", t_2, xiklm, factor=-0.25, **oovv)

    def set_hamiltonian_xiCmD(self, mo2: DenseFourIndex) -> None:
        """Derive effective Hamiltonian term for xiCmD intermediate

        **Arguments:**

        mo2
            two-electron integrals for specific blocks
        """
        #
        # Get ranges
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        oovv = self.get_range("oovv")
        ovov = self.get_range("ovov")
        t_2 = self.checkpoint["t_2"]
        #
        # Effective Hamiltonian element xiCmD
        #
        xiCmD = self.init_cache("xiCmD", nacto, nactv, nacto, nactv)
        # 1') -<ib|kc>
        mo2.contract("abcd->abcd", xiCmD, **ovov, factor=-1.0)
        # 5') <lk|cd> tidlb
        mo2.contract("abcd,edaf->efbc", t_2, xiCmD, factor=1.0, **oovv)

    def set_hamiltonian_xkcMD(self, mo2: DenseFourIndex) -> None:
        """Derive effective Hamiltonian term for xkcMD intermediate

        **Arguments:**

        mo2
            two-electron integrals for specific blocks.
        """
        #
        # Get ranges
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        oovv = self.get_range("oovv")
        ovvo = self.get_range("ovvo")
        t_2 = self.checkpoint["t_2"]
        #
        # Effective Hamiltonian element xkcMD
        #
        xkcMD = self.init_cache("xkcMD", nacto, nactv, nacto, nactv)
        # 1) <jk|bc>
        mo2.contract("abcd->acbd", xkcMD, **oovv)
        # 5) <kl||cd> tjbld -> <kl|cd>/<kc|dl>
        mo2.contract("abcd,efbd->efac", t_2, xkcMD, factor=1.0, **oovv)
        mo2.contract("abcd,efdc->efab", t_2, xkcMD, factor=-1.0, **ovvo)
        # 5) <kl|cd> (tjbld - tjdlb)
        mo2.contract("abcd,efbd->efac", t_2, xkcMD, factor=1.0, **oovv)
        mo2.contract("abcd,edbf->efac", t_2, xkcMD, factor=-1.0, **oovv)


class RDIPLCCD0(RDIPCCD0):
    """
    Restricted Double Ionization Potential Equation of Motion Coupled Cluster
    class restricted to Double IP for a LCCD reference function
    and (0,2,4) unpaired electron(s) (S_z = 0.0)

    This class (re)defines only the functions that are unique for the IP-LCCD
    model with 1 unpaired electron:

        * setting/resetting the seniority 0 sector
        * redefining effective Hamiltonian elements to exclude all T1.T2 terms
    """

    long_name = (
        "Ionization Potential Equation of Motion Linearized Coupled "
        "Cluster Singles Doubles"
    )
    acronym = "DIP-EOM-LCCD"
    reference = "LCCD"
    order = "DIP"
    alpha = 0
    disconnected_t1 = False


class RDIPfpCCD0(RDIPCCD0):
    """
    Restricted Double Ionization Potential Equation of Motion Coupled Cluster
    class restricted to Double IP for a fpCCD reference function and (0,2,4)
    unpaired electron(s) (S_z = 0.0)
    """

    long_name = (
        "Ionization Potential Equation of Motion frozen pair Coupled Cluster "
        "Singles Doubles"
    )
    acronym = "DIP-EOM-fpCCD"
    reference = "fpCCD"
    order = "DIP"
    alpha = 0
    disconnected_t1 = False


class RDIPfpLCCD0(RDIPCCD0):
    """
    Restricted Double Ionization Potential Equation of Motion Coupled Cluster
    class restricted to Double IP for a fpLCCD/pCCD-LCCD reference function
    and (0,2,4) unpaired electron(s) (S_z = 0.0)

    This class (re)defines only the functions that are unique for the DIP-fpLCCD
    model with (0,2,4) unpaired electron(s):

        * setting/resetting the seniority 0 sector
        * redefining effective Hamiltonian elements to include only T1.Tp terms
    """

    long_name = (
        "Ionization Potential Equation of Motion frozen pair Coupled "
        "Cluster Linearized Doubles"
    )
    acronym = "DIP-EOM-fpLCCD"
    reference = "fpLCCD"
    order = "DIP"
    alpha = 0
    disconnected_t1 = False

    def set_seniority_0(self) -> None:
        """Set all seniority-0 elements of excitation amplitudes (iaia) to the
        pCCD pair amplitudes.

        **Arguments:**

        :other: DenseFourIndex object

        **Optional arguments:**

        :value: some Linalg object or some value to be assigned
        """
        t_p = self.checkpoint["t_p"]
        t_2 = self.checkpoint["t_2"]
        ind1, ind2 = np.indices(
            (self.occ_model.nacto[0], self.occ_model.nactv[0])
        )
        indices = [ind1, ind2, ind1, ind2]
        t_2.assign(t_p, indices)

    def reset_seniority_0(self) -> None:
        """Set all seniority-0 elements of excitation amplitudes (iaia) back to
        zero.

        **Arguments:**

        :other: DenseFourIndex object

        **Optional arguments:**

        :value: some Linalg object or some value to be assigned
        """
        t_2 = self.checkpoint["t_2"]
        ind1, ind2 = np.indices(
            (self.occ_model.nacto[0], self.occ_model.nactv[0])
        )
        indices = [ind1, ind2, ind1, ind2]
        t_2.assign(0.0, indices)
