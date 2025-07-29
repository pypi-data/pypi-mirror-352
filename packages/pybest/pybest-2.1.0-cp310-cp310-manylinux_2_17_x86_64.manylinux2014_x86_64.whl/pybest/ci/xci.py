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
"""Restricted Configuration Interaction implementations."""

from .csf_cid import CSFRCID
from .csf_cis import CSFRCIS
from .csf_cisd import CSFRCISD
from .csf_cvs_cis import CSFCVSRCIS
from .sd_cid import SDRCID
from .sd_cis import SDRCIS
from .sd_cisd import SDRCISD
from .sd_cvs_cis import SDCVSRCIS


class RCIS:
    """Restricted Configuration Interaction Singles module
    for Slater Determinant (SD) and Configuration State Function (CSF) basis.
    """

    def __new__(cls, *args, **kwargs):
        """Create a new instance of class CSFRCIS (csf=True) or SDRCIS (csf=False).

        **Arguments**

        cls
            class of which an instance was requested.

        args, kwargs
            remaining arguments that are passed to the object constructor
            expression. They are also used in the call of __init__(self[, ...]),
            which is invoked after __new__(), where self is the new instance
            created.
        """
        csf = kwargs.pop("csf", False)
        cvs = kwargs.pop("cvs", False)
        if csf:
            if cvs:
                return CSFCVSRCIS(*args, **kwargs)
            else:
                return CSFRCIS(*args, **kwargs)
        else:
            if cvs:
                return SDCVSRCIS(*args, **kwargs)
            else:
                return SDRCIS(*args, **kwargs)


class RCID:
    """Restricted Configuration Interaction Doubles module
    for Slater Determinant (SD) and Configuration State Function (CSF) basis.
    """

    def __new__(cls, *args, **kwargs):
        """Create a new instance of class CSFRCID (csf=True) or SDRCID (csf=False).
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
        csf = kwargs.pop("csf", False)
        if csf:
            return CSFRCID(*args, **kwargs)
        else:
            return SDRCID(*args, **kwargs)


class RCISD:
    """Restricted Configuration Interaction Singles Doubles module
    for Slater Determinant (SD) and Configuration State Function (CSF) basis.
    """

    def __new__(cls, *args, **kwargs):
        """Create a new instance of class CSFRCISD (csf=True) or SDRCISD (csf=False).
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
        csf = kwargs.pop("csf", False)
        if csf:
            return CSFRCISD(*args, **kwargs)
        else:
            return SDRCISD(*args, **kwargs)
