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

from __future__ import annotations

from typing import Any

import numpy as np
import pytest

from pybest.ea_eom.dea_pccd0 import RDEApCCD0
from pybest.ea_eom.dea_pccd2 import RDEApCCD2
from pybest.ea_eom.dea_pccd4 import RDEApCCD4
from pybest.ea_eom.tests.common import EA_EOMMolecule, flatten_list
from pybest.ea_eom.xea_pccd import RDEApCCD
from pybest.exceptions import ArgumentError
from pybest.geminals import ROOpCCD, RpCCD
from pybest.linalg import DenseLinalgFactory
from pybest.linalg.cholesky import CholeskyLinalgFactory
from pybest.occ_model import AufbauOccModel

test_data_alpha_pccd = [
    (RDEApCCD0, 0),
    (RDEApCCD2, 2),
    (RDEApCCD4, 4),
]


@pytest.mark.parametrize("cls,expected", test_data_alpha_pccd)
def test_alpha_pccd(cls: RDEApCCD0 | RDEApCCD2 | RDEApCCD4, expected: int):
    """Check consistency of class attributes"""
    # some preliminaries
    lf = DenseLinalgFactory(10)
    occ_model = AufbauOccModel(lf, nel=8, ncore=0)
    # Initialize empty class
    eacc = cls(lf, occ_model)

    assert eacc.alpha == expected


#
# Test dimension
#

test_data_dim = [
    # nbasis, n_particle_operator, nocc, kwargs, expected
    (10, 2, 4, {"ncore": 0, "alpha": 0}, 36),
    (10, 3, 4, {"ncore": 0, "alpha": 0}, 756),
    (10, 2, 4, {"ncore": 0, "alpha": 2}, 15),
    (10, 3, 4, {"ncore": 0, "alpha": 2}, 455),
    (10, 3, 4, {"ncore": 0, "alpha": 4}, 80),
    (10, 2, 4, {"ncore": 1, "alpha": 0}, 36),
    (10, 3, 4, {"ncore": 1, "alpha": 0}, 576),
    (10, 2, 4, {"ncore": 1, "alpha": 2}, 15),
    (10, 3, 4, {"ncore": 1, "alpha": 2}, 345),
    (10, 3, 4, {"ncore": 1, "alpha": 4}, 60),
    (10, 2, 8, {"ncore": 0, "alpha": 0}, 4),
    (10, 3, 8, {"ncore": 0, "alpha": 0}, 36),
    (10, 2, 8, {"ncore": 0, "alpha": 2}, 1),
    (10, 3, 8, {"ncore": 0, "alpha": 2}, 17),
    (10, 3, 8, {"ncore": 0, "alpha": 4}, 0),
    (10, 2, 7, {"ncore": 0, "alpha": 0}, 9),
    (10, 3, 7, {"ncore": 0, "alpha": 0}, 135),
    (10, 2, 7, {"ncore": 0, "alpha": 2}, 3),
    (10, 3, 7, {"ncore": 0, "alpha": 2}, 73),
    (10, 3, 7, {"ncore": 0, "alpha": 4}, 7),
    (10, 2, 7, {"ncore": 1, "alpha": 0}, 9),
    (10, 3, 7, {"ncore": 1, "alpha": 0}, 117),
    (10, 2, 7, {"ncore": 1, "alpha": 2}, 3),
    (10, 3, 7, {"ncore": 1, "alpha": 2}, 63),
    (10, 3, 7, {"ncore": 1, "alpha": 4}, 6),
]


@pytest.mark.parametrize("nbasis,n_p,nocc,kwargs,expected", test_data_dim)
def test_dea_pccd_dimension(
    nbasis: int, n_p: int, nocc: int, kwargs: dict[str, int], expected: int
):
    """Test number of unknowns (CI coefficients) for various parameter sets
    (alpha, ncore, nocc)
    """
    # Create DEApCCD instance
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=nocc * 2, ncore=kwargs.pop("ncore"))
    deapccd = RDEApCCD(lf, occ_model, **kwargs)
    # overwrite private attribute
    deapccd._n_particle_operator = n_p

    assert expected == deapccd.dimension


#
# Test unmask function
#

