#!/usr/bin/env python3

from pybest.cc import RfpCCD, RfpCCSD
from pybest.context import context
from pybest.gbasis import (
    compute_cholesky_eri,
    compute_kinetic,
    compute_nuclear,
    compute_nuclear_repulsion,
    compute_overlap,
    get_gobasis,
)
from pybest.geminals import ROOpCCD
from pybest.linalg import CholeskyLinalgFactory
from pybest.localization import PipekMezey
from pybest.occ_model import AufbauOccModel
from pybest.part import get_mulliken_operators
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
lf = CholeskyLinalgFactory(basis.nbasis)
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
eri = compute_cholesky_eri(basis, threshold=1e-8)
nr = compute_nuclear_repulsion(basis)
#
# Do a Hartree-Fock calculation
#
hf = RHF(lf, occ_model)
hf_output = hf(kin, ne, eri, nr, olp, orb_a)
#
# Localize orbitals to improve pCCD convergence
#
mulliken = get_mulliken_operators(basis)
loc = PipekMezey(lf, occ_model, mulliken)
loc(orb_a, "occ")
loc(orb_a, "virt")
#
# Do pCCD
#
pccd = ROOpCCD(lf, occ_model)
pccd_output = pccd(hf_output, kin, ne, eri, e_core=nr)
#
# Do pCCD-fpCCD calculation
#
ccd = RfpCCD(lf, occ_model)
ccd_output = ccd(pccd_output, kin, ne, eri)
#
# Do pCCD-fpCCSD calculation
#
ccsd = RfpCCSD(lf, occ_model)
ccsd_output = ccsd(pccd_output, kin, ne, eri)
