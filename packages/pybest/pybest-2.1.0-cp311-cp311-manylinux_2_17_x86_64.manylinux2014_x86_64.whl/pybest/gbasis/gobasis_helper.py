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
"""Gaussian orbital basis set module."""

__all__ = [
    "shell_int2str",
    "shell_str2int",
]


def shell_str2int(s, pure=False):
    """Convert a string into a list of contraction types"""
    if pure:
        d = {"s": 0, "p": 1, "d": 2, "f": 3, "g": 4, "h": 5, "i": 6}
    else:
        d = {"s": 0, "p": 1, "d": -2, "f": -3, "g": -4, "h": -5, "i": -6}
    return [d[c] for c in s.lower()]


def shell_int2str(shell_type):
    """Convert a shell type into a character"""
    return {0: "s", 1: "p", 2: "d", 3: "f", 4: "g", 5: "h", 6: "i"}[
        abs(shell_type)
    ]
