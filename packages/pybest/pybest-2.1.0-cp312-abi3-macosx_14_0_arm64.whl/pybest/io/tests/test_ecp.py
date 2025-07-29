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
from pybest.exceptions import ArgumentError, MissingFileError
from pybest.io.ecp import parse_ecp
from pybest.iodata import IOData


def test_file_exists_exception():
    """Tests file missing detection. Should raise an error"""
    with pytest.raises(MissingFileError):
        IOData.from_file(
            context.get_fn("test/ECP60MDERROR-test.g94"), ecp_symbol="U"
        )


def test_element_in_file_exception():
    """Tests element missing detection. Should raise an error"""
    with pytest.raises(ArgumentError):
        IOData.from_file(
            context.get_fn("test/ECP60MDF-test.g94"), ecp_symbol="Be"
        )


def test_can_read_ecp_from_g94(atom_data):
    """Tests connection with IOData and if parser works correctly"""
    data = IOData.from_file(
        context.get_fn(atom_data["filepath"]),
        ecp_symbol=atom_data["ecp_symbol"],
    )

    assert data.core_electrons == atom_data["core_electrons"]
    assert data.max_angular_momentum == atom_data["max_angular_momentum"]
    for idx, shell in enumerate(atom_data["shells"]):
        np.testing.assert_allclose(shell, data.ecp_shells[idx])


def test_can_read_ecp_from_g94_directly(atom_data):
    """Directly tests if parser works correctly"""
    data = parse_ecp(
        context.get_fn(atom_data["filepath"]),
        atom_data["ecp_symbol"],
    )

    assert data["core_electrons"] == atom_data["core_electrons"]
    assert data["max_angular_momentum"] == atom_data["max_angular_momentum"]
    for idx, shell in enumerate(atom_data["shells"]):
        np.testing.assert_allclose(shell, data["ecp_shells"][idx])
