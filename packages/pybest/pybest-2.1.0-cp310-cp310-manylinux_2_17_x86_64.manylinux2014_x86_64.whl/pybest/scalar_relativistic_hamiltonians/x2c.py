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

#
# Detailed changelog:
#
# 2025-02-27: Implementation and integration into the class structure of Scalar Relativistic Hamiltonians (Kacper Cieslak)
#
from __future__ import annotations

from pybest.constants import lightspeed
from pybest.gbasis.gobasis import get_tform_u2c
from pybest.linalg import DenseOneIndex, DenseTwoIndex
from pybest.log import timer

from .scalar_relativistic_base import ScalarRelativisticBase


class X2C(ScalarRelativisticBase):
    """Class implementing the eXact 2-Component (X2C) scalar relativistic Hamiltonian."""

    @timer.with_section("Ints: X2C")
    def compute(self) -> DenseTwoIndex:
        """Compute X2C Hamiltonian

        Returns:
            DenseOneIndex: matrix Hamiltonian
        """
        # Get kin, V, and pVp integrals in r-representation
        V = self.nuc
        pVp = self.pVp

        # Get Transformation matrices: to diagonal p2-representation and back
        u_ort = self.u_ort
        u_back = self.u_back
        kin = self.e_p_2

        # V and pVp are in diagonal p2-represenation
        V.itransform(u_ort)
        pVp.itransform(u_ort)

        # assemble H matrix
        h_matrix = self.assemble_x2c_h_matrix(V, pVp, kin)
        # diagonalize the H matrix
        eigvals, eigvecs = h_matrix.diagonalize(eigvec=True, use_eigh=True)

        # Sort eigen vectors
        eigvecs.sort(eigvals)

        eigvecs_nbasis = eigvecs.nbasis
        eigvecs_nbasis_half = int(eigvecs_nbasis // 2)

        # Compute Y_+ = V21 * V11^-1
        v11 = eigvecs.copy(0, eigvecs_nbasis_half, 0, eigvecs_nbasis_half)
        v21 = eigvecs.copy(
            eigvecs_nbasis_half, eigvecs_nbasis, 0, eigvecs_nbasis_half
        )
        v11_inv = v11.inverse()

        y_plus: DenseTwoIndex = v21.contract("ab,bc->ac", v11_inv)

        # Compute Omega_plus = (1 + Y_+^T * Y_+) ^ -0.5
        y_plus_t = y_plus.copy(transpose=True)
        y_t_y = y_plus_t.contract("ab,bc->ac", y_plus)
        identity = DenseTwoIndex(y_t_y.nbasis, label="identity")
        identity.assign_diagonal(1.0)
        y_t_y.iadd(identity)

        omega_plus = y_t_y.sqrt().inverse()

        h_plus = self.compute_h_plus(h_matrix, y_plus, omega_plus)

        h_plus.itransform(u_back, transpose=True)

        # Transform to contracted basis set
        output = DenseTwoIndex(self.basis.nbasis, label="x2c")

        tform_matrix = get_tform_u2c(self.basis)
        output.iadd_transform(h_plus, tform_matrix, transpose=True)

        return output

    @staticmethod
    def assemble_x2c_h_matrix(
        nuc: DenseTwoIndex,
        pvp: DenseTwoIndex,
        p2: DenseOneIndex,
    ) -> DenseTwoIndex:
        """Assemble the X2C Hamiltonian matrix.

        Args:
            nuc: DenseTwoIndex for the H11 block
            pvp: DenseTwoIndex for the H22 block
            p2: DenseOneIndex for the kinetic energy

        Returns:
            DenseTwoIndex: The constructed H matrix
        """
        p = p2.sqrt()

        c_p = pvp.new()
        c_p_d = p.copy()
        c_p_d.iscale(lightspeed)
        c_p.iadd_diagonal(c_p_d)

        # Compute H22 = 1/p * pVp * 1/p - 2c^2
        p_inv = p.inverse()
        h22 = p_inv.contract("a,ab,b->ab", pvp, p_inv)
        h22.iadd_diagonal(-2.0 * pow(lightspeed, 2))  # -2c^2

        h_nbasis: int = nuc.nbasis * 2
        h_nbasis_half: int = int(nuc.nbasis)
        h_matrix = DenseTwoIndex(h_nbasis, h_nbasis, label="h_matrix")
        # assign blocks
        h_matrix.assign(
            nuc, begin0=0, end0=h_nbasis_half, begin1=0, end1=h_nbasis_half
        )
        h_matrix.assign(
            c_p,
            begin0=0,
            end0=h_nbasis_half,
            begin1=h_nbasis_half,
            end1=h_nbasis,
        )
        h_matrix.assign(
            c_p,
            begin0=h_nbasis_half,
            end0=h_nbasis,
            begin1=0,
            end1=h_nbasis_half,
        )
        h_matrix.assign(
            h22,
            begin0=h_nbasis_half,
            end0=h_nbasis,
            begin1=h_nbasis_half,
            end1=h_nbasis,
        )

        return h_matrix

    @staticmethod
    def compute_h_plus(
        h_matrix: DenseTwoIndex,
        y_plus: DenseTwoIndex,
        omega_plus: DenseTwoIndex,
    ) -> DenseTwoIndex:
        """Compute h_+.

        h_+ = omega_plus * (H11 + H12 * Y_+ +
                                    Y_+^t * H21 + Y_+^t * H22 * Y_+) * omega_plus

        Args:
            h_matrix (DenseTwoIndex): the H matrix
            y_plus (DenseTwoIndex): the Y_+ matrix
            omega_plus (DenseTwoIndex): the Omega_+ matrix

        Returns:
            DenseTwoIndex: The h_+ matrix hamiltonian
        """
        y_plus_t = y_plus.copy(transpose=True)

        h_nbasis = h_matrix.nbasis
        h_nbasis_half = int(h_nbasis // 2)

        h11 = h_matrix.copy(0, h_nbasis_half, 0, h_nbasis_half)
        h12 = h_matrix.copy(0, h_nbasis_half, h_nbasis_half, h_nbasis)
        h21 = h_matrix.copy(h_nbasis_half, h_nbasis, 0, h_nbasis_half)
        h22 = h_matrix.copy(h_nbasis_half, h_nbasis, h_nbasis_half, h_nbasis)

        # compute sum = H11
        inner_sum = h11.copy()

        # add H12 * Y_+
        inner_sum.iadd(h12.contract("ab,bc->ac", y_plus))

        # add Y_+^t * H21
        inner_sum.iadd(y_plus_t.contract("ab,bc->ac", h21))

        # add Y_+^t * H22 * Y_+
        inner_sum.iadd(y_plus_t.contract("ab,bc,cd->ad", h22, y_plus))

        # construct matrix hamiltonian

        h_plus = omega_plus.contract("ab,bc,cd->ad", inner_sum, omega_plus)

        return h_plus
