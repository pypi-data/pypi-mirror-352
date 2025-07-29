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
# 11/2024: This file has been written by Seyedehdelaram Jahani (original version)
# 2025: Added support for the linear response method (Somayeh Ahmadkhani)
# 05/2025: This file has been updated to a new framework for test by Seyedehdelaram Jahani and Somayeh Ahmadkhani.

from pybest.context import context
from pybest.gbasis import (
    compute_dipole,
)
from pybest.geminals import RpCCD
from pybest.iodata import IOData
from pybest.tests.molecule import BaseMolecule
from pybest.utility import get_com
from pybest.wrappers.multipole import check_coord


class PropertyMolecule(BaseMolecule):
    """Set up molecule instance that contains all quantities to perform some
    QC calculation.
    """

    def __init__(self, molfile, basis, lf_cls, **kwargs):
        """Initialize the PropertyMolecule instance.

        Args:
            molfile (str): The path to the molecular file containing the molecular structure.
            basis (str): The basis set to be used for the calculations.
            lf_cls (type): The linalg flavour.
        """
        super().__init__(molfile, basis, lf_cls, **kwargs)

        # Define data property as a dummy input argument
        self.add_result(
            "data",
            IOData(orb_a=self.orb_a, olp=self.olp, e_core=self.external),
        )

    def read_molden(self, orb_file_name, property_name="data"):
        """Modify orbitals based on the given file.

        Args:
            orb (str): Filename containing the orbitals without file suffix
        """
        fn_orb = context.get_fn(f"test/{orb_file_name}.molden")
        data = IOData.from_file(fn_orb)
        self.orb_a = data.orb_a
        # Overwrite dummy property
        self.add_result(
            property_name,
            IOData(orb_a=self.orb_a, olp=self.olp, e_core=self.external),
        )

    def do_pccd(self, cls=RpCCD, input_key="data"):
        """Do a pCCD/OOpCCD calculation based on cls choice.

        Parameters:
            cls (class): RpCCD or ROOpCCD.
            input (str): key of property taken as input
        """
        # Get input IOData container
        pccd_input = self.get_result(input_key)
        # Run pCCD
        pccd = cls(self.lf, self.occ_model)
        self.pccd = pccd(*self.hamiltonian, pccd_input)
        # Store result as property
        self.add_result("pccd", self.pccd)

    def do_orbital_energies(self, cls, method):
        """Generalized orbital energies from Koopmans/Modified Koopmans calculation from IOData file"""
        # Input data used to calculate properties
        # Stored in BaseMolecule's property attribute
        e_orb_input = self.get_result(method)
        # Calculate orbital energies
        orbital_energies = cls(self.lf, self.occ_model)
        output_e_orb = orbital_energies(self.one, self.two, e_orb_input)
        self.add_result(f"{cls.__name__}", output_e_orb)

    def do_lr_dipole_moment(self, cls, cls_jac, method):
        """Generalized LRpCCD/pCCDS excitation energies and transition dipole moments from IOData file"""
        x, y, z = get_com(self.basis)
        self.dipole = compute_dipole(self.basis, x=x, y=y, z=z)
        self.coord = check_coord(self.dipole, self.pccd)

        data_input = self.get_result(method)

        # Build Jacobian matrix and calculate excitation energies by diagonalizing Jacobian matrix.
        jac_ee_pccd = cls_jac(self.lf, self.occ_model)
        out_jac_ee_pccd = jac_ee_pccd(
            self.one, self.two, data_input, self.pccd
        )
        # Calculate transition dipole moment.
        tm_di_pccd = cls(self.lf, self.occ_model)

        self.out_tdm = tm_di_pccd(
            self.one,
            self.two,
            out_jac_ee_pccd,
            property_options={
                "operator_A": self.dipole,
                "operator_B": self.dipole,
                "coordinates": self.coord,
                "transition_dipole_moment": True,
            },
            printoptions={"nroot": 7},
        )
        # self.add_result(f"{cls.__name__}", self.out_tdm)
