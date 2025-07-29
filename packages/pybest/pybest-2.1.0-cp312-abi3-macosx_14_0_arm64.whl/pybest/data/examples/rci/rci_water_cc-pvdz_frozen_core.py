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
# Do RHF-CIS calculation using Davidson diagonalization (frozen core)
#
rcis = RCIS(lf, occ_model)
rcis_output = rcis(kin, ne, eri, hf_output)
#
# Do RHF-CID calculation using Davidson diagonalization (frozen core)
#
rcid = RCID(lf, occ_model)
rcid_output = rcid(kin, ne, eri, hf_output)
#
# Do RHF-CISD calculation using Davidson diagonalization (frozen core)
#
rcisd = RCISD(lf, occ_model)
rcisd_output = rcisd(kin, ne, eri, hf_output)
