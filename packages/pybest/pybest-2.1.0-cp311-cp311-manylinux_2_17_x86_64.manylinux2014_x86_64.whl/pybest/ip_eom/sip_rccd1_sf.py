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
a CCD reference function in its spin-free formalism

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
:alpha:     number of unpaired electrons
:cia:       the pCCD pair amplitudes (T_p)
:t_p:       also used for the pCCD pair amplitudes (T_p)
:t_1:       the CC singles amplitudes (T_1)
:t_2:       the CC doubles amplitudes (T_2)

ndexing convention:
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


class RIPCCD1SF(RSIPCC1):
    """
    Restricted Single Ionization Potential Equation of Motion Coupled Cluster
    class restricted to Single IP for a CCD reference function and 1 unpaired
    electron (S_z = 0.5). A spin-free implementation.

    This class defines only the function that are universal for the IP-CCD model
    with 1 unpaired electron:

        * set_hamiltonian (calculates effective Hamiltonian -- at most O(o2v2))
        * compute_h_diag (pre-conditioner used by Davidson)
        * build_subspace_hamiltonian (subspace to be diagonalized)

    Note that their is only one R_ijb block (spin-independent). Thus, setting
    the number of hole operators equal to 2, requires at least 1 active
    occupied orbital.
    """

    long_name = (
        "Ionization Potential Equation of Motion Coupled Cluster Doubles"
    )
    acronym = "IP-EOM-CCD"
    reference = "CCD"
    order = "IP"
    alpha = 1
    disconnected_t1 = False

    @timer.with_section("IPCCD1: H_diag sf")
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
        the spin-independent representation:
            * H_ijb,ijb

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
        goovv = self.from_cache("goovv")
        #
        # Intermediates
        #
        xijij = xijkl.contract("abab->ab")
        xibkc = self.from_cache("xibkc")
        xibib = xibkc.contract("abab->ab")
        if self.dump_cache:
            self.cache.dump("xibkc")
        xjbkc = self.from_cache("xjbkc")
        xjbjb = xjbkc.contract("abab->ab")
        if self.dump_cache:
            self.cache.dump("xjbkc")
        #
        # H_ijb,ijb
        #
        h_ijb = self.lf.create_three_index(nacto, nacto, nactv)
        #
        # x1im(j,j)
        #
        x1im.expand("bb->abc", h_ijb)
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
        xjbjb.expand("bc->abc", h_ijb, factor=-2.0)
        #
        # xibkc(i,b,i,b)
        #
        xibib.expand("ac->abc", h_ijb)
        #
        # (-2 <ij|bd> + <ji|bd>) tidjb
        #
        # We will use dense 4-index intermediate here as it will be more
        # efficient for the diagonal terms
        # TODO: Check if faster on a GPU
        goovv = goovv.contract("abcd->abcd")
        goovv.contract("abcd,adbc->abc", t_2, h_ijb, factor=-2.0)
        goovv.contract("abcd,bdac->bac", t_2, h_ijb, factor=1.0)
        del goovv
        #
        # Assign using mask
        #
        h_diag.assign(h_ijb, begin0=nacto)

    @timer.with_section("IPCCD1: H_sub sf")
    def build_subspace_hamiltonian(
        self, b_vector: DenseOneIndex, h_diag: DenseOneIndex, *args: Any
    ) -> None:
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
        # R_ijb including coupling terms
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
        b_2 = self.lf.create_three_index(nacto, nacto, nactv)
        #
        # Assign rijb
        #
        b_2.assign(b_vector, begin3=nacto)
        #
        # Get coupling terms to R_i
        #
        self.get_2_hole_r_i_terms(b_2, s_1)
        #
        # R_ijb
        #
        self.get_2_hole_r_2_terms(b_1, b_2, s_2)
        sigma.assign(s_2, begin0=nacto)

    def get_2_hole_r_i_terms(
        self, b_2: DenseThreeIndex, s_1: DenseOneIndex
    ) -> None:
        """Determine all contributions containing two holes operators:
            * coupling terms to R_i

        **Arguments:**

        b_2:
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
        #
        # (2) ximkc rmkc
        #
        ximkc.contract("abcd,bcd->a", b_2, **to_s_1)
        #
        # (3) -2 xkc rikc
        #
        b_2.contract("abc,bc->a", xkc, factor=-2.0, **to_s_1)
        #
        # (3) xkc rkic
        #
        b_2.contract("abc,ac->b", xkc, **to_s_1)

    def get_2_hole_r_2_terms(
        self, b_1: DenseOneIndex, b_2: DenseThreeIndex, s_2: DenseTwoIndex
    ) -> None:
        """Determine all contributions containing two holes operators:
            * R_ijb (spin-free)

        **Arguments:**

        b_1, b_2:
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
        xijbm = self.from_cache("xijbm")
        xijkl = self.from_cache("xijkl")
        goovv = self.from_cache("goovv")
        #
        # (1) xijbm rm
        #
        xijbm.contract("abcd,d->abc", b_1, **to_s_2)
        #
        # (2) x1im(j,m) rimb
        #
        b_2.contract("abc,db->adc", x1im, **to_s_2)
        #
        # (2) x1im(i,m) rmjb
        #
        b_2.contract("abc,da->dbc", x1im, **to_s_2)
        #
        # (3) x4bd rijd
        #
        b_2.contract("abc,dc->abd", x4bd, **to_s_2)
        #
        # (4) xijkl rklb
        #
        xijkl.contract("abcd,cde->abe", b_2, **to_s_2)
        #
        # (5) xjbkc (-2 rikc + rkic)
        #
        xjbkc = self.from_cache("xjbkc")
        xjbkc.contract("abcd,ecd->eab", b_2, factor=-2.0, **to_s_2)
        xjbkc.contract("abcd,ced->eab", b_2, **to_s_2)
        if self.dump_cache:
            self.cache.dump("xjbkc")
        #
        # (5) xibkc rkjc + xibkc[j,b,k,c] rikc
        #
        xibkc = self.from_cache("xibkc")
        xibkc.contract("abcd,ced->aeb", b_2, **to_s_2)
        xibkc.contract("abcd,ecd->eab", b_2, **to_s_2)
        if self.dump_cache:
            self.cache.dump("xibkc")
        #
        # (6) -2 <kl|cd> rkld ticjb + <kl|dc> rkld ticjb
        tmp = goovv.contract("abcd,abd->c", b_2, factor=-2.0)
        goovv.contract("abcd,abc->d", b_2, tmp, factor=1.0)
        # ticjb (c)
        t_2.contract("abcd,b->acd", tmp, **to_s_2)

    @timer.with_section("IPCCD1: H_eff sf")
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
        # ximkc
        #
        self.set_hamiltonian_ximkc(gooov)
        #
        # xijbm
        #
        self.set_hamiltonian_xijbm(fock, gooov, mo2)
        #
        # xijkl
        #
        self.set_hamiltonian_xijkl(goooo, mo2)
        #
        # xjbkc
        #
        self.set_hamiltonian_xjbkc(mo2)
        #
        # xibkc
        #
        self.set_hamiltonian_xibkc(mo2)

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
        # (1) -fim
        x1im.iadd(fock, factor=-1.0, end2=nacto, end3=nacto)
        # (2) + (3) (-2 <mk|dc> + <mk|cd>) tidkc
        mo2.contract("abcd,ecbd->ea", t_2, x1im, factor=-2.0, **oovv)
        mo2.contract("abcd,edbc->ea", t_2, x1im, factor=1.0, **oovv)

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
        # -fkc
        xkc.iadd(fock, -1.0, end2=nacto, begin3=nacto)

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
        # (1) fbd
        x4bd.iadd(fock, 1.0, begin2=nacto, begin3=nacto)
        # (2) + (2') (-2 <mk|dc> + <mk|cd>) tmbkc -> <dc|mk>/<dc|km> tmbkc
        mo2.contract("abcd,cedb->ea", t_2, x4bd, factor=-2.0, **vvoo)
        mo2.contract("abcd,decb->ea", t_2, x4bd, factor=1.0, **vvoo)

    def set_hamiltonian_ximkc(self, gooov: DenseFourIndex) -> None:
        """Derive effective Hamiltonian term for ximkc intermediate

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
        ximkc = self.init_cache("ximkc", nacto, nacto, nacto, nactv)
        # (1) + (2) -2 <mk|ic> + <km|ic>
        gooov.contract("abcd->cabd", ximkc, factor=-2.0)
        gooov.contract("abcd->cbad", ximkc, factor=1.0)

    def set_hamiltonian_xijbm(
        self, fock: DenseTwoIndex, gooov: DenseFourIndex, mo2: DenseFourIndex
    ) -> None:
        """Derive effective Hamiltonian term for xijbm intermediate

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
        xijbm = self.init_cache("xijbm", nacto, nacto, nactv, nacto)
        #
        # a) connected terms
        # 1-1) -<ij|mb>
        gooov.contract("abcd->abdc", xijbm, factor=-1.0)
        # 1-4) -fmc ticjb
        t_2.contract("abcd,eb->acde", fock, xijbm, factor=-1.0, **ov4)
        # 1-5-5'') (-2 <mk|ic> + <km|ic>) tjbkc
        gooov.contract("abcd,efbd->cefa", t_2, xijbm, factor=-2.0)
        gooov.contract("abcd,efad->cefb", t_2, xijbm)
        # This term is missing in the original paper
        # 1-5') + <mk|ic> tjckb
        gooov.contract("abcd,edbf->cefa", t_2, xijbm, factor=1.0)
        # 1-5''') <km|jc> tickb -> <jm|kc> tickb
        gooov.contract("abcd,edcf->eafb", t_2, xijbm)
        # 1-6) -<mb|cd> ticjd
        mo2.contract("abcd,ecfd->efba", t_2, xijbm, factor=-1.0, **ovvv)

    def set_hamiltonian_xijkl(
        self, goooo: DenseFourIndex, mo2: DenseFourIndex
    ) -> None:
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
        # 4-1) <ij|kl>
        goooo.contract("abcd->abcd", xijkl)
        # 4-2) <kl|cd> ticjd
        mo2.contract("abcd,ecfd->efab", t_2, xijkl, **oovv)

    def set_hamiltonian_xjbkc(self, mo2: DenseFourIndex) -> None:
        """Derive effective Hamiltonian term for xjbkc intermediate

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
        # Effective Hamiltonian element xjbkc
        #
        xjbkc = self.init_cache("xjbkc", nacto, nactv, nacto, nactv)
        # 5-1'') -<jk|bc>
        mo2.contract("abcd->acbd", xjbkc, factor=-1.0, **oovv)
        # 5-2'-2v) (-2 <kl|cd> + <kl|dc>) tjbld -> <kl|cd>/<kc|dl>
        mo2.contract("abcd,efbd->efac", t_2, xjbkc, factor=-2.0, **oovv)
        mo2.contract("abcd,efdc->efab", t_2, xjbkc, factor=1.0, **ovvo)
        # 5-2''') <kl|cd> tjdlb
        mo2.contract("abcd,edbf->efac", t_2, xjbkc, factor=1.0, **oovv)

    def set_hamiltonian_xibkc(self, mo2: DenseFourIndex) -> None:
        """Derive effective Hamiltonian term for xibkc intermediate

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
        # Effective Hamiltonian element xibkc
        #
        xibkc = self.init_cache("xibkc", nacto, nactv, nacto, nactv)
        # 5-1') -<ib|kc>
        mo2.contract("abcd->abcd", xibkc, **ovov, factor=-1.0)
        # 5-2'''') <lk|cd> tidlb
        mo2.contract("abcd,edaf->efbc", t_2, xibkc, factor=1.0, **oovv)


