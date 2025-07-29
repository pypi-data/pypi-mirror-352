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
# This module has been rewritten by Emil Sujkowski
# Moved here from rpccd.py
# - solve
#
# New methods:
# - Created get_guess with raise NotImplementedError to avoid conflicts with rpccd_base
#
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

"""Methods for pCCD"""

import warnings
from abc import ABC

from pybest.exceptions import ArgumentError
from pybest.geminals.geminals_base import GeminalsBase
from pybest.log import log, timer
from pybest.utility import check_options, check_type, unmask


class Geminals(GeminalsBase, ABC):
    """Class containing methods characteristic for all geminal models."""

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

    @timer.with_section("Geminal: solver")
    def solve(self, one, two, olp, orb, *args, **kwargs):
        """Optimize pCCD coefficients for some Hamiltonian.
                For restricted, closed-shell pCCD.

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
                              ``tensordot`` (default), ``cupy``, ``einsum``,
                              ``cpp``, ``opt_einsum``, or ``einsum_naive``. If
                              ``cupy`` is not available, we switch to ``tensordot``.
                 :warning: Print warnings (boolean) (default False)
                 :guess: initial guess (dictionary) containing:

                         * type: guess type (str). One of ``mp2`` (MP2 pair
                           amplitudes, default), ``random`` (random numbers),
                           ``const`` (a constant scaled by a factor)
                         * factor: a scaling factor (float) (default -0.1)
                         * geminal: external guess for geminal coefficients
                           (1-d np.array); if provided, 'type' is
                           ignored (default None)
                         * lagrange: external guess for Lagrange multipliers
                           (1-dim np.array) (default None)

                 :solver: wfn solver (dictionary) containing:

                          * wfn: wavefunction solver (str) (default ``krylov``)
                          * lagrange: Lagrange multiplier solver (str)
                            (default krylov)

                 :maxiter: max number of iterations (dictionary) containing:

                           * wfniter: maximum number of iterations (int) for wfn
                             solver (default 200)

                 :dumpci: dump ci coefficients (dictionary):

                          * amplitudestofile: write wfn amplitudes to file
                            (boolean) (default False)
                          * amplitudesfilename: (str) (default pccd_`amplitudes.dat)

                 :thresh: optimization thresholds (dictionary) containing:

                          * wfn: threshold for geminal coefficients (float)
                            (default 1e-12)

                 :printoptions: print level (dictionary) containing:
        `
                                * geminal: (boolean), if True, geminal matrix is
                                  printed (default True)
                                * geminal_coefficients: (boolean), if True, only
                                  the largest (in absolute value) coefficients
                                  will be printed. If False, the Slater determinant
                                  expansion will be printed instead
                                * threshold: threshold for CI coefficients (float) (requires
                                  evaluation of a permanent), all coefficients
                                  (for a given excitation order) larger than
                                  'threshold' are printed (default 0.01)
                                * excitationlevel: number of excited pairs w.r.t.
                                  reference determinant for which wfn amplitudes
                                  are reconstructed (int) (default 1)

                 :e_core: (float) core energy
                 :restart: (str) filename that contains some restart amplitudes (geminal coefficient
                        are read from file)
        """
        if log.do_medium:
            log.hline("=")
            log(f"Entering {self.acronym} module")

        #
        # Assign keyword arguments
        #
        names = []

        def _helper(x, y):
            names.append(x)
            return kwargs.get(x, y)

        indextrans = _helper("indextrans", None)
        warning = _helper("warning", False)
        guess = _helper("guess", {})
        guess.setdefault("type", "mp2")
        guess.setdefault("factor", -0.1)
        guess.setdefault("geminal", None)
        guess.setdefault("lagrange", None)
        solver = _helper("solver", {})
        solver.setdefault("wfn", "krylov")
        solver.setdefault("lagrange", "krylov")
        maxiter = _helper("maxiter", {"wfniter": 200})
        dumpci = _helper("dumpci", {})
        dumpci.setdefault("amplitudestofile", False)
        dumpci.setdefault("amplitudesfilename", "pccd_amplitudes.dat")
        thresh = _helper("thresh", {"wfn": 1e-12})
        printoptions = _helper("printoptions", {})
        printoptions.setdefault("geminal", False)
        printoptions.setdefault("geminal_coefficients", True)
        printoptions.setdefault("threshold", 0.01)
        printoptions.setdefault("excitationlevel", 1)
        restart = _helper("restart", False)
        e_core = _helper("e_core", None)

        #
        # orb_a is NOT assigned here; check for allowed keywords only
        #

        #
        # Check kwargs
        #
        for key, _value in kwargs.items():
            if key not in names:
                raise ArgumentError(f"Unknown keyword argument {key}")

        #
        # Check dictionaries in keyword arguments
        #
        self.check_keywords(
            guess, solver, maxiter, dumpci, thresh, printoptions
        )
        check_options("warning", warning, False, True, 0, 1)

        if not warning:
            warnings.filterwarnings("ignore")

        #
        # Print optimization parameters
        #
        if log.do_medium:
            self.print_options(guess, solver, thresh, printoptions, indextrans)

        #
        # Overwrite core energy using unmask function if not found in kwargs
        #
        if e_core is None:
            # Check IOData for e_core
            e_core = unmask("e_core", *args, **kwargs)
            if e_core is None:
                raise ArgumentError("Cannot find core energy in arguments.")
        self.e_core = e_core

        #
        # Generate Guess
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

        #
        # Update IOData container
        #
        self.checkpoint.update("e_core", self.e_core)
        self.checkpoint.update("orb_a", orb.copy())
        self.checkpoint.update("olp", olp)

        #
        # Dump AOs to file
        #
        self.dump_eri(two)
        #
        # Solve for wavefunction
        #
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
                "orbitaloptimizer": False,
            },
        )

        #
        # Final print statements:
        #
        if log.do_medium:
            self.print_final()
            # Dump final result but do not generate checkpoint file (-1)
            self.dump_final(orb, printoptions, dumpci, -1)

        #
        # Sanity check for correlation energy:
        #
        if self.compute_correlation_energy() > 0:
            raise ValueError(
                "Warning: Final correlation energy is positive! Improve initial guess!"
            )

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
        self.checkpoint.update("overlap", self.compute_overlap())

        #
        # Clean the Cache because we do not want to keep the effective Hamiltonian elements in memory
        #
        self.clear_cache()
        #
        # Load AOs again
        #
        two.load_array("eri")
        #
        # Create final container as return value
        #
        return self.checkpoint()

    def check_keywords(
        self, guess, solver, maxiter, dumpci, thresh, printoptions
    ):
        """Check dictionaries if they contain proper keys.

        **Arguments:**

        guess, solver, maxiter, dumpci, thresh, printoptions
             See :py:meth:`Geminals.solve`

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
            check_options("maxiter", key, "wfniter")
            check_type("maxiter", value, int)
        #
        # Check thresh
        #
        for key, value in thresh.items():
            check_options("thresh", key, "wfn")
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

    def print_options(self, guess, solver, thresh, printoptions, indextrans):
        """Print optimization options.

        **Arguments:**

        guess, solver, maxiter, thresh, printoptions, indextrans
             See :py:meth:`Geminals.solve`

        Variables used in this method:
         :nacto:    number of electron pairs
                     (abbreviated as no)
         :nactv:     number of (active) virtual orbitals in principal configuration
                     (abbreviated as nv)
         :ncore:     number of core orbitals
                     (abbreviated as nc)
        """
        nc = self.occ_model.ncore[0]
        no = self.occ_model.nacto[0]
        nv = self.occ_model.nactv[0]

        indextrans_ = "optimal" if indextrans is None else indextrans

        log.hline()
        log(" ")
        log(f"Entering {self.acronym} optimization ({self.comment}):")
        log(" ")
        log.hline()
        log("OPTIMIZATION PARAMETERS:")
        log(f"Number of frozen cores:      {nc}")
        log(f"Number of active pairs:      {no}")
        log(f"Number of active virtuals:   {nv}")
        log(f"4-index transformation:      {indextrans_}")
        log("Initial guess:")
        log(f"  type:                        {guess['type']}")
        log(f"  scaling factor:              {guess['factor']:2.3f}")
        log("Solvers:")
        log(f"  wavefunction amplitudes:   {solver['wfn']}")
        log(f"  lambda amplitudes:         {solver['lagrange']}")
        log("Optimization thresholds:")
        log(f"  wavefunction:              {thresh['wfn']:1.2e}")
        log("Printing options:")
        log(f"  threshold:                   {printoptions['threshold']:1.2e}")
        if not printoptions["geminal_coefficients"]:
            log(
                f"  excitation level:            {printoptions['excitationlevel']}"
            )
