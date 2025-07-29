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
#
# 2025: Added support for the molecule testing framework (Julia Szczuczko).

import numpy as np
import pytest

from pybest.ea_eom.tests.common import EA_EOMMolecule, flatten_list
from pybest.ea_eom.xea_pccd import REApCCD
from pybest.exceptions import ArgumentError
from pybest.geminals import ROOpCCD, RpCCD
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel
from pybest.tests.common import load_reference_data

#
# Test dimension (only spin dependent implementation)
#

test_data_dim = [
    # nbasis, nocc, n_particle_operator, ncore, alpha, dimension
    (10, 4, 1, 0, {"alpha": 1}, 6),
    (10, 3, 1, 0, {"alpha": 1}, 7),
    (10, 8, 1, 0, {"alpha": 1}, 2),
    (10, 4, 2, 0, {"alpha": 1}, 210),
    (10, 3, 2, 0, {"alpha": 1}, 217),
    (10, 8, 2, 0, {"alpha": 1}, 42),
    (10, 4, 1, 1, {"alpha": 1}, 6),
    (10, 3, 1, 1, {"alpha": 1}, 7),
    (10, 8, 1, 1, {"alpha": 1}, 2),
    (10, 4, 2, 1, {"alpha": 1}, 159),
    (10, 3, 2, 1, {"alpha": 1}, 147),
    (10, 8, 2, 1, {"alpha": 1}, 37),
    (10, 8, 2, 3, {"alpha": 1}, 27),
    (10, 4, 2, 0, {"alpha": 3}, 60),
    (10, 3, 2, 0, {"alpha": 3}, 63),
    (10, 8, 2, 0, {"alpha": 3}, 8),
    (10, 4, 2, 1, {"alpha": 3}, 45),
    (10, 3, 2, 1, {"alpha": 3}, 42),
    (10, 8, 2, 1, {"alpha": 3}, 7),
    (10, 8, 2, 3, {"alpha": 3}, 5),
]


@pytest.mark.parametrize(
    "nbasis,nocc,n_p,ncore,kwargs,expected", test_data_dim
)
def test_ea_pccd_dimension(nbasis, nocc, n_p, ncore, kwargs, expected):
    """Test number of unknowns (CI coefficients) for various parameter sets
    (alpha, ncore, nocc)
    """
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=nocc * 2, ncore=ncore)
    # Create EApCCD instance
    eapccd = REApCCD(lf, occ_model, **kwargs)
    # assign to private attribute
    eapccd._n_particle_operator = n_p

    assert expected == eapccd.dimension


#
# Test dimension (only spin dependent implementation)
#

test_unmask_error = [
    # no t_p
    ({"alpha": 1}, (), ArgumentError),
    # no olp
    ({"alpha": 1}, ("t_p",), ArgumentError),
    # no orb
    ({"alpha": 1}, ("t_p", "olp"), ArgumentError),
    # no two
    ({"alpha": 1}, ("t_p", "olp", "orb"), UnboundLocalError),
]


@pytest.mark.parametrize("kwargs,args,raised_error", test_unmask_error)
def test_ea_pccd_unmask_raise_error(boron, kwargs, args, raised_error):
    """Test unmask_arg function by passing insufficient arguments"""
    # Create EApCCD instance
    eapccd = REApCCD(boron.lf, boron.occ_model, **kwargs)

    # resolve a incomplete list of arguments
    wrong_args = flatten_list(boron, *args)
    with pytest.raises(raised_error):
        assert eapccd.unmask_args(*wrong_args)


test_unmask = [
    # everything fine
    (
        {"alpha": 1},
        ("t_p", "olp", "orb", "hamiltonian"),
        ("one", "two", "orb"),
    ),
    (
        {"alpha": 3},
        ("t_p", "olp", "orb", "hamiltonian"),
        ("one", "two", "orb"),
    ),
]


