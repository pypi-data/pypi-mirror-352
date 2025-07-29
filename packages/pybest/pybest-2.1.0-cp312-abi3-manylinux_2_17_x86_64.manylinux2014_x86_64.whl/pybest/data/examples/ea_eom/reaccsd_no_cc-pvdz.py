#!/usr/bin/env python3

from pybest import context
from pybest.cc import RCCSD
from pybest.ea_eom import REACCSD
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
fn_xyz = context.get_fn("test/no.xyz")
basis = get_gobasis("cc-pvdz", fn_xyz)
#
# Define Occupation model, orbitals, and overlap
#
lf = DenseLinalgFactory(basis.nbasis)
orb_a = lf.create_orbital(basis.nbasis)
olp = compute_overlap(basis)
# we need to remove 1 electron
# If we do not specify the number of frozen core orbitals (ncore),
# then ncore will be calculated automatically
occ_model = AufbauOccModel(basis, charge=1, ncore=0)
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
# Do CCSD calculation
#
ccsd = RCCSD(lf, occ_model)
ccsd_output = ccsd(kin, ne, eri, hf_output)
#
# Do SEACCSD calculation for 1 unpaired electron
#
ea = REACCSD(lf, occ_model, alpha=1)
ea_output = ea(kin, ne, eri, ccsd_output, nroot=8)
