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
# 2020-07-01: Update to PyBEST standard, including naming convention and exception class

"""Evaluation of convergence criteria

These implementations are independent of the SCF algorithms and can be used
to double check convergence.
"""

from pybest.exceptions import ConsistencyError
from pybest.scf.utils import compute_1dm_hf, compute_commutator

__all__ = [
    "convergence_error_commutator",
    "convergence_error_eigen",
]


def convergence_error_eigen(ham, lf, overlap, *orbs):
    """Compute the self-consistency error

    **Arguments:**

    ham
         A Hamiltonian instance.

    lf
         The linalg factory to be used.

    overlap
         The overlap operator.

    orb1, orb2, ...
         A list of orbital objects. (The number must match ham.ndm.)

    **Returns:**
    The SCF error. This measure (not this function) is also used
    in some SCF algorithms to check for convergence.
    """
    if len(orbs) != ham.ndm:
        raise ConsistencyError(
            f"Expected {ham.ndm} orbitals, got {len(orbs)}."
        )
    dms = [compute_1dm_hf(orb) for orb in orbs]
    ham.reset(*dms)
    focks = [lf.create_two_index() for i in range(ham.ndm)]
    ham.compute_fock(*focks)
    error = 0.0
    for i in range(ham.ndm):
        error += orbs[i].error_eigen(focks[i], overlap)
    return error


def convergence_error_commutator(ham, lf, overlap, *dms):
    """Compute the commutator error

    **Arguments:**

    ham
         A Hamiltonian instance.

    lf
         The linalg factory to be used.

    overlap
         The overlap operator.

    dm1, dm2, ...
         A list of density matrices. The numbers of dms must match ham.ndm.

    **Returns:**
    The commutator error. This measure (not this function) is
    also used in some SCF algorithms to check for convergence.
    """
    if len(dms) != ham.ndm:
        raise ConsistencyError(
            f"Expected {ham.ndm} density matrices, got {len(dms)}."
        )
    ham.reset(*dms)
    focks = [lf.create_two_index() for i in range(ham.ndm)]
    ham.compute_fock(*focks)
    work = lf.create_two_index()
    commutator = lf.create_two_index()
    errorsq = 0.0
    for i in range(ham.ndm):
        compute_commutator(dms[i], focks[i], overlap, work, commutator)
        errorsq += commutator.contract("ab,ab", commutator)
    return errorsq**0.5
