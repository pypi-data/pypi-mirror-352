#!/usr/bin/env python3

from pybest import context
from pybest.cc import RfpCCSD
from pybest.gbasis import (
    compute_eri,
    compute_kinetic,
    compute_nuclear,
    compute_nuclear_repulsion,
    compute_overlap,
    get_gobasis,
)
from pybest.geminals import ROOpCCD
from pybest.ip_eom import RDIPfpCCSD
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel
from pybest.wrappers import RHF

#
# Set up molecule, define basis set
#
# get the XYZ file from PyBEST's test data directory
fn_xyz = context.get_fn("test/o2_ccdz.xyz")
basis = get_gobasis("cc-pvdz", fn_xyz)

#
# Define Occupation model, orbitals, and overlap
#
lf = DenseLinalgFactory(basis.nbasis)
orb_a = lf.create_orbital(basis.nbasis)
olp = compute_overlap(basis)
# we need to add 2 additional electrons
# If we do not specify the number of frozen core orbitals (ncore),
# then ncore will be calculated automatically
occ_model = AufbauOccModel(basis, charge=-2, ncore=0)

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
# Do OO-pCCD optimization
#
oopccd = ROOpCCD(lf, occ_model)
oopccd_output = oopccd(kin, ne, eri, hf_output)

#
# Do fpCCSD optimization
#
fpccsd = RfpCCSD(lf, occ_model)
fpccsd_output = fpccsd(kin, ne, eri, oopccd_output)

#
# Do RDIP-fpCCSD calculation for 0 unpaired electron
#
ip = RDIPfpCCSD(lf, occ_model, alpha=0)
ip_output = ip(kin, ne, eri, fpccsd_output, nroot=4)
