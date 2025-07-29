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
from pybest.scalar_relativistic_hamiltonians import DKHN

# Load the coordinates from PyBEST's test data directory
# ------------------------------------------------------
fn_xyz = context.get_fn("test/h2.xyz")

# Get basis set
# -------------
basis = get_gobasis("cc-pvdz", fn_xyz)

# Create a linalg factory instance
# --------------------------------
lf = DenseLinalgFactory(basis.nbasis)

# Create a DKH instance
# ---------------------
dkh_hamiltonian = DKHN(basis)
# Compute the DKH Hamiltonian of second order (default)
# -----------------------------------------------------
dkh2 = dkh_hamiltonian()

# Compute standard QC integrals
# -----------------------------
olp = compute_overlap(basis)
eri = compute_eri(basis)
external = compute_nuclear_repulsion(basis)

# Create alpha orbitals
# ---------------------
orb_a = lf.create_orbital()

# Choose an occupation model
# --------------------------
occ_model = AufbauOccModel(basis)
