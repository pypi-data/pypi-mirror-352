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
from pybest.featuredlists import OneBodyHamiltonian, TwoBodyHamiltonian
from pybest.gbasis import (
    compute_cholesky_eri,
    compute_eri,
    compute_kinetic,
    compute_nuclear,
    compute_nuclear_repulsion,
    compute_overlap,
    get_gobasis,
)
from pybest.linalg import (
    CholeskyFourIndex,
    CholeskyLinalgFactory,
    DenseLinalgFactory,
)
from pybest.linalg.base import PYBEST_CUPY_AVAIL
from pybest.occ_model import AufbauOccModel
from pybest.utility.orbitals import (
    print_ao_mo_coeffs,
    project_orbitals_frozen_core,
    split_core_active,
    transform_integrals,
)
from pybest.wrappers.hf import RHF


def prepare_hf(basis_str, mol, linalg):
    #
    # Run a simple HF calculation on the given IOData in the given basis
    #

    # Input structure
    basis = get_gobasis(basis_str, mol, print_basis=False)
    lf = linalg(basis.nbasis)
    occ_model = AufbauOccModel(basis)

    # Compute Gaussian integrals
    olp = compute_overlap(basis)
    kin = compute_kinetic(basis)
    na = compute_nuclear(basis)
    if isinstance(lf, CholeskyLinalgFactory):
        er = compute_cholesky_eri(basis, threshold=1e-8)
    else:
        er = compute_eri(basis)
    core = compute_nuclear_repulsion(basis)

    # Initial guess
    orb = lf.create_orbital()

    hf = RHF(lf, occ_model)
    hf_ = hf(kin, na, er, olp, orb, core)

    return hf_, kin, na, er, occ_model


def do_check(
    nocc, ncore, nactive, one_small, two_small, ecore, kin, na, er, hf
):
    #
    # Verify (parts of) the RHF energy using the active space integrals
    #
    # Get the integrals in the mo basis
    ti = transform_integrals(kin, na, er, hf, indextrans="tensordot")
    (one_mo,) = ti.one
    (two_mo,) = ti.two

    # Check the core energy
    ecore_check = hf.e_core + 2 * one_mo.trace(0, ncore, 0, ncore)
    ranges = {"end0": ncore, "end1": ncore, "end2": ncore, "end3": ncore}
    ecore_check += two_mo.contract(
        "abab->ab", out=None, factor=2.0, clear=True, **ranges, select="einsum"
    ).sum()
    ecore_check += two_mo.contract(
        "abba->ab",
        out=None,
        factor=-1.0,
        clear=True,
        **ranges,
        select="einsum",
    ).sum()
    assert abs(ecore - ecore_check) < 1e-10

    # Check the one-body energy of the active space
    nocc_small = nocc - ncore
    e_one_active = 2 * one_small.trace(0, nocc_small, 0, nocc_small)
    e_one_active_check = 2 * one_mo.trace(ncore, nocc, ncore, nocc)
    coxx = {"end0": ncore, "begin1": ncore, "end1": nocc}
    xxco = {"end2": ncore, "begin3": ncore, "end3": nocc}
    xxoc = {"begin2": ncore, "end2": nocc, "end3": ncore}
    e_one_active_check += (
        2
        * two_mo.contract(
            "abab->ab", out=None, factor=2.0, clear=True, **coxx, **xxco
        ).sum()
    )
    e_one_active_check += (
        2
        * two_mo.contract(
            "abba->ab", out=None, factor=-1.0, clear=True, **coxx, **xxoc
        ).sum()
    )
    assert abs(e_one_active - e_one_active_check) < 1e-10

    # Check the two-body energy of the active space
    ssss = {f"end{i}": nocc_small for i in range(4)}
    e_two_active = (
        two_small.contract(
            "abab->ab",
            out=None,
            factor=2.0,
            clear=True,
            **ssss,
            select="einsum",
        ).sum()
        + two_small.contract(
            "abba->ab",
            out=None,
            factor=-1.0,
            clear=True,
            **ssss,
            select="einsum",
        ).sum()
    )
    oooo = {
        **{f"begin{i}": ncore for i in range(4)},
        **{f"end{i}": nocc for i in range(4)},
    }
    e_two_active_check = (
        two_mo.contract(
            "abab->ab",
            out=None,
            factor=2.0,
            clear=True,
            **oooo,
            select="einsum",
        ).sum()
        + two_mo.contract(
            "abba->ab",
            out=None,
            factor=-1.0,
            clear=True,
            **oooo,
            select="einsum",
        ).sum()
    )
    assert abs(e_two_active - e_two_active_check) < 1e-10

    # Check the total RHF energy
    e_rhf = ecore + e_one_active + e_two_active
    assert abs(e_rhf - hf.e_tot) < 1e-10


