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


# NOTE: the reference data is determined for constants defined in CODATA 2018

import numpy as np
import pytest

from pybest.scf.scf_cdiis import CDIISSCFSolver
from pybest.scf.scf_ediis import EDIISSCFSolver
from pybest.scf.scf_ediis2 import EDIIS2SCFSolver
from pybest.scf.scf_plain import PlainSCFSolver
from pybest.scf.tests.common import prepare_hf, solve_scf_hf

ref_e_water_dz = {
    "kin": 75.966167929620,
    "hartree": 46.858246885977,
    "x_hf": -8.970595331005,
    "ne": -199.019146536525,
    "nn": 9.138880475737,
    "total": -76.026446576197,
}

ref_e_orb_water_dz = np.array(
    [
        -20.55116636,
        -1.33342941,
        -0.69713262,
        -0.56454528,
        -0.49256408,
        0.18469191,
        0.25535539,
        0.78687255,
        0.84681671,
        1.1635631,
        1.20043873,
        1.25314784,
        1.44983028,
        1.47325247,
        1.67621312,
        1.86958835,
        1.92588011,
        2.4407728,
        2.47526631,
        3.27814662,
        3.33511586,
        3.50068549,
        3.8635714,
        4.13826109,
    ]
)

ref_e_o2_dz = {
    "kin": 149.575744205085,
    "hartree": 100.421461357976,
    "x_hf": -16.348044840849,
    "ne": -411.500937617869,
    "nn": 28.222784581493,
    "total": -149.628992314164,
}


ref_e_orb_o2_a_dz = np.array(
    [
        -20.74916396,
        -20.74850338,
        -1.72456926,
        -1.19861276,
        -0.84002744,
        -0.84002738,
        -0.7602589,
        -0.54608643,
        -0.54608636,
        0.43760164,
        1.05429176,
        1.0542918,
        1.06855672,
        1.1417417,
        1.16489307,
        1.16489311,
        1.31275889,
        1.95442075,
        2.36727483,
        2.36727484,
        2.62190187,
        2.62190187,
        2.94050493,
        2.94050493,
        3.16738333,
        3.65575723,
        3.65575723,
        4.17196446,
    ]
)

ref_e_orb_o2_b_dz = np.array(
    [
        -20.69452164,
        -20.69330828,
        -1.59465534,
        -0.99169551,
        -0.69892562,
        -0.57595919,
        -0.57595916,
        0.11835314,
        0.11835316,
        0.51443822,
        1.099567,
        1.15964718,
        1.17464882,
        1.17464884,
        1.29135609,
        1.2913561,
        1.34484282,
        2.0066591,
        2.44144759,
        2.4414476,
        2.73910336,
        2.73910336,
        3.08879253,
        3.08879253,
        3.23948335,
        3.73269132,
        3.73269133,
        4.21795759,
    ]
)


def test_plain_scf_no_guess():
    # When one forgets to construct the initial guess, some error must be
    # raised...
    lf, olp, ham, occ_model, orb = prepare_hf(
        "cc-pvdz", "test/h2o_ccdz.xyz", skip_guess=True
    )

    scf_solver = PlainSCFSolver()
    with pytest.raises(AssertionError):
        solve_scf_hf(scf_solver, lf, ham, occ_model, olp, *orb)


test_cases = [
    (
        "H2O",
        "cc-pvdz",
        PlainSCFSolver,
        {},
        {
            "mol": "h2o_ccdz",
            "energy": ref_e_water_dz,
            "e_orb": ref_e_orb_water_dz,
            "threshold": 1e-12,
        },
    ),
    (
        "H2O",
        "cc-pvdz",
        CDIISSCFSolver,
        {},
        {
            "mol": "h2o_ccdz",
            "energy": ref_e_water_dz,
            "e_orb": ref_e_orb_water_dz,
            "threshold": 1e-12,
        },
    ),
    (
        "H2O",
        "cc-pvdz",
        EDIISSCFSolver,
        {},
        {
            "mol": "h2o_ccdz",
            "energy": ref_e_water_dz,
            "e_orb": ref_e_orb_water_dz,
            "threshold": 1e-6,
        },
    ),
    (
        "H2O",
        "cc-pvdz",
        EDIIS2SCFSolver,
        {},
        {
            "mol": "h2o_ccdz",
            "energy": ref_e_water_dz,
            "e_orb": ref_e_orb_water_dz,
            "threshold": 1e-6,
        },
    ),
    (
        "O2",
        "cc-pvdz",
        PlainSCFSolver,
        {"alpha": 2},
        {
            "mol": "o2_ccdz",
            "energy": ref_e_o2_dz,
            "e_orb": ref_e_orb_o2_a_dz,
            "e_orb_b": ref_e_orb_o2_b_dz,
            "threshold": 1e-12,
        },
    ),
    (
        "O2",
        "cc-pvdz",
        CDIISSCFSolver,
        {"alpha": 2},
        {
            "mol": "o2_ccdz",
            "energy": ref_e_o2_dz,
            "e_orb": ref_e_orb_o2_a_dz,
            "e_orb_b": ref_e_orb_o2_b_dz,
            "threshold": 1e-12,
        },
    ),
    (
        "O2",
        "cc-pvdz",
        EDIISSCFSolver,
        {"alpha": 2},
        {
            "mol": "o2_ccdz",
            "energy": ref_e_o2_dz,
            "e_orb": ref_e_orb_o2_a_dz,
            "e_orb_b": ref_e_orb_o2_b_dz,
            "threshold": 1e-6,
        },
    ),
    (
        "O2",
        "cc-pvdz",
        EDIIS2SCFSolver,
        {"alpha": 2},
        {
            "mol": "o2_ccdz",
            "energy": ref_e_o2_dz,
            "e_orb": ref_e_orb_o2_a_dz,
            "e_orb_b": ref_e_orb_o2_b_dz,
            "threshold": 1e-6,
        },
    ),
]


@pytest.mark.parametrize(
    "name, basis, cls, kw_occ_model, expected", test_cases
)
def test_scf_solvers(name, basis, cls, kw_occ_model, expected):
    lf, olp, ham, occ_model, orb = prepare_hf(
        basis, f"test/{expected['mol']}.xyz", **kw_occ_model
    )

    scf_solver = cls(threshold=expected["threshold"])
    scf = solve_scf_hf(scf_solver, lf, ham, occ_model, olp, *orb)

    threshold = expected["threshold"]

    # test the total energy
    np.testing.assert_allclose(
        scf.e_tot, expected["energy"]["total"], atol=threshold
    )

    assert np.allclose(expected["e_orb"], orb[0].energies)
    if hasattr(expected, "e_orb_b"):
        assert np.allclose(expected["e_orb_b"], orb[1].energies)
