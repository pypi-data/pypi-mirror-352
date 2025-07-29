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
"""Double Electron Attachment Equation of Motion Coupled Cluster implementations.
   This is the base class for all double EA implementations.

   Variables used in this module:
    :ncore:     number of frozen core orbitals
    :nocc:      number of occupied orbitals in the principle configuration
    :nacto:     number of active occupied orbitals in the principle configuration
    :nvirt:     number of virtual orbitals in the principle configuration
    :nactv:     number of active virtual orbitals in the principle configuration
    :nbasis:    total number of basis functions
    :nact:      total number of active orbitals (nacto+nactv)
    :e_ea:      the energy correction for DEA
    :civ_ea:    the CI amplitudes from a given EOM model
    :rab:       2 particles operator
    :rabck:     3 particles 1 hole operator (same spin)
    :rabCK:     3 particles 1 hole operator (opposite spin)

   Indexing convention:
     :i,j,k,..: occupied orbitals of principal configuration (alpha spin)
     :a,b,c,..: virtual orbitals of principal configuration (alpha spin)
     :p,q,r,..: general indices (occupied, virtual; alpha spin)
     :I,J,K,..: occupied orbitals of principal configuration (beta spin)
     :A,B,C,..: virtual orbitals of principal configuration (beta spin)
     :P,Q,R,..: general indices (occupied, virtual; beta spin)

   Abbreviations used (if not mentioned in doc-strings):
     :2p:    2 particles
     :3p:    3 particles
     :aa:    same-spin component (Alpha-Alpha)
     :ab:    opposite-spin component (Alpha-Beta)


This module has been written by:
2023: Katharina Boguslawski
2024: KB: New RDEACC0, RDEACC2, and RDEACC4 base classes
"""

from __future__ import annotations

import math
from itertools import combinations
from typing import Any

import numpy as np
from numpy.typing import NDArray

from pybest.ea_eom.xea_base import RXEACC
from pybest.exceptions import ArgumentError, ConsistencyError
from pybest.linalg import DenseOneIndex
from pybest.linalg.base import FourIndex, OneIndex, TwoIndex
from pybest.log import log
from pybest.utility import check_options


