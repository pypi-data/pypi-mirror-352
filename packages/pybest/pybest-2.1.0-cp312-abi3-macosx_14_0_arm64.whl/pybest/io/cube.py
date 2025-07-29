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
# 2025-03: Docstrings and type hints (Kacper Cieslak)
"""
Dump cube files. PyBEST supports to dump

    * orbitals (a Basis instance)
"""

import pathlib
from typing import Any

import numpy as np

from pybest.exceptions import ArgumentError
from pybest.log import log, timer


def dump_cube(filename: pathlib.Path, data: dict[str, Any]):
    """Write data to file using the cube format.

    The cube file contains the following records (per line):
        - job title
        - brief description of the file contents
        - number of atoms, coordinates of grid origin (bohr)
        - number of grid points n_1, step vector for first grid dimension
        - number of grid points n_2, step vector for second grid dimension number of grid points n_3, step vector for third grid dimension
        - atomic number, charge and coordinates; one such record for each atom
        - values at each grid point (n_1 * n_2 records of length n_3; inner
          most loop corresponds to z axis, outer most loop to x axis)

    Args:
        filename (str): The filename of the cube file, which is the output file for this routine.
        data (IOData): An IOData instance.
            Must contain:
                - ``orb_a`` (an Orbital instance)
                - ``basis`` (a Basis instance) either as separate attribute or stored in the ``occ_model`` attribute
                - ``indices_mos`` (a tuple containing the orbital indices to be printed)

            May contain:
                - ``orb_b``
                - ``origin`` (a tuple; the origin of the cube file)
                - ``step`` (a tuple; the step taken in each direction)
                - ``points`` (a tuple; the number of points in each direction; defaults to [80, 80, 80])

    Raises:
        ArgumentError: Orbitals orb_a are missing
        ArgumentError: Basis information basis is missing
        ArgumentError: List of orbitals to be printed are missing
    """
    if log.do_medium:
        log(" ")
        log("Dumping cube files")
        log(" ")
        log.hline("-")
    #
    # Check for required attributes
    #
    if not hasattr(data, "orb_a"):
        raise ArgumentError("Orbitals orb_a are missing")
    if not any(hasattr(data, attr) for attr in ["basis", "occ_model"]):
        raise ArgumentError("Basis information basis is missing")
    if not hasattr(data, "indices_mos"):
        raise ArgumentError("List of orbitals to be printed are missing")
    #
    # Check consistency in basis set; basis is taken either from basis
    # attribute or from occ_model
    if hasattr(data, "occ_model") and hasattr(data, "basis"):
        assert (
            data.occ_model.factory == data.basis
        ), "Different basis sets stored in IOData container"
    #
    # Store data in dictionary
    #
    cube_data = get_cube_data(data)
    #
    # Print all orbitals from list mos
    #
    # Get orbitals
    mos = [] if not hasattr(data, "indices_mos") else data.indices_mos
    for mo in mos:
        # adjust filename
        f_n_ = pathlib.Path(filename.stem + "_" + str(mo) + filename.suffix)
        # check for title, if not present, update
        if not hasattr(data, "title"):
            data.title = f"Orbital no {mo}"
        # print header (same for all cube files) with new title
        print_cube_header(f_n_, **cube_data)
        # print actual grip points
        dump_orbital_to_cube(f_n_, mo, **cube_data)
    # Done
    if log.do_medium:
        log(" ")
        log.hline("~")


def get_cube_data(data: dict[str, Any]) -> dict[str, Any]:
    """Get all data required to generate cube files.

    Args:
        data (dict[str, Any]): An IOData instance.

    Returns:
        Returns a dictionary of all data required to generate cube files:
            - origin (tuple): the origin of the cube file
            - step (tuple): the number of points in each direction. Defaults to [80, 80, 80]
            - points
            - data (dict[str, Any]): a IOData instance.
    """
    origin = get_cube_origin(data)
    points = [80, 80, 80] if not hasattr(data, "points") else data.points
    step = get_cube_step(data, origin, points)
    return {
        "origin": origin,
        "points": points,
        "step": step,
        "data": data,
    }


def get_cube_origin(data: dict[str, Any], shift: float = -3.0) -> list[float]:
    """Determine origin of grid based on molecular coordinates.

    If not provided, an origin is selected:
        * determine the most negative coordinates
        * extend these coordinates by a shift (default 3 bohr)

    Args:
        data (IOData): an IOData instance.
        shift (float): a negative number to shift the origin.

    Returns:
        list[float]: the origin of the grid
    """
    if hasattr(data, "origin"):
        return data.origin
    origin = [0.0, 0.0, 0.0]
    try:
        basis = data.basis
    except AttributeError:
        basis = data.occ_model.factory
    # adjust origin to the most negative coordinates
    for coord in basis.coordinates:
        origin = [o if o < c else c for c, o in zip(coord, origin)]
    # round final result to 6 decimal places
    return [round(o + shift, 6) for o in origin]


