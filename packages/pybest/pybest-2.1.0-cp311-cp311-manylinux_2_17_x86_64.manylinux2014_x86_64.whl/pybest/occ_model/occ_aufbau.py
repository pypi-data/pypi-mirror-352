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
# 2025-01-26: Iulia Emilia Brumboiu added nactc (number of active core orbitals)
# to enable the core-valence separation approximation (for X-ray absorption and X-ray
# photoelectron spectroscopy calculations).
# 2025-04: Lena Szczuczko added nactdo and nactdv


"""
The Aufbau occupation number model

Child class of OccupationModel. This model contains additional properties that
are uniquely defined by the chosen flavor of the AufbauOccModel.

    * nocc: the number of occupied orbitals (list) with non-zero occupation
            numbers; defined with respect to some principal determinant

    * nvirt: the number of virtual orbitals (list); nbasis - nocc

    * ncore: the number of frozen core orbitals (list)

    * nactc: the number of active core orbitals (list); this is used for
             core-valence separation approximation (necessary for e.g.
             X-ray absorption spectroscopy calculations); zero by default

    * nacto: the number of active occupied orbitals (list); ; defined with
             respect to some principal determinant; nocc - nactc - ncore

    * nactv: the number of active virtual orbitals (list)

    * nact: the number of active basis functions (list)

    * nspin: the number of electrons in each spin channel (list)

    * nactdo: the number of active dressed occupied orbitals (list)

    * nactdv: the number of avtive dressed virtual orbitals (list)

Orbitals are occupied in accordance with the Aufbau principle. The rules are
as follows:

    * The first N/2 orbitals are occupied

    * Singly occupied orbitals are considered to be alpha orbitals

    * All attributes (ncore, nocc, nact, etc.) are lists. The first element
      corresponds to alpha orbitals, the second element (if present) to beta
      orbitals

Other occupation model classes inherit from the AufbauOccModel class. These
are:

    * FractionalOccModel

    * AufbauSpinOccModel

    * FermiOccModel

"""

# package imports
from __future__ import annotations

from pybest.exceptions import (
    ArgumentError,
    ConsistencyError,
    ElectronCountError,
)
from pybest.gbasis import Basis
from pybest.linalg import LinalgFactory
from pybest.log import log

# module imports
from pybest.occ_model.occ_base import OccupationModel


