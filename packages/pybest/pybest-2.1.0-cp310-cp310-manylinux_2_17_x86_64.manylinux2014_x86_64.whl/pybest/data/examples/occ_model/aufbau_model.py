#!/usr/bin/env python3

from pybest import context
from pybest.gbasis import get_gobasis
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel

# Aufbau occupation model
# -----------------------

# The H2O molecule
# ----------------

# Load the coordinates from file for H2O.
# Use the XYZ file from PyBEST's test data directory.
fn_xyz = context.get_fn("test/water.xyz")

# Create a Gaussian basis set
basis = get_gobasis("cc-pvdz", fn_xyz)
#
# Use Aufbau occupation model to occupy orbitals
#
# If we do not specify the number of frozen core orbitals (ncore),
# then ncore will be calculated automatically
#
# Example 1: H2O with only doubly occupied orbitals
# defaults to restricted orbitals
occ_model = AufbauOccModel(basis, ncore=0)

# Example 2: H2O+ with one singly occupied (alpha) orbital
# defaults to unrestricted orbitals with one unpaired alpha electron
occ_model = AufbauOccModel(basis, charge=1, ncore=0)

# Example 3: H2O with five alpha and five beta electrons
# enforce unrestricted orbitals
occ_model = AufbauOccModel(basis, unrestricted=True, ncore=0)

# Example 4: H2O+ with three singly occupied (alpha) orbitals
# defaults to unrestricted orbitals
occ_model = AufbauOccModel(basis, charge=1, alpha=3, ncore=0)


# The NO molecule
# ---------------

# Load the coordinates from file for NO.
# Use the XYZ file from PyBEST's test data directory.
fn_xyz = context.get_fn("test/no.xyz")

# Create a Gaussian basis set
basis = get_gobasis("cc-pvdz", fn_xyz)
#
# Use Aufbau occupation model to occupy orbitals
#
# Example 1: NO molecule
# defaults to unrestricted orbitals with one unpaired electron
occ_model = AufbauOccModel(basis, ncore=0)


# Using an LF instance: here, we have to pass the number of electrons
# -------------------------------------------------------------------

# Create an LF instance for 24 orbitals and 10 electrons
lf = DenseLinalgFactory(24)
#
# Use Aufbau occupation model to occupy orbitals
#
# Select default parameters
# restricted orbitals with 10 electrons
occ_model = AufbauOccModel(lf, nel=10, ncore=0)

# enforce unrestricted representation
occ_model = AufbauOccModel(lf, nel=10, unrestricted=True, ncore=0)

# unrestricted orbitals with 9 electrons (with 1 unpaired electron)
# defaults to unrestricted orbitals
occ_model = AufbauOccModel(lf, nel=9, ncore=0)

# unrestricted orbitals with 9 electrons (with 3 unpaired electrons)
# defaults to unrestricted orbitals
occ_model = AufbauOccModel(lf, nel=9, alpha=3, ncore=0)
