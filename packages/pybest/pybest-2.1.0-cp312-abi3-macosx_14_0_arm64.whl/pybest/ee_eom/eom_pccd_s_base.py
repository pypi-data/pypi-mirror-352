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
"""Equation of Motion Coupled Cluster implementations of a common base class of
EOM-pCCD+S and EOM-pCCD-CCS, that is, pCCD with single excitations.

Child class of REOMCC class.
"""

import gc
from typing import Any

import numpy as np

from pybest.auxmat import get_fock_matrix
from pybest.ee_eom.eom_base import REOMCC
from pybest.exceptions import ArgumentError
from pybest.linalg.base import FourIndex, OneIndex, TwoIndex
from pybest.log import log
from pybest.utility import unmask


class REOMpCCDSBase(REOMCC):
    """Base class for EOM-pCCD+S and EOM-pCCD-CCS."""

    long_name = ""
    acronym = ""
    reference = "pCCD"
    singles_ref = ""
    pairs_ref = True
    doubles_ref = False
    singles_ci = True
    pairs_ci = True
    doubles_ci = False

    @property
    def dimension(self) -> int:
        """The number of unknowns (total number of excited states incl. ground
        state) for each EOM-CC flavor. Variable used by the Davidson module.
        """
        return 2 * self.occ_model.nacto[0] * self.occ_model.nactv[0] + 1

    def unmask_args(self, *args: Any, **kwargs: Any) -> Any:
        """Extract all tensors/quantities from function arguments and keyword
        arguments. Arguments/kwargs have to contain:
        * t_p: some CC T_p amplitudes
        """
        #
        # t_p
        #
        t_p = unmask("t_p", *args, **kwargs)
        if t_p is not None:
            self.checkpoint.update("t_p", t_p)
        else:
            raise ArgumentError("Cannot find Tp amplitudes.")
        #
        # Call base class method
        #
        return REOMCC.unmask_args(self, *args, **kwargs)

    def print_ci_vectors(self, index: int, ci_vector: np.ndarray) -> None:
        """Print information on CI vector (excitation and its coefficient).

        **Arguments:**

        index:
            (int) the composite index that corresponds to a specific excitation

        ci_vector:
            (np.array) the CI coefficient vector that contains all coefficients
            for one specific state
        """
        #
        # Add citations
        #
        log.cite(
            "the EOM-pCCD-based methods",
            "boguslawski2016a",
            "boguslawski2017c",
        )
        #
        # Remove reference state index
        #
        index_ = index - 1
        #
        # Either single or pair excitation
        #
        pairs = index_ - self.occ_model.nacto[0] * self.occ_model.nactv[0] >= 0
        if pairs:
            index_ -= self.occ_model.nacto[0] * self.occ_model.nactv[0]
        #
        # Get excitation
        #
        i, a = self.get_index_s(index_)
        # Account for frozen core, occupied orbitals, and numpy index convention
        i, a = (
            i + self.occ_model.ncore[0] + 1,
            a + self.occ_model.ncore[0] + self.occ_model.nacto[0] + 1,
        )
        #
        # Print contribution
        #
        if pairs:
            log(
                f"          t_iaia:  ({i:3d},{a:3d},{i:3d},{a:3d})   {ci_vector[index]: 1.5f}"
            )
        else:
            log(
                f"            t_ia:          ({i:3d},{a:3d})   {ci_vector[index]: 1.5f}"
            )

    def print_weights(self, ci_vector: np.ndarray) -> None:
        """Print weights of excitations.

        **Arguments:**

        ci_vector:
            (np.array) the CI coefficient vector that contains all coefficients
            for one specific state
        """
        nov = self.occ_model.nacto[0] * self.occ_model.nactv[0] + 1
        log(
            f"          weight(s): {np.dot(ci_vector[1:nov], ci_vector[1:nov]): 1.5f}"
        )
        log(
            f"          weight(p): {np.dot(ci_vector[nov:], ci_vector[nov:]): 1.5f}"
        )

    def build_full_hamiltonian(self) -> TwoIndex:
        """Construct full Hamiltonian matrix used in exact diagonalization"""
        t_p = self.checkpoint["t_p"]
        eom_ham = self.lf.create_two_index(self.dimension)
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        #
        # effective Hamiltonian matrix elements
        #
        fock = self.from_cache("fock")
        g_ppqq = self.from_cache("gppqq")
        l_pqrq = self.from_cache("lpqrq")
        x_ik = self.from_cache("x_ik")
        x_ac = self.from_cache("x_ac")
        x_iak = self.from_cache("x_iak")
        x_iac = self.from_cache("x_iac")
        x_ia = self.from_cache("x_ia")
        xp1_iak = self.from_cache("xp1_iak")
        xp1_iac = self.from_cache("xp1_iac")
        xp_iak = self.from_cache("xp_iak")
        xp_iac = self.from_cache("xp_iac")
        xp_ia = self.from_cache("xp_ia")
        # get slices/views thereof
        g_kc = g_ppqq.copy(end0=nacto, begin1=nacto)
        fock_kc = fock.copy(end0=nacto, begin1=nacto)
        #
        # Get ranges
        #
        ovv = self.get_range("ovv")
        oov = self.get_range("oov")
        #
        # temporary storage for H_ia,ia block of <S|S>, <S|P>, <P|P>, <P|S>
        #
        tmp = self.dense_lf.create_four_index(nacto, nactv, nacto, nactv)
        #
        # some dimensions
        #
        end_s = nacto * nactv + 1
        #
        # Single excitations:
        #
        # H_0,ia
        eom_ham.assign(2.0 * fock_kc.array, end0=1, begin1=1, end1=end_s)
        # H_ia,ic
        x_ac.expand("bc->abac", tmp)
        # H_ia,ka
        x_ik.expand("ac->abcb", tmp)
        # H_ia,kc
        x1_iakc = self.from_cache("x1_iakc")
        tmp.iadd(x1_iakc)
        if self.dump_cache:
            self.cache.dump("x1_iakc")
        # Assign to eom_ham
        eom_ham.assign(tmp.array, begin0=1, end0=end_s, begin1=1, end1=end_s)
        #
        # coupling singles-pairs <S|P>
        #
        # H_ia,iiaa
        tmp.clear()
        x_ia.expand("ab->abab", tmp)
        # H_ia,iicc
        x_iac.expand("abc->abac", tmp)
        # H_ia,kkaa
        x_iak.expand("abc->abcb", tmp)
        # Assign to eom_ham (S,P)
        eom_ham.assign(tmp.array, begin0=1, end0=end_s, begin1=end_s)
        #
        # Pair excitations:
        #
        # H_0,kkcc
        eom_ham.iadd_t(g_kc.ravel(), end0=1, begin1=end_s)
        # Diagonal elements H_iiaa,iiaa
        tmp.clear()
        xp_ia.expand("ab->abab", tmp)
        # H_iiaa,iicc
        xp_iac.expand("abc->abac", tmp)
        # H_iiaa,kkaa
        xp_iak.expand("abc->abcb", tmp)
        # Assign to eom_ham
        eom_ham.assign(tmp.array, begin0=end_s, begin1=end_s)
        #
        # coupling pairs-singles <P|S>
        #
        # H_iiaa,ic
        tmp.clear()
        xp1_iac.expand("abc->abac", tmp)
        # H_iiaa,ka
        xp1_iak.expand("abc->abcb", tmp)
        # H_iiaa,kc
        # L_kaca cia / L_kici cia
        l_pqrq.contract("abc,db->dbac", t_p, tmp, factor=2.0, **ovv)
        l_pqrq.contract("abc,bd->bdac", t_p, tmp, factor=-2.0, **oov)
        # Assign to eom_ham (P,S)
        eom_ham.assign(tmp.array, begin0=end_s, begin1=1, end1=end_s)

        return eom_ham

    def compute_h_diag(self, *args: Any) -> OneIndex:
        """Used by Davidson module for pre-conditioning

        **Arguments:**

        args:
            required for Davidson module (not used here)
        """
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        end_s = nactv * nacto + 1
        ham_diag = self.lf.create_one_index(self.dimension, label="h_diag")
        #
        # Get auxiliary matrices
        #
        x_ik = self.from_cache("x_ik")
        x_ac = self.from_cache("x_ac")
        xp_ia = self.from_cache("xp_ia")
        xp_iac = self.from_cache("xp_iac")
        xp_iak = self.from_cache("xp_iak")
        #
        # Singles
        #
        x1_iakc = self.from_cache("x1_iakc")
        tmp = x1_iakc.contract("abab->ab")
        if self.dump_cache:
            self.cache.dump("x1_iakc")
        # X_ii
        tmp_ = x_ik.copy_diagonal()
        tmp_.expand("a->ab", tmp)
        # X_aa
        tmp_ = x_ac.copy_diagonal()
        tmp_.expand("b->ab", tmp)
        #
        # assign to h_diag
        #
        ham_diag.assign(tmp.ravel(), begin0=1, end0=end_s)
        #
        # Pairs
        #
        # Xp_ia
        tmp = xp_ia.copy()
        # Xp_iaa
        xp_iac.contract("abb->ab", out=tmp, factor=1.0)
        # Xp_iai
        xp_iak.contract("aba->ab", out=tmp, factor=1.0)
        #
        # assign to h_diag
        #
        ham_diag.assign(tmp.ravel(), begin0=end_s)

        return ham_diag

    def build_subspace_hamiltonian(
        self, bvector: OneIndex, hdiag: OneIndex, *args: Any
    ) -> OneIndex:
        """
        Used by Davidson module to construct subspace Hamiltonian. Includes all
        terms that are similar for all EOM-pCCD flavours with single excitations.

        **Arguments:**

        bvector:
            (OneIndex object) contains current approximation to CI coefficients

        hdiag:
            Diagonal Hamiltonian elements required in Davidson module (not used
            here)

        args:
            Set of arguments passed by the Davidson module (not used here)
        """
        t_p = self.checkpoint["t_p"]
        #
        # Get ranges
        #
        ov2 = self.get_range("ov", offset=2)
        oov = self.get_range("oov")
        ovv = self.get_range("ovv")
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        #
        # Get auxiliary matrices
        #
        fock = self.from_cache("fock")
        g_ppqq = self.from_cache("gppqq")
        l_pqrq = self.from_cache("lpqrq")
        x_ik = self.from_cache("x_ik")
        x_ac = self.from_cache("x_ac")
        x_iak = self.from_cache("x_iak")
        x_iac = self.from_cache("x_iac")
        x_ia = self.from_cache("x_ia")
        xp1_iak = self.from_cache("xp1_iak")
        xp1_iac = self.from_cache("xp1_iac")
        xp_iak = self.from_cache("xp_iak")
        xp_iac = self.from_cache("xp_iac")
        xp_ia = self.from_cache("xp_ia")
        #
        # Calculate sigma vector (H.bvector)_kc
        #
        end_s = nactv * nacto + 1
        bv_s = self.dense_lf.create_two_index(nacto, nactv)
        bv_p = self.dense_lf.create_two_index(nacto, nactv)
        #
        # reshape bvector
        #
        bv_s.assign(bvector, begin2=1, end2=end_s)
        bv_p.assign(bvector, begin2=end_s)
        #
        # Full sigma vector and temporary storage sigma_ia
        #
        sigma = self.lf.create_one_index(self.dimension)
        sigma_ia = self.lf.create_two_index(nacto, nactv)
        #
        # Reference vector R_0
        #
        # X_0,kc r_kc
        sum_0 = bv_s.contract("ab,ab", fock, **ov2) * 2.0
        sum_0 += bv_p.contract("ab,ab", g_ppqq, **ov2)
        sigma.set_element(0, sum_0)
        #
        # Single excitations
        #
        # X1_iakc r_kc
        x1_iakc = self.from_cache("x1_iakc")
        x1_iakc.contract("abcd,cd->ab", bv_s, sigma_ia)
        if self.dump_cache:
            self.cache.dump("x1_iakc")
        # X_ik r_ka
        x_ik.contract("ab,bc->ac", bv_s, sigma_ia)
        # X_ac r_ic
        bv_s.contract("ab,cb->ac", x_ac, sigma_ia)
        #
        # Coupling singles-pairs
        #
        # X_iak r_kaka
        x_iak.contract("abc,cb->ab", bv_p, sigma_ia)
        # X_iac r_icic
        x_iac.contract("abc,ac->ab", bv_p, sigma_ia)
        # X_ia r_iaia
        sigma_ia.iadd_mult(x_ia, bv_p)
        #
        # Assign to sigma vector
        #
        sigma.assign(sigma_ia.ravel(), begin0=1, end0=end_s)
        sigma_ia.clear()
        #
        # Pair excitations
        #
        # Xp_iak r_kaka
        xp_iak.contract("abc,cb->ab", bv_p, sigma_ia)
        # Xp_iac r_icic
        xp_iac.contract("abc,ac->ab", bv_p, sigma_ia)
        # Xp_ia r_iaia
        sigma_ia.iadd_mult(xp_ia, bv_p)
        #
        # Coupling pairs-singles
        #
        # Xp1_iak r_ka
        xp1_iak.contract("abc,cb->ab", bv_s, sigma_ia)
        # Xp1_iac r_ic
        xp1_iac.contract("abc,ac->ab", bv_s, sigma_ia)
        # Xp1_iakc r_kc = [ 2 L_akac cia - 2 L_ikic cia ] r_kc
        # 2 L_kaca r_kc
        tmp = l_pqrq.contract("abc,ac->b", bv_s, **ovv)
        t_p.contract("ab,b->ab", tmp, sigma_ia, factor=2.0)
        # - 2 L_kici r_kc
        tmp = l_pqrq.contract("abc,ac->b", bv_s, **oov)
        t_p.contract("ab,a->ab", tmp, sigma_ia, factor=-2.0)
        #
        # Assign to sigma vector
        #
        sigma.assign(sigma_ia.ravel(), begin0=end_s)

        return sigma

    def update_hamiltonian(self, mo1: TwoIndex, mo2: FourIndex) -> None:
        """Derive all auxiliary matrices.

        **Arguments:**

        mo1, mo2
             one- and two-electron integrals to be sorted.

        """
        t_p = self.checkpoint["t_p"]
        #
        # Get ranges
        #
        oo = self.get_range("oo")
        ov = self.get_range("ov")
        vo = self.get_range("vo")
        vv = self.get_range("vv")
        ov2 = self.get_range("ov", offset=2)
        oo2 = self.get_range("oo", offset=2)
        vv2 = self.get_range("vv", offset=2)
        vo2 = self.get_range("vo", offset=2)
        voo = self.get_range("voo")
        vov = self.get_range("vov")
        vvo = self.get_range("vvo")
        oov = self.get_range("oov")
        ovo = self.get_range("ovo")
        ovv = self.get_range("ovv")
        oovv = self.get_range("oovv")
        ovvo = self.get_range("ovvo")
        ovov = self.get_range("ovov")
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        nact = self.occ_model.nact[0]
        #
        # <pq||rq>+<pq|rq>
        #
        lpqrq = self.init_cache("lpqrq", nact, nact, nact)
        mo2.contract("abcb->abc", out=lpqrq, factor=2.0, clear=True)
        #
        # <pq|rr>
        #
        gpqrr = self.lf.create_three_index(nact)
        mo2.contract("abcc->abc", out=gpqrr, clear=True)
        #
        # add exchange part to lpqrq
        #
        lpqrq.iadd_transpose((0, 2, 1), other=gpqrr, factor=-1.0)
        #
        # Inactive Fock matrix
        #
        fock = self.init_cache("fock", nact, nact)
        get_fock_matrix(fock, mo1, mo2, nacto)
        #
        # <pp|qq>
        #
        gppqq = self.init_cache("gppqq", nact, nact)
        mo2.contract("aabb->ab", out=gppqq, clear=True)
        #
        # (1) X_ik
        #
        x_ik = self.init_cache("x_ik", nacto, nacto)
        # - F_ki
        x_ik.iadd(fock, -1.0, **oo2)
        # - <ik|ee> cie
        gpqrr.contract("abc,ac->ab", t_p, x_ik, factor=-1.0, **oov)
        #
        # (2) X_ac
        #
        x_ac = self.init_cache("x_ac", nactv, nactv)
        # F_ac
        x_ac.iadd(fock, 1.0, **vv2)
        # - <ac|mm> cma
        gpqrr.contract("abc,ca->ab", t_p, x_ac, factor=-1.0, **vvo)
        #
        # (3) X_iakc
        #
        x1_iakc = self.init_cache("x1_iakc", nacto, nactv, nacto, nactv)
        # L_icak
        mo2.contract("abcd->acdb", x1_iakc, factor=2.0, **ovvo)
        mo2.contract("abcd->adcb", x1_iakc, factor=-1.0, **ovov)
        # L_ikac cia
        mo2.contract("abcd,ac->acbd", t_p, x1_iakc, factor=2.0, **oovv)
        mo2.contract("abcd,ad->adbc", t_p, x1_iakc, factor=-1.0, **oovv)
        if self.dump_cache:
            self.cache.dump("x1_iakc")
        #
        # X_iak
        #
        x_iak = self.init_cache("x_iak", nacto, nactv, nacto)
        # L_iakk = <ia|kk>
        gpqrr.contract("abc->abc", out=x_iak, factor=-1.0, **ovo)
        #
        # X_iac
        #
        x_iac = self.init_cache("x_iac", nacto, nactv, nactv)
        # L_iacc = <ia|cc>
        gpqrr.contract("abc->abc", out=x_iac, **ovv)
        #
        # X_ia
        #
        x_ia = self.init_cache("x_ia", nacto, nactv)
        # F_ia
        x_ia.iadd(fock, 1.0, **ov2)
        #
        # Xp1_iak
        #
        xp1_iak = self.init_cache("xp1_iak", nacto, nactv, nacto)
        # - <ak|ii>
        gpqrr.contract("abc->cab", xp1_iak, factor=-2.0, **voo)
        # - 2 F_ak cia
        fock.contract("ab,ca->cab", t_p, xp1_iak, factor=-2.0, **vo)
        # - 2 <ak|ee> cie
        gpqrr.contract("abc,dc->dab", t_p, xp1_iak, factor=-2.0, **vov)
        # 2 L_aiki cia
        lpqrq.contract("abc,ba->bac", t_p, xp1_iak, factor=2.0, **voo)
        #
        # Xp1_iac
        #
        xp1_iac = self.init_cache("xp1_iac", nacto, nactv, nactv)
        # 2 <ic|aa>
        gpqrr.contract("abc->acb", xp1_iac, factor=2.0, **ovv)
        # - 2 F_ic cia
        fock.contract("ab,ac->acb", t_p, xp1_iac, factor=-2.0, **ov)
        # 2 <ic|ll> cla
        gpqrr.contract("abc,cd->adb", t_p, xp1_iac, factor=2.0, **ovo)
        # - 2 L_iaca cia
        lpqrq.contract("abc,ab->abc", t_p, xp1_iac, factor=-2.0, **ovv)
        #
        # Xp_iak
        #
        xp_iak = self.init_cache("xp_iak", nacto, nactv, nacto)
        # <ii|kk>
        gppqq.expand("ac->abc", xp_iak, **oo)
        # - 2 <aa|kk> cia
        t_p.contract("ab,bc->abc", gppqq, xp_iak, factor=-2.0, **vo2)
        # <ee|kk> cie
        tmp = t_p.contract("ab,bc->ac", gppqq, **vo2)
        tmp.expand("ac->abc", xp_iak)
        #
        # Xp_iac
        #
        xp_iac = self.init_cache("xp_iac", nacto, nactv, nactv)
        # <aa|cc>
        gppqq.expand("bc->abc", xp_iac, **vv)
        # - 2 <ii|cc> cia
        t_p.contract("ab,ac->abc", gppqq, xp_iac, factor=-2.0, **ov2)
        # <kk|cc> cka
        tmp = t_p.contract("ab,ac->bc", gppqq, **ov2)
        tmp.expand("bc->abc", xp_iac)
        #
        # Xp_ia
        #
        xp_ia = self.init_cache("xp_ia", nacto, nactv)
        # 2 F_aa - 2 F_ii
        fockdiag = fock.copy_diagonal()
        fockdiag.expand("a->ab", xp_ia, factor=-2.0, end0=nacto)
        fockdiag.expand("b->ab", xp_ia, factor=2.0, begin0=nacto)
        # - 2 L_iaia
        lpqrq.contract("aba->ab", xp_ia, factor=-2.0, **ovo)
        # 4 <ii|aa> cia
        xp_ia.iadd_mult(gppqq, t_p, 4.0, **ov)
        # - 2 <ii|cc> cic
        tmp = gppqq.contract("ab,ab->a", t_p, **ov)
        tmp.expand("a->ab", xp_ia, factor=-2.0)
        # - 2 <kk|aa> cka
        tmp = gppqq.contract("ab,ab->b", t_p, **ov)
        tmp.expand("b->ab", xp_ia, factor=-2.0)

        gc.collect()
