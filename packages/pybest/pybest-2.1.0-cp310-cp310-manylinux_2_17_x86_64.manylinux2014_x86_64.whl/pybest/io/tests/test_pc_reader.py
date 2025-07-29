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

from pybest import context
from pybest.io.external_charges import load_charges

ref_coords = np.array(
    [
        [1.00000000, 0.00000000, 0.00000000],
        [-1.00000000, 0.00000000, 0.00000000],
        [0.00000000, 1.00000000, 0.00000000],
        [0.00000000, -1.00000000, 0.00000000],
        [0.00000000, 0.00000000, 1.00000000],
        [0.00000000, 0.00000000, -1.00000000],
    ]
)

ref_charges = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0])

data_point_charges = [
    (
        "water_pc.pc",
        {"n_charges": 6, "charges": ref_charges, "coord": ref_coords},
    ),
]


def check_point_charges(point_charges_source, expected):
    """Reference data taken from test/point_charges_source."""
    data = load_charges(point_charges_source)
    n_charges = data["n_charges"]
    charges = data["charges"]
    coord = data["coordinates"]

    assert n_charges == expected["n_charges"]
    assert np.allclose(coord, expected["coord"])
    assert np.allclose(charges, expected["charges"])


@pytest.mark.parametrize("point_charges_source,expected", data_point_charges)
def test_load_charges(point_charges_source, expected):
    """Check performance of load_charges."""
    point_charge_source = context.get_fn(f"test/{point_charges_source}")

    check_point_charges(point_charge_source, expected)
