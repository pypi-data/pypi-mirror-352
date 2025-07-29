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
# 2025-02: unification of variables and type hints (Julian Świerczyński)

"""Ionization Potential Equation of Motion Coupled Cluster implementations for
a pCCD reference function.

Various IP flavors are selected from two classes:
 * RIPpCCD:   selects a specific single IP method based on pCCD
 * RDIPpCCD:  selects a specific double IP method based on pCCD
"""

from __future__ import annotations

from typing import Any

from pybest.exceptions import ArgumentError
from pybest.ip_eom.dip_pccd0 import RDIPpCCD0
from pybest.ip_eom.dip_pccd2 import RDIPpCCD2
from pybest.ip_eom.dip_pccd4 import RDIPpCCD4
from pybest.ip_eom.sip_pccd1 import RIPpCCD1
from pybest.ip_eom.sip_pccd3 import RIPpCCD3


class RIPpCCD:
    """
    Restricted Single Ionization Potential Equation of Motion Coupled Cluster
    class restricted to single IP for a pCCD reference function

    This class overwrites __new__ to create an instance of the proper IP-pCCD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyward argument alpha:
        * alpha=1: RIPpCCD1
        * alpha=3: RIPpCCD3

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = (
        "Ionization Potential Equation of Motion pair Coupled Cluster Doubles"
    )
    acronym = "IP-EOM-pCCD"
    reference = "pCCD"
    order = "IP"

    def __new__(
        cls: object, *args: Any, **kwargs: dict[str, Any]
    ) -> RIPpCCD1 | RIPpCCD3:
        """Called to create a new instance of class RIPpCCD1 (alpha=1) or
        RIPpCCD3 (alpha=3).
        The return value of __new__() is a new object instance.

        **Arguments**

        cls
            class of which an instance was requested.

        args, kwargs
            remaining arguments that are passed to the object constructor
            expression. They are also used in the call of __init__(self[, ...]),
            which is invoked after __new__(), where self is the new instance
            created.
        """
        alpha = kwargs.pop("alpha", -1)
        if alpha == 1:
            return RIPpCCD1(*args, **kwargs)
        if alpha == 3:
            return RIPpCCD3(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values "
            "are 1 and 3."
        )


class RDIPpCCD:
    """
    Restricted Double Ionization Potential Equation of Motion Coupled Cluster
    class restricted to double IP for a pCCD reference function

    This class overwrites __new__ to create an instance of the proper DIP-pCCD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyward argument alpha:
        * alpha=0: RIPpCCD0
        * alpha=2: RIPpCCD2 (high-spin formulation)
        * alpha=4: RIPpCCD4 (high-spin formulation)

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = "Dpuble Ionization Potential Equation of Motion pair Coupled Cluster Doubles"
    acronym = "DIP-EOM-pCCD"
    reference = "pCCD"
    order = "DIP"

    def __new__(
        cls: object, *args: Any, **kwargs: dict[str, Any]
    ) -> RDIPpCCD0 | RDIPpCCD2 | RDIPpCCD4:
        """Called to create a new instance of class RDIPpCCD0 (alpha=0),
        RDIPpCCD2 (alpha=2), or RDIPpCCD4 (alpha=4).
        The return value of __new__() is a new object instance.

        **Arguments**

        cls
            class of which an instance was requested.

        args, kwargs
            remaining arguments that are passed to the object constructor
            expression. They are also used in the call of __init__(self[, ...]),
            which is invoked after __new__(), where self is the new instance
            created.
        """
        alpha = kwargs.pop("alpha", -1)
        if alpha == 0:
            return RDIPpCCD0(*args, **kwargs)
        if alpha == 2:
            return RDIPpCCD2(*args, **kwargs)
        if alpha == 4:
            return RDIPpCCD4(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values "
            "are 0, 2, and 4."
        )
