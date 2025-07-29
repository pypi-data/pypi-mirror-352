#!/usr/bin/env python3

from pybest.iodata import IOData

# Load the integrals from the file
# Assuming you have run `dump_internal_ao.py` first.
data = IOData.from_file("hamiltonian_ao.h5")

# Print all attributes (stored as dictionary)
print(data.__dict__)
