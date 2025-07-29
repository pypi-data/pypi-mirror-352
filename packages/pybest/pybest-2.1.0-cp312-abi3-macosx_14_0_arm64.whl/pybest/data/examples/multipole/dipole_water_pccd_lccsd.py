#!/usr/bin/env python3

from pybest import context
from pybest.cc import RpCCDLCCSD
from pybest.gbasis import (
    compute_dipole,
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
from pybest.utility import get_com
from pybest.wrappers import RHF, compute_dipole_moment

# Define coordinate file
# ----------------------
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
orb_a = lf.create_orbital()

# Decide how to occupy the orbitals (default Aufbau occupation)
# -------------------------------------------------------------
occ_model = AufbauOccModel(basis)

# Get center of mass
# ------------------
x, y, z = get_com(basis)

# electric dipole moment integrals of the atomic basis set wrt COM
# ----------------------------------------------------------------
dipole = compute_dipole(basis, x=x, y=y, z=z)

# Converge RHF
# ------------
hf = RHF(lf, occ_model)
hf_output = hf(kin, ne, eri, nuc, olp, orb_a)

# Converge pCCD
# -------------
oopccd = ROOpCCD(lf, occ_model)
oopccd_output = oopccd(kin, ne, eri, hf_output)

# LCCSD on top of pCCD
# --------------------
lccsd = RpCCDLCCSD(lf, occ_model)
lccsd_output = lccsd(kin, ne, eri, oopccd_output, lambda_equations=True)

# Compute dipole moment from pCCD-LCCSD, activate keyword for MOs
# ---------------------------------------------------------------
dipole_lccsd = compute_dipole_moment(
    dipole, lccsd_output, molecular_orbitals=True
)