class RDEACC(RXEACC):
    """
    Restricted Double Electron Attachment Equation of Motion Coupled Cluster
    class restricted to Double EA

    Purpose:
    Determine the excitation energies from some DEA-EOM-CC model

    Currently supported particle-hole operators:
     * particle (2p)
     * particle-hole-particle (3p1h)

    """

    long_name = "Double Electron Attachment Equation of Motion Coupled Cluster"
    acronym = "DEA-EOM-CC"
    cluster_operator = ""
    particle_hole_operator = "2p + 3p1h"
    reference = ""
    order = "DEA"
    alpha = -1

    @RXEACC.n_particle_operator.setter
    def n_particle_operator(self, new: int) -> None:
        """Set number of particles operator.

        **Arguments**

        new
            Allowed values are either in [2,3] or None. If None is passed,
            n_particle_operator is set to default 3 particle operators.
        """
        if new is None:
            # set default value to three particle operators
            self._n_particle_operator = 3
        elif new in [2, 3]:
            self._n_particle_operator = new
        if not self._check_n_particle_operator():
            nacto = self.occ_model.nacto[0]
            raise ArgumentError(
                f"Inconsistent number of particle operators ({new}) and electrons "
                f"({2 * nacto}). For s_z = [0, 1], 2 and 3 particle "
                "operators are supported, while for s_z = 2, only 3 particle "
                "operators are implemented. Decrease the "
                f"number of particle operators from {new} to {new - 1} for "
                f"{int(self.s_z * 2.0)} unpaired electrons if possible."
            )

    @property
    def dimension(self) -> int:
        """Total number of unknowns of chosen DEA model"""
        raise NotImplementedError

    def _check_n_particle_operator(self) -> bool:
        """Check for consistency of the number of particle operators. Returns
        False if the number of particle operators does not agree with the spin
        projection and the number of active virtual orbitals.
        """
        raise NotImplementedError

    def set_hamiltonian(self, mo1: TwoIndex, mo2: FourIndex) -> None:
        """Compute auxiliary matrices

        **Arguments:**

        mo1, mo2
            One- and two-electron integrals (some Hamiltonian matrix
            elements) in the MO basis.
        """
        raise NotImplementedError

    def compute_h_diag(self, *args: Any) -> OneIndex:
        """Used by Davidson module for pre-conditioning"""
        raise NotImplementedError

    def build_subspace_hamiltonian(
        self, b_vector: OneIndex, h_diag: OneIndex, *args: Any
    ) -> DenseOneIndex:
        """Used by Davidson module to construct subspace Hamiltonian"""
        raise NotImplementedError

    #
    # Printing operations for all DEA models
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
            (boolean) True for same spin, False for opposite spin
        """
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        mask = np.zeros((nactv, nactv, nactv, nacto), dtype=bool)
        if self.s_z == 2.0 or (self.s_z == 1.0 and select):
            # case a<b<c
            indices_ = list(combinations(range(nactv), r=3))
            indices = tuple(np.array(indices_).T)
            mask[indices] = True
        elif self.s_z == 1.0:
            # case a<b, all c
            indices = np.triu_indices(nactv, 1)
            mask[indices] = True
        elif self.s_z == 0.0 and select:
            # case a<c, all a,B
            indices_ = np.triu_indices(nactv, 1)
            mask[indices_[0], :, indices_[1], :] = True
        elif self.s_z == 0.0 and not select:
            # case b<c, all a,B
            indices_ = np.triu_indices(nactv, 1)
            mask[:, indices_[0], indices_[1], :] = True
        return mask

    # NOTE: we can replace tuple[NDArray[np.float64], ...] with Sequence[NDArray[np.float64]]
    def get_index_of_mask(
        self, select: bool
    ) -> tuple[NDArray[np.integer], ...]:
        """Get unique indices of mask to assign during diagonalization

        **Arguments:**

        select:
            (boolean) True for same spin, False for opposite spin
        """
        mask = self.get_mask(select)
        indices = np.where(mask)
        return indices

    def get_index_ab(self, index: int) -> tuple[int, int]:
        """Return particle-particle indices from composite index of CI vector

        ** Arguments: **

        index
            The composite index to be resolved
        """
        nactv = self.occ_model.nactv[0]
        # Triu index:
        if self.s_z == 0.0:
            j = index % nactv
            i = ((index - j) // nactv) % nactv
            return i, j
        if self.s_z == 1.0:
            triu = np.triu_indices(nactv, k=1)
            return triu[0][index], triu[1][index]
        raise NotImplementedError

    def get_index_abck(
        self, index: int
    ) -> tuple[int, int, int, int, bool | None]:
        """
        Return particle-particle-particle-hole (3p1h) indices from composite
        index of CI vector

        ** Arguments: **

        index
            The composite index to be resolved
        """
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        if self.s_z == 0.0:
            end = nactv * nactv * (nactv - 1) // 2 * nacto
            spin = index < end
            index = index if spin else index - end
            mask = self.get_mask(spin)
            # return True indices
            ind = np.where(mask)
            return (
                ind[0][index],
                ind[1][index],
                ind[2][index],
                ind[3][index],
                spin,
            )
        if self.s_z == 1.0:
            end = nactv * (nactv - 1) * (nactv - 2) // 6 * nacto
            if index < end:
                # with symmetry a < b < c
                abc, k = np.unravel_index(
                    int(index), ((nactv - 2) * (nactv - 1) * nactv // 6, nacto)
                )
                a, b, c = list(combinations(range(nactv), r=3))[int(abc)]
                return a, b, c, int(k), True
            # with symmetry a < b, all c
            a_b, c, k = np.unravel_index(
                int(index - end), ((nactv - 1) * nactv // 2, nactv, nacto)
            )
            tril = np.triu_indices(nactv, k=1)
            # Triu index:
            a = tril[0][a_b]
            b = tril[1][a_b]
            return a, b, c, int(k), False
        if self.s_z == 2.0:
            # with symmetry a < b < c
            abc, k = np.unravel_index(
                int(index), ((nactv - 2) * (nactv - 1) * nactv // 6, nacto)
            )
            a, b, c = list(combinations(range(nactv), r=3))[int(abc)]
            return a, b, c, int(k), None
        raise NotImplementedError


class RDEACC0(RDEACC):
    """
    Restricted Double Electron Attachment Equation of Motion Coupled Cluster
    class restricted to Double EA for any CC reference function and 0 unpaired
    electron (S_z = 0.0)

    This class defines only the functions that are universal for any DEA-CC model
    with 0 unpaired electron:

        * dimension (number of degrees of freedom)
        * print functions (ci vector and weights)
        * _check_multiplicity (estimates spin multiplicity)
    """

    long_name = "Restricted Double Electron Affinity Equation of Motion Coupled Cluster"
    acronym = "DEA-EOM-CC"
    reference = "CC"
    order = "DEA"
    alpha = 0

    @property
    def dimension(self) -> int:
        """Total number of unknowns of chosen DEA model"""
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        if self.n_particle_operator == 3:
            return nactv * nactv + nacto * nactv * (nactv - 1) * nactv
        if self.n_particle_operator == 2:
            return nactv * nactv
        raise NotImplementedError

    def _check_n_particle_operator(self) -> bool:
        """Check for consistency of the number of particle operators. Returns
        False if the number of particle operators does not agree with the spin
        projection and the number of active virtual orbitals.
        """
        nactv = self.occ_model.nactv[0]
        check_options("n_particle_operator", self.n_particle_operator, 2, 3)
        return self.n_particle_operator <= nactv * 2.0

    def print_ci_vector(self, ci_dict: dict[int, float]) -> None:
        """Print eigenvectors for S_z = 0.0

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
            r_abck = ind - nactv * nactv
            if r_abck >= 0:
                a, b, c, k, same_spin = self.get_index_abck(r_abck)
                state = "r_aBck" if same_spin else "r_aBCK"
                log(
                    f"{state:>17}:   ({a + nocc + 1: 4},{b + nocc + 1: 3},"
                    f"{c + nocc + 1: 3},{k + ncore + 1: 3})   {ci: 1.5f}"
                )
            else:
                a, b = self.get_index_ab(ind)
                log(
                    f"{'r_aB':>17}:          ({a + nocc + 1: 4},"
                    f"{b + nocc + 1: 4})   {ci: 1.5f}"
                )

    def print_weights(self, e_vec_j: NDArray[np.float64]) -> None:
        """Print weights of R operators for S_z = 0.0

        **Arguments:**

        e_vec_j:
            (NDArray[np.float64]) CI vector
        """
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        nactv2 = nactv * nactv
        w_aB = np.dot(e_vec_j[:nactv2], e_vec_j[:nactv2])
        log(f"{'weight(r_aB)':>17}: {w_aB: 1.5f}")
        if self.n_particle_operator > 2:
            end = nactv * nactv * (nactv - 1) // 2 * nacto + nactv2
            w_aBck = np.dot(e_vec_j[nactv2:end], e_vec_j[nactv2:end])
            w_aBCK = np.dot(e_vec_j[end:], e_vec_j[end:])
            log(f"{'weight(r_aBck)':>17}: {w_aBck: 1.5f}")
            log(f"{'weight(r_aBCK)':>17}: {w_aBCK: 1.5f}")
        #
        # Assess spin symmetry of state. Since we do not have a spin-adapted
        # implementation, we can make an educated check/guess here.
        multiplicity = self._check_multiplet(e_vec_j, w_aB)
        log(f"Suggested spin multiplicity: {multiplicity}")
        log(" ")

    def _check_multiplet(
        self, e_vec_j: NDArray[np.float64], w_aB: float = 0.0
    ) -> str:
        """Check and guess the multiplet of a state based on CI weights

        Args:
            e_vec_j (NDArray[np.float64]): CI vector of state
            w_aB (float, optional): |R_aB|^2. Defaults to 0.0.

        Returns:
            str: _description_
        """
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        nactv2 = nactv * nactv
        # First check for approximate symmetry of R_aB (R_aB == R_Ba or -R_Ba)
        r_aB = e_vec_j[:nactv2].reshape(nactv, nactv)
        r_aA = r_aB.diagonal()
        triplet = np.allclose(
            r_aB, -r_aB.transpose(), rtol=1e-3, atol=1e-5
        ) and np.all(abs(r_aA) < 1e-6)
        if w_aB > 1e-5:
            # If R_aB contributions are not zero, decide solely on its symmetry
            return "triplet" if triplet else "singlet"
        # Second: compare symmetry of vectors R_aBck and R_aBCK, for pure
        # singlet states we have R_aBck ~ R_Back
        # This is a bit more complicated and requires more operations
        if self.n_particle_operator > 2:
            end = nactv * nactv * (nactv - 1) // 2 * nacto + nactv2
            r_aBck = self.denself.create_four_index(nactv, nactv, nactv, nacto)
            r_aBCK = self.denself.create_four_index(nactv, nactv, nactv, nacto)
            # assign R_aBck
            mask = self.get_index_of_mask(True)
            r_aBck.assign(e_vec_j[nactv2:end], ind=mask)
            # account for symmetry (ac)
            r_aBck.iadd_transpose((2, 1, 0, 3), factor=-1.0)
            # assign R_aBCK
            mask = self.get_index_of_mask(False)
            r_aBCK.assign(e_vec_j[end:], ind=mask)
            # account for symmetry (BC)
            r_aBCK.iadd_transpose((0, 2, 1, 3), factor=-1.0)
            # transpose inplace to compare values
            r_aBCK.itranspose((1, 0, 2, 3))
            # assess multiplicity
            # R_aBck ~= R_BaCK (R_aBCK is transposed here)
            singlet = np.allclose(r_aBck.array, r_aBCK.array, 1e-3, 1e-5)
            # R_aBck ~= -R_aBCK (R_aBCK is transposed here)
            triplet = np.allclose(r_aBck.array, -r_aBCK.array, 1e-3, 1e-5)
            # R_aBck ~= -R_acBk
            quintet = np.allclose(
                r_aBck.array, -r_aBck.array.transpose(0, 2, 1, 3), 1e-3, 1e-5
            )
            if singlet and not triplet and not quintet:
                return "singlet"
            if triplet and not quintet:
                return "triplet"
            if quintet:
                return "quintet"
        return "inconclusive"


