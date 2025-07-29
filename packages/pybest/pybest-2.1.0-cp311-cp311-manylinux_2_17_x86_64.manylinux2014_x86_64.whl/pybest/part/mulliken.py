# PyBEST: Pythonic Black-box Electronic Structure Tool
# Copyright (C) 2016-- The PyBEST Development Team
#
# This file is part of PyBEST.
#
# PyBEST is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# PyBEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
# --

# Detailed changelog:
#
# This implementation has been taken from `Horton 2.0.0`.
# However, this file has been updated and debugged. Compatibility with Horton is NOT
# guaranteed.
# Its current version contains updates from the PyBEST developer team.
#
# Detailed changes (see also CHANGELOG):
# 2020-07-01: Update to PyBEST standard, including naming convention and Basis class

"""Mulliken partitioning"""

import numpy as np

from pybest.gbasis import compute_overlap

__all__ = ["get_mulliken_operators", "partition_mulliken"]


def partition_mulliken(operator, basis, index):
    """Fill in the mulliken operator in the first argument

    **Arguments:**

    operator
         A Two index operator to which the Mulliken mask is applied

    basis
         The localized orbital basis for which the Mulliken operator is to be
         constructed

    index
         The index of the atom (center) for which the Mulliken operator
         needs to be constructed

    This routine implies that the first ``natom`` centers in the basis
    corresponds to the atoms in the system.
    """
    mask = np.zeros(basis.nbasis, dtype=bool)
    begin = 0
    for ishell in range(basis.nshell):
        end = begin + basis.get_nbasis_in_shell(ishell)
        if basis.shell2atom[ishell] != index:
            mask[begin:end] = True
        begin = end
    operator._array[mask] = 0.0
    operator._array[:] = 0.5 * (operator._array + operator._array.T)


def get_mulliken_operators(basis):
    """Return a list of Mulliken operators for the given basis."""
    operators = []
    olp = compute_overlap(basis)
    for icenter in range(basis.ncenter):
        operator = olp.copy()
        partition_mulliken(operator, basis, icenter)
        operators.append(operator)
    return operators
