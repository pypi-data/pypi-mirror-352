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
#
# Detailed changelog:
# 2024/2025: added by Saman Behjou
#
from typing import Any, Union

from pybest.ea_eom.sea_rccd1 import SEACCD1, SEALCCD1, SEAfpCCD1, SEAfpLCCD1
from pybest.ea_eom.sea_rccsd1 import (
    SEACCSD1,
    SEALCCSD1,
    SEAfpCCSD1,
    SEAfpLCCSD1,
)
from pybest.exceptions import ArgumentError


class REACCSD:
    """Single electron attachment for a restricted Coupled Cluster Singles and Doubles
    reference function.

    This class overwrites __new__ to create an instance of the proper REACCSD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyward argument alpha:
        * alpha=x: REACCSDx

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = (
        "Single Electron Attachment Coupled Cluster Singles and Doubles"
    )
    acronym = "REA-EOM-CCSD"
    reference = "RCCSD"
    order = "EA"

    def __new__(cls, *args: Any, **kwargs: Any) -> Union[SEACCSD1, None]:
        """Called to create a new instance of class REACCSDx (alpha=x).
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
            return SEACCSD1(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values are 1."
        )


class REAfpCCSD:
    """Single electron attachment for a restricted frozen-pair Coupled Cluster Singles and Doubles
    reference function.

    This class overwrites __new__ to create an instance of the proper REAfpCCSD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyward argument alpha:
        * alpha=x: SEAfpCCSDx

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = "Single Electron Attachment Equation of Motion frozen pair Coupled Cluster Singles and Doubles"
    acronym = "SEA-EOM-fpCCSD"
    reference = "fpCCSD"
    order = "EA"

    def __new__(cls, *args: Any, **kwargs: Any) -> Union[SEAfpCCSD1, None]:
        """Called to create a new instance of class SEAfpCCSDx (alpha=x).
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
            return SEAfpCCSD1(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values are 1."
        )


class REALCCSD:
    """Single electron attachment for a restricted Linearized Coupled Cluster Singles and Doubles

    This class overwrites __new__ to create an instance of the proper REALCCSD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyward argument alpha:
        * alpha=x: SEALCCSDx

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = (
        "Single Electron Attachment Equation of Motion Linearized Coupled "
        "Cluster Singles and Doubles"
    )
    acronym = "SEA-EOM-LCCSD"
    reference = "LCCSD"
    order = "EA"

    def __new__(cls, *args: Any, **kwargs: Any) -> Union[SEALCCSD1, None]:
        """Called to create a new instance of class SEALCCSDx (alpha=x).
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
            return SEALCCSD1(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported value is 1."
        )


class REAfpLCCSD:
    """Restricted Single Electron Attachment Equation of Motion Coupled Cluster
    class restricted to single EA for a fpLCCSD reference function

    This class overwrites __new__ to create an instance of the proper EA-fpLCCSD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyword argument alpha:
        * alpha=1: SEAfpLCCSD1

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = (
        "Single Electron Attachment Equation of Motion Linearized Coupled "
        "Cluster Singles Doubles"
    )
    acronym = "EA-EOM-fpLCCSD"
    reference = "fpLCCSD"
    order = "EA"

    def __new__(cls, *args: Any, **kwargs: Any) -> Union[SEAfpLCCSD1, None]:
        """Called to create a new instance of class SEAfpLCCSD1 (alpha=1).
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
        alpha = kwargs.pop("alpha", 1)
        if alpha == 1:
            return SEAfpLCCSD1(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values "
            "are 1."
        )


class REACCD:
    """Single electron attachment for a restricted Coupled Cluster Doubles
    reference function.

    This class overwrites __new__ to create an instance of the proper REACCD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyward argument alpha:
        * alpha=x: REACCDx

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = "Single Electron Attachment Coupled Cluster Doubles"
    acronym = "REA-EOM-CCD"
    reference = "RCCD"
    order = "EA"

    def __new__(cls, *args: Any, **kwargs: Any) -> Union[SEACCD1, None]:
        """Called to create a new instance of class REACCDx (alpha=x).
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
            return SEACCD1(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values are 1."
        )


class REAfpCCD:
    """Single electron attachment for a restricted frozen-pair Coupled Cluster Doubles
    reference function.

    This class overwrites __new__ to create an instance of the proper REAfpCCD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyward argument alpha:
        * alpha=x: SEAfpCCDx

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = "Single Electron Attachment Equation of Motion frozen pair Coupled Cluster Doubles"
    acronym = "SEA-EOM-CCD"
    reference = "fpCCD"
    order = "EA"

    def __new__(cls, *args: Any, **kwargs: Any) -> Union[SEAfpCCD1, None]:
        """Called to create a new instance of class SEAfpCCDx (alpha=x).
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
            return SEAfpCCD1(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values are 1."
        )


class REALCCD:
    """Single electron attachment for a restricted Linearized Coupled Cluster Doubles
    reference function.

    This class overwrites __new__ to create an instance of the proper REALCCD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyward argument alpha:
        * alpha=x: SEALCCDx

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = (
        "Single Electron Attachment Equation of Motion Linearized Coupled "
        "Cluster Doubles"
    )
    acronym = "SEA-EOM-LCCD"
    reference = "LCCD"
    order = "EA"

    def __new__(cls, *args: Any, **kwargs: Any) -> Union[SEALCCD1, None]:
        """Called to create a new instance of class SEALCCDx (alpha=x).
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
            return SEALCCD1(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values are 1."
        )


class REAfpLCCD:
    """Restricted Single Electron Attachment Equation of Motion Coupled Cluster
    class restricted to single EA for a fpLCCD reference function

    This class overwrites __new__ to create an instance of the proper EA-fpLCCD
    class for a user-specified number of unpaired electrons, which are passed
    using the keyword argument alpha:
        * alpha=1: SEAfpLCCD1

    The return value of __new__() is the new object instance. It has no other
    purpose.
    """

    long_name = (
        "Single Electron Attachment Equation of Motion Coupled "
        "Cluster Doubles"
    )
    acronym = "EA-EOM-fpLCCD"
    reference = "fpLCCD"
    order = "EA"

    def __new__(cls, *args: Any, **kwargs: Any) -> Union[SEAfpLCCD1, None]:
        """Called to create a new instance of class SEAfpLCCD1 (alpha=1).
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
            return SEAfpLCCD1(*args, **kwargs)
        raise ArgumentError(
            f"Unknown value of {alpha} for kwarg alpha. Supported values "
            "are 1."
        )
