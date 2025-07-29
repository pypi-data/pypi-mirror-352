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
Child class of AufbauOccModel.

Orbitals are occupied in accordance with the Aufbau principle, where the highest
lying orbitals might have fractional occupation numbers. These fractional
occupation numbers are set during the initialization of the class and are not
updated afterwards. The rules are as follows:

    * The basic rules of AufbauOccModel apply

    * The fractional electrons are put into the highest lying orbitals either
      alpha channel or both alpha and beta channels.

Note that the sum of all occupied orbitals does not correspond to the number
of (alpha and/or beta) electrons.

The FractionalOccModel should NOT be used in combination with multi-configurational
wave functions as the number of occupied orbitals might be assigned incorrectly.
This OccupationModel might be useful for single Slater determinant wave
functions in case of convergence difficulties.

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
from pybest.occ_model import AufbauOccModel


class FractionalOccModel(AufbauOccModel):
    """This Aufbau model features fractional occupation numbers in the HOMO
    orbital(s).

    Note that the fractional electrons are put in the highest lying orbital.
    If only one fractional occupation is given, restricted orbitals are assumed,
    where the HOMO (of both channels) is occupied by a fraction of an electron.
    """

    long_name = "Fractional occupation number model for the HOMO."

    def _set_attributes(self, **kwargs):
        """Set all class attributes."""
        ncore = self.check_ncore(**kwargs)
        nactc = kwargs.get("nactc", 0)
        if nactc != 0:
            log.warn(
                "Keyword nactc not supported for the fractional occupation model! nactc set to 0."
            )
        #
        # Get fractional occupation numbers (we do not need to check)
        #
        nocc_a = kwargs.get("nocc_a", 0)
        nocc_b = kwargs.get("nocc_b", 0)
        self._nspin = [nocc_a]
        nocc_a_ = int(np.ceil(nocc_a))
        #
        # Use restricted representation if
        # - only nocc_a is given
        # - unrestricted keyword is set to False (default)
        #
        unrestricted = kwargs.get("unrestricted", nocc_b != 0)
        # first do consistency check:
        if not unrestricted and (nocc_a - nocc_b) != 0 and nocc_b != 0:
            raise ConsistencyError(
                "Cannot enforce restricted occupation pattern due to unpaired"
                " electrons in the system."
            )
        if unrestricted:
            nocc_b = nocc_a if nocc_b == 0 else nocc_b
            self._nspin.append(nocc_b)
            nocc_b_ = int(np.ceil(nocc_b))
        else:
            nocc_b_ = nocc_a_
        #
        # Do some sanity checks
        #
        nbasis = self.nbasis[0]
        if (nocc_a_ - ncore) <= 0 or (nocc_b_ - ncore) < 0:
            raise ConsistencyError(
                "Number of active occupied orbitals has to be larger than 0."
            )
        if nbasis - ncore <= 0:
            raise ConsistencyError("Too many frozen core orbitals defined.")
        if ncore < 0:
            raise ConsistencyError(
                "Number of frozen core orbitals cannot be negative."
            )
        #
        # Assign all occupied and virtual orbitals (list) using the Aufbau
        # principle, all fractional occupations are assigned in the HOMO.
        #
        # First alpha spin block; add singly occupied orbitals to alpha block
        self._nocc = [nocc_a_]
        self._nvirt = [nbasis - nocc_a_]
        self._nacto = [nocc_a_ - ncore]
        self._nactv = [nbasis - nocc_a_]
        self._nact = [nbasis - ncore]
        self._ncore = [ncore]
        self._nactc = [nactc]

        if unrestricted:
            # Second spin block
            self._nocc.append(nocc_b_)
            self._nvirt.append(nbasis - nocc_b_)
            self._nacto.append(nocc_b_ - ncore)
            self._nactv.append(nbasis - nocc_b_)
            self._nact.append(nbasis - ncore)
            self._nbasis.append(nbasis)
            self._ncore.append(ncore)
            self._nactc.append(nactc)

    @staticmethod
    def _check_kwargs(supported_kwargs=None, **kwargs):
        """Check for valid keyword arguments."""
        if supported_kwargs is None:
            supported_kwargs = []
        AufbauOccModel._check_kwargs(supported_kwargs, **kwargs)
        if "alpha" in kwargs:
            raise ArgumentError("Unknown kwargs alpha.")

    def _check_nocc_aufbau(self, nocc_a, nocc_b):
        """Check consistency of nocc_a/nocc_b"""
        if nocc_a == 0:
            raise ArgumentError(
                f"Invalid keyword argument nocc_a. {type(self).__name__} "
                "requires nocc_a to introduce fractional occupations."
            )

    @staticmethod
    def _attrs_from_hdf5(grp):
        """Return valid kwargs for Fractional occupation model.
        We read only those attributes that are required for this occupation
        model.

        **Arguments:**

        grp
             An h5py.Group object.
        """
        attrs = {
            "charge": grp.attrs["charge"],
            "nel": grp.attrs["nel"],
            "unrestricted": grp.attrs["unrestricted"],
            "ncore": grp.attrs["ncore"],
            "nocc_a": grp.attrs["nocc_a"],
        }
        if "nocc_b" in grp.attrs:
            attrs += {"nocc_b": grp.attrs["nocc_b"]}
        return attrs

    def _attrs_to_hdf5(self, grp):
        """Write attributes for Fractional occupation model.

        **Arguments:**

        grp
             An h5py.Group object.
        """
        #
        # Get parent method (the same for all child classes)
        #
        AufbauOccModel._attrs_to_hdf5(self, grp)
        #
        # Write additional attributes
        #
        grp.attrs["nocc_a"] = self.nspin[0]
        if len(self.nspin) == 2:
            grp.attrs["nocc_b"] = self.nspin[-1]

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
        if len(orbs) != len(self.nocc):
            raise ConsistencyError(
                f"Expected {len(self.nocc)} orbitals, got {len(orbs)}."
            )
        for orb, nocc in zip(orbs, self.nspin):
            if orb.nfn < nocc:
                raise ElectronCountError(
                    "The number of orbitals must not be lower than the number of alpha "
                    "or beta electrons."
                )
            # It is assumed that the orbitals are sorted from low to high energy.
            if nocc == int(nocc):
                orb.occupations[: int(nocc)] = 1.0
                orb.occupations[int(nocc) :] = 0.0
            else:
                orb.occupations[: int(np.floor(nocc))] = 1.0
                orb.occupations[int(np.floor(nocc))] = nocc - np.floor(nocc)
                orb.occupations[int(np.ceil(nocc)) :] = 0.0

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
        if len(dms) != len(self.nocc):
            raise ConsistencyError(
                "The number of density matrices is incorrect."
            )
        for dm, nocc in zip(dms, self.nspin):
            if olp is None:
                check = abs(dm.contract("aa") - nocc) < eps
            else:
                check = abs(olp.contract("ab,ba", dm) - nocc) < eps
            if not check:
                raise ElectronCountError(
                    "1-RDM does not contain correct number of electrons"
                )
