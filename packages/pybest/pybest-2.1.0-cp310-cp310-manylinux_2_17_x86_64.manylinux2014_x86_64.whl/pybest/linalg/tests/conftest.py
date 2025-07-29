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
import pytest

from pybest.linalg import (
    DenseFourIndex,
    DenseOneIndex,
    DenseThreeIndex,
    DenseTwoIndex,
)


#
# Fixtures for testing NIndex objects
#
@pytest.fixture(
    params=[
        ((10,)),
        ((10, 10)),
        ((10, 10, 10)),
        ((10, 10, 10, 10)),
    ]
)
def dense_object(request):
    """Create some DenseIndex object of shape `dim` and with label `label`"""
    dim = request.param
    if len(dim) == 1:
        dense_array = DenseOneIndex(*dim)
    elif len(dim) == 2:
        dense_array = DenseTwoIndex(*dim)
    elif len(dim) == 3:
        dense_array = DenseThreeIndex(*dim)
    elif len(dim) == 4:
        dense_array = DenseFourIndex(*dim)
    dense_array.randomize()
    return dense_array
