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

"""Methods for the IP-EOM-CC module"""

# define test runner
from pybest._pytesttester import PytestTester

from .xip_fpcc import (
    RDIPfpCCD,
    RDIPfpCCSD,
    RDIPfpLCCD,
    RDIPfpLCCSD,
    RIPfpCCD,
    RIPfpCCSD,
    RIPfpLCCD,
    RIPfpLCCSD,
)
from .xip_pccd import RDIPpCCD, RIPpCCD
from .xip_rcc import (
    RDIPCCD,
    RDIPCCSD,
    RDIPLCCD,
    RDIPLCCSD,
    RIPCCD,
    RIPCCSD,
    RIPLCCD,
    RIPLCCSD,
)

__all__ = [
    "RDIPCCD",
    "RDIPCCSD",
    "RDIPLCCD",
    "RDIPLCCSD",
    "RIPCCD",
    "RIPCCSD",
    "RIPLCCD",
    "RIPLCCSD",
    "RDIPfpCCD",
    "RDIPfpCCSD",
    "RDIPfpLCCD",
    "RDIPfpLCCSD",
    "RDIPpCCD",
    "RIPfpCCD",
    "RIPfpCCSD",
    "RIPfpLCCD",
    "RIPfpLCCSD",
    "RIPpCCD",
]
test = PytestTester(__name__)
del PytestTester