def check_core_active(mol, basis_str, ncore, nactive, indextrans, linalg):
    #
    # Do the HF calculation
    #
    hf, kin, na, er, o_m = prepare_hf(basis_str, mol, linalg)
    # Decide how to occupy the orbitals
    assert o_m.ncore[0] + nactive > o_m.nocc[0]
    nocc = o_m.nocc[0]
    #
    # Get integrals for the active space
    #
    if isinstance(er, CholeskyFourIndex) and indextrans in [
        "opt_einsum",
        "einsum_naive",
    ]:
        pytest.skip(f"Cholesky does not support {indextrans}")
    cas = split_core_active(
        kin, na, er, hf, ncore=ncore, nactive=nactive, indextrans=indextrans
    )
    one_small = cas.one
    two_small = cas.two
    ecore = cas.e_core

    do_check(
        nocc, ncore, nactive, one_small, two_small, ecore, kin, na, er, hf
    )
    #
    # Get integrals for the active space, give twice external energy
    #
    cas = split_core_active(
        kin,
        na,
        er,
        hf,
        e_core=hf.e_core,
        ncore=ncore,
        nactive=nactive,
        indextrans=indextrans,
    )
    one_small = cas.one
    two_small = cas.two
    ecore = cas.e_core

    do_check(
        nocc, ncore, nactive, one_small, two_small, ecore, kin, na, er, hf
    )
    #
    # Get integrals for the active space, give only one e integrals
    #
    one = kin.copy()
    one.iadd(na)
    cas = split_core_active(
        one, er, hf, ncore=ncore, nactive=nactive, indextrans=indextrans
    )
    one_small = cas.one
    two_small = cas.two
    ecore = cas.e_core

    do_check(
        nocc, ncore, nactive, one_small, two_small, ecore, kin, na, er, hf
    )


def prepare_mol(
    basis_name, filen="test/h2o_ccdz.xyz", orbfilen="test/h2o_ccdz_hf.txt"
):
    fn_xyz = context.get_fn(filen)
    basis = get_gobasis(basis_name, fn_xyz, print_basis=False)

    lf = DenseLinalgFactory(basis.nbasis)
    fn_orb = context.get_fn(orbfilen)
    orb_ = np.fromfile(fn_orb, sep=",").reshape(basis.nbasis, basis.nbasis)
    orb_a = lf.create_orbital()
    orb_a._coeffs = orb_

    return basis, orb_a


test_cases = [
    # mol/atom, basis, ncore, nactive
    ("ne", "cc-pvdz", 0, 7),
    ("ne", "cc-pvdz", 2, 7),
    ("water", "cc-pvdz", 1, 8),
    ("2h-azirine", "6-31G", 3, 15),
]

if PYBEST_CUPY_AVAIL:
    test_tco = [
        ("cupy"),
        ("tensordot"),
        ("einsum"),
        pytest.param("opt_einsum", marks=pytest.mark.slow),
        pytest.param("einsum_naive", marks=pytest.mark.slow),
    ]
else:
    test_tco = [
        ("tensordot"),
        ("einsum"),
        pytest.param("opt_einsum", marks=pytest.mark.slow),
        pytest.param("einsum_naive", marks=pytest.mark.slow),
    ]


@pytest.mark.parametrize("mol,basis,ncore,nactive", test_cases)
@pytest.mark.parametrize("indextrans", test_tco)
def test_core_active(mol, basis, ncore, nactive, indextrans, linalg):
    mol = context.get_fn(f"test/{mol}.xyz")
    check_core_active(mol, basis, ncore, nactive, indextrans, linalg)


def test_print_ao_mo_coeff_full():
    basis, orb_a = prepare_mol("cc-pvdz")

    # Dry run
    print_ao_mo_coeffs(basis, orb_a)


def test_print_ao_mo_coeff_view():
    basis, orb_a = prepare_mol("cc-pvdz")

    # Dry runs
    print_ao_mo_coeffs(basis, orb_a, 1, 20)
    print_ao_mo_coeffs(basis, orb_a, 1, 1)
    print_ao_mo_coeffs(basis, orb_a, 11, 11)
    # first orbital index exceeds
    with pytest.raises(ValueError):
        print_ao_mo_coeffs(basis, orb_a, 26)
    # last orbital index exceeds
    with pytest.raises(ValueError):
        print_ao_mo_coeffs(basis, orb_a, end=26)
    # first orbital index larger than last
    with pytest.raises(ValueError):
        print_ao_mo_coeffs(basis, orb_a, 0)


def test_transform_integrals_labels():
    basis, orb_a = prepare_mol("cc-pvdz")
    kin = compute_kinetic(basis)
    ne = compute_nuclear(basis)
    eri = compute_eri(basis)
    transformed_integrals = transform_integrals(kin, ne, eri, orb_a)
    for one in transformed_integrals.one:
        assert one.label in OneBodyHamiltonian
        assert one.label == "one"
    for two in transformed_integrals.two:
        assert two.label in TwoBodyHamiltonian


@pytest.mark.parametrize("ncore", [0, 1, 2])
def test_project_orbitals_frozen_core(linalg, ncore):
    """Project orbitals from one to another solution.
    We only test for water in two different geometries.
    These are just dry runs. If something bad happens, the orbitals won't be
    normalized and test will fail. This is checked in the function itself.

    Args:
        linalg (LinalgFactory): either Dense or Cholesky
    """
    #
    # Do the HF calculation
    #
    water1 = prepare_hf("cc-pvdz", context.get_fn("test/water.xyz"), linalg)
    water2 = prepare_hf("cc-pvdz", context.get_fn("test/water_2.xyz"), linalg)
    olp0, orb0 = water1[0].olp, water1[0].orb_a
    olp1, orb1 = water2[0].olp, water2[0].orb_a
    # also runs project_orbitals (not tested here)
    project_orbitals_frozen_core(olp0, olp1, orb0, orb1, ncore=ncore)
