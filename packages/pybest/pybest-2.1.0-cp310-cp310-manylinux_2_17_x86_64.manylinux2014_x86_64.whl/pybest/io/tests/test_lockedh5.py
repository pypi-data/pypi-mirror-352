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

from pybest.io.lockedh5 import LockedH5File


def test_init_lockedh5(tmp_dir):
    """see if can LockedH5file can open existing file"""
    # just a silly test
    temp_file = tmp_dir / "foo.h5"
    temp_file.touch()
    with LockedH5File(temp_file.absolute(), mode="w"):
        pass


def test_init_lockedh5_can_throw_ioerror(tmp_dir):
    """tests if LockedH5file can throw IOError on non-existent files"""
    # test error handling in h5.File constructor
    temp_file = tmp_dir / "foo.h5"
    with pytest.raises(IOError):
        with LockedH5File(temp_file.absolute(), mode="r", wait=0.1, count=3):
            pass


def test_init_lockedh5_can_throw_valueerror(tmp_dir):
    # test error handling in h5.File constructor
    temp_file = tmp_dir / "foo.h5"
    with pytest.raises(ValueError):
        with LockedH5File(
            temp_file.absolute(),
            driver="fubar",
            wait=0.1,
            count=3,
        ):
            pass


def test_locked4(tmp_dir):
    # test error handling of wrong driver
    temp_file = tmp_dir / "foo.h5"
    with pytest.raises(ValueError):
        with LockedH5File(temp_file.absolute(), driver="core", mode="w"):
            pass
