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
"""Methods for the cc module"""

# define test runner
from pybest._pytesttester import PytestTester

from .rccd import RCCD
from .rccs import RCCS, RpCCDCCS
from .rccsd import RCCSD
from .rfpcc import RfpCCD, RfpCCSD
from .rlccd import RHFLCCD, RLCCD, RfpLCCD, RpCCDLCCD
from .rlccsd import RHFLCCSD, RLCCSD, RfpLCCSD, RpCCDLCCSD
from .rtcc import RtCCD, RtCCSD

__all__ = [
    "RCCD",
    "RCCS",
    "RCCSD",
    "RHFLCCD",
    "RHFLCCSD",
    "RLCCD",
    "RLCCSD",
    "RfpCCD",
    "RfpCCSD",
    "RfpLCCD",
    "RfpLCCSD",
    "RpCCDCCS",
    "RpCCDLCCD",
    "RpCCDLCCSD",
    "RtCCD",
    "RtCCSD",
]

test = PytestTester(__name__)
del PytestTester
