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

import pybest.gbasis.dense_ints as ints_module
import pybest.gbasis.gobasis as basis_module
from pybest import context

# output of examples/rhf_water_static_embedding.py
expected_embedding = np.array(
    [
        [
            1.23936207e-38,
            1.49164797e-22,
            -2.32708954e-31,
            5.72690419e-30,
            1.52776307e-22,
            1.87052590e-21,
            1.87052581e-21,
        ],
        [
            1.49164797e-22,
            9.40915809e-06,
            -4.96803138e-14,
            3.39355067e-13,
            9.59510589e-06,
            1.64464637e-04,
            1.64464630e-04,
        ],
        [
            -2.32708954e-31,
            -4.96803137e-14,
            3.94310687e-07,
            -2.28719839e-14,
            -5.24391514e-14,
            -1.23630454e-12,
            -6.96735822e-13,
        ],
        [
            5.72690420e-30,
            3.39355065e-13,
            -2.28719838e-14,
            1.84090007e-05,
            3.51560435e-13,
            2.14641332e-04,
            -2.14641321e-04,
        ],
        [
            1.52776307e-22,
            9.59510589e-06,
            -5.24391514e-14,
            3.51560435e-13,
            1.01046670e-05,
            1.69720760e-04,
            1.69720752e-04,
        ],
        [
            1.87052590e-21,
            1.64464637e-04,
            -1.23630454e-12,
            2.14641332e-04,
            1.69720760e-04,
            6.01682460e-03,
            4.72513472e-04,
        ],
        [
            1.87052581e-21,
            1.64464630e-04,
            -6.96735824e-13,
            -2.14641321e-04,
            1.69720752e-04,
            4.72513472e-04,
            6.01682433e-03,
        ],
    ]
)


def test_can_compute_embedding():
    """Smoke test to check whether C-extension for embedding still works"""
    coordinates_xyz = context.get_fn("test/water_emb.xyz")
    embedding_pot = context.get_fn("test/water_emb.emb")
    basis = basis_module.get_gobasis("sto-6g", coordinates_xyz)
    embedding_pot = ints_module.get_embedding(embedding_pot)
    emb = ints_module.compute_static_embedding(basis, embedding_pot)
    np.testing.assert_allclose(expected_embedding, emb.array)
