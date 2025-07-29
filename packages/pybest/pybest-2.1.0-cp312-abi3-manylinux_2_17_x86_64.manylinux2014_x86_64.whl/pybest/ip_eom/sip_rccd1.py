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
a CCD reference function

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
    :t_p:       also used for the pCCD pair amplitudes (T_p)
    :t_2:       the CC doubles amplitudes (T_2)

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
from pybest.ip_eom.sip_base import RSIPCC1
from pybest.linalg import (
    CholeskyFourIndex,
    DenseFourIndex,
    DenseOneIndex,
    DenseThreeIndex,
    DenseTwoIndex,
)
from pybest.log import timer


class RIPCCD1(RSIPCC1):
    """
    Restricted Single Ionization Potential Equation of Motion Coupled Cluster
    class restricted to Single IP for a CCD reference function and 1 unpaired
    electron (S_z = 0.5)

    This class defines only the function that are universal for the IP-CCD model
    with 1 unpaired electron:

        * set_hamiltonian (calculates effective Hamiltonian -- at most O(o2v2))
        * compute_h_diag (pre-conditioner used by Davidson)
        * build_subspace_hamiltonian (subspace to be diagonalized)

    Note that the R_ijb and R_iJB blocks are considered together. Thus, setting
    the number of hole operators equal to 2, requires at least 2 active
    occupied orbitals.
    """

    long_name = (
        "Ionization Potential Equation of Motion Coupled Cluster Doubles"
    )
    acronym = "IP-EOM-CCD"
    reference = "CCD"
    order = "IP"
    alpha = 1
    disconnected_t1 = True

    @timer.with_section("IPCCD1: H_diag")
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
        #
        # x1im(i,i)
        #
        x1im_diag = x1im.copy_diagonal()
        h_diag.assign(x1im_diag, end0=nacto)
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
        t_2 = self.checkpoint["t_2"]
        #
        # Get effective Hamiltonian terms
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        x1im = self.from_cache("x1im")
        x4bd = self.from_cache("x4bd")
        xijkl = self.from_cache("xijkl")
        xiJkL = self.from_cache("xiJkL")
        #
        # Intermediates
        #
        xijij = xijkl.contract("abab->ab")
        xjbKC = self.from_cache("xjbKC")
        xjbjb = xjbKC.contract("abab->ab")
        if self.dump_cache:
            self.cache.dump("xjbKC")
        xiBkC = self.from_cache("xiBkC")
        xiBkC.contract("abab->ab", xjbjb)
        if self.dump_cache:
            self.cache.dump("xiBkC")
        xiJiJ = xiJkL.contract("abab->ab")
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
        # xijkl(i,j,i,j)
        #
        xijij.expand("ab->abc", h_ijb)
        #
        # xjbkc(j,b,j,b)
        #
        xjbjb.expand("bc->abc", h_ijb)
        #
        # -0.25 <ij||db> (tidjb - tjdib)
        #
        goovv = self.from_cache("goovv")
        # We will use dense 4-index intermediate here as it will be more
        # efficient for the diagonal terms
        # TODO: Check if faster on a GPU
        goovv = goovv.contract("abcd->abcd")
        goovv.contract("abcd,acbd->abd", t_2, h_ijb, factor=-0.25)
        goovv.contract("abcd,bcad->abd", t_2, h_ijb, factor=0.25)
        goovv.contract("abcd,bcad->bad", t_2, h_ijb, factor=0.25)
        goovv.contract("abcd,acbd->bad", t_2, h_ijb, factor=-0.25)
        #
        # P+(ij)
        #
        h_ijb.iadd_transpose((1, 0, 2))
        #
        # Assign using mask
        #
        end = nacto + (nacto - 1) * nacto * nactv // 2
        h_diag.assign(h_ijb.array[self.get_mask(0)], begin0=nacto, end0=end)
        #
        # H_iJB,iJB
        # x1im(i,i)
        #
        x1im.expand("aa->abc", h_iJB)
        #
        # - <ij|db> tidjb
        #
        goovv.contract("abcd,acbd->abd", t_2, h_iJB, factor=-1.0)
        del goovv
        #
        # x4bd(b,b)
        #
        x4bd.expand("cc->abc", h_iJB)
        #
        # xiJkL(i,j,i,j)
        #
        xiJiJ.expand("ab->abc", h_iJB)
        #
        # xjbkc(j,b,j,b)
        #
        xjbjb.expand("bc->abc", h_iJB)
        #
        # Assign using mask
        #
        h_diag.assign(h_iJB, begin0=end)

    @timer.with_section("IPCCD1: H_sub")
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
        s_2 = self.lf.create_three_index(nacto, nacto, nactv)
        # Input
        b_2aa = self.lf.create_three_index(nacto, nacto, nactv)
        b_2bb = self.lf.create_three_index(nacto, nacto, nactv)
        #
        # Final index of b_2aa in b_vector
        #
        end = nacto + (nacto - 1) * nacto * nactv // 2
        #
        # Assign rijb
        #
        b_2aa.assign(
            b_vector, begin3=nacto, end3=end, ind0=self.get_index_of_mask(0)
        )
        b_2aa.iadd_transpose((1, 0, 2), factor=-1.0)
        # Assign riJB
        b_2bb.assign(b_vector, begin3=end)
        #
        # Get coupling terms to R_i
        #
        self.get_2_hole_r_i_terms(b_2aa, b_2bb, s_1)
        #
        # R_ijb
        #
        self.get_2_hole_r_2ss_terms(b_1, b_2aa, b_2bb, s_2)
        # Assign to sigma vector using mask
        sigma.assign(s_2.array[self.get_mask(0)], begin0=nacto, end0=end)
        #
        # R_iJB
        #
        self.get_2_hole_r_2os_terms(b_1, b_2aa, b_2bb, s_2)
        # Assign to sigma vector
        sigma.assign(s_2, begin0=end)

    def get_2_hole_r_i_terms(
        self,
        b_2aa: DenseThreeIndex,
        b_2bb: DenseThreeIndex,
        s_1: DenseOneIndex,
    ) -> None:
        """Determine all contributions containing two holes operators:
            * coupling terms to R_i

        **Arguments:**

        b_2aa, b_2bb:
            b vectors of different R operators used in the Davidson diagonalization

        s_1:
            sigma vector corresponding to R_i used in the Davidson diagonalization
        """
        to_s_1 = {"out": s_1, "clear": False}
        #
        # Get effective Hamiltonian terms
        #
        xkc = self.from_cache("xkc")
        ximkc = self.from_cache("ximkc")
        ximKC = self.from_cache("ximKC")
        #
        # (2) ximkc rmkc
        #
        ximkc.contract("abcd,bcd->a", b_2aa, **to_s_1)
        #
        # (3) ximKC rmKC
        #
        ximKC.contract("abcd,bcd->a", b_2bb, **to_s_1)
        #
        # (4) xkc rikc
        #
        b_2aa.contract("abc,bc->a", xkc, **to_s_1)
        #
        # (5) xkc riKC
        #
        b_2bb.contract("abc,bc->a", xkc, **to_s_1)

    def get_2_hole_r_2ss_terms(
        self,
        b_1: DenseOneIndex,
        b_2aa: DenseThreeIndex,
        b_2bb: DenseThreeIndex,
        s_2: DenseThreeIndex,
    ) -> None:
        """Determine all contributions containing two holes operators:
            * R_ijb (same spin - ss)

        **Arguments:**

        b_1, b_2aa, b_2bb:
            b vectors of different R operators used in Davidson diagonalization

        s_2:
            sigma vector corresponding to R_ijb used in Davidson diagonalization
        """
        s_2.clear()
        to_s_2 = {"out": s_2, "clear": False}
        t_2 = self.checkpoint["t_2"]
        #
        # Get effective Hamiltonian terms
        #
        x1im = self.from_cache("x1im")
        x2ijbm = self.from_cache("x2ijbm")
        x4bd = self.from_cache("x4bd")
        xijkl = self.from_cache("xijkl")
        #
        # (6) P(ij) x2ijbm rm
        #
        x2ijbm.contract("abcd,d->abc", b_1, **to_s_2)
        #
        # (7) P(ij) rimb x1jm
        #
        b_2aa.contract("abc,db->adc", x1im, **to_s_2)
        #
        # (8) 0.5 P(ij) x4bd rijd
        #
        b_2aa.contract("abc,dc->abd", x4bd, factor=0.5, **to_s_2)
        #
        # (9) P(ij) xijkl rklb
        #
        xijkl.contract("abcd,cde->abe", b_2aa, **to_s_2)
        #
        # (10) P(ij) (xjbKC + xiBkC[j,b,k,c]) rikc
        #
        xiBkC = self.from_cache("xiBkC")
        xiBkC.contract("abcd,ecd->eab", b_2aa, **to_s_2)
        if self.dump_cache:
            self.cache.dump("xjbKC")
        xjbKC = self.from_cache("xjbKC")
        xjbKC.contract("abcd,ecd->eab", b_2aa, **to_s_2)
        #
        # (11) P(ij) xjbKC riKC
        #
        xjbKC.contract("abcd,ecd->eab", b_2bb, **to_s_2)
        if self.dump_cache:
            self.cache.dump("xjbKC")
        #
        # (12)
        # -0.25 P(ij) <kl||cd> rlkc (tidjb - tjdib)
        # -0.5  P(ij) <kl| cd> rlKC (tidjb - tjdib)
        # (d) = -0.25 <kl||cd> rlkc - 0.5 <kl| cd> rlKC
        goovv = self.from_cache("goovv")
        tmp = goovv.contract("abcd,bac->d", b_2aa, factor=-0.25)
        goovv.contract("abcd,bad->c", b_2aa, tmp, factor=0.25)
        goovv.contract("abcd,bac->d", b_2bb, tmp, factor=-0.5)
        # (tidjb - tibjd) (d)
        t_2.contract("abcd,b->acd", tmp, **to_s_2)
        t_2.contract("abcd,d->acb", tmp, factor=-1.0, **to_s_2)
        #
        # P(ij)
        #
        s_2.iadd_transpose((1, 0, 2), factor=-1.0)

    def get_2_hole_r_2os_terms(
        self,
        b_1: DenseOneIndex,
        b_2aa: DenseThreeIndex,
        b_2bb: DenseThreeIndex,
        s_2: DenseThreeIndex,
    ) -> None:
        """Determine all contributions containing two holes operators:
            * R_iJB (opposite spin - os)

        **Arguments:**

        b_1, b_2aa, b_2bb:
            b vectors of different R operators used in Davidson diagonalization

        s_2:
            sigma vector corresponding to R_iJB used in Davidson diagonalization
        """
        s_2.clear()
        to_s_2 = {"out": s_2, "clear": False}
        t_2 = self.checkpoint["t_2"]
        #
        # Get effective Hamiltonian terms
        #
        x1im = self.from_cache("x1im")
        x4bd = self.from_cache("x4bd")
        xiJBm = self.from_cache("xiJBm")
        xiJkL = self.from_cache("xiJkL")
        xiBkC = self.from_cache("xiBkC")
        xjbKC = self.from_cache("xjbKC")
        goovv = self.from_cache("goovv")
        #
        # (13) xiJBm rm
        #
        xiJBm.contract("abcd,d->abc", b_1, **to_s_2)
        #
        # (14) riMB x1im(j,m)
        #
        b_2bb.contract("abc,db->adc", x1im, **to_s_2)
        #
        # (15) x1im(i,m) rmJB
        #
        b_2bb.contract("abc,da->dbc", x1im, **to_s_2)
        #
        # (16) x4bd riJD
        #
        b_2bb.contract("abc,dc->abd", x4bd, **to_s_2)
        #
        # (17) xiJkL rkLB
        #
        xiJkL.contract("abcd,cde->abe", b_2bb, **to_s_2)
        #
        # (18) xjbKC rikc
        #
        xjbKC.contract("abcd,ecd->eab", b_2aa, **to_s_2)
        #
        # (19) (xjbKC + xiBkC[j,b,k,c]) xjbkc riKC
        #
        xjbKC.contract("abcd,ecd->eab", b_2bb, **to_s_2)
        xiBkC.contract("abcd,ecd->eab", b_2bb, **to_s_2)
        #
        # (20) xiBkC rkJC
        #
        xiBkC.contract("abcd,ced->aeb", b_2bb, **to_s_2)
        #
        # (21) rkld dij
        # -0.5 <kl||cd> rlkc tidjb
        # -    <kl| cd> rlKC tidjb
        # (d) = -0.5 <kl||cd> rlkc - <kl| cd> rlKC
        tmp = goovv.contract("abcd,bac->d", b_2aa, factor=-0.5)
        goovv.contract("abcd,bad->c", b_2aa, tmp, factor=0.5)
        goovv.contract("abcd,bac->d", b_2bb, tmp, factor=-1.0)
        # tidjb (d)
        t_2.contract("abcd,b->acd", tmp, **to_s_2)

    @timer.with_section("IPCCD1: H_eff")
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
        nacto, nact = self.occ_model.nacto[0], self.occ_model.nact[0]
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
        #
        # Get ranges
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        oooo = self.get_range("oooo")
        ooov = self.get_range("ooov")
        #
        # xkc
        #
        self.set_hamiltonian_xkc(fock)
        #
        # x4bd
        #
        self.set_hamiltonian_x4bd(fock, mo2)
        #
        # Intermediates used to construct others: goooo and gooov
        #
        gooov = self.denself.create_four_index(nacto, nacto, nacto, nactv)
        mo2.contract("abcd->abcd", out=gooov, **ooov)
        goooo = self.denself.create_four_index(nacto, nacto, nacto, nacto)
        mo2.contract("abcd->abcd", goooo, **oooo)
        #
        # ximKC
        #
        self.set_hamiltonian_ximKC(gooov)
        #
        # ximkc
        #
        self.set_hamiltonian_ximkc(gooov)
        #
        # xiJBm
        #
        self.set_hamiltonian_xiJBm(fock, gooov, mo2)
        #
        # x2ijbm
        #
        self.set_hamiltonian_x2ijbm(fock, gooov, mo2)
        #
        # xiJkL
        #
        self.set_hamiltonian_xiJkL(goooo, mo2)
        #
        # xijkl
        #
        self.set_hamiltonian_xijkl(goooo, mo2)
        #
        # xjbKC
        #
        self.set_hamiltonian_xjbKC(mo2)
        #
        # xiBkC
        #
        self.set_hamiltonian_xiBkC(mo2)

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
        # -fim
        x1im.iadd(fock, factor=-1.0, end2=nacto, end3=nacto)
        #
        # a) connected terms
        # - 0.5 (<mk|dc> - <mk|cd>) (tidkc - tickd)
        mo2.contract("abcd,ecbd->ea", t_2, x1im, factor=-0.5, **oovv)
        mo2.contract("abcd,edbc->ea", t_2, x1im, factor=0.5, **oovv)
        mo2.contract("abcd,edbc->ea", t_2, x1im, factor=0.5, **oovv)
        mo2.contract("abcd,ecbd->ea", t_2, x1im, factor=-0.5, **oovv)
        # - <mk|dc> tidkc
        mo2.contract("abcd,ecbd->ea", t_2, x1im, factor=-1.0, **oovv)

    def set_hamiltonian_xkc(self, fock: DenseTwoIndex) -> None:
        """Derive effective Hamiltonian term for xkc intermediate

        **Arguments:**

        fock
            Fock matrix
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

    def set_hamiltonian_xiJBm(
        self, fock: DenseTwoIndex, gooov: DenseFourIndex, mo2: DenseFourIndex
    ) -> None:
        """Derive effective Hamiltonian term for xiJBm intermediate

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
        # effective hamiltonian elements
        #
        xiJBm = self.init_cache("xiJBm", nacto, nacto, nactv, nacto)
        #
        # a) connected terms
        # 1-1) -<ij|mb>
        gooov.contract("abcd->abdc", xiJBm, factor=-1.0)
        # -fmc ticjb
        t_2.contract("abcd,eb->acde", fock, xiJBm, factor=-1.0, **ov4)
        # 1-5) -<mk||ic> tjbkc
        gooov.contract("abcd,efbd->cefa", t_2, xiJBm, factor=-1.0)
        gooov.contract("abcd,efad->cefb", t_2, xiJBm)
        # 1-5) - <mk|ic> (tjbkc - tjckb)
        gooov.contract("abcd,efbd->cefa", t_2, xiJBm, factor=-1.0)
        gooov.contract("abcd,edbf->cefa", t_2, xiJBm, factor=1.0)
        # 1-5') <jm|kd> tidkb
        gooov.contract("abcd,edcf->eafb", t_2, xiJBm)
        # 1-6) -<mb|cd> ticjd
        mo2.contract("abcd,ecfd->efba", t_2, xiJBm, factor=-1.0, **ovvv)

    def set_hamiltonian_x2ijbm(
        self, fock: DenseTwoIndex, gooov: DenseFourIndex, mo2: DenseFourIndex
    ) -> None:
        """Derive effective Hamiltonian term for x2ijbm intermediate

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
        # x2ijbm
        #
        x2ijbm = self.init_cache("x2ijbm", nacto, nacto, nactv, nacto)
        # 1-1) -0.5 <ij||mb> -> <ij|mb>/<ji|mb>
        gooov.contract("abcd->abdc", x2ijbm, factor=-0.5)
        gooov.contract("abcd->badc", x2ijbm, factor=0.5)
        # 1-4) -0.5 fmc (ticjb - tjcib)
        t_2.contract("abcd,eb->acde", fock, x2ijbm, factor=-0.5, **ov4)
        t_2.contract("abcd,eb->cade", fock, x2ijbm, factor=0.5, **ov4)
        # 1-5) -<mk||ic> (tjbkc - tjckb)
        gooov.contract("abcd,efbd->cefa", t_2, x2ijbm, factor=-1.0)
        gooov.contract("abcd,efad->cefb", t_2, x2ijbm, factor=1.0)
        gooov.contract("abcd,edbf->cefa", t_2, x2ijbm, factor=1.0)
        gooov.contract("abcd,edaf->cefb", t_2, x2ijbm, factor=-1.0)
        # 1-5) - <mk|ic> tjbkc
        gooov.contract("abcd,efbd->cefa", t_2, x2ijbm, factor=-1.0)
        # 1-6) -0.25 <mb||cd> (ticjd - tidjc) -> -0.5 <mb||cd> ticjd
        mo2.contract("abcd,ecfd->efba", t_2, x2ijbm, factor=-0.5, **ovvv)
        mo2.contract("abcd,ecfd->efab", t_2, x2ijbm, factor=0.5, **vovv)

    def set_hamiltonian_ximKC(self, gooov: DenseFourIndex) -> None:
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

    def set_hamiltonian_xiJkL(
        self, goooo: DenseFourIndex, mo2: DenseFourIndex
    ):
        """Derive effective Hamiltonian term for xiJkL intermediate

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
        # Effective Hamiltonian element xiJkL
        #
        xiJkL = self.init_cache("xiJkL", nacto, nacto, nacto, nacto)
        # <ij|kl>
        goooo.contract("abcd->abcd", xiJkL)
        # <kl|cd> ticjd
        mo2.contract("abcd,ecfd->efab", t_2, xiJkL, **oovv)

    def set_hamiltonian_xijkl(
        self, goooo: DenseFourIndex, mo2: DenseFourIndex
    ):
        """Derive effective Hamiltonian term for xijkl intermediate

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
        # Effective Hamiltonian element xijkl
        #
        xijkl = self.init_cache("xijkl", nacto, nacto, nacto, nacto)
        # 0.25 <ij||kl>
        goooo.contract("abcd->abcd", xijkl, factor=0.25)
        goooo.contract("abcd->abdc", xijkl, factor=-0.25)
        # 0.125 <kl||cd> (ticjd - tidjc) -> 0.25 <kl||cd> ticjd
        mo2.contract("abcd,ecfd->efab", t_2, xijkl, factor=0.25, **oovv)
        mo2.contract("abcd,ecfd->efba", t_2, xijkl, factor=-0.25, **oovv)

    def set_hamiltonian_xiBkC(self, mo2: DenseFourIndex) -> None:
        """Derive effective Hamiltonian term for xiBkC intermediate

        **Arguments:**

        mo2
            two-electron integrals for specific blocks.
        """
        #
        # Get ranges
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        oovv = self.get_range("oovv")
        ovov = self.get_range("ovov")
        t_2 = self.checkpoint["t_2"]
        #
        # Effective Hamiltonian element xiBkC
        #
        xiBkC = self.init_cache("xiBkC", nacto, nactv, nacto, nactv)
        # -<ib|kc>
        mo2.contract("abcd->abcd", xiBkC, **ovov, factor=-1.0)
        # <lk|cd> tidlb
        mo2.contract("abcd,edaf->efbc", t_2, xiBkC, factor=1.0, **oovv)

    def set_hamiltonian_xjbKC(self, mo2: DenseFourIndex) -> None:
        """Derive effective Hamiltonian term for xjbKC intermediate

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
        # Effective Hamiltonian element xjbKC
        #
        xjbKC = self.init_cache("xjbKC", nacto, nactv, nacto, nactv)
        # 5-1) <jk|bc>
        mo2.contract("abcd->acbd", xjbKC, **oovv)
        # 5-2) <kl||cd> tjbld -> <kl|cd>/<kc|dl>
        mo2.contract("abcd,efbd->efac", t_2, xjbKC, factor=1.0, **oovv)
        mo2.contract("abcd,efdc->efab", t_2, xjbKC, factor=-1.0, **ovvo)
        # 5-2) <kl|cd> (tjbld - tjdlb)
        mo2.contract("abcd,efbd->efac", t_2, xjbKC, factor=1.0, **oovv)
        mo2.contract("abcd,edbf->efac", t_2, xjbKC, factor=-1.0, **oovv)


