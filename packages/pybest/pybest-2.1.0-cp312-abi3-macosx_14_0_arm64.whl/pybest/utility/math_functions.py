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
#
# 2024-04-24: created by Katharina Boguslawski (taken from old utils.py)

"""Utility functions related to math operations"""

from contextlib import contextmanager

import numpy as np

__all__ = [
    "numpy_seed",
]


@contextmanager
def numpy_seed(seed=1):
    """Temporarily set NumPy's random seed to a given number.

    Parameters
    ----------
    seed : int
           The seed for NumPy's random number generator.
    """
    state = np.random.get_state()
    np.random.seed(seed)
    yield None
    np.random.set_state(state)
