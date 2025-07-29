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
# This module has been originally written and updated by Katharina Boguslawski (see CHANGELOG)
# Its current version contains updates from the PyBEST developer team.
#
# An original version of this implementation can also be found in 'Horton 2.0.0'.
# # However, this file has been updated and debugged. Compatibility with Horton is NOT
# guaranteed.
#
# 10.2022:
# This module has been rewritten by Emil Sujkowski
# - Created get_guess to make sure it is being taken from rpccdbase
#
# Detailed changes:
# See CHANGELOG

"""Correlated wavefunction implementations

This module contains restricted pCCD

Variables used in this module:
 :nocc:      number of (active) occupied orbitals in the principal configuration
 :pairs:     number of electron pairs
 :nvirt:     number of (active) virtual orbitals in the principal configuration
 :nbasis:    total number of basis functions

 Indexing convention:
  :i,j,k,..: occupied orbitals of principal configuration
  :a,b,c,..: virtual orbitals of principal configuration
  :p,q,r,..: general indices (occupied, virtual)

 Abbreviations used (if not mentioned in doc-strings):
  :L_pqrs: 2<pq|rs>-<pq|sr>
  :g_pqrs: <pq|rs>

 For more information see doc-strings.
"""

from pybest.geminals.geminals import Geminals
from pybest.geminals.rpccd_base import RpCCDBase
from pybest.log import log


class RpCCD(RpCCDBase, Geminals):
    """Restricted pCCD wavefunction class"""

    acronym = "RpCCD"
    long_name = "Restricted pair Coupled Cluster Doubles"
    reference = ""
    cluster_operator = "Tp"
    comment = "restricted"
    log.cite(
        "the pCCD method",
        "limacher2013",
        "boguslawski2014a",
        "boguslawski2014b",
    )
