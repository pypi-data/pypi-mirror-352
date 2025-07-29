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
# The RSF-CC sub-package has been originally written and updated by Aleksandra Leszczyk (see CHANGELOG)
# Its current version contains updates from the PyBEST developer team.
#
# 2023/24:
# This file has been updated by Emil Sujkowski

"""Unit tests for the RSF-CCD method."""

from __future__ import annotations

import math

import numpy as np
import pytest
from scipy.special import binom

from pybest.cc import RCCD, RLCCD, RfpCCD, RpCCDLCCD
from pybest.geminals.rpccd import RpCCD
from pybest.iodata import IOData
from pybest.linalg import (
    CholeskyFourIndex,
    CholeskyLinalgFactory,
    DenseFourIndex,
    DenseLinalgFactory,
    DenseOneIndex,
    DenseOrbital,
    DenseTwoIndex,
)
from pybest.occ_model import AufbauOccModel
from pybest.rsf_eom import RSFCCD, RSFLCCD, RSFfpCCD, RSFfpLCCD
from pybest.rsf_eom.eff_ham_ccd import EffectiveHamiltonianRCCD
from pybest.rsf_eom.rsf_ccd4 import RSFCCD4
from pybest.rsf_eom.tests.common import RSF_EOM_CCMolecule
from pybest.tests.common import load_reference_data
from pybest.units import electronvolt

# NOTE: Atom tests will be updated in the future. FUTURE IS NOW


def test_print_info(
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
    rsfccd_flavor: RSFCCD4,
) -> None:
    """Tests passes if no error is raised."""
    lf = linalg(2)
    occ_model = AufbauOccModel(lf, nel=2)
    eom = rsfccd_flavor(lf, occ_model)

    eom.print_info()


# rsfccd_flavor is pytest fixture that returns a ABC metaclass, that after inicialization turns into CCD flavor class
def test_ravel(
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
    rsfccd_flavor: RSFCCD4,
) -> None:
    """Check if ravel saves only symmetry-unique elements.
    The symmetry of tensor is r_iajb = r_jbia = -r_jaib = -r_ibja
    """
    nacto = 4
    nactv = 5
    # Prepare EOM instance
    lf = linalg(nacto + nactv)
    occ_model = AufbauOccModel(lf, nel=nacto * 2)
    eom = rsfccd_flavor(lf, occ_model)
    tensor = DenseFourIndex(nacto, nactv, nacto, nactv)
    # Due to symmetry of tensor, we set four values
    tensor.clear()
    tensor.set_element(1, 2, 3, 4, 1, symmetry=1)
    tensor.set_element(3, 4, 1, 2, 1, symmetry=1)
    tensor.set_element(3, 2, 1, 4, -1, symmetry=1)
    tensor.set_element(1, 4, 3, 2, -1, symmetry=1)
    raveled = eom.ravel(tensor)
    # Check basic properties
    assert isinstance(raveled, DenseOneIndex)
    assert raveled.shape == (binom(nacto, 2) * binom(nactv, 2),)
    # Check if we have one non-zero symmetry-unique value
    assert np.count_nonzero(raveled.array) == 1


def test_unravel(
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
    rsfccd_flavor: RSFCCD4,
) -> None:
    nacto = 4
    nactv = 8
    # Prepare EOM instance
    lf = linalg(nacto + nactv)
    occ_model = AufbauOccModel(lf, nel=nacto * 2)
    eom = rsfccd_flavor(lf, occ_model)
    # Ravel
    # dim = nacto* nactv * (nacto* nactv + 1) // 2
    dim = 496
    vector = DenseOneIndex(dim)
    vector.randomize()
    # Unravel and check if an array has expected features
    unraveled = eom.unravel(vector)
    assert not np.allclose(unraveled.array, np.zeros(unraveled.array.shape))
    assert unraveled.shape == (nacto, nactv, nacto, nactv)
    assert np.allclose(unraveled.array, unraveled.array.transpose(2, 3, 0, 1))
    assert np.allclose(unraveled.array, -unraveled.array.transpose(2, 1, 0, 3))
    assert np.allclose(unraveled.array, -unraveled.array.transpose(0, 3, 2, 1))


