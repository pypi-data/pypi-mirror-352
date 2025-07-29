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
# 2020-07-01: Update to PyBEST standard, including naming convention, exception class
# 2020-07-01: Update to new python features, including f-strings

"""Utility functions"""

from pybest.exceptions import ConsistencyError
from pybest.linalg import DenseOneIndex, DenseTwoIndex
from pybest.utility import check_type

__all__ = [
    "check_dm",
    "compute_1dm_hf",
    "compute_commutator",
    "get_homo_lumo",
    "get_level_shift",
    "get_spin",
]


def check_dm(dm, overlap, lf, eps=1e-4, occ_max=1.0):
    """Check if the density matrix has eigenvalues in the proper range.

    **Arguments:**

    dm
         The density matrix

    overlap
         The overlap matrix

    lf
         A LinalgFactory instance.

    **Optional arguments:**

    eps
         The threshold on the eigenvalue inequalities.

    occ_max
         The maximum occupation.

    A ValueError is raised when the density matrix has illegal eigenvalues.
    """
    # construct natural orbitals
    orb = lf.create_orbital()
    orb.derive_naturals(dm, overlap)
    if orb.occupations.min() < -eps:
        raise ConsistencyError(
            f"The density matrix has eigenvalues considerably smaller than zero. "
            f"Error = {orb.occupations.min():e}"
        )
    if orb.occupations.max() > occ_max + eps:
        raise ConsistencyError(
            f"The density matrix has eigenvalues considerably larger than one. "
            f"Error = {orb.occupations.max() - 1:e}"
        )


def get_level_shift(dm, overlap):
    """Construct a level shift operator.

    **Arguments:**

    dm
         A density matrix.

    overlap
         The overlap matrix

    **Returns:** The level-shift operator.
    """
    level_shift = overlap.copy()
    level_shift.idot(dm)
    level_shift.idot(overlap)
    return level_shift


def get_spin(orb_a, orb_b, overlap):
    """Returns the expectation values of the projected and squared spin

    **Arguments:**

    orb_a, orb_b
         The alpha and beta orbitals.

    overlap
         The overlap matrix

    **Returns:** sz, ssq
    """
    nalpha = orb_a.occupations.sum()
    nbeta = orb_b.occupations.sum()
    sz = (nalpha - nbeta) / 2
    correction = 0.0
    for ialpha in range(orb_a.nfn):
        if orb_a.occupations[ialpha] == 0.0:
            continue
        for ibeta in range(orb_b.nfn):
            if orb_b.occupations[ibeta] == 0.0:
                continue
            correction += (
                overlap.inner(orb_a.coeffs[:, ialpha], orb_b.coeffs[:, ibeta])
                ** 2
            )

    ssq = sz * (sz + 1) + nbeta - correction
    return sz, ssq


def get_homo_lumo(*orbs):
    """Return the HOMO and LUMO energy for the given expansion

    **Arguments:**

    orb1, orb2, ...
         DensityOrbital objects

    **Returns:**
    homo_energy, lumo_energy. (The second is None when all
    orbitals are occupied.)
    """
    homo_energy = max(orb.homo_energy for orb in orbs)
    lumo_energies = [orb.lumo_energy for orb in orbs]
    lumo_energies = [
        lumo_energy for lumo_energy in lumo_energies if lumo_energy is not None
    ]
    if len(lumo_energies) == 0:
        lumo_energy = None
    else:
        lumo_energy = min(lumo_energies)
    return homo_energy, lumo_energy


def compute_commutator(dm, fock, overlap, work, output):
    """Compute the dm-fock commutator, including an overlap matrix

    **Arguments:** (all TwoIndex objects)

    dm
         A density matrix

    fock
         A fock matrix

    overlap
         An overlap matrix

    work
         A temporary matrix

    output
         The output matrix in which the commutator, S.D.F-F.D.S, is stored.
    """
    # construct sdf
    work.assign(overlap)
    work.idot(dm)
    work.idot(fock)
    output.assign(work)
    # construct fds and subtract
    work.assign(fock)
    work.idot(dm)
    work.idot(overlap)
    output.iadd(work, factor=-1)


def compute_1dm_hf(orb, out=None, factor=1.0, clear=True, other=None):
    """Compute the HF density matrix in the AO basis and add it to the
    output argument.

       **Optional arguments:**

       out
            An output density matrix (DenseTwoIndex instance).

       factor
            The density matrix is multiplied by the given scalar.

       clear
            When set to False, the output density matrix is not zeroed
            first.

       other
            Another DenseOrbital object to construct a transfer-density
            matrix.
    """
    # parse first argument
    if out is None:
        if other is None:
            out = DenseTwoIndex(orb.nbasis)
        else:
            out = DenseTwoIndex(orb.nbasis, other.nbasis)
    else:
        check_type("out", out, DenseTwoIndex)

    # actual computation
    if clear:
        out.clear()

    if other is None:
        other = orb
    # tmp matrices
    # left vector of orbitals
    c1 = DenseTwoIndex(orb.nbasis, orb.nfn)
    c1.assign(orb.coeffs)
    # right vector of orbitals, either self or other
    c2 = c1.new()
    c2.assign(other.coeffs)
    # vector of occupation numbers
    occ = DenseOneIndex(orb.nfn)
    occ.assign(orb.occupations)

    c1.imul(occ)
    c1.idot_t(c2)

    # add final result
    out.iadd(c1, factor)
    return out
