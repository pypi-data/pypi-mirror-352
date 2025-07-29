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
# This implementation has been taken from `Horton 2.0.0`.
# However, this file has been updated and debugged. Compatibility with Horton is NOT
# guaranteed.
# Its current version contains updates from the PyBEST developer team.
#
# Detailed changes (see also CHANGELOG):
# 2020-07-01: Update to PyBEST standard, including naming convention
# 2020-07-01: New function `solve_hermitian`, which does not break down in contrast to
#             `solve_safe`

"""A collection of solvers to solve linear problems"""

import numpy as np
import scipy as scipy

__all__ = ["find_1d_root", "solve_hermitian", "solve_safe"]


def find_1d_root(fn, xy0, xy2, eps):
    """Find the root of a 1D function

    **Arguments:**

    fn
         The function to be zeroed.

    (x0, y0), (x2, y2)
         Argument and function value pairs for the initial bracket.

    eps
         The allowed error on the function.
    """
    x0 = xy0[0]
    y0 = xy0[1]
    x2 = xy2[0]
    y2 = xy2[1]
    # we want y0 < 0 and y2 > 0
    if y2 < 0:
        x0, y0, x2, y2 = x2, y2, x0, y0
    assert y0 < 0
    assert y2 > 0
    # root finder loop
    while True:
        # When t would be allowed to be close to 0 or 1, slow convergence may
        # occur with exponential-like (very non-linear) functions.
        t = np.clip(y0 / (y0 - y2), 0.1, 0.9)
        # compute the new point
        x1 = x0 + t * (x2 - x0)
        y1 = fn(x1)
        # decide on convergence or which edge of the bracket to replace
        if abs(y1) < eps:
            return x1, y1
        elif y1 > 0:
            x2, y2 = x1, y1
        else:
            x0, y0 = x1, y1


def solve_safe(a, b):
    """Try to solve with numpy.linalg.solve. Use SVD as fallback.
    Note, this method is not stable for small error vectors. In such cases use
    method solve_hermitian instead (if a is Hermitian).

    **Arguments:**

    a, b
         Arrays for the matrix equation a x = b.
    """
    try:
        # The default is to use the standard solver as it is faster and more
        # accurate than the SVD code below.
        return np.linalg.solve(a, b)
    except np.linalg.LinAlgError:
        # If the standard procedure breaks, fall back to an SVD-based solver
        # that selects the least-norm solution in case of trouble.
        u, s, vt = np.linalg.svd(a, full_matrices=False)
        rank = (s != 0).sum()
        u = u[:, :rank]
        s = s[:rank]
        vt = vt[:rank]
        assert s.min() > 0
        return np.dot(vt.T, np.dot(u.T, b) / s)


def solve_hermitian(a, b):
    """Solve a linear equation of the from a x = b using scipy.eigh. Matrix a has to
    be a symmetric/Hermitian matrix.

    In contrast to solve_safe, this function is stable for small error vectors.

    **Arguments:**

    a, b
         Arrays for the matrix equation a x = b.
    """
    w, v = scipy.linalg.eigh(a)
    idx = abs(w) > 1e-14
    c = np.dot(v[:, idx] * (1 / w[idx]), np.dot(v[:, idx].T.conj(), b))
    return c, v
