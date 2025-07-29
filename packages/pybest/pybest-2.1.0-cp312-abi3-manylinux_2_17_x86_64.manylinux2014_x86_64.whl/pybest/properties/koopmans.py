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

"""Single and pair orbital energies based on the conventional Koopmans' theorem

This module computes orbital energies from Koopmans' theorem.

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
from pybest.properties.orbital_energy_base import OrbitalEnergyBase


class Koopmans(OrbitalEnergyBase):
    """Calculates single and pair orbital energies based on Koopmans' theorem.

    This class provides functionality to compute orbital energies for closed-shell reference systems
    using the assumptions of Koopmans' theorem, which approximates ionization energies and electron
    affinities by the orbital energies of a system. It extends the `OrbitalEnergyBase` class with
    Koopmans'-specific properties and methods.
    Abbreviations used (if not mentioned in doc-strings):
    :L_pqrs: 2<pq|rs>-<pq|sr>
    :g_pqrs: <pq|rs>

    For more information see doc-strings.

    Args:
        OrbitalEnergyBase (class): The base class providing foundational properties and methods
        for orbital energy calculations.
    """

    acronym = "Koopmans"
    long_name = "Orbital energies from Koopmans' theorem"
    reference = "HF/pCCD"
    comment = "Works for closed-shell systems (restricted)"

    @timer.with_section("Koopmans")
    def get_property(self) -> None:
        """Calculate and store orbital energies from Koopmans' theorem.

        This method computes:
        - ** Koopmans' Single Orbital Energies** (`e_orb_ks`): Uses the Fock matrix for both occupied
        (`e_ii = -f_ii`) and virtual orbitals (`e_aa = -f_aa`).
        - ** Koopmans' Pair Orbital Energies** (`e_orb_kp`): Includes occupied and virtual orbital
        pairs, with two-electron integral contractions applied where relevant.

         'e_orb_ks': (1d array) single (s) orbital energies based on Koopmans' (k) theorem.
         'e_orb_kp': (2d array) pair (p) orbital energies based on Koopmans' (k) theorem.
        """
        # Get ranges
        na = self.occ_model.nact[0]
        vvvv = self.get_range("vvvv")
        oooo = self.get_range("oooo")
        gpqpq = self.from_cache("gpqpq")
        gppqq = self.from_cache("gppqq")
        fock = self.from_cache("fock")

        #
        # Single orbital energies
        # For occupied e_ii = f_ii
        # For virtual  e_aa = f_aa
        #
        e_orb_ks = fock.copy()
        self.checkpoint.update("e_orb_ks", e_orb_ks)

        #
        # Pair orbital energies
        # i = alpha spin; I = beta spin
        #
        e_orb_kp = self.lf.create_two_index(na, na)
        fock.expand("a->ab", e_orb_kp)
        fock.expand("b->ab", e_orb_kp)
        #
        # For occupied orbitals
        # (i,j) block of m_s=1
        # e_ij = f_ii + f_jj - (<ij|ij> - <ij|ji>)
        #
        e_orb_kp_1 = e_orb_kp.copy()
        gpqpq.contract("ab->ab", e_orb_kp_1, factor=-1.0, **oooo)
        gppqq.contract("ab->ab", e_orb_kp_1, factor=1.0, **oooo)
        #
        # (i,J) block of m_s=0
        # e_iJ = f_ii + f_JJ -  <iJ|iJ>
        #
        e_orb_kp_0 = e_orb_kp.copy()
        gpqpq.contract("ab->ab", e_orb_kp_0, factor=-1.0, **oooo)
        #
        # For virtual orbitals
        # (a,b) block of m_s=1
        # e_ab = f_aa + f_bb + (<ab|ab> - <ab|ba>)
        #
        gpqpq.contract("ab->ab", e_orb_kp_1, factor=1.0, **vvvv)
        gppqq.contract("ab->ab", e_orb_kp_1, factor=-1.0, **vvvv)
        # Reset diagonal to 0
        e_orb_kp_1.assign_diagonal(0.0)
        #
        # (a,B) block of m_s=0
        # e_aB = f_aa + f_BB +  <aB|aB>
        #
        gpqpq.contract("ab->ab", e_orb_kp_0, factor=1.0, **vvvv)
        #
        # Update all checkpoint entries
        #
        self.checkpoint.update("e_orb_kp_0", e_orb_kp_0)
        self.checkpoint.update("e_orb_kp_1", e_orb_kp_1)
