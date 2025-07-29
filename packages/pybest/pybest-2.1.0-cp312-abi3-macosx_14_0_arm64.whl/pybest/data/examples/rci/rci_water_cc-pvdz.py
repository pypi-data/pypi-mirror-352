#!/usr/bin/env python3

from pybest.ci import RCID, RCIS, RCISD
from pybest.context import context
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
# Do RHF-CIS calculation using Davidson diagonalization
#
rcis = RCIS(lf, occ_model)
rcis_output = rcis(kin, ne, eri, hf_output)
#
# Do RHF-CID calculation using Davidson diagonalization
#
rcid = RCID(lf, occ_model)
rcid_output = rcid(kin, ne, eri, hf_output)
#
# Do RHF-CISD calculation using Davidson diagonalization
#
rcisd = RCISD(lf, occ_model)
rcisd_output = rcisd(kin, ne, eri, hf_output)
#
# Do RHF-CISD calculation for the ground state and 4 excited states
#
rcisd = RCISD(lf, occ_model)
rcisd_output = rcisd(kin, ne, eri, hf_output, nroot=5)
#
# Do RHF-CIS calculation using SD representation
#
rcis = RCIS(lf, occ_model, csf=False)
rcis_output = rcis(kin, ne, eri, hf_output)
#
# Do RHF-CID calculation using SD representation
#
rcid = RCID(lf, occ_model, csf=False)
rcid_output = rcid(kin, ne, eri, hf_output)
#
# Do RHF-CISD calculation using SD representation
#
rcisd = RCISD(lf, occ_model, csf=False)
rcisd_output = rcisd(kin, ne, eri, hf_output)
