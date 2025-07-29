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
# This module has been written and updated by Zahra Karimi in 03/2025 (see CHANGELOG).

import pytest

from pybest.context import context
from pybest.linalg import DenseLinalgFactory
from pybest.modelhamiltonians import PPP, Hubbard, Huckel
from pybest.occ_model import AufbauOccModel
from pybest.units import electronvolt

test_data = [
    (
        Huckel,
        "c28",
        28,
        {"on_site": 0.0, "hopping": -2.6, "rhf": True},
        {"e_tot": -104.9558},
    ),
    (
        Hubbard,
        None,
        28,
        {"on_site": 0.0, "hopping": -2.6, "u": 1.0, "rhf": True},
        {"e_tot": -83.849221},
    ),
    (
        PPP,
        "c28",
        28,
        {
            "on_site": 0.0,
            "hopping": -2.4 * electronvolt,
            "u": 8.0 * electronvolt,
            "k": 2.0,
            "hubbard": False,
            "rhf": True,
        },
        {"e_tot": -3.5603},
    ),
]


@pytest.mark.parametrize("cls,xyz_file, nel, parameters, expected", test_data)
def test_e_tot_model_hamiltonian(cls, xyz_file, nel, parameters, expected):
    """Test Model Hamiltonians with covalent radius-based adjacency matrix."""

    lf = DenseLinalgFactory(nel)
    occ_model = AufbauOccModel(lf, nel=nel)

    if xyz_file:
        fn_xyz = context.get_fn(f"test/{xyz_file}.xyz")
        modelham = cls(lf, occ_model, xyz_file=fn_xyz)
    else:
        modelham = cls(lf, occ_model)

    result = modelham(parameters=parameters)
    assert abs(result.e_tot - expected["e_tot"]) < 1e-4
