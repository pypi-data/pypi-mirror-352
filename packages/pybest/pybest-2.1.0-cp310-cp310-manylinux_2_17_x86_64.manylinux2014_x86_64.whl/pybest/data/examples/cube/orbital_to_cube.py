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
from pybest.geminals import ROOpCCD
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel
from pybest.wrappers import RHF

# Load the coordinates from file
# Use the XYZ file from PyBEST's test data directory
fn_xyz = context.get_fn("test/water.xyz")

# Create a Gaussian basis set
basis = get_gobasis("cc-pvdz", fn_xyz)

# Create a linalg basis
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

# Hartree-Fock calculation
# ------------------------

# Converge RHF
hf = RHF(lf, occ_model)
hf_output = hf(kin, ne, eri, external, olp, orb_a)

# Specify list of orbitals that are to be dumped in the .cube format
# Indexing starts with 1 (not 0). Add orbital #5 and #6 to list
hf_output.indices_mos = [5, 6]
# Dump cube files; each orbital will be dump as "water_rhf_[mo].cube", where
# "[mo]" is one index in the list hf_output.indices_mos
hf_output.to_file("water_rhf.cube")

# OO-pCCD calculation
# -------------------

# Converge pCCD
pccd = ROOpCCD(lf, occ_model)
pccd_output = pccd(kin, ne, eri, hf_output)

# Specify list of orbitals that are to be dumped in the .cube format
pccd_output.indices_mos = [5, 6]
# Dump cube files; each orbital will be dump as "water_pccd_[mo].cube", where
# "[mo]" is one index in the list hf_output.indices_mos
pccd_output.to_file("water_pccd.cube")
