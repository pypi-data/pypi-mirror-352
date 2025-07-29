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
"""Helper classes"""

__all__ = [
    "PropertyHelper",
]


class PropertyHelper:
    """Auxiliary class to set up some x_y attributes used in other classes."""

    def __init__(self, method, arg, doc):
        self.method = method
        self.arg = arg
        self.__doc__ = doc

    def __get__(self, obj, objtype):
        """Get the attribute value."""
        #
        # For doc strings:
        #
        if obj is None:
            return self
        #
        # For actual use
        #
        try:
            return self.method(obj, self.arg)
        except KeyError as e:
            raise AttributeError(
                f"The requested attribute {e.args[0]} is not available."
            ) from None
