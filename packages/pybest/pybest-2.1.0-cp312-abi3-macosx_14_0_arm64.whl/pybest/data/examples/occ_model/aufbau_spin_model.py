#!/usr/bin/env python3

from pybest import context
from pybest.gbasis import get_gobasis
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauSpinOccModel

# Aufbau occupation model for unrestricted wave functions
# -------------------------------------------------------

# In the AufbauSpinOccModel occupation model, the alpha and beta orbitals are
# occupied with respect to their energy. That is, the energetically lowest
# (alpha and beta) orbitals are occupied first. Only the total number of
# electrons is fixed, while the number of electrons in each spin channel can
# change during the SCF optimization.
#
# The H2O molecule
# ----------------

# Load the coordinates from file for H2O.
# Use the XYZ file from PyBEST's test data directory.
fn_xyz = context.get_fn("test/water.xyz")

# Create a Gaussian basis set
basis = get_gobasis("cc-pvdz", fn_xyz)
#
# Use Aufbau occupation model for unrestricted wave functions
#
# Example 1: H2O with a total number of 10 electrons
# defaults to unrestricted orbitals
occ_model = AufbauSpinOccModel(basis)

# Example 2: H2O+ with a total number of 9 electrons
# defaults to unrestricted orbitals
occ_model = AufbauSpinOccModel(basis, charge=1)


# The NO molecule
# ---------------

# Load the coordinates from file for NO.
# Use the XYZ file from PyBEST's test data directory.
fn_xyz = context.get_fn("test/no.xyz")

# Create a Gaussian basis set
basis = get_gobasis("cc-pvdz", fn_xyz)
#
# Use Aufbau occupation model for unrestricted wave functions
#
# Example 1: NO molecule with a total number of 15 electrons
# defaults to unrestricted orbitals
occ_model = AufbauSpinOccModel(basis)


# Using an LF instance: we need to pass the number of electrons nel
# -----------------------------------------------------------------

# Create an LF instance for 24 orbitals and 10 electrons
lf = DenseLinalgFactory(24)
#
# Use Aufbau occupation model for unrestricted wave functions
#
# Select default parameters
# 15 electrons
# defaults to unrestricted orbitals
occ_model = AufbauSpinOccModel(lf, nel=15)
