#!/usr/bin/env python3

from pybest import context
from pybest.gbasis import (
    compute_eri,
    compute_nuclear_repulsion,
    compute_overlap,
    get_gobasis,
)
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel
from pybest.scalar_relativistic_hamiltonians import dkhn
from pybest.wrappers import RHF

# Hartree-Fock calculation
# ------------------------

# Load the coordinates from file.
# Use the XYZ file from PyBEST's test data directory.
fn_xyz = context.get_fn("test/water.xyz")

# Create a Gaussian basis set
basis = get_gobasis("cc-pvdz", fn_xyz)

# Create a linalg factory
lf = DenseLinalgFactory(basis.nbasis)

# Compute integrals
olp = compute_overlap(basis)
dkh_hamiltonian = dkhn(basis)
eri = compute_eri(basis)
external = compute_nuclear_repulsion(basis)

# Create alpha orbitals
orb_a = lf.create_orbital()

# Decide how to occupy the orbitals (5 alpha electrons)
occ_model = AufbauOccModel(basis)

# Converge RHF
hf = RHF(lf, occ_model)
dkh2 = dkh_hamiltonian()
# the order of the arguments does not matter
hf_output = hf(dkh2, eri, external, olp, orb_a)

# Write SCF results to a molden file
hf_output.to_file("water-scf.molden")
