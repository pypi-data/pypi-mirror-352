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
# 2024: This module has been originally written by Katharina Boguslawski
# 2025: Added support of general EA-CC (Saman Behjou).

import numpy as np
import pytest

from pybest.ea_eom.tests.common import EA_EOMMolecule
from pybest.linalg import DenseOneIndex


#
# Generate instance of Molecule class for C atom
#
@pytest.fixture
def carbon(linalg):
    """Generate instance for the carbon atom in a DZ basis set."""
    return EA_EOMMolecule("c", "cc-pvdz", linalg, charge=2, ncore=0)


#
# Generate instance of Molecule class for C atom
#
@pytest.fixture
def boron(linalg):
    """Generate instance for the boron atom in a DZ basis set."""
    return EA_EOMMolecule("boron", "cc-pvdz", linalg, charge=2, ncore=0)


@pytest.fixture
def water_mol():
    """Returns RHF/pCCD results and reference CC energies."""
    reference_correlation_energy = {
        "RCCD": -0.36932135,
        "RCCSD": -0.37694508,
        "RfpCCD": -0.39918855,
        "RfpCCSD": -0.39858230,
    }
    return {"mol": EA_EOMMolecule, "energies": reference_correlation_energy}


#
# Fixtures for testing guess: creates various h_diags
# we always test for 11 basis functions and 10 nacto
#
@pytest.fixture(
    params=[
        np.array([1, 4, 2, 6, 8, 9, 4, 5, 7, 3]),
        np.array([1, 2, 4, 1.1, 8, 9, 4, 5, 7, 3]),
        np.array([1, 2, 4, 1.1, 8, 9, 4, 5, 7, -3]),
    ]
)
def h_diag(request):
    """Create some OneDenseIndex object of shape `dim` and a numpy array as
    guess with label `h_diag`.
    """
    h_d = DenseOneIndex(10)
    h_d.label = "h_diag"
    h_d.array[:] = request.param
    return h_d


@pytest.fixture(params=[1, 2, 3, 4])
def guess_input(request, h_diag):
    """Create some OneDenseIndex object of shape `dim` and a numpy array as
    guess with label `h_diag`.
    """
    n_guess_vectors = request.param
    guess = []
    indices = np.argsort(h_diag.array)
    for i in range(n_guess_vectors):
        guess_ = DenseOneIndex(10)
        guess_.set_element(indices[i], 1.0)
        guess.append(guess_)
    return (guess, h_diag)
