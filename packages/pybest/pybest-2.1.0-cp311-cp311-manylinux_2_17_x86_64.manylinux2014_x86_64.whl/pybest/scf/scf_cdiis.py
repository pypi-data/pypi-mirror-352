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
#
# This implementation has been taken from `Horton 2.0.0`.
# However, this file has been updated and debugged. Compatibility with Horton is NOT
# guaranteed.
# Its current version contains updates from the PyBEST developer team.
#
# Detailed changes (see also CHANGELOG):
# 2020-07-01: Update to PyBEST standard, including naming convention
# 2020-07-01: Update to new python features, including f-strings

"""Commutator DIIS SCF algorithm"""

import numpy as np

from pybest.log import log
from pybest.scf.scf_diis import DIISHistory, DIISSCFSolver
from pybest.solvers.linear_equations import solve_safe
from pybest.utility import doc_inherit

__all__ = ["CDIISSCFSolver"]


class CDIISSCFSolver(DIISSCFSolver):
    """The Commmutatator (or Pulay) DIIS SCF solver [pulay1980]_"""

    def __init__(
        self,
        threshold=1e-6,
        maxiter=128,
        nvector=6,
        skip_energy=False,
        prune_old_states=False,
    ):
        """
        **Optional arguments:**

        maxiter
             The maximum number of iterations. When set to None, the SCF loop
             will go one until convergence is reached.

        threshold
             The convergence threshold for the wavefunction

        skip_energy
             When set to True, the final energy is not computed. Note that some
             DIIS variants need to compute the energy anyway. for these methods
             this option is irrelevant.

        prune_old_states
             When set to True, old states are pruned from the history when their
             coefficient is zero. Pruning starts at the oldest state and stops
             as soon as a state is encountered with a non-zero coefficient. Even
             if some newer states have a zero coefficient.
        """
        log.cite("the commutator DIIS SCF algorithm", "pulay1980")
        DIISSCFSolver.__init__(
            self,
            CDIISHistory,
            threshold,
            maxiter,
            nvector,
            skip_energy,
            prune_old_states,
        )


class CDIISHistory(DIISHistory):
    """A commutator DIIS history object that keeps track of previous SCF solutions

    This type of DIIS is also called Pulay DIIS.
    """

    name = "CDIIS"
    need_energy = False

    def __init__(self, lf, nvector, ndm, deriv_scale, overlap):
        """
        **Arguments:**

        lf
             The LinalgFactor used to create the two-index operators.

        nvector
             The maximum size of the history.

        ndm
             The number of density matrices (and fock matrices) in one
             state.

        deriv_scale
             The deriv_scale attribute of the Effective Hamiltonian

        overlap
             The overlap matrix.
        """
        self.cdots = np.empty((nvector, nvector))
        self.cdots.fill(np.nan)
        DIISHistory.__init__(
            self, lf, nvector, ndm, deriv_scale, overlap, [self.cdots]
        )

    def _complete_cdots_matrix(self):
        """Complete the matrix of dot products between commutators

        Even after multiple additions, this routine will fill up all the
        missing dot products in self.cdots.
        """
        for i0 in range(self.nused - 1, -1, -1):
            state0 = self.stack[i0]
            self.cdots[i0, i0] = state0.normsq
            # Compute off-diagonal coefficients
            for i1 in range(i0):
                if np.isfinite(self.cdots[i0, i1]):
                    return
                state1 = self.stack[i1]
                cdot = 0.0
                for j in range(self.ndm):
                    cdot += state0.commutators[j].contract(
                        "ab,ab", state1.commutators[j]
                    )
                self.cdots[i0, i1] = cdot
                self.cdots[i1, i0] = cdot

    @doc_inherit(DIISHistory)
    def solve(self, dms_output, focks_output):
        # extrapolation only makes sense if there are two points
        assert self.nused >= 2
        # Fill in the missing commutators
        self._complete_cdots_matrix()
        coeffs = solve_cdiis(self.cdots[: self.nused, : self.nused])
        # get a condition number
        absevals = abs(
            np.linalg.eigvalsh(self.cdots[: self.nused, : self.nused])
        )
        # prevent division by 0.0 by using a really small number
        absevals_min = 1e-20 if absevals.min() == 0.0 else absevals.min()
        cn = absevals.max() / absevals_min
        # assign extrapolated fock
        error = self._build_combinations(coeffs, dms_output, focks_output)
        return None, coeffs, cn, "C", error


def solve_cdiis(a):
    r"""Solve the linear equations found in the cdiis method

    The following is minimized:

    .. math:
         \frac{1}{2} x^T a x

     under the constraint :math:`\sum_i x_i = 1`.

    **Arguments:**

    a
         The matrix a, an array of size (N,N).
    """
    n = len(a)
    assert a.shape == (n, n)
    assert (a == a.T).all()
    a2 = np.zeros((n + 1, n + 1))
    a2[:n, :n] = a
    a2[n, :n] = 1
    a2[:n, n] = 1
    b2 = np.zeros(n + 1)
    b2[n] = 1
    x2 = solve_safe(a2, b2)
    return x2[:n]
