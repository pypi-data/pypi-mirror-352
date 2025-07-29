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

from typing import Any

import pytest

method_collection = [
    # All supported CCD models
    (
        ("hf", "ccd", "ip_ccd"),
        {"ip_ccd": {"alpha": 1, "nroot": 4, "nhole": 2}},
    ),
    (
        ("hf", "oopccd", "fpccd", "ip_fpccd"),
        {
            "oopccd": {
                "sort": False,
                "molden": True,
                "maxiter": {"orbiter": 0},
            },
            "ip_fpccd": {"alpha": 1, "nroot": 5, "nhole": 2},
        },
    ),
    (
        ("hf", "oopccd", "fplccd", "ip_fplccd"),
        {
            "oopccd": {
                "sort": False,
                "molden": True,
                "maxiter": {"orbiter": 0},
            },
            "ip_fplccd": {"alpha": 1, "nroot": 4, "nguessv": 15, "nhole": 2},
        },
    ),
    # All supported CCSD models
    (
        ("hf", "ccsd", "ip_ccsd"),
        {"ip_ccsd": {"alpha": 1, "nroot": 4, "nguessv": 15, "nhole": 2}},
    ),
    (
        ("hf", "lccsd", "ip_lccsd"),
        {"ip_lccsd": {"alpha": 1, "nroot": 4, "nhole": 2}},
    ),
    (
        ("hf", "oopccd", "fpccsd", "ip_fpccsd"),
        {
            "oopccd": {
                "sort": False,
                "molden": True,
                "maxiter": {"orbiter": 0},
            },
            "ip_fpccsd": {"alpha": 1, "nroot": 4, "nguessv": 15, "nhole": 2},
        },
    ),
    (
        ("hf", "oopccd", "fplccsd", "ip_fplccsd"),
        {
            "oopccd": {
                "sort": False,
                "molden": True,
                "maxiter": {"orbiter": 0},
            },
            "ip_fplccsd": {"alpha": 1, "nroot": 4, "nguessv": 15, "nhole": 2},
        },
    ),
]

data_spin_free = [{"spinfree": True}, {"spinfree": False}]

#
# 3-fold parameterization:
# - spin-free/spin-dependent implementation
# - Dense/Cholesky
# - IP flavours (from CCD to fpLCCSD)
#


@pytest.mark.parametrize(
    "spin_free", data_spin_free, ids=["spin-free", "spin-dependent"]
)
@pytest.mark.parametrize(
    "methods,kwargs",
    method_collection,
    ids=[
        "ipccd-be_2",
        "ipfpccd-be_2",
        "ipfplccd-be_2",
        "ipccsd-be_2",
        "iplccsd-be_2",
        "ipfpccsd-be_2",
        "ipfplccsd-be_2",
    ],
)
def test_ip_rcc(
    spin_free: dict[str, bool],
    methods: tuple[str, str],
    kwargs: dict[str, dict[str, int]],
    be_2: dict[Any, dict[str, float]],
):
    """Test IP energies of various CC models including doubles and singles and
    doubles."""
    # Prepare molecule (all molecules have 1 additional electron)
    mol = be_2["molecule"]
    expected = be_2["results"]
    # Do a series of calculations
    mol.do_series_calculations(*methods, **spin_free, **kwargs)
    # Assess correctness of each method
    for method in methods:
        mol_result = getattr(mol, method)
        if hasattr(mol_result, "e_tot"):
            assert (
                abs(mol_result.e_tot - expected[f"e_{method}"]) < 1e-6
            ), f"Wrong total energy for {method}"
        if hasattr(mol_result, "e_ip_1"):
            for i, e_ip_ref in enumerate(expected[f"e_{method}"]):
                assert (
                    abs(e_ip_ref - mol_result.e_ip_1[i]) < 1e-6
                ), f"wrong IP energy for {method} and {i}-th state"
