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
# This module has been originaly written and updated by Katharina Boguslawski (see CHANGELOG)
# Its current version contains updates from the PyBEST developer team.
#
# An original version of this implementation can also be found in 'Horton 2.0.0'.
# However, this file has been updated and debugged. Compatibility with Horton is NOT
# guaranteed.
#
# 10.2022:
# This module has been rewritten by Emil Sujkowski:
# Moved here from rpccd.py:
# - solve_scf as solve
#
# New methods:
# - Created get_guess with raise NotImplementedError to avoid conflicts with rpccd_base
# - Replaced Generating Guess with get_guess method
# - ncore, npairs, nocc, nvirt, nbasis variables have been removed and replaced by
#   the use of occ_model
#
# 2024: Seyedehdelaram Jahani: orbital energies
# 2024: Seyedehdelaram Jahani: moved orbital energies to a separate module
#
#
# Detailed changes:
# See CHANGELOG

"""Methods for orbital-optimized pCCD"""

import warnings
from abc import ABC
from copy import copy

import numpy as np

from pybest.exceptions import ArgumentError
from pybest.geminals.geminals_base import GeminalsBase
from pybest.linalg.base import Orbital
from pybest.linalg.cholesky import CholeskyFourIndex
from pybest.log import log, timer
from pybest.steplength.stepsearch import RStepSearch
from pybest.utility import (
    check_options,
    check_type,
    compute_unitary_matrix,
    unmask,
)


