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

"""Initial guesses for wavefunctions"""

from pybest.exceptions import ArgumentError
from pybest.linalg.base import Orbital, TwoIndex
from pybest.log import log, timer

__all__ = ["guess_core_hamiltonian"]


@timer.with_section("SCF: Initial Guess")
def guess_core_hamiltonian(overlap, *args, **kwargs):
    """Guess the orbitals by diagonalizing a core Hamiltonian

    **Arguments:**

    overlap
         The overlap operator.

    core1, core2, ...
         A number of operators that add up to the core Hamiltonian. Any set
         of operators whose sum resembles a Fock operator is fine. Usually,
         one passes the kinetic energy and nuclear attraction integrals.

    orb1, orb2, ...
         A list of orbital objects (output arguments)

    This method only modifies the AO/MO coefficients and the orbital energies.
    """
    if len(kwargs) != 0:
        raise ArgumentError(f"Unknown keyword arguments: {kwargs.keys()}")

    if log.do_medium:
        log("Performing a core Hamiltonian guess.")
        log.blank()

    core = []
    orbs = []
    for arg in args:
        if isinstance(arg, TwoIndex):
            core.append(arg)
        elif isinstance(arg, Orbital):
            orbs.append(arg)
        else:
            raise ArgumentError(f"Argument of unsupported type: {arg}")

    if len(core) == 0:
        raise ArgumentError(
            "At least one term is needed for the core Hamiltonian."
        )
    if len(orbs) == 0:
        raise ArgumentError("At least one set of orbitals is needed.")

    # Take sum of operators for core hamiltonian
    hamcore = core[0].copy()
    for term in core[1:]:
        hamcore.iadd(term)

    # Compute orbitals.
    orbs[0].from_fock(hamcore, overlap)
    # Copy to other orbitals.
    for i in range(1, len(orbs)):
        orbs[i].coeffs[:] = orbs[0].coeffs
        orbs[i].energies[:] = orbs[0].energies