class RIPLCCD1(RIPCCD1):
    """
    Restricted Single Ionization Potential Equation of Motion Coupled Cluster
    class restricted to Single IP for a LCCD reference function and 1 unpaired
    electron (S_z = 0.5)
    """

    long_name = (
        "Ionization Potential Equation of Motion Linearized Coupled Cluster "
        "Doubles"
    )
    acronym = "IP-EOM-LCCD"
    reference = "LCCD"
    order = "IP"
    alpha = 1
    disconnected_t1 = False


class RIPfpCCD1(RIPCCD1):
    """
    Restricted Single Ionization Potential Equation of Motion Coupled Cluster
    class restricted to Single IP for a fpCCD reference function and 1 unpaired
    electron (S_z = 0.5)
    """

    long_name = (
        "Ionization Potential Equation of Motion frozen pair Coupled Cluster "
        "Doubles"
    )
    acronym = "IP-EOM-fpCCD"
    reference = "fpCCD"
    order = "IP"
    alpha = 1
    disconnected_t1 = False


class RIPfpLCCD1(RIPCCD1):
    """
    Restricted Single Ionization Potential Equation of Motion Coupled Cluster
    class restricted to Single IP for a fpLCCD/pCCD-LCCD reference function
    and 1 unpaired electron (S_z = 0.5)

    This class (re)defines only the function that are unique for the IP-fpLCCD
    model with 1 unpaired electron:

        * setting/resetting the seniority 0 sector
        * redefining effective Hamiltonian elements to include only T1.Tp terms
    """

    long_name = (
        "Ionization Potential Equation of Motion frozen pair Coupled "
        "Cluster Linearized Doubles"
    )
    acronym = "IP-EOM-fpLCCD"
    reference = "fpLCCD"
    order = "IP"
    alpha = 1
    disconnected_t1 = False

    def set_seniority_0(self):
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

    def reset_seniority_0(self):
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
