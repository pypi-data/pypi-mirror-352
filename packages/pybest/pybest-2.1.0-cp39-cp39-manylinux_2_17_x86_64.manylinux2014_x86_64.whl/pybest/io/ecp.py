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
# Detailed changes:
# 2023-07-17: parser creation for .g94 ecp files (K. Cieślak)
"""ECP file format"""

from itertools import chain
from pathlib import Path
from re import search
from typing import Any

import numpy as np

from pybest.exceptions import ArgumentError, MissingFileError


def parse_ecp(filename: str, chemical_symbol: str) -> dict[str, Any]:
    """Parse pseudopotential for an atom from a .g94 file.

    Args:
        filename: A pseudopotential file in a .94 standard
        chemical_symbol: The chemical symbol of an element to lead pseudopotentials of

    Returns:
        dict[str, Any]:
            core_electrons (int): Ecp core electrons

            max_angular_momentum (int): Maximum angular momentum shell

            ecp_shells (dict): Dictionary with ``l:array of arrays containing primitive Gaussians``,
                where ``l`` is an angular momentum of a shell

    Raises:
        MissingFileError: Provided file doesn't exist. Please, check whether the name of the file is correct.
        ArgumentError: Element not present in the file.
    """
    if not Path(filename).exists():
        raise MissingFileError(
            f"'{filename}' doesn't exist.\n \
            Please, check whether the name of the file is correct."
        )

    with open(filename, encoding="utf-8") as input_file:
        for line in input_file:
            if search(rf"^{chemical_symbol} ", line):
                break
        else:
            raise ArgumentError(
                f"'{chemical_symbol}' not present in the '{filename.name}' file."
            )
        ecp_data = next(input_file).strip().split(" ")
        max_angular_momentum = int(ecp_data[1])
        core_electrons = int(ecp_data[2])

        ecp_shells = {}

        for i in chain([max_angular_momentum], range(max_angular_momentum)):
            # skip shell identifier
            next(input_file)
            # number of primitive Gaussians for {i} shell
            number_of_primitive_gaussians = int(next(input_file).strip())
            # an array of arrays with {number_of_primitive_gaussians} primitive Gaussians for {i} shell
            # one primitive Gaussian is composed of (power of r, Gaussian exponent, coefficient)
            pgs = np.array(
                [
                    next(input_file).strip().split(" ")
                    for _ in range(number_of_primitive_gaussians)
                ],
                dtype=np.double,
            )
            ecp_shells[i] = pgs
    return {
        "core_electrons": core_electrons,
        "max_angular_momentum": max_angular_momentum,
        "ecp_shells": ecp_shells,
    }
