#!/usr/bin/env python3

import numpy as np

from pybest import context
from pybest.ea_eom import RDEApCCD
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
fn_xyz = context.get_fn("test/o2_ccdz.xyz")
basis = get_gobasis("cc-pvdz", fn_xyz)

#
# Define Occupation model, orbitals, and overlap
#
lf = CholeskyLinalgFactory(basis.nbasis)
orb_a = lf.create_orbital(basis.nbasis)
olp = compute_overlap(basis)
# We need to start with 2 electron less
occ_model = AufbauOccModel(basis, charge=2)

#
# Construct Hamiltonian
#
kin = compute_kinetic(basis)
ne = compute_nuclear(basis)
eri = compute_cholesky_eri(basis, threshold=1e-7)
external = compute_nuclear_repulsion(basis)

#
# Do a Hartree-Fock calculation
#
hf = RHF(lf, occ_model)
hf_output = hf(kin, ne, eri, external, olp, orb_a)
# swap sigma* and pi* orbitals as HF solution has wrong occupation
hf_output.orb_a.swap_orbitals(np.array([[6, 7]]))

#
# Do OO-pCCD optimization
#
oopccd = ROOpCCD(lf, occ_model)
oopccd_output = oopccd(kin, ne, eri, hf_output)

#
# Do REA-pCCD calculation
#
# 0 unpaired electron; O_2
ea_1 = RDEApCCD(lf, occ_model, alpha=0)
ea_output_1 = ea_1(kin, ne, eri, oopccd_output, nroot=4)

# 2 unpaired electrons; O_2
ea_2 = RDEApCCD(lf, occ_model, alpha=2)
ea_output_2 = ea_2(kin, ne, eri, oopccd_output, nroot=3)

# 4 unpaired electrons; O_2
ea_3 = RDEApCCD(lf, occ_model, alpha=4)
ea_output_3 = ea_3(kin, ne, eri, oopccd_output, nroot=3)