class AufbauOccModel(OccupationModel):
    """The standard Aufbau occupation number model.

    This model occupies the lowest lying orbitals. The number of doubly
    occupied orbitals is determined either automatically or extracted from
    the ``nocc_a`` and ``nocc_b`` keyword arguments. All singly occupied
    orbitals are put into the alpha orbitals.
    """

    long_name = "Aufbau occupation number model."

    def __init__(self, *noccs, **kwargs):
        """
        **Arguments:**

        nalpha, nbeta, ...
            The number of electrons in each channel. (To be deleted after grace
            period)

        basis
            A Basis instance.

        **Keyword arguments:**

        charge
            Total charge of the system (int, default: 0)

        nocc_a, nocc_b
            (int) number of occupied orbitals in alpha and beta vectors. nocc_b
            is defaulted to nocc_a if not specified.

        alpha:
            (int) the excess of alpha electrons.

        ncore:
            (int) number of frozen core orbitals. The number of frozen core orbitals is equal for alpha and beta orbitals.

        nactc:
            (int) number of active core orbitals. The number of active core
            orbitals is equal for alpha and beta orbitals. Zero by default.

        nactdo:
            (int) number of active dressed occupied orbitals.

        nactdv:
            (int) number of active dressed virtual orbitals.
        """
        # Workaround to distinguish between noccs numbers (old version) and
        # basis/lf instance (new version)
        # TBD (To Be Deleted): start
        basis = None
        for arg in noccs:
            if isinstance(arg, (Basis, LinalgFactory)):
                basis = arg
        # end
        # if not found basis, do old stuff:
        # TBD: start
        if basis is None:
            OccupationModel.__init__(self, basis, **kwargs)
            for nocc in noccs:
                if nocc < 0:
                    raise ElectronCountError(
                        "Negative number of electrons is not allowed."
                    )
            if sum(noccs) == 0 and self.factory is None:
                raise ElectronCountError("At least one electron is required.")
            self._nocc = noccs
            self._nspin = noccs
        # end
        else:
            #
            # NOTE: Here starts the new code
            #
            # First, check if proper kwargs are given as various child classes
            # support different kwargs
            #
            self._check_kwargs(**kwargs)
            #
            # Number of occupied orbitals can be assigned as follows
            # 1) using nel, alpha, and charge attributes
            # 2) using nocc_a and/or nocc_b attributes
            nocc_a = kwargs.get("nocc_a", 0)
            nocc_b = kwargs.get("nocc_b", nocc_a)

            #
            # First check for valid occupations for aufbau model if specified
            #
            self._check_nocc_aufbau(nocc_a, nocc_b)
            #
            # Call base class method (with proper nocc_a/nocc_b)
            #
            OccupationModel.__init__(self, basis, **kwargs)
            #
            # Set class attributes and check for consistency
            #
            self._set_attributes(**kwargs)
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
            "alpha",
            "charge",
            "nel",
            "ncore",
            "nocc_a",
            "nocc_b",
            "nactc",
            "auto_ncore",
            "nactdo",
            "nactdv",
        ]
        for kwarg in kwargs:
            if kwarg not in supported_kwargs:
                raise ArgumentError(f"Keyword {kwarg} not recognized.")

    def _set_attributes(self, **kwargs):
        """Set all class attributes."""
        #
        # Some default values for kwargs
        # set alpha to the smallest possible number of unpaired electrons: 0 or 1
        alpha = kwargs.get("alpha", self.nel % 2)

        ncore = self.check_ncore(**kwargs)

        nocc_a = kwargs.get("nocc_a", None)
        nocc_b = kwargs.get("nocc_b", nocc_a)
        nactc = kwargs.get("nactc", 0)
        nactdo = kwargs.get("nactdo", 0)
        nactdv = kwargs.get("nactdv", 0)

        #
        # If nocc_a and nocc_b are given, check and adjust alpha
        #
        if nocc_a is not None and alpha != nocc_a - nocc_b:
            alpha = nocc_a - nocc_b
            if log.do_medium:
                log.warn(f"Adjusting alpha to {alpha} unpaired electron(s).")
        # Check also unrestricted kwargs
        unrestricted = kwargs.get("unrestricted", alpha != 0)
        if (alpha != 0) and not unrestricted:
            raise ConsistencyError(
                "Cannot enforce a restricted occupation pattern if the system"
                " contains unpaired electrons."
            )
        #
        # Some temporary variables
        #
        n_doubly_occ = (self.nel - alpha) // 2
        nbasis = self.nbasis[0]
        nvirt = nbasis - n_doubly_occ
        #
        # Do some sanity checks
        #
        self._check_attributes(n_doubly_occ, alpha, ncore)
        #
        # Check if nactdo and nactdv are consistent with nacto and nactv
        #
        if nactdo > n_doubly_occ - ncore - nactc + alpha:
            raise ConsistencyError(
                "The number of active dressed occupied orbitals is larger"
                " than the number of active occupied orbitals."
            )
        if nactdv > nvirt - alpha:
            raise ConsistencyError(
                "The number of active dressed virtual orbitals is larger"
                " than the number of active virtual orbitals."
            )
        #
        # Assign all occupied and virtual orbitals (list) using the Aufbau
        # principle
        #
        # First alpha spin block; add singly occupied orbitals to alpha block
        self._nocc = [n_doubly_occ + alpha]
        self._nvirt = [nvirt - alpha]
        self._nacto = [n_doubly_occ - ncore - nactc + alpha]
        self._nactc = [nactc]
        self._nactv = [nvirt - alpha]
        self._nact = [nbasis - ncore]
        self._ncore = [ncore]
        self._nspin = [n_doubly_occ + alpha]
        self._nactdo = [nactdo]
        self._nactdv = [nactdv]
        # Second spin block in case of unpaired electrons or nocc_b (works
        # also for closed-shell systems)
        if alpha > 0 or hasattr(kwargs, "nocc_b") or unrestricted:
            self._nocc.append(n_doubly_occ)
            self._nvirt.append(nvirt)
            self._nacto.append(n_doubly_occ - ncore - nactc)
            self._nactc.append(nactc)
            self._nactv.append(nvirt)
            self._nact.append(nbasis - ncore)
            self._nbasis.append(nbasis)
            self._ncore.append(ncore)
            self._nspin.append(n_doubly_occ)
            self._nactdo.append(nactdo)
            self._nactdv.append(nactdv)

    @property
    def nocc(self) -> tuple | list:
        """The number of occupied orbitals"""
        return self._nocc

    @property
    def nvirt(self) -> list:
        """The number of virtual orbitals"""
        return self._nvirt

    @property
    def ncore(self) -> list:
        """The number of frozen core orbitals"""
        return self._ncore

    @property
    def nacto(self) -> list:
        """The number of active occupied orbitals"""
        return self._nacto

    @property
    def nactc(self) -> list:
        """The number of active core orbitals"""
        return self._nactc

    @property
    def nactv(self) -> list:
        """The number of active virtual orbitals"""
        return self._nactv

    @property
    def nact(self) -> list:
        """The number of active basis functions"""
        return self._nact

    @property
    def nspin(self) -> tuple | list:
        """The number of electrons in each spin channel (list)"""
        return self._nspin

    @property
    def nactdo(self) -> list:
        """The number of active dressed occupied orbitals"""
        return self._nactdo

    @property
    def nactdv(self) -> list:
        """The number of active dressed virtual orbitals"""
        return self._nactdv

    def _check_nocc_aufbau(self, nocc_a, nocc_b):
        """Check consistency of nocc_a/nocc_b"""
        if not isinstance(nocc_a, int) or not isinstance(nocc_b, int):
            raise ConsistencyError(
                f"Only integer occupations are allowed in {type(self).__name__}"
            )

    def _check_attributes(self, n_doubly_occ, alpha, ncore):
        """Check if attributes are properly assigned"""
        nbasis = self.nbasis[0]
        nvirt = nbasis - n_doubly_occ
        if (n_doubly_occ + alpha) <= 0:
            raise ElectronCountError(
                "The number of alpha electrons has to be larger than 0."
            )
        if (n_doubly_occ + alpha - ncore) <= 0:
            raise ConsistencyError(
                "Number of active occupied orbitals has to be larger than 0."
            )
        # Formally, nvirt can be 0. HF-type methods will work, post-HF not
        if (nvirt - alpha) < 0 or nvirt < 0:
            raise ConsistencyError(
                "Number of occupied orbitals is larger than the total "
                "number of basis functions."
            )
        if nbasis - ncore < 0:
            raise ConsistencyError("Too many frozen core orbitals defined.")
        if ncore < 0:
            raise ConsistencyError(
                "Number of frozen core orbitals cannot be negative."
            )
        if (self.nel - alpha) % 2 != 0:
            raise ConsistencyError(
                "Total number of electrons and number of unpaired electrons "
                f"are inconsistent. We have {self.nel} electrons and {alpha}"
                " unpaired electrons."
            )

    @staticmethod
    def _attrs_from_hdf5(grp):
        """Return valid kwargs for some Aufbau occupation model.

        **Arguments:**

        grp
             An h5py.Group object.
        """
        return {
            "charge": grp.attrs["charge"],
            "nel": grp.attrs["nel"],
            "unrestricted": grp.attrs["unrestricted"],
            "ncore": grp.attrs["ncore"],
            "alpha": grp.attrs["alpha"],
        }

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
        grp.attrs["alpha"] = self.nspin[0] - self.nspin[-1]
        grp.attrs["ncore"] = self.ncore[0]
        grp.attrs["unrestricted"] = len(self.nspin) == 2

    def print_info(self):
        """Print information on occupation number module."""

        def resolve(list_):
            return " ".join(f"{s!s:<5s}" for s in list_)

        spin = f"{'':>40} alpha"
        log(f"{spin}" if len(self.nbasis) == 1 else f"{spin} beta")
        log(f"{'Total number of basis functions:':>40} {resolve(self.nbasis)}")
        log(f"{'Total number of occupied orbitals:':>40} {resolve(self.nocc)}")
        log(f"{'Total number of virtual orbitals:':>40} {resolve(self.nvirt)}")
        log(f"{'Number of frozen core orbitals:':>40} {resolve(self.ncore)}")
        log(
            f"{'Number of active core orbitals (CVS):':>40} {resolve(self.nactc)}"
        )
        log(
            f"{'Number of active occupied orbitals:':>40} {resolve(self.nacto)}"
        )
        log(
            f"{'Number of active virtual orbitals:':>40} {resolve(self.nactv)}"
        )
        log(f"{'Number of active orbitals:':>40} {resolve(self.nact)}")
        log(
            f"{'Number of electrons for each spin:':>40} {resolve(self.nspin)}"
        )
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
        if len(orbs) != len(self.nocc):
            raise ConsistencyError(
                f"Expected {len(self.nocc)} orbitals, got {len(orbs)}."
            )
        for orb, nocc in zip(orbs, self.nocc):
            if orb.nfn < nocc:
                raise ElectronCountError(
                    "The number of orbitals must not be lower than the number of alpha "
                    "or beta electrons."
                )
            # It is assumed that the orbitals are sorted from low to high energy.
            orb.occupations[: int(nocc)] = 1.0
            orb.occupations[int(nocc) :] = 0.0

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
