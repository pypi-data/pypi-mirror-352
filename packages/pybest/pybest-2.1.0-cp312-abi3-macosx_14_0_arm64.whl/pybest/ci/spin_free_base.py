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
from functools import partial

import numpy as np

from pybest.auxmat import get_fock_matrix
from pybest.exceptions import ArgumentError
from pybest.linalg import CholeskyFourIndex
from pybest.log import log
from pybest.utility import check_options

from .rci_base import RCI


class SpinFree(RCI, ABC):
    """Spin-free base class. Contains all required methods to diagonalize the
    Hamiltonian using the spin-free basis.
    """

    cvs = False

    def __init__(self, lf, occ_model, pairs=False):
        log.cite("the pCCD-CI methods", "nowak2023")
        super().__init__(lf, occ_model)
        self.csf = False
        self._pairs = pairs
        self.dimension = self.acronym

    @property
    def pairs(self):
        """Boolean argument.
        True: include the pairs excitation
        False: exclude the pairs excitations
        """
        return self._pairs

    @pairs.setter
    def pairs(self, new):
        if not isinstance(new, bool):
            raise ArgumentError(
                "Unkown type for keyword pairs. Boolean type required."
            )
        self._pairs = new

    @RCI.dimension.setter
    def dimension(self, new=None):
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        if new is not None:
            self._dimension = SpinFree.set_dimension(
                new, nacto, nactv, pairs=self.pairs
            )

    @RCI.nroot.setter
    def nroot(self, new):
        self._nroot = new

    @RCI.davidson.setter
    def davidson(self, new):
        if not isinstance(new, bool):
            raise ArgumentError(
                "Unkown type for keyword davidson. Boolean type required."
            )
        self._davidson = new

    def calculate_exact_hamiltonian(self):
        """Calculate the exact Hamiltonian of the pCCD-CIS model."""
        raise NotImplementedError

    @abstractmethod
    def build_subspace_hamiltonian(self, bvector, hamiltonian, *args):
        """Construction of sigma vector."""

    @abstractmethod
    def compute_h_diag(self, *arg):
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

    @staticmethod
    def set_dimension(acronym, nacto, nactv, pairs=False):
        """Sets the dimension/number of unknowns of the chosen CI flavour."""
        check_options(
            "acronym",
            acronym,
            "pCCD-CIS",
            "pCCD-CID",
            "pCCD-CISD",
        )
        if acronym == "pCCD-CIS":
            return nacto * nactv + 1

        if acronym == "pCCD-CID":
            dim = (
                (nacto * nacto * nactv * nactv + nacto * nactv) // 2
                - nacto * nactv
                + 1
            )
            if pairs:
                return dim + nacto * nactv
            return dim
        if acronym == "pCCD-CISD":
            dim = (nacto * nacto * nactv * nactv + nacto * nactv) // 2 + 1
            if pairs:
                return dim + nacto * nactv
            return dim
        raise NotImplementedError

    def set_hamiltonian(self, mo1, mo2):
        """Compute auxiliary matrices.

        **Arguments:**

        mo1, mo2
            One- and two-electron integrals (some Hamiltonian matrix
            elements) in the MO basis.
        """
        self.clear_cache()
        nacto = self.occ_model.nacto[0]
        nact = self.occ_model.nact[0]
        #
        # 1) Fock matrix: fpq
        #
        fock = self.init_cache("fock", nact, nact)
        get_fock_matrix(fock, mo1, mo2, nacto)

        #
        # 4-Index slices of ERI
        #
        def alloc(arr, block):
            """Determines alloc keyword argument for init_cache method."""
            # We keep one whole CholeskyFourIndex to rule them all.
            # Non-redundant blocks are accessed as views.
            if isinstance(arr, CholeskyFourIndex):
                return (partial(arr.view, **self.get_range(block)),)
            # But we store only non-redundant blocks of DenseFourIndex
            return (partial(arr.copy, **self.get_range(block)),)

        #
        # Get blocks
        #
        slices = ["ovvo", "ovov"]
        for slice_ in slices:
            self.init_cache(f"g{slice_}", alloc=alloc(mo2, slice_))

        if self.acronym in ["pCCD-CIS", "pCCD-CID", "pCCD-CISD"]:
            #
            # Get blocks
            #
            slices = ["ooov", "oooo", "ovvv", "vvvv"]
            for slice_ in slices:
                self.init_cache(f"g{slice_}", alloc=alloc(mo2, slice_))

            # 6) temporary matrix: gppqq
            gppqq = self.init_cache("gppqq", nact, nact)
            mo2.contract("aabb->ab", gppqq)

    def get_index_s(self, index):
        """Get index for single excitation."""
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        b = index % nactv
        j = ((index - b) / nactv) % nacto
        return int(j), int(b)

    def get_index_d(self, index):
        """Get the unique indices of some doubly excited CSF. Returns the set of
        active orbital indices without adding shift related to the frozen core
        orbitals.

        **Arguments:**

        *index:
            (int) The number that encodes a doubly excited spin-free determinant
            contributing to the CI solution.
        """
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        k = 1
        if self.pairs:
            k = 0
        if nacto < 2:
            ind = np.triu_indices(nactv, k)
            i = 1
            a = ind[0][index] + 1 + nacto
            j = i
            b = ind[1][index] + 1 + nacto
            return i, a, j, b

        mask = np.ones((nacto, nactv, nacto, nactv))
        mask = np.reshape(mask, (nacto * nactv, nacto * nactv))
        mask = np.triu(mask, k)
        mask = np.reshape(mask, (nacto, nactv, nacto, nactv))

        ind = np.where(mask)
        i = ind[0][index] + 1
        a = ind[1][index] + 1 + nacto
        j = ind[2][index] + 1
        b = ind[3][index] + 1 + nacto

        return i, a, j, b
