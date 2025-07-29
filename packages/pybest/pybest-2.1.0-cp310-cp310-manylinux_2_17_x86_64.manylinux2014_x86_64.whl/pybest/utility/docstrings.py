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
# 2024-04-24: created by Katharina Boguslawski (taken from old utils.py)

"""Utility functions to modify docstrings"""

__all__ = [
    "doc_inherit",
]


def doc_inherit(base_class):
    """Docstring inheriting method descriptor

    doc_inherit decorator

    Usage:

    .. code-block:: python

         class Foo(object):
             def foo(self):
                 "Frobber"
                 pass

         class Bar(Foo):
             @doc_inherit(Foo)
             def foo(self):
                 pass

    Now, ``Bar.foo.__doc__ == Bar().foo.__doc__ == Foo.foo.__doc__ ==
    "Frobber"``
    """

    def decorator(method):
        overridden = getattr(base_class, method.__name__, None)
        if overridden is None:
            raise NameError(f"Can't find method '{overridden}' in base class.")
        method.__doc__ = overridden.__doc__
        return method

    return decorator
