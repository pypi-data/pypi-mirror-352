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
"""Equation of Motion Coupled Cluster implementations of EOM-LCCD.

Child class of REOMCCDBase(REOMCC).
"""

from __future__ import annotations

from functools import partial
from typing import Any

from pybest.linalg import CholeskyFourIndex, FourIndex, OneIndex, TwoIndex
from pybest.log import timer

from .eom_ccd_base import REOMCCDBase


class REOMLCCD(REOMCCDBase):
    """Performs a EOM-LCCD calculation"""

    long_name = "Equation of Motion Linearized Coupled Cluster Doubles"
    acronym = "EOM-LCCD"
    reference = "LCCD"
    singles_ref = False
    pairs_ref = False
    doubles_ref = True
    singles_ci = False
    pairs_ci = False
    doubles_ci = True

    disconnected = False

    @timer.with_section("EOMLCCD: H_diag")
    def compute_h_diag(self, *args: Any) -> OneIndex:
        """Used by Davidson module for pre-conditioning.

        Args:
            args (Any): required for Davidson module (not used here)
        """
        h_diag = self.lf.create_one_index(self.dimension, label="h_diag")
        #
        # Call base class method
        #
        h_diag_d = REOMCCDBase.compute_h_diag(self, *args)
        #
        # Assign only symmetry-unique elements
        #
        h_diag.assign(h_diag_d.get_triu(), begin0=1)
        #
        # Release memory
        #
        h_diag_d = None
        del h_diag_d

        return h_diag

    @timer.with_section("EOMLCCD: H_sub")
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
        # Call base class method
        #
        (sum0, sigma_d, bv_d) = REOMCCDBase.build_subspace_hamiltonian(
            self, bvector, hdiag, *args
        )
        #
        # Add permutation to doubles (not considered in base class)
        #
        sigma_d.iadd_transpose((2, 3, 0, 1))
        #
        # Clean-up
        #
        del bv_d
        #
        # Assign to sigma vector
        #
        sigma = self.lf.create_one_index(self.dimension)
        sigma.set_element(0, sum0)
        sigma.assign(sigma_d.get_triu(), begin0=1)
        #
        # Clean-up
        #
        sigma_d = None
        del sigma_d

        return sigma

    @timer.with_section("EOMLCCD: H_eff")
    def update_hamiltonian(self, mo1: TwoIndex, mo2: FourIndex) -> None:
        """Derive all auxiliary matrices. Here only used to define proper timer
        sections.

        **Arguments:**

        mo1, mo2
             one- and two-electron integrals to be sorted.
        """
        #
        # Call base class method
        #
        REOMCCDBase.update_hamiltonian(self, mo1, mo2)

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
