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
"""A collection of utility functions of universal use in PyBEST"""

# define test runner
from pybest._pytesttester import PytestTester

from .check_data import check_gobasis, check_lf, check_options, check_type
from .docstrings import doc_inherit
from .finite_difference import fda_1order, fda_2order
from .math_functions import numpy_seed
from .molecule import get_com
from .orbitals import (
    compute_unitary_matrix,
    print_ao_mo_coeffs,
    project_orbitals,
    project_orbitals_frozen_core,
    rotate_orbitals,
    split_core_active,
    transform_integrals,
)
from .unmask_data import (
    unmask,
    unmask_onebody_hamiltonian,
    unmask_orb,
    unmask_twobody_hamiltonian,
)

__all__ = [
    "check_gobasis",
    "check_lf",
    "check_options",
    "check_type",
    "compute_unitary_matrix",
    "doc_inherit",
    "fda_1order",
    "fda_2order",
    "get_com",
    "numpy_seed",
    "print_ao_mo_coeffs",
    "project_orbitals",
    "project_orbitals_frozen_core",
    "rotate_orbitals",
    "split_core_active",
    "transform_integrals",
    "unmask",
    "unmask_onebody_hamiltonian",
    "unmask_orb",
    "unmask_twobody_hamiltonian",
]

test = PytestTester(__name__)
del PytestTester
