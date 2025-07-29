#!/usr/bin/env python3

import numpy as np

from pybest.gbasis import (
    compute_eri,
    compute_kinetic,
    compute_nuclear,
    compute_nuclear_repulsion,
    compute_overlap,
    get_gobasis,
)
from pybest.iodata import IOData
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel
from pybest.utility import transform_integrals
from pybest.wrappers import RHF

# Set up Neon dimer, define basis set
# -----------------------------------
coordinates = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 5.0]])
atom = np.array(["Ne", "Ne"])
mol = IOData(coordinates=coordinates, atom=atom)
basis = get_gobasis("cc-pvdz", mol)
lf = DenseLinalgFactory(basis.nbasis)
occ_model = AufbauOccModel(basis)
orb = lf.create_orbital()

# Construct Hamiltonian
# ---------------------
kin_ao = compute_kinetic(basis)
ne_ao = compute_nuclear(basis)
eri_ao = compute_eri(basis)
e_core = compute_nuclear_repulsion(basis)
olp = compute_overlap(basis)

# Get Hartree-Fock MOs
# --------------------
hf = RHF(lf, occ_model)
hf_output = hf(kin_ao, ne_ao, eri_ao, e_core, orb, olp)

# Transform Hamiltonian to MO basis
# ---------------------------------
# transform integrals for restricted orbitals orb
t_ints = transform_integrals(kin_ao, ne_ao, eri_ao, orb)

# transformed one-electron integrals: attribute 'one' (list)
(one,) = t_ints.one  # or: one = ti_.one[0]
# transformed two-electron integrals: attribute 'two' (list)
(two,) = t_ints.two  # or: two = ti_.two[0]

# Write to an FCIDUMP file
# ------------------------
data = IOData(one=one, two=two, e_core=e_core, nelec=20, ms2=0)
data.to_file("hamiltonian_mo.FCIDUMP")