def test_ravel_unravel(
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
    rsfccd_flavor: RSFCCD4,
) -> None:
    """Check if object after raveling and unraveling is the same."""
    nacto = 2
    nactv = 3
    # Prepare matrix with symmetry r_iajb = r_jbia = - r_ibja
    matrix = DenseFourIndex(nacto, nactv, nacto, nactv)
    init_matrix = matrix.new()
    init_matrix.randomize()
    matrix.iadd(other=init_matrix)
    matrix.iadd_transpose((2, 3, 0, 1), other=init_matrix)
    matrix.iadd_transpose((0, 3, 2, 1), other=init_matrix, factor=-1)
    matrix.iadd_transpose((2, 1, 0, 3), other=init_matrix, factor=-1)
    ind1, ind2, ind3, ind4 = np.indices((nacto, nacto, nactv, nactv))
    matrix.assign(0.0, ind=[ind1, ind3, ind2, ind3])
    matrix.assign(0.0, ind=[ind1, ind3, ind1, ind4])
    assert not np.allclose(matrix.array, np.zeros(matrix.array.shape))
    assert np.allclose(matrix.array, matrix.array.transpose(2, 3, 0, 1))
    assert np.allclose(matrix.array, -matrix.array.transpose(0, 3, 2, 1))
    assert np.allclose(matrix.array, -matrix.array.transpose(2, 1, 0, 3))
    # Prepare EOM instance
    lf = linalg(nacto + nactv)
    occ_model = AufbauOccModel(lf, nel=nacto * 2)
    eom = rsfccd_flavor(lf, occ_model)
    # Ravel
    vector = eom.ravel(matrix)
    assert not np.allclose(vector.array, np.zeros(vector.array.shape))
    # Unravel and compare with original matrix
    unraveled = eom.unravel(vector)
    assert not np.allclose(unraveled.array, np.zeros(unraveled.array.shape))
    assert np.allclose(unraveled.array, unraveled.array.transpose(2, 3, 0, 1))
    assert np.allclose(unraveled.array, -unraveled.array.transpose(2, 1, 0, 3))
    assert np.allclose(unraveled.array, -unraveled.array.transpose(0, 3, 2, 1))
    assert np.allclose(matrix.array, unraveled.array)
    # Ravel once again
    raveled = eom.ravel(unraveled)
    assert vector.shape == raveled.shape
    assert not np.allclose(raveled.array, np.zeros(raveled.array.shape))
    assert np.allclose(vector.array, raveled.array)


def test_unravel_ravel(
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
    rsfccd_flavor: RSFCCD4,
) -> None:
    """Check if object after raveling and unraveling is the same."""
    nacto = 2
    nactv = 3
    # Prepare EOM instance
    lf = linalg(nacto + nactv)
    occ_model = AufbauOccModel(lf, nel=nacto * 2)
    eom = rsfccd_flavor(lf, occ_model)
    # Ravel
    vector = DenseOneIndex(eom.dimension)
    vector.randomize()
    assert not np.allclose(vector.array, np.zeros(vector.array.shape))
    # Unravel and compare with original matrix
    unraveled = eom.unravel(vector)
    assert not np.allclose(unraveled.array, np.zeros(unraveled.array.shape))
    assert np.allclose(unraveled.array, unraveled.array.transpose(2, 3, 0, 1))
    assert np.allclose(unraveled.array, -unraveled.array.transpose(2, 1, 0, 3))
    assert np.allclose(unraveled.array, -unraveled.array.transpose(0, 3, 2, 1))
    # Ravel once again
    raveled = eom.ravel(unraveled)
    assert vector.shape == raveled.shape
    assert not np.allclose(raveled.array, np.zeros(raveled.array.shape))
    assert np.allclose(vector.array, raveled.array)


def test_compute_h_diag(
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
    rsfccd_flavor: RSFCCD4,
) -> None:
    """Check if a method returns non-zero OneIndex object."""
    # Prepare dummy input data
    lf = linalg(5)
    occ_model = AufbauOccModel(lf, nel=2 * 2)
    one = DenseTwoIndex(5, 5, label="one")

    if linalg == CholeskyLinalgFactory:
        two = CholeskyFourIndex(5, 10, label="eri")
    else:
        two = DenseFourIndex(5, 5, 5, 5, label="eri")

    orbs = DenseOrbital(5, 5)
    t_2 = DenseFourIndex(2, 3, 2, 3)
    for obj in [one, two, orbs, t_2]:
        obj.randomize()
    rcc_iodata = IOData(
        t_2=t_2,
        e_ref=1.0,
        nocc=2,
        nacto=2,
        nvirt=3,
        nactv=3,
        ncore=0,
        occ_model=occ_model,
    )
    # Try to use method with minimum requirements (cache)
    eom = rsfccd_flavor(lf, occ_model)
    eom.rcc_iodata = rcc_iodata
    eom.cache = EffectiveHamiltonianRCCD(one, two, orbs, rcc_iodata).cache
    h_diag = eom.compute_h_diag()
    assert isinstance(h_diag, DenseOneIndex)
    assert not np.allclose(h_diag.array, np.zeros(h_diag.shape))


