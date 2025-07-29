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
"""Equation of Motion Coupled Cluster implementation for a pCCD reference
function.

Variables used in this module:
 :ncore:     number of frozen core orbitals
 :nocc:      number of occupied orbitals in the principle configuration
 :nacto:     number of active occupied orbitals in the principle configuration
 :nvirt:     number of virtual orbitals in the principle configuration
 :nactv:     number of active virtual orbitals in the principle configuration
 :nbasis:    total number of basis functions
 :nact:      total number of active orbitals (nacto+nactv)

 Indexing convention:
  :i,j,k,..: occupied orbitals of principle configuration
  :a,b,c,..: virtual orbitals of principle configuration
  :p,q,r,..: general indices (occupied, virtual)

 P^bc_jk performs a pair permutation, i.e., P^bc_jk o_(bcjk) = o_(cbkj)

 Abbreviations used (if not mentioned in doc-strings):
  :L_pqrs: 2<pq|rs>-<pq|sr>
  :g_pqrs: <pq|rs>

Child class of REOMCC class.
"""

from typing import Any

import numpy as np

from pybest.auxmat import get_diag_fock_matrix
from pybest.exceptions import ArgumentError
from pybest.linalg import FourIndex, OneIndex, TwoIndex
from pybest.log import log, timer
from pybest.utility import unmask

from .eom_base import REOMCC