class RIPLCCD1SF(RIPCCD1SF):
    """
    Restricted Single Ionization Potential Equation of Motion Coupled Cluster
    class restricted to Single IP for a LCCD reference function and 1 unpaired
    electron (S_z = 0.5). A spin-free implementation.
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


class RIPfpCCD1SF(RIPCCD1SF):
    """
    Restricted Single Ionization Potential Equation of Motion Coupled Cluster
    class restricted to Single IP for a fpCCD reference function and 1 unpaired
    electron (S_z = 0.5). A spin-free implementation.
    """

    long_name = "Ionization Potential Equation of Motion frozen pair Coupled Cluster Doubles"
    acronym = "IP-EOM-fpCCD"
    reference = "fpCCD"
    order = "IP"
    alpha = 1
    disconnected_t1 = False


class RIPfpLCCD1SF(RIPCCD1SF):
    """
    Restricted Single Ionization Potential Equation of Motion Coupled Cluster
    class restricted to Single IP for a fpLCCD/pCCD-LCCD reference function and
    1 unpaired electron (S_z = 0.5). A spin-free implementation.
    """

    long_name = (
        "Ionization Potential Equation of Motion frozen pair Coupled Cluster "
        "Linearized Doubles"
    )
    acronym = "IP-EOM-fpLCCD"
    reference = "fpLCCD"
    order = "IP"
    alpha = 1
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
