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

# 2024: Original version written by Katharina Boguslawski

"""Fixtures for tests"""

import numpy as np
import pytest

from pybest.linalg import DenseOneIndex

n_dim = [5, 10]


@pytest.fixture(params=n_dim)
def unit_vectors(request):
    """Generate a list of unit vectors, with len(vectors) = dimension-1"""
    dimension = request.param + 1
    vectors = []
    energies = []

    # Create dimension-1 vectors of shape (0,...,1,...,0)
    for i in range(request.param):
        vector = DenseOneIndex(dimension)
        vector.array[i] = 1
        vectors.append(vector)
        # insert energies in reverse order
        energies.insert(0, i)

    # Return vectors
    return vectors, dimension, energies


@pytest.fixture(params=[1, 3])
def random_vectors(request):
    """Generate a list of random vectors - only first vector is normalized"""
    vector_random = np.random.normal(0, 1, (10,))
    # Normalize only first one
    vector_random /= np.linalg.norm(vector_random)
    # Add more random vectors
    for _ in range(request.param - 1):
        vector_random = np.vstack(
            (vector_random, np.random.normal(0, 1, (10,)))
        )
    # Return transposed vectors (column-wise)
    return vector_random.T
