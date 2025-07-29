#!/usr/bin/env python3

from pybest import context
from pybest.cc import RLCCSD
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
from pybest.rsf_eom import RSFLCCD
from pybest.wrappers import RHF

#
# Set up molecule, define basis set
#
# get the XYZ file from PyBEST's test data directory
c_xyz = context.get_fn("test/c.xyz")
basis = get_gobasis("cc-pvdz", c_xyz)

#
# Define Occupation model, orbitals and overlap
#
lf = DenseLinalgFactory(basis.nbasis)
orb_a = lf.create_orbital(basis.nbasis)
olp = compute_overlap(basis)

occ_model = AufbauOccModel(basis)

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
# Do LCCSD optimization
#
lccd = RLCCSD(lf, occ_model)
lccd_output = lccd(kin, ne, eri, hf_output)

#
# Do RSF-LCCSD calculation with 4 unpaired electrons
#
rsf_L = RSFLCCD(lf, occ_model, alpha=4)
rsf_L_output = rsf_L(kin, ne, eri, lccd_output, nroot=8)
