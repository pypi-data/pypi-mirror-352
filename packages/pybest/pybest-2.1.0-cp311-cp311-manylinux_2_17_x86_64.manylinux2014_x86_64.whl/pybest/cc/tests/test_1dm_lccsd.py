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

from pybest.cc import RpCCDLCCD, RpCCDLCCSD
from pybest.geminals.roopccd import ROOpCCD
from pybest.utility import fda_1order, numpy_seed

from .common import CCMolecule

test_data_d = [(RpCCDLCCD, "li2", "cc-pvdz")]
test_data_sd = [(RpCCDLCCSD, "li2", "cc-pvdz")]


@pytest.mark.slow
@pytest.mark.parametrize("cls,mol_f,basis", test_data_d)
def test_lccd_one_dm(cls, mol_f, basis, linalg_slow):
    """Check if LCCD method works correctly for 1 dm."""
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()
    orb = mol_.hf.orb_a
    # Do AP1roG optimization:
    geminal_solver = ROOpCCD(mol_.lf, mol_.occ_model)
    ap1rog = geminal_solver(
        mol_.one,
        mol_.two,
        orb,
        mol_.olp,
        e_core=mol_.external,
        checkpoint=-1,
        maxiter={"orbiter": 1000},
        sort=False,
    )

    lccd_solver = cls(mol_.lf, mol_.occ_model)
    # test is written for Krylov solvers as it checks for np.arrays
    lccd_solver(
        mol_.one,
        mol_.two,
        ap1rog,
        lambda_equations=True,
        solver="krylov",
    )

    one_mo_ = mol_.lf.create_two_index(label="one")
    one_mo_.assign_two_index_transform(mol_.one, orb)
    two_mo = []
    output = mol_.two.new()
    output.label = "two"
    output.assign_four_index_transform(
        mol_.two, orb, orb, orb, orb, "tensordot"
    )
    two_mo.append(output)

    def fun(x):
        one_mo = []
        one_mo.append(geminal_solver.lf.create_two_index())
        one_mo[0].assign(x.reshape(28, 28))
        one_mo[0].label = "one"
        # pCCD
        geminal_solver.clear_cache()
        geminal_solver.update_hamiltonian("scf", two_mo, one_mo)
        # eref from pCCD
        eref_pccd = geminal_solver.compute_total_energy()
        geminal_solver.compute_reference_energy()
        # LCCSD
        tmp = one_mo[0].new()
        tmp.assign_diagonal(1.0)
        mos = orb.new()
        mos.assign(tmp)
        lccd_solver.set_hamiltonian(one_mo[0], two_mo[0].copy(), mos)
        l2 = lccd_solver.l_amplitudes["l_2"].get_triu().ravel(order="C")
        coeff = l2
        t2 = lccd_solver.amplitudes["t_2"].get_triu().ravel(order="C")
        coefft = t2

        e_lccd = lccd_solver.calculate_energy(eref_pccd, coefft)
        lagrangian = e_lccd["e_corr"] + eref_pccd

        lagrangian += (np.dot(coeff, lccd_solver.vfunction(coefft)),)
        return lagrangian

    def fun_deriv(x):
        # LCCD
        lccd_solver_ = cls(mol_.lf, mol_.occ_model)
        lccd_solver_(
            mol_.one,
            mol_.two,
            ap1rog,
            lambda_equations=True,
            threshold_r=1e-8,
            solver="krylov",
        )
        # Get 1dm
        onedm_lccd = lccd_solver_.dm_1_pq
        onedm_lccd.iscale(2.0)

        # SUM
        a = np.zeros((28, 28))
        a[:] += onedm_lccd._array

        return a.ravel()

    x = one_mo_._array.ravel()
    with numpy_seed():
        dxs = []
        for _i in range(5):
            dxs_ = np.random.rand(28, 28) * 0.1
            dxs.append(((dxs_ + dxs_.T) / 2).ravel())
        dxs = np.array(dxs)
        fda_1order(fun, fun_deriv, x, dxs)


@pytest.mark.slow
@pytest.mark.parametrize("cls,mol_f,basis", test_data_sd)
def test_lccsd_one_dm(cls, mol_f, basis, linalg_slow):
    """Test 1dm lCCSD."""
    mol_ = CCMolecule(mol_f, basis, linalg_slow, charge=0, ncore=0)
    mol_.do_rhf()

    orb = mol_.hf.orb_a
    # Do AP1roG optimization:
    geminal_solver = ROOpCCD(mol_.lf, mol_.occ_model)
    ap1rog = geminal_solver(
        mol_.one,
        mol_.two,
        orb,
        mol_.olp,
        e_core=mol_.external,
        checkpoint=-1,
        maxiter={"orbiter": 1000},
    )

    lccsd_solver = cls(mol_.lf, mol_.occ_model)
    _ = lccsd_solver(
        mol_.one,
        mol_.two,
        ap1rog,
        lambda_equations=True,
        threshold_r=1e-8,
        solver="krylov",
    )

    one_mo_ = mol_.lf.create_two_index()
    one_mo_.assign_two_index_transform(mol_.one, orb)
    two_mo = []
    output = mol_.two.new()
    output.assign_four_index_transform(
        mol_.two, orb, orb, orb, orb, "tensordot"
    )
    output.label = "two"
    two_mo.append(output)

    def fun(x):
        one_mo = []
        one_mo.append(geminal_solver.lf.create_two_index())
        one_mo[0].assign(x.reshape(28, 28))
        one_mo[0].label = "one"
        # pCCD
        geminal_solver.clear_cache()
        geminal_solver.update_hamiltonian("scf", two_mo, one_mo)
        # eref from pCCD
        eref_pccd = geminal_solver.compute_total_energy()
        geminal_solver.compute_reference_energy()
        # LCCSD
        tmp = one_mo[0].new()
        tmp.assign_diagonal(1.0)
        mos = orb.new()
        mos.assign(tmp)
        lccsd_solver.set_hamiltonian(one_mo[0], two_mo[0].copy(), mos)

        l1 = lccsd_solver.l_amplitudes["l_1"].array.ravel(order="C")
        l2 = lccsd_solver.l_amplitudes["l_2"].get_triu().ravel(order="C")
        coeff = np.hstack((l1, l2))

        t1 = lccsd_solver.amplitudes["t_1"].array.ravel(order="C")
        t2 = lccsd_solver.amplitudes["t_2"].get_triu().ravel(order="C")
        coefft = np.hstack((t1, t2))

        e_lccsd = lccsd_solver.calculate_energy(eref_pccd, coefft)
        lagrangian = e_lccsd["e_corr"] + eref_pccd

        lagrangian += (np.dot(coeff, lccsd_solver.vfunction(coefft)),)
        return lagrangian

    def fun_deriv(x):
        # LCCSD
        lccsd_solver_ = cls(mol_.lf, mol_.occ_model)
        lccsd_solver_(
            mol_.one,
            mol_.two,
            ap1rog,
            lambda_equations=True,
            threshold_r=1e-8,
            solver="krylov",
        )
        # Get 1dm
        onedm_lccsd = lccsd_solver_.dm_1_pq
        onedm_lccsd.iscale(2.0)

        # SUM
        a = np.zeros((28, 28))
        a[:] += onedm_lccsd._array

        return a.ravel()

    x = one_mo_._array.ravel()
    with numpy_seed():
        dxs = []
        for _i in range(5):
            dxs_ = np.random.rand(28, 28) * 0.1
            dxs.append(((dxs_ + dxs_.T) / 2).ravel())
        dxs = np.array(dxs)
        fda_1order(fun, fun_deriv, x, dxs)
