#!/usr/bin/env python3

from pybest.ci import RCIS
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
fn_xyz = context.get_fn("test/uracil.xyz")
basis = get_gobasis("cc-pvdz", fn_xyz)
#
# Define Occupation model, orbitals, and overlap
#
lf = DenseLinalgFactory(basis.nbasis)
# To calculate the C 1s XAS, we have to place the two N 1s and two O 1s
# in the frozen core orbitals space (ncore), and the four C 1s orbitals in the
# core active space (nactc).
occ_model = AufbauOccModel(basis, ncore=4, nactc=4)
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
# Do RHF-CIS calculation using Davidson diagonalization and CSF representation
#
rcis = RCIS(lf, occ_model, cvs=True)
rcis_output = rcis(kin, ne, eri, hf_output)
#
# Do RHF-CIS calculation using Davidson diagonalization and SD representation
#
rcis = RCIS(lf, occ_model, csf=False, cvs=True)
rcis_output = rcis(kin, ne, eri, hf_output)
