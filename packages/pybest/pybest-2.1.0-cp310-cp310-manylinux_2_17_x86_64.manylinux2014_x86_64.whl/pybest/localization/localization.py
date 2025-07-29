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
# This implementation can also be found in `Horton 2.0.0`.
# However, this file has been updated and debugged. Compatibility with Horton is NOT
# guaranteed.
#
# Detailed changes:
# See CHANGELOG
# 12/2020: frozen core support, new variable convention, abc, properties
# 02/2025: unification of variables (Zahra Karimi)


"""Orbital localization procedures

Currently supported localization flavours:
 * Pipek-Mezey

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np
from numpy.typing import NDArray

from pybest.cache import Cache
from pybest.exceptions import UnknownOption
from pybest.linalg import (
    DenseLinalgFactory,
    DenseOneIndex,
    DenseTwoIndex,
    LinalgFactory,
    OneIndex,
    TwoIndex,
)
from pybest.linalg.base import Orbital
from pybest.log import log, timer
from pybest.occ_model import AufbauOccModel
from pybest.steplength.stepsearch import RStepSearch
from pybest.utility import check_options, compute_unitary_matrix, unmask_orb

__all__ = [
    "PipekMezey",
]


class Localization(ABC):
    """Base class for all localization methods"""

    def __init__(
        self, lf: DenseLinalgFactory, occ_model: AufbauOccModel, projector: Any
    ) -> None:
        """Localize canonical HF orbitals.

        Args:
          lf (LinalgFactory):
               A LinalgFactory instance.

          occ_model (AufbauOccModel):
               Occupation model.

          Projector (Any):
               Projectors for atomic basis function. A list of TwoIndex
               instances.

        """
        self._lf = lf
        self._proj = projector
        self._occ_model = occ_model

        self._cache = Cache()
        self._block_type = None
        self._pop_matrix = None

    @timer.with_section("Localization")
    def __call__(
        self, data: Any, select: str, **kwargs: dict[str, Any]
    ) -> None:
        """Localizes the orbitals using a unitary transformation to rotate the
        AO/MO coefficient matrix. The orbitals are optimized by minimizing
        an objective function.

        This works only for restricted orbitals.

        Args:
          data (Any):
               An IOData container containing an Orbital instance. This
               instance will be overwritten.

          select (str):
               The orbital block to be localised. Any of ``occ`` (occupied
               orbitals), ``virt`` (virtual orbitals)
        **Keywords:**

        :maxiter: (int) maximum number of iterations for localization
                  (default 2000)
        :threshold: (float) localization threshold for objective function
                    (default 1e-6)
        :levelshift: level shift of Hessian (float) (default 1e-8)
        :stepsearch: step search options (dictionary) containing:

                     * method: step search method used (str). One of
                       ``trust-region`` (default), ``None``, ``backtracking``
                     * alpha: scaling factor for Newton step (float), used in
                       ``backtracking`` and ``None`` method (default 0.75)
                     * c1: parameter used in ``backtracking`` (float)
                       (default 1e-4)
                     * minalpha: minimum step length used in ``backracking``
                       (float) (default 1e-6)
                     * maxiterouter: maximum number of search steps (int)
                       (default 10)
                     * maxiterinner: maximum number of optimization
                       steps in each search step (int) (used only in ``pcg``,
                       default 500)
                     * maxeta: upper bound for estimated vs actual change in
                       ``trust-region`` (float) (default 0.75)
                     * mineta: lower bound for estimated vs actual change in
                       ``trust-region`` (float) (default 0.25)
                     * upscale: scaling factor to increase trustradius in
                       ``trust-region`` (float) (default 2.0)
                     * downscale: scaling factor to decrease trustradius in
                       ``trust-region`` (float) and scaling factor in
                       ``backtracking`` (default 0.25)
                     * trustradius: initial trustradius (float) (default
                       0.75)
                     * maxtrustradius: maximum trustradius (float) (default
                       0.75)
                     * threshold: trust-region optimization threshold, only
                       used in ``pcg`` (float) (default 1e-8)
                     * optimizer: optimizes step to boundary of trustradius
                       (str). One of ``pcg``, ``dogleg``, ``ddl`` (default
                       ddl)
        """
        if log.do_medium:
            log(f"Performing localization of {select} block")
        log.cite("the Pipek-Mezey localization scheme", "pipek1989")
        #
        # Assign default keyword arguements
        #
        names = []

        def _helper(x, y):
            names.append(x)
            return kwargs.get(x, y)

        maxiter = _helper("maxiter", 2000)
        thresh = _helper("threshold", 1e-6)
        lshift = _helper("levelshift", 1e-8)
        stepsearch = _helper("stepsearch", dict({}))
        stepsearch.setdefault("method", "trust-region")
        stepsearch.setdefault("minalpha", 1e-6)
        stepsearch.setdefault("alpha", 1.0)
        stepsearch.setdefault("c1", 0.0001)
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

        for name, value in kwargs.items():
            if name not in names:
                raise UnknownOption(f"Unknown keyword argument {name}")
            if value < 0:
                raise UnknownOption(f"Illegal value for {name}: {value}")

        #
        # Get orbitals from IOData container.
        # Note: orbitals will be overwritten in original container!
        #
        (orb,) = unmask_orb(data, **kwargs)
        #
        # Update information about localization block
        #
        self.block_type = select

        if log.do_medium:
            log(f"{'Iter':3}  {'D(ObjectiveFunction)':12}  {'Steplength':10}")
        #
        # Initialize step search
        #
        stepsearch_ = RStepSearch(self.lf, **stepsearch)
        #
        # Calculate initial objective function
        #
        self.solve_model(orb)
        objfct_ref = self.compute_objective_function()

        maxThresh = True
        maxIter = True
        it = 0
        while maxThresh and maxIter:
            #
            # Update population matrix for new orbitals
            #
            self.compute_population_matrix(orb)
            #
            # Calculate orbital gradient and diagonal approximation to the Hessian
            #
            kappa, gradient, hessian = self.orbital_rotation_step(lshift)
            #
            # Apply steps search to orbital rotation step 'kappa' and perform
            # orbital rotation
            #
            stepsearch_(
                self,
                None,
                None,
                orb,
                **{"kappa": kappa, "gradient": gradient, "hessian": hessian},
            )
            #
            # update objective function
            #
            objfct = self.compute_objective_function()
            it += 1
            #
            # Print localization progress
            #
            if log.do_medium:
                log(f"{it:4} {abs(objfct - objfct_ref):14.8f}")
            #
            # Check convergence
            #
            maxThresh = abs(objfct - objfct_ref) > thresh
            maxIter = it < maxiter
            #
            # Prepare for new iteration
            #
            objfct_ref = objfct
        if maxThresh and not maxIter:
            if log.do_medium:
                log(" ")
                log.warn(
                    f"Orbital localization not converged in {it - 1} iteration"
                )
                log(" ")
        else:
            if log.do_medium:
                log(" ")
                log(f"Orbital localization converged in {it - 1} iteration")
                log(" ")

    @property
    def occ_model(self):
        """The occupation model"""
        return self._occ_model

    @property
    def lf(self) -> LinalgFactory:
        """The LinalgFactory"""
        return self._lf

    @property
    def proj(self) -> tuple[TwoIndex, ...]:
        """The Projectors. A list of TwoIndex instances"""
        return self._proj

    @property
    def block_type(self) -> str | None:
        """The orbital block to be localized"""
        return self._block_type

    @block_type.setter
    def block_type(self, new: str) -> None:
        """Update localization block"""
        check_options("block", new, "occ", "virt")
        self._block_type = new

    @property
    def pop_matrix(self) -> tuple[TwoIndex] | None:
        """The population matrix. A list of TwoIndex instances"""
        return self._pop_matrix

    @pop_matrix.setter
    def pop_matrix(self, new: Any) -> None:
        """Update pop_matrix"""
        self._pop_matrix = new

    @property
    @abstractmethod
    def block(self) -> OneIndex:
        """The orbital block used during localization (OneIndex object)"""
        raise NotImplementedError

    @abstractmethod
    def grad(self) -> Any:
        """Gradient of objective function"""
        raise NotImplementedError

    @abstractmethod
    def hessian(self) -> Any:
        """Diagonal Hessian of objective function"""
        raise NotImplementedError

    @abstractmethod
    def compute_objective_function(self):
        """Objective function of a chosen localization flavor to be maximized"""
        raise NotImplementedError

    def __clear__(self):
        self.clear()

    def clear(self):
        """Clear all wavefunction information"""
        self._cache.clear()

    #
    # Don't change function name or implementation will break. The function
    # ``solve_model`` is used in the StepSearch module.
    #
    def solve_model(self, *args: Any, **kwargs: dict[str, Any]) -> None:
        """Update population matrix used to calculate objective function.
        args and kwargs are used in StepSearch module. Here, only args
        are used:

        **Arguments:**

        args
             an orbital instance.
        """
        for arg in args:
            if isinstance(arg, Orbital):
                self.compute_population_matrix(arg)

    def orbital_rotation_step(self, lshift: float) -> tuple:
        """Calculate gradient, hessian, and orbital rotation step

        Args:
          lshift (float):
             Shift elements of Hessian.

        """
        grad = self.grad()
        hess = self.hessian(lshift)

        kappa = grad.divide(hess, -1.0)

        return kappa, grad, hess

    def compute_rotation_matrix(self, coeff: NDArray[np.float64]) -> Any:
        """Determine orbital rotation matrix


        Args:
        coeff (Any):
             The non-reduntant orbital
        rotations, we need only values for
             p<q
        """
        nbasis = self.occ_model.nbasis[0]
        indl = np.tril_indices(nbasis, -1)
        kappa = self.lf.create_two_index(nbasis, nbasis)
        #
        # frozen core orbitals are accounted for in block property
        #
        kappa.assign(coeff, indl)
        #
        # k_pq = -k_qp
        #
        kappa.iadd_t(kappa, -1.0)

        out = compute_unitary_matrix(kappa)
        return out

    def compute_population_matrix(self, orb: Orbital) -> None:
        """Determine population matrix

        Args:
            orb (Orbital):
                The current AO/MO coefficients.

        """
        #
        # Calculate population matrices for orbital block
        #
        nbasis = self.occ_model.nbasis[0]
        pop_mat = list()
        for op in self.proj:
            pop = self.lf.create_two_index(nbasis, nbasis)
            orbblock = orb.copy()
            orbblock.imul(self.block)
            orbblock.itranspose()
            pop.assign_dot(orbblock, op)
            orbblock.itranspose()
            pop.idot(orbblock)

            pop_mat.append(pop)
        self.pop_matrix = pop_mat


class PipekMezey(Localization):
    """Perform Pipek-Mezey localization of occupied or virtual Hartree-Fock
    orbitals.
    """

    @property
    def block(self) -> DenseOneIndex:
        """The orbital block used during localization (OneIndex object)"""
        nbasis = self.occ_model.nbasis[0]
        ncore = self.occ_model.ncore[0]
        nocc = self.occ_model.nocc[0]

        block = self.lf.create_one_index(nbasis)
        if self.block_type == "occ":
            #
            # account for frozen core orbitals
            #
            block.assign(1.0, begin0=ncore, end0=nocc)
        elif self.block_type == "virt":
            block.assign(1.0, begin0=nocc)
        return block

    def grad(self) -> Any:
        """Gradient of objective function"""
        nbasis = self.occ_model.nbasis[0]
        grad = self.lf.create_two_index(nbasis, nbasis)
        for pop in self.pop_matrix:
            #
            # 4 [ pop_kk - pop_ll ] * pop_kl
            #
            diag = pop.copy_diagonal()
            pop.contract("ab,a->ab", diag, grad, factor=4.0)
            pop.contract("ab,b->ab", diag, grad, factor=-4.0)
        grad.iscale(-1)

        ind = np.tril_indices(nbasis, -1)
        return grad.ravel(ind=ind)

    # TODO: use exact Hessian
    def hessian(self, lshift: float = 1e-8) -> DenseTwoIndex:
        """Diagonal Hessian of objective function

        Args:
            lshift (float):
                Shift elements of Hessian

        lshift
             Shift elements of Hessian (float)
        Defaults to 1e-8.
        """
        nbasis = self.occ_model.nbasis[0]
        hessian = self.lf.create_two_index(nbasis, nbasis)
        for pop in self.pop_matrix:
            #
            # pop_ll*pop_ll
            #
            diag2 = self.lf.create_one_index(nbasis)
            diag = pop.copy_diagonal()
            diag.mult(diag, diag2)
            #
            # H_kl += -4 pop_ll*pop_ll - 4 pop_kk*pop_kk
            #
            hessian.iadd_t(diag2, 4.0)
            hessian.iadd(diag2, 4.0)
            #
            # H_kl += 8 pop_ll*pop_kk
            #
            hessian.iadd_one_mult(diag, diag, -8.0, transpose0=True)
            #
            # H_kl += 8 pop_kl*pop_kl
            #
            hessian.iadd_mult(pop, pop, 8.0)
        hessian.iadd_shift(lshift)

        ind = np.tril_indices(nbasis, -1)
        return hessian.ravel(ind=ind)

    def compute_objective_function(self) -> float:
        """Objective function of PM localization to be maximized. The current
        implementation minimizes -(objective_function).
        """
        nbasis = self.occ_model.nbasis[0]
        result = 0.0
        #
        # sum_iA pop(A)_ii^2
        #
        for pop in self.pop_matrix:
            diag2 = self.lf.create_one_index(nbasis)
            diag = pop.copy_diagonal()
            diag.mult(diag, diag2)

            result += diag2.trace()
        return -result
