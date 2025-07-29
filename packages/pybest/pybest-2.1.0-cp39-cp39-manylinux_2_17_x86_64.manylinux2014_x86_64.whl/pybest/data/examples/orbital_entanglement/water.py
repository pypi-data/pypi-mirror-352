#!/usr/bin/env python3

from pybest import context
from pybest.cc import RpCCDLCCD, RpCCDLCCSD
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
from pybest.orbital_entanglement import (
    OrbitalEntanglementRpCCD,
    OrbitalEntanglementRpCCDLCC,
)
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
# If we do not specify the number of frozen core orbitals (ncore),
# then ncore will be calculated automatically
occ_model = AufbauOccModel(basis, ncore=0)
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
pccd = ROOpCCD(lf, occ_model)
pccd_output = pccd(kin, ne, eri, hf_output)

#
# pCCD-LCCD calculation
#
lccd = RpCCDLCCD(lf, occ_model)
lccd_output = lccd(kin, ne, eri, pccd_output, lambda_equations=True)

#
# pCCD-LCCSD calculation
#
lccsd = RpCCDLCCSD(lf, occ_model)
lccsd_output = lccsd(kin, ne, eri, pccd_output, lambda_equations=True)

#
# Do orbital entanglement analysis for pCCD
#
entanglement = OrbitalEntanglementRpCCD(lf, pccd_output)
entanglement()

#
# Do orbital entanglement analysis for pCCD-LCCD
#
entanglement = OrbitalEntanglementRpCCDLCC(lf, lccd_output)
entanglement()

#
# Do orbital entanglement analysis for pCCD-LCCSD
#
entanglement = OrbitalEntanglementRpCCDLCC(lf, lccsd_output)
entanglement()
