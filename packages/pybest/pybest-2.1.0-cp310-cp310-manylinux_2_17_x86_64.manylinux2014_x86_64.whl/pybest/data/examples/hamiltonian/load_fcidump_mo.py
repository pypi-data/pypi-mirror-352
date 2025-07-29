#!/usr/bin/env python3

from pybest.iodata import IOData

# Load the integrals from the file
# Assuming you have run `dump_fcidump_mo.py` first.
data = IOData.from_file("hamiltonian_mo.FCIDUMP")

# Access some attributes. In more realistic cases, some code follows that does
# a useful calculation.
print("Core energy: ", data.e_core)
print("Element [0, 0] of one-body integrals: ", data.one.get_element(0, 0))
print("Available attributes: ", data.__dict__)
