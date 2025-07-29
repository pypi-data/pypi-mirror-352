#!/usr/bin/env python3


from pybest.cc import RpCCDLCCSD
from pybest.geminals import ROOpCCD
from pybest.linalg import DenseLinalgFactory
from pybest.modelhamiltonians import ContactInteraction1D
from pybest.occ_model import AufbauOccModel
from pybest.wrappers import RHF


def potential(r):
    """Defines a function used for a potential inside Contact Interaction
    Hamiltonian
    """
    return 0.5 * r**2


#
# Define Occupation model, orbitals, and overlap
#
lf = DenseLinalgFactory(10)
occ_model = AufbauOccModel(lf, nel=4)
orb_a = lf.create_orbital()
#
# Initialize an instance of the ContactInteraction1D class
#
modelham = ContactInteraction1D(
    lf, domain=[-6.0, 6.0, 0.1e-1], mass=1, potential=potential
)

olp = modelham.compute_overlap()
one = modelham.compute_one_body()
two = modelham.compute_two_body()
# Contact parameter
g = 4
two.iscale(g)
#
# Do a Hartree-Fock calculation
#
hf = RHF(lf, occ_model)
hf_output = hf(one, two, 0.0, orb_a, olp)
#
# Do OO-pCCD optimization
#
oopccd = ROOpCCD(lf, occ_model)
oopccd_output = oopccd(one, two, hf_output)
#
# Do RpCCD-LCCSD calculation
# exact tot energy is 6.77904068746 a.u., pCCD-LCC gives 6.76215649 a.u.
#
lccsd = RpCCDLCCSD(lf, occ_model)
lccsd_output = lccsd(one, two, oopccd_output, solver="krylov")
