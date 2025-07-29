#!/usr/bin/env python3
from pybest.geminals import ROOpCCD
from pybest.linalg import DenseLinalgFactory
from pybest.modelhamiltonians import Hubbard
from pybest.occ_model import AufbauOccModel
from pybest.wrappers import RHF

#
# Define Occupation model, orbitals, and overlap
#
lf = DenseLinalgFactory(6)
occ_model = AufbauOccModel(lf, nel=6)

orb_a = lf.create_orbital()

#
# Initialize an instance of the Hubbard class
#
#
# t-param, t = -1
# U-param, U = 2
#
modelham = Hubbard(lf, occ_model=occ_model, pbc=True)
modelham.parameters = {"on_site": 0.0, "hopping": -1.0, "u": 2.0}

kin = modelham.compute_one_body()
two = modelham.compute_two_body()
olp = modelham.compute_overlap()

#
# Do a Hartree-Fock calculation
#
hf = RHF(lf, occ_model)
hf_output = hf(kin, two, 0.0, orb_a, olp)

#
# Do OO-pCCD optimization
#
oopccd = ROOpCCD(lf, occ_model)
oopccd_output = oopccd(kin, two, hf_output)
