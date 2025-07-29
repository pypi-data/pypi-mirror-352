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
# 2023-12: Julian Świerczyński - For occ models added function that automatically computes the number of
# frozen core atomic orbitals using information provided in `elements.csv`.

"""
The fixed occupation number model

Child class of OccupationModel. This model contains additional properties that
are uniquely defined by the chosen flavor of the AufbauOccModel.

    * nocc: the number of occupied orbitals (list) with non-zero occupation
            numbers; defined with respect to some principal determinant

    * nvirt: the number of virtual orbitals (list); nbasis - nocc

    * ncore: the number of core orbitals (list)

    * nacto: the number of active occupied orbitals (list); ; defined with
             respect to some principal determinant; nocc - ncore

    * nactv: the number of active virtual orbitals (list)

    * nact: the number of active basis functions (list)

    * nspin: the number of electrons in each spin channel (list)

Orbitals are occupied in accordance with some
input occupation number vector defined by the user. The rules are as follows:

    * Occupation number vectors for each channel are passes as keyword
      arguments. They have to be numpy arrays with elements between [0, 1].
      Only the occupied orbitals have to be specified. Unoccupied orbitals
      between occupied orbitals are allowed.

    * All attributes concerning the occupied/active orbitals (nacto, nactv) are
      taken from the occupation number vectors, where the index of the last
      non-zero number indicates the total number of occupied orbitals.

Note that this OccupationModel is only recommended for wave function models
with a single Slater determinant. For multi-configurational wave functions,
the specification of some attributes might result in the wrong number of
occupied orbitals in the reference determinant.

"""

import numpy as np

# package imports
from pybest.exceptions import (
    ArgumentError,
    ConsistencyError,
    ElectronCountError,
)
from pybest.log import log

# module imports
from pybest.occ_model.occ_base import OccupationModel
from pybest.utility import check_type


