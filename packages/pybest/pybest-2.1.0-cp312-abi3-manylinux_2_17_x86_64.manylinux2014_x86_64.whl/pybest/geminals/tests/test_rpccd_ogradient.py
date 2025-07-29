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
from pybest.geminals.roopccd import ROOpCCD
from pybest.linalg.dense.dense_linalg_factory import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel
from pybest.utility import (
    fda_1order,
    numpy_seed,
    rotate_orbitals,
    transform_integrals,
)
from pybest.wrappers import RHF


@pytest.mark.slow
def test_pccd_gradient():
    fn_xyz = context.get_fn("test/c2.xyz")
    basis = get_gobasis("cc-pvdz", fn_xyz, print_basis=False)
    occ_model = AufbauOccModel(basis, ncore=0)
    lf = DenseLinalgFactory(basis.nbasis)
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

    # Do pCCD optimization:
    geminal_solver = ROOpCCD(lf, occ_model)
    geminal_solver(
        one,
        eri,
        orb,
        olp,
        e_core=external,
        checkpoint=-1,
        maxiter={"orbiter": 0},
    )

    def fun(x):
        rotation = geminal_solver.compute_rotation_matrix(x)
        orbs = orb.copy()
        rotate_orbitals(orbs, rotation)

        geminal_solver.clear_cache()
        ti = transform_integrals(one, eri, orbs)
        one_mo = ti.one[0]
        two_mo = ti.two[0]

        geminal_solver.update_hamiltonian("scf", two_mo, one_mo)

        coeff = geminal_solver.geminal_matrix._array
        lcoeff = geminal_solver.lagrange_matrix._array

        lagrangian = geminal_solver.compute_total_energy()
        lagrangian += np.dot(
            lcoeff.ravel(order="C"),
            geminal_solver.vector_function_geminal(coeff),
        )
        return lagrangian

    def fun_deriv(x):
        rotation = geminal_solver.compute_rotation_matrix(x)
        orbs = orb.copy()
        rotate_orbitals(orbs, rotation)

        geminal_solver.clear_cache()
        ti = transform_integrals(one, eri, orbs)
        one_mo = ti.one
        two_mo = ti.two

        geminal_solver.update_hamiltonian("scf", two_mo, one_mo)

        gradient = geminal_solver.compute_orbital_gradient(False)
        return gradient._array.ravel(order="C")

    x = np.zeros(28 * 27 // 2)
    with numpy_seed():
        dxs = np.random.rand(50, 28 * 27 // 2) * 0.0001
        fda_1order(fun, fun_deriv, x, dxs)
