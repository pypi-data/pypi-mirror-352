#!/usr/bin/env python3
#   This example is taken from the paper:
#   Many interacting fermions in a one-dimensional harmonic trap: a quantum-chemical treatment
#   Grining et. al
#   New J. Phys. 17, 115001 (2015)

from pybest.geminals import ROOpCCD
from pybest.linalg import DenseLinalgFactory
from pybest.modelhamiltonians import ContactInteraction1D
from pybest.occ_model import AufbauOccModel
from pybest.wrappers import RHF

# Define LinalgFactory for no_orbs = 30
# The maximal number of orbitals is determined by the grid size
no_orbs = 30

# numer of fermions  = 2
no_fermions = 2

# Define grid, mass and coupling strength as in
# paper of Grining, 2015,  Eq (1).
# several literature values for 2 paired (up and down) electrons:
# g /   total energy (Eh)
# 2     1.536605
# 0     0.999991
# -4   -1.816517
# note that for g=0 system corresponds to non-interacting oscillators
grid = (-10.0, 10.0, 0.05)
mass = 1.0
g_coupling = 2.0

# Define linear algebra and occupation model
lf = DenseLinalgFactory(no_orbs)
occ_model = AufbauOccModel(lf, nel=no_fermions)

# Calculate a set of 2-body integrals (no_orbs^4)
# by numerical integration, make 1-body integrals
modelham = ContactInteraction1D(lf, occ_model, domain=grid)
olp = modelham.compute_overlap()
one = modelham.compute_one_body()
two = modelham.compute_two_body()
orbs = lf.create_orbital()

# Scale 2-body integrals by the coupling strength
two.iscale(g_coupling)

# Calculate HF equations for 2 paired electrons
rhf = RHF(lf, occ_model)
rhf_output = rhf(one, two, orbs, olp, 0.0)

# Calculate oo-pCCD equations for 2 paired electrons
oopccd = ROOpCCD(lf, occ_model)
oopccd_output = oopccd(one, two, rhf_output)
