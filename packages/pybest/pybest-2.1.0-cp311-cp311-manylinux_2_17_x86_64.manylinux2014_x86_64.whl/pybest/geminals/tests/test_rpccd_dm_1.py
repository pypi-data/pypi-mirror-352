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
from pybest.utility import fda_1order, numpy_seed
from pybest.wrappers import RHF


@pytest.mark.slow
def test_pccd_one_dm():
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

    one = lf.create_two_index(basis.nbasis)
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

    one_mo_ = lf.create_two_index()
    one_mo_.assign_two_index_transform(one, orb)
    two_mo = []
    output = geminal_solver.lf.create_four_index()
    output.assign_four_index_transform(eri, orb, method="tensordot")
    two_mo.append(output)

    def fun(x):
        one_mo = []
        one_mo.append(geminal_solver.lf.create_two_index())
        one_mo[0].assign(x.reshape(28, 28))

        geminal_solver.clear_cache()
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
        one_mo = []
        one_mo.append(geminal_solver.lf.create_two_index())
        one_mo[0].assign(x.reshape(28, 28))
        geminal_solver.clear_cache()
        geminal_solver.update_hamiltonian("scf", two_mo, one_mo)

        guesst = geminal_solver.generate_guess(
            {"type": "random", "factor": -0.1}
        )
        # Optimize OpCCD wavefunction amplitudes:
        coeff = geminal_solver.solve_geminal(
            guesst, {"wfn": "krylov"}, 10e-12, 128
        )

        # Optimize OpCCD Lagrange multipliers (lambda equations):
        lcoeff = geminal_solver.solve_lagrange(
            guesst, {"lagrange": "krylov"}, 10e-12, 128
        )
        onebody1 = geminal_solver.lf.create_two_index(3, 25)
        onebody2 = geminal_solver.lf.create_two_index(3, 25)
        onebody1.assign(coeff)
        onebody2.assign(lcoeff)

        onedm = geminal_solver.lf.create_one_index()
        geminal_solver.compute_1dm(
            onedm, onebody1, onebody2, "one_dm_response", factor=2.0
        )
        a = np.zeros((28, 28))
        np.fill_diagonal(a, onedm._array.T)
        return a.ravel()

    x = one_mo_._array.ravel()
    with numpy_seed():
        dxs = np.random.rand(50, 28 * 28) * 0.00001
        fda_1order(fun, fun_deriv, x, dxs)