class RDEACC2(RDEACC):
    """
    Restricted Double Electron Attachment Equation of Motion Coupled Cluster
    class restricted to Double EA for any CC reference function and 2 unpaired
    electron (S_z = 1.0)

    This class defines only the functions that are universal for any DEA-CC model
    with 2 unpaired electron:

        * dimension (number of degrees of freedom)
        * print functions (ci vector and weights)
        * _check_multiplicity (estimates spin multiplicity)
    """

    long_name = "Restricted Double Electron Affinity Equation of Motion Coupled Cluster"
    acronym = "DEA-EOM-CC"
    reference = "CC"
    order = "DEA"
    alpha = 2

    @property
    def dimension(self) -> int:
        """Total number of unknowns of chosen DEA model"""
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        if self.n_particle_operator == 3:
            return (
                nactv * (nactv - 1) // 2
                + nactv * (nactv - 1) * (nactv - 2) // 6 * nacto
                + (nactv * (nactv - 1) // 2) * nactv * nacto
            )
        if self.n_particle_operator == 2:
            return nactv * (nactv - 1) // 2
        raise NotImplementedError

    def _check_n_particle_operator(self) -> bool:
        """Check for consistency of the number of particle operators. Returns
        False if the number of particle operators does not agree with the spin
        projection and the number of active virtual orbitals.
        """
        nactv = self.occ_model.nactv[0]
        check_options("n_particle_operator", self.n_particle_operator, 2, 3)
        # R_abCK are still possible if n_particle_operator=3 and nv=2. However, R_abck
        # terms cannot be included.
        # For the time being, we want both R terms to be included.
        # If this changes in the futuer, all code below needs to be updated.
        return self.n_particle_operator <= nactv

    def print_ci_vector(self, ci_dict: dict[int, float]) -> None:
        """Print eigenvectors for S_z = 1.0

        **Arguments:**

        ci_dict:
            (OrderedDict) composite index as key, CI vector as value
        """
        ncore, nacto, nactv = (
            self.occ_model.ncore[0],
            self.occ_model.nacto[0],
            self.occ_model.nactv[0],
        )
        nvv = nactv * (nactv - 1) // 2
        nocc = ncore + nacto
        # Loop over all composite indices above threshold
        for ind, ci in ci_dict.items():
            r_abck = ind - nvv
            if r_abck >= 0:
                a, b, c, k, same_spin = self.get_index_abck(r_abck)
                state = "r_abck" if same_spin else "r_abCK"
                log(
                    f"{state:>17}:   ({a + nocc + 1: 4},{b + nocc + 1: 3},"
                    f"{c + nocc + 1: 3},{k + ncore + 1: 3})   {ci: 1.5f}"
                )
            else:
                a, b = self.get_index_ab(ind)
                log(
                    f"{'r_ab':>17}:          ({a + nocc + 1: 4},"
                    f"{b + nocc + 1: 4})   {ci: 1.5f}"
                )

    def print_weights(self, e_vec_j: NDArray[np.float64]) -> None:
        """Print weights of R operators for S_z = 1.0

        **Arguments:**

        e_vec_j:
            (NDArray[np.float64]) CI vector
        """
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        nvv = nactv * (nactv - 1) // 2
        w_ab = np.dot(e_vec_j[:nvv], e_vec_j[:nvv])
        w_abck = 0.0
        w_abCK = 0.0
        log(f"{'weight(r_ab)':>17}: {w_ab: 1.5f}")
        if self.n_particle_operator > 2:
            end = nactv * (nactv - 1) * (nactv - 2) // 6 * nacto + nvv
            w_abck = np.dot(e_vec_j[nvv:end], e_vec_j[nvv:end])
            w_abCK = np.dot(e_vec_j[end:], e_vec_j[end:])
            log(f"{'weight(r_abck)':>17}: {w_abck: 1.5f}")
            log(f"{'weight(r_abCK)':>17}: {w_abCK: 1.5f}")
        #
        # Assess spin symmetry of state. Since we do not have a spin-adapted
        # implementation, we can make an educated check/guess here.
        multiplicity = self._check_multiplet(e_vec_j, w_ab, w_abck, w_abCK)
        log(f"Suggested spin multiplicity: {multiplicity}")
        log(" ")

    def _check_multiplet(
        self,
        e_vec_j: NDArray[np.float64],
        w_ab: float,
        w_abck: float,
        w_abCK: float,
    ) -> str:
        """Check and guess the spin-multiplicity of a state based on CI weights"""
        nactv = self.occ_model.nactv[0]
        nvv = nactv * (nactv - 1) // 2
        # First: check for R_ij (if any, we assume triplet states)
        triplet = np.any(abs(e_vec_j[:nvv]) > 1e-6) and w_ab > 1e-6
        # Second: compare weights of R_abck and R_abCK, for pure quintet states
        # we have w_abCK ~ 3*w_abck
        if (
            not math.isclose(w_abCK, 3 * w_abck, rel_tol=1e-3, abs_tol=1e-5)
            or triplet
        ):
            return "triplet"
        return "quintet"


class RDEACC4(RDEACC):
    """
    Restricted Double Electron Attachment Equation of Motion Coupled Cluster
    class restricted to Double EA for any CC reference function and 4 unpaired
    electron (S_z = 2.0)

    This class defines only the functions that are universal for any DEA-CC model
    with 2 unpaired electron:

        * dimension (number of degrees of freedom)
        * print functions (ci vector and weights)
        * _check_multiplicity (estimates spin multiplicity)
    """

    long_name = "Restricted Double Electron Affinity Equation of Motion Coupled Cluster"
    acronym = "DEA-EOM-CC"
    reference = "CC"
    order = "DEA"
    alpha = 4

    @property
    def dimension(self) -> int:
        """Total number of unknowns of chosen DEA model"""
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        if self.n_particle_operator == 3:
            return nactv * (nactv - 1) * (nactv - 2) // 6 * nacto
        if self.n_particle_operator == 2:
            raise ConsistencyError(
                "For S_z = 2.0, at least 3 particle operators are required."
            )
        raise NotImplementedError

    def _check_n_particle_operator(self) -> bool:
        """Check for consistency of the number of particle operators. Returns
        False if the number of particle operators does not agree with the spin
        projection and the number of active virtual orbitals.
        """
        nactv = self.occ_model.nactv[0]
        return self.n_particle_operator == 3 and nactv >= 3.0

    def print_ci_vector(self, ci_dict: dict[int, float]) -> None:
        """Print eigenvectors for S_z = 1.0

        **Arguments:**

        ci_dict:
            (OrderedDict) composite index as key, CI vector as value
        """
        ncore, nacto = self.occ_model.ncore[0], self.occ_model.nacto[0]
        nocc = ncore + nacto
        # Loop over all composite indices above threshold
        for ind, ci in ci_dict.items():
            a, b, c, k, _ = self.get_index_abck(ind)
            log(
                f"{'r_abcK':>17}:   ({a + nocc + 1: 4},{b + nocc + 1: 3},{c + nocc + 1: 3},"
                f"{k + ncore + 1: 3})   {ci: 1.5f}"
            )

    def print_weights(self, e_vec_j: NDArray[np.float64]) -> None:
        """Print weights of R operators for S_z = 1.0

        **Arguments:**

        e_vec_j:
            (NDArray[np.float64]) CI vector
        """
        log(f"{'weight(r_abcK)':>17}: {np.dot(e_vec_j[:], e_vec_j[:]): 1.5f}")
        log(" ")
