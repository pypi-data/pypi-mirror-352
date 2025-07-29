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


import pybest
import pybest.sapt.sapt_utils as sapt_utils


def test_plain_solver_dense_he2():
    fn_name = "he2.xyz"
    abs_path = pybest.context.get_fn("test/" + fn_name)
    scf_opts = {"wfn_thresh": 1e-12, "en_thresh": 1e-9}
    dimer, monA, monB = sapt_utils.prepare_cp_hf(
        "cc-pvdz",
        abs_path,
        fourindex_type="dense",
        solver="plain",
        solver_opts=scf_opts,
    )

    en_int = dimer.e_hf - monA.e_hf - monB.e_hf
    assert abs(en_int - 0.000026523798) < 1e-10


def test_plain_solver_cholesky_he2():
    fn_name = "he2.xyz"
    abs_path = pybest.context.get_fn("test/" + fn_name)
    scf_opts = {"wfn_thresh": 1e-12, "en_thresh": 1e-9}
    dimer, monA, monB = sapt_utils.prepare_cp_hf(
        "cc-pvdz",
        abs_path,
        fourindex_type="dense",
        solver="plain",
        solver_opts=scf_opts,
    )
    en_int = dimer.e_hf - monA.e_hf - monB.e_hf
    assert abs(en_int - 0.000026523798) < 1e-10


def test_ediis2_solver_dense_he2():
    fn_name = "he2.xyz"
    abs_path = pybest.context.get_fn("test/" + fn_name)
    scf_opts = {"wfn_thresh": 1e-12, "en_thresh": 1e-9}
    dimer, monA, monB = sapt_utils.prepare_cp_hf(
        "cc-pvdz",
        abs_path,
        fourindex_type="dense",
        solver="ediis2",
        solver_opts=scf_opts,
    )

    en_int = dimer.e_hf - monA.e_hf - monB.e_hf
    assert abs(en_int - 0.000026523798) < 1e-10


def test_ediis2_solver_cholesky_he2():
    fn_name = "he2.xyz"
    abs_path = pybest.context.get_fn("test/" + fn_name)
    scf_opts = {"wfn_thresh": 1e-12, "en_thresh": 1e-9}
    dimer, monA, monB = sapt_utils.prepare_cp_hf(
        "cc-pvdz",
        abs_path,
        fourindex_type="Dense",
        solver="ediis2",
        solver_opts=scf_opts,
    )

    en_int = dimer.e_hf - monA.e_hf - monB.e_hf
    assert abs(en_int - 0.000026523798) < 1e-10
