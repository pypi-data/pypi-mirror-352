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
"""Equation of Motion Coupled Cluster implementations of EOM-pCCD-LCCSD

Child class of REOMCCSDBase(REOMCC) class.
"""

from __future__ import annotations

import gc
from functools import partial
from typing import Any

from pybest.linalg import (
    CholeskyFourIndex,
    CholeskyLinalgFactory,
    FourIndex,
    OneIndex,
    TwoIndex,
)
from pybest.log import log, timer

from .eom_ccsd_base import REOMCCSDBase


class REOMpCCDLCCSD(REOMCCSDBase):
    """Perform an EOM-pCCD-LCCSD calculation.
    EOM-pCCD-LCCSD implementation which calls the Base class for flavor-specific
    operations, which excludes all disconnected terms.
    """

    long_name = (
        "Equation of Motion pair Coupled Cluster Doubles with a linearized "
        "Coupled Cluster Singles and Doubles correction"
    )
    acronym = "EOM-pCCD-LCCSD"
    reference = "pCCD-LCCSD"
    singles_ref = True
    pairs_ref = True
    doubles_ref = True
    singles_ci = True
    pairs_ci = True
    doubles_ci = True

    disconnected = False

    @timer.with_section("EOMfpLCCSD: H_diag")
    def compute_h_diag(self, *args: Any) -> OneIndex:
        """Used by Davidson module for pre-conditioning. Here, the base class
        method is called and all missing terms are updated/included.

        **Arguments:**

        args:
            required for Davidson module (not used here)
        """
        #
        # Add citation
        #
        log.cite(
            "the EOM-pCCD-LCC-based methods",
            "boguslawski2019",
        )
        h_diag = self.lf.create_one_index(self.dimension, label="h_diag")
        #
        # Call base class method
        #
        h_diag_s, h_diag_d = REOMCCSDBase.compute_h_diag(self, *args)
        #
        # Get ranges
        #
        end_s = self.occ_model.nacto[0] * self.occ_model.nactv[0] + 1
        #
        # Get auxiliary matrices for pair contributions
        #
        xp_ik = self.from_cache("xp_ik")
        xp_ac = self.from_cache("xp_ac")
        xp_iakc = self.from_cache("xp_iakc")
        xp_ikl = self.from_cache("xp_ikl")
        xp_acd = self.from_cache("xp_acd")
        #
        # Intermediates
        #
        xp_ii = xp_ik.copy_diagonal()
        xp_aa = xp_ac.copy_diagonal()
        xp_ikl.contract("aaa->a", out=xp_ii, factor=0.5)
        xp_acd.contract("aaa->a", out=xp_aa, factor=0.5)
        xp_iaia = xp_iakc.contract("abab->ab")
        xp_iack = self.from_cache("xp_iack")
        xp_iaai = xp_iack.contract("abba->ab")
        #
        # Calculate pair contributions
        #
        h_diag_p = xp_iaia
        h_diag_p.iadd(xp_iaai)
        xp_ii.expand("a->ab", h_diag_p)
        xp_aa.expand("b->ab", h_diag_p)
        h_diag_p.iscale(2.0)
        #
        # Update h_diag_d with proper pair contribution
        #
        self.set_seniority_0(h_diag_d, h_diag_p)
        #
        # Assign only symmetry-unique elements
        #
        h_diag.assign(h_diag_s.ravel(), begin0=1, end0=end_s)
        h_diag.assign(h_diag_d.get_triu(), begin0=end_s)
        #
        # Release memory
        #
        h_diag_s, h_diag_d = None, None
        del h_diag_s, h_diag_d

        return h_diag

    @timer.with_section("EOMfpLCCSD: H_sub")
    def build_subspace_hamiltonian(
        self, bvector: OneIndex, hdiag: OneIndex, *args: Any
    ) -> OneIndex:
        """Used by Davidson module to construct subspace Hamiltonian.
        The base class method is called, which returns all sigma vector contributions
        and the b vector, while all symmetry-unique elements are returned.

        Args:
            bvector (OneIndex): contains current approximation to CI coefficients
            hdiag (OneIndex): Diagonal Hamiltonian elements required in Davidson
                              module (not used here)
            args (Any): Set of arguments passed by the Davidson module (not used here)
        """
        #
        # Modify T_2 to contain pair amplitudes. This will reduce the number of
        # contractions
        #
        t_p = self.checkpoint["t_p"]
        t_iajb = self.checkpoint["t_2"]
        self.set_seniority_0(t_iajb, t_p)
        #
        # Call base class method
        #
        (
            sum0,
            sigma_s,
            sigma_d,
            bv_s,
            bv_d,
        ) = REOMCCSDBase.build_subspace_hamiltonian(
            self, bvector, hdiag, *args
        )
        #
        # Get ranges
        #
        ovv = self.get_range("ovv")
        oov = self.get_range("oov")
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        end_s = nacto * nactv + 1
        #
        # Get auxiliary matrices for pair excitations
        #
        L_pqrq = self.from_cache("lpqrq")
        xp_ibl = self.from_cache("xp_ibl")
        xp_iad = self.from_cache("xp_iad")
        xp_iak = self.from_cache("xp_iak")
        xp_iac = self.from_cache("xp_iac")
        xp_ik = self.from_cache("xp_ik")
        xp_ac = self.from_cache("xp_ac")
        xp_acd = self.from_cache("xp_acd")
        xp_ikl = self.from_cache("xp_ikl")
        xp_ijkc = self.from_cache("xp_ijkc")
        #
        # Pair excitations
        #
        sigma_p = self.lf.create_two_index(nacto, nactv)
        # Terms for R=R1+R2
        #
        # R1 contributions
        # P Xp_iak rka
        xp_iak.contract("abc,cb->ab", bv_s, sigma_p)
        # P Xp_iac ric
        xp_iac.contract("abc,ac->ab", bv_s, sigma_p)
        # P Xp_akci rkc = 2 Lkaca cia rkc - 2 Lkici cia rkc
        # 2 [ Lkaca rkc ] cia
        tmp = L_pqrq.contract("abc,ac->b", bv_s, **ovv)
        t_p.contract("ab,b->ab", tmp, sigma_p, factor=2.0)
        # - 2 [ Lkici rkc ] cia
        tmp = L_pqrq.contract("abc,ac->b", bv_s, **oov)
        t_p.contract("ab,a->ab", tmp, sigma_p, factor=-2.0)
        #
        # R2 contributions
        # P Xp_ik riaka
        bv_d.contract("abcb,ac->ab", xp_ik, sigma_p, factor=2.0)
        # P Xp_ac riaic
        bv_d.contract("abac,bc->ab", xp_ac, sigma_p, factor=2.0)
        # P Xp_acd ricid
        bv_d.contract("abac,dbc->ad", xp_acd, sigma_p)
        # P Xp_ikl rkala
        bv_d.contract("abcb,dac->db", xp_ikl, sigma_p)
        # - P Lklca cia rkcla
        loovv = self.from_cache("loovv")
        tmp = loovv.contract("abcd,acbd->d", bv_d)  # a
        t_p.contract("ab,b->ab", tmp, sigma_p, factor=-2.0)
        # - P Likdc cia rkcid
        tmp = loovv.contract("abcd,bdac->a", bv_d)  # i
        if self.dump_cache:
            self.cache.dump("loovv")
        t_p.contract("ab,a->ab", tmp, sigma_p, factor=-2.0)
        # P Xp_iakc riakc
        xp_iakc = self.from_cache("xp_iakc")
        bv_d.contract("abcd,abcd->ab", xp_iakc, sigma_p, factor=2.0)
        if self.dump_cache:
            self.cache.dump("xp_iakc")
        # P Xp_iack ricka
        xp_iack = self.from_cache("xp_iack")
        bv_d.contract("abcd,adbc->ad", xp_iack, sigma_p, factor=2.0)
        if self.dump_cache:
            self.cache.dump("xp_iack")
        #
        # Clean-up
        #
        del bv_d
        #
        # Coupling to singles
        #
        # Pair contributions:
        # missing terms of P X_iabd rjd
        # terms need to be included for Cholesky ONLY
        if isinstance(self.lf, CholeskyLinalgFactory):
            self.get_effective_hamiltonian_term_iabd_t_p(bv_s, sigma_d)
        # delta_ab
        # P Xp_iad rjd -> tmp[i,a,j]
        tmp = xp_iad.contract("abc,dc->abd", bv_s)
        # missing terms of P X_ilkc rkc cja = P Xp_ijkc rkc cja -> P tmp[i,j] cja
        tmp_ij = xp_ijkc.contract("abcd,cd->ab", bv_s)  # ij
        tmp_ij.contract("ab,bc->acb", t_p, tmp)  # ij,ja->iaj
        del tmp_ij
        # expand all intermediates
        tmp.expand("abc->abcb", sigma_d, factor=1.0)
        # delta_ij
        # P Xp_ibl rla -> P tmp[i,a,b]
        tmp = xp_ibl.contract("abc,cd->adb", bv_s)
        # missing terms of P X_adkc tidjb rkc -> P [ X_adkc tkc ] tidjb
        # P [ X_abkc tkc ] tibib delta_ij
        tmp_ab = self.get_effective_hamiltonian_term_abkc_t_p(bv_s)
        # P cib [ab]
        t_p.contract("ab,cb->acb", tmp_ab, tmp)
        del tmp_ab
        # expand all intermediates
        tmp.expand("abc->abac", sigma_d, factor=1.0)
        #
        # Add permutation
        #
        sigma_d.iadd_transpose((2, 3, 0, 1))
        # Update sigma_d with correct pair contribution
        # Permutation adds a factor of 2, which is accounted for when constructing
        # the effective Hamiltonian terms. Do not change the order!
        self.set_seniority_0(sigma_d, sigma_p)
        #
        # Clean-up
        #
        del bv_s
        #
        # Assign to sigma vector
        #
        sigma = self.lf.create_one_index(self.dimension)
        sigma.set_element(0, sum0)
        sigma.assign(sigma_s.ravel(), begin0=1, end0=end_s)
        sigma.assign(sigma_d.get_triu(), begin0=end_s)
        #
        # Clean-up
        #
        del sigma_s, sigma_d
        #
        # Delete pair amplitudes again
        #
        self.set_seniority_0(t_iajb, 0.0)

        return sigma

    @timer.with_section("EOMfpLCCSD: H_eff")
    def update_hamiltonian(self, mo1: TwoIndex, mo2: FourIndex) -> None:
        """Derive all effective Hamiltonian matrices.
        Effective Hamiltonian elements are determined in REOMCCSDBase, while
        additional elements for Cholesky-decomposed ERI are determined here.

        Args:
            mo1 (TwoIndex): The 1-electron integrals in MO basis
            mo2 (FourIndex): The 2-electron integrals in MO basis; either
                             Dense or Cholesky type.
        """
        #
        # Modify T_2 to contain pair amplitudes. This will reduce the number of
        # contractions
        #
        t_p = self.checkpoint["t_p"]
        t_ia = self.checkpoint["t_1"]
        t_iajb = self.checkpoint["t_2"]
        self.set_seniority_0(t_iajb, t_p)
        #
        # Call base class method
        #
        REOMCCSDBase.update_hamiltonian(self, mo1, mo2)
        #
        # Get auxiliary matrices
        #
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        nact = self.occ_model.nact[0]
        #
        # <pq|pq> and 2<pq|pq>-<pq|pq>
        #
        gpqpq = self.init_cache("gpqpq", nact, nact)
        mo2.contract("abab->ab", gpqpq)
        #
        # <pp|qq>
        #
        gppqq = self.init_cache("gppqq", nact, nact)
        mo2.contract("aabb->ab", gppqq)
        #
        # <pq|rq> and <pq||rq>+<pq|rq>
        #
        gpqrq = self.init_cache("gpqrq", nact, nact, nact)
        mo2.contract("abcb->abc", gpqrq)
        lpqrq = self.init_cache("lpqrq", nact, nact, nact)
        lpqrq.assign(gpqrq)
        lpqrq.iscale(2.0)
        #
        # <pq|rr> (expensive, but we only do it once)
        #
        gpqrr = self.lf.create_three_index(nact)
        mo2.contract("abcc->abc", out=gpqrr, clear=True)
        # add exchange part to lpqrq using gpqrr
        # - <pq|qr> = - <pr|qq>
        tmp3 = self.lf.create_three_index(nact)
        tmp3.assign(gpqrr.array.transpose(0, 2, 1))
        lpqrq.iadd(tmp3, factor=-1.0)
        del tmp3
        #
        # Add missing terms in exisiting auxiliary matrices and generate
        # additional ones
        #
        fock = self.from_cache("fock")
        gppqq = self.from_cache("gppqq")
        gpqpq = self.from_cache("gpqpq")
        lpqrq = self.from_cache("lpqrq")
        #
        # Get ranges
        #
        vo = self.get_range("vo")
        oo2 = self.get_range("oo", offset=2)
        vv2 = self.get_range("vv", offset=2)
        ooo = self.get_range("ooo")
        oov = self.get_range("oov")
        voo = self.get_range("voo")
        vov = self.get_range("vov")
        vvo = self.get_range("vvo")
        vvv = self.get_range("vvv")
        oovv = self.get_range("oovv")
        ovvo = self.get_range("ovvo")
        ovov = self.get_range("ovov")
        #
        # Compute auxiliary matrices
        #
        # Aux matrix Xp_acd
        # P = permutation(ia,ia), which adds a factor of 2, that is, P 0.5 -> 1.0
        xp_acd = self.init_cache("xp_acd", nactv, nactv, nactv)
        # pairs: P 0.5 <aa|cd>
        gpqrr.contract("abc->cab", xp_acd, **vvv)
        # pairs: p 0.5 <cd|mm> cma
        gpqrr.contract("abc,cd->dab", t_p, xp_acd, **vvo)
        #
        # Aux matrix for Xp_iak
        # P = permutation(ia,ia), which adds a factor of 2, that is, P 0.5 -> 1.0
        xp_iak = self.init_cache("xp_iak", nacto, nactv, nacto)
        # - P G_akii
        gpqrr.contract("aki->iak", xp_iak, factor=-2.0, **voo)
        # - P F_ak cia
        fock.contract("ab,ca->cab", t_p, xp_iak, factor=-2.0, **vo)
        # - P <ak|ee> cie
        gpqrr.contract("abc,dc->dab", t_p, xp_iak, factor=-2.0, **vov)
        # L_aiki cia
        lpqrq.contract("abc,ba->bac", t_p, xp_iak, factor=2.0, **voo)
        #
        # Aux matrix for Xp_iac
        # P = permutation(ia,ia), which adds a factor of 2, that is, P 0.5 -> 1.0
        xp_iac = self.init_cache("xp_iac", nacto, nactv, nactv)
        # P G_ciaa
        gpqrr.contract("cia->iac", xp_iac, factor=2.0, **vov)
        # - P F_ci cia
        fock.contract("ab,bc->bca", t_p, xp_iac, factor=-2.0, **vo)
        # P <ci|ll> cla
        gpqrr.contract("abc,cd->bda", t_p, xp_iac, factor=2.0, **voo)
        # -P L_caia cia
        lpqrq.contract("abc,cb->cba", t_p, xp_iac, factor=-2.0, **vvo)
        #
        # Aux matrix for Xp_iakc
        #
        xp_iakc = self.init_cache("xp_iakc", nacto, nactv, nacto, nactv)
        # pairs: Licak
        mo2.contract("abcd->acdb", xp_iakc, factor=2.0, **ovvo)
        mo2.contract("abcd->abcd", xp_iakc, factor=-1.0, **ovov)
        # pairs: Lkica cia
        mo2.contract("abcd,bd->bdac", t_p, xp_iakc, factor=2.0, **oovv)
        mo2.contract("abcd,bc->bcad", t_p, xp_iakc, factor=-1.0, **oovv)
        if self.dump_cache:
            self.cache.dump("xp_iakc")
        #
        # Aux matrix for Xp_iack
        #
        xp_iack = self.init_cache("xp_iack", nacto, nactv, nactv, nacto)
        # pairs: - <ic|ak>
        mo2.contract("abcd->acbd", xp_iack, factor=-1.0, **ovvo)
        # pairs: - <ia|kc>
        mo2.contract("abcd->abdc", xp_iack, factor=-1.0, **ovov)
        # pairs: Likca cia
        loovv = self.from_cache("loovv")
        loovv.contract("abcd,ad->adcb", t_p, xp_iack)
        if self.dump_cache:
            self.cache.dump("xp_iack")
            self.cache.dump("loovv")
        #
        # Aux matrix for Xp_ikl
        # P = permutation(ia,ia), which adds a factor of 2, that is, P 0.5 -> 1.0
        xp_ikl = self.init_cache("xp_ikl", nacto, nacto, nacto)
        # pairs: P 0.5 <kl|ii>
        gpqrr.contract("abc->cab", xp_ikl, **ooo)
        # pairs: P 0.5 <kl|ee> cie
        gpqrr.contract("abc,dc->dab", t_p, xp_ikl, **oov)
        #
        # Aux matrix for Xp_ik
        #
        xp_ik = self.init_cache("xp_ik", nacto, nacto)
        # pairs: - Fik
        xp_ik.iadd(fock, -1.0, **oo2)
        # pairs: - <ik|ee> cie
        gpqrr.contract("abc,ac->ab", t_p, xp_ik, factor=-1.0, **oov)
        #
        # Aux matrix for Xp_ac
        #
        xp_ac = self.init_cache("xp_ac", nactv, nactv)
        # pairs: Fac
        xp_ac.iadd(fock, 1.0, **vv2)
        # pairs: - <ac|mm> cma
        gpqrr.contract("abc,ca->ab", t_p, xp_ac, factor=-1.0, **vvo)
        #
        # Missing T_1.T_p terms in base class
        #
        # Aux matrix for Xp_ibl = (X_ijbl[i,i,a,l])
        # delta_ij
        xp_ibl = self.init_cache("xp_ibl", nacto, nactv, nacto)
        # - [ L_lkbd tkd ] cib -> - tmp[b,l] cib
        loovv = self.from_cache("loovv")
        tmp_bl = loovv.contract("abcd,bd->ca", t_ia)
        t_p.contract("ab,bc->abc", tmp_bl, xp_ibl, factor=-1.0)
        # [ <kl|cc> cic ] tkb -> tmp[i,k,l] tkb
        tmp = gpqrr.contract("abc,dc->dab", t_p, **oov)
        tmp.contract("abc,bd->adc", t_ia, xp_ibl)
        del tmp
        #
        # Aux matrix for Xp_iad = (X_iabd[i,a,a,d])
        # (8) delta_ab
        xp_iad = self.init_cache("xp_iad", nacto, nactv, nactv)
        # - L_ilcd tld cia -> - tmp_bl[c,i] cia
        tmp_bl.contract("ab,bc->bca", t_p, xp_iad, factor=-1.0)  # ci,ia->iac
        # <cd|kk> tic cka
        tmp = gpqrr.contract("abc,da->dbc", t_ia, **vvo)  # cdkk,ic->idk
        tmp.contract("abc,cd->adb", t_p, xp_iad)  # idk,ka->iac
        del tmp, tmp_bl
        #
        # Aux matrix for Xp_ijkc = (X_ilkc[i,j,k,c])
        # (10) delta_ab
        xp_ijkc = self.init_cache("xp_ijkc", nacto, nacto, nacto, nactv)
        # - L_jkdc tid
        loovv.contract("abcd,ec->eabd", t_ia, xp_ijkc, factor=-1.0)
        #
        # Aux matrix for X_ijbl
        #
        x_ijbl = self.from_cache("x_ijbl")
        # - Ljkbc tic cjb -> tmp[i,j,b,k] cjb
        tmp = loovv.contract("abcd,ed->eacb", t_ia, factor=-1.0)  # ijbk
        if self.dump_cache:
            self.cache.dump("loovv")
        # <jk|bc> tic cjb -> tmp[i,j,b,k] cjb
        goovv = self.from_cache("goovv")
        goovv.contract("abcd,ed->eacb", t_ia, tmp)
        # tmp[i,j,b,k] cjb
        tmp.contract("abcd,bc->abcd", t_p, x_ijbl)
        # <ik|cb> tjc cib -> tmp[i,j,b,k] cib
        tmp = goovv.contract("abcd,ec->aedb", t_ia)
        tmp.contract("abcd,ac->abcd", t_p, x_ijbl)
        if self.dump_cache:
            self.cache.dump("goovv")
        tmp = None

        #
        # Update expensive effective Hamiltonian arrays, which include arrays of
        # dimension ovvv and vvvv.
        #
        if not isinstance(self.lf, CholeskyLinalgFactory):
            self.get_t_p_effective_hamiltonian_xvvv()
        #
        # Delete pair amplitudes again
        #
        self.set_seniority_0(t_iajb, 0.0)

        #
        # 4-Index slices of ERI
        #
        def alloc(arr: FourIndex, block: str) -> None | tuple[partial[Any]]:
            """Determine alloc keyword argument for init_cache method.

            Args:
                arr (FourIndex): an instance of CholeskyFourIndex or DenseFourIndex
                block (str): encoding which slices to consider using the get_range
                             method.
            """
            # We keep one whole CholeskyFourIndex to rule them all.
            # Non-redundant blocks are accessed as views.
            if isinstance(arr, CholeskyFourIndex):
                return (partial(arr.view, **self.get_range(block)),)
            return None

        #
        # Get blocks (for the systems we can treat with Dense, it does not
        # matter that we store vvvv blocks)
        # But we do not store any blocks of DenseFourIndex
        #
        if isinstance(mo2, CholeskyFourIndex):
            slices = ["ovvv", "nnvv", "vvvv", "ovnn"]
            for slice_ in slices:
                self.init_cache(f"g{slice_}", alloc=alloc(mo2, slice_))
        #
        # Delete ERI (MO) as they are not required anymore
        #
        mo2.__del__()
        gc.collect()

    #
    # Expensive effective Hamiltonian terms
    #

    def get_t_p_effective_hamiltonian_xvvv(self) -> None:
        """Generate all expensive effective Hamiltonian terms involving T_p.
        This function is called if we work in the DenseLinalgFactory picture.
        All effective Hamiltonian elements of size xvvv are calculated here,
        where x is either occupied (ov^3) or virtual (v^4).
        We either construct new elements from scratch or update existing ones.
        """
        t_p = self.checkpoint["t_p"]
        t_ia = self.checkpoint["t_1"]
        #
        # Missing T_1.T_p terms in base class
        #
        # (10) delta_ij
        xp_abkc = self.init_cache(
            "xp_abkc",
            self.occ_model.nactv[0],
            self.occ_model.nactv[0],
            self.occ_model.nacto[0],
            self.occ_model.nactv[0],
        )
        # - L_klcb tla
        loovv = self.from_cache("loovv")
        loovv.contract("abcd,be->edac", t_ia, xp_abkc, factor=-1.0)
        if self.dump_cache:
            self.cache.dump("xp_abkc")
        #
        # (8) X_iabd
        #
        x_iabd = self.from_cache("x_iabd")
        # - [ L_ikac tkb ] cia -> tmp[i,a,b,c] cia
        tmp = loovv.contract("abcd,be->aced", t_ia, factor=-1.0)
        if self.dump_cache:
            self.cache.dump("loovv")
        # <ik|ac> tkb cia -> tmp[i,a,b,c] cia
        goovv = self.from_cache("goovv")
        goovv.contract("abcd,be->aced", t_ia, tmp)  # ikac,kb->iabc
        # tmp[i,a,b,c] cia
        tmp.contract("abcd,ab->abcd", t_p, x_iabd)
        # <ki|bd> tka cib -> tmp[i,a,b,d] cib
        tmp = goovv.contract("abcd,ae->becd", t_ia)
        tmp.contract("abcd,ac->abcd", t_p, x_iabd)
        del tmp
        if self.dump_cache:
            self.cache.dump("x_iabd")
            self.cache.dump("goovv")

    def get_effective_hamiltonian_term_iabd_t_p(
        self, bv_s: TwoIndex, sigma: FourIndex
    ) -> None:
        """Compute effective Hamiltonian term involving an ovvv block.
        We have to evaluate terms contained in X_iabd.rjd

        **Arguments:**

        :bv_s: (DenseTwoIndex) the current approximation to the CI singles
               coefficient

        :sigma: (DenseFourIndex) the output sigma vector
        """
        t_ia = self.checkpoint["t_1"]
        t_p = self.checkpoint["t_p"]
        # Temporary object: <ik|ad> rjd -> tmp[i,a,j,k]
        # used also for <ik|ad> rjd tkb cia -> tmp[i,a,j,k] cia tkb
        goovv = self.from_cache("goovv")
        tmp_ovoo = goovv.contract("abcd,ed->aceb", bv_s)
        if self.dump_cache:
            self.cache.dump("goovv")
        # <ki|bd> rjd tka cib -> [ tmp[i,b,j,k] cib ] tka -> [i,b,j,k] tka
        tmp = tmp_ovoo.contract("abcd,ab->abcd", t_p)
        tmp.contract("abcd,de->aecb", t_ia, sigma)
        del tmp
        # - Likad rjd tkb cia -> tmp[i,a,j,k] cia tkb
        loovv = self.from_cache("loovv")
        loovv.contract("abcd,ed->aceb", bv_s, tmp_ovoo, factor=-1.0)
        if self.dump_cache:
            self.cache.dump("loovv")
        # <ik|ad> rjd tkb cia -> tmp[i,a,j,k] cia tkb
        # tmp[i,a,j,k] cia tkb
        # Creates a copy (inconvenient, but not that expensive)
        tmp_ovoo = tmp_ovoo.contract("abcd,ab->abcd", t_p)
        # Final addition to sigma: tmp[i,a,j,k] tkb
        tmp_ovoo.contract("abcd,de->abce", t_ia, sigma)
        # Cleanup
        del tmp_ovoo

    def get_effective_hamiltonian_term_abkc_t_p(
        self, bv_s: TwoIndex
    ) -> TwoIndex:
        """Compute effective Hamiltonian term involving an ovvv block and T_p

        **Arguments:**

        :bv_s: (DenseTwoIndex) the current approximation to the CI singles
               coefficient
        """
        out = self.lf.create_two_index(self.occ_model.nactv[0])
        to_o = {"out": out, "clear": False}
        if isinstance(self.lf, CholeskyLinalgFactory):
            t_ia = self.checkpoint["t_1"]
            loovv = self.from_cache("loovv")
            # (10) - [ L_lkac rkc ] tlb [ cia delta_ij ] -> - tmp[l,a] tlb
            tmp = loovv.contract("abcd,bd->ac", bv_s)
            if self.dump_cache:
                self.cache.dump("loovv")
            tmp.contract("ab,ac->bc", t_ia, **to_o, factor=-1.0)
            return out
        xp_abkc = self.from_cache("xp_abkc")
        xp_abkc.contract("abcd,cd->ab", bv_s, **to_o)
        if self.dump_cache:
            self.cache.dump("xp_abkc")
        return out
