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
"""Equation of Motion Coupled Cluster implementations of EOM-pCCD+S, that is,
pCCD with single excitations.

Child class of REOMpCCDSBase(REOMCC) class.
"""

from typing import Any

from pybest.linalg.base import FourIndex, OneIndex, TwoIndex
from pybest.log import timer

from .eom_pccd_s_base import REOMpCCDSBase


class REOMpCCDS(REOMpCCDSBase):
    """Perform an EOM-pCCD+S calculation."""

    long_name = "Equation of Motion pair Coupled Cluster Doubles with a posteriori Singles"
    acronym = "EOM-pCCD+S"
    reference = "pCCD"
    singles_ref = False
    pairs_ref = True
    doubles_ref = False
    singles_ci = True
    pairs_ci = True
    doubles_ci = False

    @timer.with_section("EOMpCCD+S: H_full")
    def build_full_hamiltonian(self) -> TwoIndex:
        """Construct full Hamiltonian matrix used in exact diagonalization"""
        #
        # Call base class method
        #
        eom_ham = REOMpCCDSBase.build_full_hamiltonian(self)
        #
        # Add missing term(s) not included in base class
        #
        # effective Hamiltonian matrix elements
        x0_ia = self.from_cache("x0_ia")
        #
        # H_kc,0
        #
        end_s = self.occ_model.nacto[0] * self.occ_model.nactv[0] + 1
        eom_ham.iadd(x0_ia.ravel(), begin0=1, end0=end_s, end1=1)
        return eom_ham

    @timer.with_section("EOMpCCD+S: H_diag")
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

    @timer.with_section("EOMpCCD+S: H_sub")
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
        # Get auxiliary matrices
        #
        x0_ia = self.from_cache("x0_ia")
        #
        # Calculate missing terms in sigma vector (H.bvector)_kc
        #
        # Single excitations
        #
        # Xkc0 r0
        end_s = self.occ_model.nactv[0] * self.occ_model.nacto[0] + 1
        sigma.iadd(
            x0_ia.ravel(), factor=bvector.get_element(0), begin0=1, end0=end_s
        )

        return sigma

    @timer.with_section("EOMpCCD+S: H_eff")
    def update_hamiltonian(self, mo1: TwoIndex, mo2: FourIndex) -> None:
        """Derive all auxiliary matrices.

        **Arguments:**

        mo1, mo2
             one- and two-electron integrals to be sorted.

        """
        #
        # Call base class method
        #
        REOMpCCDSBase.update_hamiltonian(self, mo1, mo2)
        #
        # Modify auxiliary matrices from base class (add missing matrices)
        #
        cia = self.checkpoint["t_p"]
        fock = self.from_cache("fock")
        #
        # Get ranges
        #
        ov2 = self.get_range("ov", offset=2)
        ovoo = self.get_range("ovoo")
        ovvv = self.get_range("ovvv")
        #
        # Aux matrix for Mia,0
        #
        x0_ia = self.init_cache(
            "x0_ia", self.occ_model.nacto[0], self.occ_model.nactv[0]
        )
        # fia
        x0_ia.iadd(fock, 1.0, **ov2)
        # fia cia
        x0_ia.iadd_mult(cia, fock, 1.0, **ov2)
        # <ia|cc> cic
        mo2.contract("abcc,ac->ab", cia, x0_ia, **ovvv)
        # - <ia|ll> cla
        mo2.contract("abcc,cb->ab", cia, x0_ia, factor=-1.0, **ovoo)
        #
        # Delete ERI (MO) as they are not required anymore
        #
        mo2.__del__()
