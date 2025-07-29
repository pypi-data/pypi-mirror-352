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
"""Auxiliary matrices

Variables used in this module:
 :nocc:      number of (active) occupied orbitals in the principle configuration
 :nvirt:     number of (active) virtual orbitals in the principle configuration
 :ncore:     number of frozen core orbitals in the principle configuration
 :nbasis:    total number of basis functions

 Indexing convention:
  :i,j,k,..: occupied orbitals of principle configuration
  :a,b,c,..: virtual orbitals of principle configuration
  :p,q,r,..: general indices (occupied, virtual)
"""

from pybest.exceptions import ArgumentError
from pybest.linalg import (
    DenseThreeIndex,
    DenseTwoIndex,
    LinalgFactory,
    OneIndex,
    TwoIndex,
)
from pybest.log import timer

__all__ = [
    "get_diag_fock_matrix",
    "get_fock_matrix",
]


def get_range(string, iocc, nbasis, start=0):
    """Returns dictionary with keys beginX, endX, begin(X+1), etc.
    *  string - any sequence of 'o' (occupied) and 'n' (nbasis)
    """
    range_ = {}
    ind = start
    for char in string:
        if char == "o":
            range_[f"begin{ind}"] = 0
            range_[f"end{ind}"] = iocc
        elif char == "n":
            range_[f"begin{ind}"] = 0
            range_[f"end{ind}"] = nbasis
        else:
            raise ArgumentError(f"Do not know how to handle choice {char}.")
        ind += 1
    return range_


@timer.with_section("H_eff: Fock_full")
def get_fock_matrix(lf, mo1, mo2, nocc, ncore=0):
    """Derive fock matrix.
    fock_pq:     one_pq + sum_m(2<pm|qm> - <pm|mq>),

    **Arguments:**

    mo1, mo2
         one- and two-electron integrals to be sorted.

    nocc, ncore
         number of occupied and core orbitals
    """
    iocc = ncore + nocc
    non = get_range("non", iocc, mo1.nbasis)
    #
    # Inactive Fock matrix
    #
    if isinstance(lf, LinalgFactory):
        fock = lf.create_two_index(mo1.nbasis)
        # temp storage
        tmp = lf.create_three_index()
    elif isinstance(lf, TwoIndex):
        fock = lf
        # temp storage
        tmp = DenseThreeIndex(fock.nbasis)
    else:
        raise ArgumentError(f"Do not now how to handle lf instance {lf}")
    mo2.contract("abcb->abc", out=tmp, factor=2.0, clear=True)
    mo2.contract("abcc->acb", out=tmp, factor=-1.0)
    tmp.contract("abc->ac", fock, clear=True, **non)
    fock.iadd(mo1)
    return fock


@timer.with_section("H_eff: Fock_diag")
def get_diag_fock_matrix(lf, mo1, mo2, nocc, ncore=0):
    """Derive the diagonal fock matrix.
    fock_pq:     one_pp + sum_m(2<pm|pm> - <pm|mp>),

    **Arguments:**

    mo1, mo2
         one- and two-electron integrals to be sorted.

    nocc, ncore
         number of occupied and core orbitals
    """
    iocc = ncore + nocc
    no = get_range("no", iocc, mo1.nbasis)
    #
    # Inactive Fock matrix
    #
    if isinstance(lf, LinalgFactory):
        fock = lf.create_one_index(mo1.nbasis)
        # temp storage
        tmp = lf.create_two_index()
    elif isinstance(lf, OneIndex):
        fock = lf
        # temp storage
        tmp = DenseTwoIndex(fock.nbasis)
    else:
        raise ArgumentError(f"Do not now how to handle lf instance {lf}")
    mo2.contract("abab->ab", out=tmp, factor=2.0, clear=True)
    mo2.contract("abba->ab", out=tmp, factor=-1.0)
    tmp.contract("ab->a", fock, clear=True, **no)
    fock.iadd(mo1.copy_diagonal())
    return fock
