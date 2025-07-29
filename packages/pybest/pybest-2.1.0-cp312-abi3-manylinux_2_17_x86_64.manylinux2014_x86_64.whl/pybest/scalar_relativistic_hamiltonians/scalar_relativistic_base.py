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
# 2025-02-27: Scalar Relativistic Hamiltonians class structure (Kacper Cieslak)
#

from __future__ import annotations

from abc import ABC, abstractmethod

from pybest.gbasis import Basis, ExternalCharges
from pybest.gbasis.dense_ints import (
    compute_kinetic,
    compute_nuclear,
    compute_overlap,
    compute_point_charges,
    compute_ppcp,
    compute_pvp,
)
from pybest.linalg import DenseOneIndex, DenseTwoIndex
from pybest.log import log


class ScalarRelativisticBase(ABC):
    """Base class for scalar relativistic Hamiltonians

    The following integrals are supported:
    *pVp (standard for DKH and X2C)
    *pPCp (needed for external point charges with X2C and DKH Hamiltonians)
    """

    def __init__(
        self,
        basis: Basis,
        charges: ExternalCharges | None = None,
        order: int | None = None,
    ) -> None:
        """Instance initialize method

        Args:
            basis (Basis): Basis set information
            charges (ExternalCharges | None): External charges
            order (int): Order of the DKH transformation
        """
        self._basis = basis
        self._charges = charges

        integrals = self.compute_components(basis, charges)

        self._nuc = integrals["nuc"]
        self._pVp = integrals["pvp"]
        self._olp = integrals["olp"]
        self._kin = integrals["kin"]

        self._u_ort, self._u_back, self._e_p_2 = (
            self.get_transformation_matrices()
        )

        if isinstance(order, int) and order > 0:
            self._order = order

    @property
    def basis(self) -> Basis:
        """Basis set information"""
        return self._basis

    @property
    def charges(self) -> ExternalCharges | None:
        """External charges"""
        return self._charges

    @property
    def nuc(self) -> DenseTwoIndex:
        """Nuclear integral"""
        return self._nuc

    @property
    def pVp(self) -> DenseTwoIndex:
        """The pVp integral"""
        return self._pVp

    @property
    def olp(self) -> DenseTwoIndex:
        """Overlap integral"""
        return self._olp

    @property
    def kin(self) -> DenseTwoIndex:
        """Kinetic integral"""
        return self._kin

    @property
    def u_ort(self) -> DenseTwoIndex:
        """Transformation to orthonormal basis"""
        return self._u_ort

    @property
    def u_back(self) -> DenseTwoIndex:
        """Transformation from orthonormal basis"""
        return self._u_back

    @property
    def e_p_2(self) -> DenseOneIndex:
        """EigenValues from p^2 diagonalisation"""
        return self._e_p_2

    @property
    def order(self) -> int:
        """The order of the series expansion or transformation"""
        return self._order

    def compute_components(
        self,
        basis: Basis,
        charges: ExternalCharges | None = None,
        s_int: bool = True,
        t_int: bool = True,
        v_int: bool = True,
        pvp_int: bool = True,
    ) -> dict[str, DenseTwoIndex]:
        """Compute component integrals

        Produces uncontracted integrals.

        Args:
            basis: Basis set information
            charges: External charges (ExternalCharges | None). Defaults to None.
            s_int (bool): S integral flag. Defaults to True.
            t_int (bool): T integral flag. Defaults to True.
            v_int (bool): V integral flag. Defaults to True.
            pvp_int (bool): pVp integral flag. Defaults to True.

        Returns:
          dict[
            str,: integral key
            DenseTwoIndex: integral object
            ]
        """
        output = {}
        if s_int:
            olp = compute_overlap(basis, uncontract=True)
            output.update({"olp": olp})
        if t_int:
            kin = compute_kinetic(basis, uncontract=True)
            output.update({"kin": kin})
        if v_int:
            nuc = compute_nuclear(basis, uncontract=True)
            if charges is not None:
                log(
                    "Correcting for picture changes due to presence of external charges"
                )
                pc = compute_point_charges(basis, charges, uncontract=True)
                nuc.iadd(pc)
            output.update({"nuc": nuc})
        if pvp_int:
            pvp = compute_pvp(basis, uncontract=True)
            if charges is not None:
                ppcp = compute_ppcp(basis, charges, uncontract=True)
                pvp.iadd(ppcp)
            output.update({"pvp": pvp})
        return output

    def get_transformation_matrices(
        self,
    ) -> tuple[DenseTwoIndex, DenseTwoIndex, DenseOneIndex]:
        """Obtain transformation matrices that diagonalize p^2.

        The final basis is orthonormal.

        Returns:
          tuple[
            DenseTwoIndex,: transformation
            DenseTwoIndex,: back-transformation
            DenseOneIndex : eigenvalues
            ]
        """
        olp = self.olp
        p_2 = self.kin
        #
        # Transform to orthonormal basis diagonalising p^2
        #
        e_olp, u_olp = olp.diagonalize(eigvec=True, use_eigh=True)
        e_olp_inv_sqrt = (e_olp.inverse()).sqrt()
        # Diagonalize p^2
        # p = 2 kin
        p_2.iscale(2.0)
        p_2.itransform(u_olp.contract("ab,b->ab", e_olp_inv_sqrt, out=None))
        e_p_2, u_p_2 = p_2.diagonalize(eigvec=True, use_eigh=True)
        # Get transformation matrices
        u_ort = u_olp.contract("ab,b,bc->ac", e_olp_inv_sqrt, u_p_2, out=None)
        u_back = u_olp.contract("ab,b,bc->ac", e_olp.sqrt(), u_p_2, out=None)

        return u_ort, u_back, e_p_2

    @abstractmethod
    def compute(self) -> DenseTwoIndex:
        """Compute scalar relativistic Hamiltonian

        Returns:
            DanseTwoIndex: The matrix Hamiltonian
        """

    def __call__(self) -> DenseTwoIndex:
        return self.compute()
