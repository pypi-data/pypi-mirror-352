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
"""Equation of Motion Coupled Cluster implementations of EOM-pCCD-CCS,
that is, pCCD-CCS with single excitations.

Child class of REOMpCCDSBase(REOMCC) class.
"""

from typing import Any

from pybest.exceptions import ArgumentError
from pybest.linalg import FourIndex, OneIndex, TwoIndex
from pybest.log import timer
from pybest.utility import unmask

from .eom_pccd_s_base import REOMpCCDSBase


class REOMpCCDCCS(REOMpCCDSBase):
    """Perform an EOM-pCCD-CCS calculation."""

    long_name = "Equation of Motion pair Coupled Cluster Doubles Singles"
    acronym = "EOM-pCCD-CCS"
    reference = "pCCD-CCS"
    singles_ref = True
    pairs_ref = True
    doubles_ref = False
    singles_ci = True
    pairs_ci = True
    doubles_ci = False

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
        elif self.singles_ref:
            raise ArgumentError("Cannot find T1 amplitudes")
        #
        # Call base class method
        #
        return REOMpCCDSBase.unmask_args(self, *args, **kwargs)

    @timer.with_section("EOMpCCDCCS: H_full")
    def build_full_hamiltonian(self) -> TwoIndex:
        """Construct full Hamiltonian matrix used in exact diagonalization"""
        #
        # Call base class method
        #
        return REOMpCCDSBase.build_full_hamiltonian(self)

    @timer.with_section("EOMpCCDCCS: H_diag")
    def compute_h_diag(self, *args: Any) -> OneIndex:
        """Used by Davidson module for pre-conditioning. Here only used to
        define proper timer sections.

        **Arguments:**

        args:
            required for Davidson module (not used here)
        """
        #
        # Call base class method
        #
        return REOMpCCDSBase.compute_h_diag(self, *args)

    @timer.with_section("EOMpCCDCCS: H_sub")
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
        #
        # Full sigma vector from base method
        #
        sigma = REOMpCCDSBase.build_subspace_hamiltonian(
            self, bvector, hdiag, *args
        )
        #
        # Calculate missing terms
        #
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        end_s = nactv * nacto + 1
        #
        # reshape bvector
        #
        bv_s = self.dense_lf.create_two_index(nacto, nactv)
        bv_s.assign(bvector, begin2=1, end2=end_s)
        #
        # Reference vector R_0
        #
        # 2 L_klcd t_ld r_kc
        # X_0,kc r_kc
        x_0 = self.from_cache("x_0")
        sum_0 = bv_s.contract("ab,ab", x_0, factor=2.0)
        sigma.iadd(sum_0, end0=1)
        return sigma

    @timer.with_section("EOMpCCDCCS: H_eff")
    def update_hamiltonian(self, mo1: TwoIndex, mo2: FourIndex) -> None:
        """Derive all auxiliary matrices.

        **Arguments:**

        mo1, mo2
             one- and two-electron integrals to be sorted.

        """
        #
        # Call base class method first
        #
        REOMpCCDSBase.update_hamiltonian(self, mo1, mo2)
        #
        # Modify auxiliary matrices from base class
        #
        t_ia = self.checkpoint["t_1"]
        #
        # Get auxiliary matrices including those that need to be updated
        #
        fock = self.from_cache("fock")
        x_ik = self.from_cache("x_ik")
        x_ac = self.from_cache("x_ac")
        x1_iakc = self.from_cache("x1_iakc")
        x_iak = self.from_cache("x_iak")
        x_iac = self.from_cache("x_iac")
        x_ia = self.from_cache("x_ia")
        #
        # Get ranges
        #
        ov2 = self.get_range("ov", offset=2)
        ooov = self.get_range("ooov")
        oovo = self.get_range("oovo")
        oovv = self.get_range("oovv")
        oov = self.get_range("oov")
        vvo = self.get_range("vvo")
        ovvv = self.get_range("ovvv")
        #
        # X_0
        #
        # L_klcd t_ld
        x_0 = self.init_cache(
            "x_0", self.occ_model.nacto[0], self.occ_model.nactv[0]
        )
        mo2.contract("abcd,bd->ac", t_ia, x_0, factor=2.0, **oovv)
        mo2.contract("abcd,bc->ad", t_ia, x_0, factor=-1.0, **oovv)
        #
        # X_ik
        #
        # - tic fkc
        t_ia.contract("ab,cb->ac", fock, x_ik, factor=-1.0, **ov2)
        # - L_klid t_ld
        mo2.contract("abcd,bd->ca", t_ia, x_ik, factor=-2.0, **ooov)
        mo2.contract("abcd,bc->da", t_ia, x_ik, **oovo)
        # - L_klcd t_ld t_ic --> [ - L_klcd t_ld ]_kc t_ic
        t_ia.contract("ab,cb->ac", x_0, x_ik, factor=-1.0)
        #
        # X_ac
        #
        # - t_ka fkc
        t_ia.contract("ab,ac->bc", fock, x_ac, factor=-1.0, **ov2)
        # L_kadc t_kd
        mo2.contract("abcd,ac->bd", t_ia, x_ac, factor=2.0, **ovvv)
        mo2.contract("abcd,ad->bc", t_ia, x_ac, factor=-1.0, **ovvv)
        # - L_klcd t_ld t_ka --> [ - L_klcd t_ld ]_kc t_ka
        t_ia.contract("ab,ac->bc", x_0, x_ac, factor=-1.0)
        #
        # X1_iakc
        #
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
        #
        # X_iak
        #
        # - <ac|kk> t_ic
        gpqrr = mo2.contract("abcc->abc")
        gpqrr.contract("abc,eb->eac", t_ia, x_iak, factor=-1.0, **vvo)
        #
        # X_iac
        #
        # - <ik|cc> t_ka
        gpqrr.contract("abc,be->aec", t_ia, x_iac, factor=-1.0, **oov)
        #
        # X_ia
        #
        # L_kica t_kc
        mo2.contract("abcd,ac->bd", t_ia, x_ia, factor=2.0, **oovv)
        mo2.contract("abcd,ad->bc", t_ia, x_ia, factor=-1.0, **oovv)
        #
        # Delete ERI (MO) as they are not required anymore
        #
        mo2.__del__()
