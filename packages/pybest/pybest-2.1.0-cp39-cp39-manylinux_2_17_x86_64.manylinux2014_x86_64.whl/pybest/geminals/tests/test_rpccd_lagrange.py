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
from pybest.gbasis import (
    compute_eri,
    compute_kinetic,
    compute_nuclear,
    compute_nuclear_repulsion,
    compute_overlap,
    get_gobasis,
)
from pybest.geminals.rpccd import RpCCD
from pybest.linalg.dense.dense_linalg_factory import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel
from pybest.utility import fda_1order, numpy_seed, transform_integrals
from pybest.wrappers import RHF


@pytest.mark.slow
def test_pccd_lagrange():
    fn_xyz = context.get_fn("test/li2.xyz")
    basis = get_gobasis("cc-pvdz", fn_xyz, print_basis=False)
    lf = DenseLinalgFactory(basis.nbasis)
    occ_model = AufbauOccModel(basis, ncore=0)

    kin = compute_kinetic(basis)
    ne = compute_nuclear(basis)
    eri = compute_eri(basis)
    external = compute_nuclear_repulsion(basis)

    orb = lf.create_orbital()
    olp = compute_overlap(basis)

    hf = RHF(lf, occ_model)
    hf(kin, ne, eri, external, olp, orb)

    one = lf.create_two_index(basis.nbasis, label="one")
    one.iadd(kin)
    one.iadd(ne)

    def fun(x):
        coeff = geminal_solver.lagrange_matrix._array

        lagrangian = geminal_solver.compute_total_energy(x.reshape(3, 25))
        lagrangian += np.dot(
            coeff.ravel(order="C"),
            geminal_solver.vector_function_geminal(x.ravel(order="C")),
        )
        return lagrangian

    def fun_deriv(x):
        coeff = geminal_solver.lagrange_matrix._array.ravel(order="C")
        gmat = geminal_solver.lf.create_two_index(3, 25)
        gmat.assign(x)

        gradient = geminal_solver.vector_function_lagrange(coeff, gmat)
        return gradient.ravel(order="C")

    # Do pCCD optimization:
    geminal_solver = RpCCD(lf, occ_model)
    geminal_solver(one, eri, orb, olp, e_core=external)

    with numpy_seed():
        geminal_solver.lagrange_matrix.assign(np.random.rand(3, 25))
        x = geminal_solver.geminal_matrix._array.ravel(order="C")
        dxs = np.random.rand(200, 3 * 25) * (0.001)
        # transform AOs to MOs:
        ti = transform_integrals(one, eri, orb)
        one_mo = ti.one
        two_mo = ti.two
        # recalculate auxiliary matrices because they are deleted after call function exists
        geminal_solver.update_hamiltonian("scf", two_mo, one_mo)
        fda_1order(fun, fun_deriv, x, dxs)
