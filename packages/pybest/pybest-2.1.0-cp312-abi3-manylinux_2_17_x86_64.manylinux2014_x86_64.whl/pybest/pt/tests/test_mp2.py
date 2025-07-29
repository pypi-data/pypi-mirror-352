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


import numpy as np
import pytest

from pybest.context import context
from pybest.pt.tests.common import Molecule

test_cases = [
    (
        "h2o_ccdz",
        "cc-pvdz",
        0,
        {
            "mol": "h2o_ccdz",
            "orb_file": "h2o_ccdz_hf.txt",
            "e_ref": -76.02644658,
            "e_tot": -76.23075702,
        },
    ),
    (
        "h2o_ccdz",
        "cc-pvdz",
        1,
        {
            "mol": "h2o_ccdz",
            "orb_file": "h2o_ccdz_hf.txt",
            "e_ref": -76.02644658,
            "e_tot": -76.22843001,
        },
    ),
]

#
# Test conventional MP2
#


@pytest.mark.parametrize("mol,basis,ncore,dict_", test_cases)
def test_MP2(mol, basis, ncore, dict_, linalg):
    mol_ = Molecule(
        linalg,
        basis,
        f"test/{mol}.xyz",
        f"test/{dict_['orb_file']}",
        ncore,
    )
    # Do RHF
    mol_.do_rhf()
    # Do MP2
    mol_.do_mp2(ncore=ncore)

    assert abs(mol_.mp2.e_tot - dict_["e_tot"]) < 1e-6


@pytest.mark.parametrize("mol,basis,ncore,dict_", test_cases)
def test_MP2_update_orb(mol, basis, ncore, dict_, linalg):
    mol_ = Molecule(
        linalg,
        basis,
        f"test/{mol}.xyz",
        f"test/{dict_['orb_file']}",
        ncore,
    )
    # Do RHF
    mol_.do_rhf()
    orb_a_hf = mol_.rhf.orb_a.copy()
    # Do MP2
    mol_.do_mp2(ncore=ncore, natorb=True, relaxation=True)
    assert abs(mol_.mp2.e_tot - dict_["e_tot"]) < 1e-6

    orb_a_mp2 = mol_.mp2.orb_a.copy()

    # Reset RHF solution/container
    mol_.do_rhf()
    # Do MP2 by passing new orbitals as kwargs; natorb=relaxation=False
    mol_.do_mp2(ncore=ncore, orb_a=orb_a_mp2)

    # do not check energy as it will be different
    # check RHF orbitals
    assert np.allclose(mol_.rhf.orb_a.coeffs, orb_a_hf.coeffs)
    assert np.allclose(mol_.rhf.orb_a.energies, orb_a_hf.energies)
    assert np.allclose(mol_.rhf.orb_a.occupations, orb_a_hf.occupations)
    # check MP2 orbitals from kwargs
    assert np.allclose(mol_.mp2.orb_a.coeffs, orb_a_mp2.coeffs)
    assert np.allclose(mol_.mp2.orb_a.energies, orb_a_mp2.energies)
    assert np.allclose(mol_.mp2.orb_a.occupations, orb_a_mp2.occupations)


#
# Test SCS MP2 (different fos, fss values)
#

test_cases_scs = [
    # molfile, basis, ncore, kwargs (MP2 parameter, results, etc.)
    (
        "h2o_ccdz",
        "cc-pvdz",
        0,
        {
            "mol": "h2o_ccdz",
            "orb_file": "h2o_ccdz_hf.txt",
            "e_ref": -76.02644658,
            "e_tot": -76.17918767,
            "fos": 1.0,
            "fss": 0.0,
            "e_corr_os": -0.15274109,
            "e_corr_ss": 0.00000000,
            "relaxation": True,
            "natorb": True,
            "dm_file": "h2o_ccdz_dm_mp2_os.txt",
        },
    ),
    (
        "h2o_ccdz",
        "cc-pvdz",
        1,
        {
            "mol": "h2o_ccdz",
            "orb_file": "h2o_ccdz_hf.txt",
            "e_ref": -76.02644658,
            "e_tot": -76.17766713,
            "e_corr_os": -0.1512205,
            "e_corr_ss": 0.00000000,
            "fos": 1.0,
            "fss": 0.0,
        },
    ),
    (
        "h2o_ccdz",
        "cc-pvdz",
        0,
        {
            "mol": "h2o_ccdz",
            "orb_file": "h2o_ccdz_hf.txt",
            "e_ref": -76.02644658,
            "e_tot": -76.07801593,
            "fos": 0.0,
            "fss": 1.0,
            "e_corr_os": 0.00000000,
            "e_corr_ss": -0.05156935,
            "relaxation": True,
            "natorb": True,
            "dm_file": "h2o_ccdz_dm_mp2_ss.txt",
        },
    ),
    (
        "h2o_ccdz",
        "cc-pvdz",
        1,
        {
            "mol": "h2o_ccdz",
            "orb_file": "h2o_ccdz_hf.txt",
            "e_ref": -76.02644658,
            "e_tot": -76.07720945,
            "e_corr_os": 0.00000000,
            "e_corr_ss": -0.05076288,
            "fos": 0.0,
            "fss": 1.0,
        },
    ),
    (
        "h2o_ccdz",
        "cc-pvdz",
        0,
        {
            "mol": "h2o_ccdz",
            "orb_file": "h2o_ccdz_hf.txt",
            "e_ref": -76.02644658,
            "e_tot": -76.13415213,
            "e_corr_os": -0.04582233,
            "e_corr_ss": -0.06188322,
            "fos": 0.3,
            "fss": 1.2,
        },
    ),
    (
        "h2o_ccdz",
        "cc-pvdz",
        0,
        {
            "mol": "h2o_ccdz",
            "orb_file": "h2o_ccdz_hf.txt",
            "e_ref": -76.02644658,
            "e_tot": -76.22692568,
            "e_corr_os": -0.18328931,
            "e_corr_ss": -0.01718978,
            "fos": 1.2,
            "fss": 1 / 3,
        },
    ),
]


@pytest.mark.parametrize("mol,basis,ncore,dict_", test_cases_scs)
def test_hf_MP2_scs(mol, basis, ncore, dict_, linalg):
    # Define molecule
    mol_ = Molecule(
        linalg,
        basis,
        f"test/{mol}.xyz",
        f"test/{dict_['orb_file']}",
        ncore,
    )
    # Do RHF
    mol_.do_rhf()
    # Do MP2
    mol_.do_mp2(ncore=ncore, **dict_)

    # Check results
    assert abs(mol_.mp2.e_tot - dict_["e_tot"]) < 1e-6
    assert abs(mol_.mp2.e_corr_os - dict_["e_corr_os"]) < 1e-6
    assert abs(mol_.mp2.e_corr_ss - dict_["e_corr_ss"]) < 1e-6

    if "natorb" in dict_:
        fn_dm = context.get_fn(f"test/{dict_['dm_file']}")
        one_dm_ref = np.fromfile(fn_dm, sep=",")
        assert np.allclose(
            one_dm_ref, mol_.mp2.dm_1._array.diagonal() * 2.0
        ), "wrong electron density"
        assert (
            abs(np.sum(mol_.mp2.dm_1._array.diagonal() * 2.0) - 10.0) < 1e-8
        ), "wrong number of particles in SCS MP2 1-RDM"
