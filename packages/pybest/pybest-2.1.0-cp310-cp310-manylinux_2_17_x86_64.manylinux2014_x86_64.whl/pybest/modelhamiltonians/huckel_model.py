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
# This module has been written and updated by Zahra Karimi in 10/2024 (see CHANGELOG).

"""The Huckel model Hamiltonian"""

from pybest.linalg import DenseFourIndex, DenseTwoIndex

from .physical_model_base import PhysModBase


class Huckel(PhysModBase):
    """Hückel model Hamiltonian incorporating tight-binding and Hartree-Fock methods for electronic structure calculations."""

    acronym = "Huckel"
    long_name = "Hückel model Hamiltonian"
    comment = ""

    @property
    def pbc(self):
        """The periodic boundary conditions"""
        return self._pbc

    def tight_binding_model(self) -> DenseTwoIndex:
        """Tight-binding Hamiltonian based on the Hückel model"""
        result = self.compute_one_body()
        return result

    def compute_one_body(self) -> DenseTwoIndex:
        """Calculate the one-body term of the Hückel Model Hamiltonian."""
        on_site = self.parameters.get("on_site")
        hopping = self.parameters.get("hopping")

        result = self.lf.create_two_index(label="kin")

        # Add the onsite interaction as a diagonal term
        result.assign_diagonal(on_site)
        adj_mat, _ = self.generate_adjacency_matrix()
        # Add the hopping term using the adjacency matrix
        result.iadd(adj_mat, factor=hopping)

        return result

    def compute_two_body(self) -> DenseFourIndex:
        """This represents a two-body term in the Hamiltonian. Specifically, for the Hückel model, it is a 2D zero matrix required for Hartree-Fock calculations."""
        return self.denself.create_four_index(label="eri")
