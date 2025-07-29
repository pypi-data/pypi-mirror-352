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
"""Equation of Motion Coupled Cluster implementations of Coupled Cluster Singles
and Doubles (EOM-CCSD).

Child class of the REOMCCSDBase class.
"""

from __future__ import annotations

from functools import partial
from typing import Any

from pybest.linalg import CholeskyFourIndex
from pybest.linalg.base import FourIndex, OneIndex, TwoIndex
from pybest.log import timer

from .eom_ccsd_base import REOMCCSDBase


class REOMCCSD(REOMCCSDBase):
    """Perform an EOM-CCSD calculation.
    EOM-CCSD implementation which calls the Base class for flavor-specific
    operations. The core operations of the EOM-CCSD class do not differ from
    the Base class ones.
    """

    long_name = "Equation of Motion Coupled Cluster Singles and Doubles"
    acronym = "EOM-CCSD"
    reference = "CCSD"
    # NOTE: Change names of class attributes below (will it be useful with new
    # code structure?)
    singles_ref = True
    pairs_ref = False
    doubles_ref = True
    singles_ci = True
    pairs_ci = False
    doubles_ci = True

    @timer.with_section("EOMCCSD: H_diag")
    def compute_h_diag(self, *args: Any) -> OneIndex:
        """Used by Davidson module for pre-conditioning.

        Args:
            args (Any): required for Davidson module (not used here)
        """
        h_diag = self.lf.create_one_index(self.dimension, label="h_diag")
        #
        # Call base class method
        #
        h_diag_s, h_diag_d = REOMCCSDBase.compute_h_diag(self, *args)
        #
        # Get ranges
        #
        end_s = self.occ_model.nacto[0] * self.occ_model.nactv[0] + 1
        #
        # Assign only symmetry-unique elements
        #
        h_diag.assign(h_diag_s.ravel(), begin0=1, end0=end_s)
        h_diag.assign(h_diag_d.get_triu(), begin0=end_s)
        #
        # Release memory
        #
        h_diag_s, h_diag_d = None, None
        del h_diag_s, h_diag_d

        return h_diag

    @timer.with_section("EOMCCSD: H_sub")
    def build_subspace_hamiltonian(
        self, bvector: OneIndex, hdiag: OneIndex, *args: Any
    ) -> OneIndex:
        """Used by Davidson module to construct subspace Hamiltonian.
        The base class method is called, which returns all sigma vector contributions
        and the b vector, while all symmetry-unique elements are returned.

        Args:
            bvector (OneIndex): contains current approximation to CI coefficients
            hdiag (OneIndex): Diagonal Hamiltonian elements required in Davidson
                              module (not used here)
            args (Any): Set of arguments passed by the Davidson module (not used here)
        """
        #
        # Get ranges
        #
        end_s = self.occ_model.nacto[0] * self.occ_model.nactv[0] + 1
        #
        #
        # Call base class method
        #
        (
            sum0,
            sigma_s,
            sigma_d,
            bv_s,
            bv_d,
        ) = REOMCCSDBase.build_subspace_hamiltonian(
            self, bvector, hdiag, *args
        )
        #
        # Add permutation to doubles (not considered in base class)
        #
        sigma_d.iadd_transpose((2, 3, 0, 1))
        #
        # Clean-up
        #
        bv_s, bv_d = None, None
        del bv_s, bv_d
        #
        # Assign to sigma vector
        #
        sigma = self.lf.create_one_index(self.dimension)
        sigma.set_element(0, sum0)
        sigma.assign(sigma_s.ravel(), begin0=1, end0=end_s)
        sigma.assign(sigma_d.get_triu(), begin0=end_s)
        #
        # Clean-up
        #
        sigma_s, sigma_d = None, None
        del sigma_s, sigma_d

        return sigma

    @timer.with_section("EOMCCSD: H_eff")
    def update_hamiltonian(self, mo1: TwoIndex, mo2: FourIndex) -> None:
        """Derive all effective Hamiltonian matrices.
        Effective Hamiltonian elements are determined in REOMCCSDBase, while
        additional elements for Cholesky-decomposed ERI are determined here.

        Args:
            mo1 (TwoIndex): The 1-electron integrals in MO basis
            mo2 (FourIndex): The 2-electron integrals in MO basis; either
                             Dense or Cholesky type.
        """
        #
        # Call base class method
        #
        REOMCCSDBase.update_hamiltonian(self, mo1, mo2)

        #
        # 4-Index slices of ERI
        #
        def alloc(arr: FourIndex, block: str) -> None | tuple[partial[Any]]:
            """Determine alloc keyword argument for init_cache method.

            Args:
                arr (FourIndex): an instance of CholeskyFourIndex or DenseFourIndex
                block (str): encoding which slices to consider using the get_range
                             method.
            """
            # We keep one whole CholeskyFourIndex to rule them all.
            # Non-redundant blocks are accessed as views.
            if isinstance(arr, CholeskyFourIndex):
                return (partial(arr.view, **self.get_range(block)),)
            return None

        #
        # Get blocks (for the systems we can treat with Dense, it does not
        # matter that we store vvvv blocks)
        # But we do not store any blocks of DenseFourIndex
        #
        if isinstance(mo2, CholeskyFourIndex):
            slices = ["ooov", "ovvv", "vovv", "vvvv", "ovnn", "nnvv"]
            for slice_ in slices:
                self.init_cache(f"g{slice_}", alloc=alloc(mo2, slice_))
        #
        # Delete ERI (MO) as they are not required anymore
        #
        mo2.__del__()
