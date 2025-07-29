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
# 11/2024: This file has been written by Seyedehdelaram Jahani (original version)
# 05/2025: This file has been updated to a new framework for test by Seyedehdelaram Jahani.

import numpy as np
import pytest

from pybest.properties import Koopmans, ModifiedKoopmans
from pybest.tests.common import load_reference_data

from .common import PropertyMolecule

# Testing e_orb_ks and e_orb_kp for Be atom
# Testing e_orb_mks and e_orb_mkp for Be atom
test_set = [
    (
        "be",
        "cc-pvdz",
        {"charge": 0, "ncore": -1, "nroot": 0},
    ),
]


@pytest.mark.parametrize(
    "cls,method,ref",
    [(Koopmans, "k", "pccd"), (ModifiedKoopmans, "mk", "pccd")],
)
@pytest.mark.parametrize("mol_f,basis,kwargs", test_set)
def test_orbital_energies(cls, method, ref, mol_f, basis, kwargs, linalg):
    """Test Koopmans or Modified Koopmans orbital energies using pCCD.

    This test performs Restricted Hartree-Fock (RHF) and pair Coupled Cluster Doubles (pCCD)
    calculations to compute orbital energies based on the Koopmans or Modified Koopmans approach.
    The computed orbital energies are compared against reference values loaded from disk.

    Args:
        cls (type): Class representing the orbital energy method (e.g., Koopmans, ModifiedKoopmans).
        method (str): Method identifier used to format property names (e.g., "k", "mk").
        ref (str): Reference method label used in property calculations (typically "pccd").
        mol_f (str): Molecule identifier (e.g., "be").
        basis (str): Basis set to be used (e.g., "cc-pvdz").
        kwargs (dict): Dictionary containing:
            - ncore (int): Number of frozen core orbitals (-1 to autodetect).
            - nroot (int): Number of excited states/roots.
            - charge (int): Total molecular charge.
        linalg (Any): Linear algebra backend or solver instance.
    """
    ncore = kwargs.get("ncore")
    nroot = kwargs.get("nroot")
    charge = kwargs.get("charge")

    # Use auto_ncore feature by setting ncore=-1
    mol = PropertyMolecule(mol_f, basis, linalg, charge=charge, ncore=ncore)
    mol.do_rhf()
    # Overwrite orbitals from file
    mol.read_molden(mol_f)
    mol.do_pccd()
    mol.do_orbital_energies(cls, ref)

    expected = load_reference_data(
        method="orbitalenergies",
        molecule_name=mol_f,
        basis=basis,
        ncore=ncore,
        charge=charge,
        nroot=nroot,
    )
    params = [f"e_orb_{method}s", f"e_orb_{method}p_0", f"e_orb_{method}p_1"]

    for value in params:
        # Get calculated data stored as property (IOData)
        e_orb = mol.get_result(cls.__name__)
        # Access IOData element
        orb_en = getattr(e_orb, value)
        # Adjust this line based on actual API
        orb_en_array = orb_en.array
        # Loop over reference data
        data = expected[value]
        for i, ref_i in enumerate(data):
            assert np.allclose(
                ref_i,
                orb_en_array[i],
                atol=1e-5,
            ), f"Wrong {value} for {method}."