@pytest.mark.parametrize("kwargs,args,expected", test_unmask)
def test_ea_pccd_unmask(boron, kwargs, args, expected):
    """Test unmask_arg function by passing proper arguments"""
    # Create EApCCD instance
    eapccd = REApCCD(boron.lf, boron.occ_model, **kwargs)

    # resolve arguments and collect them in a flattened list
    flatten_args = flatten_list(boron, *args)
    # we cannot test the one-electron integrals as unmaks_args creates a new
    # element
    (one_expected, *flatten_expected) = flatten_list(boron, *expected)
    (one, *output) = eapccd.unmask_args(*flatten_args)
    # we do not need to check the arrays, just the objects
    assert output == flatten_expected, "wrong ERI and orbs"
    # for one-electron part, we need to check the arrays
    assert np.allclose(one.array, one_expected.array), "wrong 1-electron part"


#
# Test effective Hamiltonian (only initialization)
#

# h_alpha_n_particle_operator:
h_1_1 = {"fock", "x1ac"}
h_1_2 = {
    "fock",
    "x1ac",
    "x9bc",
    "x11jk",
    "gvvoo",
    "govoo",
    "x8ajck",
    "gvovv",
    "gvvov",
    "gvvvo",
    "gvvvv",
    "x4bjck",
    "x5bjck",
}
h_3_2 = {"fock", "x9bc", "x11jk", "x8ajck", "gvvvv"}


test_set_hamiltonian = [
    (1, {"alpha": 1}, h_1_1),
    (2, {"alpha": 1}, h_1_2),
    (2, {"alpha": 3}, h_3_2),
]


@pytest.mark.parametrize(
    "n_particle_operator,kwargs,expected", test_set_hamiltonian
)
def test_ea_pccd_set_hamiltonian(boron, n_particle_operator, kwargs, expected):
    """Test if effective Hamiltonian has been constructed at all. We do not
    test the actual elements.
    """
    # Create EApCCD instance
    eapccd = REApCCD(boron.lf, boron.occ_model, **kwargs)
    # set some class attributes
    eapccd.unmask_args(boron.t_p, boron.olp, *boron.orb, *boron.hamiltonian)
    eapccd.n_particle_operator = n_particle_operator

    # we do not need to check the arrays, just the objects
    # we need to copy the arrays as they get deleted
    one, two = boron.one.copy(), boron.two.copy()
    eapccd.set_hamiltonian(boron.one, boron.two)
    boron.one, boron.two = one, two

    # Check if cache instance contains all relevant terms
    assert eapccd.cache._store.keys() == expected, "Cache element not found"
    # Check loading from cache
    for h_eff in expected:
        assert eapccd.from_cache(h_eff), "Loading from cache unsuccesful"


test_dump_cache = [
    # molecule instance, nparticle, alpha, expected
    ({"alpha": 1}, "x8ajck"),
    ({"alpha": 1}, "x4bjck"),
    ({"alpha": 1}, "x5bjck"),
    ({"alpha": 3}, "x8ajck"),
]


@pytest.mark.parametrize("kwargs,cache_item", test_dump_cache)
def test_ea_pccd_dump_cache(kwargs, cache_item, boron):
    """Test if effective Hamiltonian is dumped to disk."""
    # Create REApCCD instance
    eapccd = REApCCD(boron.lf, boron.occ_model, **kwargs)
    # set some class attributes explicitly as they are set during function call
    eapccd.unmask_args(boron.t_p, boron.olp, *boron.orb, *boron.hamiltonian)
    eapccd._n_particle_operator = 3
    eapccd._dump_cache = True

    # we need to copy the arrays as they get deleted
    one, two = boron.one.copy(), boron.two.copy()
    eapccd.set_hamiltonian(one, two)

    # Check if cache has been dumped properly
    # We need to access _store directly, otherwise the load function of the
    # Cache class is called and test will fail by construction
    #
    # 1) Check set_hamiltonian
    try:
        assert not hasattr(eapccd.cache._store[cache_item]._value, "_array"), (
            f"Cache element {cache_item} not properly dumped to disk in "
            "set_hamiltonian"
        )
    except KeyError:
        pass
    # 2) Check build_hamiltonian
    vector = boron.lf.create_one_index(eapccd.dimension)
    # all elements should be loaded from the disk and dumped to the disk again
    eapccd.build_subspace_hamiltonian(vector, None)
    try:
        with pytest.raises(ArgumentError):
            assert not hasattr(
                eapccd.cache._store[cache_item].value, "_array"
            ), (
                f"Cache element {cache_item} not properly dumped to disk in "
                "build_subspace_hamiltonian"
            )
    except KeyError:
        pass
    # 3) Check compute_h_diag
    # all elements should be loaded from disk and dump to disk again
    eapccd.compute_h_diag()
    try:
        with pytest.raises(ArgumentError):
            assert not hasattr(
                eapccd.cache._store[cache_item].value, "_array"
            ), (
                f"Cache element {cache_item} not properly dumped to disk in "
                "compute_h_diag"
            )
    except KeyError:
        pass


