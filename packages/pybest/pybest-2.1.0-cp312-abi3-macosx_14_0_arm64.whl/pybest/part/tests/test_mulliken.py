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

from pybest import get_mulliken_operators
from pybest.context import context
from pybest.part.tests.common import prepare_basis

test_mulliken = [
    ("cc-pvdz", "h2o"),
]


@pytest.mark.parametrize("basis_name, mol", test_mulliken)
def test_mulliken_charges(basis_name, mol):
    basis = prepare_basis(basis_name, f"test/{mol}.xyz")

    mulliken = get_mulliken_operators(basis)

    # reference data
    fn_mulliken = context.get_fn(f"test/mulliken_{mol}_{basis_name}")
    mulliken_ref = []
    for idx in range(basis.ncenter):
        fn_mulliken_ = f"{fn_mulliken}_{idx}.txt"
        mulliken_ref.append(
            np.fromfile(fn_mulliken_, sep=",").reshape(
                basis.nbasis, basis.nbasis
            )
        )

    for idx in range(basis.ncenter):
        assert np.allclose(mulliken[idx].array, mulliken_ref[idx])
