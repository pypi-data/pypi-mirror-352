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

    Abbreviations used (if not mentioned in doc-strings):
     :L_pqrs: 2<pq|rs>-<pq|sr>
     :g_pqrs: <pq|rs>

This module has been written by:
2023: Katharina Boguslawski
"""

import math
from typing import Any

import numpy as np
from numpy.typing import NDArray

from pybest.ea_eom.xea_base import RXEACC
from pybest.exceptions import ArgumentError
from pybest.linalg import (
    DenseOneIndex,
    DenseTwoIndex,
    FourIndex,
)
from pybest.log import log


class RSEACC(RXEACC):
    """Restricted Single Electron Affinity Equation of Motion Coupled Cluster
    base class

    Purpose:
    Determine the excitation energies from some EA-EOM-CC model

    Currently supported particle-hole operators:
     * particle (1p)
     * particle-hole-particle (2p1h)

    """

    acronym = "EA-EOM-CC"
    long_name = (
        "Restricted Electron Affinity Equation of Motion Coupled Cluster"
    )
    cluster_operator = ""
    particle_hole_operator = "1p + 2p1h"
    reference = ""
    order = "EA"
    alpha = -1

    @RXEACC.n_particle_operator.setter
    def n_particle_operator(self, new: int) -> None:
        """Set number of particles operator.

        **Arguments**

        new
            Allowed values are either in [1,2] or None. If None is passed,
            n_particle_operator is set to default 2 particle operators.
        """
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        if new is None:
            # set default value to two particle operators
            self._n_particle_operator = 2
        elif new in [1, 2]:
            self._n_particle_operator = new
        if not self._n_particle_operator <= nactv:
            raise ArgumentError(
                f"Inconsistent number of particle operators ({new}) and electrons "
                f"({2 * nacto}). For s_z = 0.5, 1 and 2 particle "
                "operators are supported, while for s_z = 1.5, only 2 particle "
                "operators are implemented. Decrease the "
                f"number of particle operators from {new} to {new - 1} for "
                f"{int(self.alpha)} unpaired electrons if possible."
            )

    @property
    def dimension(self) -> int:
        """Number of unknowns"""
        raise NotImplementedError

    def set_hamiltonian(
        self,
        mo1: DenseTwoIndex,
        mo2: FourIndex,
    ) -> None:
        """Compute auxiliary matrices

        **Arguments:**

        mo1, mo2
            One- and two-electron integrals (some Hamiltonian matrix
            elements) in the MO basis.
        """
        raise NotImplementedError

    def compute_h_diag(self, *args: Any) -> DenseOneIndex:
        """Used by Davidson module for pre-conditioning"""
        raise NotImplementedError

    def build_subspace_hamiltonian(
        self, b_vector: DenseOneIndex, h_diag: DenseOneIndex, *args: Any
    ) -> DenseOneIndex:
        """Used by Davidson module to construct subspace Hamiltonian"""
        raise NotImplementedError

    #
    # Printing operations for all EA models
    #
    def print_ci_vector(self, ci_dict: dict[int, float]) -> None:
        """Print eigenvectors for various S_z

        **Arguments:**

        ci_dict:
            (OrderedDict) composite index as key, CI vector as value
        """
        raise NotImplementedError

    def print_weights(self, e_vec_j: NDArray[np.float64]) -> None:
        """Print weights of R operators for various S_z

        **Arguments:**

        e_vec_j:
            (NDArray[np.float64]) CI vector
        """
        raise NotImplementedError

    #
    # Indexing operations
    #
    def get_mask(self, select: bool) -> NDArray[np.integer]:
        """Get unique indices that are returned during diagonalization

        **Arguments:**

        select:
            (int) diagonal offset as defined in numpy.triu_indices (k arg)
        """
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        # Create mask
        ind0, ind1 = np.indices((nactv, nacto))
        mask = np.ones((nactv, nactv, nacto), dtype=bool)
        mask[ind0, ind0, ind1] = False
        mask[np.triu_indices(nactv, k=select)] = False
        return mask

    def get_index_of_mask(
        self, select: bool
    ) -> tuple[NDArray[np.integer], ...]:
        """Get unique indices of mask to assign during diagonalization

        **Arguments:**

        select:
            (int) diagonal offset as defined in numpy.triu_indices (k arg)
        """
        mask = self.get_mask(select)
        indices = np.where(mask)
        return indices

    def get_index_abj(self, index: int) -> tuple[int, int, int, int]:
        """
        Return particle-particle-hole indices from composite index of CI vector

        **Arguments:**

        index
            The composite index to be resolved
        """
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        if self.spin_free and self.s_z != 1.5:
            a, b, j = np.unravel_index(index, (nactv, nactv, nacto))
            return int(a), int(b), int(j), False
        end_aa = (nactv - 1) * nactv * nacto // 2
        # abj block (same spin):
        if index < end_aa:
            # Triu index:
            triu = np.triu_indices(nactv, k=1)
            j = index % nacto
            index_ = index // nacto
            a = triu[0][index_]
            b = triu[1][index_]
            return int(a), int(b), int(j), True
        # aBJ block (opposite spin):
        a, b, j = np.unravel_index(index - end_aa, (nactv, nactv, nacto))
        return int(a), int(b), int(j), False


class RSEACC1(RSEACC):
    """
    Restricted Single Electron Attachment Equation of Motion Coupled Cluster
    class restricted to Single EA for any CC reference function and 1 unpaired
    electron (S_z = 0.5)

    This class defines only the functions that are universal for any EA-CC model
    with 1 unpaired electron:

        * dimension (number of degrees of freedom)
        * print functions (ci vector and weights)
        * _check_multiplicity (estimates spin multiplicity)

    Note that the R_abj and R_aBJ blocks are considered together. Thus, setting
    the number of particle operators equal to 2, requires at least 2 virtual
    orbitals.
    """

    long_name = (
        "Restricted Electron Affinity Equation of Motion Coupled Cluster"
    )
    acronym = "EA-EOM-CC"
    reference = "CC"
    order = "EA"
    alpha = 1

    @property
    def dimension(self) -> int:
        """Number of unknowns"""
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        if self.n_particle_operator == 1:
            return nactv
        if self.spin_free:
            return nactv + nactv * nactv * nacto
        return (
            nactv + (nactv - 1) * nactv * nacto // 2 + (nactv) * nactv * nacto
        )

    def print_ci_vector(self, ci_dict: dict[int, float]) -> None:
        """Print eigenvectors for S_z = 0.5

        **Arguments:**

        ci_dict:
            (OrderedDict) composite index as key, CI vector as value
        """
        ncore = self.occ_model.ncore[0]
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        nocc = ncore + nacto
        # Loop over all composite indices above threshold
        for ind, ci in ci_dict.items():
            if (ind - nactv) >= 0:
                a, b, j, same_spin = self.get_index_abj(ind - nactv)
                state = "r_abj" if same_spin else "r_aBJ"
                log(
                    f"{state:>17}:   ({a + nocc + 1:>4},{b + nocc + 1:>4},"
                    f"{j + ncore + 1:3})   {ci: 3.5f}"
                )
            else:
                log(
                    f"{'r_a':>17}:            ({ind + nocc + 1:>4})   "
                    f"{ci: 3.5f}"
                )

    def print_weights(self, e_vec_j: NDArray[np.float64]) -> None:
        """Print weights of R operators for S_z = 0.5

        **Arguments:**

        e_vec_j:
            (NDArray[np.float64]) CI vector
        """
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        w_a = np.dot(e_vec_j[:nactv], e_vec_j[:nactv])
        w_abj = 0
        w_aBJ = 0
        log(f"{'weight(r_a)':>17}: {w_a: 1.5f}")
        if self.n_particle_operator >= 2:
            if self.spin_free:
                w_abj = np.dot(e_vec_j[nactv:], e_vec_j[nactv:])
                log(f"{'weight(r_abj)':>22}: {w_abj: 1.5f}")
            else:
                end = (nactv - 1) * nactv * nacto // 2 + nactv
                w_abj = np.dot(e_vec_j[nactv:end], e_vec_j[nactv:end])
                w_aBJ = np.dot(e_vec_j[end:], e_vec_j[end:])
                log(f"{'weight(r_abj)':>17}: {w_abj: 1.5f}")
                log(f"{'weight(r_aBJ)':>17}: {w_aBJ: 1.5f}")
        #
        # Assess spin symmetry of state. Since we do not have a spin-adapted
        # implementation, we can make an educated check/guess here.
        #
        multiplicity = self._check_multiplet(e_vec_j, w_a, w_abj, w_aBJ)
        log(f"Suggested spin multiplicity: {multiplicity}")
        log(" ")

    def _check_multiplet(
        self,
        e_vec_j: NDArray[np.float64],
        w_a: float,
        w_abj: float,
        w_aBJ: float,
    ) -> str:
        """Check and guess the multiplet of a state based on CI weights"""
        nactv = self.occ_model.nactv[0]
        # First: check for R_a (if any, we assume doublet states)
        check = np.any(abs(e_vec_j[:nactv]) > 1e-6) and w_a > 1e-6
        # Second: compare weights of R_abj and R_aBJ, for pure quartet states
        # we have w_aBJ ~ 2*w_abj
        if (
            not math.isclose(w_aBJ, 2 * w_abj, rel_tol=1e-3, abs_tol=1e-5)
            or check
        ):
            return "doublet"
        return "quartet"


class RSEACC3(RSEACC):
    """
    Restricted Single Electron Attachment Equation of Motion Coupled Cluster
    class restricted to Single EA for any CC reference function and 3 unpaired
    electron (S_z = 1.5)

    This class defines only the functions that are universal for any EA-CC model
    with 1 unpaired electron:

        * dimension (number of degrees of freedom)
        * print functions (ci vector and weights)

    Note that the R_abj and R_aBJ blocks are considered together. Thus, setting
    the number of particle operators equal to 2, requires at least 2 virtual
    orbitals.
    """

    long_name = (
        "Restricted Electron Affinity Equation of Motion Coupled Cluster"
    )
    acronym = "EA-EOM-CC"
    reference = "CC"
    order = "EA"
    alpha = 3

    @property
    def dimension(self) -> int:
        """Number of unknowns"""
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        return (nactv - 1) * nactv * nacto // 2

    def print_ci_vector(self, ci_dict: dict[int, float]) -> None:
        """Print eigenvectors for S_z = 1.5

        **Arguments:**

        ci_dict:
            (OrderedDict) composite index as key, CI vector as value
        """
        ncore, nacto = self.occ_model.ncore[0], self.occ_model.nacto[0]
        nocc = ncore + nacto
        # Loop over all composite indices above threshold
        for ind, ci in ci_dict.items():
            a, b, j, _ = self.get_index_abj(ind)
            log(
                f"{'r_abJ':>17}:   ({a + nocc + 1: 3},{b + nocc + 1: 3},{j + ncore + 1: 3})"
                f"   {ci: 1.5f}"
            )

    def print_weights(self, e_vec_j: NDArray[np.float64]) -> None:
        """Print weights of R operators for S_z = 0.5

        **Arguments:**

        e_vec_j:
            (NDArray[np.float64]) CI vector
        """
        log(f"{'weight(r_abJ)':>17}: {np.dot(e_vec_j[:], e_vec_j[:]): 1.5f}")
        log(" ")

    def _check_multiplet(
        self,
        e_vec_j: NDArray[np.float64],
        w_a: float,
        w_abj: float,
        w_aBJ: float,
    ) -> str:
        """Check and guess the multiplet of a state based on CI weights"""
        nactv = self.occ_model.nactv[0]
        # First: check for R_a (if any, we assume doublet states)
        check = np.any(abs(e_vec_j[:nactv]) > 1e-6) and w_a > 1e-6
        # Second: compare weights of R_abj and R_aBJ, for pure quartet states
        # we have w_aBJ ~ 2*w_abj
        if (
            not math.isclose(w_aBJ, 2 * w_abj, rel_tol=1e-3, abs_tol=1e-5)
            or check
        ):
            return "doublet"
        return "quartet"
