#!/usr/bin/env python3

from pybest import context
from pybest.gbasis import (
    compute_eri,
    compute_kinetic,
    compute_nuclear,
    compute_nuclear_repulsion,
    compute_overlap,
    compute_quadrupole,
    get_gobasis,
)
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel
from pybest.wrappers import RHF, compute_quadrupole_moment

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

# Quadrupole moment integrals of the atomic basis set wrt [0.0, 0.0, 0.0]
# -----------------------------------------------------------------------
quadrupole = compute_quadrupole(basis, x=0, y=0, z=0)

# Converge RHF
# ------------
hf = RHF(lf, occ_model)
hf_output = hf(kin, ne, eri, nuc, olp, orb_a)

# Compute quadrupole moment (nuclear and electronic parts)
# --------------------------------------------------------
quadrupole_moment = compute_quadrupole_moment(quadrupole, hf_output)
