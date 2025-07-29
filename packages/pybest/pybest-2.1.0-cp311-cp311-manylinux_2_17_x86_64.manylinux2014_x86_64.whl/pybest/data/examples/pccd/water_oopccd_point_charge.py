#!/usr/bin/env python3

from pybest import context
from pybest.cc import RpCCDLCCSD
from pybest.gbasis import (
    compute_eri,
    compute_kinetic,
    compute_nuclear,
    compute_nuclear_pc,
    compute_nuclear_repulsion,
    compute_overlap,
    compute_point_charges,
    get_charges,
    get_gobasis,
)
from pybest.geminals import ROOpCCD
from pybest.linalg import DenseLinalgFactory
from pybest.localization import PipekMezey
from pybest.occ_model import AufbauOccModel
from pybest.part.mulliken import get_mulliken_operators
from pybest.wrappers import RHF

# Load the coordinates and point-charges from PyBEST's test data directory.
# ----------------------------------------------------------------
fn_xyz = context.get_fn("test/water_pc.xyz")
pc_xyz = context.get_fn("test/water_pc.pc")

# Get basis set and charges.
# ----------------------------------------------------------------
basis = get_gobasis("cc-pvdz", fn_xyz)
charges = get_charges(pc_xyz)

# Create a linalg factory instance
# ----------------------------------------------------------------
lf = DenseLinalgFactory(basis.nbasis)

# Compute standard QC integrals
# ----------------------------------------------------------------
olp = compute_overlap(basis)
kin = compute_kinetic(basis)
ne = compute_nuclear(basis)
eri = compute_eri(basis)
external = compute_nuclear_repulsion(basis)

# Calculate the interaction of point charges with electrons.
# ----------------------------------------------------------------
pc = compute_point_charges(basis, charges)

# Calculate the interaction of point charges with nuclei.
# ----------------------------------------------------------------
external += compute_nuclear_pc(basis, charges)


# Create alpha orbitals.
# ----------------------------------------------------------------
orb_a = lf.create_orbital()

# Choose an occupation model.
# ----------------------------------------------------------------
# If we do not specify the number of frozen core atomic orbitals (ncore),
# then ncore will be calculated automatically
occ_model = AufbauOccModel(basis, ncore=0)


# HF with the embedding_pot using the non-relativistic QC Hamiltonian.
# ----------------------------------------------------------------
hf_pc = RHF(lf, occ_model)
hf_pc_output = hf_pc(kin, ne, eri, external, pc, olp, orb_a)


# Define Mulliken projectors
# --------------------------
mulliken = get_mulliken_operators(basis)

# Pipek-Mezey localizaton
# -----------------------
loc = PipekMezey(lf, occ_model, mulliken)
loc(hf_pc_output, "occ")
loc(hf_pc_output, "virt")

#
# OO-pCCD module
#
oopccd = ROOpCCD(lf, occ_model)
oopccd_output = oopccd(kin, ne, eri, pc, hf_pc_output)

# oopCCD-LCCSD
oopccdlccsd = RpCCDLCCSD(lf, occ_model)
oopccdlccsd_output = oopccdlccsd(kin, ne, eri, pc, oopccd_output)
