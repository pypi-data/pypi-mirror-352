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
# Detailed changes:
# 2020-07-01: Update to PyBEST standard, including naming convention
# 2020-07-01: Dump coordinates of active fragment
# 2025-02-27: Variable name unification and type hints (Paweł Tecmer, Dariusz Kędziera)

"""XYZ file format"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import numpy as np

from pybest.units import angstrom

__all__ = ["dump_xyz", "load_xyz", "load_xyz_plain"]


def load_xyz(filename: str, unit_angstrom: bool = False) -> dict[str, Any]:
    """Load a molecular geometry from a .xyz file.

    Args:
        filename (str): the file to load the geometry from
        unit_angstrom (bool, optional): the unit of length. Defaults to False.

    Returns:
        tuple[str, float, int, str]: dictionary with ``title`, ``coordinates`` and ``numbers`
    """
    with open(filename) as f:
        natoms = int(f.readline())
        title = f.readline().strip()
        coordinates = np.empty((natoms, 3), float)
        atoms = np.empty(natoms, dtype=object)
        for i in range(natoms):
            words = f.readline().split()
            atoms[i] = words[0]
            scale = angstrom
            if unit_angstrom:
                scale = 1.0
            coordinates[i, 0] = float(words[1]) * scale
            coordinates[i, 1] = float(words[2]) * scale
            coordinates[i, 2] = float(words[3]) * scale
    return {
        "title": title,
        "coordinates": coordinates,
        "atom": atoms,
        "filename": str(filename),
    }


def load_xyz_plain(
    geo_str: str, unit_angstrom: bool = False
) -> dict[str, Any]:
    """Load a plain molecular geometry from a .xyz file. The file does not
    include the first two lines presents in standard xyz file.

     Args:
        geo_str (str): the file to load the plain geometry from
        unit_angstrom (bool, optional): the unit of length. Defaults to False.

    Returns:
       tuple[str, float, int, str]: dictionary with ``title`, ``coordinates`` and ``numbers`
    """
    geo_lines = geo_str.split("\n")
    natoms = int(geo_lines[0])
    title = geo_lines[1].strip()
    coordinates = np.empty((natoms, 3), float)
    atoms = np.empty(natoms, dtype=object)
    for i in range(natoms):
        words = geo_lines[2 + i].split()
        atoms[i] = words[0]
        scale = angstrom
        if unit_angstrom:
            scale = 1.0
        coordinates[i, 0] = float(words[1]) * scale
        coordinates[i, 1] = float(words[2]) * scale
        coordinates[i, 2] = float(words[3]) * scale
    return {"title": title, "coordinates": coordinates, "atom": atoms}


def dump_xyz(
    filename: str,
    data: dict[str, Any],
    unit_angstrom: bool = False,
    fragment: str | None = None,
) -> None:
    """Write an ``.xyz`` file.

    Args:
        filename (str): The name of the file to be written. This usually the extension
         ".xyz".
        data (dict[str, Any]): An IOData instance. Must contain ``coordinates`` and ``numbers``.
         May contain ``title``
        unit_angstrom (bool, optional): the unit of length. Defaults to False.
        fragment (str, optional): fragment of an xyz file. Defaults to None.

    Raises:
        ValueError: fragment is larger than the whole structure
    """
    # Convert dictionary to contain attributes (as IOData instance).
    # We cannot import IOData due to circular imports
    if isinstance(data, dict):
        data = SimpleNamespace(**data)
    natom = data.natom
    if fragment is not None:
        if data.natom <= max(fragment):
            raise ValueError(
                f"Fragment index {max(fragment)} larger than total number of "
                f"atoms {data.natom}"
            )
        natom = len(fragment)
    coordinates = data.coordinates
    with open(filename, "w") as f:
        print(natom, file=f)
        print(getattr(data, "title", "Created with PyBEST"), file=f)
        for i in range(data.natom):
            scale = 1 / angstrom
            if unit_angstrom:
                scale = 1.0
            n = data.atom[i]
            x, y, z = coordinates[i] * scale
            if fragment is None or i in fragment:
                print(f"{n:2} {x:15.10f} {y:15.10f} {z:15.10f}", file=f)
