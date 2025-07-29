#!/usr/bin/env python3

from pybest import context
from pybest.gbasis import (
    compute_cholesky_eri,
    compute_kinetic,
    compute_nuclear,
    compute_nuclear_repulsion,
    get_gobasis,
)
from pybest.iodata import IOData
from pybest.linalg import CholeskyLinalgFactory

# Set up molecule, define basis set
# ---------------------------------
# get the XYZ file from PyBEST's test data directory
fn_xyz = context.get_fn("test/water.xyz")
basis = get_gobasis("cc-pvdz", fn_xyz)
lf = CholeskyLinalgFactory(basis.nbasis)

# Construct Hamiltonian
# ---------------------
mol = IOData()
mol.lf = lf
mol.kin = compute_kinetic(basis)
mol.ne = compute_nuclear(basis)
mol.eri = compute_cholesky_eri(basis)
mol.e_core = compute_nuclear_repulsion(basis)

# Write to a HDF5 file
# --------------------
mol.to_file("hamiltonian_ao.h5")
