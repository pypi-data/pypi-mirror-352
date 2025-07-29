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
# 2025-02: unification of variables and type hints (Julian Świerczyński)


import pytest

method_collection = [
    # All supported CCD models
    (
        ("hf", "ccd", "dip_ccd"),
        {"dip_ccd": {"alpha": 0, "nroot": 4, "nhole": 3}},
    ),
    (
        ("hf", "oopccd", "fpccd", "dip_fpccd"),
        {
            "oopccd": {
                "sort": False,
                "molden": True,
                "maxiter": {"orbiter": 0},
            },
            "dip_fpccd": {"alpha": 0, "nroot": 5, "nhole": 3},
        },
    ),
    (
        ("hf", "oopccd", "fplccd", "dip_fplccd"),
        {
            "oopccd": {
                "sort": False,
                "molden": True,
                "maxiter": {"orbiter": 0},
            },
            "dip_fplccd": {"alpha": 0, "nroot": 4, "nguessv": 15, "nhole": 3},
        },
    ),
    # All supported CCSD models
    (
        ("hf", "ccsd", "dip_ccsd"),
        {"dip_ccsd": {"alpha": 0, "nroot": 4, "nguessv": 15, "nhole": 3}},
    ),
    (
        ("hf", "lccsd", "dip_lccsd"),
        {"dip_lccsd": {"alpha": 0, "nroot": 6, "nhole": 3}},
    ),
    (
        ("hf", "oopccd", "fpccsd", "dip_fpccsd"),
        {
            "oopccd": {
                "sort": False,
                "molden": True,
                "maxiter": {"orbiter": 0},
            },
            "dip_fpccsd": {"alpha": 0, "nroot": 4, "nguessv": 15, "nhole": 3},
        },
    ),
    (
        ("hf", "oopccd", "fplccsd", "dip_fplccsd"),
        {
            "oopccd": {
                "sort": False,
                "molden": True,
                "maxiter": {"orbiter": 0},
            },
            "dip_fplccsd": {"alpha": 0, "nroot": 4, "nguessv": 15, "nhole": 3},
        },
    ),
]


#
# 2-fold parameterization:
# - Dense/Cholesky
# - IP flavours (from CCD to fpLCCSD)
#


@pytest.mark.parametrize(
    "methods,kwargs",
    method_collection,
    ids=[
        "dipccd-be_2",
        "dipfpccd-be_2",
        "dipfplccd-be_2",
        "dipccsd-be_2",
        "diplccsd-be_2",
        "dipfpccsd-be_2",
        "dipfplccsd-be_2",
    ],
)
def test_dip_rcc(
    methods: tuple[str, str],
    kwargs: dict[str, dict[str, int]],
    be_2: dict[str, object],
) -> None:
    """Test IP energies of various CC models including doubles and singles and
    doubles."""
    # Prepare molecule (all molecules have 1 additional electron)
    mol = be_2["molecule"]
    expected = be_2["results"]
    # Do a series of calculations
    mol.do_series_calculations(*methods, **kwargs)
    # Assess correctness of each method
    for method in methods:
        mol_result = getattr(mol, method)
        if hasattr(mol_result, "e_tot"):
            assert (
                abs(mol_result.e_tot - expected[f"e_{method}"]) < 1e-6
            ), f"Wrong total energy for {method}"
        if hasattr(mol_result, "e_ip_0"):
            for i, e_ip_ref in enumerate(expected[f"e_{method}"]):
                assert (
                    abs(e_ip_ref - mol_result.e_ip_0[i]) < 1e-6
                ), f"wrong IP energy for {method} and {i}-th state"
