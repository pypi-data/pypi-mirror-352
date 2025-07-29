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


import os

import numpy as np

from pybest import context, periodic
from pybest.gbasis import compute_nuclear_repulsion, compute_overlap
from pybest.io.tests.common import compute_hf_energy, compute_mulliken_charges
from pybest.iodata import IOData
from pybest.linalg import DenseLinalgFactory
from pybest.scf.utils import compute_1dm_hf
from pybest.units import angstrom


def test_load_mkl_ethanol():
    fn_mkl = context.get_fn("test/ethanol.mkl")
    mol = IOData.from_file(fn_mkl)

    numbers = np.array([periodic[i].number for i in mol.atom])
    # Direct checks with mkl file
    assert numbers.shape == (9,)
    assert numbers[0] == 1
    assert numbers[4] == 6
    assert mol.coordinates.shape == (9, 3)
    assert abs(mol.coordinates[2, 1] / angstrom - 2.239037) < 1e-5
    assert abs(mol.coordinates[5, 2] / angstrom - 0.948420) < 1e-5
    assert mol.basis.nbasis == 39
    assert mol.basis.alpha[0] == 18.731137000
    assert mol.basis.alpha[10] == 7.868272400
    assert mol.basis.alpha[-3] == 2.825393700
    assert mol.basis.shell2atom[:5] == [0, 0, 1, 1, 1]
    assert mol.basis.shell_types[:5] == [0, 0, 0, 0, 1]
    assert mol.basis.nprim[-5:] == [3, 1, 1, 3, 1]
    assert mol.orb_a.coeffs.shape == (39, 39)
    assert mol.orb_a.energies.shape == (39,)
    assert mol.orb_a.occupations.shape == (39,)
    assert (mol.orb_a.occupations[:13] == 1.0).all()
    assert (mol.orb_a.occupations[13:] == 0.0).all()
    assert mol.orb_a.energies[4] == -1.0206976
    assert mol.orb_a.energies[-1] == 2.0748685
    assert mol.orb_a.coeffs[0, 0] == 0.0000119
    assert mol.orb_a.coeffs[1, 0] == -0.0003216
    assert mol.orb_a.coeffs[-1, -1] == -0.1424743

    # Comparison of derived properties with ORCA output file

    # nuclear-nuclear repulsion
    assert abs(compute_nuclear_repulsion(mol.basis) - 81.87080034) < 1e-5

    # Check normalization
    olp = compute_overlap(mol.basis)
    mol.orb_a.check_normalization(olp, 1e-5)

    # Mulliken charges
    lf = DenseLinalgFactory(mol.basis.nbasis)
    dm_full = lf.create_two_index()
    dm_full = compute_1dm_hf(mol.orb_a)
    dm_full.iscale(2.0)
    charges = compute_mulliken_charges(mol.basis, lf, numbers, dm_full)
    expected_charges = np.array(
        [
            0.143316,
            -0.445861,
            0.173045,
            0.173021,
            0.024542,
            0.143066,
            0.143080,
            -0.754230,
            0.400021,
        ]
    )
    if os.path.isdir("./pybest_tmp"):
        import shutil

        shutil.rmtree("./pybest_tmp")
    assert abs(charges - expected_charges).max() < 1e-5

    # Compute HF energy
    assert abs(compute_hf_energy(mol) - -154.01322894) < 1e-4


def test_load_mkl_li2():
    fn_mkl = context.get_fn("test/li2.mkl")
    mol = IOData.from_file(fn_mkl)

    # Check normalization
    olp = compute_overlap(mol.basis)
    mol.orb_a.check_normalization(olp, 1e-5)
    mol.orb_b.check_normalization(olp, 1e-5)

    # Check charges
    lf = DenseLinalgFactory(mol.basis.nbasis)
    numbers = np.array([periodic[i].number for i in mol.atom])
    dm_full = lf.create_two_index()
    dm_full = compute_1dm_hf(mol.orb_a)
    dm_full.iadd(compute_1dm_hf(mol.orb_b))
    charges = compute_mulliken_charges(mol.basis, lf, numbers, dm_full)
    expected_charges = np.array([0.5, 0.5])
    if os.path.isdir("./pybest_tmp"):
        import shutil

        shutil.rmtree("./pybest_tmp")
    assert abs(charges - expected_charges).max() < 1e-5


def test_load_mkl_h2():
    fn_mkl = context.get_fn("test/h2_sto3g.mkl")
    mol = IOData.from_file(fn_mkl)
    olp = compute_overlap(mol.basis)
    mol.orb_a.check_normalization(olp, 1e-5)

    if os.path.isdir("./pybest_tmp"):
        import shutil

        shutil.rmtree("./pybest_tmp")
    # Compute HF energy
    assert abs(compute_hf_energy(mol) - -1.11750589) < 1e-4
