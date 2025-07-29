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
# 2020-07-01: Update to PyBEST standard, including naming convention and exception class
# 2020-07-01: Update to new python features, including f-strings, abc class
# 2021-11: Rewrite of OccModel to make class more general
# 2023-12: Julian Świerczyński - For occ models added function that automatically computes the number of
# frozen core atomic orbitals using information provided in `elements.csv`.

"""
Occupation number models.

OccupationModel is an abstract base class from which all occupation models are
derived. It only contains a minimum number of attributes that are common to
all child classes:

    * nbasis (total number of basis functions)

    * charge (charge of quantum system)

    * nel (total number of electrons)

    * basis (an instance of Basis or LinalgFactory)


Note that in all occupation models, only the occupation pattern of the
principal configuration is defined. Thus, for a wave function with a single
Slater determinant, one can occupy the orbitals according to a specific
occupation pattern defined in each child class.

For multi-configurational wave functions, the occupation model specifies
how many frozen, inactive, active, and external orbitals are defined.
These attributes have typically no effect on wave function models optimizing
a single Slater determinant (Hartree-Fock, etc.).

There are two main child classes that directly inherit from OccupationModel.
The occupation numbers are assigned (i) using the Aufbau principle or (ii)
using fixed occupation number vectors. These are:

    * AufbauOccModel

    * FixedOccModel

"""

from __future__ import annotations

import abc
import csv

from pybest.context import context
from pybest.exceptions import ArgumentError, ElectronCountError, FactoryError
from pybest.gbasis import Basis
from pybest.linalg import (
    CholeskyLinalgFactory,
    DenseLinalgFactory,
    LinalgFactory,
)
from pybest.log import log
from pybest.utility import check_type

# 22 is the column number in the file `elements.csv` file, which contains the number of
# frozen core atomic orbitals
FROZEN_CORE_INDEX = 22


