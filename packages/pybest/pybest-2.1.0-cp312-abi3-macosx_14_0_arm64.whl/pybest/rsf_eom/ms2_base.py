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
# The RSF-CC sub-package has been originally written and updated by Aleksandra Leszczyk (see CHANGELOG)
# Its current version contains updates from the PyBEST developer team.
#
# 2023/24:
# This file has been written by Emil Sujkowski (original version)

"""Equation of Motion Coupled Cluster implementations of a base class for EOM with
single and double excitations.

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
"""

from __future__ import annotations

from abc import ABC
from collections import OrderedDict
from itertools import combinations, product

import numpy as np
from numpy.typing import NDArray
from scipy.special import binom

from pybest.linalg import DenseFourIndex, DenseOneIndex
from pybest.log import log
from pybest.rsf_eom.rsf_base import RSFBase


class RSFMS2Base(RSFBase, ABC):
    """Restricted EOM reversed spin flip class that allows us to obtain high
    spin states from the reference restricted CC singlet (Ms=0) wave function.
    Currently implemented:
        * quintet state (S=2) with Ms=2
    """

    long_name = "Equation-of-motion Coupled Cluster for high-spin quintet states (Ms=2)"
    acronym = "RSF-EOM-CC"
    reference = "RCC"

    def get_symmetry_unique_indices(self) -> NDArray[np.float64]:
        """Return indices that are symmetry-unique."""
        index_nacto = combinations(range(self.occ_model.nacto[0]), 2)
        index_nactv = combinations(range(self.occ_model.nactv[0]), 2)
        return np.asarray(
            list(
                map(
                    lambda x: (x[0][0], x[1][0], x[0][1], x[1][1]),
                    product(index_nacto, index_nactv),
                )
            )
        )

    def ravel(
        self, tensor: DenseFourIndex, label: str = "h_diag"
    ) -> DenseOneIndex:
        """Returns DenseOneIndex instance with unique elements
            r_iajb = r_jbia = -r_ibja = -r_jaib

        Arguments:
            tensor : DenseFourIndex
        """
        indices = self.get_symmetry_unique_indices()
        vector = DenseOneIndex(self.dimension, label=label)
        # this loop is also terrible, replace it later
        for ivec, iten in enumerate(indices):
            i, a, j, b = iten
            vector.set_element(ivec, tensor.get_element(i, a, j, b))
        return vector

    def unravel(
        self, vector: NDArray[np.float64], label: str = "h_diag"
    ) -> DenseFourIndex:
        """Returns DenseFourIndex instance filled out with data from input
        flat_ndarray. Recovers R amplitude symmetry:
            r_iajb = r_jbia = -r_ibja = -r_jaib

        Arguments:
            vector : numpy.ndarray
        """
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        out = DenseFourIndex(nacto, nactv, nacto, nactv, label=label)
        tmp = out.new()
        for ivec, (i, a, j, b) in enumerate(
            self.get_symmetry_unique_indices()
        ):
            tmp.set_element(i, a, j, b, vector.get_element(ivec), symmetry=1)
        out.iadd(tmp)
        out.iadd_transpose((2, 3, 0, 1), other=tmp)
        out.iadd_transpose((0, 3, 2, 1), other=tmp, factor=-1)
        out.iadd_transpose((2, 1, 0, 3), other=tmp, factor=-1)
        return out

    @property
    def dimension(self) -> int:
        """The number of unknowns (total number of excited states incl. ground
        state) for this EOM-CC flavor. Variable used by the Davidson module.
        """
        return int(
            binom(self.occ_model.nacto[0], 2)
            * binom(self.occ_model.nactv[0], 2)
        )

    def get_index_iajb(self, index: int) -> tuple[int, ...]:
        """Return hole-particle-hole-particle indices from composite index of CI vector

        Args:
            index (int): The composite index to be resolved

        Returns:
            tuple[int, ...]: hole-particle-hole-particle indices
        """
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]

        indices_o = np.triu_indices(nacto, 1)
        indices_v = np.triu_indices(nactv, 1)
        mask = np.zeros((nacto, nactv, nacto, nactv), dtype=bool)
        for i, j in zip(indices_o[0], indices_o[1]):
            mask[i, indices_v[0], j, indices_v[1]] = True
        # return mask for which i<j and a<b
        ind = np.where(mask)
        i, a, j, b = (
            ind[0][index],
            ind[1][index],
            ind[2][index],
            ind[3][index],
        )
        return i, a, j, b

    def print_ci_vector(self, ci_dict: OrderedDict) -> None:
        """Print eigenvectors with 4 unpaired electrons (S_z = 2.0)

        Args:
            ci_dict (OrderedDict): composite index as key, CI vector as value
        """
        ncore, nacto = self.occ_model.ncore[0], self.occ_model.nacto[0]
        nocc = ncore + nacto
        # Loop over all composite indices above threshold
        for ind, ci in ci_dict.items():
            i, a, j, b = self.get_index_iajb(ind)
            log(
                f"{'r_iAjB':>17}:   ({i + ncore + 1: 4},{a + nocc + 1: 3},{j + ncore + 1: 3},"
                f"{b + nocc + 1: 3})   {ci: 1.5f}"
            )

    def print_weights(self, e_vec_j: NDArray[np.float64]) -> None:
        """Print weights of R operators with 4 unpaired electrons (S_z = 2.0)

        Args:
            e_vec_j (np.ndarray): The eigenvector array whose weights will be printed.
        """
        w_iAjB = np.dot(e_vec_j, e_vec_j)

        log(f"{'weight(r_iAjB)':>17}: {w_iAjB: 1.5f}")

    def set_hamiltonian(self, ham_1_ao, ham_2_ao, mos):
        """Saves Hamiltonian terms in cache."""
        raise NotImplementedError

    def compute_h_diag(self, *args):
        """Used by Davidson module for pre-conditioning."""
        raise NotImplementedError

    def build_subspace_hamiltonian(self, bvector, hdiag, *args):
        """
        Used by Davidson module to construct subspace Hamiltonian. Includes all
        terms that are similar for all EOM-LCC flavours. The doubles contributions
        do not include any permutations due to non-equivalent lines.
        """
        raise NotImplementedError
