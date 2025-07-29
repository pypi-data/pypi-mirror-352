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

from pybest.solvers.linear_equations import find_1d_root, solve_safe


def test_find_1d_root():
    # Only consider cases where the derivative of the function at the root is
    # at least 1.0. (See 'this is why'.)
    cases = [
        (-0.5, 0.1, np.sin, 0.0),
        (-10.0, 10.0, (lambda x: 2 * (x - 5)), 5.0),
        (-1.0, 2.0, (lambda x: np.exp(x) - 1), 0.0),
        (-1.0, 2.0, (lambda x: np.exp(x) - 2), np.log(2.0)),
        (0.0, 3.0, np.cos, np.pi / 2),
    ]
    eps = 1e-5
    for x0, x2, fn, solution in cases:
        x1, y1 = find_1d_root(fn, (x0, fn(x0)), (x2, fn(x2)), eps)
        assert abs(y1) < eps
        assert abs(x1 - solution) < eps  # <--- this is why


def test_solve_safe():
    a = np.diag([1.0, 2.0, 1.0])
    b = np.array([2.0, 4.0, 1.0])
    assert (solve_safe(a, b) == [2.0, 2.0, 1.0]).all()
    a = np.diag([1.0, 2.0, 0.0])
    b = np.array([2.0, 4.0, 1.0])
    assert (solve_safe(a, b) == [2.0, 2.0, 0.0]).all()
