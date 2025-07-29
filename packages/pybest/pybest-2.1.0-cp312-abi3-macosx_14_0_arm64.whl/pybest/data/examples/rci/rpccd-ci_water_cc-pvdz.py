#!/usr/bin/env python3

from pybest.ci import RpCCDCID, RpCCDCISD
from pybest.context import context
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
# Set up molecule, define basis set
#
# get the XYZ file from PyBEST's test data directory
fn_xyz = context.get_fn("test/water.xyz")
basis = get_gobasis("cc-pvdz", fn_xyz)
#
# Define the occupation model, orbitals, and overlap
#
lf = DenseLinalgFactory(basis.nbasis)
# If we do not specify the number of frozen core orbitals (ncore),
# then ncore will be calculated automatically
occ_model = AufbauOccModel(basis, ncore=0)
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
# Do an OO-pCCD calculation
#
pccd = ROOpCCD(lf, occ_model)
pccd_output = pccd(kin, ne, eri, hf_output)

#
# Do RpCCD-CID calculation using Davidson diagonalization
#
rcid = RpCCDCID(lf, occ_model)
rcid_output = rcid(kin, ne, eri, pccd_output)

#
# Do RpCCD-CISD calculation using Davidson diagonalization
#
rcisd = RpCCDCISD(lf, occ_model)
rcisd_output = rcisd(kin, ne, eri, pccd_output)
