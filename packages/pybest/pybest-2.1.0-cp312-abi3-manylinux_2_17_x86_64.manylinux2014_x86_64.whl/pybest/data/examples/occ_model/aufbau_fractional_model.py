#!/usr/bin/env python3

from pybest import context
from pybest.gbasis import get_gobasis
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import FractionalOccModel

# Aufbau occupation model allowing for fractional occupation numbers in the
# highest occupied molecular orbital
# -------------------------------------------------------------------------

# In the FractionalOccModel occupation model, the HOMO of the alpha and beta
# electrons can be occupied with a fraction of an electron. During the
# SCF optimization, this fractional occupation numbers are kept fixed.
#
# The H2O molecule
# ----------------

# Load the coordinates from file for H2O.
# Use the XYZ file from PyBEST's test data directory.
fn_xyz = context.get_fn("test/water.xyz")

# Create a Gaussian basis set
basis = get_gobasis("cc-pvdz", fn_xyz)
#
# Use Aufbau occupation model for fractional occupation numbers
#
# Example 1: H2O with 5.5 alpha and 4.5 beta electrons (sums up to 10 electrons)
# defaults to unrestricted orbitals
occ_model = FractionalOccModel(basis, nocc_a=5.5, nocc_b=4.5)

# Example 2: H2O+ with a 4.5 alpha and beta electrons (sums up 9 electrons)
# defaults to restricted orbitals
occ_model = FractionalOccModel(basis, charge=1, nocc_a=4.5, ncore=0)

# Example 2: H2O+ with a 4.5 alpha and beta electrons (sums up 9 electrons)
# enforce unrestricted orbitals
occ_model = FractionalOccModel(basis, charge=1, nocc_a=4.5, unrestricted=True)


# The NO molecule
# ---------------

# Load the coordinates from file for NO.
# Use the XYZ file from PyBEST's test data directory.
fn_xyz = context.get_fn("test/no.xyz")

# Create a Gaussian basis set
basis = get_gobasis("cc-pvdz", fn_xyz)
#
# Use Aufbau occupation model for fractional occupation numbers
#
# Example 1: NO with a 7.5 alpha and beta electrons (sums up 15 electrons)
# defaults to restricted orbitals
occ_model = FractionalOccModel(basis, nocc_a=7.5)

# Example 1: NO with a 7.5 alpha and beta electrons (sums up 15 electrons)
# enforce unrestricted orbitals
occ_model = FractionalOccModel(basis, nocc_a=7.5, unrestricted=True)


# Using an LF instance: since we have to pass nocc_a, we do not need to pass nel
# ------------------------------------------------------------------------------

# Create an LF instance for 24 orbitals and 10 electrons
lf = DenseLinalgFactory(24)
#
# Use Aufbau occupation model for fractional occupation numbers
#
# Select default parameters
# restricted orbitals with 15 electrons (7.5 alpha and 7.5 beta)
# defaults to restricted orbitals
occ_model = FractionalOccModel(lf, nocc_a=7.5)

# enforce unrestricted representation
occ_model = FractionalOccModel(lf, nocc_a=7.5, unrestricted=True)

# unrestricted orbitals with 15 electrons (9.1 alpha and 5.9 beta)
# defaults to unrestricted orbitals
occ_model = FractionalOccModel(lf, nocc_a=9.1, nocc_b=5.9)

# For an LF instance, we can have a fractional number of electrons
# unrestricted orbitals with 15.1 electrons (9.2 alpha and 5.9 beta)
# defaults to unrestricted orbitals
occ_model = FractionalOccModel(lf, nocc_a=9.2, nocc_b=5.9)
