#!/usr/bin/env python3

from pybest import context
from pybest.gbasis import (
    compute_nuclear_repulsion,
    compute_overlap,
    get_gobasis,
)
from pybest.linalg import DenseLinalgFactory
from pybest.scalar_relativistic_hamiltonians import X2C

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

# Create an X2C instance
# ----------------------
x2c_hamiltonian = X2C(basis)
# Compute the X2C Hamiltonian
# ---------------------------
x2c_ints = x2c_hamiltonian()

# Compute overlap matrix of atom-centered basis set
# -------------------------------------------------
olp = compute_overlap(basis)

# Create orbitals that store the AO/MO coefficients
# -------------------------------------------------
orb = lf.create_orbital()
