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
# 2024: This module has been originally written by Katharina Boguslawski
# 2025: Added support of REACCD, REACCSD, REALCCD, REALCCSD, REAfpCCD,
#       REAfpCCSD, REAfpLCCD, REAfpLCCSD (Saman Behjou)

"""Methods for the XEA-EOM-CC module"""

# define test runner
from pybest._pytesttester import PytestTester

from .xea_pccd import RDEApCCD, REApCCD
from .xea_rcc import (
    REACCD,
    REACCSD,
    REALCCD,
    REALCCSD,
    REAfpCCD,
    REAfpCCSD,
    REAfpLCCD,
    REAfpLCCSD,
)

__all__ = [
    "REACCD",
    "REACCSD",
    "REALCCD",
    "REALCCSD",
    "RDEApCCD",
    "REAfpCCD",
    "REAfpCCSD",
    "REAfpLCCD",
    "REAfpLCCSD",
    "REApCCD",
]

test = PytestTester(__name__)
del PytestTester
