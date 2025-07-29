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
# This file has been written by Dariusz Kedziera
#
# Detailed changes (see also CHANGELOG):
# 2023-01-16: Additional transformations, ppcp, for point charges (P.Tecmer)
# 2025-02-27: Implementation into the class structure of Scalar Relativistic Hamiltonians (Kacper Cieslak)
#

from __future__ import annotations

from pybest.constants import alpha
from pybest.gbasis import Basis, ExternalCharges
from pybest.gbasis.gobasis import get_tform_u2c
from pybest.linalg import DenseOneIndex, DenseTwoIndex
from pybest.log import timer

from .scalar_relativistic_base import ScalarRelativisticBase


class DKHN(ScalarRelativisticBase):
    """Douglas-Kroll-Hess transformation"""

    def __init__(
        self,
        basis: Basis,
        charges: ExternalCharges | None = None,
        order: int | None = 2,
    ) -> None:
        """Modified instance initialize method

        Args:
            basis (Basis): Basis set information
            charges (ExternalCharges | None): External Charges. Defaults to None.
            order (int): Order of the DKH transformation. Defaults to 2.

        Raises:
            ValueError: if order is not 1 or 2.
        """
        if isinstance(order, int) is not False and order < 1 and order > 2:
            raise ValueError("Order must be an integer greater than 0.")
        super().__init__(basis, charges, order)

    @timer.with_section("Ints: DKHN")
    def compute(self) -> DenseTwoIndex:
        """Compute DKH Hamiltonian.

        Returns:
            DenseTwoIndex -- matrix Hamiltonian
        """
        #
        # Get olp (s), p_2 (t), nuc (v), and pvp integrals
        #
        nuc = self.nuc
        pvp = self.pVp
        #
        # Transform to orthonormal basis diagonalising p^2
        #
        u_ort = self.u_ort
        u_back = self.u_back
        e_p_2 = self.e_p_2
        #
        # Transform nuc (v) and pvp ints to p^2 basis set
        #
        nuc.itransform(u_ort)
        pvp.itransform(u_ort)
        #
        # Compute all vectors for DKH transformation
        #
        vectors = self.get_dkh_vectors(e_p_2)
        #
        # The DKH Hamiltonian
        #
        # DKH1
        # E1 = T_p_at_diag + A_k ( V +1/c^2 b_k pVp b_k ) A_k
        #
        dkh = self.get_dkh_order_1(nuc, pvp, **vectors)
        #
        # DKH2
        # E2 = -0.5 ( Y + Y^T )
        #
        if self.order >= 2:
            dkh.iadd(self.get_dkh_order_2(nuc, pvp, **vectors))
        #
        # Back-transformation to r representation
        #
        dkh.itransform(u_back, transpose=True)
        #
        # Transform to contracted basis set
        #
        # create new output array
        output = DenseTwoIndex(self.basis.nbasis, label="dkh")
        # get transformation matrix
        tform_matrix = get_tform_u2c(self.basis)
        output.iadd_transform(dkh, tform_matrix, transpose=True)

        return output

    @staticmethod
    def get_dkh_vectors(e_p_2: DenseOneIndex) -> dict[str, DenseOneIndex]:
        """Compute all vectors required for DKH transformation.

        Args:
            e_p_2 (DenseOneIndex): Eigenvalues from p^2 diagonalisation

        Returns:
            dict[
                str,: vector key
                DenseOneIndex: dkh vector
                ]
        """
        #
        # Vector e_p
        # e_p = sqrt( 1+(p_2/c)^2 )
        #
        e_p = e_p_2.copy()
        e_p.iscale(alpha**2)
        e_p.iadd(1.0)
        e_p.isqrt()
        #
        # Vector a_k
        # A_k = sqrt( (1+e_k)/(2 e_k) )
        #
        A_k = e_p.copy()
        A_k.iadd(1.0)
        A_k.idivide(e_p, 0.5)
        A_k.isqrt()
        #
        # Vector b_k
        # b_k = 1/(1+e_k)
        #
        B_k = e_p.copy()
        B_k.iadd(1.0)
        B_k = B_k.inverse()

        return {"e_p": e_p, "e_p_2": e_p_2, "a_k": A_k, "b_k": B_k}

    @staticmethod
    def get_dkh_order_1(
        nuc: DenseTwoIndex,
        pvp: DenseTwoIndex,
        **vectors: dict[str, DenseOneIndex],
    ) -> DenseTwoIndex:
        """The 1st-order DKH Hamiltonian.

        Args:
            nuc (DenseTwoIndex): the nuclear repulsion integrals
            pvp (DenseTwoIndex): the pVp integrals
            vectors (dict[str,DenseOneIndex): Contains a dictionary of (OneIndex) instances defined in get_dkh_vectors
        Returns:
            DenseTwoIndex: 1st-order DKH Hamiltonian matrix
        """
        e_p_2 = vectors.get("e_p_2", None)
        b_k = vectors.get("b_k", None)
        a_k = vectors.get("a_k", None)
        #
        # A_k ( V +1/c^2 b_k pVp b_k ) A_k
        #
        # Compute components
        # tmp = 1/c^2 b_k pVp b_k
        tmp = b_k.contract("a,ab,b->ab", pvp, b_k, factor=alpha**2, out=None)
        # V + tmp = (V + 1/c^2 b_k pVp b_k)
        tmp.iadd(nuc)
        # A_k ( V +1/c^2 b_k pVp b_k ) A_k
        e_1 = a_k.contract("a,ab,b->ab", tmp, a_k, out=None)
        #
        # E1 = T_p_at_diag + e_1
        # T_p_at_diag = t_p = c^2(e_k-1) = p_2 * b_k
        t_p = e_p_2.new()
        e_p_2.mult(b_k, out=t_p)
        # Final E1 matrix
        e_1.iadd_diagonal(t_p)

        return e_1

    @staticmethod
    def get_dkh_order_2(
        nuc: DenseTwoIndex,
        pvp: DenseTwoIndex,
        **vectors: dict[str, DenseOneIndex],
    ) -> DenseTwoIndex:
        """The 2nd-order DKH Hamiltonian.

        Args:
            nuc (DenseTwoIndex): the nuclear repulsion integrals
            pvp (DenseTwoIndex): the pVp integrals
            vectors (dict[str, DenseOneIndex]): Contains a dictionary of instances defined in get_dkh_vectors
        Returns:
            DenseTwoIndex: The 2nd-order DKH Hamiltonian Matrix.
        """
        e_p = vectors.get("e_p", None)
        e_p_2 = vectors.get("e_p_2", None)
        b_k = vectors.get("b_k", None)
        a_k = vectors.get("a_k", None)
        #
        # E2 = 0.5 ( Y + Y^T )
        # Y = - W p^2 O^T
        # O = 1/c A (1/p2 pVp b_k - b_k V) A
        # W(i,j) = 1/c^2 O(j,i) / (ep(i) +ep(j))
        #
        # part: 1/p2 pVp b_k
        tmp = (e_p_2.inverse()).contract("a,ab,b->ab", pvp, b_k)
        # part: - b_k V
        b_k.contract("a,ab->ab", nuc, tmp, factor=-1.0)
        # part: A_k tmp A_k
        o_1 = a_k.contract("a,ab,b->ab", tmp, a_k)
        o_1.iscale(alpha)
        # W
        w_1 = o_1.copy()
        w_1.itranspose()
        # denominator 1/(e_p(i) + e_p(j))
        tmp.clear()
        tmp.iadd(e_p, 1.0)
        tmp.iadd(e_p, 1.0, transpose=True)
        denominator = tmp.new()
        denominator.assign(1.0)
        denominator.idivide(tmp, factor=alpha**2)
        # Final W matrix:
        w_1.imul(denominator)
        #
        # Y = - W p^2 O^T
        #
        y_matrix = w_1.contract(
            "ab,b,bc->ac", e_p_2, o_1, out=None, factor=-1.0
        )
        #
        # E2 = -0.5 ( Y + Y^T )
        #
        e_2 = y_matrix.copy()
        e_2.iadd_t(y_matrix)
        e_2.iscale(-0.5)

        return e_2