test_unmask_error = [
    # no t_p
    ({"alpha": 0}, (), ArgumentError),
    ({"alpha": 2}, (), ArgumentError),
    ({"alpha": 4}, (), ArgumentError),
    # no olp
    ({"alpha": 0}, ("t_p",), ArgumentError),
    ({"alpha": 2}, ("t_p",), ArgumentError),
    ({"alpha": 4}, ("t_p",), ArgumentError),
    # no orb
    ({"alpha": 0}, ("t_p", "olp"), ArgumentError),
    ({"alpha": 2}, ("t_p", "olp"), ArgumentError),
    ({"alpha": 4}, ("t_p", "olp"), ArgumentError),
    # no two
    ({"alpha": 0}, ("t_p", "olp", "orb"), UnboundLocalError),
    ({"alpha": 2}, ("t_p", "olp", "orb"), UnboundLocalError),
    ({"alpha": 4}, ("t_p", "olp", "orb"), UnboundLocalError),
]


@pytest.mark.parametrize("kwargs,args,raised_error", test_unmask_error)
def test_dea_pccd_unmask_raise_error(
    carbon: EA_EOMMolecule,
    kwargs: dict[str, int],
    args: Any,
    raised_error: Any,
):
    """Test unmask_arg function by passing insufficient arguments"""
    # Create EApCCD instance
    deapccd = RDEApCCD(carbon.lf, carbon.occ_model, **kwargs)

    # resolve a incomplete list of arguments
    wrong_args = flatten_list(carbon, *args)
    with pytest.raises(raised_error):
        assert deapccd.unmask_args(*wrong_args)


test_unmask = [
    # everything should be fine
    (
        {"alpha": 0},
        ("t_p", "olp", "orb", "hamiltonian"),
        ("one", "two", "orb"),
    ),
    (
        {"alpha": 2},
        ("t_p", "olp", "orb", "hamiltonian"),
        ("one", "two", "orb"),
    ),
    (
        {"alpha": 4},
        ("t_p", "olp", "orb", "hamiltonian"),
        ("one", "two", "orb"),
    ),
]


@pytest.mark.parametrize("kwargs,args,expected", test_unmask)
def test_dea_pccd_unmask(
    carbon: EA_EOMMolecule,
    kwargs: dict[str, int],
    args: tuple[str, str, str, str],
    expected: tuple[str, str, str],
):
    """Test unmask_arg function by passing proper arguments"""
    # Create DEApCCD instance
    deapccd = RDEApCCD(carbon.lf, carbon.occ_model, **kwargs)

    # resolve arguments and collect them in a flattened list
    flatten_args = flatten_list(carbon, *args)
    # we cannot test the one-electron integrals as unmaks_args creates a new
    # element
    (one_expected, *flatten_expected) = flatten_list(carbon, *expected)
    (one, *output) = deapccd.unmask_args(*flatten_args)
    # we do not need to check the arrays, just the objects
    assert output == flatten_expected, "wrong ERI and orbs"
    # for one-electron part, we need to check the arrays
    assert np.allclose(one.array, one_expected.array), "wrong 1-electron part"


#
# Test effective Hamiltonian (only initialization)
#

# h_alpha_n_particle_operator
h_0_2 = {"fock", "xcd", "gvvoo", "gvvvv"}
h_0_3 = {
    "fock",
    "xcd",
    "gvvoo",
    "gvvvv",
    "xkm",
    "xckdm",
    "xckDM",
    "xbkDm",
    "xbckd",
    "xackd",
    "gvovv",
    "gvvov",
}
h_2_2 = {"fock", "xcd", "gvvvv"}
h_2_3 = {
    "fock",
    "xcd",
    "gvvvv",
    "xkm",
    "goovv",
    "xckdm",
    "xckDM",
    "xbkDm",
    "xbckd",
    "gvovv",
    "gvvov",
}
h_4_3 = {"xkm", "xcd", "xckdm", "gvvvv"}

test_set_hamiltonian = [
    # molecule instance, n_particle_operator, alpha, expected
    (2, {"alpha": 0}, h_0_2),
    (3, {"alpha": 0}, h_0_3),
    (2, {"alpha": 2}, h_2_2),
    (3, {"alpha": 2}, h_2_3),
    (3, {"alpha": 4}, h_4_3),
]


