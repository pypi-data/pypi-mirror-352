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

"""The PPP model Hamiltonian"""

import numpy as np

from pybest.linalg import DenseFourIndex, DenseTwoIndex
from pybest.modelhamiltonians.hubbard_model import Hubbard
from pybest.modelhamiltonians.huckel_model import Huckel


class PPP(Hubbard):
    """The Pariser-Parr-Pople (PPP) model for π-conjugated systems.

    This class extends the Hubbard model by including long-range electron-electron interactions (V-term).
    The model can also optionally include the on-site electron repulsion (U-term) depending on the
    `hubbard` keyword.

    Attributes:
        hubbard (bool): If True, the model includes both the U-term (on-site Coulomb repulsion)
                        and the V-term (long-range Coulomb interactions), making it a full PPP model.
    If False, only the V-term is included, reducing it to a tight-binding + V-term model.
    """

    acronym = "PPP"
    long_name = "PPP Model Hamiltonian"
    comment = ""

    def tight_binding_model(self) -> DenseTwoIndex:
        """Tight-binding model based on the Hückel Hamiltonian"""
        result = self.lf.create_two_index(label="kin")
        huckel = Huckel.compute_one_body(self)
        u = self.parameters.get("u")
        add_hubbard = self.parameters.get("hubbard")

        _, dist_mat = self.generate_adjacency_matrix()
        intracting_matrix = self.lf.create_two_index()

        # tight-binding + V term = ppp-model.
        # V term obtained by Ohno interpolating formula.
        # Refrence: J. A. Vergés, E. SanFabián, G. Chiappe, and E. Louis,
        # "Fit of Pariser-Parr-Pople and Hubbard model Hamiltonians to charge and spin states of polycyclic aromatic hydrocarbons"
        # Phys. Rev. B, vol. 81, p. 085120, 2010
        # H_{PPP} = -∑_{i,j} t_{ij}(c^{†}_{i}c_{j} + c^{†}_{j}c_{i})
        # + U ∑_i n_{i↑}n_{i↓}
        # + ∑_{i<j} V_{ij}(n_i-1)(n_j-1).
        # V_{|i-j|} = U * (1 + (U / (e^2 / R_{ij}))^2)^{-1/2}
        for i in range(self.denself.default_nbasis):
            # if hamiltonian is: tight-binding + V term + U term.
            if add_hubbard:
                # The 1/2 prefactor in u/2 prevents double-counting the on-site Hubbard interaction between opposite spins.
                result.assign_diagonal(u / 2)
            for j in range(self.denself.default_nbasis):
                if i != j:
                    v_ij = 1 / (
                        np.sqrt(
                            1
                            + pow(
                                u * dist_mat.array[i, j] / pow(1.6 * 1e-19, 2),
                                2,
                            )
                        )
                    )
                    intracting_matrix.set_element(i, j, v_ij, 2)

        result.iadd(intracting_matrix, factor=u / 2)
        result.iadd(huckel)

        return result

    def compute_one_body(self) -> DenseTwoIndex:
        """Calculate the one-body term of the PPP model Hamiltonian"""
        result = Hubbard.compute_one_body(self)
        return result

    def compute_two_body(self) -> DenseFourIndex:
        """Calculate the two-body term of the PPP model Hamiltonian"""
        u = self.parameters.get("u")
        u_p = self.parameters.get("u_p")
        k = self.parameters.get("k")
        add_hubbard = self.parameters.get("hubbard")
        result = self.denself.create_four_index(label="eri")
        intracting_matrix = self.denself.create_four_index()
        _, dist_mat = self.generate_adjacency_matrix()
        k_ij = self.lf.create_two_index()
        v_ij = self.lf.create_two_index()
        k_ij.assign(k)

        # tight-binding + V term = ppp-model.
        # V term obtained by Ohno formula.

        # refrence: P. Bhattacharyya, D. K. Rai, and A. Shukla,
        # Pariser-Parr-Pople model based configuration-interaction study of linear optical absorption in lower-symmetry polycyclic aromatic hydrocarbon molecules,”
        # J. Phys. Chem. C, vol. 124, 2020.
        # V_{ij} = U / k_{i,j} * (1 + 0.6117R_{ij}^2)^{1/2}
        for i in range(self.denself.default_nbasis):
            for j in range(self.denself.default_nbasis):
                if i != j and k_ij.array[i, j]:
                    v_ij.array[i, j] = 1 / (
                        k_ij.array[i, j]
                        * np.sqrt(1 + 0.6117 * pow(dist_mat.array[i, j], 2))
                    )

                    intracting_matrix.set_element(
                        j, j, i, i, v_ij.array[i, j], 2
                    )
        hubbard_term = Hubbard.compute_two_body(self)
        if add_hubbard:
            result.iadd(hubbard_term)

        result.iadd(intracting_matrix, u_p)
        self.checkpoint.update("v_term", u * v_ij.array)
        return result
