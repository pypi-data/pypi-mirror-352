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
# This module has been originally written and updated by Katharina Boguslawski (see CHANGELOG)
# Its current version contains updates from the PyBEST developer team.
#
# Part of this implementation can also be found in `Horton 2.0.0`.
# However, this file has been updated and debugged. Compatibility with Horton is NOT
# guaranteed.
#
# Detailed changes (see also CHANGELOG):
# 2020-07-01: update class structure and init procedure
# 2020-07-01: update to new python features, including f-strings
# 2020-07-01: use PyBEST standards, including naming convention, exception class

"""Step search methods for orbital rotations

Optimize step length for orbital optimization (``kappa``) and rotate orbitals.

Works only with diagonal approximation to the Hessian which is stored as a
OneIndex instance.
"""

from pybest.exceptions import ArgumentError
from pybest.log import log, timer
from pybest.steplength.trustregionopt import Dogleg, DoubleDogleg, TruncatedCG
from pybest.utility import check_options, check_type, rotate_orbitals

__all__ = [
    "RStepSearch",
]


class StepSearch:
    def __init__(self, lf, **kw):
        """
        **Arguments:**

        lf
             A LinalgFactory instance

        **Keywords:**
             :method: step search method used, one of ``trust-region``
                      (default), ``None``, ``backtracking``
             :alpha: scaling factor for step, used in ``backtracking`` and
                     ``None`` method (default 0.75)
             :c1: parameter used in ``backtracking`` (default 1e-4)
             :minalpha: minimum step length used in ``backracking``
                        (default 1e-6)
             :maxiterouter: maximum number of step search steps (default 10)
             :maxiterinner: maximum number of optimization steps in each
                            step search step (used only in pcg, default 500)
             :maxeta: upper bound for estimated vs actual change in
                      ``trust-region`` (default 0.75)
             :mineta: lower bound for estimated vs actual change in
                      ``trust-region`` (default 0.25)
             :upscale: scaling factor to increase trust radius in
                       ``trust-region`` (default 2.0)
             :downscale: scaling factor to decrease trust radius in
                         ``trust-region`` and step length in ``backtracking``
                         (float) (default 0.25)
             :trustradius: initial trust radius (default 0.75)
             :maxtrustradius: maximum trust radius (default 0.75)
             :threshold: trust-region optimization threshold, only used in
                         ``pcg`` method of ``trust-region``
             :optimizer: optimizes step to boundary of trust radius. One of
                         ``pcg``, ``dogleg``, ``ddl`` (default ddl)
        """
        self._lf = lf
        #
        # Check keywords and set default arguments, types and options are also
        # checked
        #
        names = []

        def _helper(x, y):
            names.append(x)
            return kw.get(x, y)

        self._method = _helper("method", "trust-region")
        self._alpha = _helper("alpha", 1.0)
        self._c1 = _helper("c1", 0.0001)
        self._minalpha = _helper("minalpha", 1e-6)
        self._maxiterouter = _helper("maxiterouter", 10)
        self._maxiterinner = _helper("maxiterinner", 500)
        self._maxeta = _helper("maxeta", 0.75)
        self._mineta = _helper("mineta", 0.25)
        self._upscale = _helper("upscale", 2.0)
        self._downscale = _helper("downscale", 0.25)
        self._trustradius = _helper("trustradius", 0.75)
        self._maxtrustradius = _helper("maxtrustradius", 0.75)
        self._threshold = _helper("threshold", 1e-8)
        self._optimizer = _helper("optimizer", "ddl")
        self._alpha0 = self.alpha

        for name, _value in kw.items():
            if name not in names:
                raise ArgumentError(f"Unknown keyword argument {name}")

        check_options(
            "method", self.method, "None", "backtracking", "trust-region"
        )
        check_options("optimizer", self.optimizer, "pcg", "dogleg", "ddl")
        check_type("c1", self.c1, int, float)
        check_type("minalpha", self.minalpha, int, float)
        check_type("maxiterouter", self.maxiterouter, int)
        check_type("maxiterinner", self.maxiterinner, int)
        check_type("maxeta", self.maxeta, int, float)
        check_type("mineta", self.mineta, int, float)
        check_type("upscale", self.upscale, float)
        check_type("downscale", self.downscale, float)
        check_type("maxtrustradius", self.maxtrustradius, float)
        check_type("threshold", self.threshold, float)

    @property
    def lf(self):
        return self._lf

    @property
    def method(self):
        return self._method

    @property
    def maxeta(self):
        return self._maxeta

    @property
    def mineta(self):
        return self._mineta

    @property
    def upscale(self):
        return self._upscale

    @property
    def downscale(self):
        return self._downscale

    @property
    def maxiterouter(self):
        return self._maxiterouter

    @property
    def maxiterinner(self):
        return self._maxiterinner

    @property
    def alpha0(self):
        return self._alpha0

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, new):
        """Update current scaling factor"""
        check_type("alpha", new, int, float)
        self._alpha = new

    @property
    def minalpha(self):
        return self._minalpha

    @property
    def c1(self):
        return self._c1

    @property
    def maxtrustradius(self):
        return self._maxtrustradius

    @property
    def trustradius(self):
        return self._trustradius

    @trustradius.setter
    def trustradius(self, new):
        """Update current trastradius"""
        check_type("trustradius", new, float)
        self._trustradius = new

    @property
    def threshold(self):
        return self._threshold

    @property
    def optimizer(self):
        return self._optimizer

    def __call__(self, obj, one, two, orb, **kwargs):
        raise NotImplementedError


