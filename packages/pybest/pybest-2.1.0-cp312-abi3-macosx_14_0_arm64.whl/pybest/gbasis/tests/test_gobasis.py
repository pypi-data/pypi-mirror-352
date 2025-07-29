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
from numpy.testing import assert_almost_equal

from pybest import filemanager
from pybest.context import context
from pybest.exceptions import BasisError
from pybest.gbasis import Basis
from pybest.gbasis.gobasis import get_gobasis
from pybest.iodata import IOData

test_cases = [
    ("cc-pvdz", None, None),
    ("cc-pvdz", [0], [0]),
    ("cc-pvdz", [0], [0, 1]),
    ("cc-pvdz", [0], [0, 2]),
    ("cc-pvdz", [0], None),
    ("cc-pvdz", None, [0, 2]),
]

test_raises = [
    ("cc-pvdz", None, [3], ValueError),
    ("cc-pvddddz", None, None, BasisError),
    ("cc-pvdz", [0], [0, 1, 3, 4], ValueError),
    ("cc-pvdz", [0], [2], BasisError),
    ("cc-pvdz", [5], None, BasisError),
    ("cc-pvdz", [5], [5], ValueError),
]


@pytest.mark.parametrize("basis, dummy, af", test_cases)
def test_gbasis_dry_run(basis, dummy, af):
    mol_xyz = context.get_fn("test/h2o.xyz")
    basis = get_gobasis(
        basis, mol_xyz, dummy=dummy, active_fragment=af, print_basis=False
    )
    assert isinstance(basis, Basis)

    with pytest.raises(BasisError):
        get_gobasis(
            f"{basis}notexisting.g94",
            mol_xyz,
            dummy=dummy,
            active_fragment=af,
            print_basis=False,
        )


@pytest.mark.parametrize("basis, dummy, af, error", test_raises)
def test_gbasis_raises(basis, dummy, af, error):
    mol_xyz = context.get_fn("test/h2o.xyz")

    with pytest.raises(error):
        get_gobasis(
            basis,
            mol_xyz,
            dummy=dummy,
            active_fragment=af,
            print_basis=False,
        )


def test_gbasis_consistency():
    fn: str = context.get_fn("test/lih.xyz")
    shell_map = np.array([0, 0, 0, 1, 1, 1, 1], dtype=np.int64)
    nprims = np.array([2, 3, 3, 5, 5, 5, 7], dtype=np.int64)
    shell_types = np.array([2, 1, 0, 2, 3, 0, 1], dtype=np.int64)
    alphas = np.random.uniform(0, 1, nprims.sum()).astype(np.float64)
    con_coeffs = np.random.uniform(-1, 1, nprims.sum()).astype(np.float64)

    basis = Basis(fn, nprims, shell_map, shell_types, alphas, con_coeffs)
    assert basis.nbasis == 25
    assert max(basis.shell_types) == 3

    shell_types = np.array([1, 1, 0, 2, 2, 0, 1])
    basis = Basis(fn, nprims, shell_map, shell_types, alphas, con_coeffs)
    assert basis.nbasis == 21
    assert max(basis.shell_types) == 2

    # The center indexes in the shell_map are out of range.
    shell_map[0] = 2
    with pytest.raises(ValueError):
        Basis(fn, nprims, shell_map, shell_types, alphas, con_coeffs)
    shell_map[0] = 0

    # The size of the array shell_types does not match the sum of nprims.
    shell_types = np.array([1, 1])
    with pytest.raises(ValueError):
        Basis(fn, nprims, shell_map, shell_types, alphas, con_coeffs)
    shell_types = np.array([1, 1, 0, -2, -2, 0, 1])

    # The elements of nprims should be at least 1.
    nprims[1] = 0
    with pytest.raises(ValueError):
        Basis(fn, nprims, shell_map, shell_types, alphas, con_coeffs)
    nprims[1] = 3

    # The size of the array alphas does not match the sum of nprims.
    alphas = np.random.uniform(-1, 1, 2)
    with pytest.raises(ValueError):
        Basis(fn, nprims, shell_map, shell_types, alphas, con_coeffs)
    alphas = np.random.uniform(-1, 1, nprims.sum())

    # The size of con_coeffs does not match nprims.
    con_coeffs = np.random.uniform(-1, 1, 3)
    with pytest.raises(ValueError):
        Basis(fn, nprims, shell_map, shell_types, alphas, con_coeffs)
    con_coeffs = np.random.uniform(-1, 1, nprims.sum())

    # Mixing cartesian and solid harmonics:
    shell_types[0] = max(abs(shell_types)) + 1
    with pytest.raises(ValueError):
        Basis(fn, nprims, shell_map, shell_types, alphas, con_coeffs)
    shell_types[0] = 2