@pytest.mark.parametrize(
    "n_particle_operator,kwargs,expected", test_set_hamiltonian
)
def test_dea_pccd_set_hamiltonian(
    carbon: EA_EOMMolecule,
    n_particle_operator: int,
    kwargs: dict[str, int],
    expected: set[Any],
):
    """Test if effective Hamiltonian has been constructed at all. We do not
    test the actual elements.
    """
    # Create DEApCCD instance
    deapccd = RDEApCCD(carbon.lf, carbon.occ_model, **kwargs)
    # set some class attributes
    deapccd.unmask_args(
        carbon.t_p, carbon.olp, *carbon.orb, *carbon.hamiltonian
    )
    deapccd._n_particle_operator = n_particle_operator

    # we do not need to check the arrays, just the objects
    # we need to copy the arrays as they get deleted
    one, two = carbon.one.copy(), carbon.two.copy()
    deapccd.set_hamiltonian(carbon.one, carbon.two)
    carbon.one, carbon.two = one, two

    # Check if cache instance contains all relevant terms
    assert deapccd.cache._store.keys() == expected, "Cache element not found"
    # Check loading from cache
    for h_eff in expected:
        assert deapccd.from_cache(h_eff), "Loading from cache unsuccesful"


#
# Test for energies
#

testdata_ea = [
    (
        RpCCD,
        "c",
        "cc-pvdz",
        {
            "ncore": 0,
            "charge": 2,
            "alpha": 0,
            "nroot": 6,
            "nparticle": 2,
        },
        {
            "e_tot": -36.463390671529,
            "e_ea_0": [
                -1.194633e00,
                -1.194633e00,
                -1.194633e00,
                -1.143270e00,
                -1.143270e00,
                -1.143270e00,
            ],
        },
    ),
    (
        RpCCD,
        "c",
        "cc-pvdz",
        {
            "ncore": 0,
            "charge": 2,
            "alpha": 0,
            "nroot": 6,
            "nparticle": 3,
        },
        {
            "e_tot": -36.463390671529,
            "e_ea_0": [
                -1.295825e00,
                -1.295825e00,
                -1.295825e00,
                -1.240332e00,
                -1.240332e00,
                -1.240332e00,
            ],
        },
    ),
    (
        RpCCD,
        "c",
        "cc-pvdz",
        {
            "ncore": 1,
            "charge": 2,
            "alpha": 0,
            "nroot": 6,
            "nparticle": 3,
        },
        {
            "e_tot": -36.463264455571,
            "e_ea_0": [
                -1.295324e00,
                -1.295324e00,
                -1.295324e00,
                -1.239877e00,
                -1.239877e00,
                -1.239877e00,
            ],
        },
    ),
    (
        RpCCD,
        "c",
        "cc-pvdz",
        {
            "ncore": 0,
            "charge": 2,
            "alpha": 2,
            "nroot": 6,
            "nparticle": 2,
        },
        {
            "e_tot": -36.463390671529,
            "e_ea_2": [
                -1.194633e00,
                -1.194633e00,
                -1.194633e00,
                -5.887488e-01,
                -5.887488e-01,
                -5.887488e-01,
            ],
        },
    ),
    (
        RpCCD,
        "c",
        "cc-pvdz",
        {
            "ncore": 0,
            "charge": 2,
            "alpha": 2,
            "nroot": 6,
            "nparticle": 3,
            "nguessv": 34,
        },
        {
            "e_tot": -36.463390671529,
            "e_ea_2": [
                -1.295825e00,
                -1.295825e00,
                -1.295825e00,
                -1.130024e00,
                -9.548326e-01,
                -9.548326e-01,
            ],
        },
    ),
    (
        RpCCD,
        "c",
        "cc-pvdz",
        {
            "ncore": 1,
            "charge": 2,
            "alpha": 2,
            "nroot": 6,
            "nparticle": 3,
        },
        {
            "e_tot": -36.463264455571,
            "e_ea_2": [
                -1.295324e00,
                -1.295324e00,
                -1.295324e00,
                -1.129958e00,
                -9.545549e-01,
                -9.545549e-01,
            ],
        },
    ),
    (
        RpCCD,
        "c",
        "cc-pvdz",
        {
            "ncore": 0,
            "charge": 2,
            "alpha": 4,
            "nroot": 6,
            "nparticle": 3,
        },
        {
            "e_tot": -36.463390671529,
            "e_ea_4": [
                -1.130024e00,
                -4.628421e-01,
                -4.628421e-01,
                -4.628421e-01,
                -4.628421e-01,
                -4.628421e-01,
            ],
        },
    ),
    (
        RpCCD,
        "c",
        "cc-pvdz",
        {
            "ncore": 1,
            "charge": 2,
            "alpha": 4,
            "nroot": 6,
            "nparticle": 3,
        },
        {
            "e_tot": -36.463264455571,
            "e_ea_4": [
                -1.129958e00,
                -4.627638e-01,
                -4.627638e-01,
                -4.627638e-01,
                -4.627638e-01,
                -4.627638e-01,
            ],
        },
    ),
    (
        ROOpCCD,
        "c",
        "cc-pvdz",
        {
            "ncore": 0,
            "charge": 2,
            "alpha": 2,
            "nroot": 6,
            "nparticle": 3,
        },
        {
            "e_tot": -36.473160774973,
            "e_ea_2": [
                -1.288381e00,
                -1.288381e00,
                -1.288381e00,
                -1.116511e00,
                -9.417792e-01,
                -9.417792e-01,
            ],
        },
    ),
]