def test_build_guess_vectors(
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
    rsfccd_flavor: RSFCCD4,
) -> None:
    """Check if the method returns
    1) a list of non-zero OneIndex vectors and
    2) a number of them.
    """
    # Prepare dummy input data
    nacto = 3
    nactv = 7
    nbasis = nacto + nactv
    lf = linalg(nbasis)
    occ_model = AufbauOccModel(lf, nel=nacto * 2)
    one = DenseTwoIndex(nbasis, nbasis, label="one")

    if linalg == CholeskyLinalgFactory:
        two = CholeskyFourIndex(nbasis, nbasis * 2, label="eri")
    else:
        two = DenseFourIndex(nbasis, nbasis, nbasis, nbasis, label="eri")

    orbs = DenseOrbital(nbasis, nbasis)
    t_2 = DenseFourIndex(nacto, nactv, nacto, nactv)
    for obj in [one, two, orbs, t_2]:
        obj.randomize()
    rcc_iodata = IOData(
        t_2=t_2,
        e_ref=1.0,
        nocc=nacto,
        nacto=nacto,
        nvirt=nactv,
        nactv=nactv,
        ncore=0,
        occ_model=occ_model,
    )
    # Try to use method with minimum requirements (cache, h_diag)
    eom = rsfccd_flavor(lf, occ_model)
    eom.rcc_iodata = rcc_iodata
    eom.cache = EffectiveHamiltonianRCCD(one, two, orbs, rcc_iodata).cache
    h_diag = eom.compute_h_diag()
    bvectors, number = eom.build_guess_vectors(4, False, h_diag)
    assert number == 4
    assert isinstance(bvectors[0], DenseOneIndex)
    assert isinstance(bvectors[3], DenseOneIndex)
    assert not np.allclose(bvectors[0].array, np.zeros(bvectors[0].shape))
    assert not np.allclose(bvectors[1].array, np.zeros(bvectors[0].shape))
    assert not np.allclose(bvectors[2].array, np.zeros(bvectors[0].shape))
    assert not np.allclose(bvectors[3].array, np.zeros(bvectors[0].shape))
    # Check if bvector can be expanded
    bvec_0 = eom.unravel(bvectors[0])
    assert not np.allclose(bvec_0.array, np.zeros(bvec_0.array.shape))
    assert np.allclose(bvec_0.array, bvec_0.array.transpose(2, 3, 0, 1))
    assert np.allclose(bvec_0.array, -bvec_0.array.transpose(2, 1, 0, 3))
    assert np.allclose(bvec_0.array, -bvec_0.array.transpose(0, 3, 2, 1))
    bvec_0_raveled = eom.ravel(bvec_0)
    assert np.allclose(bvectors[0].array, bvec_0_raveled.array)


def test_build_subspace_hamiltonian(
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
    rsfccd_flavor: RSFCCD4,
) -> None:
    """Check if method returns a non-zero DenseOneIndex instance."""
    # Prepare dummy input data
    lf = linalg(5)
    occ_model = AufbauOccModel(lf, nel=2 * 2)
    one = DenseTwoIndex(5, 5, label="one")
    if linalg == CholeskyLinalgFactory:
        two = CholeskyFourIndex(5, 10, label="eri")
    else:
        two = DenseFourIndex(5, 5, 5, 5, label="eri")
    orbs = DenseOrbital(5, 5)
    t_2 = DenseFourIndex(2, 3, 2, 3)
    for obj in [one, two, orbs, t_2]:
        obj.randomize()
    rcc_iodata = IOData(
        t_2=t_2,
        e_ref=1.0,
        nocc=2,
        nacto=2,
        nvirt=3,
        nactv=3,
        ncore=0,
        occ_model=occ_model,
    )
    # Try to use method with minimum requirements (cache, h_diag)
    eom = rsfccd_flavor(lf, occ_model)
    eom.rcc_iodata = rcc_iodata
    eom.cache = EffectiveHamiltonianRCCD(one, two, orbs, rcc_iodata).cache
    assert not np.allclose(eom.cache.load("I_VV").array, np.zeros((3, 3)))
    h_diag = eom.compute_h_diag()
    assert not np.allclose(h_diag.array, np.zeros(h_diag.array.shape))
    vectors, _number = eom.build_guess_vectors(4, False, h_diag)
    assert not np.allclose(vectors[0].array, np.zeros(vectors[0].array.shape))
    sigma = eom.build_subspace_hamiltonian(vectors[0], h_diag)
    assert isinstance(sigma, DenseOneIndex)
    assert not np.allclose(sigma.array, np.zeros(sigma.shape))


