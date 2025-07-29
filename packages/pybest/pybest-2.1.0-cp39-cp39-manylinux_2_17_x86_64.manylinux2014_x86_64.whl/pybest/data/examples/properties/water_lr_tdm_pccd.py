#!/usr/bin/env python3

from pybest import context
from pybest.ee_jacobian import JacobianpCCD
from pybest.gbasis import (
    compute_dipole,
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
from pybest.properties import LRpCCD
from pybest.utility import get_com
from pybest.wrappers import RHF
from pybest.wrappers.multipole import check_coord

# Set up molecule, define basis set
fn_xyz = context.get_fn("test/water.xyz")
basis = get_gobasis("cc-pvdz", fn_xyz)

# Define occupation model, orbitals, and overlap
lf = DenseLinalgFactory(basis.nbasis)
occ_model = AufbauOccModel(basis)
orb_a = lf.create_orbital(basis.nbasis)
olp = compute_overlap(basis)


# Construct Hamiltonian
kin = compute_kinetic(basis)
ne = compute_nuclear(basis)
eri = compute_eri(basis)
nuc = compute_nuclear_repulsion(basis)
nuc = compute_nuclear_repulsion(basis)
# dipole moment
x, y, z = get_com(basis)
dipole = compute_dipole(basis, x=x, y=y, z=z)

# Do a Hartree-Fock calculation
hf = RHF(lf, occ_model)
hf_output = hf(kin, ne, eri, nuc, olp, orb_a)

# Do pCCD calculations
pccd = RpCCD(lf, occ_model)
pccd_output = pccd(kin, ne, eri, hf_output)
# check coordinates
coord = check_coord(dipole, pccd_output)

# Compute excitation energies using Jacobian matrix.

jac = JacobianpCCD(lf, occ_model)
jac_output = jac(kin, ne, eri, pccd_output, davidson=True)

# Compute transition dipole moment
tm_dipole = LRpCCD(lf, occ_model)
dipole_output = tm_dipole(
    kin,
    ne,
    eri,
    jac_output,
    property_options={
        "operator_A": dipole,
        "operator_B": dipole,
        "coordinates": coord,
        "transition_dipole_moment": True,
    },
    printoptions={"nroot": 2},
)
