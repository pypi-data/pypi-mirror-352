#!/usr/bin/env python3

from pybest import context
from pybest.cc import RpCCDLCCSD
from pybest.gbasis import (
    compute_eri,
    compute_kinetic,
    compute_nuclear,
    compute_nuclear_repulsion,
    compute_overlap,
    compute_static_embedding,
    get_embedding,
    get_gobasis,
)
from pybest.geminals import ROOpCCD
from pybest.linalg import DenseLinalgFactory
from pybest.localization import PipekMezey
from pybest.occ_model import AufbauOccModel
from pybest.part.mulliken import get_mulliken_operators
from pybest.wrappers import RHF

# Load the coordinates and embedding_pot from PyBEST's test data directory.
# ----------------------------------------------------------------
fn_xyz = context.get_fn("test/water_emb.xyz")
embedding_pot = context.get_fn("test/water_emb.emb")

# Get basis set and static emebedding potential.
# ----------------------------------------------------------------
basis = get_gobasis("cc-pvdz", fn_xyz)
embedding_pot = get_embedding(embedding_pot)

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

# Compute static embedding potential generated with PyADF.
# ----------------------------------------------------------------
emb = compute_static_embedding(basis, embedding_pot)

# Create alpha orbitals.
# ----------------------------------------------------------------
orb_a = lf.create_orbital()

# Choose an occupation model.
# ----------------------------------------------------------------
# If we do not specify the number of frozen core orbitals (ncore),
# then ncore will be calculated automatically
occ_model = AufbauOccModel(basis, ncore=0)


# HF with the embedding_pot using the non-relativistic QC Hamiltonian.
# ----------------------------------------------------------------
hf_emb = RHF(lf, occ_model)
hf_emb_output = hf_emb(kin, ne, eri, external, emb, olp, orb_a)


# Define Mulliken projectors
# --------------------------
mulliken = get_mulliken_operators(basis)

# Pipek-Mezey localizaton
# -----------------------
loc = PipekMezey(lf, occ_model, mulliken)
loc(hf_emb_output, "occ")
loc(hf_emb_output, "virt")

#
# OO-pCCD module
#
oopccd = ROOpCCD(lf, occ_model)
oopccd_output = oopccd(kin, ne, eri, emb, hf_emb_output)

# oopCCD-LCCSD
oopccdlccsd = RpCCDLCCSD(lf, occ_model)
oopccdlccsd_output = oopccdlccsd(kin, ne, eri, emb, oopccd_output)
