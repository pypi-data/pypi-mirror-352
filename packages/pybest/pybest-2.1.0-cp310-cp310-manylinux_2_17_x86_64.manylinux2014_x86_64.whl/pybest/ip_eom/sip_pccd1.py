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

"""Ionization Potential Equation of Motion Coupled Cluster implementations for
a pCCD reference function

   Variables used in this module:
    :ncore:     number of frozen core orbitals
    :nocc:      number of occupied orbitals in the principal configuration
    :nacto:     number of active occupied orbitals in the principal configuration
    :nvirt:     number of virtual orbitals in the principal configuration
    :nactv:     number of active virtual orbitals in the principal configuration
    :nbasis:    total number of basis functions
    :nact:      total number of active orbitals (nacto+nactv)
    :e_ip:      the energy correction for IP
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

from pybest.auxmat import get_fock_matrix
from pybest.ip_eom.sip_base import RSIPCC1
from pybest.linalg import (
    DenseFourIndex,
    DenseOneIndex,
    DenseThreeIndex,
    DenseTwoIndex,
)
from pybest.linalg.cholesky import CholeskyFourIndex
from pybest.log import timer


class RIPpCCD1(RSIPCC1):
    """
    Restricted Single Ionization Potential Equation of Motion Coupled Cluster
    class restricted to Single IP for a pCCD reference function and 1 unpaired
    electron (S_z = 0.5)

    This class defines only the function that are unique for the IP-pCCD model
    with 1 unpaired electron:

        * dimension (number of degrees of freedom)
        * unmask_args (resolve T_p amplitudes)
        * set_hamiltonian (calculates effective Hamiltonian -- at most O(o2v2))
        * compute_h_diag (pre-conditioner used by Davidson)
        * build_subspace_hamiltonian (subspace to be diagonalized)
        * print functions (ci vector and weights)

    Note that the R_ijb and R_iJB blocks are considered together. Thus, setting
    the number of hole operators equal to 2, requires at least 2 active
    occupied orbitals.
    """

    long_name = (
        "Ionization Potential Equation of Motion pair Coupled Cluster Doubles"
    )
    acronym = "IP-EOM-pCCD"
    reference = "pCCD"
    order = "IP"
    alpha = 1

    def compute_h_diag(self, *args: Any) -> DenseOneIndex:
        """Used by the Davidson module for pre-conditioning

        **Arguments:**

        args:
            required for the Davidson module (not used here)
        """
        if self.spin_free:
            return self.h_diag_sf()
        return self.h_diag()

    @timer.with_section("IPpCCD1: H_diag sf")
    def h_diag_sf(self) -> DenseOneIndex:
        """Diagonal approximation to Hamiltonian in spin-free representation"""
        h_diag = self.lf.create_one_index(self.dimension, label="h_diag")
        #
        # Get effective Hamiltonian terms
        #
        nacto = self.occ_model.nacto[0]
        x1im = self.from_cache("x1im")
        #
        # x1im(i,i)
        #
        x1imdiag = x1im.copy_diagonal()
        h_diag.assign(x1imdiag, end0=nacto)
        #
        # rijb
        #
        if self.nhole >= 2:
            self.get_2_hole_terms_h_diag_sf(h_diag)
        return h_diag

    def get_2_hole_terms_h_diag_sf(self, h_diag: DenseOneIndex) -> None:
        """Determine all contributions containing two hole operators for
        the spin-free representation:
            * H_ijb,ijb

        **Arguments:**

        h_diag:
            The diagonal elements of the Hamiltonian
        """
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        cia = self.checkpoint["t_p"]
        h_ijb = self.lf.create_three_index(nacto, nacto, nactv)
        #
        # Get effective Hamiltonian terms
        #
        loovv = self.from_cache("loovv")
        x6jbld = self.from_cache("x6jbld")
        x8ibld = self.from_cache("x8ibld")
        x9il = self.from_cache("x9il")
        x10bc = self.from_cache("x10bc")
        x12ijlm = self.from_cache("x12ijlm")
        #
        # x6(j,b,j,b)
        #
        x6jbld.expand("bcbc->abc", h_ijb)
        #
        # x8(i,b,i,b)
        #
        x8ibld.expand("acac->abc", h_ijb)
        #
        # x9(i,i)
        #
        x9il.expand("aa->abc", h_ijb)
        #
        # x10(b,b)
        #
        x10bc.expand("cc->abc", h_ijb)
        #
        # x11(j,j)
        #
        x9il.expand("bb->abc", h_ijb, end0=nacto, end1=nacto)
        #
        # x12(i,j,i,j)
        #
        x12ijlm.expand("abab->abc", h_ijb)
        #
        # x13(i,j,b,j) dij
        #
        tmp = loovv.contract("aabb,ab->ab", cia, out=None)
        tmp.expand("ab->aab", h_ijb, factor=-1.0)
        #
        # Assign to h_diag output
        #
        h_diag.assign(h_ijb, begin0=nacto)

    @timer.with_section("IPpCCD1: H_diag")
    def h_diag(self) -> DenseOneIndex:
        """Diagonal approximation to Hamiltonian for S_z=0.5 states"""
        h_diag = self.lf.create_one_index(self.dimension, label="h_diag")
        #
        # Get effective Hamiltonian terms
        #
        nacto = self.occ_model.nacto[0]
        x1im = self.from_cache("x1im")
        #
        # x1im(i,i)
        #
        x1imdiag = x1im.copy_diagonal()
        h_diag.assign(x1imdiag, end0=nacto)
        #
        # R_ijb/R_iJB terms
        #
        if self.nhole >= 2:
            self.get_2_hole_terms_h_diag(h_diag)

        return h_diag

    def get_2_hole_terms_h_diag(self, h_diag: DenseOneIndex) -> None:
        """Determine all contributions containing two hole operators for
        the spin-dependent representation:
            * H_ijb,ijb
            * H_iJB,iJB

        **Arguments:**

        h_diag:
            The diagonal elements of the Hamiltonian
        """
        cia = self.checkpoint["t_p"]
        #
        # Get effective Hamiltonian terms
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        fock = self.from_cache("fock")
        goooo = self.from_cache("goooo")
        x1im = self.from_cache("x1im")
        x4bd = self.from_cache("x4bd")
        x6ijlm = self.from_cache("x6ijlm")
        goovv = self.from_cache("goovv")
        govvo = self.from_cache("govvo")
        govov = self.from_cache("govov")
        #
        # Intermediates
        #
        lij = x1im.new()
        goooo.contract("abab->ab", out=lij)
        goooo.contract("abab->ab", out=lij, factor=-1.0)
        gov = goovv.contract("aabb->ab", out=None)
        lov = govov.contract("abab->ab", out=None)
        govvo.contract("abba->ab", out=lov, factor=-1.0)
        x6ij = x6ijlm.contract("abab->ab", out=None)
        gjjbb = goovv.contract("aabb->ab", out=None)
        gjbjb = govov.contract("abab->ab", out=None)
        #
        # H_ijb,ijb
        #
        h_ijb = self.lf.create_three_index(nacto, nacto, nactv)
        #
        # x1im(j,j)
        #
        x1im.expand("bb->abc", h_ijb)
        h_iJB = h_ijb.copy()
        #
        # x4bd(b,b)
        #
        x4bd.expand("cc->abc", h_ijb, factor=0.5)
        #
        # lij
        #
        lij.expand("ab->abc", h_ijb, factor=0.25)
        #
        # lov(j,b)
        #
        lov.expand("bc->abc", h_ijb, factor=-1.0)
        #
        # gov(j,b) cjb
        #
        cia_ = cia.copy()
        cia_.imul(gov)
        cia_.expand("bc->abc", h_ijb)
        h_ijb.iadd_transpose((1, 0, 2), factor=1.0)
        #
        # Assign using mask
        #
        end = nacto + (nacto - 1) * nacto * nactv // 2
        h_diag.assign(h_ijb.array[self.get_mask(0)], begin0=nacto, end0=end)
        #
        # H_iJB,iJB
        # -fim(i,i)
        fock.expand("aa->abc", h_iJB, factor=-1.0, end0=nacto, end1=nacto)
        #
        # x4bd(b,b)
        #
        x4bd.expand("cc->abc", h_iJB)
        #
        # x6ijlm(i,j,i,j)
        #
        x6ij.expand("ab->abc", h_iJB)
        #
        # gjjbb
        #
        gjjbb.expand("bc->abc", h_iJB)
        #
        # gjjbb cjb / giibb cia
        #
        cia_ = cia.copy()
        cia_.imul(gjjbb)
        cia_.expand("bc->abc", h_iJB)
        cia_.expand("ac->abc", h_iJB)
        # -gjjbb cjb dij
        cia_.expand("ab->aab", h_iJB, factor=-1.0)
        #
        # -gibib
        #
        gjbjb.expand("ac->abc", h_iJB, factor=-1.0)
        #
        # Assign using mask
        #
        h_diag.assign(h_iJB, begin0=end)

    def build_subspace_hamiltonian(
        self, b_vector: DenseOneIndex, h_diag: DenseOneIndex, *args: Any
    ) -> DenseOneIndex:
        """
        Used by the Davidson module to construct subspace Hamiltonian

        **Arguments:**

        b_vector:
            (OneIndex object) contains current approximation to CI coefficients

        h_diag:
            Diagonal Hamiltonian elements required in davidson module (not used
            here)

        args:
            Set of arguments passed by the davidson module (not used here)
        """
        if self.spin_free:
            return self.subspace_sf(b_vector)
        return self.subspace(b_vector)

    @timer.with_section("IPpCCD1: H_sub sf")
    def subspace_sf(self, b_vector: DenseOneIndex) -> DenseOneIndex:
        """
        Used by the Davidson module to construct subspace Hamiltonian in the
        spin-free representation

        **Arguments:**

        b_vector:
            (OneIndex object) contains current approximation to CI coefficients
        """
        #
        # Get effective Hamiltonian terms
        #
        nacto = self.occ_model.nacto[0]
        x1im = self.from_cache("x1im")
        #
        # Calculate sigma vector (H.b_vector)
        #
        # output
        s_1 = self.lf.create_one_index(nacto)
        to_s_1 = {"out": s_1, "clear": False}
        sigma = self.lf.create_one_index(self.dimension)
        # Input
        b_1 = self.lf.create_one_index(nacto)
        b_1.assign(b_vector, end1=nacto)
        #
        # R_i
        #
        # (1) xim rm
        x1im.contract("ab,b->a", b_1, **to_s_1)
        #
        # R_ijb including coupling terms
        #
        if self.nhole >= 2:
            self.get_2_hole_terms_sf(b_1, b_vector, s_1, sigma)
        #
        # Assign to sigma vector
        #
        sigma.assign(s_1, begin0=0, end0=nacto)
        del s_1

        return sigma

    def get_2_hole_terms_sf(
        self,
        b_1: DenseOneIndex,
        b_vector: DenseOneIndex,
        s_1: DenseOneIndex,
        sigma: DenseOneIndex,
    ) -> None:
        """Determine all contributions containing two hole operators for
        the spin-free representation:
            * coupling terms to R_i
            * R_ijb

        **Arguments:**

        b_1, b_vector:
            b vectors used in Davidson diagonalization

        s_1, sigma:
            sigma vectors used in Davidson diagonalization
        """
        cia = self.checkpoint["t_p"]
        #
        # Get effective Hamiltonian terms
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        fock = self.from_cache("fock")
        looov = self.from_cache("looov")
        loovv = self.from_cache("loovv")
        x5ijbm = self.from_cache("x5ijbm")
        x6jbld = self.from_cache("x6jbld")
        x7jbld = self.from_cache("x7jbld")
        x8ibld = self.from_cache("x8ibld")
        x9il = self.from_cache("x9il")
        x10bc = self.from_cache("x10bc")
        x12ijlm = self.from_cache("x12ijlm")
        #
        # Get ranges
        #
        ov3 = self.get_range("ov", start=3)
        #
        # Calculate sigma vector (H.b_vector)_kc
        #
        # output
        to_s_1 = {"out": s_1, "clear": False}
        s_3 = self.lf.create_three_index(nacto, nacto, nactv)
        to_s_3 = {"out": s_3, "clear": False}
        # Input
        b_3 = self.lf.create_three_index(nacto, nacto, nactv)
        b_3.assign(b_vector, begin3=nacto)
        #
        # (2) 2 Fmd rimd
        #
        b_3.contract("abc,bc->a", fock, factor=2.0, **ov3, **to_s_1)
        #
        # (3) - Fmd rmid
        #
        b_3.contract("abc,ac->b", fock, factor=-1.0, **ov3, **to_s_1)
        #
        # (4) - ximld rmld (looov[mlid])
        #
        looov.contract("abcd,abd->c", b_3, factor=-1.0, **to_s_1)
        #
        # (5) x5ijbm rm
        #
        x5ijbm.contract("abcd,d->abc", b_1, **to_s_3)
        #
        # (6) x6jbld rild
        #
        x6jbld.contract("abcd,ecd->eab", b_3, **to_s_3)
        #
        # (7) x7jbld rlid
        #
        x7jbld.contract("abcd,ced->eab", b_3, **to_s_3)
        #
        # (8) x8ibld rljd
        #
        x8ibld.contract("abcd,ced->aeb", b_3, **to_s_3)
        #
        # (9) x9il rljb
        #
        b_3.contract("abc,ea->ebc", x9il, **to_s_3)
        #
        # (10) x10bc rijc
        #
        b_3.contract("abc,ec->abe", x10bc, **to_s_3)
        #
        # (11) x11jl rilb (=x9il)
        #
        b_3.contract("abc,eb->aec", x9il, **to_s_3)
        #
        # (12) x12ijlm rlmb
        #
        x12ijlm.contract("abcd,cde->abe", b_3, **to_s_3)
        #
        # (13) - xklcbj rlkc dij
        # (b) = lklcb rlkc
        tmp = loovv.contract("abcd,bac->d", b_3, out=None)
        cia_ = cia.new()
        cia.contract("ab,b->ab", tmp, cia_)
        cia_.expand("ab->aab", s_3, factor=-1.0)
        #
        # Assign to sigma vector
        #
        sigma.assign(s_3, begin0=nacto)

    @timer.with_section("IPpCCD1: H_sub")
    def subspace(self, b_vector: DenseOneIndex) -> DenseOneIndex:
        """
        Used by the Davidson module to construct subspace Hamiltonian for doublet
        states

        **Arguments:**

        b_vector:
            (OneIndex object) contains current approximation to CI coefficients
        """
        #
        # Get auxiliary matrices
        #
        nacto = self.occ_model.nacto[0]
        x1im = self.from_cache("x1im")
        #
        # Calculate sigma vector s = (H.b)
        #
        # output
        s_1 = self.lf.create_one_index(nacto)
        to_s_1 = {"out": s_1, "clear": False}
        sigma = self.lf.create_one_index(self.dimension)
        # Input
        b_1 = self.lf.create_one_index(nacto)
        #
        # Assign ri
        #
        b_1.assign(b_vector, end1=nacto)
        #
        # R_i
        #
        # (1) xim rm
        #
        x1im.contract("ab,b->a", b_1, **to_s_1)
        #
        # R_ijb/R_iJB including coupling terms
        #
        if self.nhole >= 2:
            self.get_2_hole_terms(b_1, b_vector, s_1, sigma)
        #
        # Assign to sigma vector
        #
        sigma.assign(s_1, begin0=0, end0=nacto)
        del s_1

        return sigma

    def get_2_hole_terms(
        self,
        b_1: DenseOneIndex,
        b_vector: DenseOneIndex,
        s_1: DenseOneIndex,
        sigma: DenseOneIndex,
    ) -> None:
        """Determine all contributions containing two hole operators for
        the spin-dependent representation:
            * coupling terms to R_i
            * R_ijb
            * R_iJB

        **Arguments:**

        b_1, b_vector:
            b vectors used in Davidson diagonalization

        s_1, sigma:
            sigma vectors used in Davidson diagonalization
        """
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        #
        # Calculate sigma vector s = (H.b)_kc
        #
        # output
        s_3 = self.lf.create_three_index(nacto, nacto, nactv)
        # Input
        b_3aa = self.lf.create_three_index(nacto, nacto, nactv)
        b_3bb = self.lf.create_three_index(nacto, nacto, nactv)
        #
        # Final index of b_3aa in b_vector
        #
        end = nacto + (nacto - 1) * nacto * nactv // 2
        #
        # Assign rijb
        #
        b_3aa.assign(
            b_vector, begin3=nacto, end3=end, ind0=self.get_index_of_mask(0)
        )
        b_3aa.iadd_transpose((1, 0, 2), factor=-1.0)
        # Assign riJB
        b_3bb.assign(b_vector, begin3=end)
        #
        # Get coupling terms to R_i
        #
        self.get_2_hole_r_i_terms(b_3aa, b_3bb, s_1)
        #
        # R_ijb
        #
        self.get_2_hole_r_3ss_terms(b_1, b_3aa, b_3bb, s_3)
        # Assign to sigma vector using mask
        sigma.assign(s_3.array[self.get_mask(0)], begin0=nacto, end0=end)
        #
        # R_iJB
        #
        self.get_2_hole_r_3os_terms(b_1, b_3aa, b_3bb, s_3)
        # Assign to sigma vector
        sigma.assign(s_3, begin0=end)

    def get_2_hole_r_i_terms(
        self,
        b_3aa: DenseThreeIndex,
        b_3bb: DenseThreeIndex,
        s_1: DenseOneIndex,
    ) -> None:
        """Determine all contributions containing two particle operators:
            * coupling terms to R_i

        **Arguments:**

        b_3aa, b_3bb:
            b vectors of different R operators used in the Davidson diagonalization

        s_1:
            sigma vector corresponding to R_i used in the Davidson diagonalization
        """
        to_s_1 = {"out": s_1, "clear": False}
        #
        # Get effective Hamiltonian terms
        #
        fock = self.from_cache("fock")
        gooov = self.from_cache("gooov")
        #
        # Get ranges
        #
        ov3 = self.get_range("ov", start=3)
        #
        # (2) -0.5 <mn||id> rmnd
        #
        gooov.contract("abcd,abd->c", b_3aa, factor=-0.5, **to_s_1)
        gooov.contract("abcd,bad->c", b_3aa, factor=0.5, **to_s_1)
        #
        # (3) - <mN|iD> rmND
        #
        gooov.contract("abcd,abd->c", b_3bb, factor=-1.0, **to_s_1)
        #
        # (4) fmd rimd
        #
        b_3aa.contract("abc,bc->a", fock, **ov3, **to_s_1)
        #
        # (5) fmd riMD
        #
        b_3bb.contract("abc,bc->a", fock, **ov3, **to_s_1)

    def get_2_hole_r_3ss_terms(
        self,
        b_1: DenseOneIndex,
        b_3aa: DenseThreeIndex,
        b_3bb: DenseThreeIndex,
        s_3: DenseThreeIndex,
    ) -> None:
        """Determine all contributions containing two particle operators:
            * R_ijb (same spin - ss)

        **Arguments:**

        b_1, b_3aa, b_3bb:
            b vectors of different R operators used in Davidson diagonalization

        s_3:
            sigma vector corresponding to R_ijb used in Davidson diagonalization
        """
        s_3.clear()
        to_s_3 = {"out": s_3, "clear": False}
        cia = self.checkpoint["t_p"]
        #
        # Get effective Hamiltonian terms
        #
        x1im = self.from_cache("x1im")
        x2ijbm = self.from_cache("x2ijbm")
        x4bd = self.from_cache("x4bd")
        goooo = self.from_cache("goooo")
        gvvoo = self.from_cache("gvvoo")
        govvo = self.from_cache("govvo")
        govov = self.from_cache("govov")
        #
        # (6) P(ij) 0.5 x2ijbm rm
        #
        x2ijbm.contract("abcd,d->abc", b_1, factor=0.5, **to_s_3)
        #
        # (7) P(ij) rimb x1jm
        #
        b_3aa.contract("abc,db->adc", x1im, **to_s_3)
        #
        # (8) 0.5 P(ij) x4bd rijd
        #
        b_3aa.contract("abc,dc->abd", x4bd, factor=0.5, **to_s_3)
        #
        # (9) 0.25 P(ij) <ij||kl> rklb
        #
        goooo.contract("abcd,cde->abe", b_3aa, factor=0.25, **to_s_3)
        goooo.contract("abcd,cde->bae", b_3aa, factor=-0.25, **to_s_3)
        #
        # (10) P(ij) (jdbl) rild
        # <jd||bl> rild
        govvo.contract("abcd,edb->eac", b_3aa, **to_s_3)
        govov.contract("abcd,ecb->ead", b_3aa, factor=-1.0, **to_s_3)
        # P(ij) <bD|jL> rild cjb
        tmp = gvvoo.contract("abcd,edb->eca", b_3aa)
        tmp.contract("abc,bc->abc", cia, s_3)
        #
        # (11) (DjLb) riLD
        # P(ij) <bd||jl> riLD
        tmp = gvvoo.contract("abcd,edb->eca", b_3bb)
        # (ijb)
        s_3.iadd(tmp)
        # ex term
        gvvoo.contract("abcd,ecb->eda", b_3bb, tmp, factor=-1.0)
        # (ijb) cjb
        tmp.contract("abc,bc->abc", cia, s_3)
        #
        # P(ij)
        #
        s_3.iadd_transpose((1, 0, 2), factor=-1.0)

    def get_2_hole_r_3os_terms(
        self,
        b_1: DenseOneIndex,
        b_3aa: DenseThreeIndex,
        b_3bb: DenseThreeIndex,
        s_3: DenseThreeIndex,
    ) -> None:
        """Determine all contributions containing two particle operators:
            * R_iJB (opposite spin - os)

        **Arguments:**

        b_1, b_3aa, b_3bb:
            b vectors of different R operators used in Davidson diagonalization

        s_3:
            sigma vector corresponding to R_iJB used in Davidson diagonalization
        """
        s_3.clear()
        to_s_3 = {"out": s_3, "clear": False}
        cia = self.checkpoint["t_p"]
        #
        # Get effective Hamiltonian terms
        #
        x1im = self.from_cache("x1im")
        x4bd = self.from_cache("x4bd")
        x5ijbm = self.from_cache("x5ijbm")
        x6ijlm = self.from_cache("x6ijlm")
        goovv = self.from_cache("goovv")
        gvvoo = self.from_cache("gvvoo")
        govvo = self.from_cache("govvo")
        govov = self.from_cache("govov")
        #
        # (12) x5ijbm rm
        #
        x5ijbm.contract("abcd,d->abc", b_1, **to_s_3)
        #
        # (13) riMB x1im(j,m)
        #
        b_3bb.contract("abc,db->adc", x1im, **to_s_3)
        #
        # (14) x1im(i,m) rmJB
        #
        b_3bb.contract("abc,da->dbc", x1im, **to_s_3)
        #
        # (15) x4bd riJD
        #
        b_3bb.contract("abc,dc->abd", x4bd, **to_s_3)
        #
        # (16) x6ijkl rkLB
        #
        x6ijlm.contract("abcd,cde->abe", b_3bb, **to_s_3)
        #
        # (17) (jdbl) rild
        # <jL|bD> rild
        # (ijb)
        tmp = goovv.contract("abcd,ebd->eac", b_3aa)
        s_3.iadd(tmp)
        # <jl|db> rild (ex. part of <jl||bd> rild)
        # (ijb)
        goovv.contract("abcd,ebc->ead", b_3aa, tmp, factor=-1.0)
        # (ijb) cjb
        tmp.contract("abc,bc->abc", cia, s_3)
        #
        # (18) (jDbL) riLD
        # <jd||bl> riLD
        govvo.contract("abcd,edb->eac", b_3bb, **to_s_3)
        govov.contract("abcd,ecb->ead", b_3bb, factor=-1.0, **to_s_3)
        # <jl|bd> riLD
        # (ijb)
        tmp = goovv.contract("abcd,ebd->eac", b_3bb)
        # (ijb) cjb
        tmp.contract("abc,bc->abc", cia, s_3)
        #
        # (19) (idkb) rkJD
        # -<ib|kd> rkJD
        tmp = govov.contract("abcd,ced->aeb", b_3bb, out=None)
        s_3.iadd(tmp, -1.0)
        # <ib|dk> cib rkJD
        # <ib|dk> rkJD
        tmp = govvo.contract("abcd,dec->aeb", b_3bb, out=None)
        # (ijb) cib
        tmp.contract("abc,ac->abc", cia, s_3)
        #
        # (20) rkld dij
        # (b) = 0.5 <bd||kl> rkld
        tmp = gvvoo.contract("abcd,cdb->a", b_3aa, factor=0.5)
        gvvoo.contract("abcd,dcb->a", b_3aa, tmp, factor=-0.5)
        #
        # (21) rkLD dij
        # (b) = <bd|kl> rkLD
        gvvoo.contract("abcd,cdb->a", b_3bb, tmp)
        # - b cib
        cia_ = cia.new()
        cia.contract("ab,b->ab", tmp, cia_)
        cia_.expand("ab->aab", s_3, factor=-1.0)

    @timer.with_section("IPpCCD1: H_eff")
    def set_hamiltonian(self, mo1: DenseTwoIndex, mo2: DenseFourIndex) -> None:
        """Derive all effective Hamiltonian terms. Like
        fock_pq/f:     mo1_pq + sum_m(2<pm|qm> - <pm|mq>),

        **Arguments:**

        mo1, mo2
             one- and two-electron integrals.
        """
        cia = self.checkpoint["t_p"]
        #
        # Get ranges
        #
        nacto, nact = self.occ_model.nacto[0], self.occ_model.nact[0]
        oovv = self.get_range("oovv")
        # optimize contractions
        opt = "td" if isinstance(mo2, CholeskyFourIndex) else None
        #
        # Inactive Fock matrix
        #
        fock = self.init_cache("fock", nact, nact)
        get_fock_matrix(fock, mo1, mo2, nacto)
        #
        # x1im
        #
        x1im = self.init_cache("x1im", nacto, nacto)
        # -fim
        x1im.iadd(fock, -1.0, end2=nacto, end3=nacto)
        # -<im|ee> cie
        mo2.contract("abcc,ac->ab", cia, x1im, factor=-1.0, **oovv, select=opt)
        #
        # 2 hole terms
        #
        if self.nhole >= 2:
            self.set_hamiltonian_2_hole(fock, mo2)
        #
        # Clean up
        #
        mo1.__del__()
        mo2.__del__()

    def set_hamiltonian_2_hole(
        self, fock: DenseTwoIndex, mo2: DenseFourIndex
    ) -> None:
        """Derive all effective Hamiltonian terms for 2 hole operators

        **Arguments:**

        fock, mo2
            Fock matrix and two-electron integrals.
        """
        cia = self.checkpoint["t_p"]
        #
        # Get ranges
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        vo2 = self.get_range("vo", start=2)
        oooo = self.get_range("oooo")
        ooov = self.get_range("ooov")
        oovv = self.get_range("oovv")
        vvoo = self.get_range("vvoo")
        vovv = self.get_range("vovv")
        # optimize contractions
        opt = "td" if isinstance(mo2, CholeskyFourIndex) else None
        #
        # x4bd
        #
        x4bd = self.init_cache("x4bd", nactv, nactv)
        # fbd
        x4bd.iadd(fock, 1.0, begin2=nacto, begin3=nacto)
        # -<bd|kk> ckb
        mo2.contract("abcc,ca->ab", cia, x4bd, factor=-1.0, **vvoo, select=opt)
        #
        # goooo
        #
        goooo = self.init_cache("goooo", nacto, nacto, nacto, nacto)
        mo2.contract("abcd->abcd", out=goooo, **oooo)
        #
        # gooov
        #
        gooov = self.init_cache("gooov", nacto, nacto, nacto, nactv)
        mo2.contract("abcd->abcd", out=gooov, **ooov)
        #
        # x2ijbm (implemented as x2[ij]bm)
        #
        x2ijbm = self.init_cache("x2ijbm", nacto, nacto, nactv, nacto)
        # -<ij||mb>
        gooov.contract("abcd->abdc", out=x2ijbm, factor=-1.0)
        gooov.contract("abcd->badc", out=x2ijbm, factor=1.0)
        # -<ij|mb> cjb
        gooov.contract("abcd,bd->abdc", cia, x2ijbm, factor=-1.0)
        # +<ji|mb> cib
        gooov.contract("abcd,bd->badc", cia, x2ijbm)
        #
        # x5ijbm
        #
        x5ijbm = self.init_cache("x5ijbm", nacto, nacto, nactv, nacto)
        # -<ij|mb>
        gooov.contract("abcd->abdc", out=x5ijbm, factor=-1.0)
        # -<ij|mb> cjb
        gooov.contract("abcd,bd->abdc", cia, x5ijbm, factor=-1.0)
        # <im|jb> cjb
        gooov.contract("abcd,cd->acdb", cia, x5ijbm)
        # <im|jb> cib
        gooov.contract("abcd,ad->acdb", cia, x5ijbm)
        # -fbm cib dij
        tibm = self.lf.create_three_index(nacto, nactv, nacto)
        cia.contract("ab,bc->abc", fock, tibm, factor=-1.0, **vo2)
        # -<bm|ee> cie dij
        mo2.contract("abcc,dc->dab", cia, tibm, factor=-1.0, **vovv)
        # dij tibm
        tibm.expand("abc->aabc", x5ijbm, factor=1.0)
        #
        # x6ijlm
        #
        x6ijlm = self.init_cache("x6ijlm", nacto, nacto, nacto, nacto)
        # gijlm
        mo2.contract("abcd->abcd", out=x6ijlm, **oooo)
        # glmcc cic dij
        tmpilm = self.lf.create_three_index(nacto, nacto, nacto)
        mo2.contract("abcc,dc->dab", cia, tmpilm, **oovv)
        # dij tilm
        tmpilm.expand("abc->aabc", x6ijlm, factor=1.0)

        if self.spin_free:
            self.set_sf_terms(fock, mo2)
        else:
            self.set_sd_terms(mo2)

    def set_sf_terms(self, fock: DenseTwoIndex, mo2: DenseFourIndex) -> None:
        """Derive all Hamiltonian elements for the spin-free representation

        **Arguments:**

        fock, mo2
            Fock matrix and two-electron integrals.
        """
        cia = self.checkpoint["t_p"]
        #
        # Get ranges
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        oooo = self.get_range("oooo")
        ooov = self.get_range("ooov")
        oovo = self.get_range("oovo")
        ovov = self.get_range("ovov")
        oovv = self.get_range("oovv")
        vvoo = self.get_range("vvoo")
        ovvo = self.get_range("ovvo")
        #
        # optimize contractions
        #
        opt = "td" if isinstance(mo2, CholeskyFourIndex) else None
        #
        # looov
        #
        looov = self.init_cache("looov", nacto, nacto, nacto, nactv)
        mo2.contract("abcd->abcd", out=looov, factor=2.0, **ooov)
        mo2.contract("abcd->abdc", out=looov, factor=-1.0, **oovo)
        #
        # temporary matrices: g_ovvo
        govvo = self.denself.create_four_index(nacto, nactv, nactv, nacto)
        mo2.contract("abcd->abcd", out=govvo, **ovvo)
        # temporary matrices: g_ovov
        govov = self.denself.create_four_index(nacto, nactv, nacto, nactv)
        mo2.contract("abcd->abcd", out=govov, **ovov)
        #
        # x6jbld
        #
        x6jbld = self.init_cache("x6jbld", nacto, nactv, nacto, nactv)
        # Ljdbl
        govvo.contract("abcd->acdb", out=x6jbld, factor=2.0)
        govov.contract("abcd->abcd", out=x6jbld, factor=-1.0)
        # Ljlbd cjb / jdbl jbdl
        govvo.contract("abcd,ac->acdb", cia, x6jbld, factor=2.0)
        govvo.contract("abcd,ab->abdc", cia, x6jbld, factor=-1.0)
        #
        # x7jbld
        #
        x7jbld = self.init_cache("x7jbld", nacto, nactv, nacto, nactv)
        # -gjdbl
        govvo.contract("abcd->acdb", out=x7jbld, factor=-1.0)
        # -<jl||bd> cjb / jdbl jbdl
        govvo.contract("abcd,ac->acdb", cia, x7jbld, factor=-1.0)
        govvo.contract("abcd,ab->abdc", cia, x7jbld)
        #
        # x8ibld
        #
        x8ibld = self.init_cache("x8ibld", nacto, nactv, nacto, nactv)
        # -gibld
        govov.contract("abcd->abcd", out=x8ibld, factor=-1.0)
        # gibdl cib
        govvo.contract("abcd,ab->abdc", cia, x8ibld)
        #
        # loovv
        #
        del govov
        del govvo
        loovv = self.init_cache("loovv", nacto, nacto, nactv, nactv)
        mo2.contract("abcd->abcd", out=loovv, factor=2.0, **oovv)
        mo2.contract("abcd->abdc", out=loovv, factor=-1.0, **oovv)
        #
        # x9il = x11jl
        #
        x9il = self.init_cache("x9il", nacto, nacto)
        # -fil
        x9il.iadd(fock, factor=-1.0, end2=nacto, end3=nacto)
        # -<il|cc> cic
        mo2.contract("abcc,ac->ab", cia, x9il, factor=-1.0, **oovv, select=opt)
        #
        # x10bc
        #
        x10bc = self.init_cache("x10bc", nactv, nactv)
        # fbc
        x10bc.iadd(fock, 1.0, begin2=nacto, begin3=nacto)
        # -gbckk ckb
        mo2.contract(
            "abcc,ca->ab", cia, x10bc, factor=-1.0, **vvoo, select=opt
        )
        #
        # x12ijlm
        #
        x12ijlm = self.init_cache("x12ijlm", nacto, nacto, nacto, nacto)
        # gijlm
        mo2.contract("abcd->abcd", out=x12ijlm, **oooo)
        # glmcc cic dij
        tmpilm = self.lf.create_three_index(nacto, nacto, nacto)
        mo2.contract("abcc,dc->dab", cia, tmpilm, **oovv)
        # dij tilm
        tmpilm.expand("abc->aabc", x12ijlm, factor=1.0)

    def set_sd_terms(self, mo2: DenseFourIndex) -> None:
        """Derive all Hamiltonian elements for the spin-dependent representation

        **Arguments:**

        mo2
            two-electron integrals.
        """

        #
        # 4-Index slices of ERI
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
        slices = ["ovvo", "ovov", "vvoo", "oovv"]
        for slice_ in slices:
            self.init_cache(f"g{slice_}", alloc=alloc(mo2, slice_))
