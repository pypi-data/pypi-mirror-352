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
from pybest.iodata import IOData
from pybest.occ_model import AufbauOccModel
from pybest.wrappers import RHF

# Part I - computing energy operator integrals
# This part can be skipped if you generated overlap and FCIDUMP file beforehand

# Get geometry and basis functions
fn_xyz = context.get_fn("test/water.xyz")
basis = get_gobasis("cc-pvdz", fn_xyz)

# Compute integrals and write them to FCIDUMP-format file
kin = compute_kinetic(basis)
ne = compute_nuclear(basis)
eri = compute_eri(basis)
nucnuc_energy = compute_nuclear_repulsion(basis)
IOData(kin=kin, ne=ne, two=eri, e_core=nucnuc_energy).to_file("FCIDUMP")

# Write orbital overlap matrix to file
olp = compute_overlap(basis)
IOData(olp=olp).to_file("overlap.h5")

# Part II
# In this part, we read integrals and overlap from files
#
# Read data from FCIDUMP file
fcidump = IOData.from_file("FCIDUMP")
olp = IOData.from_file("overlap.h5").olp

# Part III
# Finally, RHF

# Define occupations
occ_model = AufbauOccModel(basis)

# Converge RHF
hf = RHF(fcidump.lf, occ_model)
hf_output = hf(fcidump.one, fcidump.two, fcidump.e_core, fcidump.orb_a, olp)
