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

"""Utility functions"""

from __future__ import annotations

from collections import Counter
from typing import Any

import numpy as np

from pybest.exceptions import ArgumentError, BasisError

__all__ = [
    "check_gobasis",
    "check_lf",
    "check_options",
    "check_type",
]


def check_gobasis(basis: Any | None = None) -> None:
    """Check a GO Basis specification

    **Arguments:**

    basis
         A Basis instance.

    **Optional arguments:**

    **Returns:**
    """
    #
    # Determine PyBasis:
    #
    if basis is not None:
        atom = np.array(basis.atom)
        natom = len(atom)
        shell = basis.shell2atom
        coord = np.array(basis.coordinates)
    else:
        raise BasisError("No PyBasis instance given.")

    #
    # Check coordinates:
    #
    if coord.shape != (natom, 3):
        raise BasisError("Coordinates corrupted.")
    if not issubclass(coord.dtype.type, np.floating):
        raise BasisError("Coordinates have wrong type.")

    #
    # Check atoms:
    #
    if not issubclass(atom.dtype.type, np.integer):
        raise BasisError("Atoms have wrong type.")

    #
    # Check basis set:
    #

    if len(Counter(shell).keys()) != natom:
        raise BasisError(
            "Basis set incomplete. Pleases check if basis set file is correct."
        )
    if basis.ncenter != natom:
        raise BasisError(
            "Number of atom centers. Does not agree with number of atoms"
        )
    if len(basis.alpha) != len(basis.contraction):
        raise BasisError(
            "Number of contractions and exponents does not agree."
        )
    if sum(basis.nprim) != len(basis.contraction):
        raise BasisError(
            "Number of contractions does not agree with number of primitives."
        )


def check_type(name: Any, instance: Any, *Classes: Any) -> None:
    """Check type of argument with given name against list of types

    **Arguments:**

    name
         The name of the argument being checked.

    instance
         The object being checked.

    Classes
         A list of allowed types.
    """
    if len(Classes) == 0:
        raise TypeError(
            "Type checking with an empty list of classes. This is a simple bug!"
        )
    match = False
    for Class in Classes:
        if isinstance(instance, Class):
            match = True
            break
    if not match:
        classes_parts = ["'", Classes[0].__name__, "'"]
        for Class in Classes[1:-1]:
            classes_parts.extend([", ``", Class.__name__, "'"])
        if len(Classes) > 1:
            classes_parts.extend([" or '", Classes[-1].__name__, "'"])
        raise TypeError(
            f"The argument '{name}' must be an instance of {''.join(classes_parts)}. "
            f"Got a '{instance.__class__.__name__}' instance instead."
        )


def check_options(name: Any, select: Any, *options: Any) -> None:
    """Check if a select is in the list of options. If not raise ValueError

    **Arguments:**

    name
         The name of the argument.

    select
         The value of the argument.

    options
         A list of allowed options.
    """
    if select not in options:
        formatted = ", ".join([f"'{option}'" for option in options])
        raise ValueError(f"The argument '{name}' must be one of: {formatted}")


def check_lf(lf: Any, operand: Any) -> None:
    """Check if operand and lf belong to the same factory.
    Only 4-index quantities are supported.
    All lower-dimensional quantities are always Dense and
    work with both factories.

    **Arguments:**

    lf
         An instance of LinalgFactory.

    operand
         The operand to be checked.

    """
    # Check lf instances
    if not hasattr(lf, "linalg_identifier"):
        raise ArgumentError(f"Unknown linalg factory type {lf}")
    # Check operand instances
    if not hasattr(operand, "four_identifier"):
        raise ArgumentError(f"Unknown operand type {operand}")

    # Note: CholeskyLinalgFactory inherits from DenseLinalgFactory. Checking for
    # DenseLinalgFactory will always be True
    if hasattr(lf, "cholesky_linalg_identifier") != hasattr(
        operand, "cholesky_four_identifier"
    ):
        raise ArgumentError(
            f"LinalgFactory {type(lf)} and operand {type(operand)} are of different type."
        )
