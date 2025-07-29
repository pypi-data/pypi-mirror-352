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

"""Abstract DIIS code used by the different DIIS implementations"""

import numpy as np

from pybest.exceptions import ConsistencyError, EmptyData, NoSCFConvergence
from pybest.iodata import CheckPoint
from pybest.log import log, timer
from pybest.scf.convergence import convergence_error_commutator
from pybest.scf.utils import check_dm, compute_1dm_hf, compute_commutator

__all__ = ["DIISHistory", "DIISSCFSolver", "DIISState"]


class DIISSCFSolver:
    """Base class for all DIIS SCF solvers"""

    kind = "dm"  # input/output variable is the density matrix

    def __init__(
        self,
        DIISHistoryClass,
        threshold=1e-6,
        maxiter=128,
        nvector=6,
        skip_energy=False,
        prune_old_states=False,
    ):
        """
        **Arguments:**

        DIISHistoryClass
             A DIIS history class.

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
        self.DIISHistoryClass = DIISHistoryClass
        self.threshold = threshold
        self.maxiter = maxiter
        self.nvector = nvector
        self.skip_energy = skip_energy
        self.prune_old_states = prune_old_states
        self._checkpoint = CheckPoint({})

    @property
    def checkpoint(self):
        """The iodata container that contains all data dump to disk"""
        return self._checkpoint

    @timer.with_section("SCF")
    def __call__(self, ham, lf, overlap, occ_model, *dms):
        """Find a self-consistent set of density matrices.

        **Arguments:**

        ham
             An effective Hamiltonian.

        lf
             The linalg factory to be used.

        overlap
             The overlap operator.

        occ_model
             Model for the orbital occupations.

        dm1, dm2, ...
             The initial density matrices. The number of dms must match
             ham.ndm.
        """
        # update checkpoint file
        self.checkpoint.update("olp", overlap)
        # Some type checking
        if ham.ndm != len(dms):
            raise ConsistencyError(
                "The number of initial density matrices does not match the Hamiltonian."
            )

        # Check input density matrices.
        for i in range(ham.ndm):
            check_dm(dms[i], overlap, lf)
        occ_model.check_dms(*dms, olp=overlap)

        # keep local variables as attributes for inspection/debugging by caller
        self._history = self.DIISHistoryClass(
            lf, self.nvector, ham.ndm, ham.deriv_scale, overlap
        )
        self._focks = [lf.create_two_index() for i in range(ham.ndm)]
        self._orbs = [lf.create_orbital() for i in range(ham.ndm)]

        if log.do_medium:
            log(f"Starting restricted closed-shell {self._history.name}-SCF")
            log.hline()
            log(
                "Iter         Error        CN         Last nv Method          Energy       Change"
            )
            log.hline()

        converged = False
        counter = 0
        while self.maxiter is None or counter < self.maxiter:
            # Construct the Fock operator from scratch if the history is empty:
            if self._history.nused == 0:
                # feed the latest density matrices in the hamiltonian
                ham.reset(*dms)
                # Construct the Fock operators
                ham.compute_fock(*self._focks)
                # Compute the energy if needed by the history
                energy = (
                    ham.compute_energy(self.checkpoint)
                    if self._history.need_energy
                    else None
                )
                # Add the current fock+dm pair to the history
                error = self._history.add(energy, dms, self._focks)

                # Screen logging
                if log.do_high:
                    log("          DIIS add")
                if error < self.threshold:
                    converged = True
                    break
                if log.do_high:
                    log.blank()
                if log.do_medium:
                    energy_ = " " if energy is None else f"{energy: 43.13f}"
                    log(
                        f"{counter:>4} {error:> 16.5e} {self._history.nused:> 5} "
                        f"{energy_}"
                    )
                if log.do_high:
                    log.blank()
            else:
                energy = None

            # Take a regular SCF step using the current fock matrix. Then
            # construct a new density matrix and Fock matrix.
            for i in range(ham.ndm):
                self._orbs[i].from_fock(self._focks[i], overlap)
            occ_model.assign_occ_reference(*self._orbs)
            for i in range(ham.ndm):
                self.compute_1dm(self._orbs[i], dms[i])
            ham.reset(*dms)
            energy = (
                ham.compute_energy(self.checkpoint)
                if self._history.need_energy
                else None
            )
            ham.compute_fock(*self._focks)

            # Add the current (dm, fock) pair to the history
            if log.do_high:
                log("          DIIS add")
            error = self._history.add(energy, dms, self._focks)

            # break when converged
            if error < self.threshold:
                converged = True
                break

            # Screen logging
            if log.do_high:
                log.blank()
            if log.do_medium:
                energy_ = " " if energy is None else f"{energy: 43.13f}"
                log(
                    f"{counter:>4} {error:> 16.5e} {self._history.nused:> 5} {energy_}"
                )
            if log.do_high:
                log.blank()

            # get extra/intra-polated Fock matrix
            while True:
                # The following method writes the interpolated dms and focks
                # in-place.
                energy_approx, coeffs, cn, method, error = self._history.solve(
                    dms, self._focks
                )
                # if the error is small on the interpolated state, we have
                # converged to a solution that may have fractional occupation
                # numbers.
                if error < self.threshold:
                    converged = True
                    break
                if self._history.nused <= 2:
                    break
                if coeffs[-1] == 0.0:
                    if log.do_high:
                        log(
                            "          DIIS (last coeff zero) -> drop "
                            f"{self._history.stack[0].identity} and retry"
                        )
                    self._history.shrink()
                else:
                    break

            if energy_approx is not None:
                energy_change = energy_approx - min(
                    state.energy for state in self._history.stack
                )
            else:
                energy_change = None

            # log
            if log.do_high:
                self._history.log(coeffs)

            if log.do_medium:
                change_ = (
                    " " if energy_change is None else f"{energy_change: 35.7f}"
                )
                log(
                    f"{counter:>4} {cn:> 26.3e} {coeffs[-1]:> 9.5f} "
                    f"{self._history.nused:2} {method} {change_}"
                )

            if log.do_high:
                log.blank()

            if self.prune_old_states:
                # get rid of old states with zero coeff
                for i in range(self._history.nused):
                    if coeffs[i] == 0.0:
                        if log.do_high:
                            log(
                                "          DIIS insignificant -> drop "
                                f"{self._history.stack[0].identity}"
                            )
                        self._history.shrink()
                    else:
                        break

            # counter
            counter += 1

            # Update dms
            if ham.ndm == 2:
                self.checkpoint.update("dm_1_a", dms[0])
                self.checkpoint.update("dm_1_b", dms[1])
            else:
                self.checkpoint.update("dm_1", dms[0])
            # Update orbitals
            self.checkpoint.update("orb_a", self._orbs[0])
            if ham.ndm == 2:
                self.checkpoint.update("orb_b", self._orbs[1])
            # Dump checkpoint to file
            self.checkpoint.to_file("checkpoint_scf.h5")

        if log.do_medium:
            if converged:
                log(f"{counter:>4} {error:> 16.5e} (converged)")
            log.blank()

        # Update final orbitals. This is not required. However, we do it to
        # dump the final orbitals to a checkpoint file
        ham.compute_fock(*self._focks)
        for i in range(ham.ndm):
            self._orbs[i].from_fock(self._focks[i], overlap)
        occ_model.assign_occ_reference(*self._orbs)
        for i in range(ham.ndm):
            self.compute_1dm(self._orbs[i], dms[i])
        energy = (
            ham.compute_energy(self.checkpoint)
            if self._history.need_energy
            else None
        )

        # Update dms
        if ham.ndm == 2:
            self.checkpoint.update("dm_1_a", dms[0])
            self.checkpoint.update("dm_1_b", dms[1])
        else:
            self.checkpoint.update("dm_1", dms[0])

        # Update orbitals
        self.checkpoint.update("orb_a", self._orbs[0])
        if ham.ndm == 2:
            self.checkpoint.update("orb_b", self._orbs[1])

        if not self.skip_energy or self._history.need_energy:
            if not self._history.need_energy:
                ham.compute_energy(self.checkpoint)
            if log.do_medium:
                ham.log(self.checkpoint)

        if not converged:
            raise NoSCFConvergence
        self.checkpoint.update("converged", True)

        # Dump checkpoint to file
        self.checkpoint.to_file("checkpoint_scf.h5")

        return self.checkpoint()

    def error(self, ham, lf, overlap, *dms):
        """A convergence error function"""
        return convergence_error_commutator(ham, lf, overlap, *dms)

    def compute_1dm(self, orb, out=None, factor=1.0, clear=True):
        """A funtion to compute 1-DM"""
        return compute_1dm_hf(orb, out, factor, clear)


class DIISState:
    """A single record (vector) in a DIIS history object."""

    def __init__(self, lf, ndm, work, overlap):
        """
        **Arguments:**

        lf
             The LinalgFactor used to create the two-index operators.

        ndm
             The number of density matrices (and fock matrices) in one
             state.

        work
             A two index operator to be used as a temporary variable. This
             object is allocated by the history object.

        overlap
             The overlap matrix.
        """
        # Not all of these need to be used.
        self.ndm = ndm
        self.work = work
        self.overlap = overlap
        self.energy = np.nan
        self.normsq = np.nan
        self.dms = [lf.create_two_index() for i in range(self.ndm)]
        self.focks = [lf.create_two_index() for i in range(self.ndm)]
        self.commutators = [lf.create_two_index() for i in range(self.ndm)]
        self.identity = None  # every state has a different id.

    def clear(self):
        """Reset this record."""
        self.energy = np.nan
        self.normsq = np.nan
        for i in range(self.ndm):
            self.dms[i].clear()
            self.focks[i].clear()
            self.commutators[i].clear()

    def assign(self, identity, energy, dms, focks):
        """Assign a new state.

        **Arguments:**

        identity
             A unique id for the new state.

        energy
             The energy of the new state.

        dm
             The density matrix of the new state.

        fock
             The Fock matrix of the new state.
        """
        self.identity = identity
        self.energy = energy
        self.normsq = 0.0
        for i in range(self.ndm):
            self.dms[i].assign(dms[i])
            self.focks[i].assign(focks[i])
            compute_commutator(
                dms[i], focks[i], self.overlap, self.work, self.commutators[i]
            )
            self.normsq += self.commutators[i].contract(
                "ab,ab", self.commutators[i]
            )


class DIISHistory:
    """A base class of DIIS histories"""

    name = None
    need_energy = None

    def __init__(self, lf, nvector, ndm, deriv_scale, overlap, dots_matrices):
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

        dots_matrices
             Matrices in which dot products will be stored

        **Useful attributes:**

        used
             The actual number of vectors in the history.
        """
        self.work = lf.create_two_index()
        self.stack = [
            DIISState(lf, ndm, self.work, overlap) for i in range(nvector)
        ]
        self.ndm = ndm
        self.deriv_scale = deriv_scale
        self.overlap = overlap
        self.dots_matrices = dots_matrices
        self.nused = 0
        self.idcounter = 0
        self.commutator = lf.create_two_index()

    @property
    def nvector(self):
        """The maximum size of the history"""
        return len(self.stack)

    def log(self, coeffs):
        """Print energy reference and coeffs"""
        # Skip if e_ref is None
        e_ref = None
        try:
            e_ref = min(state.energy for state in self.stack[: self.nused])
        except EmptyData:
            pass
        if e_ref is None:
            log("          DIIS history      normsq         coeff         id")
            for i in range(self.nused):
                state = self.stack[i]
                log(
                    f"          DIIS history  {state.normsq: 12.5e}  {coeffs[i]: 12.7f} "
                    f"{state.identity:8}"
                )
        else:
            log(
                "          DIIS history      normsq      energy         coeff         id"
            )
            for i in range(self.nused):
                state = self.stack[i]
                log(
                    f"          DIIS history  {state.normsq: 12.5e}  "
                    f"{state.energy - e_ref: 12.5e} {coeffs[i]: 12.7f} "
                    f"{state.identity:8}"
                )
        log.blank()

    def solve(self, dms_output, focks_output):
        """Inter- or extrapolate new density and/or fock matrices.

        **Arguments:**

        dms_output
             The output for the density matrices. If set to None, this is
             argument is ignored.

        focks_output
             The output for the Fock matrices. If set to None, this is
             argument is ignored.
        """
        raise NotImplementedError

    def shrink(self):
        """Remove the oldest item from the history"""
        self.nused -= 1
        state = self.stack.pop(0)
        state.clear()
        self.stack.append(state)
        for dots in self.dots_matrices:
            dots[:-1] = dots[1:]
            dots[:, :-1] = dots[:, 1:]
            dots[-1] = np.nan
            dots[:, -1] = np.nan

    def add(self, energy, dms, focks):
        """Add new state to the history.

        **Arguments:**

        energy
             The energy of the new state.

        dms
             A list of density matrices of the new state.

        focks
             A list of Fock matrix of the new state.

        **Returns**: the square root of commutator error for the given pairs
        of density and Fock matrices.
        """
        if len(dms) != self.ndm or len(focks) != self.ndm:
            raise ConsistencyError(
                "The number of density and Fock matrices must match the ndm parameter."
            )
        # There must be a free spot. If needed, make one.
        if self.nused == self.nvector:
            self.shrink()

        # assign dm and fock
        state = self.stack[self.nused]
        state.assign(self.idcounter, energy, dms, focks)
        self.idcounter += 1

        # prepare for next iteration
        self.nused += 1
        return np.sqrt(state.normsq)

    def _build_combinations(self, coeffs, dms_output, focks_output):
        """Construct a linear combination of density/fock matrices

        **Arguments:**

        coeffs
             The linear mixing coefficients for the previous SCF states.

        dms_output
             A list of output density matrices. (Ignored if None)

        focks_output
             A list of output density matrices. (Ignored if None)

        **Returns:** the commutator error, only when both dms_output and
        focks_output are given.
        """
        if dms_output is not None:
            if len(dms_output) != self.ndm:
                raise ConsistencyError(
                    "The number of density matrices must match the ndm parameter."
                )
            for i in range(self.ndm):
                dms_stack = [self.stack[j].dms[i] for j in range(self.nused)]
                self._linear_combination(coeffs, dms_stack, dms_output[i])
        if focks_output is not None:
            if len(focks_output) != self.ndm:
                raise ConsistencyError(
                    "The number of Fock matrices must match the ndm parameter."
                )
            for i in range(self.ndm):
                focks_stack = [
                    self.stack[j].focks[i] for j in range(self.nused)
                ]
                self._linear_combination(coeffs, focks_stack, focks_output[i])
        if not (dms_output is None or focks_output is None):
            errorsq = 0.0
            for i in range(self.ndm):
                compute_commutator(
                    dms_output[i],
                    focks_output[i],
                    self.overlap,
                    self.work,
                    self.commutator,
                )
                errorsq += self.commutator.contract("ab,ab", self.commutator)
            return errorsq**0.5
        return None

    def _linear_combination(self, coeffs, ops, output):
        """Make a linear combination of two-index objects

        **Arguments:**

        coeffs
             The linear mixing coefficients for the previous SCF states.

        ops
             A list of input operators.

        output
             The output operator.
        """
        output.clear()
        for i in range(self.nused):
            output.iadd(ops[i], factor=coeffs[i])
