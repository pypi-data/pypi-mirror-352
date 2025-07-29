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
# ruff: noqa: F403
"""The main PyBEST Package"""

from importlib.metadata import PackageNotFoundError, version

__version__: str
try:
    __version__ = version("pybest")
except PackageNotFoundError:
    __version__ = "2.1.0"

import atexit

# intialize exceptions first
from .exceptions import *

# then initialize global FileManager
from .file_manager import FileManager  # isort:skip

filemanager = FileManager("pybest-results", "pybest-temp")
# If keep_temp is set to False, delete all temp dirs after exit
atexit.register(filemanager.clean_up_temporary_directory)

# stolen from NumPy
from pybest._pytesttester import PytestTester

from .auxmat import get_diag_fock_matrix, get_fock_matrix
from .cache import Cache, JustOnceClass, just_once
from .cc import *
from .ci import *
from .constants import *
from .context import context
from .corrections import RCICorrections
from .ea_eom import RDEApCCD, REApCCD
from .ee_eom import *
from .featuredlists import OneBodyHamiltonian, TwoBodyHamiltonian
from .gbasis import *
from .geminals import ROOpCCD, RpCCD
from .helperclass import PropertyHelper
from .io import *
from .iodata import *
from .ip_eom import *
from .linalg import *
from .localization import PipekMezey
from .log import log, timer
from .modelhamiltonians import PPP, ContactInteraction1D, Hubbard, Huckel
from .occ_model import (
    AufbauOccModel,
    AufbauSpinOccModel,
    FermiOccModel,
    FixedOccModel,
    FractionalOccModel,
)
from .orbital_entanglement import *
from .part import get_mulliken_operators, partition_mulliken
from .periodic import Element, Periodic, periodic
from .pt import *
from .rsf_eom import *
from .sapt import (
    SAPT0,
    prepare_cp_hf,
    prepare_cp_molecules,
    prepare_cp_monomers,
)
from .scf import *
from .solvers import *
from .steplength import *
from .units import *
from .utility import *
from .wrappers import *

__all__ = [
    "PPP",
    "SAPT0",
    "AufbauOccModel",
    "AufbauSpinOccModel",
    "Cache",
    "ContactInteraction1D",
    "Element",
    "FermiOccModel",
    "FileManager",
    "FixedOccModel",
    "FractionalOccModel",
    "Hubbard",
    "Huckel",
    "JustOnceClass",
    "OneBodyHamiltonian",
    "Periodic",
    "PipekMezey",
    "PropertyHelper",
    "RCICorrections",
    "RDEApCCD",
    "REApCCD",
    "ROOpCCD",
    "RpCCD",
    "TwoBodyHamiltonian",
    "context",
    "get_diag_fock_matrix",
    "get_fock_matrix",
    "get_mulliken_operators",
    "just_once",
    "log",
    "partition_mulliken",
    "periodic",
    "prepare_cp_hf",
    "prepare_cp_molecules",
    "prepare_cp_monomers",
    "timer",
]

test = PytestTester(__name__)
del PytestTester
