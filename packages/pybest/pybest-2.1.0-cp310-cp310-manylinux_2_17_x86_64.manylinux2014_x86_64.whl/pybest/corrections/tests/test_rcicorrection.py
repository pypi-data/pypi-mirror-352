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


import pytest

from pybest.corrections.rci_corrections import RCICorrections

# Reference data
ref_data = [
    {
        "Davidson": -0.00989139,
        "Renormalized Davidson": -0.01039463,
        "Modified Pople": -0.00831570,
        "Meissner": -0.00646777,
        "Duch and Diercksen": -0.00866853,
    },
    {
        "Davidson": -0.05622841,
        "Renormalized Davidson": -0.06975964,
        "Modified Pople": -0.05813303,
        "Meissner": -0.04756339,
        "Duch and Diercksen": -0.07271534,
    },
    {
        "Davidson": -0.19832306,
        "Renormalized Davidson": -0.30306976,
        "Modified Pople": -0.26939534,
        "Meissner": -0.23770177,
        "Duch and Diercksen": -0.50779234,
    },
]

parameters = [
    (5, 0.97549280, -0.20430931, ref_data, 0),
    (6, -0.89779211, -0.28988297, ref_data, 1),
    (9, -0.80893811, -0.573819693, ref_data, 2),
]


@pytest.mark.parametrize(
    "nacto, civ_0, e_civ_0, exp_result, set_number", parameters
)
def test_cis(nacto, civ_0, e_civ_0, exp_result, set_number):
    rcicorrections = RCICorrections(nacto)
    rcicorrections_output = rcicorrections(civ_0, e_civ_0, display=True)
    for key in rcicorrections_output.e_ci_scc:
        assert (
            abs(
                rcicorrections_output.e_ci_scc[key]
                - exp_result[set_number][key]
            )
            < 1e-6
        )