def test_gob_normalization():
    fn = context.get_fn("test/h.xyz")
    alpha = np.array(
        [
            82.640000000,
            12.410000000,
            2.824000000,
            0.797700000,
            0.258100000,
            0.089890000,
            2.292000000,
            0.838000000,
            0.292000000,
            2.062000000,
            0.662000000,
            1.397000000,
        ]
    )
    nprim = np.array([3, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    shell2atom = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    shell_types = np.array([0, 0, 0, 0, 1, 1, 1, 2, 2, 3])
    contraction = np.array(
        [
            0.002006,
            0.015343,
            0.075579,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
        ]
    )
    basis = Basis(fn, nprim, shell2atom, shell_types, alpha, contraction)
    # l, s_obs, n_alpha
    assert abs(basis.get_renorm_pure(0, 1, 0) - 0.601575009051) < 1e-5
    assert abs(basis.get_renorm_pure(0, 3, 0) - 0.117002092145) < 1e-5
    assert abs(basis.get_renorm_pure(1, 4, 0) - 4.0198361784) < 1e-5
    assert (
        abs(
            basis.get_renorm_cart(2, 7, 0, np.array([2, 0, 0])) - 5.84002374414
        )
        < 1e-8
    )
    assert (
        abs(
            basis.get_renorm_cart(2, 7, 0, np.array([1, 1, 0])) - 10.1152178423
        )
        < 1e-8
    )
    assert (
        abs(
            basis.get_renorm_cart(3, 9, 0, np.array([3, 0, 0])) - 3.12353490477
        )
        < 1e-8
    )
    assert (
        abs(
            basis.get_renorm_cart(3, 9, 0, np.array([2, 1, 0])) - 6.98443637716
        )
        < 1e-8
    )
    assert (
        abs(
            basis.get_renorm_cart(3, 9, 0, np.array([1, 1, 1])) - 12.0973986675
        )
        < 1e-8
    )
    assert (
        abs(
            basis.get_renorm_pure(0, 0, 0)
            - basis.get_renorm_cart(0, 0, 0, np.array([0, 0, 0]))
        )
        < 1e-10
    )
    assert (
        abs(
            basis.get_renorm_pure(0, 1, 0)
            - basis.get_renorm_cart(0, 1, 0, np.array([0, 0, 0]))
        )
        < 1e-10
    )
    assert (
        abs(
            basis.get_renorm_pure(0, 2, 0)
            - basis.get_renorm_cart(0, 2, 0, np.array([0, 0, 0]))
        )
        < 1e-10
    )
    assert (
        abs(
            basis.get_renorm_pure(1, 4, 0)
            - basis.get_renorm_cart(1, 4, 0, np.array([1, 0, 0]))
        )
        < 1e-10
    )
    assert (
        abs(
            basis.get_renorm_pure(1, 5, 0)
            - basis.get_renorm_cart(1, 5, 0, np.array([0, 1, 0]))
        )
        < 1e-10
    )
    assert (
        abs(
            basis.get_renorm_pure(1, 6, 0)
            - basis.get_renorm_cart(1, 6, 0, np.array([0, 0, 1]))
        )
        < 1e-10
    )


def test_copy_basis():
    fn = context.get_fn("test/h.xyz")
    obs1 = get_gobasis("cc-pvqz", fn, print_basis=False)
    obs2 = Basis(obs1)
    assert obs1 != obs2
    assert obs1.alpha == obs2.alpha
    assert obs1.contraction == obs2.contraction
    assert obs1.basisname == obs2.basisname
    assert obs1.molfile == obs2.molfile
    assert obs1.nbasis == obs2.nbasis
    assert obs1.nprim == obs2.nprim
    assert obs1.nshell == obs2.nshell
    assert obs1.ncenter == obs2.ncenter
    assert obs1.shell2atom == obs2.shell2atom
    assert obs1.shell_types == obs2.shell_types
    assert obs1.atom == obs2.atom
    assert obs1.coordinates == obs2.coordinates


def test_write_read_basis():
    fn = context.get_fn("test/h.xyz")
    obs1 = get_gobasis("cc-pvqz", fn, print_basis=False)
    dump = IOData()
    dump.gbasis = obs1
    dump.to_file(f"{filemanager.temp_path('checkpoint.h5')}")
    # reading
    obs2 = IOData.from_file(f"{filemanager.temp_path('checkpoint.h5')}").gbasis

    assert obs1 != obs2
    assert obs1.alpha == obs2.alpha
    assert_almost_equal(obs1.contraction, obs2.contraction, decimal=14)
    assert obs2.basisname == ""
    assert obs2.molfile == ""
    assert obs1.nbasis == obs2.nbasis
    assert obs1.nprim == obs2.nprim
    assert obs1.nshell == obs2.nshell
    assert obs1.ncenter == obs2.ncenter
    assert obs1.shell2atom == obs2.shell2atom
    assert obs1.shell_types == obs2.shell_types
    assert obs1.atom == obs2.atom
    assert obs1.coordinates == obs2.coordinates


#
# Test dummy atoms
#

test_dummy = [
    ("cc-pvdz", "water_dimer", [0], None, [0, 1, 1, 8, 1, 1]),
    ("cc-pvdz", "water_dimer", [0, 1, 2], None, [0, 0, 0, 8, 1, 1]),
    ("cc-pvdz", "water_dimer", [0, 1, 5], None, [0, 0, 1, 8, 1, 0]),
    ("cc-pvdz", "water_dimer", [0, 1, 2, 3, 4, 5], None, [0, 0, 0, 0, 0, 0]),
    ("cc-pvdz", "water_dimer", [0, 1, 2], [0, 1, 2], [0, 0, 0]),
    ("cc-pvdz", "water_dimer", [0], [0, 3], [0, 8]),
    ("cc-pvdz", "water_dimer", [0], [0, 1, 2], [0, 1, 1]),
]


@pytest.mark.parametrize("basis, mol, dummy, af, expected", test_dummy)
def test_gbasis_dry_run_v2(basis, mol, dummy, af, expected):
    """Test set_dummy_atoms in Basis c++ class, which needs to set all dummy
    atoms in both atoms.atomic_number (used by libint) and atomic_numbers
    (exported by PyBasis) to zero.
    """
    mol_xyz = context.get_fn(f"test/{mol}.xyz")
    basis = get_gobasis(
        basis, mol_xyz, dummy=dummy, active_fragment=af, print_basis=False
    )

    assert basis.atom == expected


data_star_basis = [
    # basis set, molecule, number of basis functions
    ("3-21g", "h2o", 13),
    ("6-31g", "h2o", 13),
    ("6-31g*", "h2o", 18),
    ("6-31gstar", "h2o", 18),
    ("6-31g**", "h2o", 24),
    ("6-31gstarstar", "h2o", 24),
    ("6-311g**", "h2o", 30),
    ("6-311gstarstar", "h2o", 30),
]


@pytest.mark.parametrize("basis,molecule,nbasis", data_star_basis)
def test_gbasis_star_basis_reader(basis, molecule, nbasis):
    """Test of 6-31g*-type basis sets are read in correctly. We simply check
    if the number of contracted basis functions is correct. This is enough to
    check if the `*` is properly translated to `star`."""
    mol_xyz = context.get_fn(f"test/{molecule}.xyz")
    basis = get_gobasis(basis, mol_xyz, print_basis=False)

    assert basis.nbasis == nbasis, "Wrong number of basis functions"


data_nbasis = [
    ("sadlej-pvtz", "h2o", 42)
]  # data for any new basis set can be included here in future.


@pytest.mark.parametrize("basis,molecule,nbasis", data_nbasis)
def test_gbasis_basis_reader(basis, molecule, nbasis):
    """Test for any new basis set to be included in the PyBEST basis set library. We simply check
    if the number of contracted basis functions is correct."""
    mol_xyz = context.get_fn(f"test/{molecule}.xyz")
    basis = get_gobasis(basis, mol_xyz, print_basis=False)

    assert basis.nbasis == nbasis, "Wrong number of basis functions"
