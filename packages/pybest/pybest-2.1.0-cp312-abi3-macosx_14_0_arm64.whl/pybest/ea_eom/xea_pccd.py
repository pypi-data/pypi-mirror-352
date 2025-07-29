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
"""Electron Affinity Equation of Motion Coupled Cluster implementations for
   a pCCD reference function.

   Various EA flavors are selected from two classes:
    * REApCCD:   selects a specific single EA method based on pCCD
    * RDEApCCD:  selects a specific double EA method based on pCCD

This module has been written by:
2023: Katharina Boguslawski
"""

from typing import Any, Union

from pybest.ea_eom.dea_pccd0 import RDEApCCD0
from pybest.ea_eom.dea_pccd2 import RDEApCCD2
from pybest.ea_eom.dea_pccd4 import RDEApCCD4
from pybest.ea_eom.sea_pccd1 import REApCCD1
from pybest.ea_eom.sea_pccd1_sf import REApCCD1SF
from pybest.ea_eom.sea_pccd3 import REApCCD3
from pybest.exceptions import ArgumentError


class REApCCD:
    """
    Restricted Single Electron Affinity Equation of Motion Coupled Cluster
    class restricted to single EA for a pCCD reference function

    This class overwrites __new__ to create an instance of the proper EA-pCCD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyword argument alpha:
        * alpha=1: REApCCD1
        * alpha=3: REApCCD3

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = (
        "Electron Affinity Equation of Motion pair Coupled Cluster Doubles"
    )
    acronym = "EA-EOM-pCCD"
    reference = "pCCD"
    order = "EA"
    particle_hole_operator = "1p + 2p1h"
    cluster_operator = "Tp"

    def __new__(
        cls, *args: Any, **kwargs: Any
    ) -> Union[REApCCD1, REApCCD1SF, REApCCD3]:
        """Create a new instance of class REApCCD1 (alpha=1) or
        REApCCD3 (alpha=3).
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
        spin_free = kwargs.get("spinfree", False)
        if alpha == 1:
            if spin_free:
                return REApCCD1SF(*args, **kwargs)
            return REApCCD1(*args, **kwargs)
        if alpha == 3:
            return REApCCD3(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values "
            "are 1 and 3."
        )


class RDEApCCD:
    """
    Restricted Double Electron Affinity Equation of Motion Coupled Cluster
    class restricted to double EA for a pCCD reference function

    This class overwrites __new__ to create an instance of the proper DEA-pCCD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyword argument alpha:
        * alpha=0: REApCCD0
        * alpha=2: REApCCD2 (high-spin formulation)
        * alpha=4: REApCCD4 (high-spin formulation)

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = "Double Electron Affinity Equation of Motion pair Coupled Cluster Doubles"
    acronym = "DEA-EOM-pCCD"
    reference = "pCCD"
    order = "DEA"
    particle_hole_operator = "2p + 3p1h"
    cluster_operator = "Tp"

    def __new__(
        cls, *args: Any, **kwargs: Any
    ) -> Union[RDEApCCD0, RDEApCCD2, RDEApCCD4]:
        """Create a new instance of class RDEApCCD0 (alpha=0),
        RDEApCCD2 (alpha=2), or RDEApCCD4 (alpha=4).
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
            return RDEApCCD0(*args, **kwargs)
        if alpha == 2:
            return RDEApCCD2(*args, **kwargs)
        if alpha == 4:
            return RDEApCCD4(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values "
            "are 0, 2, and 4."
        )
