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
"""Basic Self-Consistent Field (SCF) algorithm"""

from abc import ABC, abstractmethod
from typing import Any

import numpy as np

from pybest.exceptions import ArgumentError, UnknownHamiltonian
from pybest.featuredlists import OneBodyHamiltonian, TwoBodyHamiltonian
from pybest.iodata import IOData
from pybest.linalg.base import FourIndex, Orbital, TwoIndex
from pybest.log import log
from pybest.scf.guess import guess_core_hamiltonian
from pybest.scf.hamiltonian import RScfHam, UScfHam
from pybest.scf.observable import (
    RDirectTerm,
    RExchangeTerm,
    RTwoIndexTerm,
    UDirectTerm,
    UExchangeTerm,
    UTwoIndexTerm,
)
from pybest.scf.scf_cdiis import CDIISSCFSolver
from pybest.scf.scf_ediis import EDIISSCFSolver
from pybest.scf.scf_ediis2 import EDIIS2SCFSolver
from pybest.scf.scf_plain import PlainSCFSolver
from pybest.scf.utils import compute_1dm_hf
from pybest.utility import check_options, project_orbitals


class HF(ABC):
    """A wrapper class to perform RHF/SCF calculations."""

    kind = "orb"  # input/output variable are the orbitals

    def __init__(self, lf, occ_model):
        """
        *Arguments:**

        lf
             The linalg factory to be used.

        occ_model
             Model for the orbital occupations.
        """
        self.lf = lf
        self.occ_model = occ_model
        self.maxiter = 128
        self.threshold = 1e-8
        self.skip_energy = False
        self.prune_old_states = False
        self.hamiltonian = None

    @property
    def lf(self):
        """Linear algebra factory instance."""
        return self._lf

    @lf.setter
    def lf(self, args):
        self._lf = args

    @property
    def occ_model(self):
        """Occupation model instance."""
        return self._occ_model

    @occ_model.setter
    def occ_model(self, args):
        self._occ_model = args

    @property
    def maxiter(self):
        """Maximum number of iterations."""
        return self._maxiter

    @maxiter.setter
    def maxiter(self, args):
        self._maxiter = args

    @property
    def threshold(self):
        """Convergence threshold."""
        return self._threshold

    @threshold.setter
    def threshold(self, args):
        self._threshold = args

    @property
    def skip_energy(self):
        """Informs if energy computations should be skipped."""
        return self._skip_energy

    @skip_energy.setter
    def skip_energy(self, args):
        self._skip_energy = args

    @property
    def prune_old_states(self):
        """Used in DIIS."""
        return self._prune_old_states

    @prune_old_states.setter
    def prune_old_states(self, args):
        self._prune_old_states = args

    @staticmethod
    def get_guess(olp: TwoIndex, *args):
        """Get core Hamiltonian guess."""
        core = []
        for arg in args:
            if isinstance(arg, TwoIndex):
                core.append(arg)
            elif isinstance(arg, Orbital):
                core.append(arg)

        guess_core_hamiltonian(olp, *core)

    @staticmethod
    def get_restart(filename: str, olp: TwoIndex, *orbs: tuple[Orbital, ...]):
        """Reads previous results from file."""
        old = IOData.from_file(filename)
        project_orbitals(old.olp, olp, old.orb_a, orbs[0])
        try:
            project_orbitals(old.olp, olp, old.orb_b, orbs[1])
        except (IndexError, AttributeError):
            pass

    @staticmethod
    def check_input(**kwargs: dict[str, Any]) -> None:
        """Check input parameters."""
        for name, _ in kwargs.items():
            check_options(
                name,
                name,
                "diis",
                "maxiter",
                "threshold",
                "nvector",
                "skip_energy",
                "prune_old_states",
                "restart",
            )
        diis = kwargs.get("diis", "cdiis")
        check_options("diis", diis, None, "plain", "cdiis", "ediis", "ediis2")
        nvector = kwargs.get("nvector", 6)
        if nvector < 0:
            raise ValueError(
                "Warning: At least one diis vector has to be used!"
            )

    def __call__(self, *args, **kwargs: dict[str, Any]) -> IOData:
        """Find a self-consistent set of orbitals.

        **Arguments:**

        ham1, ham2, .. , olp, orb1, orb2, ...
             A list of one and two-electron integrals forming the Hamiltonian,
             the overlap integrals and the initial orbitals.
             The order of the orbitals will always be alpha, beta.

        **Keywords:**
             Contains solver specific input parameters:
              * diis:             DIIS algorithm (default value cdiis)
              * nvector:          the number of DIIS vectors (default value 6)
              * maxiter:          Maximum number of iterations (default value
                                  128)
              * threshold:        update convergence threshold to a new value
                                  (default 1e-8)
              * skip_energy:      do not calculate energy (default value False)
              * prune_old_states: used in DIIS (default value False)
              * restart:          name of restart file (default value None)
        """
        #
        # Get keyword arguments to steer SCF behaviour
        #
        diis = kwargs.get("diis", "cdiis")
        #
        nvector = kwargs.get("nvector", 6)
        #
        self.maxiter = kwargs.get("maxiter", self.maxiter)
        #
        self.threshold = kwargs.get("threshold", self.threshold)
        #
        self.skip_energy = kwargs.get("skip_energy", self.skip_energy)
        #
        self.prune_old_states = kwargs.get(
            "prune_old_states", self.prune_old_states
        )
        #
        restart = kwargs.get("restart", None)

        #
        # Do some minimal checks
        #
        self.check_input(**kwargs)

        #
        # Sort args into Hamiltonian, orbs, and olp
        #
        ham = []
        orbs = []
        for arg in args:
            if isinstance(arg, (TwoIndex, FourIndex)):
                if arg.label == "olp":
                    olp = arg
                else:
                    ham.append(arg)
            elif isinstance(arg, (dict, float, np.integer)):
                ham.append(arg)
            elif isinstance(arg, Orbital):
                orbs.append(arg)
            else:
                raise ArgumentError(
                    f"Unknown argument {arg} in SCF function call."
                )

        #
        # Construct Hamiltonian
        #
        self.hamiltonian = self.construct_ham(ham)
        #
        # Perform initial guess or do restart
        #
        if restart is not None:
            self.get_restart(restart, olp, *orbs)
        else:
            skip_guess = orbs[0].any()
            try:
                skip_guess = orbs[1].any()
            except (IndexError, AttributeError):
                pass
            if log.do_medium:
                log.hline()
            if not skip_guess:
                self.get_guess(olp, *ham, *orbs)
            else:
                if log.do_medium:
                    log("Skipping guess since orbitals have been provided.")
            if log.do_medium:
                log.hline()

        self.occ_model.assign_occ_reference(*orbs)
        #
        # SCF solvers
        #
        try:
            diis = diis.lower()
        except AttributeError:
            pass
        if diis is None or diis == "plain":
            #
            # Plain SCF solver
            #
            scf = PlainSCFSolver(
                threshold=self.threshold,
                maxiter=self.maxiter,
                skip_energy=self.skip_energy,
            )
            out = scf(self.hamiltonian, self.lf, olp, self.occ_model, *orbs)
            #
            # Add occupation model to IOData output (to dump molden files)
            #
            out.occ_model = self.occ_model
            return out
        #
        # various DIIS solvers
        #
        dms = [compute_1dm_hf(orb) for orb in orbs]
        solver = {
            "cdiis": CDIISSCFSolver,
            "ediis": EDIISSCFSolver,
            "ediis2": EDIIS2SCFSolver,
        }
        scf = solver[diis](
            threshold=self.threshold,
            maxiter=self.maxiter,
            skip_energy=self.skip_energy,
            prune_old_states=self.prune_old_states,
            nvector=nvector,
        )
        out = scf(self.hamiltonian, self.lf, olp, self.occ_model, *dms)
        #
        # Add occupation model to IOData output (to dump molden files)
        #
        out.occ_model = self.occ_model
        #
        # Update orbitals as DIIS solver work with dms
        #
        orbs[0].assign(out.orb_a)
        if hasattr(out, "orb_b"):
            orbs[1].assign(out.orb_b)
        return out

    @abstractmethod
    def construct_ham(self, ham: FourIndex) -> None:
        """Loop over Hamiltonian list to construct SCF Hamiltonian terms."""


