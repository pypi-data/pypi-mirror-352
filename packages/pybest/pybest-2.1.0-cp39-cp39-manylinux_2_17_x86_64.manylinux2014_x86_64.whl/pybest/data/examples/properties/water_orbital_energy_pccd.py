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
from pybest.geminals import RpCCD
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel
from pybest.properties.koopmans import Koopmans
from pybest.properties.modified_koopmans import ModifiedKoopmans
from pybest.wrappers import RHF

#
# Set up molecule, define basis set
#
fn_xyz = context.get_fn("test/water.xyz")
basis = get_gobasis("cc-pvdz", fn_xyz)
#
# Define the Occupation model, orbitals, and overlap
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
# Do pCCD calculation for the water molecule with a frozen 1s orbital
#
pccd = RpCCD(lf, occ_model)
pccd_output = pccd(kin, ne, eri, hf_output)

# Do orbital enrgy from Koopmans' theorem
# orb_range_o: (int) range of occupied orbitals
# orb_range_v: (int) range of virtual orbitals
# all : (str) all orbiatl energies are printed.
#
orbital_energyk = Koopmans(lf, occ_model)
orben_outputk = orbital_energyk(
    kin,
    ne,
    eri,
    pccd_output,
    printoptions={"orb_range_o": 3, "orb_range_v": 15},
)

# Do orbital enrgy from Modified Koopmans' theorem
# orb_range_o: (int) range of occupied orbitals
# orb_range_v: (int) range of virtual orbitals
# all : (str) all orbiatl energies are printed.
#
orbital_energymk = ModifiedKoopmans(lf, occ_model)
orben_outputmk = orbital_energymk(
    kin,
    ne,
    eri,
    pccd_output,
    printoptions={"orb_range_o": "all", "orb_range_v": "all"},
)
