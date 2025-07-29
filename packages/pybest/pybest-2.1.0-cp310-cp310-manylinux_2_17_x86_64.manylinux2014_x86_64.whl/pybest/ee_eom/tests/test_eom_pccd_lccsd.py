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

from typing import Any

import pytest

method_collection: list[
    tuple[tuple[str, str, str], dict[str, dict[str, Any]]]
] = [
    # All supported pCCD-LCCSD models
    (
        ("pccd", "fplccsd", "eom_fplccsd"),
        {"eom_fplccsd": {"nroot": 6, "nguessv": 20, "davidson": True}},
    ),
]

#
# 1-fold parameterization:
# - EOM flavors
#


@pytest.mark.parametrize(
    "methods,kwargs",
    method_collection,
    ids=[
        "eompccdlccsd-chplus-Davidson",
    ],
)
def test_eom_pccdlccsd(
    methods: tuple[str, str, str],
    kwargs: dict[str, dict[str, Any]],
    chplus: dict[str, Any],
):
    """Test EE-EOM energies of various CC models."""
    # Prepare molecule
    mol = chplus["molecule"]
    ncore = chplus["ncore"]
    expected = chplus["results"][ncore]
    # Do a series of calculations contained in methods argument
    mol.do_series_calculations(*methods, **kwargs)
    # Assess the correctness of each method
    for method in methods:
        mol_result = getattr(mol, method)
        # Check if total energy (here of the CC ground state) is correct
        if hasattr(mol_result, "e_tot"):
            assert (
                abs(mol_result.e_tot - expected[f"e_{method}"]) < 1e-6
            ), f"Wrong total energy for {method}"
        # Check correctness of excitation energies
        if hasattr(mol_result, "e_ee"):
            for i, e_ee_ref in enumerate(expected[f"e_{method}"]):
                assert (
                    abs(e_ee_ref - mol_result.e_ee[i + 1]) < 1e-6
                ), f"wrong EE-EOM energy for {method} and {i}-th state"


#
# Test for both Cholesky and Dense (H2O)
#


@pytest.mark.parametrize(
    "methods,kwargs",
    method_collection,
    ids=[
        "eompccdlccsd-h2o-Davidson",
    ],
)
def test_eom_pccdlccsd_chol(
    methods: tuple[str, str, str],
    kwargs: dict[str, dict[str, Any]],
    h2o: dict[str, Any],
):
    """Test EE-EOM energies of various CC models."""
    # Prepare molecule
    mol = h2o["molecule"]
    expected = h2o["results"]
    # Do a series of calculations
    mol.do_series_calculations(*methods, **kwargs)
    # Assess the correctness of each method
    for method in methods:
        mol_result = getattr(mol, method)
        if hasattr(mol_result, "e_tot"):
            assert (
                abs(mol_result.e_tot - expected[f"e_{method}"]) < 1e-6
            ), f"Wrong total energy for {method}"
        if hasattr(mol_result, "e_ee"):
            for i, e_ee_ref in enumerate(expected[f"e_{method}"]):
                assert (
                    abs(e_ee_ref - mol_result.e_ee[i + 1]) < 1e-5
                ), f"wrong EE-EOM energy for {method} and {i}-th state"
