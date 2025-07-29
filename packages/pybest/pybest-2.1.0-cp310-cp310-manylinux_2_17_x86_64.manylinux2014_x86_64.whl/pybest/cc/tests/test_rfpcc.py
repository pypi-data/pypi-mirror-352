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
# 03/2025:
# This file has been modified by Somayeh Ahmadkhani and Lena Szczuczko

"""Unit tests for RfpCCD and RfpCCSD methods from rfpcc module."""

import pytest

from pybest.cc.rfpcc import RfpCCD, RfpCCSD
from pybest.linalg import DenseFourIndex, DenseLinalgFactory, DenseTwoIndex
from pybest.occ_model import AufbauOccModel

from .common import CCMolecule

#
#  Unit test
#


def check_pair_amplitudes(t_2, value):
    "Check if t_2 (DenseFourIndex) array has a given value at diagonal abab."
    assert t_2.get_element(0, 0, 0, 0) == value
    assert t_2.get_element(0, 1, 0, 1) == value
    assert t_2.get_element(0, 2, 0, 2) == value
    assert t_2.get_element(0, 0, 0, 1) != value
    assert t_2.get_element(0, 1, 0, 0) != value
    assert t_2.get_element(0, 1, 0, 2) != value
    assert t_2.get_element(0, 2, 0, 1) != value


test_data = [("h2", "cc-pvdz", {"ncore": 0, "charge": 0})]


@pytest.mark.parametrize("cls", [RfpCCD, RfpCCSD])
@pytest.mark.parametrize("mol_f,basis,kwargs", test_data)
@pytest.mark.parametrize("select", ["random", "constant"])
def test_generate_guess(cls, mol_f, basis, kwargs, linalg_slow, select):
    "Check if initial guess is dict and contains t_2 amplitudes."
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    cls_instance = cls(mol_.lf, mol_.occ_model)
    cls_instance.initguess = select
    nocc = mol_.occ_model.nocc[0]
    cls_instance.t_p = DenseTwoIndex(nocc, mol_.lf.default_nbasis - nocc)
    cls_instance.t_p.assign(2.0)
    initguess = cls_instance.generate_guess()
    assert isinstance(initguess, dict)
    assert isinstance(initguess["t_2"], DenseFourIndex)
    check_pair_amplitudes(initguess["t_2"], 2.0)


@pytest.mark.parametrize("cls", [RfpCCD, RfpCCSD])
@pytest.mark.parametrize("mol_f,basis,kwargs", test_data)
def test_vfunction(cls, mol_f, basis, kwargs, linalg_slow):
    "Check if vector function has 0 for seniority 0 amplitudes."
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()
    fpcc = cls(mol_.lf, mol_.occ_model)
    fpcc.set_hamiltonian(mol_.one, mol_.two, mol_.hf.orb_a)
    initguess = fpcc.generate_constant_guess(constant=0.125)
    vfunc = fpcc.vfunction(fpcc.ravel(initguess))
    check_pair_amplitudes(fpcc.unravel(vfunc)["t_2"], 0.0)


def test_set_pair_amplitudes():
    "Check if pair-amplitudes are set properly."
    t_p = DenseTwoIndex(2, 3)
    t_p.assign(1.0)
    t_2 = DenseFourIndex(2, 3, 2, 3)
    lf = DenseLinalgFactory(5)
    cc_solver = RfpCCD(lf, AufbauOccModel(lf, nel=4, ncore=0))
    four_index = cc_solver.set_pair_amplitudes(t_2, t_p)
    assert four_index.get_element(0, 0, 0, 0) == 1
    assert four_index.get_element(0, 2, 0, 2) == 1
    assert four_index.get_element(1, 0, 1, 0) == 1
    assert four_index.get_element(0, 2, 0, 0) == 0
    assert four_index.get_element(0, 0, 1, 0) == 0
    assert four_index.get_element(1, 1, 0, 0) == 0
    assert four_index.get_element(0, 1, 1, 2) == 0
