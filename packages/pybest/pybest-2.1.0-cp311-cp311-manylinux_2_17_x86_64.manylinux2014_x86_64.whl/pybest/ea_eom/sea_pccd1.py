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


class REApCCD1(RSEACC1):
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

    @timer.with_section("EApCCD1: H_diag")
    def compute_h_diag(self, *args: Any) -> DenseOneIndex:
        """Used by Davidson module for pre-conditioning.
        Diagonal approximation to Hamiltonian for S_z=0.5

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
        # H_a,a
        #
        # x1ac(a,a)
        x1aa = x1ac.copy_diagonal()
        h_diag.assign(x1aa, end0=nactv)
        #
        # 2 particle terms
        #
        if self.n_particle_operator >= 2:
            self.get_2_particle_terms_h_diag(h_diag)

        return h_diag

    def get_2_particle_terms_h_diag(self, h_diag: DenseThreeIndex) -> None:
        """Determine all contributions containing two particle operators for
        the spin-dependent representation:
            * H_abj,abj
            * H_aBJ,BJ

        **Arguments:**

        h_diag:
            The diagonal elements of the Hamiltonian
        """
        cia = self.checkpoint["t_p"]
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        #
        # Get auxiliary matrices
        #
        x9bc = self.from_cache("x9bc")
        x11jk = self.from_cache("x11jk")
        gvvvv = self.from_cache("gvvvv")
        #
        # get intermediates
        #
        gabab = gvvvv.contract("abab->ab")
        labab = gabab.copy()
        gvvvv.contract("abba->ab", labab, factor=-1.0)
        x4bjck = self.from_cache("x4bjck")
        x4bj = x4bjck.contract("abab->ab")
        if self.dump_cache:
            self.cache.dump("x4bjck")
        x8ajck = self.from_cache("x8ajck")
        x8aj = x8ajck.contract("abab->ab")
        if self.dump_cache:
            self.cache.dump("x8ajck")
        gvvoo = self.from_cache("gvvoo")
        gbbjj = gvvoo.contract("aabb->ab")
        #
        # H_abj,abj
        #
        h_abj = self.lf.create_three_index(nactv, nactv, nacto)
        #
        # x9bc(b,b)
        #
        x9bc.expand("bb->abc", h_abj)
        #
        # x11jk(j,j)
        #
        x11jk.expand("cc->abc", h_abj, factor=0.5)
        #
        # ab||ab
        #
        labab.expand("ab->abc", h_abj, factor=0.25)
        #
        # x4bjck(b,j,b,j)
        #
        x4bj.expand("bc->abc", h_abj)
        #
        # P(ab)
        h_abj.iadd_transpose((1, 0, 2))
        #
        # assign using mask
        #
        end_3aa = nactv + (nactv - 1) * nactv * nacto // 2
        h_diag.assign(
            h_abj.array[self.get_mask(0)], begin0=nactv, end0=end_3aa
        )
        #
        # H_aBJ,aBJ
        #
        h_abj.clear()
        #
        # x9bc(b,b)
        #
        x9bc.expand("bb->abc", h_abj)
        #
        # x9bc(a,a)
        #
        x9bc.expand("aa->abc", h_abj)
        #
        # x11jk(j,j)
        #
        x11jk.expand("cc->abc", h_abj)
        #
        # x4bjck(b,j,b,j)
        #
        x4bj.expand("bc->abc", h_abj)
        #
        # x8ajck(a,j,a,j)
        #
        x8aj.expand("bc->abc", h_abj)
        #
        # ab|ab
        #
        gabab.expand("ab->abc", h_abj)
        #
        # dab( aa|kk cka - aa|jj cja)
        #
        tmp = gbbjj.contract("ab,ba->a", cia, out=None)
        tmp.expand("a->aab", h_abj)
        # [aj] -> aaj
        tmp = gbbjj.contract("ab,ba->ab", cia, out=None)
        tmp.expand("ab->aab", h_abj, factor=-1.0)
        #
        # assign using mask
        #
        h_diag.assign(h_abj, begin0=end_3aa)

    @timer.with_section("EApCCD1: H_sub")
    def build_subspace_hamiltonian(
        self, b_vector: DenseOneIndex, h_diag: DenseOneIndex, *args: Any
    ) -> DenseOneIndex:
        """
        Used by Davidson module to construct subspace Hamiltonian
        for S_z=0.5 states

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
        nactv = self.occ_model.nactv[0]
        x1ac = self.from_cache("x1ac")
        #
        # Calculate sigma vector (H.b_vector)_kc
        #
        # output
        s_1 = self.lf.create_one_index(nactv)
        to_s_1 = {"out": s_1, "clear": False}
        sigma = self.lf.create_one_index(self.dimension)
        # input
        b_1 = self.lf.create_one_index(nactv)
        #
        # assign R_a
        #
        b_1.assign(b_vector, end1=nactv)
        #
        # R_a
        #
        # (1) xac rc
        #
        x1ac.contract("ab,b->a", b_1, **to_s_1)
        #
        # R_abj/R_aBJ including coupling terms
        #
        if self.n_particle_operator >= 2:
            self.get_2_particle_terms(b_1, s_1, b_vector, sigma)
        #
        # Assign to sigma vector
        #
        sigma.assign(s_1, begin0=0, end0=nactv)
        del s_1

        return sigma

    def get_2_particle_terms(
        self,
        b_1: DenseOneIndex,
        s_1: DenseOneIndex,
        b_vector: DenseOneIndex,
        sigma: DenseOneIndex,
    ) -> None:
        """Determine all contributions containing two particle operators:
            * coupling terms to R_a
            * R_abj
            * R_aBJ

        **Arguments:**

        b_1, b_vector:
            b vectors used in Davidson diagonalization

        s_1, sigma:
            sigma vectors used in Davidson diagonalization
        """
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        #
        # Calculate sigma vector (H.b_vector) of 2 particle terms
        #
        # output
        s_3 = self.lf.create_three_index(nactv, nactv, nacto)
        # input
        b_3aa = self.lf.create_three_index(nactv, nactv, nacto)
        b_3bb = self.lf.create_three_index(nactv, nactv, nacto)
        #
        # Final index of b_3aa in b_vector
        #
        end = nactv + (nactv - 1) * nactv * nacto // 2
        #
        # reshape b_vector
        # assign rabj
        b_3aa.assign(
            b_vector, begin3=nactv, end3=end, ind0=self.get_index_of_mask(0)
        )
        b_3aa.iadd_transpose((1, 0, 2), factor=-1.0)
        # assign raBJ
        b_3bb.assign(b_vector, begin3=end)
        #
        # Get coupling terms to R_a
        #
        self.get_2_particle_r_a_terms(b_3aa, b_3bb, s_1)
        #
        # R_abj
        #
        if nactv > 1:
            self.get_2_particle_r_3ss_terms(b_1, b_3aa, b_3bb, s_3)
            # Assign to sigma vector using mask
            sigma.assign(s_3.array[self.get_mask(0)], begin0=nactv, end0=end)
        #
        # R_aBJ
        #
        self.get_2_particle_r_3os_terms(b_1, b_3aa, b_3bb, s_3)
        # Assign to sigma vector
        sigma.assign(s_3, begin0=end)

    def get_2_particle_r_a_terms(
        self,
        b_3aa: DenseThreeIndex,
        b_3bb: DenseThreeIndex,
        s_1: DenseOneIndex,
    ) -> None:
        """Determine all contributions containing two particle operators:
            * coupling terms to R_a

        **Arguments:**

        b_3aa, b_3bb:
            b vectors of different R operators used in Davidson diagonalization

        s_1:
            sigma vector corresponding to R_a used in Davidson diagonalization
        """
        to_s_1 = {"out": s_1, "clear": False}
        #
        # Get auxiliary matrices
        #
        fock = self.from_cache("fock")
        gvovv = self.from_cache("gvovv")
        #
        # Get ranges for contract
        #
        vo3 = self.get_range("vo", start=3)
        #
        # (2) 0.5 ak||dc rdck
        #
        gvovv.contract("abcd,cdb->a", b_3aa, **to_s_1, factor=0.5)
        gvovv.contract("abcd,dcb->a", b_3aa, **to_s_1, factor=-0.5)
        #
        # (3) ak|dc rdCK
        #
        gvovv.contract("abcd,cdb->a", b_3bb, **to_s_1)
        #
        # (4) fck rack
        #
        b_3aa.contract("abc,bc->a", fock, **to_s_1, **vo3)
        #
        # (5) fck raCK
        #
        b_3bb.contract("abc,bc->a", fock, **to_s_1, **vo3)

    def get_2_particle_r_3ss_terms(
        self,
        b_1: DenseOneIndex,
        b_3aa: DenseThreeIndex,
        b_3bb: DenseThreeIndex,
        s_3: DenseThreeIndex,
    ) -> None:
        """Determine all contributions containing two particle operators:
            * R_abj (same spin - ss)

        **Arguments:**

        b_1, b_3aa, b_3bb:
            b vectors of different R operators used in Davidson diagonalization

        s_3:
            sigma vector corresponding to R_abj used in Davidson diagonalization
        """
        s_3.clear()
        cia = self.checkpoint["t_p"]
        to_s_3 = {"out": s_3, "clear": False}
        #
        # Get auxiliary matrices
        #
        x9bc = self.from_cache("x9bc")
        x11jk = self.from_cache("x11jk")
        gvvov = self.from_cache("gvvov")
        gvvvo = self.from_cache("gvvvo")
        gvvvv = self.from_cache("gvvvv")
        #
        # optimize contractions due to memory bottleneck
        #
        #
        # (6) rc (ab||cj + ab|cj cjb)
        #
        tmp = gvvvo.contract("abcd,c->abd", b_1, factor=1.0)
        s_3.iadd(tmp, factor=0.5)
        gvvov.contract("abcd,d->abc", b_1, s_3, factor=-0.5)
        tmp.contract("abc,cb->abc", cia, s_3)
        #
        # (7) racj x9bc
        #
        b_3aa.contract("abc,db->adc", x9bc, **to_s_3)
        #
        # (8) rabk x11jk
        #
        b_3aa.contract("abc,dc->abd", x11jk, **to_s_3, factor=0.5)
        #
        # (9) rcdj ab||cd
        # Bottlenck operations
        gvvvv.contract("abcd,cde->abe", b_3aa, **to_s_3, factor=0.25)
        gvvvv.contract("abcd,dce->abe", b_3aa, **to_s_3, factor=-0.25)
        #
        # (10) rack x4bjck
        #
        x4bjck = self.from_cache("x4bjck")
        x4bjck.contract("abcd,ecd->eab", b_3aa, **to_s_3)
        if self.dump_cache:
            self.cache.dump("x4bjck")
        #
        # (11) raCK x5bjck
        #
        x5bjck = self.from_cache("x5bjck")
        x5bjck.contract("abcd,ecd->eab", b_3bb, **to_s_3)
        #
        # P(ab)
        #
        s_3.iadd_transpose((1, 0, 2), factor=-1.0)

    def get_2_particle_r_3os_terms(
        self,
        b_1: DenseOneIndex,
        b_3aa: DenseThreeIndex,
        b_3bb: DenseThreeIndex,
        s_3: DenseThreeIndex,
    ) -> None:
        """Determine all contributions containing two particle operators:
            * R_aBJ (opposite spin - os)

        **Arguments:**

        b_1, b_3aa, b_3bb:
            b vectors of different R operators used in Davidson diagonalization

        s_3:
            sigma vector corresponding to R_aBJ used in Davidson diagonalization
        """
        s_3.clear()
        cia = self.checkpoint["t_p"]
        to_s_3 = {"out": s_3, "clear": False}
        #
        # Get auxiliary matrices
        #
        fock = self.from_cache("fock")
        x9bc = self.from_cache("x9bc")
        x11jk = self.from_cache("x11jk")
        govoo = self.from_cache("govoo")
        gvvoo = self.from_cache("gvvoo")
        gvovv = self.from_cache("gvovv")
        gvvvo = self.from_cache("gvvvo")
        gvvvv = self.from_cache("gvvvv")
        #
        # optimize contractions due to memory bottleneck
        #
        #
        # Get ranges for contract
        #
        ov = self.get_range("ov")
        #
        # (12) rc (ab|cj - aj||bc cjb - aj|bc cja + dab [-fjc cja + jc|kk cka])
        # [abj]
        gvvvo.contract("abcd,c->abd", b_1, **to_s_3)
        # aj|bc rc => [abj]
        tmp = gvovv.contract("abcd,d->acb", b_1, factor=-1.0)
        # [abj] cja
        tmp.contract("abc,ca->abc", cia, s_3)
        # [abj] + ex. -> [abj] cjb
        gvovv.contract("abcd,c->adb", b_1, tmp)
        tmp.contract("abc,cb->abc", cia, s_3)
        # [fjc rc] -> [j] cja -> [aj]
        tmp = fock.contract("ab,b->a", b_1, factor=-1.0, **ov)
        tmp_aj = cia.contract("ab,a->ba", tmp, out=None)
        # [jc|kk rc] -> [jk] cka -> [aj]
        tmp = govoo.contract("abcc,b->ac", b_1, out=None)
        tmp.contract("ab,bc->ca", cia, tmp_aj)
        # dab
        tmp_aj.expand("ab->aab", s_3)
        #
        # (13) raCJ x9bc
        #
        b_3bb.contract("abc,db->adc", x9bc, **to_s_3)
        #
        # (14) rcBJ x9ac
        #
        b_3bb.contract("abc,da->dbc", x9bc, **to_s_3)
        #
        # (15) raBK x11jk
        #
        b_3bb.contract("abc,dc->abd", x11jk, **to_s_3)
        #
        # (16) rcDJ (ab|cd + cd|kk cka dab)
        # Bottlenck operations
        gvvvv.contract("abcd,cde->abe", b_3bb, **to_s_3)
        # [kj] cka
        tmp = gvvoo.contract("abcc,abd->cd", b_3bb)
        # [aj]
        tmp1 = tmp.contract("ab,ac->cb", cia)
        tmp1.expand("ab->aab", s_3)
        del tmp, tmp1
        #
        # (17) rack x5bjck
        #
        x5bjck = self.from_cache("x5bjck")
        x5bjck.contract("abcd,ecd->eab", b_3aa, **to_s_3)
        if self.dump_cache:
            self.cache.dump("x5bjck")
        #
        # (18) raCK x4bjck
        #
        x4bjck = self.from_cache("x4bjck")
        x4bjck.contract("abcd,ecd->eab", b_3bb, **to_s_3)
        if self.dump_cache:
            self.cache.dump("x4bjck")
        #
        # (19) rcBK x8ajck
        #
        x8ajck = self.from_cache("x8ajck")
        x8ajck.contract("abcd,ced->aeb", b_3bb, **to_s_3)
        if self.dump_cache:
            self.cache.dump("x8ajck")
        #
        # (20) rdck (- dc||jk cja dab)
        #
        tmp = gvvoo.contract("abcd,abd->c", b_3aa, factor=-0.5)
        gvvoo.contract("abcd,abc->d", b_3aa, tmp, factor=0.5)
        # [j] cja
        tmpj = cia.contract("ab,a->ba", tmp, out=None)
        del tmp
        #
        # (21) rdCK (- dc|jk cja dab)
        #
        tmp = gvvoo.contract("abcd,abd->c", b_3bb, factor=-1.0)
        # [j] cja
        cia.contract("ab,a->ba", tmp, tmpj)
        tmpj.expand("ab->aab", s_3)
        del tmpj

    @timer.with_section("EApCCD1: H_eff")
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
        # temporary object gvvoo
        #
        gvvoo = mo2.contract("abcd->abcd", **vvoo)
        #
        # x8ajck
        #
        x8ajck = self.init_cache("x8ajck", nactv, nacto, nactv, nacto)
        # gajck
        mo2.contract("abcd->abcd", x8ajck, factor=-1.0, **vovo)
        # gcajk cja
        gvvoo.contract("abcd,cb->bcad", cia, x8ajck)
        if self.dump_cache:
            self.cache.dump("x8ajck")
        #
        # x4bjck
        #
        x4bjck = self.init_cache("x4bjck", nactv, nacto, nactv, nacto)
        # <bk||jc>
        gvvoo.contract("abcd->acbd", x4bjck)
        mo2.contract("abcd->adcb", x4bjck, factor=-1.0, **vovo)
        # gbcjk cjb
        gvvoo.contract("abcd,ca->acbd", cia, x4bjck)
        if self.dump_cache:
            self.cache.dump("x4bjck")
        #
        # x5bjck
        #
        x5bjck = self.init_cache("x5bjck", nactv, nacto, nactv, nacto)
        # gbkjc
        gvvoo.contract("abcd->acbd", x5bjck)
        # <bc||jk> cjb
        gvvoo.contract("abcd,ca->acbd", cia, x5bjck, factor=1.0)
        gvvoo.contract("abcd,da->adbc", cia, x5bjck, factor=-1.0)
        if self.dump_cache:
            self.cache.dump("x5bjck")
        del gvvoo

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
