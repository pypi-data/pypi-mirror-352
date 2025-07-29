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
from pybest.geminals import ROOpCCD
from pybest.iodata import IOData
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel
from pybest.units import deg
from pybest.wrappers import RHF

#
# Set up molecule, define basis set
#
fn_xyz = context.get_fn("test/water_2.xyz")
basis = get_gobasis("cc-pvdz", fn_xyz)
#
# Define Occupation model, orbitals, and overlap
#
lf = DenseLinalgFactory(basis.nbasis)
# If we do not specify the number of frozen core orbitals (ncore),
# then ncore will be calculated automatically
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
# Do OO-pCCD optimization
#
oopccd = ROOpCCD(lf, occ_model)
oopccd_output = oopccd(kin, ne, eri, hf_output)

#
# Restart an OO-pCCD calculation from default restart file
#
oopccd = ROOpCCD(lf, occ_model)
oopccd_output = oopccd(
    kin, ne, eri, restart="pybest-results/checkpoint_pccd.h5"
)

#
# Restart an OO-pCCD calculation from perturbed orbitals
#
# read in the orbitals
restart = IOData.from_file("pybest-results/checkpoint_pccd.h5")
# perturb them as you wish, eg, HOMO-LUMO 2x2 rotation (python indexing, starts
# with 0)
restart.orb_a.rotate_2orbitals(60 * deg, 4, 5)

# Now pass the restart container as argument
oopccd = ROOpCCD(lf, occ_model)
oopccd_output = oopccd(kin, ne, eri, restart)
