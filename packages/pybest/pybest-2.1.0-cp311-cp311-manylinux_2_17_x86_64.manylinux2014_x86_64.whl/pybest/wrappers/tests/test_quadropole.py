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
"""Unit tests for quadrupole moment"""

import numpy as np
import pytest

from pybest.exceptions import ArgumentError
from pybest.wrappers import compute_quadrupole_moment

fails = [
    "missing orb",
    "missing density_matrix",
    "no arguments",
    "no ints",
    "no basis",
]


@pytest.mark.parametrize("select", fails)
def test_fails(select, mol_generation_quadrupole_moment):
    """Test fails for example molecule"""
    molecule = mol_generation_quadrupole_moment[0]
    with pytest.raises(ArgumentError):
        if select == "missing density_matrix":
            del molecule.scf.dm_1
            compute_quadrupole_moment(molecule.quadrupole, molecule.scf)
        elif select == "missing orb":
            del molecule.scf.orb_a
            compute_quadrupole_moment(
                molecule.quadrupole, molecule.scf, molecular_orbitals=True
            )
        elif select == "no ints":
            # del molecule.quadrupole
            molecule.quadrupole = None
            compute_quadrupole_moment(molecule.quadrupole, molecule.scf)
        elif select == "no basis":
            compute_quadrupole_moment(molecule.quadrupole)
        elif select == "no arguments":
            compute_quadrupole_moment()


def test_separate_args(mol_generation_quadrupole_moment):
    """Separating arguments of Twoindex objects from their list"""
    molecule = mol_generation_quadrupole_moment[0]
    assert compute_quadrupole_moment(*molecule.quadrupole, molecule.scf)


# Test can be extended to more molecules or UHF in the future
def test_quadrupole_hf(mol_generation_quadrupole_moment):
    """Test HF quadrupole moment."""
    molecule, expected = mol_generation_quadrupole_moment
    quadrupole_hf = np.array(
        compute_quadrupole_moment(molecule.quadrupole, molecule.scf)
    )
    assert (abs(quadrupole_hf - expected["quadrupole_hf"]) < 1e-3).all()


# Test can be extended to more molecules or to UHF in the future
def test_quadrupole_hf_args(mol_generation_quadrupole_moment):
    """Test various args in SCF wrapper for quadrupole moment."""

    molecule, expected = mol_generation_quadrupole_moment
    quadrupole_hf = np.array(
        compute_quadrupole_moment(molecule.quadrupole, molecule.scf)
    )

    # different scaling factor
    quadrupole_hf = np.array(
        compute_quadrupole_moment(
            molecule.quadrupole, molecule.scf, scale_1dm=1.0
        )
    )

    assert (abs(quadrupole_hf * 2.0 - expected["quadrupole_hf"]) < 1e-3).all()


# Test OOpCCD-LCCSD quadrupole moment in Debyes
@pytest.mark.slow
def test_quadrupole_oopccd(mol_generation_oopccd_qm):
    """Test quadrupole moment from OOpCCD and OOpCCD-LCCSD ."""

    molecule, expected = mol_generation_oopccd_qm

    quadrupole_pccd = np.array(
        compute_quadrupole_moment(
            molecule.quadrupole, molecule.pccd, molecular_orbitals=True
        )
    )

    assert (abs(quadrupole_pccd - expected["quadrupole_pccd"]) < 1e-3).all()

    molecule.do_pccd_lccsd()
    molecule.compute_quadrupole()
    quadrupole_pccd_lccsd = np.array(
        compute_quadrupole_moment(
            molecule.quadrupole, molecule.pccd_lccsd, molecular_orbitals=True
        )
    )

    assert (
        abs(quadrupole_pccd_lccsd - expected["quadrupole_lccsd"]) < 1e-3
    ).all()
