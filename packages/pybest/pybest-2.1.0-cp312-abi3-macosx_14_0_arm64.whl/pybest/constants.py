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
# This implementation has been taken from `Horton 2.0.0`.
# However, this file has been updated and debugged. Compatibility with Horton is NOT
# guaranteed.
# Its current version contains updates from the PyBEST developer team.
#
# Detailed changes (see also CHANGELOG):
# 2020-07-01: update to new python features, including f-strings
# 2025-02-18: updated alpha value to 1/c (Kacper Cieślak)

"""Physicochemical constants in atomic units

These are the physical constants defined in this module (in atomic units):

"""

boltzmann = 3.1668154051341965e-06
avogadro = 6.0221415e23
planck = 6.2831853071795864769
pi = 3.141592653589793
# Morel, L., Yao, Z., Cladé, P. et al. Nature 588, 61-65 (2020). https://doi.org/10.1038/s41586-020-2964-7
lightspeed = 137.035999206
# alpha = 1/c
alpha = 1 / lightspeed

# Other constants that rule the performance/behavior of pybest
# If implemented, intermediates will be dumped to disk if number of active
# orbitals is larger than the following number
CACHE_DUMP_ACTIVE_ORBITAL_THRESHOLD = 300


# automatically spice up the docstrings

lines = [
    "    ================  ==================",
    "    Name              Value             ",
    "    ================  ==================",
]

for key, value in sorted(globals().items()):
    if not isinstance(value, float):
        continue
    lines.append(f"    {key:16}  {value:.10e}")
lines.append("    ================  ==================")

__doc__ += "\n".join(lines)  # noqa

__all__ = [
    "CACHE_DUMP_ACTIVE_ORBITAL_THRESHOLD",
    "alpha",
    "avogadro",
    "boltzmann",
    "lightspeed",
    "pi",
    "planck",
]
