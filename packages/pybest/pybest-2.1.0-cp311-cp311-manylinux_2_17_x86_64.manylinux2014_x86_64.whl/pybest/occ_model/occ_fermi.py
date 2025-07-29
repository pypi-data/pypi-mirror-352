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
# Detailed changes (see also CHANGELOG):
# 2021-11: Created
# Detailed changelog:
# 2023-12: Julian Świerczyński - For occ models added function that automatically computes the number of
# frozen core atomic orbitals using information provided in `elements.csv`.
# ruff: noqa: B023

"""
Child class of AufbauOccModel.

Orbitals are occupied in accordance with the Aufbau principle, where the lowest
lying orbitals are occupied using a distrubtion. The rules are as follows:

    * The basic rules of AufbauOccModel apply

    * All orbitals that are partially occupied are considered to be formally
      occupied. Thus, attributes like nocc, nact, nacto, etc. are set
      accordingly.

Note that the sum of all occupied orbitals does not correspond to the number
of (alpha and/or beta) electrons.

The FermiOccModel should NOT be used in combination with multi-configurational
wave functions as the number of occupied orbitals might be assigned incorrectly.
This OccupationModel might be useful for single Slater determinant wave
functions in case of convergence difficulties.

"""

import numpy as np
from scipy import special

from pybest.constants import boltzmann

# package imports
from pybest.exceptions import ArgumentError
from pybest.log import log

# module imports
from pybest.occ_model import AufbauOccModel
from pybest.solvers.linear_equations import find_1d_root


