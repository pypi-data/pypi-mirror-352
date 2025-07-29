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

Orbitals are occupied in accordance with the Aufbau principle, where the orbitals
of each channel are occupied with respect to their energy. That means, the
electrons are put into the orbitals of lowest energy. The rules are as follows:

    * The basic rules of AufbauOccModel apply

    * The electrons are put into the orbitals of lowest energy considering
      both the alpha and beta channels.

Note that the occupation of alpha and beta orbitals can change during the
optimization of the wave function. The corresponding attributes of the
AufbauOccModel are updated by the assign_occ_reference function.

The AufbauSpinOccModel should NOT be used in combination with multi-configurational
wave functions as it is designed for models optimizing a single Slater
determinant using unrestricted orbitals.

"""

# package imports
from pybest.exceptions import (
    ArgumentError,
    ConsistencyError,
    ElectronCountError,
)
from pybest.log import log

# module imports
from pybest.occ_model import AufbauOccModel
from pybest.utility import unmask_orb


class AufbauSpinOccModel(AufbauOccModel):
    """This Aufbau model only applies to unrestricted wavefunctions"""

    long_name = (
        "Spin aufbau occupation number model for unrestricted wave functions"
    )

    def _set_attributes(self, **kwargs):
        """Set all class attributes."""
        ncore = self.check_ncore(**kwargs)

        #
        # Some temporary variables
        #
        n_doubly_occ = self.nel // 2
        alpha = self.nel % 2
        nbasis = self.nbasis[0]
        nvirt = nbasis - n_doubly_occ
        #
        # Do some sanity checks
        #
        self._check_attributes(n_doubly_occ, alpha, ncore)
        #
        # Assign all occupied and virtual orbitals (list) using the Aufbau
        # principle
        #
        # First alpha spin block; add singly occupied orbitals to alpha block
        self._nocc = [n_doubly_occ + alpha]
        self._nvirt = [nvirt - alpha]
        self._nacto = [n_doubly_occ - ncore + alpha]
        self._nactv = [nvirt - alpha]
        self._nact = [nbasis - ncore]
        self._ncore = [ncore]
        self._nspin = [n_doubly_occ + alpha]
        # Second spin block
        self._nocc.append(n_doubly_occ)
        self._nvirt.append(nvirt)
        self._nacto.append(n_doubly_occ - ncore)
        self._nactv.append(nvirt)
        self._nact.append(nbasis - ncore)
        self._nbasis.append(nbasis)
        self._ncore.append(ncore)
        self._nspin.append(n_doubly_occ)

    @staticmethod
    def _check_kwargs(supported_kwargs=None, **kwargs):
        """Check for valid keyword arguments."""
        supported_kwargs = ["nel", "ncore", "charge", "auto_ncore"]
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
        return {
            "charge": grp.attrs["charge"],
            "nel": grp.attrs["nel"],
            "ncore": grp.attrs["ncore"],
        }

    def print_info(self):
        """Print attributes of occupation model"""
        if log.do_medium:

            def resolve(list_):
                return " ".join(f"{s!s:<5s}" for s in list_)

            spin = f"{'':>40} alpha"
            log(f"{spin}" if len(self.nbasis) == 1 else f"{spin} beta")
            log(
                f"{'Total number of basis functions:':>40} {resolve(self.nbasis)}"
            )
            log(
                f"{'Number of frozen core orbitals:':>40} {resolve(self.ncore)}"
            )
            log.warn(
                f"{type(self).__name__} assigns alpha and beta occupations "
                "on-the-fly. Thus, no information can be given here."
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
        nel = self.nel
        ialpha = 0
        ibeta = 0
        # We always assume that first set of orbitals is alpha, second is beta
        orb_a, orb_b = unmask_orb(*orbs)
        # remove previous information on occupations
        orb_a.occupations[:] = 0.0
        orb_b.occupations[:] = 0.0
        while nel > 0:
            if orb_a.energies[ialpha] <= orb_b.energies[ibeta]:
                orb_a.occupations[ialpha] = min(1.0, nel)
                ialpha += 1
            else:
                orb_b.occupations[ibeta] = min(1.0, nel)
                ibeta += 1
            nel -= 1
        #
        # Overwrite all properties
        #
        self._nocc = [ialpha, ibeta]
        self._nspin = [ialpha, ibeta]
        self._nacto = [
            nocc - ncore for nocc, ncore in zip(self.nocc, self.ncore)
        ]
        self._nvirt = [
            nbasis - nocc for nbasis, nocc in zip(self.nbasis, self.nocc)
        ]
        self._nactv = self.nvirt

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
        if olp is None:
            check = abs(sum(dm.contract("aa") for dm in dms) - self.nel) < eps
        else:
            check = (
                abs(sum(olp.contract("ab,ba", dm) for dm in dms) - self.nel)
                < eps
            )
        if not check:
            raise ElectronCountError(
                "1-RDM does not contain correct number of electrons"
            )
