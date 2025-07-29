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

from __future__ import annotations

from collections.abc import Sequence

import pytest

from pybest.rsf_eom.eff_ham_ccsd import (
    EffectiveHamiltonianRCCSD,
    EffectiveHamiltonianRLCCSD,
)
from pybest.rsf_eom.eff_ham_ccsd_base import EffectiveHamiltonianRCCSDBase
from pybest.rsf_eom.rsf_ccd4 import RSFCCD4, RSFLCCD4, RSFfpCCD4
from pybest.rsf_eom.rsf_ccsd4 import (
    RSFCCSD4,
    RSFLCCSD4,
    RSFfpCCSD4,
    RSFfpLCCSD4,
)

ccd: Sequence[RSFCCD4] = [RSFCCD4, RSFLCCD4, RSFfpCCD4]


@pytest.fixture(scope="class", params=ccd)
def rsfccd_flavor(request) -> RSFCCD4:
    flavor = request.param
    return flavor


ccsd: Sequence[RSFCCSD4 | EffectiveHamiltonianRCCSDBase] = [
    [RSFCCSD4, EffectiveHamiltonianRCCSD],
    [RSFLCCSD4, EffectiveHamiltonianRLCCSD],
    [RSFfpCCSD4, EffectiveHamiltonianRCCSD],
    [RSFfpLCCSD4, EffectiveHamiltonianRLCCSD],
]


@pytest.fixture(scope="class", params=ccsd)
def rsfccsd_flavor(request) -> tuple[RSFCCSD4, EffectiveHamiltonianRCCSDBase]:
    flavor, eff_ham = request.param
    return flavor, eff_ham
