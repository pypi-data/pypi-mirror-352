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


import pytest

from pybest.ip_eom.dip_base import RDIPCC
from pybest.ip_eom.dip_rccd0 import (
    RDIPCCD0,
    RDIPLCCD0,
    RDIPfpCCD0,
    RDIPfpLCCD0,
)
from pybest.ip_eom.dip_rccsd0 import (
    RDIPCCSD0,
    RDIPLCCSD0,
    RDIPfpCCSD0,
    RDIPfpLCCSD0,
)
from pybest.ip_eom.tests.common import IP_EOMMolecule
from pybest.ip_eom.xip_fpcc import (
    RDIPfpCCD,
    RDIPfpCCSD,
    RDIPfpLCCD,
    RDIPfpLCCSD,
)
from pybest.ip_eom.xip_rcc import RDIPCCD, RDIPCCSD, RDIPLCCD, RDIPLCCSD
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel

test_dip_data_class = [
    (RDIPCCD, RDIPCCD0, 0),
    (RDIPLCCD, RDIPLCCD0, 0),
    (RDIPCCSD, RDIPCCSD0, 0),
    (RDIPLCCSD, RDIPLCCSD0, 0),
    (RDIPfpCCD, RDIPfpCCD0, 0),
    (RDIPfpCCSD, RDIPfpCCSD0, 0),
    (RDIPfpLCCD, RDIPfpLCCD0, 0),
    (RDIPfpLCCSD, RDIPfpLCCSD0, 0),
]


@pytest.mark.parametrize("cls0,cls1,alpha", test_dip_data_class)
def test_class_instance_dipcc(cls0: RDIPCC, cls1: RDIPCC, alpha: int) -> None:
    """Check whether alpha keyword generates proper instance of class."""
    # Some preliminaries
    lf = DenseLinalgFactory(10)
    occ_model = AufbauOccModel(lf, nel=8, ncore=0)
    # Initialize empty class
    ipcc = cls0(lf, occ_model, alpha=alpha)

    assert isinstance(ipcc, cls1)


#
# Test dimension (so far, only spin-dependent implementation)
#

test_dip_data_dim = [
    # nbasis, nhole, nocc, kwargs, expected
    (10, 2, 2, {"ncore": 0, "alpha": 0}, 4),
    (10, 3, 2, {"ncore": 0, "alpha": 0}, 36),
    (10, 2, 2, {"ncore": 1, "alpha": 0}, 1),
    (10, 3, 2, {"ncore": 1, "alpha": 0}, 1),
    (10, 2, 4, {"ncore": 0, "alpha": 0}, 16),
    (10, 3, 4, {"ncore": 0, "alpha": 0}, 304),
    (10, 2, 4, {"ncore": 1, "alpha": 0}, 9),
    (10, 3, 4, {"ncore": 1, "alpha": 0}, 117),
    (10, 2, 8, {"ncore": 0, "alpha": 0}, 64),
    (10, 3, 8, {"ncore": 0, "alpha": 0}, 960),
]

test_dip_flavor = [
    RDIPCCD,
    RDIPLCCD,
    RDIPCCSD,
    RDIPLCCSD,
    RDIPfpCCD,
    RDIPfpCCSD,
    RDIPfpLCCD,
    RDIPfpLCCSD,
]


@pytest.mark.parametrize("nbasis,nh,nocc,kwargs,expected", test_dip_data_dim)
@pytest.mark.parametrize("cls", test_dip_flavor)
def test_dip_cc_dimension(
    cls: RDIPCC,
    nbasis: int,
    nh: int,
    nocc: int,
    kwargs: dict[str, int],
    expected: int,
):
    """Test number of unkowns (CI coefficients) for various parameter sets
    (alpha, ncore, nocc)
    """
    # Create IPCC instance
    lf = DenseLinalgFactory(nbasis)
    occ_model = AufbauOccModel(lf, nel=nocc * 2, ncore=kwargs.get("ncore"))
    ip_cc = cls(lf, occ_model, **kwargs)
    # Overwrite private attribute
    ip_cc._nhole = nh

    assert expected == ip_cc.dimension


#
# Test unmask function
#

test_dip_unmask = [
    # Everything should be fine
    {"alpha": 0},
]


@pytest.mark.parametrize("cls", test_dip_flavor)
@pytest.mark.parametrize("kwargs", test_dip_unmask)
def test_dip_cc_unmask(
    cls: RDIPCC, kwargs: dict[str, int], no_1m: IP_EOMMolecule
) -> None:
    """Test unmask_arg function by passing proper arguments"""
    # Create IPCC instance
    ip_cc = cls(no_1m.lf, no_1m.occ_model, **kwargs)

    # We do not need to check the arrays, just the objects
    assert ip_cc.unmask_args(*no_1m.args, **no_1m.amplitudes) == (
        no_1m.one,
        no_1m.two,
        no_1m.orb[0],
    )


#
# Test effective Hamiltonian (only initialization)
#

# h_alpha_nhole:
h_0_2 = {"fock", "x1im", "xiJmN"}
# Elements for spin-dependent version
h_0_3 = {
    "fock",
    "x1im",
    "xiJmN",
    "xkc",
    "x4bd",
    "ximKC",
    "ximkc",
    "xJkcM",
    "xikcm",
    "xiklm",
    "xkcMD",
    "xiCmD",
    "gooov",
    "goovv",
}

test_set_hamiltonian = [
    # Molecule instance, nhole, {alpha, spin-free}, expected
    (2, {"alpha": 0}, h_0_2),
    (3, {"alpha": 0}, h_0_3),
]


@pytest.mark.parametrize("cls", test_dip_flavor)
@pytest.mark.parametrize("nhole,kwargs,expected", test_set_hamiltonian)
def test_dip_cc_set_hamiltonian(
    cls: RDIPCC,
    nhole: int,
    kwargs: dict[str, int],
    expected: dict,
    no_1m: set[str],
) -> None:
    """Test if effective Hamiltonian has been constructed at all. We do not
    test the actual elements.
    """
    # Create RIPCC instance
    ipcc = cls(no_1m.lf, no_1m.occ_model, **kwargs)
    # Set some class attributes
    ipcc.unmask_args(
        no_1m.t_p,
        no_1m.olp,
        *no_1m.orb,
        *no_1m.hamiltonian,
        **no_1m.amplitudes,
    )
    ipcc._nhole = nhole

    # We do not need to check the arrays, just the objects
    # We need to copy the arrays as they get deleted
    one, two = no_1m.one.copy(), no_1m.two.copy()
    ipcc.set_hamiltonian(no_1m.one, no_1m.two)
    no_1m.one, no_1m.two = one, two

    # Check if cache instance contains all relevant terms
    assert (
        ipcc.cache._store.keys() == expected
    ), f"Cache element not found {ipcc.cache._store.keys()}"
    # Check loading from cache
    for h_eff in expected:
        assert ipcc.from_cache(h_eff), "Loading from cache unsuccessful"