testdata_flavors = [
    ([RCCD], RSFCCD, {"solver": "pbqn"}),
    ([RLCCD], RSFLCCD, {"solver": "krylov"}),
    ([RpCCD, RfpCCD], RSFfpCCD, {"solver": "krylov", "threshold": 1e-7}),
    ([RpCCD, RpCCDLCCD], RSFfpLCCD, {"solver": "krylov"}),
]
testdata_rsf_xccd = [
    (
        "c",
        "augcc-pvdz",
        {"ncore": 0, "charge": 0, "nguessv": 10, "nroot": 1, "alpha": 4},
    ),
    (
        "si",
        "cc-pvdz",
        {"ncore": 0, "charge": 0, "nguessv": 10, "nroot": 3, "alpha": 4},
    ),
]


@pytest.mark.parametrize(
    "cls,rsf_cls,flavor_kwargs",
    testdata_flavors,
    ids=["RCCD", "RLCCD", "RpCCD_RfpCCD", "RpCCD_RpCCDLCCD"],
)
@pytest.mark.parametrize("mol_f,basis,kwargs", testdata_rsf_xccd)
def test_rsf_xccd_ms2(
    cls: list[RCCD],
    rsf_cls: RSFCCD,
    flavor_kwargs: dict[str, str | float],
    mol_f: str,
    basis: str,
    kwargs: dict[str, int],
    linalg_slow: DenseLinalgFactory,
):
    """Test energies of RSFRCCSD flavors"""
    threshold = flavor_kwargs.get("threshold", 1e-6)
    solver = flavor_kwargs.get("solver")
    nguessv = kwargs.get("nguessv")
    nroot = kwargs.get("nroot")
    alpha = kwargs.get("alpha")
    ncore = kwargs.get("ncore")
    charge = kwargs.get("charge")
    required_keys = ["e_tot", f"e_ee_{alpha}"]

    method = (
        cls[-1].__name__
        if len(cls) == 1
        else cls[0].__name__ + "-" + cls[1].__name__
    )
    expected = load_reference_data(
        method,
        mol_f,
        basis,
        charge,
        ncore=ncore,
        nroot=nroot,
        nguessv=nguessv,
        required_keys=required_keys,
    )

    # Prepare molecule
    mol_ = RSF_EOM_CCMolecule(
        mol_f, basis, linalg_slow, charge=charge, ncore=ncore
    )
    # Do RHF optimization:
    mol_.do_rhf()
    # Do CC optimization:
    mol_.do_rxcc(cls, solver, threshold)

    assert (
        abs(mol_.cc.e_tot - expected["e_tot"]) < 1e-5
    ), f"Total energy mismatch: expected {expected['e_tot']}, got {mol_.cc.e_tot}"

    # Do RSF-CC optimization:
    mol_.do_rsf_cc(rsf_cls, alpha, nroot, nguessv)

    # State 2s^1 2p^3
    energy_eom_ms2 = mol_.rsf_cc.e_ee_4[0] * (1 / electronvolt)

    assert not math.isclose(
        energy_eom_ms2, mol_.rsf_cc.e_ee_4[0]
    ), f"Excitation energy values too close: e_ee * (1 / {electronvolt}) = {energy_eom_ms2}, e_ee = {mol_.rsf_cc.e_ee_4[0]}"

    # Check if the excitation energy roughly matches experimental results
    assert math.isclose(
        expected["e_ee_4"],
        energy_eom_ms2,
        abs_tol=1e-5 if RpCCD not in cls else 1e-3,
    ), f"Excitation energy mismatch: experimental results {expected['e_ee_4']}, got {energy_eom_ms2}"
