#!/usr/bin/env python3

from pybest import context
from pybest.gbasis import (
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
from pybest.wrappers import RHF

#
# Note for user:
# Please run water-oopccd_cc-pvdz.py before running this script, to obtain the
# required checkpoint file.
#

#
# Set up molecule, define basis set
#
fn_xyz = context.get_fn("test/water_2.xyz")
basis = get_gobasis("cc-pvdz", fn_xyz)
#
# Define Occupation model, orbitals, and overlap
#
lf = DenseLinalgFactory(basis.nbasis)
# If we do not specify the number of frozen core orbitals (ncore),
# then ncore will be calculated automatically
occ_model = AufbauOccModel(basis)
orb_a = lf.create_orbital(basis.nbasis)
olp = compute_overlap(basis)
#
# Construct the Hamiltonian
#
kin = compute_kinetic(basis)
ne = compute_nuclear(basis)
eri = compute_eri(basis)
external = compute_nuclear_repulsion(basis)
#
# If we want to restart from a different geometry, we need the RHF
# orbitals from the current geometry, otherwise the code will fail
#
# Do a Hartree-Fock calculation
#
hf = RHF(lf, occ_model)
hf_output = hf(kin, ne, eri, external, olp, orb_a)
#
# Restart an OO-pCCD calculation from default restart file (which contains orbitals
# from a different geometry)
#
# We can pass the hf_output or each argument separately (olp, orb_a, e_core=external)
oopccd = ROOpCCD(lf, occ_model)
oopccd_output = oopccd(
    kin,
    ne,
    eri,
    olp,
    orb_a,
    e_core=external,
    restart="pybest-results/checkpoint_pccd.h5",
)
