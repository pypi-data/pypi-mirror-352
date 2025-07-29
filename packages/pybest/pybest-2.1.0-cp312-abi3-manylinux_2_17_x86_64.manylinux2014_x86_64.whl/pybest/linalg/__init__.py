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
"""One-, two-, three-, four-, five-, and six-dimensional matrix implementations

The purpose of this package is to provide a generic API for different
implementations of real-valued double precision matrix storage and
operations.

This module assumes physicists notation for the two-particle operators.

One should use these matrix implementations without accessing the internals
of each class, i.e. without accessing attributes or methods that start with
an underscore.

In order to avoid temporaries when working with arrays, the methods do
not return arrays. Instead such methods are an in place operation or have
output arguments. This forces the user to allocate all memory in advance,
which can then be moved out of the loops. The initial implementation (the
Dense... classes) are just a proof of concept and may therefore contain
internals that still make temporaries. This fixed later with an alternative
implementation.
"""

# define test runner
from pybest._pytesttester import PytestTester

from .base import (
    EightIndex,
    FiveIndex,
    FourIndex,
    LinalgFactory,
    OneIndex,
    Orbital,
    SixIndex,
    ThreeIndex,
    TwoIndex,
)
from .dense.dense_eight_index import DenseEightIndex
from .dense.dense_five_index import DenseFiveIndex
from .dense.dense_four_index import DenseFourIndex
from .dense.dense_linalg_factory import DenseLinalgFactory
from .dense.dense_one_index import DenseOneIndex
from .dense.dense_orbital import DenseOrbital
from .dense.dense_six_index import DenseSixIndex
from .dense.dense_three_index import DenseThreeIndex
from .dense.dense_two_index import DenseTwoIndex

# NOTE: cholesky needs to be imported last as it depends on dense
from .cholesky import CholeskyFourIndex, CholeskyLinalgFactory  # isort:skip


__all__ = [
    "CholeskyFourIndex",
    "CholeskyLinalgFactory",
    "DenseEightIndex",
    "DenseFiveIndex",
    "DenseFourIndex",
    "DenseLinalgFactory",
    "DenseOneIndex",
    "DenseOrbital",
    "DenseSixIndex",
    "DenseThreeIndex",
    "DenseTwoIndex",
    "EightIndex",
    "FiveIndex",
    "FourIndex",
    "LinalgFactory",
    "OneIndex",
    "Orbital",
    "SixIndex",
    "ThreeIndex",
    "TwoIndex",
]

test = PytestTester(__name__)
del PytestTester
