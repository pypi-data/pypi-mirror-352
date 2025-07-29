#!/usr/bin/env python3

from pybest import context
from pybest.gbasis import get_gobasis
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import FermiOccModel

# Aufbau occupation model with Fermi smearing
# -------------------------------------------

# In the FermiOccModel occupation model, the alpha and beta orbitals are
# occupied with respect to their energy. That is, the energetically lowest
# (alpha and beta) orbitals are occupied first, while a Fermi distribution is
# applied to the occupation numbers. Thus, the occupation numbers are real
# numbers in the range [0, 1] for each spin channel. During the SCF
# optimization the temperature of the Fermi distribution is (by default)
# gradually lowered.
#

# The H2O molecule
# ----------------

# Load the coordinates from file for H2O.
# Use the XYZ file from PyBEST's test data directory.
fn_xyz = context.get_fn("test/water.xyz")

# Create a Gaussian basis set
basis = get_gobasis("cc-pvdz", fn_xyz)

# Use Aufbau occupation model to occupy orbitals, while occupation numbers are
# assigned according to a Fermi distribution
#
# Example 1: H2O with default parameters (T=250K, dT=50K, method=pfon - pseudo
# fractional occupation numbers)
# defaults to restricted orbitals
occ_model = FermiOccModel(basis)

# Example 2: H2O+ with one (in total) alpha electron and default parameters
# (T=250K, dT=50K, method=pfon - pseudo fractional occupation numbers)
# defaults to unrestricted orbitals
occ_model = FermiOccModel(basis, charge=1)

# Example 3: H2O with default parameters (T=250K, dT=50K, method=pfon - pseudo
# fractional occupation numbers)
# enforce unrestricted orbitals
occ_model = FermiOccModel(basis, unrestricted=True)

# Example 4: H2O+ with (in total) three unpaired alpha electrons and default
# parameters (T=250K, dT=50K, method=pfon - pseudo fractional occupation numbers)
# defaults to unrestricted orbitals
occ_model = FermiOccModel(basis, charge=1, alpha=3)

# Example 5: H2O+ with (in total) three unpaired alpha electrons and default
# parameters (T=500K, dT=25K, method=fon - fractional occupation numbers)
# defaults to unrestricted orbitals
occ_model = FermiOccModel(
    basis, charge=1, alpha=3, temperature=500, delta_t=25, method="fon"
)

# The NO molecule
# ---------------

# Load the coordinates from file for NO.
# Use the XYZ file from PyBEST's test data directory.
fn_xyz = context.get_fn("test/no.xyz")

# Create a Gaussian basis set
basis = get_gobasis("cc-pvdz", fn_xyz)

# Use Aufbau occupation model to occupy orbitals, while occupation numbers are
# assigned according to a Fermi distribution

# Example 1: NO molecule
# defaults to unrestricted orbitals with one unpaired electron (in total)
occ_model = FermiOccModel(basis)

# Example 2: NO molecule
# parameters (T=500K, dT=25K, method=fon - fractional occupation numbers)
# defaults to unrestricted orbitals with one unpaired electron (in total)
occ_model = FermiOccModel(basis, temperature=500, delta_t=25, method="fon")

# Example 3: NO molecule with 3 unpaired electrons
# parameters (T=500K, dT=25K, method=fon - fractional occupation numbers)
# defaults to unrestricted orbitals with one unpaired electron (in total)
occ_model = FermiOccModel(
    basis, alpha=3, temperature=500, delta_t=25, method="fon"
)

# Using an LF instance: here, we have to pass the number of electrons
# -------------------------------------------------------------------

# Create an LF instance for 24 orbitals and 10 electrons
lf = DenseLinalgFactory(24)
#
# Use Aufbau occupation model to occupy orbitals
#
# Select default parameters
# restricted orbitals with 10 electrons
occ_model = FermiOccModel(lf, nel=10)

# enforce unrestricted representation
occ_model = FermiOccModel(lf, nel=10, unrestricted=True)

# unrestricted orbitals with 9 electrons (with 1 unpaired electron)
# defaults to unrestricted orbitals
occ_model = FermiOccModel(lf, nel=9)

# unrestricted orbitals with 9 electrons (with 3 unpaired electrons in total)
# defaults to unrestricted orbitals
occ_model = FermiOccModel(lf, nel=9, alpha=3)