class OOGeminals(GeminalsBase, ABC):
    """Class containing methods characteristic for orbital optimised geminals."""

    acronym = ""
    long_name = ""
    reference = ""
    cluster_operator = ""
    comment = "restricted, closed-shell"

    def get_guess(self, one, two, olp, orb, **kwargs):
        """**Arguments:**

        one, two
             One- (TwoIndex instance) and two-body integrals (FourIndex or
             Cholesky instance) (some Hamiltonian matrix elements)

        orb
             An expansion instance. It contains the MO coefficients.

        olp
             The AO overlap matrix. A TwoIndex instance.
        """
        raise NotImplementedError

    def solve_model(self, one, two, orb, **kwargs):
        """Solve for some geminal model.
        **Arguments:**

        one, two
             One- and two-body integrals (some Hamiltonian matrix elements).
             A TwoIndex and FourIndex/Cholesky instance

        orb
             An expansion instance which contains the MO coefficients.
        """
        raise NotImplementedError

    def print_final(self, status="Final"):
        """Print energies

        **Optional arguments:**

        status
             A string.
        """
        raise NotImplementedError

    def dump_final(
        self,
        orb,
        printoptions,
        dumpci,
        checkpoint,
        checkpoint_fn="checkpoint_pccd.h5",
    ):
        """Dump final solution. See :py:meth `RpCCDBase.dump_final`"""
        raise NotImplementedError

    def compute_correlation_energy(self, arg=None):
        """Get correlation energy of restricted pCCD

        **Optional arguments:**

        arg
             The pCCD coefficient matrix (np.array or TwoIndex instance).
             If not provided, the correlation energy is calculated
             from self.geminal_matrix (default None)
        """
        raise NotImplementedError

    def compute_total_energy(self, coeff=None):
        """Get total energy (reference + correlation) including nuclear-repulsion/
        core energy for restricted pCCD.

        **Optional arguments:**

        coeff
             The pCCD coefficient matrix (np.array or TwoIndex instance).
             If not provided, the correlation energy is calculated
             from self.geminal_matrix (default None)
        """
        raise NotImplementedError

    def compute_reference_energy(self):
        """Get energy of reference determinant for restricted pCCD including core energy"""
        raise NotImplementedError

    def compute_overlap(self):
        """Compute approximate overlap of pCCD"""
        raise NotImplementedError

    @timer.with_section("OOGeminal: Solver")
    def solve(self, one, two, olp, orb, *args, **kwargs):
        """Find Geminal expansion coefficient for some Hamiltonian.
        For restricted, closed-shell geminal model.
        Perform orbital optimization.

        **Arguments:**

        one, two
             One- (TwoIndex instance) and two-body integrals (FourIndex or
             Cholesky instance) (some Hamiltonian matrix elements)

        orb
             An expansion instance. It contains the MO coefficients.

        olp
             The AO overlap matrix. A TwoIndex instance.

        *args
             May contain an IOData instance

        **Keywords:**

         :indextrans: 4-index Transformation (str). Choice between
                      ``tensordot`` (default), ``cupy``, ``einsum``, ``cpp``,
                      ``opt_einsum``, or ``einsum_naive``.
                      If ``cupy`` is not available, we switch to ``tensordot``.
         :warning: print warnings (boolean) (default False)
         :guess: initial guess (dictionary) containing:

                 * type: guess type (str). One of ``mp2`` (MP2 pair
                   amplitudes, default), ``random`` (random numbers),
                   ``const`` (a constant scaled by a factor)
                 * factor: a scaling factor (float) (default -0.1)
                 * geminal: external guess for geminal coefficients
                   (1-dim np.array) (default None)
                 * lagrange: external guess for Lagrange multipliers
                   (1-dim np.array) (default None)

         :solver: wfn/Lagrange solver (dictionary) containing:

                  * wfn: wavefunction solver (str) (default ``krylov``)
                  * lagrange: Lagrange multiplier solver (str)
                    (default krylov)

         :maxiter: max number of iterations (dictionary) containing:

                   * wfniter: maximum number of iterations for
                              wfn/lagrange solver (int) (default 200)
                   * orbiter: maximum number of orbital optimization
                              steps (int) (default 1000)
         :dumpci: dump ci coefficient (dictionary) containing:

                  * amplitudestofile: write wfn amplitudes to file
                    (boolean) (default False)
                  * amplitudesfilename: (str) (default pccd_amplitudes.dat)

         :thresh: optimization thresholds (dictionary) containing:

                  * wfn: threshold for geminal coefficients and
                    Lagrange multipliers (float) (defaulf 1e-12)
                  * energy: convergence threshold for energy (float)
                    (default 1e-8)
                  * gradientnorm: convergence threshold for norm of
                    orbital gradient (float) (default 1e-4)
                  * gradientmax: threshold for maximum absolute value of
                    orbital gradient (float) (default 5e-5)

         :printoptions: print level; dictionary containing:

                        * geminal: (boolean), if True, geminal matrix is
                          printed (default True)
                        * geminal_coefficients: (boolean), if True, only
                          the largest (in absolute value) coefficients
                          will be printed. If False, the Slater determinant
                          expansion will be printed instead
                        * threshold: threshold for CI coefficients (requires
                          evaluation of a permanent) (float). All
                          coefficients (for a given excitation order)
                          larger than `threshold` are printed (default 0.01)
                        * excitationlevel: number of excited pairs w.r.t.
                          reference determinant for which
                          wfn amplitudes are reconstructed
                          (int) (default 1)

         :stepsearch: step search options (dictionary) containing:

                      * method: step search method used (str). One of
                        ``trust-region`` (default), ``None``,
                        ``backtracking``
                      * alpha: scaling factor for Newton step (float),
                        used in ``backtracking`` and ``None`` method (default
                        1.00)
                      * c1: parameter used in ``backtracking`` (float)
                        (default 1e-4)
                      * minalpha: minimum scaling factor used in
                        ``backracking`` (float) (default 1e-6)
                      * maxiterouter: maximum number of search steps
                        (int) (default 10)
                      * maxiterinner: maximum number of optimization
                        step in each search step (int) (used only in ``pcg``,
                        default 500)
                      * maxeta: upper bound for estimated vs actual
                        change in ``trust-region`` (float) (default 0.75)
                      * mineta: lower bound for estimated vs actual change in
                        ``trust-region`` (float) (default 0.25)
                      * upscale: scaling factor to increase trustradius
                        in ``trust-region`` (float) (default 2.0)
                      * downscale: scaling factor to decrease trustradius
                        in ``trust-region`` and step length in
                        ``backtracking`` (float) (default 0.25)
                      * trustradius: initial trustradius (float) (default
                        0.75)
                      * maxtrustradius: maximum trustradius (float) (default
                        0.75)
                      * threshold: trust-region optimization threshold, only
                        used in ``pcg`` (float) (default 1e-8)
                      * optimizer: optimizes step to boundary of trustradius
                        (str). One of ``pcg``, ``dogleg``, ``ddl`` (default
                        ddl)
                      * reset: resets the current value of the trustradius to
                        ``maxtrustradius`` after a number of iterations have
                        passed (int) (default 10)

         :checkpoint: frequency of checkpointing (int). If > 0, writes
                      orbitals and overlap to a checkpont file (defatul 1)
         :checkpoint_fn: filename to use for the checkpoint file (default
                         "checkpoint_pccd.h5")
         :levelshift: level shift of Hessian (float) (default 1e-8)
         :absolute: (boolean), if True, take absolute values of Hessian
                    (default False)
         :sort: (boolean | str), if True, orbitals are sorted according to their
                natural occupation numbers. This requires us to solve for
                the wavefunction again. Works only if orbitaloptimizer
                is set to ``variational``. Orbitals are only sorted if Aufbau
                occupation changes. Sorting can be enforced by using ``force``
                instead of True/False. (default True)
         :orbitaloptimizer: (str) switch between variational orbital
                            optimization (``variational``) and PS2c
                            (``ps2c``) (default ``variational``).
         :e_core: (float) core energy
         :restart: (str) filename that contains some restart amplitudes (geminal
                   coefficient are read from file).
        """
        if log.do_medium:
            log.hline("=")
            log(f"Entering orbital-optimized {self.acronym} module")

        #
        # Assign keyword arguements, checks only name of dictionary, keys and
        # values are checked below.
        #
        names = []

        def _helper(x, y):
            names.append(x)
            return kwargs.get(x, y)

        indextrans = _helper("indextrans", None)
        warning = _helper("warning", False)
        checkpoint = _helper("checkpoint", 1)
        checkpoint_fn = _helper("checkpoint_fn", "checkpoint_pccd.h5")
        lshift = _helper("levelshift", 1e-8)
        pos = _helper("absolute", False)
        sort = _helper("sort", True)
        guess = _helper("guess", {})
        guess.setdefault("type", "mp2")
        guess.setdefault("factor", -0.1)
        guess.setdefault("geminal", None)
        guess.setdefault("lagrange", None)
        solver = _helper("solver", {})
        solver.setdefault("wfn", "krylov")
        solver.setdefault("lagrange", "krylov")
        maxiter = _helper("maxiter", {})
        maxiter.setdefault("wfniter", 200)
        maxiter.setdefault("orbiter", 1000)
        dumpci = _helper("dumpci", {})
        dumpci.setdefault("amplitudestofile", False)
        dumpci.setdefault("amplitudesfilename", "./pccd_amplitudes.dat")
        thresh = _helper("thresh", {})
        thresh.setdefault("wfn", 1e-12)
        thresh.setdefault("energy", 1e-8)
        thresh.setdefault("gradientnorm", 1e-4)
        thresh.setdefault("gradientmax", 5e-5)
        printoptions = _helper("printoptions", {})
        printoptions.setdefault("geminal", False)
        printoptions.setdefault("geminal_coefficients", True)
        printoptions.setdefault("threshold", 0.01)
        printoptions.setdefault("excitationlevel", 1)
        stepsearch = _helper("stepsearch", {})
        stepsearch.setdefault("method", "trust-region")
        stepsearch.setdefault("alpha", 1.0)
        stepsearch.setdefault("c1", 0.0001)
        stepsearch.setdefault("minalpha", 1e-6)
        stepsearch.setdefault("maxiterouter", 10)
        stepsearch.setdefault("maxiterinner", 500)
        stepsearch.setdefault("maxeta", 0.75)
        stepsearch.setdefault("mineta", 0.25)
        stepsearch.setdefault("upscale", 2.0)
        stepsearch.setdefault("downscale", 0.25)
        stepsearch.setdefault("trustradius", 0.75)
        stepsearch.setdefault("maxtrustradius", 0.75)
        stepsearch.setdefault("threshold", 1e-8)
        stepsearch.setdefault("optimizer", "ddl")
        stepsearch.setdefault("reset", 10)
        orbitaloptimizer = _helper("orbitaloptimizer", "variational")
        restart = _helper("restart", False)
        e_core = _helper("e_core", None)

        for key, _value in kwargs.items():
            if key not in names:
                raise ArgumentError(f"Unknown keyword argument {key}")

        #
        # Check dictionaries in keyword arguments
        #
        self.check_keywords_scf(
            guess, solver, maxiter, dumpci, thresh, printoptions, stepsearch
        )
        check_options("warning", warning, False, True, 0, 1)
        check_type("checkpoint", checkpoint, int)
        check_type("checkpoint_fn", checkpoint_fn, str)
        check_type("levelshift", lshift, float, int)
        check_options("absolute", pos, False, True, 0, 1)
        check_options("sort", sort, True, False, 0, 1, "force")

        #
        # Set optimization parameters
        #
        if not warning:
            warnings.filterwarnings("ignore")
        if maxiter["orbiter"] < 0:
            raise ValueError("Number of iterations must be greater/equal 0!")

        #
        # Print optimization parameters
        #
        if log.do_medium:
            self.print_options_scf(
                guess,
                solver,
                maxiter,
                lshift,
                stepsearch,
                thresh,
                printoptions,
                checkpoint,
                checkpoint_fn,
                indextrans,
                orbitaloptimizer,
                sort,
            )

        #
        # Overwrite core energy using unmask function if not found in kwargs
        #
        if e_core is None:
            # Check IOData for e_core
            e_core = unmask("e_core", *args, **kwargs)
            if e_core is None and not restart:
                raise ArgumentError("Cannot find core energy in arguments.")
        self.e_core = e_core

        #
        # Generate Guess [geminal_matrix, lagrange_matrix]
        #
        olp, orb, initial_guess = self.get_guess(
            one,
            two,
            olp,
            orb,
            **{
                "guess": guess,
                "indextrans": indextrans,
                "restart": restart,
                **kwargs,
            },
        )
        # create a copy, this adds more flexibility during calculations and
        # the olp files are typically very small
        self.checkpoint.update("olp", olp)
        self.checkpoint.update("orb_a", orb.copy())
        #
        # First iteration:
        #
        if log.do_medium:
            log(" ")
            log(f"Starting optimization of {self.acronym} wave function...")

        self.solve_model(
            one,
            two,
            orb,
            **{
                "maxiter": maxiter,
                "thresh": thresh,
                "guess": initial_guess["t_p"],
                "guesslm": initial_guess["l_p"],
                "solver": solver,
                "indextrans": indextrans,
                "orbitaloptimizer": orbitaloptimizer,
            },
        )

        #
        # Update total/corr/single/pair energy
        #
        e_tot = self.compute_total_energy()
        e_corr = self.compute_correlation_energy()
        e_ref = self.compute_reference_energy()

        e_dict = {
            "e_tot": e_tot,
            "e_corr": e_corr,
            "e_ref": e_ref,
        }
        self.energy = e_dict
        #
        # Update IOData container
        #
        self.checkpoint.update("e_core", self.e_core)
        self.checkpoint.update("e_tot", e_tot)
        self.checkpoint.update("e_corr", e_corr)
        self.checkpoint.update("e_ref", e_ref)

        if log.do_medium:
            log.hline("~")
            log("Initial step:")
            self.print_final("Initial")
            log(f"Entering orbital optimization of {self.acronym}...")
            log.hline(" ")
            if stepsearch["method"] == "trust-region":
                log(
                    f"{'step':>6} {'Etot':>10} {'D(Etot)':>14} {'Ecorr':>12} "
                    f"{'D(Ecorr)':>14} {'Max(Grad)':>12} {'|Grad|':>8} "
                    f"{'TrustRegion':>14}"
                )
            else:
                log(
                    f"{'step':>6} {'Etot':>10} {'D(Etot)':>14} {'Ecorr':>12} "
                    f"{'D(Ecorr)':>14} {'Max(Grad)':>12} {'|Grad|':>8} "
                    f"{'Step':>14}"
                )
        i = 0

        #
        # Extract reset option from kwargs and remove them as they are not
        # accepted in the `RStepSearch` class
        #
        reset_trust_radius = stepsearch.pop("reset")
        check_type("reset", reset_trust_radius, int)

        #
        # Initialize step search
        #
        stepsearch_ = RStepSearch(self.lf, **stepsearch)
        while i < maxiter["orbiter"]:
            #
            # Copy energies from previous iteration step
            #
            e_tot_old = copy(e_tot)
            e_corr_old = copy(e_corr)

            #
            # Calculate orbital gradient and diagonal approximation to the Hessian
            #
            kappa, gradient, hessian = self.orbital_rotation_step(
                lshift, pos, orbitaloptimizer
            )

            #
            # Apply step search to orbital rotation step 'kappa'
            #
            stepsearch_(
                self,
                one,
                two,
                orb,
                **{
                    "kappa": kappa,
                    "thresh": thresh,
                    "maxiter": maxiter,
                    "gradient": gradient,
                    "hessian": hessian,
                    "guess": initial_guess["t_p"],
                    "guesslm": initial_guess["l_p"],
                    "solver": solver,
                    "indextrans": indextrans,
                    "orbitaloptimizer": orbitaloptimizer,
                },
            )

            #
            # reorder orbitals according to natural occupation numbers
            # works only for variational orbital optimization
            #
            if sort and orbitaloptimizer == "variational":
                # Decide if orbital sorting is enforced
                force = sort == "force"
                # We only sort if the Aufbau occupation changes or if enforced
                # Orbitals will also be sorted in final iterations
                # NOTE: This works fine for pCCD, but might not be the case for
                # other geminal models.
                orbital_sorting = self.sort_natural_orbitals(
                    orb, skip_if_aufbau=True, force=force
                )
                if orbital_sorting:
                    # Recalculate WFN:
                    self.solve_model(
                        one,
                        two,
                        orb,
                        **{
                            "maxiter": maxiter,
                            "thresh": thresh,
                            "guess": initial_guess["t_p"],
                            "guesslm": initial_guess["l_p"],
                            "solver": solver,
                            "indextrans": indextrans,
                            "orbitaloptimizer": orbitaloptimizer,
                        },
                    )

            e_tot = self.compute_total_energy()
            e_corr = self.compute_correlation_energy()
            e_ref = self.compute_reference_energy()

            e_dict = {"e_tot": e_tot, "e_corr": e_corr, "e_ref": e_ref}
            self.energy = e_dict
            #
            # Update IOData container
            #
            self.checkpoint.update("e_core", self.e_core)
            self.checkpoint.update("e_tot", e_tot)
            self.checkpoint.update("e_corr", e_corr)
            self.checkpoint.update("e_ref", e_ref)

            #
            # Print information of iteration step
            #
            if log.do_medium:
                if stepsearch["method"] == "trust-region":
                    log(
                        f"{(i + 1):>5} {e_tot:> 14.8f} {(e_tot - e_tot_old):> 12.8f} "
                        f"{e_corr:> 14.8f} {(e_corr - e_corr_old):> 12.8f} "
                        f"{gradient.get_max():>10.5f} {gradient.norm():>10.2e} "
                        f"{stepsearch_.trustradius:>10.2e}"
                    )
                else:
                    log(
                        f"{(i + 1):>5} {e_tot:> 14.8f} {(e_tot - e_tot_old):> 12.8f} "
                        f"{e_corr:> 14.8f} {(e_corr - e_corr_old):> 12.8f} "
                        f"{gradient.get_max():>10.5f} {gradient.norm():>10.2e} "
                        f"{stepsearch_.alpha:>10.2e}"
                    )

            #
            # Checkpoint for orbitals
            #
            if (i + 1) % checkpoint == 0 and checkpoint > 0:
                self.checkpoint.to_file(checkpoint_fn)

            #
            # Check convergence
            #
            if self.check_convergence(e_tot, e_tot_old, gradient, thresh):
                if log.do_medium:
                    log.hline(" ")
                    log(
                        f"Orbital optimization converged in {(i + 1)} iterations"
                    )
                    log.hline(" ")
                self.checkpoint.update("converged", True)
                break
            if self.check_stepsearch(stepsearch_):
                if log.do_medium:
                    log.hline(" ")
                    log("Trustradius too small. Orbital optimization aborted!")
                    log.hline(" ")
                self.checkpoint.update("converged", False)
                break
            #
            # Reset trustradius if a specific number of iterations is used
            # We do it here as we do not want to touch the original stepsearch
            # implementation. An OO-pCCD calculation might converge slowly.
            # Until this problem is fixed, we simply reset the current value
            # of the trustradius to its original value. It is not the best
            # solution, but it works.
            #
            if (i + 1) % reset_trust_radius == 0.0:
                stepsearch_.trustradius = stepsearch_.maxtrustradius
            # go to next iteration
            i = i + 1

        #
        # Check convergence if i = maxorbiter:
        # Don't raise annoying ValueError
        #
        if i >= maxiter["orbiter"] and i > 0:
            if not self.check_convergence(e_tot, e_tot_old, gradient, thresh):
                if log.do_medium:
                    log.hline(" ")
                    log.warn(
                        f"Orbital optimization NOT converged in {i} iterations"
                    )
                self.checkpoint.update("converged", False)
        self.norbiter = i

        #
        # After final iterations, sort orbitals (if supported)
        #
        if sort and orbitaloptimizer == "variational":
            # Decide if orbital sorting is enforced
            force = sort == "force"
            # We sort whenever occupation numbers are not in decreasing order
            orbital_sorting = self.sort_natural_orbitals(
                orb, skip_if_aufbau=False, force=force
            )
            if orbital_sorting:
                if log.do_medium:
                    log(
                        "Resorting orbitals according to occupation numbers and",
                        "recalculating wavefunction and energies",
                    )
                    log(" ")
                # Recalculate WFN:
                self.solve_model(
                    one,
                    two,
                    orb,
                    **{
                        "maxiter": maxiter,
                        "thresh": thresh,
                        "guess": initial_guess["t_p"],
                        "guesslm": initial_guess["l_p"],
                        "solver": solver,
                        "indextrans": indextrans,
                        "orbitaloptimizer": orbitaloptimizer,
                    },
                )
            # Update all energies for sorted orbitals
            e_tot = self.compute_total_energy()
            e_corr = self.compute_correlation_energy()
            e_ref = self.compute_reference_energy()

            e_dict = {"e_tot": e_tot, "e_corr": e_corr, "e_ref": e_ref}
            self.energy = e_dict
            #
            # Update IOData container
            #
            self.checkpoint.update("e_core", self.e_core)
            self.checkpoint.update("e_tot", e_tot)
            self.checkpoint.update("e_corr", e_corr)
            self.checkpoint.update("e_ref", e_ref)
        #
        # Update IOData container
        #
        self.checkpoint.update("niter_orb", i)
        self.checkpoint.update("overlap", self.compute_overlap())

        #
        # Print final information
        #
        if log.do_medium:
            self.print_final()
            self.dump_final(
                orb, printoptions, dumpci, checkpoint, checkpoint_fn
            )

        #
        # Clean the Cache because we do not want to keep the effective Hamiltonian elements in memory
        #
        self.clear_cache()
        #
        # Load AOs again
        #
        two.load_array("eri")
        #
        # reset to init value to make multiple calls of the same instance work
        #
        self.mo2_dumped = False
        #
        # Create final container as return value
        #
        return self.checkpoint()

    #
    # Functions for orbital optimization (except gradient/Hessian):
    #
    def compute_rotation_matrix(self, coeff):
        """Determine orbital rotation matrix for (oo), (vo), and (vv) blocks

        **Arguments:**

        coeff
             The nonreduntant orbital rotations k_pq (1-dim np.array). The
             elements are sorted w.r.t. lower triangular indices (p>q).
        """
        nc = self.occ_model.ncore[0]
        na = self.occ_model.nact[0]

        indl = np.tril_indices(na, -1)
        # account for frozen core
        kappa = self.lf.create_two_index(na + nc, na + nc)
        kappa.assign(coeff, indl, begin0=nc, begin1=nc)
        #
        # k_pq = -k_qp
        #
        kappa.iadd_t(kappa, -1.0)

        out = compute_unitary_matrix(kappa)
        return out

    def orbital_rotation_step(
        self, lshift=1e-8, positive=True, optimizer="variational"
    ):
        """Get orbital rotation step (Newton--Raphson)

        **Arguments:**


        **Optional arguments:**

        lshift
            Level shift (float) for approximate Hessian added to small elements
            (default 1e-8)

        positive
            (boolean) Make all elements of Hessian positive if set to True
            (default True)

        optimizer
            Orbital otimization method (str) (default 'variational')

        """
        check_options("orbitaloptimizer", optimizer, "variational", "ps2c")
        #
        # Switch between different orbital optimization schemes
        #
        ps2c = optimizer == "ps2c"
        #
        # Calculate orbital gradient and diagonal approximation to the Hessian
        #
        if log.do_high:
            log("Calculating orbital gradient")
        grad = self.compute_orbital_gradient(ps2c)
        #
        # We use a diagonal Hessian
        #
        if log.do_high:
            log("Calculating orbital hessian")
        hessian = self.compute_orbital_hessian(lshift, positive, ps2c)
        #
        # Orbital rotation step
        #
        kappa = grad.divide(hessian, -1.0)

        return kappa, grad, hessian

    #
    # Calculate orbital gradient for OOGeminal model (oo,vo,vv):
    #
    @timer.with_section("OOGeminal: gradient")
    def compute_orbital_gradient(self, ps2c=False):
        """Determine orbital gradient for all non-reduntant orbital rotations
        (oo,vo,vv).

        **Optional arguments:**

        ps2c
             (boolean) If True, switches to PS2c orbital optimization
             (default False)
        """
        na = self.occ_model.nact[0]

        one = self.from_cache("t")
        gpqrq = self.from_cache("gpqrq")
        mo2 = self.from_cache("mo2")

        oo = self.get_range("oo")
        vv = self.get_range("vv")
        ov = self.get_range("ov")
        vo = self.get_range("vo")
        #
        # get optimal contraction option
        #
        opt = None
        if isinstance(mo2, CholeskyFourIndex):
            opt = "td"
        #
        # Get 1- and 2-RDMs
        #
        self.clear_dm()
        if ps2c:
            self.update_ndm("one_dm_ps2")
            self.update_ndm("two_dm_pqpq")
            self.update_ndm("two_dm_ppqq")
            onedm = self.one_dm_ps2
            twodmpqpq = self.two_dm_pqpq
            twodmppqq = self.two_dm_ppqq
        else:
            self.update_ndm("one_dm_response")
            self.update_ndm("two_dm_rpqpq")
            self.update_ndm("two_dm_rppqq")
            onedm = self.one_dm_response
            twodmpqpq = self.two_dm_rpqpq
            twodmppqq = self.two_dm_rppqq
        #
        # Update IOData container
        #
        self.checkpoint.update("dm_1", onedm)
        self.checkpoint.update("dm_2", {"pqpq": twodmpqpq, "ppqq": twodmppqq})

        #
        # Orbital gradient g_ut
        #
        gradient = self.lf.create_two_index(na, na)

        #
        # Symmetrize G(amma)_ppqq 2-RDM. This reduces the number of operations
        #
        two_dm_av = twodmppqq.copy()
        two_dm_av.symmetrize()
        #
        # Substract G(amma)_pqpq to reduce the number of operations for exchange terms
        #
        two_dm_av.iadd(twodmpqpq, factor=-1.0)
        #
        # L_uptp*G_up (Coulomb part)
        #
        gpqrq.contract("abc,ab->ac", twodmpqpq, gradient, factor=8.0)
        #
        # <tu|pp>*G_up (incl. exchange part)
        #
        mo2.contract(
            "abcc,ac->ab", two_dm_av, gradient, factor=4.0, select=opt
        )
        #
        # h_ut g_tt
        #
        one.contract("ab,a->ab", onedm, gradient, factor=4.0)
        #
        # Add permutation
        #
        gradient.iadd_t(gradient, -1.0)

        ind = np.tril_indices(na, -1)

        # TODO: This is a quick hack and should be cleaned up in the future
        if self.freezerot is not None:
            if "vv" in self.freezerot:
                gradient.assign(0.0, **vv)
            if "oo" in self.freezerot:
                gradient.assign(0.0, **oo)
            if "ov" in self.freezerot:
                gradient.assign(0.0, **ov)
                gradient.assign(0.0, **vo)

        #
        # return only lower triangle
        #
        return gradient.ravel(ind=ind)

    #
    # Approximate diagonal Hessian for OOGeminal model:
    #
    def compute_orbital_hessian(self, lshift=1e-8, positive=False, ps2c=False):
        """Construct diagonal approximation to Hessian for orbital optimization.

        **Optional arguments:**

        lshift
             Level shift (float) (default 1e-8)

        positive
             Set all elements positive (boolean) (default False)

        ps2c
             (boolean) If True, switches to PS2c orbital optimization
             (default False)
        """
        na = self.occ_model.nact[0]

        #
        # Get effective Hamiltonian elements
        #
        one = self.from_cache("t")
        vpq = self.from_cache("lpqpq")
        vpp = self.from_cache("gppqq")
        vmat = self.from_cache("gpqpq")
        vmata = self.from_cache("gppqq")

        #
        # Get 1- and 2-RDMs
        #
        self.clear_dm()
        if ps2c:
            self.update_ndm("one_dm_ps2")
            self.update_ndm("two_dm_pqpq")
            self.update_ndm("two_dm_ppqq")
            onedm = self.one_dm_ps2
            twodmpqpq = self.two_dm_pqpq
            twodmppqq = self.two_dm_ppqq
        else:
            self.update_ndm("one_dm_response")
            self.update_ndm("two_dm_rpqpq")
            self.update_ndm("two_dm_rppqq")
            onedm = self.one_dm_response
            twodmpqpq = self.two_dm_rpqpq
            twodmppqq = self.two_dm_rppqq

        #
        # Symmetrize G(amma)_ppqq 2-RDM
        #
        two_dm_av = twodmppqq.copy()
        two_dm_av.symmetrize()
        #
        # Modify diagonal elements to simplify contractions
        #
        two_dm_av.assign_diagonal(0.0)
        twodmpqpq.assign_diagonal(0.0)

        #
        # Calculate additional effective Hamiltonian elements
        #
        vmatdiag = vmat.copy_diagonal()
        one_diag = one.copy_diagonal()
        two_c = self.lf.create_one_index(na)
        two_ca = self.lf.create_one_index(na)
        vpq.contract("ab,ab->a", twodmpqpq, two_c)
        vpp.contract("ab,ab->a", two_dm_av, two_ca)

        #
        # Diagonal orbital Hessian hessian_pq = hessian_(pq,pq)
        #
        hessian = self.lf.create_two_index(na, na)
        #
        # <qt> G_pt
        #
        hessian.iadd_dot(vpq, twodmpqpq, 4.0)
        #
        # <pt> G_qt
        #
        hessian.iadd_dot(twodmpqpq, vpq, 4.0)
        #
        # <qt> G_qt
        #
        hessian.iadd(two_c, -4.0)
        #
        # <pt> G_pt
        #
        hessian.iadd_t(two_c, -4.0)
        #
        # <qt> G_pt
        #
        hessian.iadd_dot(two_dm_av, vpp, 4.0)
        #
        # <pt> G_qt
        #
        hessian.iadd_dot(vpp, two_dm_av, 4.0)
        #
        # <qt> G_qt
        #
        hessian.iadd(two_ca, -4.0)
        #
        # <pt> G_pt
        #
        hessian.iadd_t(two_ca, -4.0)
        #
        # <pq> G_pq
        #
        hessian.iadd_mult(vmat, twodmpqpq, 8.0)
        hessian.iadd_mult(vmata, twodmpqpq, -8.0)
        hessian.iadd_mult(vpp, twodmpqpq, -16.0)
        hessian.iadd_mult(vmat, two_dm_av, -8.0)
        hessian.iadd_mult(vpp, two_dm_av, -8.0)
        #
        # <ppqq> G_pp
        #
        vpp.contract("ab,a->ab", onedm, hessian, factor=8.0)
        vpp.contract("ab,b->ab", onedm, hessian, factor=8.0)
        #
        # <qq> g_pp
        #
        hessian.iadd_one_mult(one_diag, onedm, 4.0, True, False)
        #
        # <pp> g_qq
        #
        hessian.iadd_one_mult(onedm, one_diag, 4.0, True, False)
        #
        # <qq> g_qq
        #
        hessian.iadd_one_mult(one_diag, onedm, -4.0, True, True)
        #
        # <pp> g_pp
        #
        hessian.iadd_one_mult(onedm, one_diag, -4.0, False, False)
        vmat.contract("ab,a->ab", onedm, hessian, factor=4.0)
        vmat.contract("ab,b->ab", onedm, hessian, factor=4.0)
        hessian.iadd_one_mult(vmatdiag, onedm, -4.0, True, True)
        hessian.iadd_one_mult(vmatdiag, onedm, -4.0, False, False)

        #
        # Make everything positive
        #
        if positive:
            hessian.iabs()
        #
        # Add levelshift:
        #
        if lshift:
            hessian.iadd_shift(lshift)

        ind = np.tril_indices(na, -1)

        return hessian.ravel(ind=ind)

    @timer.with_section("OOGeminal: Hessian")
    def get_exact_hessian(self, mo1, mo2):
        """Construct exact Hessian for orbital optimization of restricted OOGeminal model.

        The usage of the exact orbital Hessian for the orbital optimization
        is currently not supported. The exact Hessian can only be evaluated
        a posteriori.

        **Arguments**

        mo1, mo2
             The 1- and 2-el integrals in the MO basis (TwoIndex and
             FourIndex instances)
        """
        na = self.occ_model.nact[0]

        if log.do_medium:
            log("Calculating exact Hessian")
        #
        # exact orbital Hessian output hessian_pq,rs
        #
        hessian = self.denself.create_four_index(na)
        if isinstance(mo2, CholeskyFourIndex):
            mo2 = mo2.get_dense()

        #
        # Get response DMs
        #
        self.clear_dm()
        self.update_ndm("one_dm_response")
        self.update_ndm("two_dm_rpqpq")
        self.update_ndm("two_dm_rppqq")
        dm1 = self.one_dm_response.copy()
        dm2pqpq = self.two_dm_rpqpq.copy()
        dm2pqpqex = self.two_dm_rpqpq.copy()
        dm2ppqq = self.two_dm_rppqq.copy()
        #
        # Symmetrize 2DM
        #
        dm2av = dm2ppqq.copy()
        dm2av.symmetrize()
        #
        # Reset diagonal elements of DMs
        #
        dm2pqpqex.assign_diagonal(0.0)
        dm2pqpq.assign_diagonal(dm1)
        dm2av.assign_diagonal(0.0)

        #
        # temporary storage
        #
        ind2 = self.lf.create_two_index(na)
        ind30 = self.lf.create_three_index(na)
        ind31 = self.lf.create_three_index(na)

        if log.do_medium:
            log(" Direct part...")
        # Direct part
        # (1)
        # ab
        mo2.contract("abcd,cd->acbd", dm2pqpq, hessian, factor=4.0)
        mo2.contract("abcd,ab->acdb", dm2pqpq, hessian, factor=-4.0)
        mo2.contract("abcd,cd->acdb", dm2pqpq, hessian, factor=-4.0)
        mo2.contract("abcd,ab->acbd", dm2pqpq, hessian, factor=4.0)
        # (2)
        # ab
        mo2.contract("abcd,cb->acdb", dm2pqpq, hessian, factor=4.0)
        mo2.contract("abcd,ad->acbd", dm2pqpq, hessian, factor=-4.0)
        mo2.contract("abcd,cb->acbd", dm2pqpq, hessian, factor=-4.0)
        mo2.contract("abcd,ad->acdb", dm2pqpq, hessian, factor=4.0)
        # (3)
        mo2.contract("abcd,bd->abcd", dm2av, hessian, factor=4.0)
        mo2.contract("abcd,ad->abcd", dm2av, hessian, factor=-4.0)
        mo2.contract("abcd,bd->abdc", dm2av, hessian, factor=-4.0)
        mo2.contract("abcd,ac->abcd", dm2av, hessian, factor=4.0)
        mo2.contract("abcd,bc->abdc", dm2av, hessian, factor=4.0)
        mo2.contract("abcd,ac->abdc", dm2av, hessian, factor=-4.0)
        mo2.contract("abcd,bc->abcd", dm2av, hessian, factor=-4.0)
        mo2.contract("abcd,ad->abdc", dm2av, hessian, factor=4.0)
        # Apq,qw (pw) (qv) (-qw) (-pv)
        mo1.contract("ab,b->ab", dm1, ind2, factor=4.0)
        # ab
        mo2.contract("abcb,cb->ac", dm2pqpq, ind2, factor=2.0)
        mo2.contract("abcb,ab->ac", dm2pqpq, ind2, factor=2.0)
        mo2.contract("abcc,bc->ba", dm2av, ind2, factor=2.0)
        mo2.contract("abcc,bc->ab", dm2av, ind2, factor=2.0)
        # Apq,pw (pq,pw) (-pq,vp)
        mo1.contract("ab,c->cab", dm1, ind30, factor=4)
        # ab
        mo2.contract("abcb,db->dac", dm2pqpq, ind30, factor=4.0)
        mo2.contract("abcc,dc->dab", dm2av, ind30, factor=4.0)
        # Apq,vq (pq,vq) (-pq,qw)
        mo1.contract("ab,c->acb", dm1, ind31, factor=4)
        # ab
        mo2.contract("abcb,db->adc", dm2pqpq, ind31, factor=4.0)
        mo2.contract("abcc,dc->adb", dm2av, ind31, factor=4.0)

        if log.do_medium:
            log(" Exchange part...")
        # Exchange part
        #
        # calculate <pq|rs>-<pq|sr>
        #
        mo2.iadd_exchange()
        # (1)
        # aa
        mo2.contract("abcd,cd->acbd", dm2pqpqex, hessian, factor=4.0)
        mo2.contract("abcd,ab->acdb", dm2pqpqex, hessian, factor=-4.0)
        mo2.contract("abcd,cd->acdb", dm2pqpqex, hessian, factor=-4.0)
        mo2.contract("abcd,ab->acbd", dm2pqpqex, hessian, factor=4.0)
        # (2)
        # aa
        mo2.contract("abcd,cb->acdb", dm2pqpqex, hessian, factor=4.0)
        mo2.contract("abcd,ad->acbd", dm2pqpqex, hessian, factor=-4.0)
        mo2.contract("abcd,cb->acbd", dm2pqpqex, hessian, factor=-4.0)
        mo2.contract("abcd,ad->acdb", dm2pqpqex, hessian, factor=4.0)
        # Apq,qw (pw) (qv) (-qw) (-pv)
        # aa
        mo2.contract("abcb,cb->ac", dm2pqpqex, ind2, factor=2.0)
        mo2.contract("abcb,ab->ac", dm2pqpqex, ind2, factor=2.0)
        # Apq,pw (pq,pw) (-pq,vp)
        # aa
        mo2.contract("abcb,db->dac", dm2pqpqex, ind30, factor=4.0)
        # Apq,vp (pq,vq) (-pq,qw)
        # aa
        mo2.contract("abcb,db->adc", dm2pqpqex, ind31, factor=4.0)

        # release memory
        del mo2

        if log.do_medium:
            log(" Collecting terms...")
        #
        # collect 2- and 3-index terms
        #
        # Apq,vq
        ind2.expand("ac->abcb", hessian, factor=-1.0)
        # Apq,qw
        ind2.expand("ac->abbc", hessian)
        # Apq,vp
        ind2.expand("bc->abca", hessian)
        # Apq,pw
        ind2.expand("bc->abac", hessian, factor=-1.0)
        # Apq,vw (pq,pw) (-pq,vp)
        ind30.expand("abc->abac", hessian)
        ind30.expand("abc->abca", hessian, factor=-1.0)
        # Apq,vw (pq,vq) (-pq,qw)
        ind31.expand("abc->abcb", hessian)
        ind31.expand("abc->abbc", hessian, factor=-1.0)

        #
        # reorder elements (p,q,r,s)->(pq,rs)
        #
        dim = (na * (na - 1)) // 2
        tril = np.tril_indices(na, -1)
        out = self.lf.create_two_index(dim, dim)
        # FIXME: use matrix class
        out.array[:] = (hessian.array[:, :, tril[0], tril[1]])[tril]

        # release memory
        del hessian
        if log.do_medium:
            log("...Done")

        return out.array

    def sort_natural_orbitals(
        self, orb: Orbital, skip_if_aufbau: bool = False, force: bool = False
    ) -> bool:
        """Sort orbitals w.r.t. the natural occupation numbers.
        Orbitals are only sorted if order of orbitals changes. Sorting can be
        suppressed if skip_if_aufbau is set to False.

        Args:
            orb (Orbital): The AO/MO coefficients (natural orbitals) and the natural
                           occupation numbers (Orbital instance)
            skip_if_aufbau (bool, optional): Sort only if Aufbau occupation
                                             changes. Defaults to False.
            sort (bool): Force sorting of orbitals if set to True. Defaults to False.

        Returns:
            bool: True if orbitals have been resorted, False otherwise
        """
        ncore = self.occ_model.ncore[0]
        nacto = self.occ_model.nacto[0]
        nact = self.occ_model.nact[0]

        #
        # Take natural occupation numbers from orb.occupations
        #
        onedm = self.lf.create_one_index()
        onedm.assign(orb.occupations)
        order = onedm.sort_indices(begin0=ncore)
        orderref = np.arange(nact)
        if not (order == orderref).all():
            # Check if occupied orbital indices change
            check_aufbau = (order[:nacto] < nacto).all()
            # Reorder anyways if force==True, no matter of Aufbau occupation
            skip_sorting = not force and (check_aufbau and skip_if_aufbau)
            if skip_sorting:
                return False
            # Permute orbitals if their occupation changes
            orb.permute_orbitals(order, begin0=ncore)
            return True
        return False

    def check_keywords_scf(
        self, guess, solver, maxiter, dumpci, thresh, printoptions, stepsearch
    ):
        """Check dictionaries if they contain proper keys.

        **Arguments:**

        guess, solver, maxiter, dumpci, thresh, printoptions, stepseach
             See :py:meth:`OOGeminals.solve`

        """
        #
        # Check guess, values are checked separately
        #
        for key in guess:
            check_options(
                "guess", key, "type", "factor", "geminal", "lagrange"
            )
        #
        # Check solver
        #
        for key in solver:
            check_options("solver", key, "wfn", "lagrange")
        #
        # Check maxiter
        #
        for key, value in maxiter.items():
            check_options("maxiter", key, "wfniter", "orbiter")
            check_type("maxiter", value, int)
        #
        # Check thresh
        #
        for key, value in thresh.items():
            check_options(
                "thresh", key, "wfn", "energy", "gradientnorm", "gradientmax"
            )
            check_type("thresh", value, float)
            if value < 0:
                raise ValueError(
                    f"Negative convergence threshold for {key} is not allowed!"
                )
        #
        # Check printoptions
        #
        for key, value in printoptions.items():
            check_options(
                "printoptions",
                key,
                "geminal",
                "geminal_coefficients",
                "threshold",
                "excitationlevel",
            )
            if key in ["geminal", "geminal_coefficients"]:
                check_options("printoptions.geminal", value, False, True, 0, 1)
                check_options(
                    "printoptions.geminal_coefficients",
                    value,
                    False,
                    True,
                    0,
                    1,
                )
            elif key == "threshold":
                check_type("printoptions.threshold", value, float)
            elif key == "excitationlevel":
                check_type("printoptions.excitationlevel", value, int)

        #
        # Check dumpci
        #
        for key, value in dumpci.items():
            check_options(
                "dumpci", key, "amplitudestofile", "amplitudesfilename"
            )
            if key == "amplitudestofile":
                check_options(
                    "dumpci.amplitudestofile", value, False, True, 0, 1
                )
            if key == "amplitudesfilename":
                check_type("dumpci.amplitudesfilename", value, str)
        #
        # Check stepsearch, values are checked separately
        #
        for key in stepsearch:
            check_options(
                "stepsearch",
                key,
                "method",
                "optimizer",
                "alpha",
                "c1",
                "minalpha",
                "maxiterouter",
                "maxiterinner",
                "maxeta",
                "mineta",
                "upscale",
                "downscale",
                "trustradius",
                "maxtrustradius",
                "threshold",
                "reset",
            )

    def print_options_scf(
        self,
        guess,
        solver,
        maxiter,
        lshift,
        stepsearch,
        thresh,
        printoptions,
        checkpoint,
        checkpoint_fn,
        indextrans,
        orbitaloptimizer,
        sort,
    ):
        """Print optimization options.

        **Arguments:**

        See :py:meth:`OOGeminals.solve`

        Variables used in this method:
         :nacto:    number of electron pairs
                     (abbreviated as no)
         :nactv:     number of (active) virtual orbitals in the principal configuration
                     (abbreviated as nv)
         :ncore:     number of core orbials
                     (abbreviated as nc)

        """
        nc = self.occ_model.ncore[0]
        no = self.occ_model.nacto[0]
        nv = self.occ_model.nactv[0]

        indextrans_ = "optimal" if indextrans is None else indextrans

        if log.do_medium:
            log.hline()
            log(" ")
            log(f"Entering OO{self.acronym} optimization ({self.comment}):")
            log(" ")
            log.hline()
            log("OPTIMIZATION PARAMETERS:")
            log(f"Number of frozen cores:        {nc}")
            log(f"Number of active pairs:        {no}")
            log(f"Number of active virtuals:     {nv}")
            log("Initial guess:")
            log(f"  type:                        {guess['type']}")
            log(f"  scaling factor:              {guess['factor']:2.3f}")
            log("Solvers:")
            log(f"  wavefunction amplitudes:     {solver['wfn']}")
            log(f"  Lagrange multipliers:        {solver['lagrange']}")
            log(f"  orbital optimization:        {orbitaloptimizer}")
            log(f"Number of iterations:          {maxiter['orbiter']}")
            log(f"Checkpointing:                 {checkpoint}")
            log(f"Checkpoint file:               {checkpoint_fn}")
            log(f"4-index transformation:        {indextrans_}")
            log(f"Level shift:                   {lshift:3.3e}")
            log(
                f"Sorting natural orbitals:      {sort} (only in last iteration",
                "or for different Aufbau occupation)",
            )
            if stepsearch["method"] == "trust-region":
                log("Apply trust region:")
                log(
                    f"  initial trust radius:        {stepsearch['trustradius']:1.3f}"
                )
                log(
                    f"  maximum trust radius:        {stepsearch['maxtrustradius']:2.3f}"
                )
                log(
                    f"  upper trust ratio bound:     {stepsearch['maxeta']:1.2e}"
                )
                log(
                    f"  lower trust ratio bound:     {stepsearch['mineta']:1.2e}"
                )
                log(
                    f"  upper scaling factor:        {stepsearch['upscale']:1.2e}"
                )
                log(
                    f"  lower scaling factor:        {stepsearch['downscale']:1.2e}"
                )
                log(
                    f"  max number of iterations:    {stepsearch['maxiterouter']}"
                )
                log(f"  reset after # of iterations: {stepsearch['reset']}")
                log(
                    f"  max number of optimizations: {stepsearch['maxiterinner']}"
                )
                log(
                    f"  optimization threshold:      {stepsearch['threshold']:1.2e}"
                )
                log(
                    f"  optimizer:                   {stepsearch['optimizer']}"
                )
            elif stepsearch["method"] == "backtracking":
                log("Apply line search:")
                log(f"  line search method:          {stepsearch['method']}")
                log(
                    f"  initial scaling factor:      {stepsearch['alpha']:1.3f}"
                )
                log(
                    f"  contraction factor:          {stepsearch['downscale']:1.3f}"
                )
                log(f"  c1 factor:                   {stepsearch['c1']:1.3e}")
                log(
                    f"  minimum scaling factor:      {stepsearch['minalpha']:1.3e}"
                )
            else:
                log("No step search selected:")
                log(
                    f"  scaling factor:              {stepsearch['alpha']:1.3f}"
                )
            log("Optimization thresholds:")
            log(f"  wavefunction:                {thresh['wfn']:1.2e}")
            log(f"  energy:                      {thresh['energy']:1.2e}")
            log(f"  gradient:                    {thresh['gradientmax']:1.2e}")
            log(
                f"  gradient norm:               {thresh['gradientnorm']:1.2e}"
            )
            log("Printing options:")
            log(
                f"  threshold:                   {printoptions['threshold']:1.2e}"
            )
            if not printoptions["geminal_coefficients"]:
                log(
                    f"  excitation level:            {printoptions['excitationlevel']}"
                )

    def compute_objective_function(self, coeff=None):
        """Objective function for line search optimization

        **Optional arguments:**

        coeff
             See :py:meth:`RpCCDBase.compute_total_energy`
        """
        return self.compute_total_energy(coeff)
