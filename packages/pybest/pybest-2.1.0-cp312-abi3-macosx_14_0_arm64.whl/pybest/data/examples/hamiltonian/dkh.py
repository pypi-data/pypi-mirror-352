#!/usr/bin/env python3

from pybest import context
from pybest.gbasis import (
    compute_nuclear_repulsion,
    compute_overlap,
    get_gobasis,
)
from pybest.linalg import DenseLinalgFactory
from pybest.scalar_relativistic_hamiltonians import DKHN

# DKH2 Hamiltonian for the U dimer
# --------------------------------

# Define coordinate file
# ----------------------
fn_xyz = context.get_fn("test/u2.xyz")

# Create a Gaussian basis set
# ---------------------------
basis = get_gobasis("ano-rcc-vdz", fn_xyz)

# Create a linalg factory instance
# --------------------------------
lf = DenseLinalgFactory(basis.nbasis)

# Compute standard QC integrals
# -----------------------------
nuc = compute_nuclear_repulsion(basis)
# ERI are not computed in this example
external = compute_nuclear_repulsion(basis)

# Create a DKH instance
# ---------------------
dkh_hamiltonian = DKHN(basis)
# Compute the DKH Hamiltonian of second order (default)
# -----------------------------------------------------
dkh2_ints = dkh_hamiltonian()

# Compute overlap matrix of atom-centered basis set
# -------------------------------------------------
olp = compute_overlap(basis)

# Create orbitals that store the AO/MO coefficients
# -------------------------------------------------
orb = lf.create_orbital()
