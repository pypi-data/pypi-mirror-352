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

from __future__ import annotations

import pytest

from pybest.ip_eom import (
    RIPCCD,
    RIPCCSD,
    RIPLCCD,
    RIPLCCSD,
    RIPfpCCD,
    RIPfpCCSD,
    RIPfpLCCD,
    RIPfpLCCSD,
)
from pybest.ip_eom.sip_rccd1 import RIPCCD1, RIPLCCD1, RIPfpCCD1, RIPfpLCCD1
from pybest.ip_eom.sip_rccd1_sf import (
    RIPCCD1SF,
    RIPLCCD1SF,
    RIPfpCCD1SF,
    RIPfpLCCD1SF,
)
from pybest.ip_eom.sip_rccsd1 import (
    RIPCCSD1,
    RIPLCCSD1,
    RIPfpCCSD1,
    RIPfpLCCSD1,
)
from pybest.ip_eom.sip_rccsd1_sf import (
    RIPCCSD1SF,
    RIPLCCSD1SF,
    RIPfpCCSD1SF,
    RIPfpLCCSD1SF,
)
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel

test_data_alpha = [
    (RIPCCD, {"alpha": 1}, 1),
    (RIPCCSD, {"alpha": 1}, 1),
    (RIPLCCD, {"alpha": 1}, 1),
    (RIPLCCSD, {"alpha": 1}, 1),
    (RIPfpCCD, {"alpha": 1}, 1),
    (RIPfpCCSD, {"alpha": 1}, 1),
    (RIPfpLCCD, {"alpha": 1}, 1),
    (RIPfpLCCSD, {"alpha": 1}, 1),
    (RIPCCD, {"alpha": 1, "spinfree": True}, 1),
    (RIPCCSD, {"alpha": 1, "spinfree": True}, 1),
    (RIPLCCD, {"alpha": 1, "spinfree": True}, 1),
    (RIPLCCSD, {"alpha": 1, "spinfree": True}, 1),
    (RIPfpCCD, {"alpha": 1, "spinfree": True}, 1),
    (RIPfpCCSD, {"alpha": 1, "spinfree": True}, 1),
    (RIPfpLCCD, {"alpha": 1, "spinfree": True}, 1),
    (RIPfpLCCSD, {"alpha": 1, "spinfree": True}, 1),
]


@pytest.mark.parametrize("cls,kwargs,expected", test_data_alpha)
def test_alpha_fp_cc(
    cls: RIPfpCCD, kwargs: dict[str, int | bool], expected: int
) -> None:
    """Check if alpha agrees after RIPpCCD/RDIPpCCD inits."""
    # Some preliminaries
    lf = DenseLinalgFactory(10)
    occ_model = AufbauOccModel(lf, nel=8, ncore=0)
    # Initialize empty class
    ipcc = cls(lf, occ_model, **kwargs)

    assert ipcc.alpha == expected


test_data_instance = [
    (RIPCCD, {"alpha": 1}, RIPCCD1),
    (RIPCCSD, {"alpha": 1}, RIPCCSD1),
    (RIPLCCD, {"alpha": 1}, RIPLCCD1),
    (RIPLCCSD, {"alpha": 1}, RIPLCCSD1),
    (RIPfpCCD, {"alpha": 1}, RIPfpCCD1),
    (RIPfpCCSD, {"alpha": 1}, RIPfpCCSD1),
    (RIPfpLCCD, {"alpha": 1}, RIPfpLCCD1),
    (RIPfpLCCSD, {"alpha": 1}, RIPfpLCCSD1),
    (RIPCCD, {"alpha": 1, "spinfree": True}, RIPCCD1SF),
    (RIPCCSD, {"alpha": 1, "spinfree": True}, RIPCCSD1SF),
    (RIPLCCD, {"alpha": 1, "spinfree": True}, RIPLCCD1SF),
    (RIPLCCSD, {"alpha": 1, "spinfree": True}, RIPLCCSD1SF),
    (RIPfpCCD, {"alpha": 1, "spinfree": True}, RIPfpCCD1SF),
    (RIPfpCCSD, {"alpha": 1, "spinfree": True}, RIPfpCCSD1SF),
    (RIPfpLCCD, {"alpha": 1, "spinfree": True}, RIPfpLCCD1SF),
    (RIPfpLCCSD, {"alpha": 1, "spinfree": True}, RIPfpLCCSD1SF),
]


@pytest.mark.parametrize("cls,kwargs,expected", test_data_instance)
def test_instance(
    cls: RIPCCD, kwargs: dict[str, int | bool], expected: type[RIPCCD]
):
    """Check if __new__ overwrite works properly."""
    # Some preliminaries
    lf = DenseLinalgFactory(10)
    occ_model = AufbauOccModel(lf, nel=8, ncore=0)
    # Initialize empty class
    ipcc = cls(lf, occ_model, **kwargs)

    assert isinstance(ipcc, expected)
