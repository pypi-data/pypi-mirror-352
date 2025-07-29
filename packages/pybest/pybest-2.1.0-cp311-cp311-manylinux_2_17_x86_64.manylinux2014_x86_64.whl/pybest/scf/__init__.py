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
"""Mean-field electronic structure code"""

# define test runner
from pybest._pytesttester import PytestTester

from .convergence import convergence_error_commutator, convergence_error_eigen
from .guess import guess_core_hamiltonian
from .hamiltonian import RScfHam, UScfHam
from .observable import (
    Observable,
    RDirectTerm,
    RExchangeTerm,
    RTwoIndexTerm,
    UDirectTerm,
    UExchangeTerm,
    UTwoIndexTerm,
    compute_dm_full,
)
from .scf_cdiis import CDIISSCFSolver
from .scf_ediis import EDIISSCFSolver
from .scf_ediis2 import EDIIS2SCFSolver
from .scf_plain import PlainSCFSolver
from .utils import (
    check_dm,
    compute_1dm_hf,
    compute_commutator,
    get_homo_lumo,
    get_level_shift,
    get_spin,
)

__all__ = [
    "CDIISSCFSolver",
    "EDIIS2SCFSolver",
    "EDIISSCFSolver",
    "Observable",
    "PlainSCFSolver",
    "RDirectTerm",
    "RExchangeTerm",
    "RScfHam",
    "RTwoIndexTerm",
    "UDirectTerm",
    "UExchangeTerm",
    "UScfHam",
    "UTwoIndexTerm",
    "check_dm",
    "compute_1dm_hf",
    "compute_commutator",
    "compute_dm_full",
    "convergence_error_commutator",
    "convergence_error_eigen",
    "get_homo_lumo",
    "get_level_shift",
    "get_spin",
    "guess_core_hamiltonian",
]

test = PytestTester(__name__)
del PytestTester
