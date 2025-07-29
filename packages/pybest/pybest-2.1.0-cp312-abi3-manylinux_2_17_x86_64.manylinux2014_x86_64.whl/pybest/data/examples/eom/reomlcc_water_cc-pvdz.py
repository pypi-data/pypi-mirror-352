#!/usr/bin/env python3

from pybest import context
from pybest.cc import RLCCD, RLCCSD
from pybest.ee_eom import REOMLCCD, REOMLCCSD
from pybest.gbasis import (
    compute_eri,
    compute_kinetic,
    compute_nuclear,
    compute_nuclear_repulsion,
    compute_overlap,
    get_gobasis,
)
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel
from pybest.wrappers import RHF

#
# Set up molecule, define basis set
#
# get the XYZ file from PyBEST's test data directory
fn_xyz = context.get_fn("test/water.xyz")
basis = get_gobasis("cc-pvdz", fn_xyz)
#
# Define Occupation model, orbitals, and overlap
#
lf = DenseLinalgFactory(basis.nbasis)
occ_model = AufbauOccModel(basis)
orb_a = lf.create_orbital(basis.nbasis)
olp = compute_overlap(basis)
#
# Construct Hamiltonian
#
kin = compute_kinetic(basis)
ne = compute_nuclear(basis)
eri = compute_eri(basis)
external = compute_nuclear_repulsion(basis)

#
# Do a Hartree-Fock calculation
#
hf = RHF(lf, occ_model)
hf_output = hf(kin, ne, eri, external, olp, orb_a)

#
# Do LCCD optimization
#
lccd = RLCCD(lf, occ_model)
lccd_output = lccd(kin, ne, eri, hf_output)

#
# Do REOM-LCCD calculation
#
eom = REOMLCCD(lf, occ_model)
eom_output = eom(kin, ne, eri, lccd_output, nroot=3)

#
# Do LCCSD optimization
#
lccsd = RLCCSD(lf, occ_model)
lccsd_output = lccsd(kin, ne, eri, hf_output)

#
# Do REOM-LCCSD calculation
#
eom = REOMLCCSD(lf, occ_model)
eom_output = eom(kin, ne, eri, lccsd_output, nroot=3)
