#!/usr/bin/env python3

from pybest import context
from pybest.sapt import SAPT0, sapt_utils

#
# Perform DCBS HF calculations
#
# get the XYZ file from PyBEST's test data directory
dimer_xyz = context.get_fn("test/water_dimer.xyz")
# monA is 'test/water_dimera.xyz'
# monB is 'test/water_dimerb.xyz'
basis_set = "cc-pvdz"
# occupation model specific kwargs (e.g., charge); not required here
occupation = ({}, {}, {})
# call wrapper routine that returns fragments IOData objects
dimer, monA, monB = sapt_utils.prepare_cp_hf(
    "cc-pvdz",
    dimer_xyz,
    occupation,
    fourindex_type="dense",
)
#
# Build SAPT0 solver and run computation
#
# construct solver
sapt0_solver = SAPT0(monA, monB)
# call solver routine
sapt0_solver(monA, monB, dimer)

# dictionary with corrections values
corrections = sapt0_solver.result

# access value of each correction
e10_elst = corrections["E^{(10)}_{elst}"]
e10_exch = corrections["E^{(10)}_{exch}(S^2)"]
e20_ind = corrections["E^{(20)}_{ind},unc"]
e20_exch_ind = corrections["E^{(20)}_{exch-ind}(S^2),unc"]
e20_disp = corrections["E^{(20)}_{disp},unc"]
e20_exch_disp = corrections["E^{(20)}_{exch-disp}(S^2),unc"]
