#!/usr/bin/env python3

import numpy as np

from pybest.gbasis import (
    compute_eri,
    compute_kinetic,
    compute_nuclear,
    compute_nuclear_repulsion,
    get_gobasis,
)
from pybest.iodata import IOData
from pybest.linalg import DenseLinalgFactory

# Set up Neon atom, define basis set
# ----------------------------------
coordinates = np.array([[0.0, 0.0, 0.0]])
atom = np.array(["Ne"])
mol = IOData(atom=atom, coordinates=coordinates)
basis = get_gobasis("cc-pvdz", mol)
lf = DenseLinalgFactory(basis.nbasis)

# Construct Hamiltonian
# ---------------------
one_mo = lf.create_two_index()
one_mo = compute_kinetic(basis)
one_mo.iadd(compute_nuclear(basis))
two_mo = compute_eri(basis)
core_energy = compute_nuclear_repulsion(basis)

# Write to a HDF5 file
# --------------------
data = IOData()
data.lf = lf
data.one_mo = one_mo
data.two_mo = two_mo
data.core_energy = core_energy
data.nelec = 10
data.ms2 = 0
data.to_file("hamiltonian_ao_fcidump.h5")
