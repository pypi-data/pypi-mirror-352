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

import pybest
import pybest.sapt as sapt_module
import pybest.sapt.sapt_utils as sapt_utils

SCF_EN_THRESH = 4e-10


def test_cp_he2_cc_pvdz():
    fn_name = "he2.xyz"
    he2_path = pybest.context.get_fn("test/" + fn_name)
    dimer, monA, monB = sapt_utils.prepare_cp_hf("cc-pvdz", he2_path)
    en_int = dimer.e_hf - monA.e_hf - monB.e_hf
    assert abs(en_int - 0.000026523798) < SCF_EN_THRESH


def test_cp_he2_aug_cc_pvdz():
    fn_name = "he2.xyz"
    he2_path = pybest.context.get_fn("test/" + fn_name)
    dimer, monA, monB = sapt_utils.prepare_cp_hf("aug-cc-pvdz", he2_path)
    en_int = dimer.e_hf - monA.e_hf - monB.e_hf
    assert abs(en_int - 0.00003032524) < SCF_EN_THRESH


def test_cp_arhf_cc_pvdz():
    fn_name = "arhf.xyz"
    arhf_path = pybest.context.get_fn("test/" + fn_name)
    dimer, monA, monB = sapt_utils.prepare_cp_hf(
        basis="cc-pvdz",
        fn_geo=arhf_path,
        fourindex_type="dense",
        solver="plain",
    )
    en_int = dimer.e_hf - monA.e_hf - monB.e_hf
    assert abs(en_int - 0.007730168601) < SCF_EN_THRESH


def check_value(tested, reference, threshold=1e-6):
    return abs(tested - reference) < threshold


@pytest.fixture(scope="module")
def get_sapt0_corrections():
    fn_name = "arhf.xyz"
    arhf_path = pybest.context.get_fn("test/" + fn_name)
    dimer, monA, monB = sapt_utils.prepare_cp_hf(
        basis="cc-pvdz",
        fn_geo=arhf_path,
        fourindex_type="dense",
        solver="plain",
    )
    sapt0_solver = sapt_module.SAPT0(monA, monB)
    sapt0_solver(monA, monB, dimer)
    corr = sapt0_solver.result

    return corr


def test_ind20u(get_sapt0_corrections):
    value = get_sapt0_corrections.get("E^{(20)}_{ind},unc")
    assert check_value(value, -4.77222070e-3)


def test_exch_ind20u(get_sapt0_corrections):
    value = get_sapt0_corrections.get("E^{(20)}_{exch-ind}(S^2),unc")
    assert check_value(value, 4.561761755e-3)


def test_elst10(get_sapt0_corrections):
    value = get_sapt0_corrections.get("E^{(10)}_{elst}")
    assert check_value(value, -4.504608294e-3)


def test_exch10(get_sapt0_corrections):
    value = get_sapt0_corrections.get("E^{(10)}_{exch}(S^2)")
    assert check_value(value, 12.720251218e-3)


def test_disp20u(get_sapt0_corrections):
    value = get_sapt0_corrections.get("E^{(20)}_{disp},unc")
    assert check_value(value, -1.378183383e-3)


def test_exch_disp20u(get_sapt0_corrections):
    value = get_sapt0_corrections.get("E^{(20)}_{exch-disp}(S^2),unc")
    assert check_value(value, 0.465155919e-3)
