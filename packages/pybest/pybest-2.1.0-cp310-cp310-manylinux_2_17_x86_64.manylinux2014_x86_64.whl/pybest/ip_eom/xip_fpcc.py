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
various fpCC reference functions.

Various IP flavors are selected from two classes:
 * RIPfpCCD:     selects a specific single IP method based on fpCCD
 * RIPfpCCSD:    selects a specific single IP method based on fpCCSD
 * RIPfpLCCD:    selects a specific single IP method based on fpLCCD
 * RIPfpLCCSD:   selects a specific single IP method based on fpLCCSD
"""

from __future__ import annotations

from typing import Any

from pybest.exceptions import ArgumentError
from pybest.ip_eom.dip_rccd0 import RDIPfpCCD0, RDIPfpLCCD0
from pybest.ip_eom.dip_rccsd0 import RDIPfpCCSD0, RDIPfpLCCSD0
from pybest.ip_eom.sip_rccd1 import RIPfpCCD1, RIPfpLCCD1
from pybest.ip_eom.sip_rccd1_sf import RIPfpCCD1SF, RIPfpLCCD1SF
from pybest.ip_eom.sip_rccsd1 import RIPfpCCSD1, RIPfpLCCSD1
from pybest.ip_eom.sip_rccsd1_sf import RIPfpCCSD1SF, RIPfpLCCSD1SF


class RIPfpCCD:
    """
    Restricted Single Ionization Potential Equation of Motion Coupled Cluster
    class restricted to single IP for a fpCCD reference function

    This class overwrites __new__ to create an instance of the proper IP-fpCCD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyword argument alpha:
        * alpha=1: RIPfpCCD1

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = "Ionization Potential Equation of Motion frozen pair Coupled Cluster Doubles"
    acronym = "IP-EOM-fpCCD"
    reference = "fpCCD"
    order = "IP"

    def __new__(
        cls: object, *args: Any, **kwargs: dict[str, Any]
    ) -> RIPfpCCD1SF | RIPfpCCD1:
        """Called to create a new instance of class RIPfpCCD1 (alpha=1).
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
                return RIPfpCCD1SF(*args, **kwargs)
            return RIPfpCCD1(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values "
            "are 1."
        )


class RIPfpCCSD:
    """
    Restricted Single Ionization Potential Equation of Motion Coupled Cluster
    class restricted to single IP for a fpCCSD reference function

    This class overwrites __new__ to create an instance of the proper IP-fpCCSD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyword argument alpha:
        * alpha=1: RIPfpCCSD1

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = (
        "Ionization Potential Equation of Motion frozen pair Coupled Cluster "
        "Singles Doubles"
    )
    acronym = "IP-EOM-fpCCSD"
    reference = "fpCCSD"
    order = "IP"

    def __new__(
        cls: object, *args: Any, **kwargs: dict[str, Any]
    ) -> RIPfpCCSD1SF | RIPfpCCSD1:
        """Called to create a new instance of class RIPfpCCSD1 (alpha=1).
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
                return RIPfpCCSD1SF(*args, **kwargs)
            return RIPfpCCSD1(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values "
            "are 1."
        )


class RIPfpLCCD:
    """
    Restricted Single Ionization Potential Equation of Motion Coupled Cluster
    class restricted to single IP for a fpLCCD/pCCD-LCCD reference function

    This class overwrites __new__ to create an instance of the proper IP-fpLCCD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyword argument alpha:
        * alpha=1: RIPfpLCCD1

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = (
        "Ionization Potential Equation of Motion frozen pair Linearized Coupled "
        "Cluster Doubles"
    )
    acronym = "IP-EOM-fpLCCD"
    reference = "fpLCCD"
    order = "IP"

    def __new__(
        cls: object, *args, **kwargs: dict[str, Any]
    ) -> RIPfpLCCD1SF | RIPfpLCCD1:
        """Called to create a new instance of class RIPfpLCCD1 (alpha=1).
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
                return RIPfpLCCD1SF(*args, **kwargs)
            return RIPfpLCCD1(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values "
            "are 1."
        )


class RIPfpLCCSD:
    """
    Restricted Single Ionization Potential Equation of Motion Coupled Cluster
    class restricted to single IP for a fpLCCSD reference function

    This class overwrites __new__ to create an instance of the proper IP-fpLCCSD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyword argument alpha:
        * alpha=1: RIPfpLCCSD1

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = (
        "Ionization Potential Equation of Motion frozen pair Linearized Coupled "
        "Cluster Singles Doubles"
    )
    acronym = "IP-EOM-fpLCCSD"
    reference = "fpLCCSD"
    order = "IP"

    def __new__(
        cls: object, *args: Any, **kwargs: dict[str, Any]
    ) -> RIPfpLCCSD1SF | RIPfpLCCSD1:
        """Called to create a new instance of class RIPfpLCCSD1 (alpha=1).
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
                return RIPfpLCCSD1SF(*args, **kwargs)
            return RIPfpLCCSD1(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values "
            "are 1."
        )


class RDIPfpCCD:
    """
    Restricted Double Ionization Potential Equation of Motion Coupled Cluster
    class restricted to double IP for a fpCCD reference function

    This class overwrites __new__ to create an instance of the proper DIP-fpCCD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyword argument alpha:
        * alpha=0: RDIPfpCCD0

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = (
        "Double Ionization Potential Equation of Motion frozen pair Coupled "
        "Cluster Doubles"
    )
    acronym = "DIP-EOM-fpCCD"
    reference = "fpCCD"
    order = "DIP"

    def __new__(
        cls: object, *args: Any, **kwargs: dict[str, Any]
    ) -> RDIPfpCCD0:
        """Called to create a new instance of class RDIPfpCCD0 (alpha=0).
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
            return RDIPfpCCD0(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values "
            "are 0."
        )


class RDIPfpCCSD:
    """
    Restricted Double Ionization Potential Equation of Motion Coupled Cluster
    class restricted to double IP for a fpCCSD reference function

    This class overwrites __new__ to create an instance of the proper DIP-fpCCSD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyword argument alpha:
        * alpha=0: RIPfpCCSD0

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = (
        "Double Ionization Potential Equation of Motion frozen pair Coupled "
        "Cluster Singles Doubles"
    )
    acronym = "DIP-EOM-fpCCSD"
    reference = "fpCCSD"
    order = "DIP"

    def __new__(
        cls: object, *args: Any, **kwargs: dict[str, Any]
    ) -> RDIPfpCCSD0:
        """Called to create a new instance of class RDIPfpCCSD0 (alpha=0).
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
            return RDIPfpCCSD0(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values "
            "are 0."
        )


class RDIPfpLCCD:
    """
    Restricted Double Ionization Potential Equation of Motion Coupled Cluster
    class restricted to double IP for a fpLCCD reference function

    This class overwrites __new__ to create an instance of the proper DIP-fpLCCD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyword argument alpha:
        * alpha=0: RDIPfpLCCD0

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = (
        "Double Ionization Potential Equation of Motion frozen pair Linearized "
        "Coupled Cluster Doubles"
    )
    acronym = "DIP-EOM-fpLCCD"
    reference = "fpLCCD"
    order = "DIP"

    def __new__(
        cls: object, *args: Any, **kwargs: dict[str, Any]
    ) -> RDIPfpLCCD0:
        """Called to create a new instance of class RDIPfpLCCD0 (alpha=0).
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
            return RDIPfpLCCD0(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values "
            "are 0."
        )


class RDIPfpLCCSD:
    """
    Restricted Double Ionization Potential Equation of Motion Coupled Cluster
    class restricted to double IP for a fpLCCSD reference function

    This class overwrites __new__ to create an instance of the proper DIP-fpLCCSD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyw0rd argument alpha:
        * alpha=0: RDIPfpLCCSD0

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = (
        "Double Ionization Potential Equation of Motion frozen pair Linearized "
        "Coupled Cluster Singles Doubles"
    )
    acronym = "DIP-EOM-fpLCCSD"
    reference = "fpLCCSD"
    order = "DIP"

    def __new__(cls, *args: Any, **kwargs: dict[str, Any]) -> RDIPfpLCCSD0:
        """Called to create a new instance of class RDIPfpLCCSD0 (alpha=0).
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
            return RDIPfpLCCSD0(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values "
            "are 0."
        )