def get_cube_step(
    data: dict[str, Any],
    origin: list[float],
    points: list[int],
    shift: float = 3.0,
) -> list[float]:
    """Determine step size in each grid dimension.

    If not provided, a step size will be provided
    based on the outer-most coordinates plus a shift (defaults to 2 bohr).

    Args:
        data (dict[str, Any]): an IOData instance
        origin (list[float]): the origin of the grid
        points (list[int]): number of grid points along each dimension
        shift (float): a number to shift the boundary of the cube

    Returns:
        list[float]: step size of each grid dimension
    """
    if hasattr(data, "step"):
        return data.step
    max_coord = origin
    try:
        basis = data.basis
    except AttributeError:
        basis = data.occ_model.factory
    for coord in basis.coordinates:
        max_coord = [c if c > o else o for c, o in zip(coord, max_coord)]
    # shift coordinates
    max_coord = [o + shift for o in max_coord]
    # return step size rounded to 6 decimal places
    return [
        round((p - m) / point, 6)
        for p, m, point in zip(max_coord, origin, points)
    ]


def print_cube_header(
    filename: pathlib.Path, **cube_data: dict[str, Any]
) -> None:
    """Prints the header of a cube file

    Args:
        filename (str): pathlib.Path instance of a filename

    Keyword Args:
        data (dict[str, Any]): an IOData instance
        origin (list[float]): the origin of the grid
        step (list[float]): step size of each grid dimension
        points (list[int]): number of grid points along each dimension

    Raises:
        ValueError: Origin, points, or step not provided. Check the cube_data dictionary
    """
    data = cube_data.get("data")
    origin = cube_data.get("origin")
    points = cube_data.get("points")
    step = cube_data.get("step")

    if origin is None or points is None or step is None:
        raise ValueError(
            "Origin, points, or step not provided. Check the cube_data dictionary"
        )
    try:
        basis = data.basis
    except AttributeError:
        basis = data.occ_model.factory
    title = "" if not hasattr(data, "title") else data.title
    with open(filename, "w", encoding="utf8") as f:
        #
        # Job title
        #
        print("Cube file generated by PyBEST", file=f)
        #
        # File title
        #
        print(title, file=f)
        #
        # Number of atoms, coordinates of origin (bohr)
        #
        print(
            f"{len(basis.atom):>5} {origin[0]:> 12.6f} {origin[1]:> 12.6f} {origin[2]:> 12.6f}",
            file=f,
        )
        #
        # Number f grid points
        # n_1, step vector for first grid dimension
        print(
            f"{points[0]:>5} {step[0]:> 12.6f} {0.0:> 12.6f} {0.0:> 12.6f}",
            file=f,
        )
        # n_2, step vector for second grid dimension
        print(
            f"{points[1]:>5} {0.0:> 12.6f} {step[1]:> 12.6f} {0.0:> 12.6f}",
            file=f,
        )
        # n_3, step vector for third grid dimension
        print(
            f"{points[2]:>5} {0.0:> 12.6f} {0.0:> 12.6f} {step[2]:> 12.6f}",
            file=f,
        )
        #
        # Atomic number, charge and coordinates; one such record for each atom
        #
        for i, atom in enumerate(basis.atom):
            x, y, z = basis.coordinates[i]
            print(
                f"{atom:>5} {atom:> 12.6f} {x:> 12.6f} {y:> 12.6f} {z:> 12.6f}",
                file=f,
            )


@timer.with_section("cube (orbital)")
def dump_orbital_to_cube(
    filename: pathlib.Path, mo: int, **cube_data: dict[str, Any]
) -> None:
    """Dumps one orbital to a cube file with the name {filename} (contains the suffix .cube).

    This function only calculates the values at each grid
    point and appends them to the file {filename}.
    Note that no new file is created.

    Args:
        filename (str): pathlib.Path instance of a filename
        mo (int): the number of the MO to be printed (Fortran indexing is assumed)

    Keyword Args:
        data (dict[str, Any]): an IOData instance
        origin (list[float]): the origin of the grid
        step (list[float]): step size of each grid dimension
        points (list[int]): number of grid points along each dimension

    Raises:
        ValueError: Origin, points, or step not provided. Check the cube_data dictionary
    """
    data = cube_data.get("data")
    origin = cube_data.get("origin")
    points = cube_data.get("points")
    step = cube_data.get("step")

    if origin is None or points is None or step is None:
        raise ValueError(
            "Origin, points, or step not provided. Check the cube_data dictionary"
        )
    try:
        basis = data.basis
    except AttributeError:
        basis = data.occ_model.factory
    if log.do_medium:
        log(" ")
        log(f"Dumping orbital no {mo} to file {filename}")
        log(" ")
        log(f"Origin: {origin}")
        log(f"Step:   {step}")
        log(f"Points: {points}")
        log.hline(".")
    orb = data.orb_a

    x = np.arange(origin[0], points[0] * step[0] + origin[0], step[0])
    y = np.arange(origin[1], points[1] * step[1] + origin[1], step[1])
    z = np.arange(origin[2], points[2] * step[2] + origin[2], step[2])
    basis.dump_cube_orbital(
        str(filename.resolve()), orb.coeffs[:, mo - 1], x, y, z
    )
