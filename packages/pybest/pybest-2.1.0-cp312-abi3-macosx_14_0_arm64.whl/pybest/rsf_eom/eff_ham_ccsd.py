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
# The RSF-CC sub-package has been originally written and updated by Aleksandra Leszczyk (see CHANGELOG)
# Its current version contains updates from the PyBEST developer team.
#
# 2023/24:
# This file has been written by Emil Sujkowski (original version)

"""RCC Effective Hamiltonian class

Variables used in this module:
:nocc:      number of occupied orbitals in the principle configuration
:nvirt:     number of virtual orbitals in the principle configuration
:nbasis:    total number of basis functions

Indexing convention:
:i,j,k,..: occupied alpha orbitals of principle configuration
:I,J,K,..: occupied beta orbitals of principle configuration
:a,b,c,..: virtual alpha orbitals of principle configuration
"""

from .eff_ham_ccsd_base import EffectiveHamiltonianRCCSDBase


class EffectiveHamiltonianRLCCSD(EffectiveHamiltonianRCCSDBase):
    """Effective Hamiltonian Restricted Linearized Coupled Cluster Singles and Doubles class"""

    disconnected: bool = False


class EffectiveHamiltonianRCCSD(EffectiveHamiltonianRCCSDBase):
    """Effective Hamiltonian Restricted Coupled Cluster Singles and Doubles class"""

    disconnected: bool = True
