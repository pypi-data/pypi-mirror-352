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

"""
Variables used in this module:
 :ncore:     number of frozen core orbitals
 :nocc:      number of occupied orbitals in the principal configuration
 :nactc:     number of active core orbitals for the core-valence separation
             approximation (zero by default)
 :nacto:     number of active occupied orbitals in the principal configuration
 :nvirt:     number of virtual orbitals in the principal configuration
 :nactv:     number of active virtual orbitals in the principal configuration
 :nbasis:    total number of basis functions
 :nact:      total number of active orbitals (nactc+nacto+nactv)
 :e_ci:      eigenvalues of CI Hamiltonian (IOData container attribute)
 :civ:       eigenvectors of CI Hamiltonian (IOData container attribute)
 :t_p:       The pair coupled cluster amplitudes of pCCD

Indexing convention:
 :i,j,k,..:  occupied orbitals of principal configuration
 :a,b,c,..:  virtual orbitals of principal configuration
 :p,q,r,..:  any orbital in the principal configuration (occupied or virtual)

Intermediates:
 :<pq||rs>:  <pq|rs>-<pq|sr> (Coulomb and exchange terms of ERI)
 :fock:      h_pp + sum_i(2<pi|pi>-<pi|ip>) (the inactive Fock matrix)
"""

from abc import ABC, abstractmethod

import numpy as np

from pybest.utility import check_options


class CSF(ABC):
    """Configuration State Function (CSF) base class. Contains all required methods
    to diagonalize the Hamiltonian using SD basis.
    """

    @property
    def csf(self):
        """The dimension of the Hamiltonian matrix."""
        return True

    @property
    def dimension(self):
        """The dimension of the Hamiltonian matrix."""
        return self._dimension

    @dimension.setter
    @abstractmethod
    def dimension(self, new=None):
        raise NotImplementedError

    @abstractmethod
    def build_subspace_hamiltonian(self, bvector, hamiltonian, *args):
        """Construction of sigma vector."""

    @abstractmethod
    def compute_h_diag(self, *args):
        """The diagonal of the Hamiltonian."""

    def get_index_d_csf(self, index):
        """Get the unique indices of some doubly excited CSF. Returns the set of
        active orbital indices without adding shift related to the frozen core
        orbitals.

        **Arguments:**

        *index:
            (int) The number that indicates doubly excited CSF which
            is contributing in the CI solution.
        """
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        end_1 = nacto * nactv
        end_2 = end_1 + nacto * (nactv * (nactv - 1)) // 2
        end_3 = end_2 + nacto * (nacto - 1) // 2 * nactv
        end_4 = end_3 + (nacto * (nacto - 1) // 2 * nactv * (nactv - 1) // 2)
        if index < end_1:
            i = index // (nactv) + 1
            j = i
            a = index % nactv + nacto + 1
            b = a
            return i, a, j, b
        if index < end_2:
            index = index - end_1
            indices = np.where(CSF.get_mask_csf(self, "iab"))

        elif index < end_3:
            index = index - end_2
            indices = np.where(CSF.get_mask_csf(self, "iaj"))

        elif index < end_4:
            index = index - end_3
            indices = np.where(CSF.get_mask_csf(self, "iajb"))
        else:
            index = index - end_4
            indices = np.where(CSF.get_mask_csf(self, "iajb"))

        i, a, j, b = (
            indices[0][index],
            indices[1][index],
            indices[2][index],
            indices[3][index],
        )
        return (
            i + 1,
            a + 1 + nacto,
            j + 1,
            b + 1 + nacto,
        )

    def get_index_of_mask_csf(self, select):
        """Get the indices where the True values are assigned."""
        mask = self.get_mask_csf(select)
        indices = np.where(mask)
        return indices

    def get_mask_csf(self, select):
        """The function returns a 4-dimensional boolean np.array. True values
        are assigned to all non-redundant and symmetry-unique elements of the
        CI coefficient tensor for double excitations.
        """
        check_options(
            "select",
            select,
            "iab",
            "iaj",
            "iajb",
        )
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        mask = np.zeros((nacto, nactv, nacto, nactv), dtype=bool)

        if select in ["iab"]:
            indices_o = np.triu_indices(nacto, 0)
            indices_v = np.triu_indices(nactv, 1)

            for i in indices_o[0]:
                mask[i, indices_v[0], i, indices_v[1]] = True

        elif select in ["iaj"]:
            indices_o = np.triu_indices(nacto, 1)
            indices_v = np.triu_indices(nactv, 0)

            for a in indices_v[0]:
                mask[indices_o[0], a, indices_o[1], a] = True

        else:
            indices_o = np.triu_indices(nacto, 1)
            indices_v = np.triu_indices(nactv, 1)
            for i, j in zip(indices_o[0], indices_o[1]):
                mask[i, indices_v[0], j, indices_v[1]] = True
        return mask

    @staticmethod
    def set_dimension(acronym, nacto, nactv):
        """Sets the dimension/number of unknowns of the chosen CI flavour."""
        check_options(
            "acronym",
            acronym,
            "CIS",
            "CID",
            "CISD",
        )
        if acronym == "CIS":
            return nacto * nactv + 1

        if acronym == "CID":
            return (
                nacto * nactv
                + nacto * (nactv * (nactv - 1)) // 2
                + nacto * (nacto - 1) // 2 * nactv
                + nacto * (nacto - 1) * nactv * (nactv - 1) // 2
            ) + 1
        return (
            nacto * nactv
            + (
                nacto * nactv
                + nacto * (nactv * (nactv - 1)) // 2
                + nacto * (nacto - 1) // 2 * nactv
                + nacto * (nacto - 1) * nactv * (nactv - 1) // 2
            )
            + 1
        )
