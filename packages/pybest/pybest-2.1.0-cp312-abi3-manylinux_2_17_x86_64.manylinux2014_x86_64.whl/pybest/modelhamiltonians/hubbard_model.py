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

"""The Hubbard model Hamiltonian"""

from pybest.linalg import DenseFourIndex, DenseTwoIndex
from pybest.modelhamiltonians.huckel_model import Huckel


class Hubbard(Huckel):
    """This class performs Tight-Binding and Hartree-Fock calculations for the extended Hückel model Hamiltonian, incorporating the Hubbard interaction for correlated systems."""

    acronym = "Hubbard"
    long_name = "Hubbard Model Hamiltonian"
    comment = ""

    def tight_binding_model(self) -> DenseTwoIndex:
        """Tight-binding model based on the Hubbard Hamiltonian"""
        u = self.parameters.get("u")
        result = Huckel.compute_one_body(self)
        # u/2 because of the mean field approximation.
        result.assign_diagonal(u / 2)

        return result

    def compute_one_body(self) -> DenseTwoIndex:
        """Calculate the one-body term of the Hubbard Hamiltonian"""
        if self.xyz_file:
            return Huckel.compute_one_body(self)
        # If no XYZ file is provided, we assume the 1D Hubbard model.
        # (1D lattice with local sites)
        hopping = self.parameters.get("hopping")
        result = self.lf.create_two_index(label="kin")
        n = self.lf.default_nbasis
        for i in range(n - 1):
            result.set_element(i, i + 1, hopping, 2)
        if self.pbc and n > 2:
            result.set_element(n - 1, 0, hopping, 2)
        return result

    def compute_two_body(self) -> DenseFourIndex:
        """Calculate the two-body term of the of the Hubbard Hamiltonian"""
        u = self.parameters.get("u")
        result = Huckel.compute_two_body(self)

        for i in range(self.denself.default_nbasis):
            result.set_element(i, i, i, i, u)

        return result
