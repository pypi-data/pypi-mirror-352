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

"""Methods for the rsf-eom cc module"""

# define test runner
from pybest._pytesttester import PytestTester

from .eff_ham_ccd import EffectiveHamiltonianRCCD
from .eff_ham_ccsd import EffectiveHamiltonianRCCSD, EffectiveHamiltonianRLCCSD
from .xrsf_cc import RSFCCD, RSFCCSD, RSFLCCD, RSFLCCSD
from .xrsf_fpcc import RSFfpCCD, RSFfpCCSD, RSFfpLCCD, RSFfpLCCSD

__all__ = [
    "RSFCCD",
    "RSFCCSD",
    "RSFLCCD",
    "RSFLCCSD",
    "EffectiveHamiltonianRCCD",
    "EffectiveHamiltonianRCCSD",
    "EffectiveHamiltonianRLCCSD",
    "RSFfpCCD",
    "RSFfpCCSD",
    "RSFfpLCCD",
    "RSFfpLCCSD",
]

test = PytestTester(__name__)
del PytestTester
