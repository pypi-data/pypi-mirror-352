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
# 03/2025:
# This file has been modified by Somayeh Ahmadkhani and Lena Szczuczko

import numpy as np
import pytest

from pybest.cc import RLCCD, RLCCSD, RpCCDLCCD, RpCCDLCCSD
from pybest.geminals.roopccd import ROOpCCD
from pybest.utility import fda_1order, numpy_seed

from .common import CCMolecule

scalingfactor = 1e-6

#
# NOTE: all tests are written for the Krylov scipy.root solver as we access
# np.arrays directly
#

test_data12 = [("c2-12", "cc-pvdz")]
test_data30 = [("c2_30", "cc-pvdz")]


@pytest.mark.slow
@pytest.mark.parametrize("cls", [(RLCCD)])
@pytest.mark.parametrize("mol_f,basis", test_data12)
def test_lccd_rhf_lambda(cls, mol_f, basis, linalg_slow):
    """Perform a finite difference test of the Lambda equations. The finite
    difference approximation of sum function ``fun`` is compared to the analytical
    derivative defined in ``fun_deriv``.
    """
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()

    lccd_solver = cls(mol_.lf, mol_.occ_model)
    with numpy_seed():
        lccd_solver(
            mol_.one,
            mol_.two,
            mol_.hf,
            lambda_equations=True,
            threshold_r=1e-6,
            solver="krylov",
        )
        lccd_solver.l_amplitudes["l_2"].assign(np.random.rand(6, 22, 6, 22))
        # Symmetrize
        lccd_solver.l_amplitudes["l_2"].iadd_transpose((2, 3, 0, 1))
        lccd_solver.l_amplitudes["l_2"].iscale(0.5)
        xt2 = lccd_solver.amplitudes["t_2"].get_triu().ravel(order="C")

        def fun(x):
            l2 = lccd_solver.l_amplitudes["l_2"].get_triu().ravel(order="C")
            x_ = lccd_solver.unravel(x)

            lagrangian = lccd_solver.calculate_energy(mol_.hf.e_tot, **x_)[
                "e_tot"
            ]
            # L_2 = 0.5 sum_{ijab} L_ijab <iajb| (H e^T)_C |0>
            lagrangian += np.dot(
                l2 * 0.5, lccd_solver.vfunction(x.ravel(order="C"))
            )
            return lagrangian

        def fun_deriv(x):
            l2 = lccd_solver.l_amplitudes["l_2"].get_triu().ravel(order="C")

            gradient = lccd_solver.vfunction_l(l2)
            return gradient

        x = xt2
        dx2 = []
        for _i in range(5):
            tmp = np.random.rand(6, 22, 6, 22) * scalingfactor
            tmp[:] = tmp + tmp.transpose((2, 3, 0, 1))
            indtriu = np.triu_indices(6 * 22)
            tmp = tmp.reshape(6 * 22, 6 * 22)[indtriu]
            dx2.append(tmp.ravel())
        dx2 = np.array(dx2)
        dxs = dx2
        # recalculate auxiliary matrices because they are deleted after call function exists
        lccd_solver.set_hamiltonian(mol_.one, mol_.two, mol_.hf.orb_a)
        fda_1order(fun, fun_deriv, x, dxs)


