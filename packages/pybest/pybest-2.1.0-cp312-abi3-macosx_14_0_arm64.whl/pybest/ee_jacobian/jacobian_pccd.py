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

#  2023/2024 This module has been written by Somayeh Ahmadkhani (original version)

"""The Coupled Cluster Jacobian matrix implementation for a pCCD reference
function.

 Indexing convention:
  :i,j,k,..: occupied orbitals of principle configuration
  :a,b,c,..: virtual orbitals of principle configuration
  :p,q,r,..: general indices (occupied, virtual)

 P^bc_jk performs a pair permutation, i.e., P^bc_jk o_(bcjk) = o_(cbkj)

 Abbreviations used (if not mentioned in doc-strings):
  :L_pqrs: 2<pq|rs>-<pq|sr>
  :g_pqrs: <pq|rs>

Child class of REOMCC and REOMpCCD.
"""

from typing import Any

from pybest.ee_eom.eom_pccd import REOMpCCD
from pybest.exceptions import ArgumentError
from pybest.linalg.base import FourIndex, OneIndex, TwoIndex
from pybest.log import timer
from pybest.utility import unmask


class JacobianpCCD(REOMpCCD):
    """Extract the Jacobian pCCD matrix from EOM-pCCD Hamiltonian."""

    long_name = "Jacobian pair Coupled Cluster Doubles"
    acronym = "Jacobian-pCCD"
    reference = "pCCD"
    singles_ref = False
    pairs_ref = True
    doubles_ref = False
    singles_ci = False
    pairs_ci = True
    doubles_ci = False

    def unmask_args(self, *args: Any, **kwargs: dict[str, Any]) -> Any:
        """Extract all tensors/quantities from function arguments and keyword
        arguments. Arguments/kwargs may contain:
        * t_p (DenseTwoIndex): Pair CC doubles amplitudes.
        * l_p (DenseTwoIndex): Lagrange multipliers.
        * dm_1/dm_a (DenseTwoIndex): Spin independent one-particle density matrix (1-RDM)/1-RDM for alpha electrons.
        """
        t_p = unmask("t_p", *args, **kwargs)
        if t_p is None:
            raise ArgumentError("Cannot find amplitudes(t_p).")
        self.checkpoint.update("t_p", t_p)

        l_p = unmask("l_p", *args, **kwargs)
        if l_p is None:
            raise ArgumentError("Cannot find lagrange multipliers (l_p).")
        self.checkpoint.update("l_p", l_p)

        dm_1 = unmask("dm_1", *args) or unmask("dm_1_a", *args)
        if dm_1 is None:
            raise ArgumentError("Cannot find one particle density matrix.")
        self.checkpoint.update("dm_1", dm_1)

        # Overwrite nroot attribute of eom_base class
        self.nroot = kwargs.get("nroot", self.dimension - 1)

        return REOMpCCD.unmask_args(self, *args, **kwargs)

    @timer.with_section("J: pCCD")
    def build_full_hamiltonian(self) -> TwoIndex:
        """Jacobian matrix where ground state elements are zero.
           We overwrite the parent class method of REOMpCCD to
           eliminate the <0|H|X> and <X|H|0> terms in the Hamiltonian
           matrix.

        Returns:
            TwoIndex: Jacobian matrix
        """
        jacobian = REOMpCCD.build_full_hamiltonian(self)

        # jacobian[begin0:end0, begin1:end1] = 0.0
        # first row: jacobian[:1, :] = 0.0
        jacobian.assign(0.0, end0=1)
        # first column: jacobian[:, :1] = 0.0
        jacobian.assign(0.0, end1=1)

        return jacobian

    def compute_h_diag(self, *args: Any) -> OneIndex:
        """Used by Davidson module for pre-conditioning

        args:
            required for Davidson module (not used here)

        Returns:
            OneIndex: Diagonal elements of Jacobian
        """
        jacobian_diag = REOMpCCD.compute_h_diag(self, *args)

        # jacobian_diag[begin0:end0] = 0.0
        # first element: jacobian[0] = 0
        jacobian_diag.assign(0.0, end0=1)

        return jacobian_diag

    @timer.with_section("J: pCCD H_sub")
    def build_subspace_hamiltonian(
        self, bvector: OneIndex, hdiag: OneIndex, *args: Any
    ) -> OneIndex:
        """Used by Davidson module to construct subspace Hamiltonian. Includes all
        terms that are similar for all Jacobian-pCCD flavours with single excitations.

        Args:
            bvector (OneIndex): contains current approximation to CI coefficients
            hdiag (OneIndex): Diagonal Jacobian elements required in Davidson module
                              (not used here)

        Returns:
            OneIndex: Set of arguments passed by the Davidson module (not used here)
        """
        sigma = REOMpCCD.build_subspace_hamiltonian(
            self, bvector, hdiag, *args
        )
        # sigma[begin0:end0] = 0.0
        # first element: sigma[0] = 0
        sigma.assign(0.0, end0=1)

        return sigma

    def update_hamiltonian(self, mo1: TwoIndex, mo2: FourIndex) -> None:
        """Derive all auxiliary matrices.

        Args:
            mo1 (TwoIndex): one-electron integrals
            mo2 (FourIndex): two-electron integrals
        """
        REOMpCCD.update_hamiltonian(self, mo1, mo2)
