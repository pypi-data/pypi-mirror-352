#!/usr/bin/env python3
"""Calculates a dipole moment in the presence of point charges and the X2C Hamiltonian."""

from pybest import context
from pybest.gbasis import (
    compute_dipole,
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
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel
from pybest.scalar_relativistic_hamiltonians import X2C
from pybest.utility import get_com
from pybest.wrappers import RHF, compute_dipole_moment

# Load the coordinates and charges from PyBEST's test data directory
# ------------------------------------------------------------------
fn_xyz = context.get_fn("test/water_pc.xyz")
pc_xyz = context.get_fn("test/water_pc.pc")

# Get basis set and external charges
# ----------------------------------
basis = get_gobasis("cc-pvdz", fn_xyz)
charges = get_charges(pc_xyz)

# Create a linalg factory instance
# --------------------------------
lf = DenseLinalgFactory(basis.nbasis)

# Compute standard QC integrals
# -----------------------------
olp = compute_overlap(basis)
kin = compute_kinetic(basis)
ne = compute_nuclear(basis)
eri = compute_eri(basis)
external = compute_nuclear_repulsion(basis)

# Calculate the interaction of point charges with electrons
# ---------------------------------------------------------
pc = compute_point_charges(basis, charges)

# Calculate the interaction of point charges with nuclei
# ------------------------------------------------------
external += compute_nuclear_pc(basis, charges)

# Create alpha orbitals
# ---------------------
orb_a = lf.create_orbital()

# Choose an occupation model
# --------------------------
occ_model = AufbauOccModel(basis)

# Create an X2C instance
# ----------------------
x2c_hamiltonian = X2C(basis, charges)

# Get the center of mass
# ----------------------
x, y, z = get_com(basis)

# Electric dipole moment integrals of the atomic basis set wrt COM
# ----------------------------------------------------------------
dipole = compute_dipole(basis, x=x, y=y, z=z)

# HF with the point charges in the non-relativistic QC Hamiltonian
# ----------------------------------------------------------------
hf_pc = RHF(lf, occ_model)
hf_pc_output = hf_pc(eri, kin, ne, external, pc, olp, orb_a)

# Compute HF dipole moment using non-relativistic QC Hamiltonian
# --------------------------------------------------------------
dipole_moment = compute_dipole_moment(dipole, hf_pc_output)

# HF with the point charges in the X2C Hamiltonian
# ------------------------------------------------
x2c_pc = x2c_hamiltonian()
hf_x2c_pc = RHF(lf, occ_model)
hf_x2c_pc_output = hf_x2c_pc(x2c_pc, eri, pc, external, olp, orb_a)

# Compute HF dipole moment using the X2C Hamiltonian
# ---------------------------------------------------
dipole_moment = compute_dipole_moment(dipole, hf_x2c_pc_output)
