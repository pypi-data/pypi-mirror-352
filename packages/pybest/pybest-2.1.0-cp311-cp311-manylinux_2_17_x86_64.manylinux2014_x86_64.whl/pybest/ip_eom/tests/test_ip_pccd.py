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
#
# 2025-02: unification of variables and type hints (Julian Świerczyński)
# 2025-03: incorporation of new molecue testing framework (Julia Szczuczko)

from __future__ import annotations

import pytest

from pybest.geminals import ROOpCCD, RpCCD
from pybest.geminals.rpccd_base import RpCCDBase
from pybest.ip_eom.sip_pccd1 import RIPpCCD1
from pybest.ip_eom.sip_pccd3 import RIPpCCD3
from pybest.ip_eom.tests.common import IP_EOMMolecule
from pybest.ip_eom.xip_pccd import RIPpCCD
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel
from pybest.tests.common import load_reference_data

test_data_class = [(RIPpCCD1, 1), (RIPpCCD3, 3)]


@pytest.mark.parametrize("cls, alpha", test_data_class)
def test_class_instance_ippccd(cls: RIPpCCD, alpha: int) -> None:
    """Check whether alpha keyword generates proper instance of class."""
    # Some preliminaries
    lf = DenseLinalgFactory(10)
    occ_model = AufbauOccModel(lf, nel=8, ncore=0)
    # Initialize empty class
    ipcc = RIPpCCD(lf, occ_model, alpha=alpha)

    assert isinstance(ipcc, cls)


#
# Test dimension (only spin-dependent implementation)
#

test_data_dim = [
    # nbasis, nhole, nocc, kwargs, expected
    (10, 1, 3, {"ncore": 0, "alpha": 1}, 3),
    (10, 2, 3, {"ncore": 0, "alpha": 1}, 87),
    (10, 2, 3, {"ncore": 0, "alpha": 3}, 21),
    (10, 1, 3, {"ncore": 1, "alpha": 1}, 2),
    (10, 2, 3, {"ncore": 1, "alpha": 1}, 37),
    (10, 2, 3, {"ncore": 1, "alpha": 3}, 7),
    (10, 1, 5, {"ncore": 0, "alpha": 1}, 5),
    (10, 2, 5, {"ncore": 0, "alpha": 1}, 180),
    (10, 2, 5, {"ncore": 0, "alpha": 3}, 50),
    (10, 1, 5, {"ncore": 2, "alpha": 1}, 3),
    (10, 2, 5, {"ncore": 2, "alpha": 1}, 63),
    (10, 2, 5, {"ncore": 2, "alpha": 3}, 15),
]


@pytest.mark.parametrize("nbasis,nh,nocc,kwargs,expected", test_data_dim)
def test_ip_pccd_dimension(
    nbasis: int, nh: int, nocc: int, kwargs: dict[str, int], expected: int
) -> None:
    """Test number of unkowns (CI coefficients) for various parameter sets
    (alpha, ncore, nocc)
    """
    # Create IPpCCD instance
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=nocc * 2, ncore=kwargs.pop("ncore"))
    ippccd = RIPpCCD(lf, occ_model, **kwargs)
    # Overwrite private attribute
    ippccd._nhole = nh

    assert expected == ippccd.dimension


#
# Test unmask function
#

test_unmask = [
    # Everything should be fine
    {"alpha": 1},
    {"alpha": 3},
]


@pytest.mark.parametrize("kwargs", test_unmask)
def test_ip_pccd_unmask(kwargs: dict[str, int], no_1m: IP_EOMMolecule) -> None:
    """Test unmask_arg function by passing proper arguments"""
    # Create IPpCCD instance
    ippccd = RIPpCCD(no_1m.lf, no_1m.occ_model, **kwargs)

    # We do not need to check the arrays, just the objects
    assert ippccd.unmask_args(*no_1m.args) == (
        no_1m.one,
        no_1m.two,
        no_1m.orb[0],
    )


#
# Test effective Hamiltonian (only initialization)
#

# h_alpha_nhole:
h_1_1 = {"fock", "x1im"}
h_1_2 = {
    "fock",
    "x1im",
    "x4bd",
    "goooo",
    "gooov",
    "x2ijbm",
    "x5ijbm",
    "x6ijlm",
    "goovv",
    "govvo",
    "gvvoo",
    "govov",
}
h_3_2 = {"fock", "x1im", "x4bd", "goooo", "goovv", "govvo", "govov"}

