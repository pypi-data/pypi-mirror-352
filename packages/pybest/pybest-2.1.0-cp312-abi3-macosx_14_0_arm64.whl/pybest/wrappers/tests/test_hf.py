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

from pybest import filemanager
from pybest.exceptions import ArgumentError
from pybest.iodata import IOData
from pybest.wrappers.hf import RHF, UHF
from pybest.wrappers.tests.common import Molecule

ref_e_water_dz = {
    "kin": 75.966167929737,
    "hartree": 46.858246886237,
    "x_hf": -8.970595331038,
    "ne": -199.019146537165,
    "nn": 9.138880476031,
    "total": -76.026446576199,
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
    "kin": 149.575743761456,
    "hartree": 100.421460958164,
    "x_hf": -16.348044690036,
    "ne": -411.500936926153,
    "nn": 28.222784582400,
    "total": -149.628992314170,
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


# HF class, alpha, molecule:
test_args_mol = [(RHF, 0, "h2o_ccdz"), (UHF, 2, "o2_ccdz")]

test_args = [
    ((), {"diis": "None"}, ValueError),
    ((), {"nvector": -1}, ValueError),
    # pass some string
    (("wrong argument",), {}, ArgumentError),
    # pass empty list
    (([],), {}, ArgumentError),
    # pass IOData
    ((IOData(),), {}, ArgumentError),
]


@pytest.mark.parametrize("cls,alpha,mol", test_args_mol)
@pytest.mark.parametrize("args,kwargs,error", test_args)
def test_hf_input_args(cls, alpha, mol, args, kwargs, error, linalg):
    """Test for wrong args/kwargs in HF wrappers. An error should be raised."""

    mol_ = Molecule(linalg, "cc-pvdz", f"test/{mol}.xyz", alpha=alpha)

    with pytest.raises(error):
        mol_.do_scf(cls, *args, **kwargs)


test_class = [
    (
        RHF,
        0,
        "h2o_ccdz",
        "plain",
        [ref_e_water_dz["total"], ref_e_orb_water_dz],
    ),
    (
        RHF,
        0,
        "h2o_ccdz",
        "cdiis",
        [ref_e_water_dz["total"], ref_e_orb_water_dz],
    ),
    (
        RHF,
        0,
        "h2o_ccdz",
        "ediis2",
        [ref_e_water_dz["total"], ref_e_orb_water_dz],
    ),
    (
        UHF,
        2,
        "o2_ccdz",
        "plain",
        [ref_e_o2_dz["total"], ref_e_orb_o2_a_dz, ref_e_orb_o2_b_dz],
    ),
    (
        UHF,
        2,
        "o2_ccdz",
        "cdiis",
        [ref_e_o2_dz["total"], ref_e_orb_o2_a_dz, ref_e_orb_o2_b_dz],
    ),
    (
        UHF,
        2,
        "o2_ccdz",
        "ediis2",
        [ref_e_o2_dz["total"], ref_e_orb_o2_a_dz, ref_e_orb_o2_b_dz],
    ),
]


@pytest.mark.parametrize("cls,alpha,mol,diis,expected", test_class)
def test_hf_restart(cls, alpha, mol, diis, expected, linalg):
    """Test restart kwarg."""

    mol_ = Molecule(linalg, "cc-pvdz", f"test/{mol}.xyz", alpha=alpha)
    # Do RHF/UHF using specific DIIS and tight threshold
    mol_.do_scf(cls, diis=diis, threshold=1e-12)

    assert abs(expected[0] - mol_.scf.e_tot) < 1e-8
    assert np.allclose(expected[1], mol_.scf.orb_a.energies)
    # The SCF solver does not create a copy of the initial orbitals
    assert mol_.scf.orb_a == mol_.orb[0]
    try:
        assert np.allclose(expected[2], mol_.scf.orb_b.energies)
        # The SCF solver does not create a copy of the initial orbitals
        assert mol_.scf.orb_b == mol_.orb[1]
    except IndexError:
        pass

    # Test restart option
    mol_2 = Molecule(linalg, "cc-pvdz", f"test/{mol}.xyz", alpha=alpha)
    # Do RHF/UHF using specific DIIS and tight threshold
    mol_2.do_scf(
        cls,
        diis=diis,
        threshold=1e-12,
        restart=f"{filemanager.result_dir}/checkpoint_scf.h5",
    )

    assert abs(expected[0] - mol_2.scf.e_tot) < 1e-8
    assert np.allclose(expected[1], mol_2.scf.orb_a.energies)
    # The SCF solver does not create a copy of the initial orbitals
    assert mol_2.scf.orb_a == mol_2.orb[0]
    try:
        assert np.allclose(expected[2], mol_2.scf.orb_b.energies)
        # The SCF solver does not create a copy of the initial orbitals
        assert mol_2.scf.orb_b == mol_2.orb[1]
    except IndexError:
        pass


testdata_diis = [
    ("plain", 1e-12, 1e-8),
    ("cdiis", 1e-12, 1e-8),
    ("ediis", 1e-5, 1e-6),
    ("ediis2", 1e-12, 1e-8),
]


@pytest.mark.parametrize("diis,thresh,compare", testdata_diis)
def test_diis_rhf_water(diis, thresh, compare, linalg):
    """Test various DIIS solvers for convergence: RHF."""

    mol_ = Molecule(linalg, "cc-pvdz", "test/h2o_ccdz.xyz")
    # Do RHF/UHF using specific DIIS and tight threshold
    mol_.do_scf(RHF, diis=diis, threshold=thresh)

    assert abs(ref_e_water_dz["total"] - mol_.scf.e_tot) < compare
    assert np.allclose(ref_e_orb_water_dz, mol_.orb[0].energies)
    assert np.allclose(ref_e_orb_water_dz, mol_.scf.orb_a.energies)
    # The SCF solver does not create a copy of the initial orbitals
    assert mol_.scf.orb_a == mol_.orb[0]


@pytest.mark.parametrize("diis,thresh,compare", testdata_diis)
def test_diis_uhf_o2(diis, thresh, compare, linalg):
    """Test various DIIS solvers for convergence: UHF."""

    mol_ = Molecule(linalg, "cc-pvdz", "test/o2_ccdz.xyz", alpha=2)
    # Do RHF/UHF using specific DIIS and tight threshold
    mol_.do_scf(UHF, diis=diis, threshold=thresh)

    assert abs(ref_e_o2_dz["total"] - mol_.scf.e_tot) < compare
    assert np.allclose(ref_e_orb_o2_a_dz, mol_.scf.orb_a.energies)
    assert np.allclose(ref_e_orb_o2_b_dz, mol_.scf.orb_b.energies)
    # The SCF solver does not create a copy of the initial orbitals
    assert mol_.scf.orb_a == mol_.orb[0]
    assert mol_.scf.orb_b == mol_.orb[1]
