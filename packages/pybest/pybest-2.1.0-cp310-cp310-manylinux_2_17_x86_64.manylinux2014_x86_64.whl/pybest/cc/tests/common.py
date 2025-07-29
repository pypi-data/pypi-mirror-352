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
# 03/2025:
# This file has been modified by Somayeh Ahmadkhani and Lena Szczuczko
"""Common routines, classes, fixtures for CC tests."""

import numpy as np

from pybest.context import context
from pybest.geminals import ROOpCCD
from pybest.iodata import IOData
from pybest.linalg import DenseTwoIndex, FourIndex
from pybest.tests.molecule import BaseMolecule


class CCMolecule(BaseMolecule):
    """Handles all common pre-CC operations."""

    def __init__(self, molfile, basis, lf_cls, **kwargs):
        """Initialize the CCMolecule instance.

        Args:
            molfile (str): The path to the molecular file containing the molecular structure.
            basis (str): The basis set to be used for the calculations.
            lf_cls (type): The linalg flavour.
        """
        super().__init__(molfile, basis, lf_cls, **kwargs)

        self.pccd = None
        self.read = True

    def do_pccd(self, pccd_cls, hf: bool = True):
        """Perform pCCD optimization using the specified pCCD class.

        Args:
            pccd_cls: The class implementing the pCCD method.
            hf (bool, optional): If True, the pCCD optimization is based on the RHF solution.
                                 If False, the optimization is done without HF
                                 (used in test_rccs.py)

        Raises:
            ValueError: If no RHF solution is found.
        """
        pccd = pccd_cls(self.lf, self.occ_model)

        # If all additional arguments are None, call pccd as before
        if hf is True:
            if self.hf is None:
                raise ValueError("No RHF solution found.")
            self.pccd = pccd(*self.hamiltonian, self.hf)
        else:
            self.pccd = pccd(
                self.one, self.two, self.orb_a, self.olp, e_core=self.external
            )

    def read_oopccd(self, name):
        """Do OO-pCCD optimization based on input from a given file using RHF solution

        Args:
            name (str): The name of the file to read OO-pCCD results from.

        Raises:
            ValueError: No pCCD results found in the given file.
        """
        if self.hf is None:
            raise ValueError("No RHF solution found.")

        # Read pCCD orbitals and compute other pCCD-related quantities
        data = IOData.from_file(context.get_fn(name + "_pccd.molden"))
        # do oopccd
        pccd = ROOpCCD(self.lf, self.occ_model)
        self.pccd = pccd(
            *self.ints(),
            self.olp,
            data.orb_a,
            e_core=0.0,
            maxiter={"orbiter": 0},
        )

    def modify_orb(self, orb):
        """Modify orbitals based on the given file.

        Args:
            orb (str): Path to a file containing the orbitals
        """
        fn_orb = context.get_fn(orb)
        orb_ = np.fromfile(fn_orb, sep=",").reshape(
            self.basis.nbasis, self.basis.nbasis
        )
        self.orb_a._coeffs = orb_


def check_fock_in_cache(cache, labels, nocc=5, nvirt=8):
    """Check if labels correspond to Fock matrix blocks in cache."""
    dim = {"o": nocc, "v": nvirt}
    for label in labels:
        msg = f"{label} block in cc.hamiltonian: \n"
        matrix = cache.load(label)
        assert isinstance(matrix, DenseTwoIndex), msg + "incorrect type"
        assert matrix.shape[0] == dim[label[-2]], msg + "incorrect size"
        assert matrix.shape[1] == dim[label[-1]], msg + "incorrect size"
        # occupied-virtual block for RHF orbitals is zeros by nature
        if not label == "fock_ov":
            is_zeros = np.allclose(matrix.array, np.zeros(matrix.shape))
            assert not is_zeros, msg + " is filled with zeros!"


def check_eri_in_cache(cache, labels, nocc=5, nvirt=8):
    """Check if labels correspond to 2-body CC Hamiltonian blocks in cache."""
    dim = {"o": nocc, "v": nvirt}
    for label in labels:
        msg = f"Checking {label} block in cc.hamiltonian...\n"
        matrix = cache.load(label)
        assert isinstance(matrix, FourIndex), msg + "wrong type!"
        for i in range(4):
            assert matrix.shape[i] == dim[label[i - 4]], msg + "incorrect size"
        assert not np.allclose(matrix.array, np.zeros(matrix.array.shape))
        assert not np.isnan(matrix.array).any()
