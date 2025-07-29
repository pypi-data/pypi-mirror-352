#!/usr/bin/env python3
"""DMRG-tailored CCSD calculations performed in the pCCD orbital basis for the
CN+ molecule. DMRG amplitudes have been precomputed using the Budapest DMRG
program.
"""

from pybest.cc import RtCCSD
from pybest.gbasis import get_gobasis
from pybest.iodata import IOData
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel

#
# Set up molecule, define basis set
#
# get the XYZ file from PyBEST's test data directory
basis = get_gobasis("cc-pvdz", "data/cn+.xyz")
lf = DenseLinalgFactory(basis.nbasis)
# ncore set to 0 to avoid conflict due to autocore in the tcc module
occ_model = AufbauOccModel(basis, charge=1, ncore=0)
#
# Load all integrals to a FCIDUMP file
#
ints = IOData.from_file("all.FCIDUMP")
pccd = IOData.from_file("pybest-results/checkpoint_pccd.h5")
#
# Do DMRG-tailored CCSD calculation
#
tcc = RtCCSD(lf, occ_model)
tcc_output = tcc(
    ints.one,
    ints.two,
    ints.orb_a,
    e_ref=pccd.e_ref,
    external_file="data/T_DUMP",
)
