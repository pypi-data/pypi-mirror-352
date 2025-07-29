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

from typing import Any

import numpy as np

from pybest.exceptions import ArgumentError
from pybest.featuredlists import SupportedAtomsPhysicalHam

from .xyz import load_xyz


def check_supported_atoms(
    supported_atoms: tuple[str, ...], xyz_file: str, unit_angstrom: bool = True
) -> dict[str, Any]:
    """
     Check atoms in an xyz file against supported atoms and return relevant details.

    Args:
        supported_atoms (tuple[str, ...]): Supported atom symbols.
        xyz_file (str): Path to the XYZ file.
        unit_angstrom (bool, optional): If True, coordinates are in Angstroms; otherwise, atomic units. Defaults to True.

    Returns:
        dict[str, Any]: Dictionary with:
            - 'symbols': Atom symbols in the file.
            - 'natoms': number of total atoms.
            - 'title': name of the xyz file.
            - 'supported_coordinates':coordinates of all atoms contained supported and unsupported atoms; taken from the SupportedAtomsPhysicalHam list (featuredlists.py).
    """
    if not xyz_file:
        return {
            "symbols": [],
            "natoms": 0,
            "title": "No file provided",
            "supported_coordinates": [],
            "coordinates": [],
        }
    data = load_xyz(xyz_file, unit_angstrom=unit_angstrom)
    coordinates = np.array(data.get("coordinates", []))
    atoms = data.get("atom", [])
    title = data.get("title", "No title provided")

    # Get total atoms count
    total_atoms = len(atoms)

    # Select model supported atoms (e.g., Hückel)
    # Check SupportedAtomsPhysicalHam for currently supported list of atoms.
    valid_atoms = [atom for atom in atoms if atom in supported_atoms]
    coord_sup_atoms = [
        coordinates[i]
        for i, atom in enumerate(atoms)
        if atom in supported_atoms
    ]
    valid_atom_count = len(valid_atoms)

    # Log a warning if no valid atoms are found
    if valid_atom_count <= 0:
        raise ArgumentError(
            f"Warning: No valid supported atoms in {title} structure."
        )
    output = {
        "symbols": valid_atoms,
        "natoms": total_atoms,
        "title": title,
        "supported_coordinates": coord_sup_atoms,
        "coordinates": coordinates,
    }

    return output


def check_physical_ham_coordinates(
    xyz_file: str, unit_angstrom: bool = True
) -> dict[str, Any]:
    """
    Checks coordinates in an xyz file for atoms specific to the Physical Hamiltonian model.


    Args:
        xyz_file (str): Path to the xyz file.
        unit_angstrom (bool, optional): If True, coordinates are in Angstroms; otherwise, atomic units. Defaults to True.

    Returns:
        dict[str, Any]: Dictionary with details about Physical Model Hamiltonian supported atoms and their coordinates.
    """
    supported_atoms = SupportedAtomsPhysicalHam
    return check_supported_atoms(supported_atoms, xyz_file, unit_angstrom)
