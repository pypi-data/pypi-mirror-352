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
"""Optimization methods

PBQuasiNewton:  Perturbation-Based Quasi-Newton method
"""

from pybest.exceptions import ConsistencyError, UnknownOption
from pybest.log import log, timer
from pybest.utility import check_options

from .diis import DIIS


# NOTE: Use dataclasses
class ObjectView:
    """Allows to access the elements of a dictionary as object attributes.
    Note that the final object does not behave as a dictionary. This class
    allows us to access the solution of the PBQN solver as attributes to be
    compatible with common SciPy solvers.
    """

    def __init__(self, dict_):
        self.__dict__ = dict_


class PBQuasiNewton:
    """Perturbation-Based Quasi-Newton method with a diagonal Jacobian.

    Vectorfunction has to be provided in different class (called obj here)
    as vfunction (`t`) or vfunction_l (`l`).

    Both vector function and jacobian have to be instances of DenseOneIndex.

    The energy is calculated in obj class using the function calculate_energy
    and has to return a dict of energies.
    """

    def __init__(
        self, lf, maxiter=200, ethreshold=1e-6, tthreshold=1e-6, select="t"
    ):
        """
        ** Arguments **

        maxiter
            Maximum number of iterations (int)

        ethreshold
            Convergence tolerance for energy (float)

        tthreshold
            Convergence tolerance for amplitudes (float)

        select
            Either `t` (amplitudes) or `l` (lambda/lagrange). Determines which
            vector function etc. is chosen and whether the energy is determined
            (only for `t`).
        """
        self.lf = lf
        self.maxiter = maxiter
        self.etol = ethreshold
        self.ttol = tthreshold
        self.select = select

    @property
    def lf(self):
        """The linalg factory"""
        return self._lf

    @lf.setter
    def lf(self, new):
        self._lf = new

    @property
    def maxiter(self):
        """The maximum number of iterations"""
        return self._maxiter

    @maxiter.setter
    def maxiter(self, new):
        if new < 0:
            raise UnknownOption("Number of iterations has to be positive")

        self._maxiter = new

    @property
    def etol(self):
        """The convergence threshold for the energy"""
        return self._etol

    @etol.setter
    def etol(self, new):
        self._etol = new

    @property
    def ttol(self):
        """The convergence threshold for the amplitudes"""
        return self._ttol

    @ttol.setter
    def ttol(self, new):
        self._ttol = new

    @property
    def select(self):
        """Choose between amplitudes and lambdas"""
        return self._select

    @select.setter
    def select(self, new):
        if new not in ["t", "l"]:
            raise UnknownOption("Choose between `t` and `l`")

        self._select = new

    def print_info(self, **kwargs):
        """Print optimization options."""
        diismax = kwargs.get("diismax", 9)
        diisstart = kwargs.get("diisstart", 0)
        reset = kwargs.get("diisreset", True)
        if log.do_medium:
            log.hline()
            log("Entering perturbation-based quasi-Newton solver")
            log.hline()
            log("OPTIMIZATION PARAMETERS:")
            log("Optimization thresholds:")
            log(f"  wfn amplitudes:    {self.ttol:.2e}")
            log(f"  energy:            {self.etol:.2e}")
            log(f"  maxiter:           {self.maxiter:3}")
            log("DIIS:")
            log(f"  max vectors:       {diismax}")
            log(f"  start:             {diisstart}")
            log(f"  reset:             {reset}")
            log.hline()

    @staticmethod
    def check_input(**kwargs):
        """Check keyword arguments for consistency"""
        for name in kwargs:
            check_options(name, name, "diismax", "diisstart", "diisreset")

    def compute_vfunction(self, obj, guess):
        """Vector function used in optimization. It is defined in instance obj as
           vfunction.

        ** Returns **

            OneIndex instance
        """
        v_function = obj.vfunction if self.select == "t" else obj.vfunction_l
        return v_function(guess)

    @staticmethod
    def compute_jacobian(obj, guess, *args):
        """Jacobian function used in optimization. It is defined in instance obj as
           jacobian."

        ** Returns **

            OneIndex instance
        """
        jacobian = obj.jacobian(guess, *args)
        return jacobian

    @staticmethod
    def compute_energy(obj, tk) -> dict[str, float]:
        """Energy calculated in class obj. Function is defined as calculate_energy
        and is defined as follows:

            calculate_energy(self, e_ref, **amplitudes)

        where e_ref is some reference energy and amplitudes is a dictionary
        containing all wfn amplitudes.

        ** Returns **

            A dictionary of energies
        """
        return obj.calculate_energy(obj.e_ref, **obj.unravel(tk.copy()))

    @timer.with_section("PBQN")
    def __call__(self, obj, guess, *args, **kwargs):
        """The optimization method."""
        diismax = kwargs.get("diismax", 9)
        diisstart = kwargs.get("diisstart", 0)
        reset = kwargs.get("diisreset", True)
        #
        # Check input
        #
        self.check_input(**kwargs)
        #
        # Print some information
        #
        self.print_info(**kwargs)
        #
        # Compute Jacobian used in optimization (each iteration uses the same Jacobian)
        #
        eps = self.compute_jacobian(obj, guess, *args)

        tk = guess.copy()
        ek = 0.0 if self.select == "l" else self.compute_energy(obj, tk)
        de = {"e_tot": 0.0}
        dtknorm = guess.norm()

        diis = DIIS(self.lf, diismax, diisstart)
        iter_ = 0
        if log.do_medium:
            print_e = f"{'Total energy':>16} {'Diff':>11} {'Corr. energy':>15}"
            print_e = print_e if self.select == "t" else ""
            log(
                f"\n{'Iter':>6} {print_e} {'|Residual|':>11s} "
                f"{'max(Residual)':>16s} {'Time':>12}"
            )
        while iter_ < self.maxiter:
            #
            # compute vector function for zeroth iteration
            #
            if iter_ == 0:
                vf = self.compute_vfunction(obj, guess)
            else:
                vf = self.compute_vfunction(obj, diis.tk[-1].copy())
                tk = diis.tk[-1]
            #
            # Calculate correction as Dt = -vf/eps
            #
            deltatk = vf.divide(eps, -1.0)
            #
            # Calculate average solution vector
            #
            diis(tk, deltatk, iter_, de["e_tot"])
            #
            # calculate new energy
            #
            ekn = 0.0
            dek = {}
            if self.select == "t":
                ekn = self.compute_energy(obj, diis.tk[-1])
            #
            # check convergence
            #
            if self.select == "t":
                for e_ in ek:
                    dek.update({e_: (ekn[e_] - ek[e_])})
                # reset diis if necessary
                if abs(dek["e_tot"]) > abs(de["e_tot"]):
                    diis.reset(deltatk, reset)
                    # Recalculate energy
                    ekn = self.compute_energy(obj, diis.tk[-1])
                    dek = {}
                    for e_ in ek:
                        dek.update({e_: (ekn[e_] - ek[e_])})
                    # for en, e in zip(ekn, ek):
                    # dek.append(en - e)
            else:
                # reset if residual norm increases
                if dtknorm < diis.dtk[-1].norm():
                    diis.reset(deltatk, reset)
                dek.update({"e_tot": 0.0})

            dtknorm = diis.dtk[-1].norm()
            #
            # Use callback function
            #
            callback = obj.callback_t if self.select == "t" else obj.callback_l
            try:
                callback(diis.tk[-1].array, diis.dtk[-1].array)
            except TypeError:
                callback(diis.tk[-1], diis.dtk[-1])
            #
            # Check if converged
            #
            if abs(dek["e_tot"]) < self.etol and dtknorm < self.ttol:
                if log.do_medium:
                    log.hline("~")
                    log(f"   Quasi-Netwon converged in {iter_ + 1} iterations")
                    log.hline("=")
                return ObjectView(
                    {
                        "e_tot": ekn,
                        "x": diis.tk[-1].array,
                        "success": True,
                        "nit": iter_ + 3,
                    }
                )
            # check if norm is reasonable, otherwise abort
            if abs(dtknorm) > 10:
                raise ConsistencyError(
                    "Unreasonable L2 norm. Aborting calculation!"
                )
            iter_ += 1
            ek = ekn
            de = dek
        #
        # Not converged
        #
        if log.do_medium:
            log.hline("~")
            log("   Quasi-Netwon NOT converged")
            log.hline("=")
        return ObjectView(
            {"e_tot": ekn, "x": diis.tk[-1].array, "success": False}
        )
