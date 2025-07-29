#!/usr/bin/env python3

from pybest import context
from pybest.cc import RpCCDLCCD, RpCCDLCCSD
from pybest.ee_eom import REOMpCCDLCCD, REOMpCCDLCCSD
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
# Do pCCD optimization
#
oopccd = RpCCD(lf, occ_model)
oopccd_output = oopccd(kin, ne, eri, hf_output)

#
# Do pCCD-LCCD optimization
#
lccd = RpCCDLCCD(lf, occ_model)
lccd_output = lccd(kin, ne, eri, oopccd_output)

#
# Do REOM-pCCD-LCCD calculation
#
eom = REOMpCCDLCCD(lf, occ_model)
eom_output = eom(kin, ne, eri, lccd_output, nroot=3)

#
# Do pCCD-LCCSD optimization
#
lccsd = RpCCDLCCSD(lf, occ_model)
lccsd_output = lccsd(kin, ne, eri, oopccd_output)

#
# Do REOM-pCCD-LCCSD calculation
#
eom = REOMpCCDLCCSD(lf, occ_model)
eom_output = eom(kin, ne, eri, lccsd_output, nroot=3)