class FermiOccModel(AufbauOccModel):
    """Fermi smearing electron occupation model"""

    long_name = "Fractional occupation number model using Fermi smearing"

    def __init__(self, basis, **kwargs):
        r"""
        For each channel, the orbital occupations are assigned with the Fermi
        distribution:

        .. math::

             n_i = \frac{1}{1 + e^{(\epsilon_i - \mu)/k_B T}}

        where, for a given set of energy levels, :math:`\{\epsilon_i\}`, the
        chemical potential. Two different methods are supported: FON
        (fractional occupation number) and pFON (pseudo-FON).
        In FON, :math:`\mu`, is optimized as to satisfy the following constraint:

        .. math::

            \sum_i n_i = n_\text{occ}

        where :math:`n_\text{occ}` can be set per (spin) channel.

        In pFON, :math:`\mu` is taken as the Fermi energy set at a constant
        value of :math:`(\epsilon_{HOMO} + \epsilon_{LUMO})/2`, while the
        occupation numbers are normalized to

        .. math::

            n_i^\prime = \frac{n_i N}{\sum_i n_i}

        where N is the number of electrons in each channel.

        Both methods are explained in detail in [rabuck1999]_.

        **Keyword arguments:**

        temperature
            Controls the width of the distribution (derivative)

        eps
            The error on the sum of the occupation number when searching for
            the right Fermi level. Only required for the FON method.

        method
            (str) the method to define fraction occupation numbers FON as
            presented in [rabuck1999]_. FON and pFON are supported.

        delta_t
            (float) the amount in K by which the temperature is reduced
            (default: 50 K)
        """
        self._temperature = float(kwargs.pop("temperature", 250))
        self._eps = kwargs.pop("eps", 1e-8)
        self._method = kwargs.get("method", "pfon")
        self._delta_t = kwargs.get("delta_t", 50)
        if self.temperature <= 0:
            raise ArgumentError("The temperature must be strictly positive")
        if self.eps <= 0:
            raise ArgumentError(
                "The root-finder threshold (eps) must be strictly positive."
            )
        if self.delta_t < 0:
            raise ArgumentError(
                "Keyword argument delta_t cannot be smaller than 0. Expected"
                f" delta_t > 0, received delta_t = {self.delta_t}"
            )
        #
        # Call Base class method; it also checks for proper kwargs
        #
        AufbauOccModel.__init__(self, basis, **kwargs)
        log.cite(
            "the Fermi broading method to assign orbital occupations",
            "rabuck1999",
        )

    @staticmethod
    def _check_kwargs(supported_kwargs=None, **kwargs):
        """Check for valid keyword arguments."""
        if supported_kwargs is None:
            supported_kwargs = []
        supported_kwargs += ["temperature", "eps", "method", "delta_t"]
        AufbauOccModel._check_kwargs(supported_kwargs, **kwargs)
        unsupported_kwargs = ["nocc_a", "nocc_b"]
        for el in unsupported_kwargs:
            if el in kwargs:
                raise ArgumentError(f"Keyword argument {el} not supported.")

    @staticmethod
    def _attrs_from_hdf5(grp):
        """Return valid kwargs for some Aufbau occupation model.

        **Arguments:**

        grp
             An h5py.Group object.
        """
        attrs1 = AufbauOccModel._attrs_from_hdf5(grp)
        attrs2 = {
            "temperature": grp.attrs["temperature"],
            "eps": grp.attrs["eps"],
            "method": grp.attrs["method"],
            "delta_t": grp.attrs["delta_t"],
        }
        return {**attrs1, **attrs2}

    def _attrs_to_hdf5(self, grp):
        """Write attributes for some occupation model.

        **Arguments:**

        grp
             An h5py.Group object.
        """
        #
        # Get OccupationModel method (the same for all child classes)
        #
        AufbauOccModel._attrs_to_hdf5(self, grp)
        #
        # Store child class specific attributes
        #
        grp.attrs["temperature"] = self.temperature
        grp.attrs["eps"] = self.eps
        grp.attrs["method"] = self.method
        grp.attrs["delta_t"] = self.delta_t

    @property
    def temperature(self):
        """Temperature applied in Fermi smearing."""
        return self._temperature

    @temperature.setter
    def temperature(self, new):
        self._temperature = new if new > 0 else 1e-18

    @property
    def eps(self):
        """The root-finder threshold."""
        return self._eps

    @property
    def method(self):
        """The method for defining fractional occupation numbers."""
        return self._method

    @property
    def delta_t(self):
        """The amount in K by which the temperature is lowered."""
        return self._delta_t

    def print_info(self):
        """Print information on occupation number module."""
        #
        # Call base class method
        #
        AufbauOccModel.print_info(self)
        #
        # Print model-specific parameters
        #
        log(" ")
        log(f"{type(self).__name__} specific parameters:")
        log(f"{'Temperature:':>40} {self.temperature}")
        log(f"{'dT (T = T - dT):':>40} {self.delta_t}")
        log(f"{'method:':>40} {self.method}")

    def assign_occ_reference(self, *orbs):
        """Assign occupation numbers for the reference determinant to the
        orbitals.

        Note that this function only works properly for 1-determinant wave
        functions, where the occupation numbers are assigned based on the
        chosen occupation model. This function should not be used for
        multi-determinant wave functions.

        **Arguments:**

        orb_a, orb_b, ...
             Orbital objects
        """
        if self.method == "fon":
            self.assign_fon(*orbs)
        if self.method == "pfon":
            self.assign_pfon(*orbs)
        #
        # Update attributes
        #
        for i, orb in enumerate(orbs):
            # get index of last nonzero element in occupation number vector
            ind_max = np.max(np.nonzero(orb.occupations)) + 1
            # assume all orbitals as occupied that have nonzero occs
            self._nocc[i] = ind_max
            self._nvirt[i] = self.nbasis[i] - ind_max
            self._nacto[i] = self.nocc[i] - self.ncore[i]
            self._nactv[i] = self.nvirt[i]
        #
        # Print information on temperature etc. after each assignment
        #
        log(f"{'T = ':>75} {self.temperature}, dT = {self.delta_t}")

    def assign_fon(self, *orbs):
        """Assign occupation numbers for the reference determinant to the
        orbitals using FON.
        """
        beta = 1.0 / self.temperature / boltzmann
        for orb, nocc in zip(orbs, self.nspin):
            # we need to define those functions in the loop, otherwise
            # find_1d_root won't work
            def get_occ(mu):
                occ = np.zeros(orb.nfn)
                mask = orb.energies < mu
                e = np.exp(beta * (orb.energies[mask] - mu))
                occ[mask] = 1.0 / (e + 1.0)
                mask = ~mask
                e = np.exp(-beta * (orb.energies[mask] - mu))
                occ[mask] = e / (1.0 + e)
                return occ

            def error(mu):
                return nocc - get_occ(mu).sum()

            mu0 = orb.energies[orb.nfn // 2]
            error0 = error(mu0)
            delta = 0.1 * (1 - 2 * (error0 < 0))
            for _i in range(100):
                mu1 = mu0 + delta
                error1 = error(mu1)
                if error1 == 0 or ((error0 > 0) ^ (error1 > 0)):
                    break
                delta *= 2

            if error1 == 0:
                orb.occupations[:] = get_occ(mu1)
            else:
                mu, error = find_1d_root(
                    error, (mu0, error0), (mu1, error1), eps=self.eps
                )
                orb.occupations[:] = get_occ(mu)
        #
        # Decrease temperature
        #
        self.temperature -= self.delta_t

    def assign_pfon(self, *orbs):
        """Assign occupation numbers for the reference determinant to the
        orbitals using pFON.
        """
        beta = 1.0 / self.temperature / boltzmann
        for orb, nocc in zip(orbs, self.nspin):
            #
            # Get Fermi energy as (E(HOMO)+E(LUMO))/2, where HOMO and LUMO are
            # taken from the total number of alpha and beta electrons
            #
            e_fermi = (orb.energies[nocc - 1] + orb.energies[nocc]) / 2
            #
            # fon using scipy.special.expit function 1/(1+exp(-x))
            #
            fon = special.expit(-beta * (orb.energies - e_fermi))
            fon[np.where(fon < 1e-16)] = 0.0
            #
            # normalize
            #
            pfon = fon * nocc / sum(fon)
            #
            # assign
            #
            orb.occupations[:] = pfon
        #
        # Decrease temperature
        #
        self.temperature -= self.delta_t
