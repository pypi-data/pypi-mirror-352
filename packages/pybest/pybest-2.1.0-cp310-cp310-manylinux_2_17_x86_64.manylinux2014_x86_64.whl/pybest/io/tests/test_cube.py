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


import numpy as np
import pytest

from pybest import context, filemanager
from pybest.exceptions import ArgumentError
from pybest.gbasis import get_gobasis
from pybest.io.cube import (
    dump_cube,
    dump_orbital_to_cube,
    get_cube_data,
    get_cube_origin,
    get_cube_step,
)
from pybest.io.tests.common import get_orbital_data
from pybest.iodata import IOData

test_cube_fail = [
    (IOData(), ArgumentError),  # missing any data
    (
        IOData(**{"basis": None, "indices_mos": None}),
        ArgumentError,
    ),  # missing orb_a attribute in IOData
    (
        IOData(**{"orb_a": None, "indices_mos": None}),
        ArgumentError,
    ),  # missing basis attribute in IOData
    (IOData(**{"orb_a": None, "basis": None}), ArgumentError),  # mos
]


@pytest.mark.parametrize("data,error", test_cube_fail)
def test_cube_arguments(data, error):
    """Test if input IOData container has proper arguments. Test should fail.
    It does not matter what type the arguments have.
    """
    with pytest.raises(error):
        dump_cube("some_name", data)


test_origin = [
    [0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0],
    [0.0, 0.0, -1.0],
    [-1.0, -1.0, -1.0],
]

test_step = [
    [0.1, 0.1, 0.1],
    [0.2, 0.1, 0.5],
    [0.3, 0.2, 0.2],
]

test_points = [
    [10, 10, 10],
    [50, 50, 50],
]


@pytest.mark.parametrize("origin", test_origin)
@pytest.mark.parametrize("step", test_step)
@pytest.mark.parametrize("points", test_points)
def test_get_cube_data(origin, step, points):
    """Test whether data is assigned properly from input IOData container."""
    data = IOData()
    data.origin = origin
    data.step = step
    data.points = points
    data.data = data
    result = get_cube_data(data)

    for key, value in result.items():
        assert value == getattr(data, key)


test_origin_data = [
    # new coordinates, shift, expected origin
    (np.array([[0, 0, 0]]), (), [-3, -3, -3]),
    (np.array([[-1, 0, -2]]), (), [-4, -3, -5]),
    (np.array([[-1, 0, -2], [-4, -3, 8]]), (), [-7, -6, -5]),
    (np.array([[-1, 0, -2], [4, 3, 8]]), (), [-4, -3, -5]),
    (np.array([[0, 0, 0]]), (-1,), [-1, -1, -1]),
    (np.array([[0, 0, 0]]), (0.5,), [0.5, 0.5, 0.5]),
    (np.array([[-1, 0, -2], [4, 3, 8]]), (-1,), [-2, -1, -3]),
]


@pytest.mark.parametrize("coord,args,expected", test_origin_data)
def test_get_cube_origin(coord, args, expected):
    """Test whether data is assigned properly from input IOData container."""
    # Create dummy molecule
    fn = context.get_fn("test/h2.xyz")
    data = IOData(**{"basis": get_gobasis("cc-pvdz", fn, print_basis=False)})
    # overwrite coordinates (we can do that as we only access the coordinates
    # attribute)
    data.basis.coordinates = coord

    assert get_cube_origin(data, *args) == expected


