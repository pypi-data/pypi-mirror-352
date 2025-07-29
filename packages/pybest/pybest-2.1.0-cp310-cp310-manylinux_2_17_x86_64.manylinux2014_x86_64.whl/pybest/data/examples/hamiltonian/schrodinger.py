#!/usr/bin/env python3

from pybest import context
from pybest.gbasis import (
    compute_dipole,
    compute_eri,
    compute_kinetic,
    compute_nuclear,
    compute_nuclear_repulsion,
    compute_overlap,
    compute_quadrupole,
    get_gobasis,
)
from pybest.linalg import DenseLinalgFactory
from pybest.utility import get_com

# Molecular Schroedinger Hamiltonian for the water molecule
# ---------------------------------------------------------

# Define coordinate file
# ----------------------------------------------------
fn_xyz = context.get_fn("test/water.xyz")

# Create a Gaussian basis set
# ---------------------------
basis = get_gobasis("cc-pvdz", fn_xyz)

# Create a linalg factory
# -----------------------
lf = DenseLinalgFactory(basis.nbasis)

# Compute integrals in the atom-centered Gaussian basis set
# ---------------------------------------------------------
kin = compute_kinetic(basis)
ne = compute_nuclear(basis)
eri = compute_eri(basis)
nuc = compute_nuclear_repulsion(basis)

# Compute overlap matrix of atom-centered basis set
# -------------------------------------------------
olp = compute_overlap(basis)

# Create orbitals that store the AO/MO coefficients
# -------------------------------------------------
orb = lf.create_orbital()

# Get center of mass
# ------------------
x, y, z = get_com(basis)

# electric dipole moment integrals of the atomic basis set wrt COM
# ----------------------------------------------------------------
olp, mux, muy, muz, origin = compute_dipole(basis, x=x, y=y, z=z)

# electric quadrupole moment integrals of the atomic basis set wrt COM
# --------------------------------------------------------------------
olp, mux, muy, muz, muxx, muxy, muxz, muyy, muyz, muzz = compute_quadrupole(
    basis, x=x, y=y, z=z
)
