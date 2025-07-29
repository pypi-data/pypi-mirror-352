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
# 2020-07-01: updated unit value for meter
# 2022-11-25: updated unit value for meter according to CODATA 2018

"""Conversion from and to atomic units

Internally PyBEST always uses atomic units. Atomic units are consistent,
similar to the SI unit system: one does not need conversion factors in the
middle of a computation. This choice facilitates the programming and reduces
accidental bugs.

References for the conversion values:

* B. J. Mohr and B. N. Taylor,
  CODATA recommended values of the fundamental physical
  constants: 1998, Rev. Mod. Phys. 72(2), 351 (2000)
* The NIST Reference on Constants, Units, and Uncertainty
  (http://physics.nist.gov/cuu/Constants/index.html)
* 1 calorie = 4.184 Joules

**Conventions followed by this module:**

Let foo be is the value of an external unit in internal (atomic) units. The
way to use this unit is as follows: ``5*foo`` litterally means `five times
foo`. The result of this operation is a floating point number for this value
in atomic units.

**Examples:**

If you want to have a distance of five angstrom in internal units:
``5*angstrom``.

If you want to convert a length of 5 internal units to angstrom:
``5/angstrom``.

**Remarks:**

It is highly recommended to perform unit conversions only when data is read
from the input or data is written to the output. It may also be useful in
`input scripts` that use PyBEST. Do not perform any unit conversion in other
parts of the program.

An often recurring question is how to convert a frequency in internal units
to a spectroscopic wavenumber in inverse centimeters. This is how it can be
done::

  >>> from pybest import centimeter, lightspeed
  >>> invcm = lightspeed/centimeter
  >>> freq = 0.00320232
  >>> print freq/invcm

These are the conversion constants defined in this module:

"""

from pybest.constants import avogadro, lightspeed, pi

# *** Generic ***
au = 1.0


# *** Charge ***

coulomb = 1.0 / 1.602176462e-19

# *** Mass ***

kilogram = 1.0 / 9.10938188e-31

gram = 1.0e-3 * kilogram
miligram = 1.0e-6 * kilogram
unified = 1.0e-3 * kilogram / avogadro
amu = unified

# *** Length ***
# the 2014 CODATA reference set, available at DOI 10.1103/RevModPhys.88.035009
# meter = 1.0 / 0.52917721067e-10
# the 2018 CODATA reference set, available at DOI 10.1103/RevModPhys.93.025010
meter = 1.0 / 0.529177210903e-10

decimeter = 1.0e-1 * meter
centimeter = 1.0e-2 * meter
milimeter = 1.0e-3 * meter
micrometer = 1.0e-6 * meter
nanometer = 1.0e-9 * meter
angstrom = 1.0e-10 * meter
picometer = 1.0e-12 * meter

# *** Volume ***

liter = decimeter**3

# *** Energy ***

joule = 1 / 4.35974381e-18

calorie = 4.184 * joule
kjmol = 1.0e3 * joule / avogadro
kcalmol = 1.0e3 * calorie / avogadro
invcm = 2 * pi * lightspeed / centimeter
electronvolt = (1.0 / coulomb) * joule
# NOTE: https://en.wikipedia.org/wiki/Boltzmann_constant#Value_in_different_units
ekelvin = 3.1668154051341965e-06
rydberg = 0.5

# *** Force ***

newton = joule / meter

# *** Angles ***

deg = pi / 180.0
rad = 1.0

# *** Time ***

second = 1 / 2.418884326500e-17

nanosecond = 1e-9 * second
femtosecond = 1e-15 * second
picosecond = 1e-12 * second

# *** Frequency ***

hertz = 1 / second

# *** Pressure ***

pascal = newton / meter**2
bar = 100000 * pascal
atm = 1.01325 * bar

# *** Temperature ***

kelvin = 1.0

# *** Multipole ***

debye = coulomb * meter**2 / second / lightspeed * 1e-21
buckingham = debye * angstrom

# *** Current ***

ampere = coulomb / second


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
    "ampere",
    "amu",
    "angstrom",
    "atm",
    "au",
    "bar",
    "buckingham",
    "calorie",
    "centimeter",
    "coulomb",
    "debye",
    "decimeter",
    "deg",
    "ekelvin",
    "electronvolt",
    "femtosecond",
    "gram",
    "hertz",
    "invcm",
    "joule",
    "kcalmol",
    "kelvin",
    "kilogram",
    "kjmol",
    "liter",
    "meter",
    "micrometer",
    "miligram",
    "milimeter",
    "nanometer",
    "nanosecond",
    "newton",
    "pascal",
    "picometer",
    "picosecond",
    "rad",
    "rydberg",
    "second",
    "unified",
]

del lines
