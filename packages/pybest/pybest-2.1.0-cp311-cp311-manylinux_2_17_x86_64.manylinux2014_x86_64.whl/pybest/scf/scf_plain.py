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
# 2020-07-01: Update to PyBEST standard, including naming convention, exception class
# 2020-07-01: Update to new python features, including f-strings

"""Basic Self-Consistent Field (SCF) algorithm"""

from pybest.exceptions import ConsistencyError, NoSCFConvergence
from pybest.iodata import CheckPoint
from pybest.log import log, timer
from pybest.scf.convergence import convergence_error_eigen
from pybest.scf.utils import compute_1dm_hf

__all__ = ["PlainSCFSolver"]


class PlainSCFSolver:
    """A bare-bones SCF solver without mixing."""

    kind = "orb"  # input/output variable are the orbitals

    def __init__(self, threshold=1e-8, maxiter=128, skip_energy=False):
        """
        **Optional arguments:**

        maxiter
             The maximum number of iterations. When set to None, the SCF loop
             will go one until convergence is reached.

        threshold
             The convergence threshold for the wavefunction

        skip_energy
             When set to True, the final energy is not computed.
        """
        self.maxiter = maxiter
        self.threshold = threshold
        self.skip_energy = skip_energy
        self._checkpoint = CheckPoint({})

    @property
    def checkpoint(self):
        """The iodata container that contains all data dump to disk"""
        return self._checkpoint

    @timer.with_section("SCF")
    def __call__(self, ham, lf, overlap, occ_model, *orbs):
        """Find a self-consistent set of orbitals.

        **Arguments:**

        ham
             An effective Hamiltonian.

        lf
             The linalg factory to be used.

        overlap
             The overlap operator.

        occ_model
             Model for the orbital occupations.

        orb1, orb2, ...
             The initial orbitals. The number of orbitals must match ham.ndm.
        """
        # update checkpoint file
        self.checkpoint.update("olp", overlap)
        # Some type checking
        if ham.ndm != len(orbs):
            raise ConsistencyError(
                "The number of initial orbital expansions does not match the Hamiltonian."
            )
        # Impose the requested occupation numbers
        occ_model.assign_occ_reference(*orbs)
        # Check the orthogonality of the orbitals
        for orb in orbs:
            orb.check_normalization(overlap)

        if log.do_medium:
            log(f"Starting plain SCF solver. ndm = {ham.ndm}")
            log.hline()
            log("Iter         Error")
            log.hline()

        focks = [lf.create_two_index() for i in range(ham.ndm)]
        dms = [lf.create_two_index() for i in range(ham.ndm)]
        converged = False
        self.checkpoint.update("converged", False)
        counter = 0
        while self.maxiter is None or counter < self.maxiter:
            # convert the orbital expansions to density matrices
            for i in range(ham.ndm):
                self.compute_1dm(orbs[i], dms[i])
            # feed the latest density matrices in the hamiltonian
            ham.reset(*dms)
            # Construct the Fock operator
            ham.compute_fock(*focks)
            # Check for convergence
            error = 0.0
            for i in range(ham.ndm):
                error += orbs[i].error_eigen(focks[i], overlap)
            if log.do_medium:
                log(f"{counter:>4}  {error:> 16.5e}")
            if error < self.threshold:
                converged = True
                break
            # Diagonalize the fock operators to obtain new orbitals and
            for i in range(ham.ndm):
                orbs[i].from_fock(focks[i], overlap)
            # update checkpoint file
            self.checkpoint.update("orb_a", orbs[0].copy())
            if ham.ndm == 2:
                self.checkpoint.update("orb_b", orbs[1].copy())
            # Assign new occupation numbers.
            occ_model.assign_occ_reference(*orbs)
            # counter
            counter += 1
            self.checkpoint.update("niter", counter)
            # Dump checkpoint to file
            self.checkpoint.to_file("checkpoint_scf.h5")

        if log.do_medium:
            log.blank()

        if not self.skip_energy:
            ham.compute_energy(self.checkpoint)
            if log.do_medium:
                ham.log(self.checkpoint)

        if not converged:
            raise NoSCFConvergence(
                f"Plain SCF solver not converged within {self.maxiter} iterations."
            )
        self.checkpoint.update("converged", True)

        # Update dms
        for i in range(ham.ndm):
            self.compute_1dm(orbs[i], dms[i])
        if ham.ndm == 2:
            self.checkpoint.update("dm_1_a", dms[0])
            self.checkpoint.update("dm_1_b", dms[1])
        else:
            self.checkpoint.update("dm_1", dms[0])
        # Dump checkpoint to file
        self.checkpoint.to_file("checkpoint_scf.h5")

        return self.checkpoint()

    def error(self, ham, lf, overlap, *orbs):
        """See :py:func:`pybest.scf.convergence.convergence_error_eigen`."""
        return convergence_error_eigen(ham, lf, overlap, *orbs)

    def compute_1dm(self, orb, out=None, factor=1.0, clear=True):
        return compute_1dm_hf(orb, out, factor, clear)
