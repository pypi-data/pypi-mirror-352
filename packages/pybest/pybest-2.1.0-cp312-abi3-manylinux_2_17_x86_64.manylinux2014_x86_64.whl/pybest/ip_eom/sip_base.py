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

# Detailed changelog:
#
# 2025-02: unification of variables and type hints (Julian Świerczyński)

"""Ionization Potential Equation of Motion Coupled Cluster implementations.
This is a base class for all single IP implementations.

   Variables used in this module:
    :ncore:     number of frozen core orbitals
    :nocc:      number of occupied orbitals in the principal configuration
    :nacto:     number of active occupied orbitals in the principal configuration
    :nvirt:     number of virtual orbitals in the principal configuration
    :nactv:     number of active virtual orbitals in the principal configuration
    :nbasis:    total number of basis functions
    :nact:      total number of active orbitals (nacto+nactv)
    :alpha:     number of unpaired electrons; for alpha=0, the spin-integrated
                equations target all possible m_s=0 states (singlet, triplet,
                quintet), for alpha=1, m_s=1/2 states are accessible (doublet,
                quartet), for alpha=2, m_s=1 states (triplet, quintet), for
                alpha=3, m_s=3/2 states (quartet), and for alpha=4, m_s=2 states
                (quintet)
    :e_ip:      the energy correction for IP
    :civ_ip:    the CI amplitudes from a given EOM model
    :e_ref:     the total energy of the (CC) referece wave function
    :alpha:     number of unpaired electrons

   Indexing convention:
    :i,j,k,..: occupied orbitals of principal configuration
    :a,b,c,..: virtual orbitals of principal configuration
    :p,q,r,..: general indices (occupied, virtual)
"""

import math
from collections import OrderedDict
from typing import Any

import numpy as np
from numpy.typing import NDArray

from pybest.exceptions import ArgumentError
from pybest.ip_eom.xip_base import RXIPCC
from pybest.log import log


class RSIPCC(RXIPCC):
    """
    Restricted Ionization Potential Equation of Motion Coupled Cluster
    class restricted to single IP

    Purpose:
    Determine the excitation energies from some IP-EOM-CC model

    Currently supported particle-hole operators:
     * hole (1h)
     * hole-particle-hole (2h1p)

    """

    long_name = ""
    acronym = "IP-EOM-CC"
    reference = ""
    order = "IP"
    alpha = -1

    @RXIPCC.nhole.setter
    def nhole(self, new: int) -> None:
        """Set number of hole operators.

        **Arguments**

        new
            Allowed values are either in [1,2] or None. If None is passed,
            nhole is defaulted to 2 hole operators.
        """
        if new is None:
            # Set default value to two hole operators
            self._nhole = 2
        elif new in [1, 2]:
            self._nhole = new
        else:
            raise NotImplementedError
        if not self._check_nhole():
            raise ArgumentError(
                "Unsupported number of hole operators and occupied orbitals. "
                f"We have {self.occ_model.nacto[0]} occupied orbitals and {self._nhole} "
                f"hole operators for {self.alpha} unpaired electrons."
            )

    @property
    def dimension(self):
        """Total number of unknowns of chosen IP model"""
        raise NotImplementedError

    def _check_nhole(self) -> bool:
        """Check for consistency of the number of hole operators. Returns
        False if the number of hole operators does not agree with the spin
        projection and the number of active occupied orbitals.
        """
        return self.nhole <= self.occ_model.nacto[0]

    def set_hamiltonian(self, mo1, mo2):
        """Update auxiliary tensors for specific IP model"""
        raise NotImplementedError

    def compute_h_diag(self, *args):
        """Used by the Davidson module for pre-conditioning"""
        raise NotImplementedError

    def build_subspace_hamiltonian(self, b_vector, h_diag, *args):
        """Used by the Davidson module to construct subspace Hamiltonian"""
        raise NotImplementedError

    #
    # Printing operations for all IP models
    #

    def print_ci_vector(self, ci_dict):
        """Print eigenvectors for various S_z

        **Arguments:**

        ci_dict:
            (OrderedDict) composite index as key, CI vector as value
        """
        raise NotImplementedError

    def print_weights(self, e_vec_j):
        """Print weights of R operators for various S_z

        **Arguments:**

        e_vec_j:
            (np.array) CI vector
        """
        raise NotImplementedError

    #
    # Indexing operations
    #

    def get_mask(self, select: int) -> NDArray[np.float64]:
        """Get unique indices that are returned during diagonalization

        **Arguments:**

        select:
            (int) diagonal offset as defined in numpy.triu_indices (k arg)
        """
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        ind0, ind1 = np.indices((nacto, nactv))
        mask = np.ones((nacto, nacto, nactv), dtype=bool)
        mask[ind0, ind0, ind1] = False
        mask[np.triu_indices(nacto, k=select)] = False
        return mask

    def get_index_of_mask(self, select: int) -> tuple[NDArray[np.int64], ...]:
        """Get unique indices of mask to assign during diagonalization

        **Arguments:**

        select:
            (int) diagonal offset as defined in numpy.triu_indices (k arg)
        """
        mask = self.get_mask(select)
        indices = np.where(mask)
        return indices

    def get_index_ijb(self, index: int) -> tuple[Any, Any, Any, bool]:
        """
        Return hole-hole-particle indices from composite index of CI vector

        ** Arguments: **

        index
            The composite index to be resolved
        """
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        if self.spin_free:
            i, j, b = np.unravel_index(index, (nacto, nacto, nactv))
            return i, j, b, False
        end_aa = (nacto - 1) * nacto * nactv // 2
        same_spin = True
        # Full index:
        if index < end_aa:
            #
            # return ijb block
            #
            # Triu index:
            triu = np.triu_indices(nacto, k=1)
            b = index % nactv
            index_ = index // nactv
            i = triu[0][index_]
            j = triu[1][index_]
        else:
            #
            # return iJB block
            #
            i, j, b = np.unravel_index(index - end_aa, (nacto, nacto, nactv))
            same_spin = False
        return i, j, b, same_spin


