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
    # All supported CCD models
    (
        ("hf", "lccd", "eom_lccd"),
        {"eom_lccd": {"nroot": 4}},
    ),
    (
        ("hf", "ccd", "eom_ccd"),
        {"eom_ccd": {"nroot": 4}},
    ),
    # All supported CCSD models
    (
        ("hf", "lccsd", "eom_lccsd"),
        {"eom_lccsd": {"nroot": 4}},
    ),
    (
        ("hf", "ccsd", "eom_ccsd"),
        {"eom_ccsd": {"nroot": 4}},
    ),
]

#
# 2-fold parameterization:
# - Dense/Cholesky
# - EOM flavors
#


@pytest.mark.parametrize(
    "methods,kwargs",
    method_collection,
    ids=[
        "eomlccd-h2o",
        "eomccd-h2o",
        "eomlccsd-h2o",
        "eomccsd-h2o",
    ],
)
def test_eom_rcc(
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
                    abs(e_ee_ref - mol_result.e_ee[i + 1]) < 1e-6
                ), f"wrong EE-EOM energy for {method} and {i}-th state"
