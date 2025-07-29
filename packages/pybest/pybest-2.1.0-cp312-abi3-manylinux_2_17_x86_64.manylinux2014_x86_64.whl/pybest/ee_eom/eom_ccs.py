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
"""Equation of Motion Coupled Cluster implementations of EOM-CCS

Child class of REOMCC class.
"""

import gc
from typing import Any

import numpy as np

from pybest.auxmat import get_fock_matrix
from pybest.linalg import FourIndex, OneIndex, TwoIndex
from pybest.log import log, timer
from pybest.utility import unmask

from .eom_base import REOMCC


class REOMCCS(REOMCC):
    """Performs an EOM-CCS calculation, which is equivalent to CIS."""

    long_name = "Equation of Motion Coupled Cluster Singles"
    acronym = "EOM-CCS"
    reference = "CCS"
    singles_ref = True
    pairs_ref = False
    doubles_ref = False
    singles_ci = True
    pairs_ci = False
    doubles_ci = False

    @property
    def dimension(self):
        """The number of unknowns (total number of excited states incl. ground
        state) for each EOM-CC flavor. Variable used by the Davidson module.
        """
        return self.occ_model.nacto[0] * self.occ_model.nactv[0] + 1

    def unmask_args(self, *args: Any, **kwargs: Any) -> Any:
        """Extract all tensors/quantities from function arguments and keyword
        arguments. Arguments/kwargs have to contain:
        * t_1: some CC T_1 amplitudes
        """
        #
        # t_1
        #
        t_1 = unmask("t_1", *args, **kwargs)
        if t_1 is not None:
            self.checkpoint.update("t_1", t_1)
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
        # get excitation (remove reference state from composite index)
        #
        i, a = self.get_index_s(index - 1)
        #
        # Print contribution
        #
        log(
            f"            t_ia:          ({i + 1:3},"
            f"{a + 1 + self.occ_model.nacto[0]:3})   {ci_vector[index]: 1.5f}"
        )

    def print_weights(self, ci_vector: np.ndarray) -> None:
        """Print weights of excitations.

        **Arguments:**

        ci_vector:
            (np.array) the CI coefficient vector that contains all coefficients
            for one specific state
        """
        log(
            f"          weight(s): {np.dot(ci_vector[1:], ci_vector[1:]): 1.5f}"
        )

    @timer.with_section("EOMCCS: H_full")
    def build_full_hamiltonian(self) -> TwoIndex:
        """Construct full Hamiltonian matrix used in exact diagonalization"""
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        eom_ham = self.lf.create_two_index(
            nacto * nactv + 1, nacto * nactv + 1
        )
        #
        # Get auxiliary matrices
        #
        fock = self.from_cache("fock")
        x_ik = self.from_cache("x_ik")
        x_ac = self.from_cache("x_ac")
        # get slices/views thereof
        fock_kc = fock.copy(end0=nacto, begin1=nacto)
        # temporary storage for H_ia,ia block
        tmp = self.dense_lf.create_four_index(nacto, nactv, nacto, nactv)
        #
        # Assign matrix elements of H
        #
        # H_0,ia
        eom_ham.assign(2.0 * fock_kc.array, end0=1, begin1=1)
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
        eom_ham.assign(tmp.array, begin0=1, begin1=1)

        return eom_ham

    @timer.with_section("EOMCCS: H_diag")
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
        x_ik = self.from_cache("x_ik")
        x_ac = self.from_cache("x_ac")
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        #
        # H_diag_ia,ia
        #
        diag_s = self.lf.create_two_index(nacto, nactv)
        #
        # Singles
        #
        # X1_iakc[i,a,i,a]
        #
        x1_iakc = self.from_cache("x1_iakc")
        x1_iakc.contract("abab->ab", out=diag_s, clear=True)
        if self.dump_cache:
            self.cache.dump("x1_iakc")
        #
        # X_ik[i,i]
        #
        tmp = x_ik.copy_diagonal()
        tmp.expand("a->ab", diag_s)
        #
        # X_ac[a,a]
        #
        tmp = x_ac.copy_diagonal()
        tmp.expand("b->ab", diag_s)

        eom_ham_diag.assign(diag_s.ravel(), begin0=1)
        return eom_ham_diag

    @timer.with_section("EOMCCS: H_sub")
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
        fock = self.from_cache("fock")
        x_0 = self.from_cache("x_0")
        x_ik = self.from_cache("x_ik")
        x_ac = self.from_cache("x_ac")
        #
        # Get ranges
        #
        ov2 = self.get_range("ov", offset=2)
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        #
        # Calculate sigma vector (H.bvector)_ia
        #
        sigma_s = self.lf.create_two_index(nacto, nactv)
        bv_s = self.dense_lf.create_two_index(nacto, nactv)
        #
        # reshape bvector
        #
        bv_s.assign(bvector, begin2=1)
        #
        # Reference vector R_0
        #
        # X0,kc rkc
        sum_0 = bv_s.contract("ab,ab", fock, **ov2, factor=2.0)
        sum_0 += bv_s.contract("ab,ab", x_0) * 2.0
        #
        # Single excitations
        #
        # X1_iakc r_kc
        x1_iakc = self.from_cache("x1_iakc")
        x1_iakc.contract("abcd,cd->ab", bv_s, sigma_s)
        if self.dump_cache:
            self.cache.dump("x1_iakc")
        # X_ik r_ka
        x_ik.contract("ab,bc->ac", bv_s, sigma_s)
        # X_ac r_ic
        bv_s.contract("ab,cb->ac", x_ac, sigma_s)
        #
        # output vector
        #
        sigma = self.lf.create_one_index(self.dimension)
        sigma.set_element(0, sum_0)
        sigma.assign(sigma_s.ravel(), begin0=1)

        return sigma

    @timer.with_section("EOMCCS: H_eff")
    def update_hamiltonian(self, mo1: TwoIndex, mo2: FourIndex) -> None:
        """Derive all auxiliary matrices.

        **Arguments:**

        mo1, mo2
             one- and two-electron integrals to be sorted.
        """
        t_ia = self.checkpoint["t_1"]
        #
        # Get ranges
        #
        ov2 = self.get_range("ov", offset=2)
        oo2 = self.get_range("oo", offset=2)
        vv2 = self.get_range("vv", offset=2)
        ooov = self.get_range("ooov")
        oovv = self.get_range("oovv")
        ovov = self.get_range("ovov")
        ovvo = self.get_range("ovvo")
        oovo = self.get_range("oovo")
        ovvv = self.get_range("ovvv")
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        nact = self.occ_model.nact[0]
        #
        # Inactive Fock matrix
        #
        fock = self.init_cache("fock", nact, nact)
        get_fock_matrix(fock, mo1, mo2, nacto)
        #
        # X_0
        #
        # L_klcd t_ld
        x_0 = self.init_cache("x_0", nacto, nactv)
        mo2.contract("abcd,bd->ac", t_ia, x_0, factor=2.0, **oovv)
        mo2.contract("abcd,bc->ad", t_ia, x_0, factor=-1.0, **oovv)
        #
        # X_ik
        #
        x_ik = self.init_cache("x_ik", nacto, nacto)
        # - F_ik
        x_ik.iadd(fock, -1.0, **oo2)
        # - tic fkc
        t_ia.contract("ab,cb->ac", fock, x_ik, factor=-1.0, **ov2)
        # - 2 L_klid t_ld
        mo2.contract("abcd,bd->ca", t_ia, x_ik, factor=-2.0, **ooov)
        mo2.contract("abcd,bc->da", t_ia, x_ik, **oovo)
        # - L_klcd t_ld t_ic --> [ - L_klcd t_ld ]_kc t_ic --> X_0_kc t_ic
        t_ia.contract("ab,cb->ac", x_0, x_ik)
        #
        # X_ac
        #
        x_ac = self.init_cache("x_ac", nactv, nactv)
        # F_ac
        x_ac.iadd(fock, 1.0, **vv2)
        # - t_ka fkc
        t_ia.contract("ab,ac->bc", fock, x_ac, factor=-1.0, **ov2)
        # L_kadc t_kd
        mo2.contract("abcd,ac->bd", t_ia, x_ac, factor=2.0, **ovvv)
        mo2.contract("abcd,ad->bc", t_ia, x_ac, factor=-1.0, **ovvv)
        # - L_klcd t_ld t_ka --> [ - L_klcd t_ld ]_kc t_ka
        t_ia.contract("ab,ac->bc", x_0, x_ac)
        #
        # X1_iakc
        #
        x1_iakc = self.init_cache("x1_iakc", nacto, nactv, nacto, nactv)
        # L_icak
        mo2.contract("abcd->acdb", x1_iakc, factor=2.0, **ovvo)
        mo2.contract("abcd->abcd", x1_iakc, factor=-1.0, **ovov)
        # - L_lkic t_la
        mo2.contract("abcd,ae->cebd", t_ia, x1_iakc, factor=-2.0, **ooov)
        mo2.contract("abcd,ae->debc", t_ia, x1_iakc, **oovo)
        # L_kacd t_id
        mo2.contract("abcd,ed->ebac", t_ia, x1_iakc, factor=2.0, **ovvv)
        mo2.contract("abcd,ec->ebad", t_ia, x1_iakc, factor=-1.0, **ovvv)
        # - L_klcd t_la t_id --> [ - L_klcd t_id ]_ikcl t_la
        tmp = mo2.contract("abcd,ed->eacb", t_ia, factor=-2.0, **oovv)
        mo2.contract("abcd,ec->eadb", t_ia, tmp, **oovv)
        tmp.contract("abcd,de->aebc", t_ia, x1_iakc)
        if self.dump_cache:
            self.cache.dump("x1_iakc")

        gc.collect()
        #
        # Delete mo2 as they are not required anymore
        #
        mo2.__del__()
