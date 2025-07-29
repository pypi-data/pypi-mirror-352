#!/usr/bin/env python3

import numpy as np

from pybest import context
from pybest.gbasis import (
    compute_eri,
    compute_kinetic,
    compute_nuclear,
    compute_nuclear_repulsion,
    compute_overlap,
    get_gobasis,
)
from pybest.iodata import IOData
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel
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
kin = compute_kinetic(basis)
ne = compute_nuclear(basis)
eri = compute_eri(basis)
external = compute_nuclear_repulsion(basis)

# Create alpha orbitals
orb_a = lf.create_orbital()

# Decide how to occupy the orbitals (5 alpha electrons)
occ_model = AufbauOccModel(basis)

# Converge RHF
hf = RHF(lf, occ_model)

# the order of the arguments does not matter
hf_output = hf(kin, ne, eri, external, olp, orb_a)

# Write SCF results to a molden file
hf_output.to_file("water-scf.molden")

# Restart RHF
hf = RHF(lf, occ_model)
# we still need to provide some inital guess orbitals
# results are stored in pybest-results directory
hf_output = hf(
    kin,
    ne,
    eri,
    external,
    olp,
    orb_a,
    restart="pybest-results/checkpoint_scf.h5",
)

# Read in orbitals and modify them
restart = IOData.from_file("pybest-results/checkpoint_scf.h5")

# Swap HOMO-LUMO orbitals (Python indexing, starts with 0)
swaps = np.array([[4, 5]])
# Only swap AO/MO coefficients
restart.orb_a.swap_orbitals(swaps, skip_occs=True, skip_energies=True)

# Do RHF calculation using those orbitals
hf = RHF(lf, occ_model)
hf_output = hf(kin, ne, eri, external, restart.olp, restart.orb_a)
