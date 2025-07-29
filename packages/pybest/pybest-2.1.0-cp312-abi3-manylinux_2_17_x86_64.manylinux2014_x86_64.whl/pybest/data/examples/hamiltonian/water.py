#!/usr/bin/env python3

import numpy as np

from pybest.iodata import IOData
from pybest.utility import get_com

# define the molecule
natom = 3
alpha = 109.0 / 2.0 * np.pi / 180.0  # bond angle in radian
radius = 1.8  # distance between two neighboring atoms in bohr

# define the coordinates and elements
coordinates = np.zeros((natom, 3))
atom = np.array(["O", "H", "H"], dtype=object)  # must be strings

# update coordinates of the hydrogens (the oxygen atoms remains at the origin)
coordinates[1, 1] = -radius * np.sin(alpha)
coordinates[1, 2] = radius * np.cos(alpha)
coordinates[2, 1] = radius * np.sin(alpha)
coordinates[2, 2] = radius * np.cos(alpha)

# assign coordinates to container
mol = IOData(coordinates=coordinates, atom=atom, title="Water")

# move center of mass to the origin
com = get_com(mol)
mol.coordinates = mol.coordinates - com

# write the molecule to an XYZ file (optional)
mol.to_file("water.xyz")
