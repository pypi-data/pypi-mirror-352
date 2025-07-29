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

from __future__ import annotations

from typing import Any

import pytest

from .common import FromFile, Molecule


#
# Define fixtures for testing: C^{2-}
#
@pytest.fixture
def c_atom(linalg) -> Molecule:
    """Returns instance of Molecule for C^2- that contains all information
    to perform several calculations (integrals, methods, etc.).
    """
    return Molecule("c", "cc-pvdz", linalg, ncore=0)


# Define fixtures for testing: H2O
#
@pytest.fixture
def h2o(linalg_slow) -> dict[str, Molecule | dict[str, Any]]:
    """Returns instance of Molecule for H2O that contains all information
    to perform several calculations (integrals, methods, etc.) and the
    corresponding solutions.
    """
    molecule = Molecule("water", "cc-pvdz", linalg_slow, ncore=0)
    results = {
        "e_hf": -76.025896291285,
        "e_pccd": -76.07225799852388,
        "e_ccd": -76.2382557548,
        "e_lccd": -76.2412842426491,
        "e_ccsd": -76.2389804958,
        "e_lccsd": -76.24223656721253,
        "e_fplccd": -76.24087307910472,
        "e_fplccsd": -76.24161609404385,
        "e_eom_fplccd": [
            0.90651537,
            1.02022512,
            1.02720833,
            1.05361035,
        ],
        "e_eom_fplccsd": [
            0.30129713,
            0.37634338,
            0.38708271,
            0.46444937,
        ],
        "e_eom_lccd": [
            0.99160927,
            1.02675950,
            1.05314153,
            1.09848780,
        ],
        "e_eom_ccd": [
            0.98991726,
            1.02495290,
            1.05094260,
            1.09654152,
        ],
        "e_eom_lccsd": [
            0.30082238,
            0.37571183,
            0.38896305,
            0.46490997,
        ],
        "e_eom_ccsd": [
            0.29948185,
            0.37428200,
            0.38731340,
            0.46327748,
        ],
    }
    return {"molecule": molecule, "results": results}


# Define fixtures for testing: CH+ (from FCIDUMP)
#
@pytest.fixture(params=[0, 1])
def chplus(request) -> dict[str, Molecule | list[dict[str, Any]] | int]:
    """Returns instance of Molecule for H2O that contains all information
    to perform several calculations (integrals, methods, etc.) and the
    corresponding solutions.
    """
    # Parameterize core electrons
    ncore = request.param
    molecule = FromFile(
        "chplus", 25, nocc=3, ncore=ncore, orb="test/chplus_opt.dat"
    )
    result_0 = {
        "e_ccs": -0.00073225,
        "e_pccd": -37.991225550170,
        "e_pccdccs": -37.99124837,
        "e_eom_ccs": [
            1.056498e-01,
            1.056498e-01,
            4.983904e-01,
            5.519407e-01,
            5.519407e-01,
            6.393116e-01,
        ],
        "e_eom_pccd": [
            6.889018e-01,
            7.930113e-01,
            1.355189e00,
            1.373127e00,
            1.833921e00,
            2.074985e00,
        ],
        "e_eom_pccds": [
            1.566229e-01,
            1.566229e-01,
            5.345106e-01,
            6.010138e-01,
            6.010138e-01,
            6.602393e-01,
        ],
        "e_eom_pccdccs": [
            1.56719601e-01,
            1.56719601e-01,
            5.34374846e-01,
            6.00964959e-01,
            6.00964959e-01,
            6.60240673e-01,
        ],
        "e_fplccd": -38.01414672,
        "e_eom_fplccd": [
            2.801303e-01,
            2.898505e-01,
            3.236840e-01,
            6.029520e-01,
            6.029528e-01,
            6.488371e-01,
        ],
        "e_fplccsd": -38.01452545,
        "e_eom_fplccsd": [
            1.169010e-01,
            1.169010e-01,
            2.770937e-01,
            2.870472e-01,
            3.220840e-01,
            4.908727e-01,
        ],
        "e_lccd": -0.1200197422,
        "e_eom_lccd": [
            0.29546007,
            0.29546007,
            0.33969795,
            0.66805648,
            0.66805649,
        ],
        "e_lccsd": -0.1205697860,
        "e_eom_lccsd": [
            0.12179294,
            0.12179294,
            0.33817215,
            0.49513671,
            0.52232539,
            0.52232540,
        ],
    }
    result_1 = {
        "e_ccs": -0.00073146,
        "e_pccd": -37.980850814377,
        "e_pccdccs": -37.980871952506284,
        "e_eom_ccs": [
            1.059466e-01,
            1.059466e-01,
            4.987062e-01,
            5.585047e-01,
            5.585047e-01,
            6.398128e-01,
        ],
        "e_eom_pccd": [
            6.889361e-01,
            7.930974e-01,
            1.355166e00,
            1.373136e00,
            1.833894e00,
            2.075022e00,
        ],
        "e_eom_pccds": [
            1.568994e-01,
            1.568995e-01,
            5.347868e-01,
            6.076699e-01,
            6.076699e-01,
            6.603085e-01,
        ],
        "e_eom_pccdccs": [
            1.56998064e-01,
            1.56998064e-01,
            5.34625566e-01,
            6.07623833e-01,
            6.07623833e-01,
            6.60309751e-01,
        ],
        "e_fplccd": -38.000861613522815,
        "e_eom_fplccd": [
            0.28067648,
            0.29007315,
            0.32406091,
            0.60279748,
            0.60279748,
            0.65588639,
        ],
        "e_fplccsd": -38.00123753963915,
        "e_eom_fplccsd": [
            0.11729709,
            0.11729709,
            0.27769558,
            0.28731237,
            0.32247700,
            0.49136035,
        ],
        "e_lccd": -0.1065150553,
        "e_eom_lccd": [
            0.29557695,
            0.29557695,
            0.33968274,
            0.67418902,
            0.67418902,
        ],
        "e_lccsd": -0.1070684559,
        "e_eom_lccsd": [
            0.12211131,
            0.12211131,
            0.33818162,
            0.49549585,
            0.52696580,
            0.52696581,
        ],
    }
    # We store the results as a list. First element is for ncore=0, second
    # for ncore=1. Thus, we can access the results for a given number of core
    # orbitals as results[ncore]
    return {
        "molecule": molecule,
        "results": [result_0, result_1],
        "ncore": ncore,
    }
