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

import pytest

import pybest.exceptions as exception_module
from pybest.exceptions import PyBestException

custom_exceptions = [
    cls
    for name, cls in exception_module.__dict__.items()
    if isinstance(cls, type)
]

custom_valueerror_exceptions = [
    cls
    for name, cls in exception_module.__dict__.items()
    if isinstance(cls, type) and issubclass(cls, ValueError)
]


@pytest.mark.parametrize("exception", custom_exceptions)
def test_are_subclasses_of_base_class(exception):
    with pytest.raises(PyBestException):
        raise exception


@pytest.mark.parametrize("exception", custom_exceptions)
def test_can_be_catched_with_baseclass_except(exception):
    try:
        raise exception
    except PyBestException:
        pass


@pytest.mark.parametrize("exception", custom_valueerror_exceptions)
def test_can_be_catched_with_valueerror_except(exception):
    try:
        raise exception
    except ValueError:
        pass
