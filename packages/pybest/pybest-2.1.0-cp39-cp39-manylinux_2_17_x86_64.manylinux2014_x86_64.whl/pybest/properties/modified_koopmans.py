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
# 11/2024:
# This file has been written by Seyedehdelaram Jahani (original version)
#

"""Single and pair orbital energies based on the conventional Modified Koopmans' theorem

This module computes orbital energies from the modified Koopmans' theorem.

 Indexing convention:
  :i,j,k,..: occupied orbitals of principal configuration
  :a,b,c,..: virtual orbitals of principal configuration
  :p,q,r,..: general indices (occupied, virtual)

 Abbreviations used (if not mentioned in doc-strings):
  :L_pqrs: 2<pq|rs>-<pq|sr>
  :g_pqrs: <pq|rs>

 For more information see doc-strings.
"""

from pybest.log import timer
from pybest.properties.koopmans import Koopmans


class ModifiedKoopmans(Koopmans):
    """Calculates single and pair orbital energies based on modified Koopmans' theorem.

    This class refines orbital energy estimates for closed-shell reference systems by modifying
    the Koopmans' theorem, improving the approximation of ionization energies and electron affinities
    by incorporating electron correlation effects.

    Abbreviations used (if not mentioned in doc-strings):
    :L_pqrs: 2<pq|rs>-<pq|sr>
    :g_pqrs: <pq|rs>

    For more information see doc-strings.

    Args:
        Koopmans (class): Inherits from the `Koopmans` class, which provides the base Koopmans' theorem
        functionality, including single and pair orbital energy calculations for restricted (closed-shell) systems.

    """

    acronym = "Modified Koopmans"
    long_name = "Orbital energies from the modified Koopmans' theorem"
    reference = "HF/pCCD"
    comment = "Works for closed-shell systems (restricted)"

    @timer.with_section("ModifiedKoopmans")
    def get_property(self) -> None:
        """Calculate and store pCCD-based single and pair orbital energies from Modified Koopmans' theorem.

        This method computes:
        - ** Modified Koopmans' Single Orbital Energies** (`e_orb_mks`): Adjusts single orbital energies using
        Fock matrix elements and correlation terms from electron integrals.
        - ** Modified Koopmans' Pair Orbital Energies** ('e_orb_mkp'): Computes modified koopmans' to pair orbital energies
        for both occupied and virtual orbitals, applying correlation terms from two-electron integrals.

        **Arguments:**

        'e_orb_mks': (1d array) modification (m) to single (s) orbital energies based on
        Koopmans' (k) theorem.
        'e_orb_mkp': (2d array) modification (m) to pair (p) orbital energies based on
        Koopmans' (k) theorem.
        """
        # Get ranges
        na = self.occ_model.nact[0]
        no = self.occ_model.nacto[0]
        cia = self.checkpoint["t_p"]
        vvvv = self.get_range("vvvv")
        oooo = self.get_range("oooo")
        ov = self.get_range("ov")
        o4 = self.get_range("o", 4)
        v4 = self.get_range("v", 4)

        # Get necessary matrices from cache
        gppqq = self.from_cache("gppqq")
        gpqpq = self.from_cache("gpqpq")
        fock = self.from_cache("fock")

        #
        # Modified Koopmans' for single orbital energies
        # i = alpha spin; I = beta spin
        #
        e_orb_mks = fock.copy()
        #
        # For occupied orbitals
        # e_ii = f_ii + sum_c <iI|cC> t_iIcC
        #
        gppqq.contract("ab,ab->a", cia, out=e_orb_mks, factor=1.0, **ov, **o4)
        #
        # For virtual orbitals
        # e_aa = f_aa - sum_k <kK|aA> t_kKaA
        #
        gppqq.contract("ab,ab->b", cia, out=e_orb_mks, factor=-1.0, **ov, **v4)
        #
        # Update checkpoint entries
        #
        self.checkpoint.update("e_orb_mks", e_orb_mks)

        #
        # Modified Koopmans' for pair orbital energies
        #
        e_orb_mkp = self.lf.create_two_index(na, na)
        #
        # e_ij = e_ii + e_jj + [...]
        #
        e_orb_mks.expand("a->ab", e_orb_mkp)
        e_orb_mks.expand("b->ab", e_orb_mkp)
        #
        # For occupied orbitals
        # Same spin and triplet states (block of m_s=1)
        # e_ij = f_ii + f_jj - <ij||ij> + sum_c <iI|cC> t_iIcC + sum_c <jJ|cC> t_jJcC
        #      = e_ii + e_jj - <ij||ij>
        #
        e_orb_mkp_1 = e_orb_mkp.copy()
        gpqpq.contract("ab->ab", e_orb_mkp_1, factor=-1.0, **oooo)
        gppqq.contract("ab->ab", e_orb_mkp_1, factor=1.0, **oooo)
        #
        # Spin pair, singlet and diagonal part (block of m_s=0)
        # e_iJ = f_ii + f_JJ - <iJ|iJ> + sum_c <iI|cC> t_iIcC + sum_c <jJ|cC> t_jJcC - sum_c <iI|cC> t_iIcC delta_ij
        #      = e_ii + e_JJ - <iJ||iJ> - sum_c <iI|cC> t_iIcC delta_ij
        #
        e_orb_mkp_0 = e_orb_mkp.copy()
        gpqpq.contract("ab->ab", e_orb_mkp_0, factor=-1.0, **oooo)
        tmp = gppqq.contract("ab,cb->ac", cia, factor=-1.0, **ov)
        e_orb_mkp_0.iadd_diagonal(tmp.copy_diagonal(), end0=no)
        #
        # For virtual orbitals
        # Same spin and triplet states (block of m_s=1)
        # e_ab = f_aa + f_bb + <ab||ab> + sum_k <kK|aA> t_kKaA + sum_k <kK|bB> t_kKbB
        #      = e_aa + e_bb + <ab||ab>
        #
        gpqpq.contract("ab->ab", e_orb_mkp_1, factor=1.0, **vvvv)
        gppqq.contract("ab->ab", e_orb_mkp_1, factor=-1.0, **vvvv)
        #
        # Spin pair, singlet and diagonal part (block of m_s=0)
        # e_aB = f_aa + f_BB + <aB|aB> - sum_k <kK|aA> t_kKaA - sum_k <kK|bB> t_kKbB + sum_k <kK|aA> t_kKaA delta_ab
        #      = e_aa + e_BB + <aB||aB> + sum_k <kK|aA> t_kKaA delta_ab
        #
        gpqpq.contract("ab->ab", e_orb_mkp_0, factor=1.0, **vvvv)
        tmp = gppqq.contract("ab,ac->bc", cia, factor=1.0, **ov)
        e_orb_mkp.iadd_diagonal(tmp.copy_diagonal(), begin0=no)
        # Reset diagonal to 0
        e_orb_mkp_1.assign_diagonal(0.0)
        #
        # Update all checkpoint entries
        #
        self.checkpoint.update("e_orb_mkp_0", e_orb_mkp_0)
        self.checkpoint.update("e_orb_mkp_1", e_orb_mkp_1)
