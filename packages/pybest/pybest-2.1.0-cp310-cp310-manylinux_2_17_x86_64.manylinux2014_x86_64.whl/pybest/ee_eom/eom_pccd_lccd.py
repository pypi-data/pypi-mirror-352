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
"""Equation of Motion Coupled Cluster implementations of EOM-pCCD-LCCD

Child class of REOMCCDBase(REOMCC) class.
"""

from __future__ import annotations

import gc
from functools import partial
from typing import Any

from pybest.linalg import CholeskyFourIndex
from pybest.linalg.base import FourIndex, OneIndex, TwoIndex
from pybest.log import log, timer

from .eom_ccd_base import REOMCCDBase


class REOMpCCDLCCD(REOMCCDBase):
    """Perform an EOM-pCCD-LCCD calculation.
    EOM-pCCD-LCCD implementation which calls the Base class for flavor-specific
    operations, which excludes all disconnected terms.
    """

    long_name = (
        "Equation of Motion pair Coupled Cluster Doubles with a linearized "
        "Coupled Cluster Doubles correction"
    )
    acronym = "EOM-pCCD-LCCD"
    reference = "pCCD-LCCD"
    singles_ref = False
    pairs_ref = True
    doubles_ref = True
    singles_ci = False
    pairs_ci = True
    doubles_ci = True

    disconnected = False

    @timer.with_section("EOMfpLCCD: H_diag")
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
        h_diag_d = REOMCCDBase.compute_h_diag(self, *args)
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
        h_diag.assign(h_diag_d.get_triu(), begin0=1)
        #
        # Release memory
        #
        h_diag_d = None
        del h_diag_d

        return h_diag

    @timer.with_section("EOMfpLCCD: H_sub")
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
        (sum0, sigma_d, bv_d) = REOMCCDBase.build_subspace_hamiltonian(
            self, bvector, hdiag, *args
        )
        #
        # Get ranges
        #
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        #
        # Get auxiliary matrices for pair excitations
        #
        xp_ik = self.from_cache("xp_ik")
        xp_ac = self.from_cache("xp_ac")
        xp_acd = self.from_cache("xp_acd")
        xp_ikl = self.from_cache("xp_ikl")
        #
        # Pair excitations
        #
        sigma_p = self.lf.create_two_index(nacto, nactv)
        # Terms for R=R2
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
        # Add permutation
        #
        sigma_d.iadd_transpose((2, 3, 0, 1))
        # Update sigma_d with correct pair contribution
        # Permutation adds a factor of 2, which is accounted for when constructing
        # the effective Hamiltonian terms. Do not change the order!
        self.set_seniority_0(sigma_d, sigma_p)
        #
        # Assign to sigma vector
        #
        sigma = self.lf.create_one_index(self.dimension)
        sigma.set_element(0, sum0)
        sigma.assign(sigma_d.get_triu(), begin0=1)
        #
        # Clean-up
        #
        del sigma_d
        #
        # Delete pair amplitudes again
        #
        self.set_seniority_0(t_iajb, 0.0)

        return sigma

    @timer.with_section("EOMfpLCCD: H_eff")
    def update_hamiltonian(self, mo1: TwoIndex, mo2: FourIndex) -> None:
        """Derive all effective Hamiltonian matrices.
        Effective Hamiltonian elements are determined in REOMCCDBase, while
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
        t_iajb = self.checkpoint["t_2"]
        self.set_seniority_0(t_iajb, t_p)
        #
        # Call base class method
        #
        REOMCCDBase.update_hamiltonian(self, mo1, mo2)
        #
        # Get auxiliary matrices
        #
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        nact = self.occ_model.nact[0]
        fock = self.from_cache("fock")
        #
        # <pq|rq> and <pq||rq>+<pq|rq>
        #
        lpqrq = self.lf.create_three_index(nact)
        mo2.contract("abcb->abc", lpqrq, factor=2.0)
        #
        # <pq|rr> (expensive, but we only do it once)
        #
        gpqrr = self.lf.create_three_index(nact)
        mo2.contract("abcc->abc", out=gpqrr)
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
            slices = ["nnvv", "vvvv"]
            for slice_ in slices:
                self.init_cache(f"g{slice_}", alloc=alloc(mo2, slice_))
        #
        # Delete ERI (MO) as they are not required anymore
        #
        mo2.__del__()
        gc.collect()
