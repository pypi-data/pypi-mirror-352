#!/usr/bin/env python3
"""Getting one- and two-body integrals in the ROOpCCD orbital basis for
the CN+ molecule.
"""

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
from pybest.utility import split_core_active, transform_integrals
from pybest.wrappers import RHF

#
# Set up molecule, define basis set
#
# get the XYZ file from PyBEST's test data directory
basis = get_gobasis("cc-pvdz", "data/cn+.xyz")
lf = DenseLinalgFactory(basis.nbasis)
# ncore set to 0 to avoid conflict due to autocore in the tcc module
occ_model = AufbauOccModel(basis, charge=1, ncore=0)
# Construct Hamiltonian
kin = compute_kinetic(basis)
ne = compute_nuclear(basis)
eri = compute_eri(basis)
e_core = compute_nuclear_repulsion(basis)
olp = compute_overlap(basis)
orb_a = lf.create_orbital()
#
# Do a Hartree-Fock calculation
#
hf = RHF(lf, occ_model)
hf_output = hf(kin, ne, eri, e_core, olp, orb_a)
#
# Do pCCD using RHF orbitals as an inital guess for solver
#
pccd = ROOpCCD(lf, occ_model)
pccd_output = pccd(kin, ne, eri, olp, hf_output)
#
# Transform Hamiltonian to MO basis
#
mo_ints = transform_integrals(kin, ne, eri, hf_output.orb_a)
one = mo_ints.one[0]
two = mo_ints.two[0]
#
# Write all integrals to a FCIDUMP file
#
data = IOData(one=one, two=two, e_core=e_core, ms2=0, nelec=12)
data.to_file("all.FCIDUMP")
#
# Get CAS Hamiltonian
#
mo_ints_cas = split_core_active(one, two, ncore=2, nactive=8, e_core=e_core)
one_cas = mo_ints_cas.one
two_cas = mo_ints_cas.two
#
# Write CAS integrals to a FCIDUMP file
#
data = IOData(one=one_cas, two=two_cas, e_core=e_core, ms2=0, nelec=8)
data.to_file("cas.FCIDUMP")
