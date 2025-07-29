#!/usr/bin/env python3

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
from pybest.wrappers import UHF

# Load the coordinates from file.
# Use the XYZ file from PyBEST's test data directory.
fn_xyz = context.get_fn("test/methyl.xyz")
mol = IOData.from_file(fn_xyz)

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
orb_b = lf.create_orbital()

# Decide how to occupy the orbitals (1 unpaired alpha electron)
occ_model = AufbauOccModel(basis, alpha=1)

# Converge UHF
hf = UHF(lf, occ_model)
hf_output = hf(kin, ne, eri, external, olp, orb_a, orb_b)

# Write SCF results to a molden file
hf_output.to_file("methyl-scf.molden")
