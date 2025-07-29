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

"""Unit tests for RtCCSD method from rtcc module."""

import pytest

from pybest import filemanager
from pybest.cc.rtcc import RtCCSD

from .common import CCMolecule

testdata_rtcc = [(RtCCSD, "cn+", "cc-pvdz", {"ncore": 0, "charge": 1})]


def write_external_amplitudes():
    """CC amplitudes from external source only for testing purposes
    (no physical meaning).
    """
    data = """ 1 4 1 4 7 12 7 12
        0.5000 1 1  7  7\n
        0.2500 1 2  8  8\n
        0.1250 3 3  9 10\n
        0.0625 1 4 11 12\n
        0 0 0 0 0\n
        0.7500 1 7 0 0\n
    """
    path = filemanager.temp_path("cc_amplitudes_ext.tmp")
    with open(path, "w+") as ext_t_file:
        ext_t_file.write(data)
    return path


def generate_RtCCSD_instance(cls, mol_f, basis, kwargs, linalg_slow):
    ncore = kwargs.get("ncore")
    charge = kwargs.get("charge")
    "Create RtCCSD instance that can be used for testing purposes."
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=charge, ncore=ncore)
    mol_.do_rhf()
    cls_instance = cls(mol_.lf, mol_.occ_model)
    cls_instance.initguess = "constant"
    cls_instance.read_external_amplitudes(write_external_amplitudes())
    cls_instance.set_hamiltonian(mol_.one, mol_.two, mol_.hf.orb_a)
    return cls_instance


@pytest.mark.parametrize("cls,mol_f,basis,kwargs", testdata_rtcc)
def test_rtcc_read_header(cls, mol_f, basis, kwargs, linalg_slow):
    "Check if method recognizes length of header and number of core electrons."
    tcc = generate_RtCCSD_instance(cls, mol_f, basis, kwargs, linalg_slow)
    length, core = tcc.read_header(write_external_amplitudes())
    assert length == 1
    assert core == 2


@pytest.mark.parametrize("cls,mol_f,basis,kwargs", testdata_rtcc)
def test_rtcc_read_external_amplitudes(cls, mol_f, basis, kwargs, linalg_slow):
    "Check if external amplitudes are assigned to proper positions."
    tcc = generate_RtCCSD_instance(cls, mol_f, basis, kwargs, linalg_slow)
    assert tcc.fixed_t1_value == [0.75]
    assert tcc.fixed_t1_index == [(2, 2)]
    assert tcc.fixed_t2_value == [0.5, 0.25, 0.125, 0.0625]
    assert tcc.fixed_t2_index == [
        (2, 2, 2, 2),
        (2, 3, 3, 3),
        (4, 4, 4, 5),
        (2, 6, 5, 7),
    ]


@pytest.mark.parametrize("cls,mol_f,basis,kwargs", testdata_rtcc)
def test_rtcc_generate_guess(cls, mol_f, basis, kwargs, linalg_slow):
    "Check if external amplitudes are assigned to proper positions."
    tcc = generate_RtCCSD_instance(cls, mol_f, basis, kwargs, linalg_slow)
    initguess = tcc.generate_guess(constant=0.125)
    t_1 = initguess["t_1"]
    t_2 = initguess["t_2"]
    assert t_2.get_element(2, 2, 2, 2) == 0.5
    assert t_2.get_element(2, 6, 5, 7) == 0.0625
    assert t_2.get_element(5, 7, 2, 6) == 0.0625
    assert t_2.get_element(2, 3, 4, 5) == 0.125
    assert t_1.get_element(2, 2) == 0.75
    assert t_1.get_element(4, 5) == 0.125


@pytest.mark.parametrize("cls,mol_f,basis,kwargs", testdata_rtcc)
def test_rtcc_vfunction(cls, mol_f, basis, kwargs, linalg_slow):
    """Check if residual vector elements that correspond to external amplitudes
    are set to zero."""
    tcc = generate_RtCCSD_instance(cls, mol_f, basis, kwargs, linalg_slow)
    initguess = tcc.generate_guess(constant=0.125)
    rvector = tcc.vfunction(tcc.ravel(initguess))
    vfunc = tcc.unravel(rvector)
    assert vfunc["t_2"].get_element(2, 2, 2, 2) == 0
    assert vfunc["t_2"].get_element(2, 6, 5, 7) == 0
    assert vfunc["t_2"].get_element(5, 7, 2, 6) == 0
    assert vfunc["t_2"].get_element(1, 1, 1, 1) != 0
    assert vfunc["t_1"].get_element(2, 2) == 0
