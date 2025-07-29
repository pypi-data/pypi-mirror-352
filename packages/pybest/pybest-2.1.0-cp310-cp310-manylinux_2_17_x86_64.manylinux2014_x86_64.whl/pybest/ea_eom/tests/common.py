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
#
# 2024: This module has been originally written by Katharina Boguslawski
# 2025: Added support of general EA-CC (Saman Behjou)
# 2025: Added support for the molecule testing framework (Julia Szczuczko).

# imports for old Molecule
from pybest.context import context
from pybest.ea_eom.xea_pccd import RDEApCCD, REApCCD
from pybest.geminals import ROOpCCD, RpCCD
from pybest.iodata import IOData
from pybest.linalg import (
    DenseFourIndex,
    DenseTwoIndex,
)
from pybest.tests.molecule import BaseMolecule


class EA_EOMMolecule(BaseMolecule):
    """Represents an Electron Attachment (EA) Equation of Motion (EOM) molecule.

    This class extends `BaseMolecule` to incorporate electron attachment methods
    for various coupled-cluster (CC) and perturbative approaches.

    Attributes:
        hf (None or object): Hartree-Fock reference state.
        pccd (None or object): Pair coupled-cluster doubles (pCCD) method.
        ea_pccd (None or object): Electron-attached pCCD method.
        dea_pccd (None or object): Double-electron-attached pCCD method.
        rcc (None or object): All possible restricted CC methods.
        ea_rcc (None or object): All possible EA-CC variants.
        args (tuple): Collection of key molecular arguments.
        amplitudes (dict): Dictionary of CC amplitudes including `t_1`, `t_2`, and `t_p`.
        t (tuple): Tuple containing `t_1`, `t_2`, and `t_p` amplitudes.

    Args:
        molfile (str): Path to the molecular input file.
        basis (str): Basis set specification.
        lf_cls (object): Localized function class for CC methods.
        **kwargs: Additional keyword arguments for `BaseMolecule`.
    """

    def __init__(self, molfile, basis, lf_cls, **kwargs):
        """Initializes the EA_EOMMolecule instance.

        Args:
            molfile (str): Path to the molecular input file.
            basis (str): Basis set specification.
            lf_cls (object): Localized function class for CC methods.
            **kwargs: Additional keyword arguments for `BaseMolecule`.
        """
        super().__init__(molfile, basis, lf_cls, **kwargs)

        self.pccd = None
        self.ea_pccd = None
        self.dea_pccd = None
        # Stores all CC method from CCD to fpCCSD
        self.rcc = None
        # Stores all EA-CC methods
        self.ea_rcc = None
        # Only used for testing purposes, we do not store any values here
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        self.t_p = DenseTwoIndex(nacto, nactv, label="t_p")
        self.args = (self.olp, *self.orb, *self.hamiltonian, self.t_p)
        self.t_1 = DenseTwoIndex(nacto, nactv, label="t_1")
        self.t_2 = DenseFourIndex(nacto, nactv, nacto, nactv, label="t_2")
        self.amplitudes = {"t_1": self.t_1, "t_2": self.t_2, "t_p": self.t_p}
        self.t = (self.t_1, self.t_2, self.t_p)

    def do_pccd(self, pccd_cls):
        """Do pCCD optimization based on input class pccd_cls using this class'
        RHF solution
        """
        if self.hf is None:
            raise ValueError("No RHF solution found.")
        pccd = pccd_cls(self.lf, self.occ_model)
        self.pccd = pccd(*self.hamiltonian, self.hf)

    def do_ea_pccd(self, alpha, nroot, spinfree=False):
        """Do EApCCD optimization based on input class pccd_cls using this
        class' pCCD solution
        """
        if self.pccd is None:
            raise ValueError("No pCCD solution found.")
        eapccd = REApCCD(
            self.lf, self.occ_model, alpha=alpha, spinfree=spinfree
        )
        self.ea_pccd = eapccd(*self.hamiltonian, self.pccd, nroot=nroot)

    def do_dea_pccd(self, alpha, nroot, n_particle_operator):
        """Do DEApCCD optimization based on input class pccd_cls using this
        class' pCCD solution
        """
        if self.pccd is None:
            raise ValueError("No pCCD solution found.")
        eapccd = RDEApCCD(self.lf, self.occ_model, alpha=alpha)
        self.dea_pccd = eapccd(
            *self.hamiltonian,
            self.pccd,
            nroot=nroot,
            nparticle=n_particle_operator,
        )

    def do_rcc(self, cc_cls, orbital_file=None):
        """Do RCC optimization using this class' RHF solution"""
        if self.hf is None:
            raise ValueError("No RHF solution found.")

        rcc_iodata = self.hf

        if RpCCD in cc_cls or ROOpCCD in cc_cls:
            # Maybe pass as first element
            rcc = cc_cls[0](self.lf, self.occ_model)
            # Load orbitals to be faster
            if orbital_file is not None:
                data = IOData.from_file(
                    context.get_fn("test/" + orbital_file + "_oopccd.molden")
                )
                self.hf.orb_a = data.orb_a
            rcc_iodata = rcc(self.hf, *self.hamiltonian)
            self.pccd = rcc_iodata

        # we assume that CC is passed as last element
        cc = cc_cls[-1](self.lf, self.occ_model)
        self.cc = cc(*self.hamiltonian, rcc_iodata, threshold_r=1e-8)

    def do_ea_rcc(self, rsf_cls, alpha, nroot):
        """Do EARCC optimization based on input class cc_cls using this
        class' RCCD solution
        """
        if self.cc is None:
            raise ValueError("No CC solution found.")
        earcc = rsf_cls(self.lf, self.occ_model, alpha=alpha)
        # Some quartet states cause problems and nguessv must be set to a large number
        self.ea_rcc = earcc(
            *self.hamiltonian,
            self.cc,
            nroot=nroot,
            nguessv=40 * nroot,
        )


def flatten_list(obj, *args):
    """Return a flattened list by resolving a list of attributes contained in
    args (list of str) from an instance obj.
    """
    # first use list comprehension to append all non-tuple objects
    flattened_list = list(
        getattr(obj, arg)
        for arg in args
        if not isinstance(getattr(obj, arg), list)
    )
    for arg in args:
        value = getattr(obj, arg)
        if isinstance(value, list):
            for element in value:
                flattened_list.append(element)
    return flattened_list