@pytest.mark.parametrize("kwargs,cache_item", test_dump_cache)
def test_ea_pccd_load_dump_cache(kwargs, cache_item, boron):
    """Test if effective Hamiltonian is loaded and dumped again to disk."""
    # Create REApCCD instance
    eapccd = REApCCD(boron.lf, boron.occ_model, **kwargs)
    # set some class attributes explicitly as they are set during function call
    eapccd.unmask_args(boron.t_p, boron.olp, *boron.orb, *boron.hamiltonian)
    eapccd._n_particle_operator = 3
    eapccd._dump_cache = True

    # we need to copy the arrays as they get deleted
    one, two = boron.one.copy(), boron.two.copy()
    eapccd.set_hamiltonian(one, two)

    # First load arrays again and check if present
    assert hasattr(
        eapccd.cache[cache_item], "_array"
    ), f"Cache element {cache_item} not properly loaded from disk"

    # Dump again, so cache item should not be present
    eapccd.cache.dump(cache_item)
    assert not hasattr(
        eapccd.cache._store[cache_item]._value, "_array"
    ), f"Cache element {cache_item} not properly dumped to disk"


#
# Test for energies
#

testdata_ea = [
    (
        RpCCD,
        "boron",
        "cc-pvdz",
        {"ncore": 0, "charge": 1, "alpha": 1, "nroot": 5},
    ),
    (
        RpCCD,
        "boron",
        "cc-pvdz",
        {"ncore": 0, "charge": 1, "alpha": 3, "nroot": 5},
    ),
    (
        RpCCD,
        "boron",
        "cc-pvdz",
        {"ncore": 1, "charge": 1, "alpha": 1, "nroot": 5},
    ),
    (
        RpCCD,
        "boron",
        "cc-pvdz",
        {"ncore": 1, "charge": 1, "alpha": 3, "nroot": 5},
    ),
    (
        ROOpCCD,
        "boron",
        "cc-pvdz",
        {"ncore": 0, "charge": 1, "alpha": 1, "nroot": 5},
    ),
    (
        ROOpCCD,
        "boron",
        "cc-pvdz",
        {"ncore": 0, "charge": 1, "alpha": 1, "nroot": 5, "spinfree": True},
    ),
]


