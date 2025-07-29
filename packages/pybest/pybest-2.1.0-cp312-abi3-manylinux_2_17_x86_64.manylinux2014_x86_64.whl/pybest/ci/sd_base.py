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


class SD(ABC):
    """Slater Determinant (SD) base class. Contains all required methods
    to diagonalize the Hamiltonian using SD basis.
    """

    @property
    def dimension(self):
        """The dimension of the Hamiltonian matrix."""
        return self._dimension

    @dimension.setter
    @abstractmethod
    def dimension(self, new=None):
        raise NotImplementedError

    @property
    def csf(self):
        """The dimension of the Hamiltonian matrix."""
        return False

    @abstractmethod
    def build_subspace_hamiltonian(self, bvector, hamiltonian, *args):
        """Construction of sigma vector."""

    @abstractmethod
    def compute_h_diag(self, *args):
        """The diagonal of the Hamiltonian."""

    def get_mask(self):
        """The function returns a 4-dimensional boolean np.array. True values
        are assigned to all non-redundant and symmetry-unique elements of the
        CI coefficient tensor for double excitations.
        """
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        mask = np.zeros((nacto, nactv, nacto, nactv), dtype=bool)
        indices_o = np.triu_indices(nacto, 1)
        indices_v = np.triu_indices(nactv, 1)

        for i, j in zip(indices_o[0], indices_o[1]):
            mask[i, indices_v[0], j, indices_v[1]] = True
        return mask

    def get_index_of_mask(self):
        """Get the indices where the True values are assigned."""
        mask = self.get_mask()
        indices = np.where(mask)
        return indices

    def get_index_d(self, index):
        """Get the unique indices of some doubly excited SD. Returns the set of
        active orbital indices without adding shift related to the frozen core
        orbitals.

        **Arguments:**

        *index:
            (int) The number that indicates doubly excited SD which
            is contributing in the CI solution.
        """
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        # Case 1) C_iaJB:
        end_ab = nacto * nacto * nactv * nactv
        # Case 2) C_iajb:
        end_aa = ((nacto * (nacto - 1)) // 2) * ((nactv * (nactv - 1)) // 2)
        # 1) we store all i,a,j,b and we can simply use np's unravel_index build-in function
        if index < end_ab:
            (i, a, j, b) = np.unravel_index(
                index, (nacto, nactv, nacto, nactv)
            )
            i, a, j, b = (
                i + 1,
                a + 1 + nacto,
                j + 1,
                b + 1 + nacto,
            )
            return i, a, j, b
        # 2) This is more complicated, one possible way is to use a mask function:
        index = index - end_ab
        # 3) This is the same as case 2) but index has to be shifted by end_aa as well
        if index > end_aa:
            index = index - end_aa
        ind = np.where(self.get_mask())
        i, a, j, b = (
            ind[0][index],
            ind[1][index],
            ind[2][index],
            ind[3][index],
        )
        return (
            i + 1,
            a + 1 + nacto,
            j + 1,
            b + 1 + nacto,
        )

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
                nacto * nacto * nactv * nactv
                + ((nacto * (nacto - 1)) // 2)
                * ((nactv * (nactv - 1)) // 2)
                * 2
            ) + 1
        return (
            nacto * nactv * 2
            + (
                nacto * nacto * nactv * nactv
                + ((nacto * (nacto - 1)) // 2)
                * ((nactv * (nactv - 1)) // 2)
                * 2
            )
            + 1
        )
