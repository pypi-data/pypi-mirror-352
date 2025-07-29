#!/usr/bin/env python3

from pybest import context
from pybest.gbasis import (
    compute_eri,
    compute_kinetic,
    compute_nuclear,
    get_gobasis,
)
from pybest.geminals import ROOpCCD
from pybest.iodata import IOData
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel

#
# Note for user:
# Please run water-oopccd_cc-pvdz.py before running this script, to obtain the
# required checkpoint file.
#

#
# Set up molecule, define basis set
#
fn_xyz = context.get_fn("test/water.xyz")
basis = get_gobasis("cc-pvdz", fn_xyz)
#
# Define Occupation model, orbitals, and overlap
#
lf = DenseLinalgFactory(basis.nbasis)
# If we do not specify the number of frozen core orbitals (ncore),
# then ncore will be calculated automatically
occ_model = AufbauOccModel(basis, ncore=0)
orb_a = lf.create_orbital(basis.nbasis)
#
# Construct Hamiltonian
#
kin = compute_kinetic(basis)
ne = compute_nuclear(basis)
eri = compute_eri(basis)

#
# Restart an OO-pCCD calculation from file
#
# Step 1: Read in restart file
restart = IOData.from_file("pybest-results/checkpoint_pccd.h5")
# Step 2: Pass restart IOData container as input
oopccd = ROOpCCD(lf, occ_model)
oopccd_output = oopccd(kin, ne, eri, restart)
