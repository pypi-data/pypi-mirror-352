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

from pybest.iodata import IOData

# Aufbau section
# (atom symbol, expected value of frozen core)
elements = [
    ("h", 0),
    ("he", 0),
    ("li", 1),
    ("be", 1),
    ("b", 1),
    ("c", 1),
    ("n", 1),
    ("o", 1),
    ("f", 1),
    ("ne", 1),
    ("na", 5),
    ("mg", 5),
    ("al", 5),
    ("si", 5),
    ("p", 5),
    ("s", 5),
    ("cl", 5),
    ("ar", 5),
    ("k", 9),
    ("ca", 9),
    ("sc", 9),
    ("ti", 9),
    ("v", 9),
    ("cr", 9),
    ("mn", 9),
    ("fe", 9),
    ("co", 9),
    ("ni", 9),
    ("cu", 9),
    ("zn", 9),
    ("ga", 9),
    ("ge", 9),
    ("as", 9),
    ("se", 9),
    ("br", 9),
    ("kr", 9),
    ("rb", 18),
    ("sr", 18),
    ("y", 18),
    ("zr", 18),
    ("nb", 18),
    ("mo", 18),
    ("tc", 18),
    ("ru", 18),
    ("rh", 18),
    ("pd", 18),
    ("ag", 18),
    ("cd", 18),
    ("in", 18),
    ("sn", 18),
    ("sb", 18),
    ("te", 18),
    ("i", 18),
    ("xe", 18),
    ("cs", 27),
    ("ba", 27),
    ("la", 27),
    ("ce", 27),
    ("pr", 27),
    ("nd", 27),
    ("pm", 27),
    ("sm", 27),
    ("eu", 27),
    ("gd", 27),
    ("tb", 27),
    ("dy", 27),
    ("ho", 27),
    ("er", 27),
    ("tm", 27),
    ("yb", 27),
    ("lu", 27),
    ("ta", 27),
    ("w", 27),
    ("re", 27),
    ("os", 27),
    ("ir", 27),
    ("pt", 27),
    ("au", 27),
    ("hg", 27),
    ("tl", 27),
    ("pb", 27),
    ("bi", 27),
    ("po", 27),
    ("at", 27),
    ("fr", 43),
    ("ra", 43),
    ("ac", 43),
    ("th", 43),
    ("pa", 43),
    ("u", 43),
    ("np", 43),
    ("pu", 43),
    ("am", 43),
    ("cm", 43),
]


@pytest.fixture(params=elements)
def ncore_test_with_atoms(request):
    atom_symbol, ncore = request.param
    basis = None
    if atom_symbol == "k":
        basis = "def2-SVP"
    elif ncore in range(10):
        basis = "cc-pvdz"
    elif ncore in range(18, 44):
        basis = "ANO-RCC-VTZP"

    # define the molecule and the coordinates and elements
    coordinates = np.zeros((1, 3))
    atom = np.array([atom_symbol], dtype=object)  # must be strings

    # assign coordinates to container
    mol = IOData(coordinates=coordinates, atom=atom)

    return basis, mol, ncore


test_ncore_with_molecule = [
    # Basis; Molecule; Kwargs; Expected ncore
    ("cc-pvdz", "test/water.xyz", {"charge": 1, "alpha": 1}, [1, 1]),
    ("cc-pvdz", "test/he.xyz", {"charge": 1, "alpha": 1}, [0, 0]),
    ("cc-pvdz", "test/h2o.xyz", {"charge": 1, "alpha": 1}, [1, 1]),
    ("cc-pvdz", "test/li.xyz", {"charge": 0, "alpha": 1}, [1, 1]),
    (
        "cc-pvdz",
        "test/no.xyz",
        {
            "charge": 0,
            "alpha": 1,
        },
        [2, 2],
    ),
    (
        "ano-rcc-vdz",
        "test/u2.xyz",
        {
            "charge": 1,
            "alpha": 1,
        },
        [86, 86],
    ),
]


@pytest.fixture(params=test_ncore_with_molecule)
def ncore_test_with_molecule(request):
    """Function that returns (basis, molecule, kwargs, expected) for testing the `ncore` value"""
    return request.param


instance_aufbau = ["cc-pvdz", "test/water.xyz", {"charge": 1, "alpha": 1}]