@pytest.mark.slow
@pytest.mark.parametrize("cls", [(RLCCSD)])
@pytest.mark.parametrize("mol_f,basis", test_data12)
def test_lccsd_rhf_lambda(
    cls,
    mol_f,
    basis,
    linalg_slow,
):
    """Perform a finite difference test of the Lambda equations. The finite
    difference approximation of sum function ``fun`` is compared to the analytical
    derivative defined in ``fun_deriv``.
    """
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()

    lccsd_solver = cls(mol_.lf, mol_.occ_model)
    with numpy_seed():
        lccsd_solver(
            mol_.one,
            mol_.two,
            mol_.hf,
            lambda_equations=True,
            solver="krylov",
        )
        lccsd_solver.l_amplitudes["l_1"].assign(np.random.rand(6, 22))
        lccsd_solver.l_amplitudes["l_2"].assign(np.random.rand(6, 22, 6, 22))
        # Symmetrize
        lccsd_solver.l_amplitudes["l_2"].iadd_transpose((2, 3, 0, 1))
        lccsd_solver.l_amplitudes["l_2"].iscale(0.5)
        xt1 = lccsd_solver.amplitudes["t_1"]._array.ravel(order="C")
        xt2 = lccsd_solver.amplitudes["t_2"].get_triu().ravel(order="C")

        def fun(x):
            l1 = lccsd_solver.l_amplitudes["l_1"]._array.ravel(order="C")
            l2 = lccsd_solver.l_amplitudes["l_2"].get_triu().ravel(order="C")
            coeff = np.hstack((l1, l2))
            x_ = lccsd_solver.unravel(coeff)

            lagrangian = lccsd_solver.calculate_energy(mol_.hf.e_tot, **x_)[
                "e_tot"
            ]

            # L_2 = 0.5 sum_{ijab} L_ijab <iajb| (H e^T)_C |0>
            coeff = np.hstack((l1, l2 * 0.5))
            lagrangian += np.dot(
                coeff, lccsd_solver.vfunction(x.ravel(order="C"))
            )
            return lagrangian

        def fun_deriv(x):
            l1 = lccsd_solver.l_amplitudes["l_1"]._array.ravel(order="C")
            l2 = lccsd_solver.l_amplitudes["l_2"].get_triu().ravel(order="C")
            coeff = np.hstack((l1, l2)).ravel(order="C")
            t1 = lccsd_solver.lf.create_two_index(6, 22)
            t2 = lccsd_solver.denself.create_four_index(6, 22, 6, 22)
            t1.assign(x[: 6 * 22])
            t2.assign_triu(x[6 * 22 :])

            gradient = lccsd_solver.vfunction_l(coeff)
            return gradient.ravel(order="C")

        x = np.hstack((xt1, xt2))
        dx1 = np.random.rand(5, (6 * 22)) * scalingfactor
        dx2 = []
        for _i in range(5):
            tmp = np.random.rand(6, 22, 6, 22) * scalingfactor
            tmp[:] = tmp + tmp.transpose((2, 3, 0, 1))
            indtriu = np.triu_indices(6 * 22)
            tmp = tmp.reshape(6 * 22, 6 * 22)[indtriu]
            dx2.append(tmp.ravel())
        dx2 = np.array(dx2)
        dxs = np.hstack((dx1, dx2))
        # recalculate auxiliary matrices because they are deleted after call function exists
        lccsd_solver.set_hamiltonian(mol_.one, mol_.two, mol_.hf.orb_a)
        fda_1order(fun, fun_deriv, x, dxs)


@pytest.mark.slow
@pytest.mark.parametrize("geminal,cls", [(ROOpCCD, RpCCDLCCD)])
@pytest.mark.parametrize("mol_f,basis", test_data30)
def test_lccd_lambda(geminal, cls, mol_f, basis, linalg_slow):
    """Perform a finite difference test of the Lambda equations. The finite
    difference approximation of sum function ``fun`` is compared to the analytical
    derivative defined in ``fun_deriv``.
    """
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()
    # Do AP1roG optimization:
    geminal_solver = geminal(mol_.lf, mol_.occ_model)
    lccd_solver = cls(mol_.lf, mol_.occ_model)
    with numpy_seed():
        ap1rog = geminal_solver(
            mol_.one,
            mol_.two,
            mol_.hf.orb_a,
            mol_.olp,
            e_core=mol_.external,
            checkpoint=-1,
            maxiter={"orbiter": 0},
        )
        _ = lccd_solver(
            mol_.one,
            mol_.two,
            ap1rog,
            lambda_equations=True,
            solver="krylov",
        )
        lccd_solver.l_amplitudes["l_2"].assign(np.random.rand(6, 22, 6, 22))
        # Symmetrize
        lccd_solver.l_amplitudes["l_2"].iadd_transpose((2, 3, 0, 1))
        lccd_solver.l_amplitudes["l_2"].iscale(0.5)
        xt2 = lccd_solver.amplitudes["t_2"].get_triu().ravel(order="C")
        ind1, ind2 = np.indices((6, 22))
        indices = [ind1, ind2, ind1, ind2]
        # Get rid of pairs
        lccd_solver.l_amplitudes["l_2"].assign(0.0, indices)

        def fun(x):
            l2 = lccd_solver.l_amplitudes["l_2"].get_triu().ravel(order="C")
            x_ = lccd_solver.unravel(x)

            lagrangian = lccd_solver.calculate_energy(lccd_solver.e_ref, **x_)[
                "e_tot"
            ]

            # L_2 = 0.5 sum_{ijab} L_ijab <iajb| (H e^T)_C |0>
            lagrangian += np.dot(
                l2 * 0.5,
                lccd_solver.vfunction(x.ravel(order="C")),
            )
            return lagrangian

        def fun_deriv(x):
            l2 = lccd_solver.l_amplitudes["l_2"].get_triu().ravel(order="C")

            gradient = lccd_solver.vfunction_l(l2)
            return gradient.ravel(order="C")

        x = xt2
        dx2 = []
        for _i in range(5):
            tmp = np.random.rand(6, 22, 6, 22) * scalingfactor
            tmp[:] = tmp + tmp.transpose((2, 3, 0, 1))
            tmp[tuple(indices)] = 0.0
            indtriu = np.triu_indices(6 * 22)
            tmp = tmp.reshape(6 * 22, 6 * 22)[indtriu]
            dx2.append(tmp.ravel())
        dx2 = np.array(dx2)
        dxs = dx2
        # recalculate auxiliary matrices because they are deleted after call function exists
        lccd_solver.set_hamiltonian(mol_.one, mol_.two, mol_.hf.orb_a)
        fda_1order(fun, fun_deriv, x, dxs)


