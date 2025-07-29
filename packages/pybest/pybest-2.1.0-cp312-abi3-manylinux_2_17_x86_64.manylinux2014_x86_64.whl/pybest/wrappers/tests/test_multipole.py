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


"""Unit tests for dipole moment"""

import numpy as np
import pytest

from pybest.exceptions import ArgumentError
from pybest.linalg.base import OneIndex, TwoIndex
from pybest.utility import get_com, unmask, unmask_orb
from pybest.wrappers.multipole import (
    check_coord,
    check_ints,
    compute_dipole_moment,
    transform_dm,
    unfolding_dm,
)

fails = [
    "missing orb",
    "missing density_matrix",
    "no arguments",
    "no ints",
    "no basis",
    "no origin_coord",
]


@pytest.mark.parametrize("select", fails)
def test_fails(select, mol_generation):
    """Test fails for example molecule"""
    molecule = mol_generation[0]
    with pytest.raises(ArgumentError):
        if select == "missing density_matrix":
            del molecule.scf.dm_1
            compute_dipole_moment(molecule.dipole, molecule.scf)
        elif select == "missing orb":
            del molecule.scf.orb_a
            compute_dipole_moment(
                molecule.dipole, molecule.scf, molecular_orbitals=True
            )
        elif select == "no ints":
            molecule.dipole = None
            compute_dipole_moment(molecule.dipole, molecule.scf)
        elif select == "no basis":
            compute_dipole_moment(molecule.dipole)
        elif select == "no arguments":
            compute_dipole_moment()
        elif select == "no origin_coord":
            for i, arg in enumerate(molecule.dipole):
                if isinstance(arg, dict):
                    if "origin_coord" in arg:
                        molecule.dipole[i]["origin_coord"] = None
                        break
            compute_dipole_moment(molecule.dipole, molecule.scf)


# Test unfolding DM from OneIndex to TwoIndex object
def test_unfolding_dm(mol_generation_oopccd, scale=2.0):
    """unfolding DM from OneIndex to TwoIndex object"""
    molecule = mol_generation_oopccd[0]
    args = (molecule.dipole, molecule.pccd)
    occ_model = unmask("occ_model", molecule.pccd)
    nbasis = occ_model.nbasis[0]
    ncore = occ_model.ncore[0]
    dm_1 = unmask("dm_1", *args) or unmask("dm_1_a", *args)
    dm_1.iscale(scale)
    assert isinstance(dm_1, OneIndex)
    dm_1 = unfolding_dm(dm_1, nbasis, ncore)
    assert isinstance(dm_1, TwoIndex)


def test_transform_dm(mol_generation_oopccd_ncore, dm1_data):
    """Checks the shape and elements of DM (with and without frozen core) in the AO basis"""
    molecule_fc = mol_generation_oopccd_ncore
    expected = dm1_data
    args = (molecule_fc.pccd, molecule_fc.pccd_lccsd)
    occ_model_fc = unmask("occ_model", molecule_fc.pccd)
    nbasis = occ_model_fc.nbasis[0]
    ncore = occ_model_fc.ncore[0]
    scale = [1.0, 2.0, -2.0]
    orb = unmask_orb(*args)
    dm_1_unmask = unmask("dm_1", *args) or unmask("dm_1_a", *args)
    dm_1 = None
    if isinstance(dm_1_unmask, dict):
        dm_1 = dm_1_unmask["pq"].copy()
    else:
        dm_1 = dm_1_unmask.copy()

    if isinstance(dm_1, OneIndex):
        dm_1 = unfolding_dm(dm_1, nbasis, ncore)
    dm_1 = transform_dm(dm_1, nbasis, ncore, orb)
    assert dm_1.shape == (nbasis, nbasis)
    for i in range(len(scale)):
        dm_1.iscale(scale[i])
        #  check if the density matrix is correct only when scaled by 2.0
        if isinstance(dm_1_unmask, OneIndex):
            if ncore == 0:
                if scale[i] == 2.0:
                    assert np.allclose(
                        dm_1.array, expected["ref_pccd_dm1_no_fc"]
                    )
                else:
                    assert not np.allclose(
                        dm_1.array, expected["ref_pccd_dm1_no_fc"]
                    )

            else:
                if scale[i] == 2.0:
                    assert np.allclose(dm_1.array, expected["ref_pccd_dm1_fc"])
                else:
                    assert not np.allclose(
                        dm_1.array, expected["ref_pccd_dm1_fc"]
                    )
        else:
            if ncore == 0:
                if scale[i] == 2.0:
                    assert np.allclose(
                        dm_1.array, expected["ref_lccsd_dm1_no_fc"]
                    )
                else:
                    assert not np.allclose(
                        dm_1.array, expected["ref_lccsd_dm1_no_fc"]
                    )

            else:
                if scale[i] == 2.0:
                    assert np.allclose(
                        dm_1.array, expected["ref_lccsd_dm1_fc"]
                    )
                else:
                    assert not np.allclose(
                        dm_1.array, expected["ref_lccsd_dm1_fc"]
                    )


def test_checking_coord(mol_generation):
    """Checking coordinates"""
    molecule = mol_generation[0]
    basis = unmask("occ_model", molecule.dipole, molecule.scf)
    basis = basis.factory
    pos_x, pos_y, pos_z = get_com(basis)
    assert check_coord(molecule.dipole) == [pos_x, pos_y, pos_z]


def test_ints(mol_generation):
    """Checking ints"""
    molecule = mol_generation[0]
    expected_ints = ["mu_x", "mu_y", "mu_z"]
    mus = check_ints(molecule.dipole)
    assert all(mus_ in expected_ints for mus_ in mus)


def test_separate_args(mol_generation):
    """Separating arguments of Twoindex objects from their list"""
    molecule = mol_generation[0]
    assert compute_dipole_moment(*molecule.dipole, molecule.scf)


# Test can be extended to more molecules or UHF in the future
def test_dipole_hf(mol_generation):
    """Test HF dipole moment."""
    molecule, expected = mol_generation
    dipole_hf = np.array(compute_dipole_moment(molecule.dipole, molecule.scf))
    assert (abs(dipole_hf - expected["dipole_hf"]) < 1e-3).all()


# Test can be extended to more molecules or to UHF in the future
def test_dipole_hf_args(mol_generation):
    """Test various args in SCF wrapper for dipole moment."""

    molecule, expected = mol_generation
    dipole_hf = np.array(compute_dipole_moment(molecule.dipole, molecule.scf))

    # different scaling factor
    dipole_hf = np.array(
        compute_dipole_moment(molecule.dipole, molecule.scf, scale=1.0)
    )

    assert (abs(dipole_hf * 2.0 - expected["dipole_hf"]) < 1e-3).all()


# Test OOpCCD-LCCSD dipole moment in Debyes
@pytest.mark.slow
def test_dipole_oopccd(mol_generation_oopccd):
    """Test dipole moment from OOpCCD and OOpCCD-LCCSD ."""

    molecule, expected = mol_generation_oopccd

    dipole_pccd = np.array(
        compute_dipole_moment(
            molecule.dipole, molecule.pccd, molecular_orbitals=True
        )
    )

    assert (abs(dipole_pccd - expected["dipole_pccd"]) < 1e-3).all()

    molecule.do_pccd_lccsd()
    molecule.compute_dipole()
    dipole_pccd_lccsd = np.array(
        compute_dipole_moment(
            molecule.dipole, molecule.pccd_lccsd, molecular_orbitals=True
        )
    )
    assert (abs(dipole_pccd_lccsd - expected["dipole_lccsd"]) < 1e-3).all()
