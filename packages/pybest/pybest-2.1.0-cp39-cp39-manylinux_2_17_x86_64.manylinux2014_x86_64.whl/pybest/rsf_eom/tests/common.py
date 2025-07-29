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
# The RSF-CC sub-package has been originally written and updated by Aleksandra Leszczyk (see CHANGELOG)
# Its current version contains updates from the PyBEST developer team.
#
# 2023/24:
# This file has been updated by Emil Sujkowski (original version)

"""Common routines, classes, fixtures for EOM tests."""

from __future__ import annotations

from pybest.geminals import ROOpCCD, RpCCD
from pybest.tests.molecule import BaseMolecule


class RSF_EOM_CCMolecule(BaseMolecule):
    def __init__(self, molfile, basis, lf_cls, **kwargs):
        super().__init__(molfile, basis, lf_cls, **kwargs)

        self.cc = None
        self.rsf_cc = None

    def do_rxcc(self, cc_cls, solver, threshold=1e-6):
        """Do RCC optimization using this class' RHF solution
        This method works only when you pass either list of CC only or R(OO)pCCD as first element in the list and CC as second

        Args:
            cc_cls (list): CC class or R(OO)pCCD and CC classes
            solver (str): type of solver used
            threshold (float, optional): Tolerance for amplitudes. Defaults to 1e-6.

        Raises:
            ValueError: If no RHF optimization was done before
        """
        if self.hf is None:
            raise ValueError("No RHF solution found.")
        cc1_iodata = self.hf

        if RpCCD in cc_cls or ROOpCCD in cc_cls:
            cc1 = cc_cls[0](self.lf, self.occ_model)
            cc1_iodata = cc1(self.hf, *self.hamiltonian)

        cc = cc_cls[-1](self.lf, self.occ_model)
        self.cc = cc(
            *self.hamiltonian,
            cc1_iodata,
            threshold_r=threshold,
            solver=solver,
        )

    def do_rsf_cc(self, rsf_cls, alpha, nroot, nguessv):
        """Do RSFCC optimization based on input class cc_cls using this
        class' RCC solution

        Args:
            rsf_cls (RSFCCD | RSFCCSD): RSFCC class
            alpha (int): number of unpaired electrons
            nroot (int): number of roots
            nguessv (int): number of guess vectors

        Raises:
            ValueError: If no CC optimization was done before
        """
        if self.cc is None:
            raise ValueError("No CC solution found.")
        rsfcc = rsf_cls(self.lf, self.occ_model, alpha=alpha)
        self.rsf_cc = rsfcc(
            *self.hamiltonian, self.cc, nroot=nroot, nguessv=nguessv
        )