class RHF(HF):
    """Restricted Hartee-Fock class."""

    acronym = "RHF"
    long_name = "Restricted Hartree-Fock"

    def construct_ham(self, ham: FourIndex) -> Any:
        """Loop over Hamiltonian list to construct SCF Hamiltonian terms."""
        terms = []
        external = None
        for ham_ in ham:
            if hasattr(ham_, "label"):
                if ham_.label in OneBodyHamiltonian:
                    terms.insert(0, RTwoIndexTerm(ham_, ham_.label))
                elif ham_.label in TwoBodyHamiltonian:
                    terms.append(RDirectTerm(ham_, "hartree"))
                    terms.append(RExchangeTerm(ham_, "x_hf"))
                else:
                    raise UnknownHamiltonian(
                        f"Hamiltonian term {ham_.label} unkown."
                    )
            else:
                external = ham_

        return RScfHam(terms, external)


class UHF(HF):
    """Unrestricted Hartee-Fock class."""

    acronym = "UHF"
    long_name = "Unrestricted Hartree-Fock"

    def construct_ham(self, ham: FourIndex) -> Any:
        """Loop over Hamiltonian list to construct SCF Hamiltonian terms."""
        terms = []
        external = None
        for ham_ in ham:
            if hasattr(ham_, "label"):
                if ham_.label in OneBodyHamiltonian:
                    terms.insert(0, UTwoIndexTerm(ham_, ham_.label))
                elif ham_.label in TwoBodyHamiltonian:
                    terms.append(UDirectTerm(ham_, "hartree"))
                    terms.append(UExchangeTerm(ham_, "x_hf"))
                else:
                    raise UnknownHamiltonian(
                        f"Hamiltonian term {ham_.label} unkown."
                    )
            else:
                external = ham_

        return UScfHam(terms, external)
