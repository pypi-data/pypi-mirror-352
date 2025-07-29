#!/usr/bin/env python3

from pybest import context
from pybest.cc import RCCS, RpCCDCCS
from pybest.ee_eom import REOMCCS, REOMpCCDCCS
from pybest.gbasis import (
    compute_eri,
    compute_kinetic,
    compute_nuclear,
    compute_nuclear_repulsion,
    compute_overlap,
    get_gobasis,
)
from pybest.geminals import RpCCD
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
# Do CCS optimization
#
ccs = RCCS(lf, occ_model)
ccs_output = ccs(kin, ne, eri, hf_output)

#
# Do REOM-CCS calculation
#
eom = REOMCCS(lf, occ_model)
eom_output = eom(kin, ne, eri, ccs_output, nroot=3)

#
# Do pCCD optimization
#
oopccd = RpCCD(lf, occ_model)
oopccd_output = oopccd(kin, ne, eri, hf_output)

#
# Do pCCD-CCS optimization
#
pccdccs = RpCCDCCS(lf, occ_model)
pccdccs_output = pccdccs(kin, ne, eri, oopccd_output)

#
# Do REOM-pCCD-CCS calculation
#
eom = REOMpCCDCCS(lf, occ_model)
eom_output = eom(kin, ne, eri, pccdccs_output, nroot=3)
