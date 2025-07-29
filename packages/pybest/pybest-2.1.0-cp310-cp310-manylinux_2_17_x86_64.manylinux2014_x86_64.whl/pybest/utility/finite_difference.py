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

"""Utility functions to calculate finite difference tests"""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

__all__ = [
    "fda_1order",
    "fda_2order",
]


def fda_1order(
    fun: Any,
    fun_deriv: Any,
    x: NDArray[np.float64],
    dxs: NDArray[np.float64],
    threshold: float = 1e-5,
) -> None:
    """Check the analytical gradient of `fun_deriv` using finite difference approximation

    Arguments:
    fun
         The function whose derivatives must be to be tested

    fun_deriv
         The implementation of the analytical derivatives

    x
         The argument for the reference point.

    dxs
         A list with small relative changes to x

    threshold
         The threshold

    For every displacement in ``dxs``, the following computation is repeated:

    1) D1 = 'fun(x+dx) - fun(x)' is computed.
    2) D2 = '0.5 (fun_deriv(x+dx) + fun_deriv(x)) . dx' is computed.

    For each case, |D1 - D2| should be smaller than the threshold.
    """
    dn1s = []
    dn2s = []
    dnds = []
    f0 = fun(x)
    grad0 = fun_deriv(x)
    for dx in dxs:
        f1 = fun(x + dx)
        grad1 = fun_deriv(x + dx)
        grad = 0.5 * (grad0 + grad1)
        d1 = f1 - f0
        if hasattr(d1, "__iter__"):
            norm = np.linalg.norm
        else:
            norm = abs
        d2 = np.dot(grad, dx)

        dn1s.append(norm(d1))
        dn2s.append(norm(d2))
        dnds.append(norm(d1 - d2))
    dn1s = np.array(dn1s)
    dn2s = np.array(dn2s)
    dnds = np.array(dnds)

    mask = dnds > threshold
    if (mask).all():
        raise AssertionError(
            f"The first order approximation for the difference is too wrong. "
            f"The allowed threshold is {threshold}.\n"
            f"First order approximation to differences:\n {*dn1s[mask], }\n"
            f"Analytic derivative:\n {*dn2s[mask], }\n"
            f"Absolute errors:\n {*dnds[mask], }"
        )


def fda_2order(
    fun: Any,
    fun_deriv: Any,
    x: NDArray[np.float64],
    dxs: NDArray[np.float64],
    threshold: float = 1e-5,
) -> None:
    """Check the analytical hessian of `fun_deriv` using finite differece approximation

    Arguments:
    fun
         The function whose derivatives must be to be tested

    fun_deriv
         The implementation of the analytical derivatives

    x
         The argument for the reference point.

    dxs
         A list with small relative changes to x

    threshold
         The threshold

    For every displacement in ``dxs``, the following computation is repeated:

    1) D1 = 'fun(x+dx) - 2 fun(x) + fun(x-dx)' is computed.
    2) D2 = '0.25 dx . (fun_deriv(x+dx) + 2 fun_deriv(x) + fun_deriv(x-dz)) . dx' is
       computed.

    For each case, |D1 - D2|, should be smaller than the threshold.
    """
    dn1s = []
    dn2s = []
    dnds = []
    f0 = fun(x)
    grad0 = fun_deriv(x)
    for dx in dxs:
        f1 = fun(x + dx)
        f2 = fun(x - dx)
        grad1 = fun_deriv(x + dx)
        grad2 = fun_deriv(x - dx)
        grad = (grad1 + 2.0 * grad0 + grad2) * 0.25
        d1 = f1 - 2.0 * f0 + f2
        if hasattr(d1, "__iter__"):
            norm = np.linalg.norm
        else:
            norm = abs
        d2_ = np.dot(grad, dx)
        d2 = np.dot(dx, d2_)

        dn1s.append(norm(d1))
        dn2s.append(norm(d2))
        dnds.append(norm(d1 - d2))
    dn1s = np.array(dn1s)
    dn2s = np.array(dn2s)
    dnds = np.array(dnds)

    mask = dnds > threshold
    if (mask).all():
        raise AssertionError(
            f"The first order approximation for the difference is too wrong. "
            f"The allowed threshold is {threshold}.\n"
            f"First order approximation to differences:\n {*dn1s[mask], }\n"
            f"Analytic derivative:\n {*dn2s[mask], }\n"
            f"Absolute errors:\n {*dnds[mask], }"
        )