test_ncore_own_args = [
    # Args to create instance of AufbauOccModel; atomic number/s or symbol/s; Exptected
    (instance_aufbau, 1, 0),
    (instance_aufbau, 3, 1),
    (instance_aufbau, 11, 5),
    (instance_aufbau, 19, 9),
    (instance_aufbau, 37, 18),
    (instance_aufbau, 55, 27),
    (instance_aufbau, 87, 43),
    (instance_aufbau, "h", 0),
    (instance_aufbau, "Li", 1),
    (instance_aufbau, "Na", 5),
    (instance_aufbau, "K", 9),
    (instance_aufbau, "Rb", 18),
    (instance_aufbau, "Cs", 27),
    (instance_aufbau, "Fr", 43),
    (instance_aufbau, [1, 8, 1], 1),
    (instance_aufbau, [92, 92], 86),
    (instance_aufbau, ["H", "O", "H"], 1),
    (instance_aufbau, ["U", "U"], 86),
]


@pytest.fixture(params=test_ncore_own_args)
def ncore_test_with_own_args(request):
    """Function that returns:
    - List - a list containing information to create an instance of the class
    - Molecule - Returns the argument that the function accepts.
               Either a single int/str or list of atomic numbers or symbols.
    - ncore - an int specifying the expected number of ncore orbitals.
    """
    return request.param


