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
from pybest.rsf_eom.rsf_ccd4 import RSFCCD4, RSFLCCD4
from pybest.rsf_eom.rsf_ccsd4 import RSFCCSD4, RSFLCCSD4


class RSFCCD:
    """
    Reversed spin flip coupled cluster doubles
    class restricted to reversed spin flip for a CCD reference function

    This class overwrites __new__ to create an instance of the proper RSFCCD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyword argument alpha:
        * alpha=x: RSFCCDx

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = "Reversed Spin Flip Coupled Cluster Doubles"
    acronym = "RSF-EOM-CCD"
    reference = "RCCD"

    def __new__(cls, *args: Any, **kwargs: Any) -> RSFCCD4 | None:
        """Called to create a new instance of class RSFCCDx (alpha=x).
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
            return RSFCCD4(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values are 4."
        )


class RSFLCCD:
    """
    Reversed spin flip linearized coupled cluster doubles
    class restricted to reversed spin flip for a LCCD reference function

    This class overwrites __new__ to create an instance of the proper RSFLCCD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyword argument alpha:
        * alpha=x: RSFLCCDx

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = "Reversed Spin Flip Linearized Coupled Cluster Doubles"
    acronym = "RSF-EOM-LCCD"
    reference = "RLCCD"

    def __new__(cls, *args: Any, **kwargs: Any) -> RSFLCCD4 | None:
        """Called to create a new instance of class RSFLCCDx (alpha=x).
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
            return RSFLCCD4(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values are 4."
        )


class RSFCCSD:
    """
    Reversed spin flip coupled cluster singles and doubles
    class restricted to reversed spin flip for a CCSD reference function

    This class overwrites __new__ to create an instance of the proper RSFCCSD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyword argument alpha:
        * alpha=x: RSFCCSDx
    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = "Reversed Spin Flip Coupled Cluster Singles and Doubles"
    acronym = "RSF-CCSD"
    reference = "RCCSD"

    def __new__(cls, *args: Any, **kwargs: Any) -> RSFCCSD4 | None:
        """Called to create a new instance of class RSFCCSDx (alpha=x).
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
            return RSFCCSD4(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values are 4."
        )


class RSFLCCSD:
    """
    Reversed spin flip linearized coupled cluster singles and doubles
    class restricted to reversed spin flip for a LCCSD reference function

    This class overwrites __new__ to create an instance of the proper RSFLCCSD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyword argument alpha:
        * alpha=x: RSFLCCSDx

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = (
        "Reversed Spin Flip Linearized Coupled Cluster Singles and Doubles"
    )
    acronym = "RSF-EOM-LCCSD"
    reference = "RLCCSD"

    def __new__(cls, *args: Any, **kwargs: Any) -> RSFLCCSD4 | None:
        """Called to create a new instance of class RSFLCCSDx (alpha=x).
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
            return RSFLCCSD4(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values are 4."
        )