test_set_hamiltonian = [
    # Molecule instance, nhole, alpha, expected
    (1, {"alpha": 1}, h_1_1),
    (2, {"alpha": 1}, h_1_2),
    (2, {"alpha": 3}, h_3_2),
]


@pytest.mark.parametrize("nhole,kwargs,expected", test_set_hamiltonian)
def test_ip_pccd_set_hamiltonian(
    nhole: int,
    kwargs: dict[str, int],
    expected: set[str],
    no_1m: IP_EOMMolecule,
):
    """Test if effective Hamiltonian has been constructed at all. We do not
    test the actual elements.
    """
    # Create RIPpCCD instance
    ippccd = RIPpCCD(no_1m.lf, no_1m.occ_model, **kwargs)
    # Set some class attributes
    ippccd.unmask_args(no_1m.t_p, no_1m.olp, *no_1m.orb, *no_1m.hamiltonian)
    ippccd._nhole = nhole

    # We do not need to check the arrays, just the objects
    # We need to copy the arrays as they get deleted
    one, two = no_1m.one.copy(), no_1m.two.copy()
    ippccd.set_hamiltonian(no_1m.one, no_1m.two)
    no_1m.one, no_1m.two = one, two

    # Check if cache instance contains all relevant terms
    assert ippccd.cache._store.keys() == expected, "Cache element not found"
    # Check loading from cache
    for h_eff in expected:
        assert ippccd.from_cache(h_eff), "Loading from cache unsuccesful"


test_data_ip = [
    (
        RpCCD,
        "li",
        "cc-pvdz",
        {"ncore": 0, "charge": -1, "alpha": 1, "nroot": 5, "nhole": 2},
    ),
    (
        RpCCD,
        "li",
        "cc-pvdz",
        {"ncore": 0, "charge": -1, "alpha": 3, "nroot": 5, "nhole": 2},
    ),
    (
        RpCCD,
        "no",
        "cc-pvdz",
        {"ncore": 1, "charge": -1, "alpha": 1, "nroot": 5, "nhole": 1},
    ),
    (
        ROOpCCD,
        "li",
        "cc-pvdz",
        {"ncore": 0, "charge": -1, "alpha": 1, "nroot": 5, "nhole": 2},
    ),
    (
        ROOpCCD,
        "li",
        "cc-pvdz",
        {"ncore": 0, "charge": -1, "alpha": 3, "nroot": 5, "nhole": 2},
    ),
]


@pytest.mark.parametrize("cls, mol, basis, kwargs", test_data_ip)
def test_ip_pccd(
    cls: RpCCDBase,
    mol: str,
    basis: str,
    kwargs: dict[str, int],
    linalg: str,
) -> None:
    """Test attachement energies of DEApCCD models"""
    ncore = kwargs.get("ncore")
    charge = kwargs.get("charge")
    alpha = kwargs.get("alpha")
    nroot = kwargs.get("nroot")
    nhole = kwargs.get("nhole")

    # Load and validate reference data
    required_keys = ["e_tot", f"e_ip_{alpha}"]
    expected = load_reference_data(
        cls.__name__,
        mol,
        basis,
        charge,
        ncore=ncore,
        nroot=nroot,
        nhole=nhole,
        required_keys=required_keys,
    )

    # Prepare molecule (all molecules have 1 additional electron)
    mol_ = IP_EOMMolecule(mol, basis, linalg, ncore=ncore, charge=charge)
    # Do RHF optimization:
    mol_.do_rhf()
    # Do pCCD optimization:
    mol_.do_pccd(cls)
    assert (
        abs(mol_.pccd.e_tot - expected["e_tot"]) < 1e-6
    ), f"Total energy mismatch: expected {expected['e_tot']}, got {mol_.pccd.e_tot}"
    # Do DIPpCCD optimization:
    mol_.do_ip_pccd(alpha, nroot, nhole)

    for ind in range(nroot):
        key = f"e_ip_{alpha}"
        assert (
            abs(getattr(mol_.ip_pccd, key)[ind] - expected[key][ind]) < 5e-6
        ), f"Attachment energy mismatch for root {ind}: expected {expected[key][ind]}, got {getattr(mol_.ip_pccd, key)[ind]}"
