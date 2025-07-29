#!/usr/bin/env python3

from pybest import context
from pybest.cc import RpCCDLCCSD
from pybest.ea_eom import REAfpLCCSD
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
lf = CholeskyLinalgFactory(basis.nbasis)
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
eri = compute_cholesky_eri(basis)
external = compute_nuclear_repulsion(basis)
#
# Do a Hartree-Fock calculation
#
hf = RHF(lf, occ_model)
hf_output = hf(kin, ne, eri, external, olp, orb_a)
#
# Do OOpCCD calculation
#
OOpCCD = ROOpCCD(lf, occ_model)
OOpCCD_output = OOpCCD(kin, ne, eri, hf_output)
#
# Do fpLCCSD calculation
#
fplccsd = RpCCDLCCSD(lf, occ_model)
fplccsd_output = fplccsd(kin, ne, eri, OOpCCD_output)

#
# Do REAfpLCCSD calculation for 1 unpaired electron
#
ea = REAfpLCCSD(lf, occ_model, alpha=1)
ea_output = ea(kin, ne, eri, fplccsd_output, nroot=8)