@pytest.mark.parametrize("cls,mol_f,basis,kwargs", testdata_ea)
def test_ea_pccd(cls, mol_f, basis, kwargs, linalg_slow):
    """
    Test attachment energies for EApCCD models.

    Validates:
        - Total energy (`e_tot`) matches reference data.
        - Attachment energies for `nroot` roots match reference values for `e_ea_<alpha>`.

    Assumptions:
        - Reference data files follow the naming convention and contain the required keys.
        - The molecule supports RHF, pCCD, and EApCCD optimizations.

    Raises:
        - AssertionError: If the reference data is missing or does not contain required keys.
        - AssertionError if the results deviate from the expected reference data.
    """

    ncore = kwargs.get("ncore")
    alpha = kwargs.get("alpha")
    nroot = kwargs.get("nroot")
    charge = kwargs.get("charge")
    spinfree = kwargs.get("spinfree", False)

    # Load and validate reference data
    required_keys = ["e_tot", f"e_ea_{alpha}"]
    expected = load_reference_data(
        cls.__name__,
        mol_f,
        basis,
        charge,
        ncore=ncore,
        nroot=nroot,
        spinfree=spinfree,
        required_keys=required_keys,
    )

    # Prepare molecule
    mol_ = EA_EOMMolecule(
        mol_f, basis, linalg_slow, ncore=ncore, charge=charge
    )
    # Do RHF optimization:
    mol_.do_rhf()
    # Do pCCD optimization:
    mol_.do_pccd(cls)
    assert (
        abs(mol_.pccd.e_tot - expected["e_tot"]) < 1e-6
    ), f"Total energy mismatch: expected {expected['e_tot']}, got {mol_.pccd.e_tot}"
    # Do EApCCD optimization:
    mol_.do_ea_pccd(alpha, nroot, spinfree)

    # Assert results
    for ind in range(nroot):
        # get proper key (e_ea_0 or e_ea_2 or e_ea_4)
        key = f"e_ea_{alpha}"
        assert (
            abs(getattr(mol_.ea_pccd, key)[ind] - expected[key][ind]) < 5e-6
        ), f"Root {ind} energy mismatch for {key}: expected {expected[key][ind]}, got {getattr(mol_.ea_pccd, key)[ind]}"


testdata_ea_cholesky = [
    (
        RpCCD,
        "boron",
        "cc-pvdz",
        {"ncore": 0, "charge": 1, "alpha": 1, "nroot": 2},
    )
]


#
# Just run one Cholesky test (other tests are marked as slow)
# We only check for two roots to be fast.
#
@pytest.mark.parametrize("cls,mol_f,basis,kwargs", testdata_ea_cholesky)
def test_ea_pccd_cholesky(cls, mol_f, basis, kwargs, linalg):
    """
    Test attachment energies for EApCCD models using Cholesky decomposition.

    Assumptions:
        - The reference data contains the required keys: `e_tot` and `e_ea_<alpha>`.
        - The molecule supports RHF, pCCD, and EApCCD optimizations.
        - The reference data file is correctly named and located in the expected directory.

    Validates:
        - Total energy (`e_tot`) matches the reference data within a tolerance of 1e-6.
        - Attachment energies for the specified number of roots (`nroot`) match the reference
        values within a tolerance of 5e-6.

    Raises:
        - AssertionError: If the reference data is missing or does not contain required keys.
        - AssertionError: If the calculated total energy or attachment energies deviate from
        the expected values beyond the allowed tolerances.
    """
    ncore = kwargs.get("ncore")
    alpha = kwargs.get("alpha")
    nroot = kwargs.get("nroot")
    charge = kwargs.get("charge")

    # Load and validate reference data
    required_keys = ["e_tot", f"e_ea_{alpha}"]
    expected = load_reference_data(
        cls.__name__,
        mol_f,
        basis,
        charge,
        ncore=ncore,
        nroot=nroot,
        required_keys=required_keys,
    )

    # Prepare molecule
    mol_ = EA_EOMMolecule(mol_f, basis, linalg, ncore=ncore, charge=charge)
    # Do RHF optimization:
    mol_.do_rhf()
    # Do pCCD optimization:
    mol_.do_pccd(cls)
    assert (
        abs(mol_.pccd.e_tot - expected["e_tot"]) < 1e-6
    ), f"Total energy mismatch: expected {expected['e_tot']}, got {mol_.pccd.e_tot}"
    # Do EApCCD optimization:
    mol_.do_ea_pccd(alpha, nroot, spinfree=kwargs.get("spinfree", False))

    # Assert results
    for ind in range(nroot):
        # get proper key (e_ea_0 or e_ea_2 or e_ea_4)
        key = f"e_ea_{alpha}"  # (key,) = (key for key in expected if "e_ea" in key.lower())
        assert (
            abs(getattr(mol_.ea_pccd, key)[ind] - expected[key][ind]) < 5e-6
        ), f"Attachment energy mismatch for root {ind}: expected {expected[key][ind]}, got {getattr(mol_.ea_pccd, key)[ind]}"
