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
# 2022-06-10: embedding potential reader (P. Tecmer)
# 2025-03: Docstrings and type hints (Kacper Cieslak)

"""Embedding potential reader (.emb)"""

from pathlib import Path
from typing import Any

import numpy as np

from pybest.exceptions import MissingFileError

__all__ = ["load_embedding"]


def load_embedding(filename: str) -> dict[str, Any]:
    """Load an embedding potential from .emb file.

    Args:
        filename: The file to load the embedding potential from.

    Returns:
        dict[str, Any]: dict with ``n_points``, ``title`, ``charges``,
    ``coordinates``, and ``weights``.

    Raises:
        MissingFileError: File does not exist. Please Check whether the name of the file is correct.
        Exception: Number of point charges and lines is not equal.
    """
    if not Path(filename).exists():
        raise MissingFileError(
            f"'{filename}' doesn't exist.\n \
            Please check whether the name of the file is correct."
        )

    with open(filename, encoding="utf-8") as f:
        # read first line and interpret it as number of grid points
        n_points = int(f.readline())
        # read second line and interpret is as a comment/tittle
        title = f.readline().strip()
        # The next lines contain all information regarding point charges.
        lines = f.readlines()
        if len(lines) != n_points:
            raise Exception(
                f"{n_points} point charges mentioned, {len(lines)} lines found."
            )
        # allocate arrays for coordinates, weights, and charges
        coordinates = np.empty((n_points, 3), float)
        weights = np.empty(n_points, float)
        charges = np.empty(n_points, float)
        # go through grid point list and parse coords, weights, and charges
        for grid_point in range(n_points):
            x_pos, y_pos, z_pos, weight, charge = lines[grid_point].split()
            coordinates[grid_point, 0] = float(x_pos)
            coordinates[grid_point, 1] = float(y_pos)
            coordinates[grid_point, 2] = float(z_pos)
            weights[grid_point] = float(weight)
            charges[grid_point] = float(charge)

    return {
        "n_points": n_points,
        "title": title,
        "coordinates": coordinates,
        "weights": weights,
        "charges": charges,
        "filename": str(filename),
    }