test_aufbau = [
    # basis, molecule, {charge, #unpaired electrons (alpha), ncore}
    # test also different combinations of alpha/charge/unrestricted
    (
        "cc-pvdz",
        "test/water.xyz",
        {"charge": 0, "alpha": 0, "unrestricted": True},
        {
            "occ": [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
            "charge": 0,
            "nel": 10,
            "nbasis": [24, 24],
            "nact": [23, 23],
            "nocc": [5, 5],
            "nvirt": [19, 19],
            "nacto": [4, 4],
            "nactv": [19, 19],
            "ncore": [1, 1],
            "nactdo": [0, 0],
            "nactdv": [0, 0],
        },
    ),
    (
        "cc-pvdz",
        "test/water.xyz",
        {"charge": 0, "alpha": 0, "auto_ncore": True, "unrestricted": True},
        {
            "occ": [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
            "charge": 0,
            "nel": 10,
            "nbasis": [24, 24],
            "nact": [23, 23],
            "nocc": [5, 5],
            "nvirt": [19, 19],
            "nacto": [4, 4],
            "nactv": [19, 19],
            "ncore": [1, 1],
            "nactdo": [0, 0],
            "nactdv": [0, 0],
        },
    ),
    (
        "cc-pvdz",
        "test/water.xyz",
        {"charge": 0, "alpha": 0, "ncore": 1, "unrestricted": True},
        {
            "occ": [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
            "charge": 0,
            "nel": 10,
            "nbasis": [24, 24],
            "nact": [23, 23],
            "nocc": [5, 5],
            "nvirt": [19, 19],
            "nacto": [4, 4],
            "nactv": [19, 19],
            "ncore": [1, 1],
            "nactdo": [0, 0],
            "nactdv": [0, 0],
        },
    ),
    (
        "cc-pvdz",
        "test/water.xyz",
        {"charge": 0, "alpha": 0, "ncore": 0},
        {
            "occ": [[1, 1, 1, 1, 1]],
            "charge": 0,
            "nel": 10,
            "nbasis": [24],
            "nact": [24],
            "nocc": [5],
            "nvirt": [19],
            "nacto": [5],
            "nactv": [19],
            "ncore": [0],
            "nactdo": [0],
            "nactdv": [0],
        },
    ),
    (
        "cc-pvdz",
        "test/water.xyz",
        {"charge": 0, "alpha": 0, "ncore": 0, "unrestricted": True},
        {
            "occ": [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
            "charge": 0,
            "nel": 10,
            "nbasis": [24, 24],
            "nact": [24, 24],
            "nocc": [5, 5],
            "nvirt": [19, 19],
            "nacto": [5, 5],
            "nactv": [19, 19],
            "ncore": [0, 0],
            "nactdo": [0, 0],
            "nactdv": [0, 0],
        },
    ),
    (
        "cc-pvdz",
        "test/water.xyz",
        {"charge": 0, "alpha": 0, "ncore": 1, "unrestricted": True},
        {
            "occ": [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
            "charge": 0,
            "nel": 10,
            "nbasis": [24, 24],
            "nact": [23, 23],
            "nocc": [5, 5],
            "nvirt": [19, 19],
            "nacto": [4, 4],
            "nactv": [19, 19],
            "ncore": [1, 1],
            "nactdo": [0, 0],
            "nactdv": [0, 0],
        },
    ),
    (
        "cc-pvdz",
        "test/water.xyz",
        {"charge": 0, "alpha": 0, "ncore": 1},
        {
            "occ": [[1, 1, 1, 1, 1]],
            "charge": 0,
            "nel": 10,
            "nbasis": [24],
            "nact": [23],
            "nocc": [5],
            "nvirt": [19],
            "nacto": [4],
            "nactv": [19],
            "ncore": [1],
            "nactdo": [0],
            "nactdv": [0],
        },
    ),
    (
        "cc-pvdz",
        "test/water.xyz",
        {"charge": 1, "alpha": 1, "ncore": 0},
        {
            "occ": [[1, 1, 1, 1, 1], [1, 1, 1, 1]],
            "charge": 1,
            "nel": 9,
            "nbasis": [24, 24],
            "nact": [24, 24],
            "nocc": [5, 4],
            "nvirt": [19, 20],
            "nacto": [5, 4],
            "nactv": [19, 20],
            "ncore": [0, 0],
            "nactdo": [0, 0],
            "nactdv": [0, 0],
        },
    ),
    (
        "cc-pvdz",
        "test/water.xyz",
        {"charge": 1, "ncore": 0},  # test default value for alpha = 1
        {
            "occ": [[1, 1, 1, 1, 1], [1, 1, 1, 1]],
            "charge": 1,
            "nel": 9,
            "nbasis": [24, 24],
            "nact": [24, 24],
            "nocc": [5, 4],
            "nvirt": [19, 20],
            "nacto": [5, 4],
            "nactv": [19, 20],
            "ncore": [0, 0],
            "nactdo": [0, 0],
            "nactdv": [0, 0],
        },
    ),
    (
        "cc-pvdz",
        "test/water.xyz",
        {
            "charge": 1,
            "ncore": 0,
            "nactdo": 3,
            "nactdv": 1,
        },  # test default value for alpha = 1
        {
            "occ": [[1, 1, 1, 1, 1], [1, 1, 1, 1]],
            "charge": 1,
            "nel": 9,
            "nbasis": [24, 24],
            "nact": [24, 24],
            "nocc": [5, 4],
            "nvirt": [19, 20],
            "nacto": [5, 4],
            "nactv": [19, 20],
            "ncore": [0, 0],
            "nactdo": [3, 3],
            "nactdv": [1, 1],
        },
    ),
    (
        "cc-pvdz",
        "test/water.xyz",
        {"charge": 1, "alpha": 1, "ncore": 1},
        {
            "occ": [[1, 1, 1, 1, 1], [1, 1, 1, 1]],
            "charge": 1,
            "nel": 9,
            "nbasis": [24, 24],
            "nact": [23, 23],
            "nocc": [5, 4],
            "nvirt": [19, 20],
            "nacto": [4, 3],
            "nactv": [19, 20],
            "ncore": [1, 1],
            "nactdo": [0, 0],
            "nactdv": [0, 0],
        },
    ),
    (  # water with O 1s orbital as active core orbital
        "cc-pvdz",
        "test/water.xyz",
        {
            "charge": 0,
            "alpha": 0,
            "ncore": 0,
            "nactc": 1,
            "unrestricted": True,
            "nactdo": 0,
            "nactdv": 0,
        },
        {
            "occ": [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]],
            "charge": 0,
            "nel": 10,
            "nbasis": [24, 24],
            "nact": [24, 24],
            "nocc": [5, 5],
            "nvirt": [19, 19],
            "nacto": [4, 4],
            "nactc": [1, 1],
            "nactv": [19, 19],
            "ncore": [0, 0],
            "nactdo": [0, 0],
            "nactdv": [0, 0],
        },
    ),
    (  # water with O 1s orbital as active core
        "cc-pvdz",
        "test/water.xyz",
        {"charge": 0, "alpha": 0, "ncore": 0, "nactc": 1},
        {
            "occ": [[1, 1, 1, 1, 1]],
            "charge": 0,
            "nel": 10,
            "nbasis": [24],
            "nact": [24],
            "nocc": [5],
            "nvirt": [19],
            "nacto": [4],
            "nactc": [1],
            "nactv": [19],
            "ncore": [0],
            "nactdo": [0],
            "nactdv": [0],
        },
    ),
    (
        "sto-3g",
        "test/uracil.xyz",
        {
            "charge": 0,
            "alpha": 0,
            "ncore": 4,
            "nactc": 4,
            "unrestricted": True,
            "nactdo": 0,
            "nactdv": 0,
        },
        {
            "occ": [np.ones(29), np.ones(29)],
            "charge": 0,
            "nel": 58,
            "nbasis": [44, 44],
            "nact": [40, 40],
            "nocc": [29, 29],
            "nvirt": [15, 15],
            "nactc": [4, 4],  # C 1s active core orbitals
            "nacto": [21, 21],
            "nactv": [15, 15],
            "ncore": [4, 4],  # O 1s and N 1s in the core
            "nactdo": [0, 0],
            "nactdv": [0, 0],
        },
    ),
    (
        "sto-3g",
        "test/uracil.xyz",
        {"charge": 0, "ncore": 2, "nactc": 2, "unrestricted": True},
        {
            "occ": [np.ones(29), np.ones(29)],
            "charge": 0,
            "nel": 58,
            "nbasis": [44, 44],
            "nact": [42, 42],
            "nocc": [29, 29],
            "nvirt": [15, 15],
            "nactc": [2, 2],  # N 1s active core orbitals
            "nacto": [25, 25],
            "nactv": [15, 15],
            "ncore": [2, 2],  # O 1s in the core
            "nactdo": [0, 0],
            "nactdv": [0, 0],
        },
    ),
    (
        "sto-3g",
        "test/uracil.xyz",
        {"charge": 0, "ncore": 0, "nactc": 2, "unrestricted": True},
        {
            "occ": [np.ones(29), np.ones(29)],
            "charge": 0,
            "nel": 58,
            "nbasis": [44, 44],
            "nact": [44, 44],
            "nocc": [29, 29],
            "nvirt": [15, 15],
            "nactc": [2, 2],  # O 1s active core orbitals
            "nacto": [27, 27],
            "nactv": [15, 15],
            "ncore": [0, 0],
            "nactdo": [0, 0],
            "nactdv": [0, 0],
        },
    ),
]


@pytest.fixture(params=test_aufbau)
def aufbau_test(request):
    """Function that returns (basis, molecule, kwargs, expected) for testing the aufbau occupation model"""
    return request.param


#
# Additional tests for AufbauOccModel using lf instance
#

expected_lf_nel = {
    "occ": [[1, 1, 1, 1]],
    "charge": 0,
    "nel": 8,
    "nbasis": [8],
    "nact": [8],
    "nocc": [4],
    "nvirt": [4],
    "nacto": [4],
    "nactv": [4],
    "ncore": [0],
    "nactdo": [0],
    "nactdv": [0],
}


test_aufbau_lf_nel = [
    # nbasis, nel, nocc (as kwargs)
    (8, 8, {"ncore": 0}, expected_lf_nel),
    (8, 8, {"ncore": 0, "nocc_a": 4}, expected_lf_nel),
    (8, None, {"ncore": 0, "nocc_a": 4}, expected_lf_nel),
    (8, None, {"ncore": 0, "nocc_a": 4, "nocc_b": 4}, expected_lf_nel),
    (8, 8, {"ncore": 0, "unrestricted": False}, expected_lf_nel),
]


@pytest.fixture(params=test_aufbau_lf_nel)
def aufbau_test_lf_nel(request):
    """Function that returns (basis, molecule, kwargs, expected)
    and testing AufbauOccModel for lf, nel, and occ_a, occ_b as only input
    """
    return request.param


#
# Tests for unrestricted (open-shell) cases using AufbauOccModel
#

expected_lf_nel_os = {
    "occ": [[1, 1, 1, 1, 1], [1, 1, 1, 1]],
    "charge": 0,
    "nel": 9,
    "nbasis": [8, 8],
    "nact": [8, 8],
    "nocc": [5, 4],
    "nvirt": [3, 4],
    "nacto": [5, 4],
    "nactv": [3, 4],
    "ncore": [0, 0],
    "nactdo": [0, 0],
    "nactdv": [0, 0],
}


test_aufbau_lf_nel_os = [
    # nbasis, nel, nocc (as kwargs)
    (8, 9, {"ncore": 0, "alpha": 1}, expected_lf_nel_os),
    (8, 9, {"ncore": 0}, expected_lf_nel_os),
    (8, 9, {"ncore": 0, "unrestricted": True}, expected_lf_nel_os),
    (8, 9, {"ncore": 0, "nocc_a": 5, "nocc_b": 4}, expected_lf_nel_os),
    (8, None, {"ncore": 0, "nocc_a": 5, "nocc_b": 4}, expected_lf_nel_os),
]


@pytest.fixture(params=test_aufbau_lf_nel_os)
def aufbau_test_lf_nel_os(request):
    """Function that returns (basis, molecule, kwargs, expected)
    and testing AufbauOccModel for lf, nel, and occ_a, occ_b as the only input
    """
    return request.param


# occ_Fixed section


args_fixed_to_test_ncore = [
    ("cc-pvdz", "test/water.xyz", np.array([1, 1, 1, 1, 0, 1]), 1),
    ("cc-pvdz", "test/be.xyz", np.array([1, 0, 1]), 1),
    ("cc-pvdz", "test/ne.xyz", np.array([1, 1, 1, 1, 0, 1]), 1),
]


@pytest.fixture(params=args_fixed_to_test_ncore)
def fixed_test_ncore(request):
    """Function that returns (basis, molecule, kwargs, expected)
    for testing ncore value in FixedOccModel
    """
    return request.param


# occ_Fractional section