class FixedOccModel(OccupationModel):
    """Occupation model with fixed occupation numbers specified by user.

    Currently, we assume that all orbitals specified in the occupation number
    vector are occupied orbitals and count to the ``nocc`` property.

    Note that this occupation model is only supported for HF wave functions.
    """

    long_name = "Fixed occupation number model."

    def __init__(self, basis, **kwargs):
        #
        # Check user-specified kwargs
        #
        self._check_kwargs(**kwargs)
        #
        # Assign fixed occupation array (class specific)
        # First: alpha channel
        occ_a = kwargs.get("occ_a", None)
        if occ_a is None:
            raise ArgumentError("No occupation vectors specified")
        check_type("occ_a", occ_a, np.ndarray)
        self._occ_array = [occ_a]
        #
        # Second: beta channel
        #
        occ_b = kwargs.get("occ_b", None)
        # Enforce unrestricted orbitals if required
        # default depends on whether occ_b is given
        unrestricted = kwargs.get("unrestricted", occ_b is not None)
        if unrestricted:
            if occ_b is None:
                self._occ_array.append(occ_a)
            else:
                check_type("occ_b", occ_b, np.ndarray)
                self._occ_array.append(occ_b)
        #
        # Check if occupation numbers lie in [0,1]
        #
        for occ in self.occ_array:
            if any(nocc_ > 1.0 or nocc_ < 0.0 for nocc_ in occ):
                raise ElectronCountError(
                    "Occupation numbers have to lie in the range [0,1]."
                )
        #
        # Extract nocc_a/b from occ_a/b. For Basis, checks whether nel and
        # nocc agree; we do not need to check for unrestricted as these
        # kwargs are only used for Base class checks
        nocc_ = {
            "nocc_a": sum(self._occ_array[0]),
            "nocc_b": sum(self._occ_array[-1]),
        }
        #
        # Call base class method
        #
        OccupationModel.__init__(self, basis, **kwargs, **nocc_)
        #
        # Check for consistency
        #
        factor = 2 if not unrestricted else 1
        nel_ = sum([sum(occ_array) for occ_array in self.occ_array]) * factor

        if self.nel != nel_:
            raise ElectronCountError(
                "Number of electrons in occ_a/occ_b does not agree with total"
                f"number of electrons. Got {nel_}, expected {self.nel}"
            )
        #
        # Specify child class attributes
        #
        ncore = self.check_ncore(**kwargs)

        nbasis = self.nbasis[0]
        if len(self.occ_array) == 2:
            self._nbasis.append(nbasis)
        self._nocc = [len(occ_array) for occ_array in self.occ_array]
        self._ncore = [ncore for i in range(len(self.occ_array))]
        self._nacto = [
            nocc - ncore for nocc, ncore in zip(self.nocc, self.ncore)
        ]
        self._nvirt = [
            nbasis - nocc for nbasis, nocc in zip(self.nbasis, self.nocc)
        ]
        self._nactv = self.nvirt
        self._nact = [nbasis_ - ncore for nbasis_ in self.nbasis]
        self._nspin = [sum(occ_array) for occ_array in self.occ_array]
        #
        # Do some sanity checks of user-defined occupations are consistent
        # with base class settings
        self._check_attributes()
        #
        # Print some information
        #
        if log.do_medium:
            self.print_info()
            log.hline()

    @staticmethod
    def _check_kwargs(supported_kwargs=None, **kwargs):
        """Check for valid keyword arguments."""
        if supported_kwargs is None:
            supported_kwargs = []
        supported_kwargs += [
            "unrestricted",
            "charge",
            "nel",
            "ncore",
            "occ_a",
            "occ_b",
            "auto_ncore",
        ]
        for kwarg in kwargs:
            if kwarg not in supported_kwargs:
                raise ArgumentError(f"Keyword {kwarg} not recognized.")

    @staticmethod
    def _attrs_from_hdf5(grp):
        """Return valid kwargs for some Aufbau occupation model.

        **Arguments:**

        grp
             An h5py.Group object.
        """
        attrs = {
            "charge": grp.attrs["charge"],
            "nel": grp.attrs["nel"],
            "unrestricted": grp.attrs["unrestricted"],
            "ncore": grp.attrs["ncore"],
            "occ_a": grp["occ_a"][:],
        }
        if "occ_b" in grp:
            attrs += {"occ_b": grp["occ_b"][:]}
        return attrs

    def _attrs_to_hdf5(self, grp):
        """Write attributes for some occupation model.

        **Arguments:**

        grp
             An h5py.Group object.
        """
        #
        # Get OccupationModel method (the same for all child classes)
        #
        OccupationModel._attrs_to_hdf5(self, grp)
        #
        # Store child class specific attributes
        #
        grp.attrs["ncore"] = self.ncore[0]
        grp.attrs["unrestricted"] = len(self.nspin) == 2
        grp["occ_a"] = self.occ_array[0]
        if len(self.nspin) == 2:
            grp["occ_b"] = self.occ_array[-1]

    @property
    def nocc(self):
        """The number of occupied orbitals"""
        return self._nocc

    @property
    def nvirt(self):
        """The number of virtual orbitals"""
        return self._nvirt

    @property
    def ncore(self):
        """The number of core orbitals"""
        return self._ncore

    @property
    def nacto(self):
        """The number of active occupied orbitals"""
        return self._nacto

    @property
    def nactv(self):
        """The number of active virtual orbitals"""
        return self._nactv

    @property
    def nact(self):
        """The number of active basis functions"""
        return self._nact

    @property
    def occ_array(self):
        """Numpy arrays containing the occupation number vectors (list)."""
        return self._occ_array

    @property
    def nspin(self):
        """The number of electrons in each spin channel (list)"""
        return self._nspin

    def _check_attributes(self):
        """Check if attributes are properly assigned"""
        if len(self.occ_array) == 1:
            nel = sum(self.occ_array[0]) * 2
        else:
            nel = sum([sum(occ_) for occ_ in self.occ_array])
        if self.nel != nel:
            raise ElectronCountError(
                "Occupation vector does not agree with total number of "
                f"electrons. Got {nel} electrons, expected {self.nel}."
            )
        if any(val < 0.0 for val in self.nacto):
            raise ConsistencyError(
                "Number of active occupied orbitals cannot be negative"
            )
        if any(val < 0.0 for val in self.nactv):
            raise ConsistencyError(
                "Number of active virtual orbitals cannot be negative"
            )
        if any(val < 0.0 for val in self.nvirt):
            raise ConsistencyError(
                "Number of virtual orbitals cannot be negative"
            )

    def print_info(self):
        """Print information on occupation number module."""

        def resolve(list_):
            return " ".join(f"{s!s:<5s}" for s in list_)

        spin_block = f"{'':>40} alpha"
        log(f"{spin_block}" if len(self.nbasis) == 1 else f"{spin_block} beta")
        log(f"{'Total number of basis functions:':>40} {resolve(self.nbasis)}")
        log(f"{'Total number of occupied orbitals:':>40} {resolve(self.nocc)}")
        log(f"{'Total number of virtual orbitals:':>40} {resolve(self.nvirt)}")
        log(f"{'Number of frozen core orbitals:':>40} {resolve(self.ncore)}")
        log(
            f"{'Number of active occupied orbitals:':>40} {resolve(self.nacto)}"
        )
        log(
            f"{'Number of active virtual orbitals:':>40} {resolve(self.nactv)}"
        )
        log(f"{'Number of active orbitals:':>40} {resolve(self.nact)}")
        log(f"{'Number of electrons:':>40} {resolve(self.nspin)}")
        if any(self.ncore) > 0:
            log.warn(
                "Frozen core orbitals are not supported in the SCF module."
                " Only post-HF methods support a frozen core."
            )

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
        if len(orbs) != len(self.occ_array):
            raise ConsistencyError(
                f"Expected {len(self.nocc)} orbitals, got {len(orbs)}."
            )
        for orb, occ_array in zip(orbs, self.occ_array):
            orb.occupations[: len(occ_array)] = occ_array
            orb.occupations[len(occ_array) :] = 0.0

    def check_dms(self, *dms, **kwargs):
        """Test if the given density matrices contain the right number of electrons

        **Arguments:**

        dm1, dm2, ...
            1-particle reduced density matrices to be tested.

        **Optional keyword arguments:**

        eps (default=1e-4)
            The allowed deviation.

        olp
            The overlap operator. Required if 1-RDMs are represented in the AO
            basis.
        """
        eps = kwargs.get("eps", 1e-4)
        olp = kwargs.get("olp", None)
        if len(dms) != len(self.occ_array):
            raise ConsistencyError(
                "The number of density matrices is incorrect."
            )
        for dm, occ_array in zip(dms, self.occ_array):
            if olp is None:
                check = abs(dm.contract("aa") - occ_array.sum()) < eps
            else:
                check = abs(olp.contract("ab,ba", dm) - occ_array.sum()) < eps
            if not check:
                raise ElectronCountError(
                    "1-RDM does not contain correct number of electrons"
                )
