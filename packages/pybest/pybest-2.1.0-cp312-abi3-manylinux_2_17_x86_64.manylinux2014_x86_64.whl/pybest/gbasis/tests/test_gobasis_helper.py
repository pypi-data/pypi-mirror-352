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

from pybest.context import context
from pybest.gbasis.gobasis import get_gobasis
from pybest.gbasis.gobasis_helper import shell_int2str, shell_str2int
from pybest.iodata import IOData


def test_shell_str2int_cart():
    assert shell_str2int("s") == [0]
    assert shell_str2int("S") == [0]
    assert shell_str2int("Ss") == [0, 0]
    assert shell_str2int("SP") == [0, 1]
    assert shell_str2int("SDD") == [0, -2, -2]


def test_shell_str2int_pure():
    assert shell_str2int("s", True) == [0]
    assert shell_str2int("S", True) == [0]
    assert shell_str2int("Ss", True) == [0, 0]
    assert shell_str2int("SP", True) == [0, 1]
    assert shell_str2int("SDF", True) == [0, 2, 3]


def test_shell_int2str():
    assert shell_int2str(0) == "s"
    assert shell_int2str(1) == "p"
    assert shell_int2str(3) == "f"
    assert shell_int2str(4) == "g"
    assert shell_int2str(5) == "h"
    assert shell_int2str(6) == "i"


test_cases = [
    (
        "he",
        "STO-3G",
        {
            "alpha": [6.36242139, 1.15892300, 0.31364979],
            "contraction": [0.15432897, 0.53532814, 0.44463454],
            "shell2atom": np.array([0]),
            "nprim": np.array([3]),
            "shell_types": np.array([0]),
            "nbasis": 1,
        },
    ),
    (
        "h",
        "3-21G",
        {
            "alpha": [5.4471780, 0.8245470, 0.1831920],
            "contraction": [0.1562850, 0.9046910, 1.0000000],
            "shell2atom": np.array([0, 0]),
            "nprim": np.array([2, 1]),
            "shell_types": np.array([0, 0]),
            "nbasis": 2,
        },
    ),
    (
        "li",
        "3-21G",
        {
            "alpha": [
                36.8382000,
                5.4817200,
                1.1132700,
                0.5402050,
                0.1022550,
                0.5402050,
                0.1022550,
                0.0285650,
                0.0285650,
            ],
            "contraction": [
                0.0696686,
                0.3813460,
                0.6817020,
                -0.2631270,
                1.1433900,
                0.1615460,
                0.9156630,
                1.0000000,
                1.0000000,
            ],
            "shell2atom": np.array([0, 0, 0, 0, 0]),
            "nprim": np.array([3, 2, 2, 1, 1]),
            "shell_types": np.array([0, 0, 1, 0, 1]),
            "nbasis": 9,
        },
    ),
    (
        "water_element",
        "STO-3G",
        {
            "alpha": [
                3.42525091,
                0.62391373,
                0.16885540,
                130.7093200,
                23.8088610,
                6.4436083,
                5.0331513,
                1.1695961,
                0.3803890,
                5.0331513,
                1.1695961,
                0.3803890,
                3.42525091,
                0.62391373,
                0.16885540,
            ],
            "contraction": [
                0.15432897,
                0.53532814,
                0.44463454,
                0.15432897,
                0.53532814,
                0.44463454,
                -0.09996723,
                0.39951283,
                0.70011547,
                0.15591627,
                0.60768372,
                0.39195739,
                0.15432897,
                0.53532814,
                0.44463454,
            ],
            "shell2atom": np.array([0, 1, 1, 1, 2]),
            "nprim": np.array([3, 3, 3, 3, 3]),
            "shell_types": np.array([0, 0, 0, 1, 0]),
            "nbasis": 7,
        },
    ),
]


@pytest.mark.parametrize("mol, basis_name, expected", test_cases)
def test_go_basis_desc(mol, basis_name, expected):
    fn = context.get_fn(f"test/{mol}.xyz")
    mol = IOData.from_file(fn)
    basis = get_gobasis(f"{basis_name}", fn, print_basis=False)
    assert (basis.shell2atom == expected["shell2atom"]).all()
    assert (basis.nprim == expected["nprim"]).all()
    assert (basis.shell_types == expected["shell_types"]).all()
    np.testing.assert_almost_equal(basis.alpha, expected["alpha"])
    np.testing.assert_almost_equal(basis.contraction, expected["contraction"])
    assert basis.nbasis == expected["nbasis"]