class OccupationModel(abc.ABC):
    """Base class for the occupation models.

    It only assigns the total number of basis functions, charge, and number of
    electrons. All other properties are model-specific and assigned in child
    classes.

    Class attributes can be assigned in two ways:

    1) Using a Basis instance. Here, nel is deduced from the electronic
    charge and the corresponding atomic charges. nocc_a and nocc_b are not
    used here. We only check for consistencies (nel = nocc_a + nocc_b), but
    nel is not assigned using nocc_a/nocc_b

    2) Using an LF instance. Here, nel is specified by the user either using
    the nel keyword argument or nocc_a/nocc_b. If both are given, we check for
    consistencies (nel = nocc_a + nocc_b). The charge has no effect here.

    """

    long_name = ""

    def __init__(self, factory: Basis | LinalgFactory, **kwargs) -> None:
        """
        **Arguments:**

        factory:
            A Basis instance (e.g., for molecules) or a LinalgFactory instance
            (e.g., for model Hamiltonians).

        **Keyword arguments:**

        charge:
            Total charge of the system (int, default: 0).

        nel:
            (int) number of electrons. This input can be used for model
            Hamiltonians (optional, default: None).

        nbasis:
            (list of int) total number of basis functions.

        nocc_a, nocc_b:
            (int) number of occupied alpha, beta orbitals (optional, default:
            None). We perform a consistency check: nel == nocc_a + nocc_b.
            Note, this kwarg is only supported by some child classes.
        """
        check_type("basis/lf", factory, Basis, LinalgFactory)
        self._factory = factory
        # specify number of electrons
        self._charge = kwargs.get("charge", 0)
        self._nel = kwargs.get("nel", None)
        nocc_a = kwargs.get("nocc_a", None)
        nocc_b = kwargs.get("nocc_b", nocc_a)

        #
        # Distinguish between Basis and LF instances
        #
        if isinstance(self.factory, Basis):
            self._nbasis = [self.factory.nbasis]
            nel_ = sum(self.factory.atom) - self.charge
            # Check and if needed reassign to self.nel
            self.nel = nel_
        if isinstance(self.factory, LinalgFactory):
            self._nbasis = [self.factory.default_nbasis]
            # Use either nel or nocc_a kwargs
            if self.nel is None and nocc_a is None:
                raise ArgumentError(
                    "Either nel or nocc_a has to be specified."
                )
            if nocc_a is not None:
                # Check and if needed reassign to self.nel
                self.nel = nocc_a + nocc_b
            # Print warning if user speficies charge:
            if "charge" in kwargs:
                if log.do_medium:
                    log.warn(
                        "Ignoring keyword argument charge. Not used here."
                    )
        # In case the users specifies also nocc_a/nocc_b, check for
        # consistency
        if nocc_a is not None or nocc_b is not None:
            self._check_nocc(nocc_a, nocc_b)
        #
        # Print some information
        #
        if log.do_medium:
            log.hline("~")
            log("Occupation Module:")
            log(" ")
            log(f"{self.long_name}")
            log.hline("+")
            log(f"{'Total number of electrons:':>40} {self.nel}")
            log(f"{'Total electronic charge:':>40} {self.charge}")

    @property
    def factory(self):
        """A Basis or LinalgFactory instance depending on the chosen
        Hamiltonian
        """
        return self._factory

    @property
    def nbasis(self):
        """The total number of basis functions"""
        return self._nbasis

    @property
    def nel(self):
        """The number of electrons"""
        return self._nel

    @nel.setter
    def nel(self, nel):
        """Check consistency of user-specified nel with class-assigned value.
        If required, re-assign new value nel.
        self.nel can only be overwritten if the original value is set to None.

        If self.nel is None, we check if self.nel and nel are equivalent and
        raise an error otherwise.
        If the number of electrons changes, it is better to initialize a new
        instance with well-set properties.
        """
        # Check argument
        if nel is None:
            raise ArgumentError("Number of electrons cannot be None.")
        # If self.nel has not been specified yet, set to nel
        if self.nel is None:
            self._nel = nel
        # Check for consistency
        if nel != self.nel:
            raise ElectronCountError(
                "Number of electrons nel does not agree with user-defined "
                f"input {self.nel} and {nel}. Cannot reset number of electrons."
            )
        if self.nel <= 0:
            raise ElectronCountError(
                "The total number of electrons has to be greater than 0."
            )

    @property
    def charge(self):
        """The total electronic charge of the system"""
        return self._charge

    def _check_nocc(self, nocc_a, nocc_b):
        """Check whether nocc_a/nocc_b are properly defined and result in the
        correct number of electrons stored in self.nel
        """
        if nocc_a is None and nocc_b is not None:
            raise ArgumentError(
                "nocc_a needs to be defined first, then nocc_b."
            )
        if nocc_b is None:
            nocc_b = nocc_a

        nocc_ab = nocc_a + nocc_b
        if self.nel != nocc_ab:
            raise ElectronCountError(
                f"Number of electrons {self.nel} does not agree with orbital"
                f" occupations/charge of {nocc_ab}"
            )
        if self.nel == 0 and nocc_a == 0:
            raise ElectronCountError(
                "Either nel or nocc_a have to be specified."
            )
        if nocc_a < nocc_b:
            raise ElectronCountError(
                "nocc_a has to be greater or equal to nocc_b. Specified "
                f"nocc_a = {nocc_a} and nocc_b = {nocc_b}."
            )
        if nocc_a < 0 or nocc_b < 0:
            raise ArgumentError(
                "The number of occupied orbitals cannot be negative."
            )

    @abc.abstractmethod
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

    @abc.abstractmethod
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

    @classmethod
    def from_hdf5(cls, grp):
        """Construct an instance from data previously stored in an h5py.Group.

        **Arguments:**

        grp
             An h5py.Group object.
        """
        basis = cls._gobasis_from_hdf5(grp)
        kwargs = cls._attrs_from_hdf5(grp)
        result = cls(basis, **kwargs)
        return result

    def to_hdf5(self, grp):
        """Dump this object in an h5py.Group

        **Arguments:**

        grp
             An h5py.Group object.
        """
        grp.attrs["class"] = self.__class__.__name__
        # Class specific attributes
        self._attrs_to_hdf5(grp)
        # Basis/LF information
        if isinstance(self.factory, Basis):
            # dumb basis set using monkeypatch
            self.factory.to_hdf5(grp)
        if isinstance(self.factory, LinalgFactory):
            # dump information on default basis set size and lf class name
            grp.attrs["default_nbasis"] = self.factory.default_nbasis
            grp.attrs["lf"] = self.factory.__class__.__name__

    @staticmethod
    def _gobasis_from_hdf5(grp):
        """Get proper Basis/LF instance from stored file.

        **Arguments:**

        grp
             An h5py.Group object.
        """
        # Check if we are dealing with Basis or LF instance
        if "basisname" in grp.attrs:
            return Basis.from_hdf5(grp)
        linear_factory = grp.attrs["lf"]
        # distinguish between different lf flavors
        if linear_factory == "DenseLinalgFactory":
            return DenseLinalgFactory.from_hdf5(grp)
        if linear_factory == "CholeskyLinalgFactory":
            return CholeskyLinalgFactory.from_hdf5(grp)
        raise ArgumentError(f"Unkown lf class {linear_factory}")

    def _attrs_to_hdf5(self, grp):
        """Write attributes for some occupation model.

        **Arguments:**

        grp
             An h5py.Group object.
        """
        grp.attrs["charge"] = self.charge
        grp.attrs["nel"] = self.nel

    @staticmethod
    def _attrs_from_hdf5(grp):
        """Return valid kwargs for some occupation model.

        **Arguments:**

        grp
             An h5py.Group object.
        """
        return {
            "charge": grp.attrs["charge"],
            "nel": grp.attrs["nel"],
        }

    def check_ncore(self, **kwargs):
        """Determine the number of frozen core orbitals for Basis"""
        # defaults to -1 for Molecules, to 0 for LinalgFactory, respectively
        ncore_ = -1 if isinstance(self.factory, Basis) else 0
        # if ncore=-1, auto_core is defaulted to True
        # if ncore>= 0, auto_core is defaulted to False
        ncore = kwargs.get("ncore", ncore_)

        auto_ncore = kwargs.get("auto_ncore", ncore == -1)

        if auto_ncore and ncore >= 0:
            log.warn(
                "You specified both `ncore` and `auto_ncore`! `ncore` takes priority!"
            )
        if auto_ncore and ncore < 0:
            ncore = self.number_ncore()
        return ncore

    def number_ncore(self, atoms=None) -> int:
        """Function that automatically computes the number of
        frozen core atomic orbitals using information provided in `elements.csv`.
        The information contained in `elements.csv` is based on NWChem atomic core defaults.
        """
        log("\nAutomatically choosing frozen core orbitals.")
        log("If you prefer a different choice, set the `ncore` argument.\n")
        ncore = 0
        index = 0  # In the elements.csv file, the first column is int(atomic number)
        if not isinstance(self.factory, Basis):
            raise FactoryError(
                "\nWe can only automatically calculate frozen core orbitals when Basis is provided.\n"
            )

        # Checking given argument (we can provide arguments manually)
        if atoms is None:
            # Checking whether factory has the atom property
            if hasattr(self.factory, "atom"):
                atoms = self.factory.atom
        else:
            # If we have a single int(atomic number) or str(atomic symbol)
            if isinstance(atoms, (int, str)):
                atoms = [atoms]
            # If we have a list of int(atomic number) or str(atomic symbol)
            if isinstance(atoms, list):
                if all(isinstance(item, str) for item in atoms):
                    # In the elements.csv file, the secend column is str(atomic symbol)
                    index = 1
        # Reading the file line by line and search for atomic number or symbol to grab the number of
        # frozen core atomic orbitals
        with open(context.get_fn("elements.csv"), encoding="UTF-8") as file:
            rows = csv.reader(file)
            for atom in atoms:
                # Go back to the first line in the file
                file.seek(0)
                for row in rows:
                    # Searching for a frozen core index
                    if row[index] == str(atom):
                        ncore += int(row[FROZEN_CORE_INDEX])
                        break
        return ncore