class RSIPCC1(RSIPCC):
    """
    Restricted Single Ionization Potential Equation of Motion Coupled Cluster
    class restricted to Single IP for any CC reference function and 1 unpaired
    electron (S_z = 0.5)

    This class defines only the functions that are universal for any IP-CC model
    with 1 unpaired electron:

        * dimension (number of degrees of freedom)
        * unmask_args (resolve T_p amplitudes)
        * print functions (ci vector and weights)
        * _check_multiplicity (estimates spin multiplicity)

    Note that the R_ijb and R_iJB blocks are considered together. Thus, setting
    the number of hole operators equal to 2, requires at least 2 active
    occupied orbitals.
    """

    long_name = "Ionization Potential Equation of Motion Coupled Cluster"
    acronym = "IP-EOM-CC"
    reference = "CC"
    order = "IP"
    alpha = 1

    @property
    def dimension(self) -> int:
        """Total number of unknowns of chosen IP model. Independent of the CC
        reference state.
        """
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        if self.nhole < 2:
            return nacto
        if self.spin_free:
            return nacto + nacto * nacto * nactv
        return nacto + (nacto - 1) * nacto * nactv // 2 + nacto * nacto * nactv

    def print_ci_vector(self, ci_dict: OrderedDict) -> None:
        """Print eigenvectors for S_z = 0.5

        **Arguments:**

        ci_dict:
            (OrderedDict) composite index as key, CI vector as value
        """
        ncore, nacto = self.occ_model.ncore[0], self.occ_model.nacto[0]
        nocc = ncore + nacto
        # Loop over all composite indices above threshold
        for ind, ci in ci_dict.items():
            if (ind - nacto) >= 0:
                i, j, b, same_spin = self.get_index_ijb(ind - nacto)
                state = "r_ijb" if same_spin else "r_iJB"
                log(
                    f"{state:>17}:   ({i + ncore + 1: 3},{j + ncore + 1: 3},"
                    f"{b + nocc + 1: 3})   {ci: 1.5f}"
                )
            else:
                log(
                    f"{'r_i':>17}:           ({ind + ncore + 1: 3})   "
                    f"{ci: 1.5f}"
                )

    def print_weights(self, e_vec_j: NDArray[np.float64]) -> None:
        """Print weights of R operators for S_z = 0.5

        **Arguments:**

        e_vec_j:
            (np.array) CI vector
        """
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        w_i = np.dot(e_vec_j[:nacto], e_vec_j[:nacto])
        w_ijb = 0
        w_iJB = 0
        log(f"{'weight(r_i)':>17}: {w_i: 1.5f}")
        if self.nhole >= 2:
            if self.spin_free:
                w_ijb = np.dot(e_vec_j[nacto:], e_vec_j[nacto:])
                log(f"{'weight(r_ijb)':>17}: {w_ijb: 1.5f}")
            else:
                end = (nacto - 1) * nacto * nactv // 2 + nacto
                w_ijb = np.dot(e_vec_j[nacto:end], e_vec_j[nacto:end])
                w_iJB = np.dot(e_vec_j[end:], e_vec_j[end:])
                log(f"{'weight(r_ijb)':>17}: {w_ijb: 1.5f}")
                log(f"{'weight(r_iJB)':>17}: {w_iJB: 1.5f}")
        #
        # Assess spin symmetry of state. Since we do not have a spin-adapted
        # implementation, we can make an educated check/guess here.
        #
        multiplicity = self._check_multiplicity(e_vec_j, w_i, w_ijb, w_iJB)
        log(f"Suggested spin multiplicity: {multiplicity}")
        log(" ")

    def _check_multiplicity(
        self,
        e_vec_j: NDArray[np.float64],
        w_i: float,
        w_ijb: float,
        w_iJB: float,
    ) -> str:
        """Check and guess the multiplicity of a state based on CI weights"""
        nacto = self.occ_model.nacto[0]
        # First: check for R_i (if any, we assume doublet states)
        check = np.any(abs(e_vec_j[:nacto]) > 1e-5) and w_i > 1e-5
        # Second: compare weights of R_ijb and R_iJB, for pure quartet states
        # We have w_iJB ~ 2*w_ijb
        if (
            not math.isclose(w_iJB, 2 * w_ijb, rel_tol=1e-3, abs_tol=1e-5)
            or check
        ):
            return "doublet"
        return "quartet"


