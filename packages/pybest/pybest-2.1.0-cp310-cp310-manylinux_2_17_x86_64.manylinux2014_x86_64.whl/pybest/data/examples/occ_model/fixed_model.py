#!/usr/bin/env python3

import numpy as np

from pybest import context
from pybest.gbasis import get_gobasis
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import FixedOccModel

# Occupation model with fixed (user-defined) occupations
# ------------------------------------------------------

# In the FixedOccModel occupation model, the alpha and beta orbitals are
# occupied with respect to user-defined occupation number vectors.
# The occupation numbers have to be any real number in the interval [0,1].
# Only the occupation numbers for all occupied orbitals have to be specified.
# All remaining (virtual) orbitals will be assigned occupation numbers of 0.
#
# The H2O molecule
# ----------------

# Load the coordinates from file for H2O.
# Use the XYZ file from PyBEST's test data directory.
fn_xyz = context.get_fn("test/water.xyz")

# Create a Gaussian basis set
basis = get_gobasis("cc-pvdz", fn_xyz)
#
# Use FixedOccModel occupation model
#
# Example 1: H2O with a total number of 10 electrons and occupying the 5
# energetically lowest orbitals (this is equivalent to the AufbauOccModel)
# defaults to restricted orbitals
occ_model = FixedOccModel(basis, occ_a=np.array([1, 1, 1, 1, 1]))

# Example 2: H2O+ with a 5 alpha and 4 beta electrons (Aufbau occupation)
# defaults to unrestricted orbitals
occ_model = FixedOccModel(
    basis,
    charge=1,
    occ_a=np.array([1, 1, 1, 1, 1]),
    occ_b=np.array([1, 1, 1, 1]),
)

# Example 3: H2O+ with a 5 alpha and 4 beta electrons (non Aufbau occupation)
# defaults to unrestricted orbitals
occ_model = FixedOccModel(
    basis,
    charge=1,
    occ_a=np.array([1, 1, 0, 0, 1, 1, 1]),
    occ_b=np.array([1, 1, 1, 0, 1]),
)

# Example 4: H2O with fractional occupation numbers in some orbitals (non Aufbau)
# defaults to restricted orbitals (enforces fractional occupations on alpha and
# beta orbitals)
occ_model = FixedOccModel(basis, occ_a=np.array([1, 1, 0.3, 0, 0.7, 1, 1]))

# Example 5: H2O with fractional occupation numbers in some orbitals (non Aufbau)
# enforces unrestricted orbitals (enforces fractional occupations on alpha and
# beta orbitals)
occ_model = FixedOccModel(
    basis, unrestricted=True, occ_a=np.array([1, 1, 0.3, 0, 0.7, 1, 1])
)

# The NO molecule
# ---------------

# Load the coordinates from file for NO.
# Use the XYZ file from PyBEST's test data directory.
fn_xyz = context.get_fn("test/no.xyz")

# Create a Gaussian basis set
basis = get_gobasis("cc-pvdz", fn_xyz)
#
# Use FixedOccModel occupation model
#
# Example 1: NO molecule with a total number of 15 electrons (since we have an
# odd number of electrons, both occ_a and occ_b need to be specified).
# defaults to unrestricted orbitals
occ_model = FixedOccModel(
    basis,
    occ_a=np.array([1, 1, 1, 1, 1, 1, 1, 0, 1]),
    occ_b=np.array([1, 1, 1, 1, 1, 1, 1]),
)


# Using an LF instance: since we have to pass occ_a, we do not need to pass nel
# -----------------------------------------------------------------------------

# Create an LF instance for 24 orbitals and 10 electrons
lf = DenseLinalgFactory(24)
#
# Use FixedOccModel occupation model
#
# restricted orbitals with 10 electrons and fractional occupation numbers
# defaults to restricted orbitals
occ_model = FixedOccModel(lf, occ_a=np.array([1, 1, 0.3, 0, 0.7, 1, 1]))

# unrestricted orbitals with 15 electrons (8 alpha and 7 beta)
# defaults to unrestricted orbitals
occ_model = FixedOccModel(
    lf,
    occ_a=np.array([1, 1, 1, 1, 1, 1, 1, 0, 1]),
    occ_b=np.array([1, 1, 1, 1, 1, 1, 1]),
)