class REOMpCCD(REOMCC):
    """Performs an EOM-pCCD calculation."""

    long_name = "Equation of Motion pair Coupled Cluster Doubles"
    acronym = "EOM-pCCD"
    reference = "pCCD"
    singles_ref = False
    pairs_ref = True
    doubles_ref = False
    singles_ci = False
    pairs_ci = True
    doubles_ci = False

    @property
    def dimension(self) -> int:
        """The number of unknowns (total number of excited states incl. ground
        state) for each EOM-CC flavor. Variable used by the Davidson module.
        """
        return self.occ_model.nacto[0] * self.occ_model.nactv[0] + 1

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
        #
        # Remove reference state index
        #
        index_ = index - 1
        #
        # Print contribution of pair excitation
        #
        i, a = self.get_index_s(index_)
        # Account for frozen core, occupied orbitals, and numpy index convention
        i, a = (
            i + self.occ_model.ncore[0] + 1,
            a + self.occ_model.ncore[0] + self.occ_model.nacto[0] + 1,
        )
        log(
            f"          t_iaia:  ({i:3d},{a:3d},{i:3d},{a:3d})   {ci_vector[index]: 1.5f}"
        )

    def print_weights(self, ci_vector: np.ndarray) -> None:
        """Print weights of excitations.

        **Arguments:**

        ci_vector:
            (np.array) the CI coefficient vector that contains all coefficients
            for one specific state
        """
        log(
            f"          weight(p): {np.dot(ci_vector[1:], ci_vector[1:]): 1.5f}"
        )

    @timer.with_section("EOMpCCD: H_full")
    def build_full_hamiltonian(self) -> TwoIndex:
        """Construct full Hamiltonian matrix used in exact diagonalization"""
        eom_ham = self.lf.create_two_index(self.dimension)
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        #
        # Get auxiliary matrices
        #
        g_ppqq = self.from_cache("gppqq")
        xp_iak = self.from_cache("xp_iak")
        xp_iac = self.from_cache("xp_iac")
        xp_ia = self.from_cache("xp_ia")
        g_kc = g_ppqq.copy(end0=nacto, begin1=nacto)
        # Temporary storage
        temp_h = self.dense_lf.create_four_index(nacto, nactv, nacto, nactv)
        #
        # Assign matrix elements
        #
        # H_0,iiaa
        eom_ham.iadd_t(g_kc.ravel(), end0=1, begin1=1)
        # Diagonal elements H_iiaa,iiaa
        xp_ia.expand("ab->abab", temp_h)
        # H_iiaa,iicc
        xp_iac.expand("abc->abac", temp_h)
        # H_iiaa,kkaa
        xp_iak.expand("abc->abcb", temp_h)

        eom_ham.assign(temp_h.array, begin0=1, begin1=1)

        return eom_ham

    @timer.with_section("EOMpCCD: H_diag")
    def compute_h_diag(self, *args: Any) -> OneIndex:
        """Used by Davidson module for pre-conditioning

        **Arguments:**

        args:
            required for Davidson module (not used here)
        """
        eom_ham_diag = self.lf.create_one_index(self.dimension, label="h_diag")
        #
        # Get auxiliary matrices
        #
        xp_ia = self.from_cache("xp_ia")
        xp_iac = self.from_cache("xp_iac")
        xp_iak = self.from_cache("xp_iak")
        #
        # Assign matrix elements
        #
        # Xp_ia
        diag_p = xp_ia.copy()
        # Xp_iaa
        xp_iac.contract("abb->ab", out=diag_p, factor=1.0)
        # Xp_iai
        xp_iak.contract("aba->ab", out=diag_p, factor=1.0)
        eom_ham_diag.assign(diag_p.ravel(), begin0=1)

        return eom_ham_diag

    @timer.with_section("EOMpCCD: H_sub")
    def build_subspace_hamiltonian(
        self, bvector: OneIndex, hdiag: OneIndex, *args: Any
    ) -> OneIndex:
        """
        Used by Davidson module to construct subspace Hamiltonian

        **Arguments:**

        bvector:
            (OneIndex object) contains current approximation to CI coefficients

        hdiag:
            Diagonal Hamiltonian elements required in Davidson module (not used
            here)

        args:
            Set of arguments passed by the Davidson module (not used here)
        """
        #
        # Get auxiliary matrices
        #
        g_ppqq = self.from_cache("gppqq")
        xp_iak = self.from_cache("xp_iak")
        xp_iac = self.from_cache("xp_iac")
        xp_ia = self.from_cache("xp_ia")
        #
        # Get ranges
        #
        ov2 = self.get_range("ov", offset=2)
        #
        # Calculate sigma vector (H.bvector)_kc
        #
        sigma_p = self.lf.create_two_index(
            self.occ_model.nacto[0], self.occ_model.nactv[0]
        )
        bv_p = self.lf.create_two_index(
            self.occ_model.nacto[0], self.occ_model.nactv[0]
        )
        sigma = self.lf.create_one_index(
            self.occ_model.nacto[0] * self.occ_model.nactv[0] + 1
        )
        bv_p.assign(bvector, begin2=1)
        #
        # Reference state
        #
        sum_0 = bv_p.contract("ab,ab", g_ppqq, **ov2)
        sigma.set_element(0, sum_0)
        #
        # Pair excitations
        #
        # Xp_iak r_kaka
        xp_iak.contract("abc,cb->ab", bv_p, sigma_p)
        # Xp_iac r_icic
        xp_iac.contract("abc,ac->ab", bv_p, sigma_p)
        # Xp_ia r_iaia
        sigma_p.iadd_mult(xp_ia, bv_p)
        #
        # Assign new sigma vector
        #
        sigma.assign(sigma_p.ravel(), begin0=1)
        return sigma

    @timer.with_section("EOMpCCD: H_eff")
    def update_hamiltonian(self, mo1: TwoIndex, mo2: FourIndex) -> None:
        """Derive all auxiliary matrices.
        fock_pq:     one_pq + sum_m(2<pm|qm> - <pm|mq>),
        lpqpq:   2<pq|pq>-<pq|qp>,
        gpqpq:   <pq|pq>,

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
        vv = self.get_range("vv")
        ov2 = self.get_range("ov", offset=2)
        vo2 = self.get_range("vo", offset=2)
        ovo = self.get_range("ovo")
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
        fock = self.lf.create_one_index(nact)
        get_diag_fock_matrix(fock, mo1, mo2, nacto)
        #
        # <pp|qq>
        #
        gppqq = self.init_cache("gppqq", nact, nact)
        mo2.contract("aabb->ab", out=gppqq, clear=True)
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
        fock.expand("a->ab", xp_ia, factor=-2.0, end0=nacto)
        fock.expand("b->ab", xp_ia, factor=2.0, begin0=nacto)
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
        #
        # Remove ERI (MO) to save memory as they are not required anymore
        #
        mo2.__del__()