class RSIPCC3(RSIPCC):
    """
    Restricted Single Ionization Potential Equation of Motion Coupled Cluster
    class restricted to Single IP for any CC reference function for 3 unpaired
    electrons.

    This class defines only the function that are universal for any IP-CC model
    with 3 unpaired electrons:

        * dimension (number of degrees of freedom)
        * _check_nhole (check for sufficient number of occupied orbitals)
        * print functions (ci vector and weights)
        * _check_multiplicity (estimates spin multiplicity)
    """

    long_name = (
        "Ionization Potential Equation of Motion pair Coupled Cluster Doubles"
    )
    acronym = "IP-EOM-pCCD"
    reference = "pCCD"
    order = "IP"
    alpha = 3

    @property
    def dimension(self) -> int:
        """Total number of unknowns of chosen IP model"""
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        return (nacto - 1) * nacto * nactv // 2

    def _check_nhole(self) -> bool:
        """Check for consistency of the number of hole operators. Returns
        False if the number of hole operators does not agree with the spin
        projection and the number of active occupied orbitals.
        """
        return self.nhole >= 2 and self.occ_model.nacto[0] >= 2

    def print_ci_vector(self, ci_dict: OrderedDict) -> None:
        """Print eigenvectors for S_z = 1.5

        **Arguments:**

        ci_dict:
            (OrderedDict) composite index as key, CI vector as value
        """
        ncore, nacto = self.occ_model.ncore[0], self.occ_model.nacto[0]
        nocc = ncore + nacto
        # Loop over all composite indices above threshold
        for ind, ci in ci_dict.items():
            i, j, b, _ = self.get_index_ijb(ind)
            log(
                f"{'r_ijB':>17}:   ({i + ncore + 1: 3},{j + ncore + 1: 3},{b + nocc + 1: 3})"
                f"   {ci: 1.5f}"
            )

    def print_weights(self, e_vec_j: NDArray[np.float64]) -> None:
        """Print weights of R operators for S_z = 1.5

        **Arguments:**

        e_vec_j:
            (np.array) CI vector
        """
        log(f"{'weight(r_ijB)':>17}: {np.dot(e_vec_j[:], e_vec_j[:]): 1.5f}")
        log(" ")