@pytest.mark.slow
@pytest.mark.parametrize("geminal,cls", [(ROOpCCD, RpCCDLCCSD)])
@pytest.mark.parametrize("mol_f,basis", test_data30)
def test_lccsd_lambda(geminal, cls, mol_f, basis, linalg_slow):
    """Perform a finite difference test of the Lambda equations. The finite
    difference approximation of sum function ``fun`` is compared to the analytical
    derivative defined in ``fun_deriv``.
    """
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()
    mol_.modify_orb("test/ap1rog_c2_30.txt")
    # Do AP1roG optimization:
    geminal_solver = geminal(mol_.lf, mol_.occ_model)
    lccsd_solver = cls(mol_.lf, mol_.occ_model)
    with numpy_seed():
        ap1rog = geminal_solver(
            mol_.one,
            mol_.two,
            mol_.orb_a,
            mol_.olp,
            e_core=mol_.external,
            checkpoint=-1,
            maxiter={"orbiter": 0},
        )
        _ = lccsd_solver(
            mol_.one,
            mol_.two,
            ap1rog,
            lambda_equations=True,
            threshold_r=1e-6,
            solver="krylov",
        )
        lccsd_solver.l_amplitudes["l_1"].assign(np.random.rand(6, 22))
        lccsd_solver.l_amplitudes["l_2"].assign(np.random.rand(6, 22, 6, 22))
        # Symmetrize
        lccsd_solver.l_amplitudes["l_2"].iadd_transpose((2, 3, 0, 1))
        lccsd_solver.l_amplitudes["l_2"].iscale(0.5)
        xt1 = lccsd_solver.amplitudes["t_1"]._array.ravel(order="C")
        xt2 = lccsd_solver.amplitudes["t_2"].get_triu().ravel(order="C")
        ind1, ind2 = np.indices((6, 22))
        indices = [ind1, ind2, ind1, ind2]
        # Get rid of pairs
        lccsd_solver.l_amplitudes["l_2"].assign(0.0, indices)

        def fun(x):
            l1 = lccsd_solver.l_amplitudes["l_1"]._array.ravel(order="C")
            l2 = lccsd_solver.l_amplitudes["l_2"].get_triu().ravel(order="C")
            coeff = np.hstack((l1, l2))
            x_ = lccsd_solver.unravel(coeff)

            lagrangian = lccsd_solver.calculate_energy(
                lccsd_solver.e_ref, **x_
            )["e_tot"]

            # L_2 = 0.5 sum_{ijab} L_ijab <iajb| (H e^T)_C |0>
            coeff = np.hstack((l1, l2 * 0.5))
            lagrangian += np.dot(
                coeff, lccsd_solver.vfunction(x.ravel(order="C"))
            )
            return lagrangian

        def fun_deriv(x):
            l1 = lccsd_solver.l_amplitudes["l_1"]._array.ravel(order="C")
            l2 = lccsd_solver.l_amplitudes["l_2"].get_triu().ravel(order="C")
            coeff = np.hstack((l1, l2)).ravel(order="C")
            t1 = lccsd_solver.lf.create_two_index(6, 22)
            t2 = lccsd_solver.denself.create_four_index(6, 22, 6, 22)
            t1.assign(x[: 6 * 22])
            t2.assign_triu(x[6 * 22 :])

            gradient = lccsd_solver.vfunction_l(coeff)
            return gradient.ravel(order="C")

        x = np.hstack((xt1, xt2))
        dx1 = np.random.rand(5, (6 * 22)) * scalingfactor
        dx2 = []
        for _i in range(5):
            tmp = np.random.rand(6, 22, 6, 22) * scalingfactor
            tmp[:] = tmp + tmp.transpose((2, 3, 0, 1))
            tmp[tuple(indices)] = 0.0
            indtriu = np.triu_indices(6 * 22)
            tmp = tmp.reshape(6 * 22, 6 * 22)[indtriu]
            dx2.append(tmp.ravel())
        dx2 = np.array(dx2)
        dxs = np.hstack((dx1, dx2))
        # recalculate auxiliary matrices because they are deleted after call function exists
        lccsd_solver.set_hamiltonian(mol_.one, mol_.two, mol_.hf.orb_a)
        fda_1order(fun, fun_deriv, x, dxs)
