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
# 2022-06-10: Point charge reader (P. Tecmer)
# 2025-03: Docstrings and type hints (Kacper Cieslak)

"""External point charge file reader"""

from pathlib import Path

import numpy as np

from pybest.exceptions import MissingFileError

__all__ = ["load_charges"]


def load_charges(filename: str):
    """Load external point charges from a .pc file

    Args:
        filename: The file to load external point charges.

    Returns:
        dict: dictionary with ``n_charges``, ``title`,
    ``xyz coordinates``, ``charges``, and the ``filename``.

    Raises:
        MissingFileError: File does not exist. Please check whether the name of the file is correct.
        Exception: number of pouint charges does not equal lines found.
    """
    if not Path(filename).exists():
        raise MissingFileError(
            f"'{filename}' doesn't exist.\n \
            Please check whether the name of the file is correct."
        )

    with open(filename, encoding="utf-8") as cp_file:
        # read first line and interpret it as the number of charges
        n_charges = int(cp_file.readline())
        # read second line and interpret is as a comment/tittle
        title = cp_file.readline().strip()
        # The next lines contain all information regarding point charges.
        lines = cp_file.readlines()
        if len(lines) != n_charges:
            raise Exception(
                f"{n_charges} point charges mentioned, {len(lines)} lines found."
            )
        # allocate arrays for charges and coordinates
        coordinates = np.empty((n_charges, 3), float)
        charges = np.empty(n_charges, float)
        # go through charges list and parse coords and charges
        for charge_index in range(n_charges):
            x_pos, y_pos, z_pos, charge = lines[charge_index].split()
            # by default the Angstroms are used
            coordinates[charge_index, 0] = float(x_pos)
            coordinates[charge_index, 1] = float(y_pos)
            coordinates[charge_index, 2] = float(z_pos)
            charges[charge_index] = float(charge)

    return {
        "n_charges": n_charges,
        "title": title,
        "coordinates": coordinates,
        "charges": charges,
        "filename": str(filename),
    }
