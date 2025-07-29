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

from typing import Any

import pytest

from pybest.ip_eom.sip_rccd1 import RIPCCD1, RIPLCCD1, RIPfpCCD1, RIPfpLCCD1
from pybest.ip_eom.sip_rccsd1 import (
    RIPCCSD1,
    RIPLCCSD1,
    RIPfpCCSD1,
    RIPfpLCCSD1,
)
from pybest.ip_eom.xip_fpcc import RIPfpCCD, RIPfpCCSD, RIPfpLCCD, RIPfpLCCSD
from pybest.ip_eom.xip_rcc import RIPCCD, RIPCCSD, RIPLCCD, RIPLCCSD
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel

test_data_class = [
    (RIPCCD, RIPCCD1, 1),
    (RIPLCCD, RIPLCCD1, 1),
    (RIPCCSD, RIPCCSD1, 1),
    (RIPLCCSD, RIPLCCSD1, 1),
    (RIPfpCCD, RIPfpCCD1, 1),
    (RIPfpCCSD, RIPfpCCSD1, 1),
    (RIPfpLCCD, RIPfpLCCD1, 1),
    (RIPfpLCCSD, RIPfpLCCSD1, 1),
]


@pytest.mark.parametrize("cls0,cls1,alpha", test_data_class)
def test_class_instance_ipcc(cls0: RIPCCD, cls1: RIPCCD, alpha: int) -> None:
    """Check whether alpha keyword generates proper instance of class."""
    # Some preliminaries
    lf = DenseLinalgFactory(10)
    occ_model = AufbauOccModel(lf, nel=8, ncore=0)
    # Initialize empty class
    ipcc = cls0(lf, occ_model, alpha=alpha)

    assert isinstance(ipcc, cls1)


#
# Test dimension (spin-free and spin-dependent implementation)
#

test_data_dim = [
    # nbasis, nhole, nocc, kwargs, expected
    (10, 1, 3, {"ncore": 0, "alpha": 1}, 3),
    (10, 2, 3, {"ncore": 0, "alpha": 1}, 87),
    (10, 1, 3, {"ncore": 1, "alpha": 1}, 2),
    (10, 2, 3, {"ncore": 1, "alpha": 1}, 37),
    (10, 1, 5, {"ncore": 0, "alpha": 1}, 5),
    (10, 2, 5, {"ncore": 0, "alpha": 1}, 180),
    (10, 1, 5, {"ncore": 2, "alpha": 1}, 3),
    (10, 2, 5, {"ncore": 2, "alpha": 1}, 63),
    (10, 1, 3, {"ncore": 0, "alpha": 1, "spinfree": True}, 3),
    (10, 2, 3, {"ncore": 0, "alpha": 1, "spinfree": True}, 66),
    (10, 1, 3, {"ncore": 1, "alpha": 1, "spinfree": True}, 2),
    (10, 2, 3, {"ncore": 1, "alpha": 1, "spinfree": True}, 30),
    (10, 1, 5, {"ncore": 0, "alpha": 1, "spinfree": True}, 5),
    (10, 2, 5, {"ncore": 0, "alpha": 1, "spinfree": True}, 130),
    (10, 1, 5, {"ncore": 2, "alpha": 1, "spinfree": True}, 3),
    (10, 2, 5, {"ncore": 2, "alpha": 1, "spinfree": True}, 48),
]

test_ip_flavor = [
    RIPCCD,
    RIPLCCD,
    RIPCCSD,
    RIPLCCSD,
    RIPfpCCD,
    RIPfpCCSD,
    RIPfpLCCD,
    RIPfpLCCSD,
]


@pytest.mark.parametrize("nbasis,nh,nocc,kwargs,expected", test_data_dim)
@pytest.mark.parametrize("cls", test_ip_flavor)
def test_ip_cc_dimension(
    cls: RIPCCD,
    nbasis: int,
    nh: int,
    nocc: int,
    kwargs: dict[str, int | bool],
    expected: int,
) -> None:
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

test_unmask = [
    # Everything should be fine
    {"alpha": 1},
    {"alpha": 1, "spin-free": True},
]


@pytest.mark.parametrize("cls", test_ip_flavor)
@pytest.mark.parametrize("kwargs", test_unmask)
def test_ip_cc_unmask(cls: RIPCCD, kwargs: dict[str, int], no_1m: Any) -> None:
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
h_1_1 = {"fock", "x1im"}
# Elements common for spin-free and spin-dependent version
h_1_2 = {"fock", "x1im", "xkc", "x4bd", "ximkc", "xijkl", "goovv"}
# spin-free elements
h_1_2_sf = {"ximkc", "xijbm", "xjbkc", "xibkc"}
h_1_2_sf.update(h_1_2)
# spin-dependent elements
h_1_2_sd = {"ximKC", "xiJBm", "xiJkL", "xjbKC", "xiBkC", "x2ijbm"}
h_1_2_sd.update(h_1_2)

test_set_hamiltonian = [
    # Molecule instance, nhole, {alpha, spin-free}, expected
    (1, {"alpha": 1}, h_1_1),
    (2, {"alpha": 1}, h_1_2_sd),
    (1, {"alpha": 1, "spinfree": True}, h_1_1),
    (2, {"alpha": 1, "spinfree": True}, h_1_2_sf),
]


@pytest.mark.parametrize("cls", test_ip_flavor)
@pytest.mark.parametrize("nhole,kwargs,expected", test_set_hamiltonian)
def test_ip_cc_set_hamiltonian(
    cls: RIPCCD,
    nhole: int,
    kwargs: dict[str, int],
    expected: set[str],
    no_1m: Any,
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