class RStepSearch(StepSearch):
    @timer.with_section("Linesearch")
    def __call__(self, obj, one, two, orb, **kwargs):
        """Optimize Newton-Rapshon step.

        **Arguments:**

        obj
             A class instance containing the objective function.

        one, two
             One- and Two-electron integrals (TwoIndex and FourIndex/Cholesky
             instances)

        orb
             An Orbital instance. Contains the MO coefficients

        **Keywords:**

        """
        if self.method == "None":
            self.do_no_stepsearch(obj, one, two, orb, **kwargs)
        elif self.method == "backtracking":
            self.do_backtracking(obj, one, two, orb, **kwargs)
        elif self.method == "trust-region":
            self.do_trust_region(obj, one, two, orb, **kwargs)

    def do_no_stepsearch(self, obj, one, two, orb, **kwargs):
        """Scale step size with factor self.alpha

        **Arguments:**

        obj
             A class instance containing the objective function.

        one, two
             One- and Two-electron integrals (TwoIndex and FourIndex/Cholesky
             instances)

        orb
             An Orbital instance. Contains the MO coefficients

        **Keywords:**
             :kappa: Initial step size (OneIndex instance)
        """
        kappa = kwargs.get("kappa")

        #
        # Scale current optimization step, rotate orbitals
        #
        kappa.iscale(self.alpha)
        rotation = obj.compute_rotation_matrix(kappa)
        rotate_orbitals(orb, rotation)

        #
        # Solve for wfn/population model
        #
        try:
            obj.solve_model(one, two, orb, **kwargs)
        except Exception:
            pass

    def do_backtracking(self, obj, one, two, orb, **kwargs):
        """Backtracking line search.

        **Arguments:**

        obj
             A class instance containing the objctive function.

        one, two
             One- and Two-electron integrals (TwoIndex and FourIndex/Cholesky
             instances)

        orb
             An Orbital instance. Contains the MO coefficients

        **Keywords:**
             :kappa: Initial step size (OneIndex instance)
             :gradient: Orbital gradient (OneIndex instance)
        """
        kappa = kwargs.get("kappa")
        gradient = kwargs.get("gradient")

        #
        # Update scaling factor to initial value
        #
        self.alpha = self.alpha0

        #
        # Calculate objective function
        #
        ofun_ref = obj.compute_objective_function()

        #
        # Copy current orbitals
        #
        orb_ = orb.copy()
        #
        # Initial rotation
        #
        kappa.iscale(self.alpha)
        rotation = obj.compute_rotation_matrix(kappa)
        rotate_orbitals(orb_, rotation)

        #
        # Solve for wfn/population model if required
        #
        try:
            obj.solve_model(one, two, orb_, **kwargs)
        except Exception:
            pass

        #
        # Calculate objective function for rotated orbitals
        #
        ofun = obj.compute_objective_function()

        #
        # reduce step size until line search condition is satisfied
        #
        while self.check_line_search_condition(
            ofun, ofun_ref, kappa, gradient
        ):
            self.alpha = self.alpha * self.downscale
            #
            # New rotation
            #
            kappa.iscale(self.alpha)
            rotation = obj.compute_rotation_matrix(kappa)
            orb_ = orb.copy()
            rotate_orbitals(orb_, rotation)
            #
            # Solve for wfn/population model if required
            #
            try:
                obj.solve_model(one, two, orb_, **kwargs)
            except Exception:
                pass
            #
            # Calculate objective function for scaled rotation
            #
            ofun = obj.compute_objective_function()
            #
            # Abort if scaling factor falls below threshold
            #
            if self.alpha < self.minalpha:
                break
        orb.assign(orb_)

    def do_trust_region(self, obj, one, two, orb, **kwargs):
        """Do trust-region optimization.

        **Arguments:**

        obj
             A class instance containing the objective function.

        one/two
             One and Two-body Hamiltonian (TwoIndex and FourIndex/Cholesky
             instances)

        orb
             (Orbital instance) An MO expansion

        **Keywords:**
             :kappa: Initial step size (OneIndex instance)
             :gradient: Orbital gradient (OneIndex instance)
             :hessian: Orbital Hessian (OneIndex instance)
        """
        kappa = kwargs.get("kappa")
        gradient = kwargs.get("gradient")
        hessian = kwargs.get("hessian")

        iteri = 1
        ofun_ref = obj.compute_objective_function()
        De = 0.0

        stepn = kappa.copy()
        while True:
            norm = stepn.norm()
            #
            # If ||kappa||_2 is outside the trust region, find a new Newton
            # step inside the trust region:
            #
            if norm > self.trustradius:
                #
                # Preconditioned conjugate gradient
                #
                if self.optimizer == "pcg":
                    optimizer = TruncatedCG(
                        self.lf, gradient, hessian, self.trustradius
                    )
                    optimizer(
                        **{
                            "niter": self.maxiterinner,
                            "abstol": self.threshold,
                        }
                    )
                    stepn = optimizer.step
                #
                # Powell's dogleg optimization:
                #
                elif self.optimizer == "dogleg":
                    optimizer = Dogleg(
                        kappa, gradient, hessian, self.trustradius
                    )
                    optimizer()
                    stepn = optimizer.step
                #
                # Powell's double dogleg optimization:
                #
                elif self.optimizer == "ddl":
                    optimizer = DoubleDogleg(
                        kappa, gradient, hessian, self.trustradius
                    )
                    optimizer()
                    stepn = optimizer.step
            #
            # New rotation
            #
            rotation = obj.compute_rotation_matrix(stepn)
            orb_ = orb.copy()
            rotate_orbitals(orb_, rotation)

            #
            # Solve for wfn/population model if required
            #
            try:
                obj.solve_model(one, two, orb_, **kwargs)
            except Exception:
                pass

            #
            # Calculate objective function after rotation
            #
            ofun = obj.compute_objective_function()

            #
            # Determine ratio for a given step:
            #
            hstep = hessian.new()
            hessian.mult(stepn, hstep)
            Destimate = gradient.dot(stepn) + 0.5 * stepn.dot(hstep)
            De = ofun - ofun_ref
            rho = De / Destimate

            #
            # For a given ratio, adjust trust radius and accept or reject
            # Newton step:
            #
            if rho > self.maxeta and De <= 0.0:
                #
                # Enlarge trust radius:
                #
                new = min(self.upscale * self.trustradius, self.maxtrustradius)
                self.trustradius = new
                orb.assign(orb_)
                break
            elif rho >= self.mineta and rho <= self.maxeta and De <= 0.0:
                #
                # Do nothing with trust radius:
                #
                orb.assign(orb_)
                break
            elif rho > 0 and rho < self.mineta and De <= 0.0:
                #
                # Decrease trust radius:
                #
                self.trustradius = self.downscale * self.trustradius
                orb.assign(orb_)
                break
            else:
                #
                # Bad step! Reject Newton step and repeat with smaller trust
                # radius
                #
                self.trustradius = self.downscale * self.trustradius

            iteri = iteri + 1
            if iteri > self.maxiterouter:
                log.warn(
                    f"Trust region search not converged after {self.maxiterouter} "
                    f"iterations. Trust region search aborted."
                )
                orb.assign(orb_)
                break

    def check_line_search_condition(self, cetot, petot, kappa, grad):
        """Check if Armijo condition is satisfied
        (e_tot(0+alpha*kappa)-e_tot(0) <= c1*alpha*(kappa,grad))
        """
        term = self.c1 * self.alpha * kappa.dot(grad)
        return (cetot - petot - term) > 0
