#!/usr/bin/env python3

from pybest import context
from pybest.gbasis import (
    compute_eri,
    compute_kinetic,
    compute_nuclear,
    compute_nuclear_repulsion,
    compute_overlap,
    get_gobasis,
)
from pybest.linalg import DenseLinalgFactory
from pybest.localization import PipekMezey
from pybest.occ_model import AufbauOccModel
from pybest.part import get_mulliken_operators
from pybest.wrappers import RHF

#
# Set up molecule, define basis set
#
# Use the XYZ file from PyBEST's test data directory.
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
# Define Mulliken projectors
#
mulliken = get_mulliken_operators(basis)
#
# Pipek-Mezey localizaton
#
loc = PipekMezey(lf, occ_model, mulliken)
#
# occupied block
#
loc(hf_output, "occ")
#
# virtual block
#
loc(hf_output, "virt")

#
# dump Molden file; hf_output already contains the orb_a attribute
#
hf_output.to_file("water.molden")