test_step_data = [
    # new coordinates, shift, origin, number of points, expected step length
    (
        np.array([[0, 0, 0]]),
        (),
        [-2, -2, -2],
        [30, 10, 20],
        [0.166667, 0.5, 0.25],
    ),
    (
        np.array([[-1, 0, -2]]),
        (),
        [-3, -2, -4],
        [30, 10, 20],
        [0.166667, 0.5, 0.25],
    ),
    (
        np.array([[-1, 0, -2], [-4, -3, 8]]),
        (),
        [-6, -5, -4],
        [30, 10, 20],
        [0.266667, 0.8, 0.75],
    ),
    (
        np.array([[-1, 0, -2], [4, 3, 8]]),
        (),
        [-3, -2, -4],
        [30, 10, 20],
        [0.333333, 0.8, 0.75],
    ),
    (
        np.array([[0, 0, 0]]),
        (-1,),
        [-1, -1, -1],
        [30, 10, 20],
        [0.0, 0.0, 0.0],
    ),
    (
        np.array([[0, 0, 0]]),
        (3,),
        [-1, -1, -1],
        [30, 10, 20],
        [0.133333, 0.4, 0.2],
    ),
    (
        np.array([[0, 0, 0]]),
        (0.5,),
        [0.5, 0.5, 0.5],
        [30, 10, 20],
        [0.016667, 0.05, 0.025],
    ),
    (
        np.array([[-1, 0, -2], [4, 3, 8]]),
        (-1,),
        [-2, -1, -3],
        [30, 10, 20],
        [0.166667, 0.3, 0.5],
    ),
]


@pytest.mark.parametrize("coord,args,origin,points,expected", test_step_data)
def test_get_cube_step(coord, args, origin, points, expected):
    """Test whether data is assigned properly from input IOData container."""
    # Create dummy molecule
    fn = context.get_fn("test/h2.xyz")
    data = IOData(**{"basis": get_gobasis("cc-pvdz", fn, print_basis=False)})
    # overwrite coordinates (we can do that as we only access the coordinates
    # attribute)
    data.basis.coordinates = coord

    assert get_cube_step(data, origin, points, *args) == expected


h2_data = get_orbital_data("h2_cube", "h2_orb_cube", "cube-test.g94")

test_orbital_to_cube = [
    (
        {
            "data": h2_data,
            "origin": [-2.107779, -2.107779, -2.598632],
            "step": [0.057747, 0.057747, 0.057747],
            "points": [1, 1, 1],
        },
        1,
        [0.006520139],
    ),
    (
        {
            "data": h2_data,
            "origin": [-2.107779, -2.107779, -2.598632],
            "step": [0.057747, 0.057747, 0.057747],
            "points": [1, 1, 1],
        },
        7,
        [-1.508285e-02],
    ),
    (
        {
            "data": h2_data,
            "origin": [-2.107779, -2.107779, -2.598632],
            "step": [0.057747, 0.057747, 0.057747],
            "points": [1, 1, 1],
        },
        30,
        [1.633583e-02],
    ),
    (
        {
            "data": h2_data,
            "origin": [-2.107779, -2.107779, -2.598632],
            "step": [0.057747, 0.057747, 0.057747],
            "points": [1, 1, 1],
        },
        116,
        [6.416415e-03],
    ),
    (
        {
            "data": h2_data,
            "origin": [-2.107779, -2.107779, -2.598632],
            "step": [0.057747, 0.057747, 0.057747],
            "points": [1, 1, 2],
        },
        1,
        [6.520139e-03, 6.783344e-03],
    ),
    (
        {
            "data": h2_data,
            "origin": [-2.107779, -2.107779, -2.598632],
            "step": [0.057747, 0.057747, 0.057747],
            "points": [1, 2, 1],
        },
        1,
        [6.520139e-03, 6.730278e-03],
    ),
    (
        {
            "data": h2_data,
            "origin": [-2.107779, -2.107779, -2.598632],
            "step": [0.057747, 0.057747, 0.057747],
            "points": [2, 1, 1],
        },
        1,
        [6.520139e-03, 6.730278e-03],
    ),
]


@pytest.mark.parametrize("cube_data,mo,expected", test_orbital_to_cube)
def test_dump_orbital_to_cube(cube_data, mo, expected):
    """Test evaluation of grid points"""
    # first dump points to file
    dump_orbital_to_cube(filemanager.temp_path("tmp.cube"), mo, **cube_data)
    # read data from file and compare
    result = []
    with open(filemanager.temp_path("tmp.cube"), encoding="utf8") as f:
        for line in f:
            numbers = line.split()
            for number in numbers:
                result.append(float(number))
    assert result == expected
