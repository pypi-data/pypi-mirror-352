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
# This file has been written by Emil Sujkowski (original version)
from __future__ import annotations

from collections.abc import Sequence

import pytest

from pybest.linalg import CholeskyLinalgFactory, DenseLinalgFactory
from pybest.occ_model import AufbauOccModel
from pybest.rsf_eom import (
    RSFCCD,
    RSFCCSD,
    RSFLCCD,
    RSFLCCSD,
    RSFfpCCD,
    RSFfpCCSD,
    RSFfpLCCD,
    RSFfpLCCSD,
)
from pybest.rsf_eom.rsf_ccd4 import RSFCCD4, RSFLCCD4, RSFfpCCD4, RSFfpLCCD4
from pybest.rsf_eom.rsf_ccsd4 import (
    RSFCCSD4,
    RSFLCCSD4,
    RSFfpCCSD4,
    RSFfpLCCSD4,
)

test_data_alpha: Sequence[RSFCCD4 | RSFCCSD4 | dict[str, int] | int] = [
    (RSFCCD, {"alpha": 4}, 4),
    (RSFLCCD, {"alpha": 4}, 4),
    (RSFfpCCD, {"alpha": 4}, 4),
    (RSFfpLCCD, {"alpha": 4}, 4),
    (RSFCCSD, {"alpha": 4}, 4),
    (RSFLCCSD, {"alpha": 4}, 4),
    (RSFfpCCSD, {"alpha": 4}, 4),
    (RSFfpLCCSD, {"alpha": 4}, 4),
]


@pytest.mark.parametrize("cls,kwargs,expected", test_data_alpha)
def test_alpha(
    cls: RSFCCD4 | RSFCCSD4,
    kwargs: dict[str, int],
    expected: int,
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
) -> None:
    """Check if alpha agrees after RSFCC inits."""
    # some preliminaries
    lf = linalg(2)
    occ_model = AufbauOccModel(lf, nel=2)
    # Initialize empty class
    rsfcc = cls(lf, occ_model, **kwargs)

    assert rsfcc.alpha == expected


test_data_instance: Sequence[RSFCCD4 | RSFCCSD4 | dict[str, int]] = [
    (RSFCCD, {"alpha": 4}, RSFCCD4),
    (RSFLCCD, {"alpha": 4}, RSFLCCD4),
    (RSFfpCCD, {"alpha": 4}, RSFfpCCD4),
    (RSFfpLCCD, {"alpha": 4}, RSFfpLCCD4),
    (RSFCCSD, {"alpha": 4}, RSFCCSD4),
    (RSFLCCSD, {"alpha": 4}, RSFLCCSD4),
    (RSFfpCCSD, {"alpha": 4}, RSFfpCCSD4),
    (RSFfpLCCSD, {"alpha": 4}, RSFfpLCCSD4),
]


@pytest.mark.parametrize("cls,kwargs,expected", test_data_instance)
def test_instance(
    cls: RSFCCD4 | RSFCCSD4,
    kwargs: dict[str, int],
    expected: RSFCCD4 | RSFCCSD4,
    linalg: list[DenseLinalgFactory]
    | list[DenseLinalgFactory | CholeskyLinalgFactory],
) -> None:
    """Check if __new__ overwrite works properly."""
    # some preliminaries
    lf = linalg(2)
    occ_model = AufbauOccModel(lf, nel=2)
    # Initialize empty class
    rsfcc = cls(lf, occ_model, **kwargs)

    assert isinstance(rsfcc, expected)
