#!/usr/bin/env python3

import numpy as np

from pybest import context
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
from pybest.utility import split_core_active
from pybest.wrappers import RHF

#
# Set up molecule, define basis set
#
fn_xyz = context.get_fn("test/water.xyz")
basis = get_gobasis("cc-pvdz", fn_xyz)
#
# Define Occupation model, orbitals, and overlap
#
lf = DenseLinalgFactory(basis.nbasis)
occ_model = AufbauOccModel(basis, ncore=1)
orb_a = lf.create_orbital(basis.nbasis)
olp = compute_overlap(basis)
#
# Construct the Hamiltonian
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
# Calculate the exact orbital Hessian of pCCD
#
# transform integrals for restricted orbitals oopccd_.orb_a
t_ints = split_core_active(kin, ne, eri, oopccd_output, ncore=1)

# transformed one-electron integrals: attribute 'one'
one = t_ints.one
# transformed two-electron integrals: attribute 'two'
two = t_ints.two

# calculate the exact orbital hessian of OOpCCD
hessian = oopccd.get_exact_hessian(one, two)

# diagonalize the exact orbital Hessian
eigv = np.linalg.eigvalsh(hessian)

print(eigv)
