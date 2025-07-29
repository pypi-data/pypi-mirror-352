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
# This module has been written and updated by Zahra Karimi in 11/2024 (see CHANGELOG).

"""Physical Model Hamiltonians' base functionality"""

from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

from pybest.context import context
from pybest.exceptions import ArgumentError
from pybest.featuredlists import SupportedAtomsPhysicalHam
from pybest.io import check_physical_ham_coordinates
from pybest.iodata import CheckPoint
from pybest.linalg import DenseLinalgFactory, DenseTwoIndex
from pybest.log import log
from pybest.units import electronvolt
from pybest.utility import check_options, check_type
from pybest.wrappers import RHF


class PhysModBase(ABC):
    """
    Base class for implementing Hamiltonians used in quantum chemistry and condensed matter physics.

    Supported Hamiltonians:
    - Hückel Hamiltonian: A tight-binding model using adjacency matrices based on covalent radii.
    - Hubbard Hamiltonian: Incorporates electron correlation through onsite interaction, tight-binding model + U term.
    - PPP Hamiltonian: The Pariser-Parr-Pople model, combining π-electron approximation with long-range electron interactions, Hubbard model + V term.
    - Contact Interaction in 1D: Models fermions with delta interactions in external potentials using a DVR grid.

    This class serves as a framework for defining and solving these Hamiltonians.

    Args:
        lf (LinalgFactory): Linear algebra factory for creating matrix structures.
        occ_model (AufbauOccModel): Occupation model for managing the numer of occupied electrons.
        xyz_file (str): Path to the xyz file containing atomic coordinates.
        elements_file (str, optional): Path to a csv file with covalent radii data (default: Cordero parameters from "elements.csv").


    Attributes:
        occ_model (property): Returns the occupation model.
        lf (property): Returns the linear algebra factory instance.
        denself (property): Returns a dense linear algebra factory for matrix operations.
        xyz_file (property): Path to the atomic coordinates file.
        checkpoint (property): Container for storing intermediate data and results.

    Requirements for Hartree-Fock calculations:
    compute_one_body():
        Abstract requirement for defining the one-body terms of the Hamiltonian.
    compute_two_body():
        Abstract requirement for defining the two-body terms of the Hamiltonian.
    compute_overlap():
        Requirement for defining the overlap matrix (identity for 1D systems).

    Methods:
        tight_binding_model():
        Abstract method for generating the Hamiltonian based on the specific model.
        print_info():
            Prints structural information about the system, including unsupported atoms.
        get_covalent_radius_cordero(atoms = None):
            Retrieves covalent radii for the specified atoms using "elements.csv".
        generate_adjacency_matrix():
            Generates an adjacency matrix based on covalent radii overlap.
        diagonalization(ham):
            Diagonalizes the given Hamiltonian and stores the sorted eigenvalues.
        rhf_diagonalization(*args, **kwargs):
            Performs restricted Hartree-Fock (RHF) diagonalization on the Hamiltonian.
        check_keywords(parameters):
            Validates the input parameters for supported keys and value types.
        read_input(*args, **kwargs):
            Reads input parameters and keyword options for integral transformations.
        print_result():
            Prints the calculated orbital energies and their associated gaps.
        __call__(*args, **kwargs):
            Executes the entire workflow, including reading input, computing the Hamiltonian,
            performing diagonalizations, and printing results.
    Raises:
        FileNotFoundError: If the "elements.csv" file is not found.
        ValueError: For invalid atom types or covalent radii data.
    """

    acronym = ""
    long_name = "Physical model Hamiltonians' base class"
    comment = ""

    def __init__(
        self,
        lf: DenseLinalgFactory,
        occ_model: Any,
        xyz_file: str | None = None,
        elements_file: str | None = None,
        model_name: str | None = None,
        pbc=False,
    ):
        """
        **Arguments:**

        lf
            The linear algebra factory used for matrix operations. Typically a `DenseLinalgFactory` instance.

        occ_model
            The occupation model defining the orbital occupation scheme for the system.

        xyz_file
            Path to the xyz file containing atomic coordinates of the system.

        **Optional arguments:**

        elements_file
            Path to a csv file containing covalent radii data for the elements. If not provided,
            a default file (`elements.csv`) is used from the context.

        **Attributes Initialized:**

        - `_xyz_file`: Stores the provided `xyz_file` path.
        - `_occ_model`: Stores the occupation model.
        - `_lf`: Stores the linear algebra factory.
        - `_denself`: Initializes a dense linear algebra factory.
        """
        self._xyz_file = xyz_file
        self._occ_model = occ_model
        self._lf = lf
        self._denself = DenseLinalgFactory(lf.default_nbasis)
        self.model_name = model_name
        self._pbc = pbc

        # Ensure self.elements_file is always defined
        if elements_file is None:
            elements_file = context.get_fn("elements.csv")

        elements_file = Path(elements_file)

        self._elements_file = elements_file

        self._checkpoint = CheckPoint({})
        self.adjacency_matrix = None

    @property
    def occ_model(self):
        """The occupation model. It contains all information on the number of
        active occupied, virtual.
        """
        return self._occ_model

    @property
    def lf(self):
        """The LinalgFactory instance."""
        return self._lf

    @property
    def denself(self):
        """The dense linalg factory."""
        return self._denself

    @property
    def xyz_file(self):
        """The xyz file containing atomic coordinates."""
        return self._xyz_file

    @property
    def pbc(self):
        """The periodic boundary conditions"""
        return self._pbc

    @property
    def checkpoint(self):
        """The IOData container that contains all data dump to disk."""
        return self._checkpoint

    @abstractmethod
    def tight_binding_model(self):
        """Tight-binding model based on the Physical Model Hamiltonian"""

    @abstractmethod
    def compute_one_body(self):
        """Calculate the one-body term of the 1D Physical Hamiltonian"""

    @abstractmethod
    def compute_two_body(self):
        """Calculate the two-body term of the 1D Physical Hamiltonian"""

    def compute_overlap(self) -> DenseTwoIndex:
        """The overlap integrals used for HF claculations"""
        result = self.lf.create_two_index(label="olp")
        result.assign_diagonal(1.0)
        return result

    def print_info(self, *args: Any, **kwargs: dict[str, Any]) -> None:
        """Print structural information about the system.

        Displays the total number of atoms, the name of the model Hamiltonian,
        and the symbols of supported atoms, excluding unsupported ones.
        """
        self.read_input(*args, **kwargs)
        coordinate = check_physical_ham_coordinates(self.xyz_file)
        symbols = coordinate["symbols"]
        supported_atoms = SupportedAtomsPhysicalHam
        n_symbols = Counter(symbols)
        # Create a compressed representation of atoms with counts (e.g., C4H10),
        # including only supported atoms to avoid repetition and unsupported entries.
        compressed_symbols = [
            f"{atom}{n_symbols[atom]}"
            for atom in supported_atoms
            if atom in n_symbols
        ]

        log.hline(" ")
        log(f"Entering the {self.__class__.long_name}")
        log(" ")
        log(f"{'Total number of atoms:':>32} {coordinate['natoms']}")

        log(f"{'Structure information for:':>32} {coordinate['title']}")
        log(" ")
        log(
            f"{'Symbols of supported atoms:':>32} {''.join(compressed_symbols)}"
        )
        log(
            f"{'On-site value (epsilon):':>32} {self.parameters.get('on_site') / electronvolt: 6.2f} eV"
        )
        log(
            f"{'Hubbard value (U):':>32} {self.parameters.get('u') / electronvolt: 6.2f} eV   |  {self.parameters.get('u'): 6.2f} a.u."
        )
        log(
            f"{'Hopping value (t):':>32} {self.parameters.get('hopping') / electronvolt: 6.2f} eV   |  {self.parameters.get('hopping'): 6.2f} a.u."
        )
        log(
            f"{'Dielectric constant (k):':>32} {self.parameters.get('k'): 6.2f} eV"
        )
        log(f"{'Hubbard term:':>32} {self.parameters.get('hubbard')}")
        log(f"{'RHF calculations:':>32} {self.parameters.get('rhf')}")

    def get_covalent_radius_cordero(self, atoms=None) -> list:
        """Retrieve covalent radii for the given atoms from 'elements.csv'.

        This function checks if the atoms are in the SupportedAtomsPhysicalHam set and retrieves
        the radius data. If no atoms are provided, it attempts to use `self.factory.atom`.
        Missing or invalid radii are replaced with `None`.

        Args:
        atoms (Any): Atoms for which radii are requested. If `None`, attempts to use `self.factory.atom`.

        Returns:
        list: List of covalent radii (floats) or `None` for missing data.
        """
        radius = []

        # Validate file existence
        if not Path.exists(self._elements_file):
            raise FileNotFoundError(
                f"The required file '{self._elements_file}' is not present."
            )

        if atoms is None:
            if hasattr(self.occ_model.factory, "atom"):
                atoms = self.occ_model.factory.atom
            else:
                raise ArgumentError("Cannot find atom argument!")

        if isinstance(atoms, (int, str)):
            atoms = [atoms]

        # Reads the elements file and creates a dictionary mapping each element symbol
        # to its covalent radius (column 5: cov_radius_cordero).
        with open(self._elements_file) as file:
            elements_data = {
                row[1].strip(): row[5].strip()
                for row in csv.reader(file)
                if row
            }
        for atom in atoms:
            atom_str = str(atom).strip()
            if atom_str not in SupportedAtomsPhysicalHam:
                raise ValueError(
                    f"Error: Atom {atom_str} is not in the list of SupportedAtomsPhysicalHam."
                )

            cov_radius = elements_data.get(atom_str)

            if cov_radius is not None:
                try:
                    radius.append(float(cov_radius))
                except ValueError:
                    log(
                        f"warning: Covalent radius is not a valid number for atom: {atom}"
                    )
                    radius.append(None)
            else:
                log(f"warning: Covalent radius not found for atom: {atom}")
                radius.append(None)

        return radius

    def generate_adjacency_matrix(self) -> Any:
        """Generate an adjacency matrix based on covalent radius overlap.

        Calculates the adjacency matrix by determining whether the covalent radii
        of pairs of atoms overlap, indicating bonded atoms. Only atoms within
        `supported_atoms` are considered.

        Returns:
        np.ndarray: A square matrix where each element represents whether
        a bond exists between two atoms (1 for bond, 0 for no bond).
        """
        coord_file = check_physical_ham_coordinates(self.xyz_file)

        coordinates = coord_file["supported_coordinates"]
        symbols = coord_file["symbols"]

        num_atoms = len(coordinates)

        # Create an empty two-index matrix using lf.create_two_index()
        adjacency_matrix = self.lf.create_two_index(label="adjacency")
        distance_matrix = self.lf.create_two_index(label="distance")

        if num_atoms < 2:
            log("warning: Not enough atoms to generate an adjacency matrix.")
            return adjacency_matrix, distance_matrix

        radius_list = self.get_covalent_radius_cordero(atoms=symbols)

        # Creating adjacency matrix in terms of covalent radius overlap
        for i in range(num_atoms):
            # Loop only over lower triangle (i > j, because of symmetry)
            for j in range(i):
                # Check if both atoms are in the list of supported atoms
                r_ij = np.linalg.norm(coordinates[i] - coordinates[j])
                if (
                    symbols[i] in SupportedAtomsPhysicalHam
                    and symbols[j] in SupportedAtomsPhysicalHam
                    and (radius_list[i] and radius_list[j])
                ):
                    # r_ij = np.linalg.norm(coordinates[i] - coordinates[j])
                    if r_ij <= radius_list[i] + radius_list[j]:
                        # Set the value = 1 for connected atoms
                        adjacency_matrix.set_element(i, j, 1, symmetry=2)
                distance_matrix.set_element(i, j, r_ij, symmetry=2)

            # Applying periodic boundary conditions for the upper triangle (i <= j)
            for j in range(i, num_atoms):
                block_i = i // num_atoms
                block_j = j // num_atoms

                if block_i == block_j:
                    # Applying periodic boundary conditions
                    ii = i % num_atoms
                    jj = j % num_atoms

                    adjacency_matrix.set_element(
                        i, j, adjacency_matrix.get_element(ii, jj), symmetry=2
                    )

        return adjacency_matrix, distance_matrix

    def diagonalization(
        self,
        hamiltonian: DenseTwoIndex,
        rhf: bool = False,
        *args: Any,
        **kwargs: dict[str, Any],
    ):
        """Diagonalizes the given Hamiltonian matrix, returning sorted eigenvalues."""
        # Step 1: Diagonalize the tight-binding part of the model
        # Hamiltonian in question (only 1-body components)
        # Getting the eigenvalues and eigenvectors
        evals = hamiltonian.diagonalize(eigvec=False, use_eigh=True)

        # Sort the eigenvalues and eigenvectors
        # Get indices that would sort `evals`
        sorted_indices = evals.sort_indices(reverse=True)
        # Sort eigenvalues
        sorted_evals = evals.array[sorted_indices]

        self.checkpoint.update("e_orb_tb", sorted_evals)

        # Step 2: Compute RHF solution (if required) for one- and two-body interactions.
        if rhf:
            # Compute the one-body Hamiltonian, two-body (zero for Huckel), and overlap
            one_body = self.compute_one_body()
            two_body = self.compute_two_body()
            orb_a = self.lf.create_orbital()

            # Compute the overlap matrix (if needed for the on-site basis)
            olp = self.compute_overlap()

            log_level = log.level
            log.level = 0

            hf = RHF(self.lf, self.occ_model)

            e_hf = hf(one_body, two_body, olp, orb_a)

            log.level = log_level

            self.checkpoint.update("orb_a", e_hf.orb_a.copy())
            self.checkpoint.update("e_tot", e_hf.e_tot)

    def check_keywords(self, parameters: dict[str, Any]) -> None:
        """Check dictionaries if they contain proper keys.

        **Arguments:**

        parameters (dict):
            Dictionary containing input parameters to be validated.

        **Notes:**

        This method validates the input dictionary `parameters` to ensure
        that it contains the expected keys and values. Specific checks and
        validations are performed based on the requirements of the
        :py:meth:`OrbitalEnergyBase.read_input` method.
        """
        #
        # Check parameters
        #
        for key, value in parameters.items():
            check_options(
                "parameters",
                key,
                "u",
                "hopping",
                "on_site",
                "k",
                "u_p",
                "hubbard",
                "rhf",
                "pbc",
            )
            if key == "u":
                check_type("parameters.u", value, float)
            elif key == "k":
                check_type("parameters.k", value, float)
            elif key == "u_p":
                check_type("parameters.u_p", value, float)
            elif key == "hopping":
                check_type("parameters.hopping", value, float)
            elif key == "on_site":
                check_type("parameters.on_site", value, float)
            elif key == "k":
                check_type("parameters.k", value, float)
            elif key == "hubbard":
                check_type("parameters.hubbard", value, bool)
            elif key == "pbc":
                check_type("pbc", value, bool)

    def read_input(self, *args: Any, **kwargs: dict[str, Any]) -> Any:
        """Read input parameters and keyword options for transforming electron integrals.

        **Positional Arguments** (passed via `args`):
            one (DenseOneIndex): The sum of all one-electron integrals, such as kinetic energy
                and potential energy contributions.
            two (DenseFourIndex, CholeskyIndex): Two-electron integrals in a chosen representation,
                used to describe electron repulsion interactions.
            orb (DenseOrbital): An expansion instance containing Molecular Orbital (MO) coefficients.

        **Keyword Arguments** (passed via `kwargs`):
            - `parameters` (dict, optional): Dictionary for controlling print options, with the
            following keys:
            - `warning` (bool, optional): Controls whether warning messages are printed during the
            execution. Default is False.
        """
        if log.do_medium:
            log.hline("=")
            log.cite("model Hamiltonians", "karimi2025")

        #
        # Assign keyword arguments
        #
        names = []

        # Helper function to retrieve values from kwargs with a default fallback, while tracking used names

        def _helper(x, y):
            names.append(x)
            return kwargs.get(x, y)

        warning = _helper("warning", False)
        _parameters = _helper("parameters", {})
        _parameters.setdefault("u", 0.0)
        _parameters.setdefault("hopping", -1.0)
        _parameters.setdefault("on_site", 0.0)
        _parameters.setdefault("k", 0.0)
        _parameters.setdefault("u_p", 0.0)
        _parameters.setdefault("hubbard", False)
        _parameters.setdefault("rhf", True)
        _parameters.setdefault("pbc", False)

        self.parameters = _parameters

        #
        # Check kwargs
        #
        for key, _value in kwargs.items():
            if key not in names:
                raise ArgumentError(f"Unknown keyword argument {key}")

        #
        # Check dictionaries in keyword arguments
        #
        self.check_keywords(_parameters)
        #
        # Check and validate 'warning' and print option types
        #
        # t: hopping, u: e-e repulsion, k: dielectric constant, u_p=u/k, hubbard: hubbard term in ppp.
        # rhf: RHF (Restricted Hartree-Fock) calculations
        # pbc: periodic boundary condition for 1d-hubbard model.
        check_options("warning", warning, False, True, 0, 1)
        check_type("u", _parameters["u"], float)
        check_type("hopping", _parameters["hopping"], float)
        check_type("on_site", _parameters["on_site"], float)
        check_type("k", _parameters["k"], float)
        check_type("u_p", _parameters["u_p"], float)
        check_type("hubbard", _parameters["hubbard"], bool)
        check_type("rhf", _parameters["rhf"], bool)
        check_type("pbc", _parameters["pbc"], bool)

    def print_result(self) -> None:
        """Print orbital energy information from diagonalization and HF calculations."""
        e_homo = None
        e_lumo = None
        e_tb = self.checkpoint["e_orb_tb"]
        nocc = self.occ_model.nacto[0]
        rhf = self.parameters.get("rhf")

        if rhf:
            e_hf = self.checkpoint["orb_a"]
            orbs = e_hf
            log(
                f"{'orb_index':>24s} {'Energy_hf [E_h]':>18s} {'Energy_hf [eV]':>14s}{'Energy_tb [E_h]':>18s} {'Energy_tb [eV]':>14s}"
            )

            for count, e_orbital in enumerate(orbs.energies):
                if count == orbs.get_homo_index():
                    e_homo = e_orbital
                    e_homo_tb = e_tb[count]
                    log(
                        f"\t\t{'HOMO':>4}\t{e_homo:> 18.7f}{e_orbital / electronvolt:> 14.3f}{e_tb[count]:> 18.7f}{e_tb[count] / electronvolt:> 14.3f}"
                    )
                elif count == orbs.get_lumo_index():
                    e_lumo = e_orbital
                    e_lumo_tb = e_tb[count]
                    log(
                        f"\t\t{'LUMO':>4}\t{e_lumo:> 18.7f}{e_orbital / electronvolt:> 14.3f}{e_tb[count]:> 18.7f}{e_tb[count] / electronvolt:> 14.3f}"
                    )
                else:
                    log(
                        f"\t\t{count + 1:>4} {'':>4}\t{e_orbital:> 10.7f}{e_orbital / electronvolt:> 14.3f}{e_tb[count]:> 18.7f}{e_tb[count] / electronvolt:> 14.3f}"
                    )

        else:
            log("warning: RHF orbital energies (orb_a) are not available.")
            log(
                f"{'orb_index':>24s} {'Energy_tb [E_h]':>18s} {'Energy_tb [eV]':>14s}"
            )
            for count, en in enumerate(e_tb):
                if count == nocc - 1:
                    e_homo = en
                    log(
                        f"\t\t{'HOMO':>4}\t{e_homo:> 18.7f}{en / electronvolt:> 14.3f}"
                    )
                elif count == nocc:
                    e_lumo = en

                    log(
                        f"\t\t{'LUMO':>4}\t{e_lumo:> 18.7f}{en / electronvolt:> 14.3f}"
                    )
                else:
                    log(
                        f"\t\t{count + 1:>4} {'':>4}\t{en:> 10.7f}{en / electronvolt:> 14.3f}"
                    )
        self.checkpoint.update("e_homo", e_homo)
        self.checkpoint.update("e_lumo", e_lumo)
        self.checkpoint.update("e_gap", e_lumo - e_homo)

        log.hline("-")
        # Calculate LUMO-HOMO gap if both HOMO and LUMO orbitals were found
        if e_homo is not None and e_lumo is not None:
            if rhf:
                lumo_homo_gap = e_lumo - e_homo
                lumo_homo_gap_tb = e_lumo_tb - e_homo_tb
                log(
                    f"{'LUMO-HOMO gap':>20} \t\t{lumo_homo_gap:> 10.7f}{lumo_homo_gap / electronvolt:> 14.3f}{lumo_homo_gap_tb:> 18.7f}{lumo_homo_gap_tb / electronvolt:> 14.3f}"
                )
                # Check if the LUMO-HOMO gap is negative and print a warning
                if lumo_homo_gap < 0:
                    log.warning("Warning: LUMO-HOMO gap is negative.")

            else:
                lumo_homo_gap = e_lumo - e_homo
                log(
                    f"{'LUMO-HOMO gap':>20} \t\t{lumo_homo_gap:> 10.7f}{lumo_homo_gap / electronvolt:> 14.3f}"
                )
                # Check if the LUMO-HOMO gap is negative and print a warning
                if lumo_homo_gap < 0:
                    log.warning("Warning: LUMO-HOMO gap is negative.")
        else:
            raise ValueError(
                "Unable to calculate LUMO-HOMO gap: HOMO or LUMO orbital not found."
            )

        log.hline()
        log.hline()

    def __call__(self, *args: Any, **kwargs: dict[str, Any]) -> Any:
        """
        Execute the entire process for modeling the Hamiltonian.
        This method orchestrates the following steps:
        1. Reads and validates input parameters using the `read_input` method.
        2. Computes the Hamiltonian (including one-body and optional two-body terms).
        3. Constructs overlap and adjacency matrices as needed.
        4. Diagonalizes the Hamiltonian to obtain orbital energies.
        5. Optionally performs restricted Hartree-Fock (RHF) diagonalization.
        6. Prints the results, including orbital energies and LUMO-HOMO gaps.

        **Positional Arguments**:
            *args: Additional arguments passed to the method.

        **Keyword Arguments**:
            - `parameters` (dict, optional): Model parameters, such as:
                * `u` (float): On-site Coulomb interaction (Hubbard).
                * `hopping` (float): Hopping parameter between sites.
                * `on_site` (float): On-site energy offset.
                * `add_hubbard` (bool): Whether to perform pCCD calculations.
                * `k` (float): Dielectric constant.
                * `u_p` (float): u/k.
            - Other options relevant to specific models.

        **Returns**:
            None
        """
        if log.do_medium:
            self.print_info(*args, **kwargs)
        # Compute the Hamiltonian (including one-body and optional two-body terms)
        self.read_input(*args, **kwargs)
        tb_ham = self.tight_binding_model()
        # Retrieve the RHF parameter to determine if RHF diagonalization is needed.
        rhf = self.parameters.get("rhf")
        self.diagonalization(tb_ham, rhf=rhf)
        # Print the results, including orbital energies and LUMO-HOMO gaps.
        if log.do_medium:
            self.print_result()

        return self.checkpoint()
