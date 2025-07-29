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
from pybest.gbasis import Basis, compute_eri, get_gobasis


def test_eri():
    fn = context.get_fn("test/h2o_ccdz.xyz")
    obs = get_gobasis("cc-pVDZ", fn, print_basis=False)

    eri = compute_eri(obs)

    assert eri.nbasis == eri.nbasis1 == eri.nbasis2 == eri.nbasis3 == 24

    fnints = context.get_fn("test/ints_h2o_eri.txt")
    ref = np.fromfile(fnints, sep=",").reshape(24, 24, 24, 24)

    assert np.allclose(eri._array, ref)


def test_eri_symmetry():
    fn = context.get_fn("test/h2o.xyz")
    obs1 = get_gobasis("cc-pvdz", fn, print_basis=False)
    obs2 = Basis(obs1)
    eri1 = compute_eri(obs1, symmetry=False)
    eri2 = compute_eri(obs1, symmetry=True)
    # identical to eri1
    eri3 = compute_eri(obs1, obs2, symmetry=True)
    eri4 = compute_eri(obs1, basis2=obs2, symmetry=True)
    eri5 = compute_eri(obs1, basis3=obs2, symmetry=True)

    assert np.allclose(eri1._array, eri2._array, 1e-8, 1e-13)
    assert eri1.is_symmetric()
    assert eri2.is_symmetric()
    assert np.allclose(eri1._array, eri3._array, 1e-10, 1e-14)
    assert np.allclose(eri1._array, eri4._array, 1e-10, 1e-14)
    assert np.allclose(eri1._array, eri5._array, 1e-10, 1e-14)
