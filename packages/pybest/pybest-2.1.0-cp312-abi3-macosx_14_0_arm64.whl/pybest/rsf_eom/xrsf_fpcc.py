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

from __future__ import annotations

from typing import Any

from pybest.exceptions import ArgumentError
from pybest.rsf_eom.rsf_ccd4 import RSFfpCCD4, RSFfpLCCD4
from pybest.rsf_eom.rsf_ccsd4 import RSFfpCCSD4, RSFfpLCCSD4


class RSFfpCCD:
    """
    Reversed spin flip frozen pair coupled cluster doubles
    class restricted to reversed spin flip for a fpCCD reference function

    This class overwrites __new__ to create an instance of the proper RSFfpCCD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyword argument alpha:
        * alpha=x: RSFfpCCDx

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = "Reversed Spin Flip frozen pair Coupled Cluster Doubles"
    acronym = "RSF-EOM-fpCCD"
    reference = "RfpCCD"

    def __new__(cls, *args: Any, **kwargs: Any) -> RSFfpCCD4 | None:
        """Called to create a new instance of class RSFfpCCDx (alpha=x).
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
        if alpha == 4:
            return RSFfpCCD4(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values are 4."
        )


class RSFfpCCSD:
    """
    Reversed spin flip frozen pair coupled cluster singles and doubles
    class restricted to reversed spin flip for a fpCCSD reference function

    This class overwrites __new__ to create an instance of the proper RSFfpCCSD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyword argument alpha:
        * alpha=x: RSFfpCCSDx

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = (
        "Reversed Spin Flip frozen pair Coupled Cluster Singles and Doubles"
    )
    acronym = "RSF-EOM-fpCCSD"
    reference = "RfpCCSD"

    def __new__(cls, *args: Any, **kwargs: Any) -> RSFfpCCSD4 | None:
        """Called to create a new instance of class RSFfpCCSDx (alpha=x).
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
        if alpha == 4:
            return RSFfpCCSD4(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values are 4."
        )


class RSFfpLCCSD:
    """
    Reversed Spin Flip frozen pair Linearized Coupled Cluster Singles and Doubles
    class restricted to reversed spin flip for a fpLCCSD reference function

    This class overwrites __new__ to create an instance of the proper RSFfpLCCSD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyword argument alpha:
        * alpha=x: RSFfpCCSDx

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = "Reversed Spin Flip frozen pair Linearized Coupled Cluster Singles and Doubles"
    acronym = "RSF-EOM-fpLCCSD"
    reference = "RfpLCCSD"

    def __new__(cls, *args: Any, **kwargs: Any) -> RSFfpLCCSD4 | None:
        """Called to create a new instance of class RSFfpLCCSDx (alpha=x).
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
        if alpha == 4:
            return RSFfpLCCSD4(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values are 4."
        )


class RSFfpLCCD:
    """
    Reversed Spin Flip frozen pair Linearized Coupled Cluster Doubles
    class restricted to reversed spin flip for a fpLCCD reference function

    This class overwrites __new__ to create an instance of the proper RSFfpLCCD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyword argument alpha:
        * alpha=x: RSFfpCCDx

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = (
        "Reversed Spin Flip frozen pair Linearized Coupled Cluster Doubles"
    )
    acronym = "RSF-EOM-fpLCCD"
    reference = "RfpLCCD"

    def __new__(cls, *args: Any, **kwargs: Any) -> RSFfpLCCD4 | None:
        """Called to create a new instance of class RSFfpLCCDx (alpha=x).
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
        if alpha == 4:
            return RSFfpLCCD4(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values are 4."
        )
