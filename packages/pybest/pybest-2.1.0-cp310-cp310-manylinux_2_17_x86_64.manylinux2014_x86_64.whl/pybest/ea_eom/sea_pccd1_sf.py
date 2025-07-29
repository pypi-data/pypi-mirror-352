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
from pybest.ea_eom.sea_base import RSEACC1
from pybest.linalg import (
    CholeskyFourIndex,
    DenseOneIndex,
    DenseThreeIndex,
    DenseTwoIndex,
    FourIndex,
)
from pybest.log import timer


class REApCCD1SF(RSEACC1):
    """Restricted Single Electron Affinity Equation of Motion Coupled Cluster
    class restricted to Single EA for a pCCD reference function and 1 unpaired
    electron (m_s = 0.5)

    This class defines only the function that are unique for the EA-pCCD model
    with 1 unpaired electron:

        * set_hamiltonian (calculates effective Hamiltonian -- at most O(o2v2))
        * compute_h_diag (pre-conditioner used by Davidson)
        * build_subspace_hamiltonian (subspace to be diagonalized)
    """

    acronym = "EA-EOM-pCCD"
    long_name = "Restricted Electron Affinity Equation of Motion pair Coupled Cluster Doubles"
    cluster_operator = "Tp"
    particle_hole_operator = "1p + 2p1h"
    reference = "pCCD"
    order = "EA"
    alpha = 1

    @timer.with_section("EApCCD1: H_diag sf")
    def compute_h_diag(self, *args: Any) -> DenseOneIndex:
        """Used by Davidson module for pre-conditioning
        Diagonal approximation to Hamiltonian in spin-free representation

        **Arguments:**

        args:
            required for Davidson module (not used here)
        """
        h_diag = self.lf.create_one_index(self.dimension, "h_diag")
        #
        # Get auxiliary matrices
        #
        nactv = self.occ_model.nactv[0]
        x1ac = self.from_cache("x1ac")
        #
        # x1ac(a,a)
        #
        x1aa = x1ac.copy_diagonal()
        h_diag.assign(x1aa, end0=nactv)
        #
        # 2 particle terms
        #
        if self.n_particle_operator >= 2:
            self.get_2_particle_terms_h_diag_sf(h_diag)

        return h_diag

    def get_2_particle_terms_h_diag_sf(self, h_diag: DenseThreeIndex) -> None:
        """Determine all contributions containing two particle operators for
        the spin-free representation:
            * H_abj,abj

        **Arguments:**

        h_diag:
            The diagonal elements of the Hamiltonian
        """
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        cia = self.checkpoint["t_p"]
        #
        # Get auxiliary matrices
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        x6bjck = self.from_cache("x6bjck")
        x9bc = self.from_cache("x9bc")
        x11jk = self.from_cache("x11jk")
        gpqpq = self.from_cache("gpqpq")
        gvvoo = self.from_cache("gvvoo")
        #
        # get ranges
        #
        vv = self.get_range("vv")
        #
        # H_abj,abj
        #
        h_abj = self.lf.create_three_index(nactv, nactv, nacto)
        #
        # x6(b,j,b,j)
        #
        x6bjck.expand("bcbc->abc", h_abj)
        #
        # x8(a,j,a,j)
        #
        x8ajck = self.from_cache("x8ajck")
        x8ajck.expand("acac->abc", h_abj)
        if self.dump_cache:
            self.cache.dump("x8ajck")
        #
        # x9(b,b)
        #
        x9bc.expand("bb->abc", h_abj)
        #
        # x10(a,a)
        #
        x9bc.expand("aa->abc", h_abj)
        #
        # x11(j,j)
        #
        # Check what is correct:
        x11jk.expand("cc->abc", h_abj)
        #
        # x12(a,b,a,b)
        #
        gpqpq.expand("ab->abc", h_abj, **vv)
        # gabkk cka dab
        tmp = gvvoo.contract("abcc,ca->ab", cia)
        tmp_d = tmp.copy_diagonal()
        tmp_d.expand("a->aab", h_abj)
        #
        # x13(j,j,b,a) dab
        #
        tmp = gvvoo.contract("aabb,ba->ab", cia)
        tmp.expand("ab->aab", h_abj, factor=-1.0)

        h_diag.assign(h_abj, begin0=nactv)

    @timer.with_section("EApCCD1: H_sub sf")
    def build_subspace_hamiltonian(
        self, b_vector: DenseOneIndex, h_diag: DenseOneIndex, *args: Any
    ) -> DenseOneIndex:
        """
        Used by Davidson module to construct subspace Hamiltonian in the
        spin-free representation

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
        x1ac = self.from_cache("x1ac")
        #
        # Get ranges for contract
        #
        nactv = self.occ_model.nactv[0]
        #
        # Calculate sigma vector (H.b_vector)
        #
        # output
        s_1 = self.lf.create_one_index(nactv)
        to_s_1 = {"out": s_1, "clear": False}
        sigma = self.lf.create_one_index(self.dimension)
        # input
        b_1 = self.lf.create_one_index(nactv)
        #
        # reshape b_vector
        #
        b_1.assign(b_vector, end1=nactv)
        #
        # R_a
        #
        # (1) xac rc
        #
        x1ac.contract("ab,b->a", b_1, **to_s_1)
        #
        # R_abj terms
        #
        if self.n_particle_operator >= 2:
            self.get_2_particle_terms_sf(b_1, b_vector, s_1, sigma)
        #
        # Assign to sigma vector
        #
        sigma.assign(s_1, begin0=0, end0=nactv)

        return sigma

    def get_2_particle_terms_sf(
        self,
        b_1: DenseOneIndex,
        b_vector: DenseOneIndex,
        s_1: DenseOneIndex,
        sigma: DenseOneIndex,
    ) -> None:
        """Determine all contributions containing two particle operators for
        the spin-free representation:
            * coupling terms to R_a
            * R_abj

        **Arguments:**

        b_1, b_vector:
            b vectors used in Davidson diagonalization

        s_1, sigma:
            sigma vectors used in Davidson diagonalization
        """
        cia = self.checkpoint["t_p"]
        #
        # Get auxiliary matrices
        #
        fock = self.from_cache("fock")
        x6bjck = self.from_cache("x6bjck")
        x7bjkc = self.from_cache("x7bjkc")
        x9bc = self.from_cache("x9bc")
        x11jk = self.from_cache("x11jk")
        govoo = self.from_cache("govoo")
        gvvoo = self.from_cache("gvvoo")
        gvovv = self.from_cache("gvovv")
        gvvvo = self.from_cache("gvvvo")
        gvvvv = self.from_cache("gvvvv")
        #
        # Get ranges for contract
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        ov = self.get_range("ov")
        ov3 = self.get_range("ov", start=3)
        #
        # Calculate sigma vector (H.b_vector)_kc
        #
        # output
        s_3 = self.lf.create_three_index(nactv, nactv, nacto)
        to_s_1 = {"out": s_1, "clear": False}
        to_s_3 = {"out": s_3, "clear": False}
        # input
        b_3 = self.lf.create_three_index(nactv, nactv, nacto)
        #
        # reshape b_vector
        #
        b_3.assign(b_vector, begin3=nactv)
        #
        # (2) xkc rack
        #
        b_3.contract("abc,cb->a", fock, **to_s_1, factor=2.0, **ov3)
        #
        # (3) x'kc rcak
        #
        b_3.contract("abc,ca->b", fock, **to_s_1, factor=-1.0, **ov3)
        #
        # (4) ldcak rdck
        #
        gvvvo.contract("abcd,abd->c", b_3, **to_s_1, factor=2.0)
        gvvvo.contract("abcd,bad->c", b_3, **to_s_1, factor=-1.0)
        #
        # R_abj !jba
        #
        # (5) x5jabc rc
        # gabcj rc
        gvvvo.contract("abcd,c->abd", b_1, **to_s_3)
        # [abj](gjabc rc) tjb
        tmp = s_3.copy()
        tmp.contract("abc,cb->abc", cia, s_3)
        # gajbc rc
        gvovv.contract("abcd,d->acb", b_1, tmp, clear=True)
        # [abj](gajbc rc) cjb
        tmp.contract("abc,cb->abc", cia, s_3, factor=-1.0)
        # [abj](gajbc rc) cja
        tmp.contract("abc,ca->abc", cia, s_3, factor=-1.0)
        # -fjc rc -> [j] cja dab
        tmp = fock.contract("ab,b->a", b_1, **ov)
        cia_ = cia.contract("ab,a->ba", tmp, out=None)
        cia_.expand("ab->aab", s_3, factor=-1.0)
        # gjckk rc -> [jk] cka dab [jk,ka]
        tmp = govoo.contract("abcc,b->ac", b_1)
        tmp_ = tmp.contract("ab,bc->ca", cia)
        tmp_.expand("ab->aab", s_3)
        #
        # (6) x6bjck rack
        #
        x6bjck.contract("abcd,ecd->eab", b_3, **to_s_3)
        #
        # (7) x7bjkc rcak
        #
        x7bjkc.contract("abcd,dec->eab", b_3, **to_s_3)
        #
        # (8) x8ajck rcbk
        #
        x8ajck = self.from_cache("x8ajck")
        x8ajck.contract("abcd,ced->aeb", b_3, **to_s_3)
        if self.dump_cache:
            self.cache.dump("x8ajck")
        #
        # (9) racj x9bc
        #
        b_3.contract("abc,eb->aec", x9bc, **to_s_3)
        #
        # (10) rcbj x10ac=x9bc
        #
        b_3.contract("abc,ea->ebc", x9bc, **to_s_3)
        #
        # (11) rabk x11jk
        #
        b_3.contract("abc,ec->abe", x11jk, **to_s_3)
        #
        # (12) (gabcd+gcdkk cka dab) rcdj
        #
        gvvvv.contract("abcd,cde->abe", b_3, **to_s_3)
        # rcdj gcdkk (jk)
        tmp = gvvoo.contract("abcc,abd->cd", b_3)
        # (jk) cka
        tmpja = tmp.contract("ab,bc->ca", cia)
        tmpja.expand("ab->aab", s_3)
        tmpja = None
        # (13) xkjcda rdck dab
        # Lcdkj rdck cja dab
        tmp = gvvoo.contract("abcd,bac->d", b_3, factor=2.0)
        gvvoo.contract("abcd,bad->c", b_3, tmp, factor=-1.0)
        cia_ = cia.contract("ab,a->ba", tmp)
        cia_.expand("ab->aab", s_3, factor=-1.0)
        #
        # Assign to sigma vector
        #
        sigma.assign(s_3, begin0=nactv)

    @timer.with_section("EApCCD1: H_eff sf")
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
        vvoo = self.get_range("vvoo")
        #
        # <pq|pq>
        #
        gpqpq = self.init_cache("gpqpq", nact, nact)
        mo2.contract("abab->ab", gpqpq)
        #
        # Inactive Fock matrix
        #
        fock = self.init_cache("fock", nact, nact)
        get_fock_matrix(fock, mo1, mo2, nacto)
        #
        # x1ac
        #
        x1ac = self.init_cache("x1ac", nactv, nactv)
        # fac
        x1ac.iadd(fock, 1.0, begin2=nacto, begin3=nacto)
        # -<ac|kk> cka
        mo2.contract("abcc,ca->ab", cia, x1ac, factor=-1.0, **vvoo)
        #
        # Effective Hamiltonian terms for 2 particle operators
        #
        if self.n_particle_operator >= 2:
            self.set_hamiltonian_2_particle(fock, mo2)
        #
        # Clean up
        #
        mo1.__del__()
        mo2.__del__()

    def set_hamiltonian_2_particle(
        self,
        fock: DenseTwoIndex,
        mo2: FourIndex,
    ) -> None:
        """Derive selected effective Hamiltonian for all 2 particle operators

        **Arguments:**

        fock:
            The Fock matrix

        mo2
            two-electron integrals
        """
        cia = self.checkpoint["t_p"]
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        #
        # Get ranges for contract
        #
        ovoo = self.get_range("ovoo")
        voov = self.get_range("voov")
        vovo = self.get_range("vovo")
        oovv = self.get_range("oovv")
        vvoo = self.get_range("vvoo")
        #
        # x9bc = x10ac
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
        # govoo
        #
        govoo = self.init_cache("govoo", nacto, nactv, nacto, nacto)
        mo2.contract("abcd->abcd", govoo, **ovoo)
        #
        # x8ajck
        #
        x8ajck = self.init_cache("x8ajck", nactv, nacto, nactv, nacto)
        # gajck
        mo2.contract("abcd->abcd", x8ajck, factor=-1.0, **vovo)
        # gcajk cja
        mo2.contract("abcd,cb->bcad", cia, x8ajck, **vvoo)
        if self.dump_cache:
            self.cache.dump("x8ajck")
        #
        # x6bjck
        #
        x6bjck = self.init_cache("x6bjck", nactv, nacto, nactv, nacto)
        # Lbkjc
        mo2.contract("abcd->acdb", x6bjck, factor=2.0, **voov)
        mo2.contract("abcd->adcb", x6bjck, factor=-1.0, **vovo)
        # Lbcjk cjb
        mo2.contract("abcd,ca->acbd", cia, x6bjck, factor=2.0, **vvoo)
        mo2.contract("abcd,da->adbc", cia, x6bjck, factor=-1.0, **vvoo)
        #
        # x7bjkc
        #
        x7bjkc = self.init_cache("x7bjkc", nactv, nacto, nacto, nactv)
        # gbcjk
        mo2.contract("abcd->acdb", x7bjkc, factor=-1.0, **vvoo)
        # -gbcjk+gbckj cjb
        mo2.contract("abcd,ca->acdb", cia, x7bjkc, factor=-1.0, **vvoo)
        mo2.contract("abcd,da->adcb", cia, x7bjkc, **vvoo)

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
        slices = ["vvoo", "vovv", "vvov", "vvvo", "vvvv"]
        for slice_ in slices:
            self.init_cache(f"g{slice_}", alloc=alloc(mo2, slice_))