#
# Cholesky tests
#


@pytest.mark.parametrize("cls,mol_f,basis,kwargs,expected", testdata_ea)
def test_dea_pccd(
    cls: RpCCD | ROOpCCD,
    mol_f: str,
    basis: str,
    kwargs: dict[str, int],
    expected: dict[str, Any],
    linalg_slow: DenseLinalgFactory,
):
    """Test attachement energies of DEApCCD flavors"""
    ncore = kwargs.get("ncore")
    alpha = kwargs.get("alpha")
    nroot = kwargs.get("nroot")
    charge = kwargs.get("charge")
    n_particle_operator = kwargs.get("nparticle")
    # Prepare molecule
    mol_ = EA_EOMMolecule(
        mol_f, basis, linalg_slow, charge=charge, ncore=ncore
    )
    # Do RHF optimization:
    mol_.do_rhf()
    # Do pCCD optimization:
    mol_.do_pccd(cls)
    assert abs(mol_.pccd.e_tot - expected["e_tot"]) < 1e-6
    # Do DEApCCD optimization:
    mol_.do_dea_pccd(alpha, nroot, n_particle_operator)

    for ind in range(nroot):
        # get proper key (e_ea_0 or e_ea_2 or e_ea_4)
        (key,) = (key for key in expected if "e_ea" in key.lower())
        assert (
            abs(getattr(mol_.dea_pccd, key)[ind] - expected[key][ind]) < 5e-6
        )


#
# Cholesky tests
#

testdata_ea_cholesky = [
    (
        RpCCD,
        "c",
        "cc-pvdz",
        {
            "ncore": 1,
            "charge": 2,
            "alpha": 0,
            "nroot": 3,
            "nparticle": 3,
        },
        {
            "e_tot": -36.463264455571,
            "e_ea_0": [
                -1.295324e00,
                -1.295324e00,
                -1.295324e00,
                -1.239877e00,
                -1.239877e00,
                -1.239877e00,
            ],
        },
    ),
]


@pytest.mark.parametrize(
    "cls,mol_f,basis,kwargs,expected", testdata_ea_cholesky
)
def test_dea_pccd_cholesky(
    cls: RpCCD | ROOpCCD,
    mol_f: str,
    basis: str,
    kwargs: dict[str, int],
    expected: dict[str, Any],
    linalg: DenseLinalgFactory | CholeskyLinalgFactory,
):
    """Test attachement energies of DEApCCD model"""
    ncore = kwargs.get("ncore")
    alpha = kwargs.get("alpha")
    nroot = kwargs.get("nroot")
    charge = kwargs.get("charge")
    n_particle_operator = kwargs.get("nparticle")
    # Prepare molecule
    mol_ = EA_EOMMolecule(mol_f, basis, linalg, charge=charge, ncore=ncore)
    # Do RHF optimization:
    mol_.do_rhf()
    # Do pCCD optimization:
    mol_.do_pccd(cls)
    assert abs(mol_.pccd.e_tot - expected["e_tot"]) < 1e-6
    # Do DEApCCD optimization:
    mol_.do_dea_pccd(alpha, nroot, n_particle_operator)

    for ind in range(nroot):
        # get proper key (e_ea_0 or e_ea_2 or e_ea_4)
        (key,) = (key for key in expected if "e_ea" in key.lower())
        assert (
            abs(getattr(mol_.dea_pccd, key)[ind] - expected[key][ind]) < 5e-6
        )
