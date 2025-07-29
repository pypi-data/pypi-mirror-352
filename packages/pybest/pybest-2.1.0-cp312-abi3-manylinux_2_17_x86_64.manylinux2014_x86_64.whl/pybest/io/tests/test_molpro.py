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

from pybest import context
from pybest.gbasis import (
    compute_eri,
    compute_kinetic,
    compute_nuclear,
    compute_nuclear_repulsion,
    get_gobasis,
)
from pybest.iodata import IOData
from pybest.linalg import DenseLinalgFactory


def test_load_fcidump_psi4_h2():
    mol = IOData.from_file(context.get_fn("test/FCIDUMP.psi4.h2"))
    assert mol.e_core == 0.7151043364864863e00
    assert mol.nelec == 2
    assert mol.ms2 == 0
    assert mol.lf.default_nbasis == 10
    assert mol.one.nbasis == 10
    assert mol.one.get_element(0, 0) == -0.1251399119550580e01
    assert mol.one.get_element(2, 1) == 0.9292454365115077e-01
    assert mol.one.get_element(1, 2) == 0.9292454365115077e-01
    assert mol.one.get_element(9, 9) == 0.9035054979531029e00
    assert mol.two.nbasis == 10
    assert mol.two.get_element(0, 0, 0, 0) == 0.6589928924251115e00
    # Check physicist's notation and symmetry
    assert mol.two.get_element(6, 1, 5, 0) == 0.5335846565304321e-01
    assert mol.two.get_element(5, 1, 6, 0) == 0.5335846565304321e-01
    assert mol.two.get_element(6, 0, 5, 1) == 0.5335846565304321e-01
    assert mol.two.get_element(5, 0, 6, 1) == 0.5335846565304321e-01
    assert mol.two.get_element(1, 6, 0, 5) == 0.5335846565304321e-01
    assert mol.two.get_element(1, 5, 0, 6) == 0.5335846565304321e-01
    assert mol.two.get_element(0, 6, 1, 5) == 0.5335846565304321e-01
    assert mol.two.get_element(0, 5, 1, 6) == 0.5335846565304321e-01
    assert mol.two.get_element(9, 9, 9, 9) == 0.6273759381091796e00


def test_load_fcidump_molpro_h2():
    mol = IOData.from_file(context.get_fn("test/FCIDUMP.molpro.h2"))
    assert mol.e_core == 0.7151043364864863e00
    assert mol.nelec == 2
    assert mol.ms2 == 0
    assert mol.lf.default_nbasis == 4
    assert mol.one.nbasis == 4
    assert mol.one.get_element(0, 0) == -0.1245406261597530e01
    assert mol.one.get_element(0, 1) == -0.1666402467335385e00
    assert mol.one.get_element(1, 0) == -0.1666402467335385e00
    assert mol.one.get_element(3, 3) == 0.3216193420753873e00
    assert mol.two.nbasis == 4
    assert mol.two.get_element(0, 0, 0, 0) == 0.6527679278914691e00
    # Check physicist's notation and symmetry
    assert mol.two.get_element(3, 0, 2, 1) == 0.7756042287284058e-01
    assert mol.two.get_element(2, 0, 3, 1) == 0.7756042287284058e-01
    assert mol.two.get_element(3, 1, 2, 0) == 0.7756042287284058e-01
    assert mol.two.get_element(2, 1, 3, 0) == 0.7756042287284058e-01
    assert mol.two.get_element(0, 3, 1, 2) == 0.7756042287284058e-01
    assert mol.two.get_element(0, 2, 1, 3) == 0.7756042287284058e-01
    assert mol.two.get_element(1, 3, 0, 2) == 0.7756042287284058e-01
    assert mol.two.get_element(1, 2, 0, 3) == 0.7756042287284058e-01
    assert mol.two.get_element(3, 3, 3, 3) == 0.7484308847738417e00


def test_dump_load_fcidimp_consistency_ao(tmp_dir):
    # Setup IOData
    mol0 = IOData.from_file(context.get_fn("test/water.xyz"))
    basis = get_gobasis(
        "3-21G", context.get_fn("test/water.xyz"), print_basis=False
    )
    lf = DenseLinalgFactory(basis.nbasis)

    # Compute stuff for fcidump file. test without transforming to mo basis
    mol0.e_core = compute_nuclear_repulsion(basis)
    mol0.nelec = 10
    mol0.ms2 = 1
    mol0.one = lf.create_two_index()
    mol0.one = compute_kinetic(basis)
    mol0.one.iadd(compute_nuclear(basis))
    mol0.two = compute_eri(basis)

    # Dump to a file and load it again
    mol0.to_file(f"{tmp_dir.absolute()}/FCIDUMP")
    mol1 = IOData.from_file(f"{tmp_dir.absolute()}/FCIDUMP")

    # Compare results
    assert mol0.e_core == mol1.e_core
    assert mol0.nelec == mol1.nelec
    assert mol0.ms2 == mol1.ms2
    assert np.allclose(mol0.one._array, mol1.one._array)
    assert np.allclose(mol0.two._array, mol1.two._array)


def test_dump_load_fcidimp_consistency_separate(tmp_dir):
    # Setup IOData
    mol0 = IOData.from_file(context.get_fn("test/water.xyz"))
    basis = get_gobasis(
        "3-21G", context.get_fn("test/water.xyz"), print_basis=False
    )

    # Compute stuff for fcidump file. test without transforming to mo basis
    mol0.e_core = compute_nuclear_repulsion(basis)
    mol0.nelec = 10
    mol0.ms2 = 1
    mol0.kin = compute_kinetic(basis)
    mol0.ne = compute_nuclear(basis)
    mol0.eri = compute_eri(basis)
    mol0_one = mol0.kin.copy()
    mol0_one.iadd(mol0.ne)

    # Dump to a file and load it again
    mol0.to_file(f"{tmp_dir.absolute()}/FCIDUMP")
    mol1 = IOData.from_file(f"{tmp_dir.absolute()}/FCIDUMP")

    # Compare results
    assert mol0.e_core == mol1.e_core
    assert mol0.nelec == mol1.nelec
    assert mol0.ms2 == mol1.ms2
    assert np.allclose(mol0_one._array, mol1.one._array)
    assert np.allclose(mol0.eri._array, mol1.two._array)
