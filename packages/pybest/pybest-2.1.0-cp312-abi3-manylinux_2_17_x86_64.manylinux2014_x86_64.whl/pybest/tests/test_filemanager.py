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


from pathlib import PurePath

import pytest

from pybest import filemanager

test_dirs = [
    ("foo0"),
    ("foo1"),
    ("foo2"),
    ("foo3"),
    ("foo4"),
]

test_join = [
    ("foo", "foobar0"),
    ("foo", "foobar1"),
    ("foo", "foobar2"),
]


@pytest.mark.parametrize("temp_dir", test_dirs)
def test_temp_dir(temp_dir):
    filemanager.temp_dir = temp_dir
    assert str(PurePath(filemanager.temp_dir).name) == temp_dir
    assert filemanager.temp_dir.exists()
    assert filemanager.temp_dir.is_dir()


@pytest.mark.parametrize("result_dir", test_dirs)
def test_result_dir(result_dir):
    filemanager.result_dir = result_dir
    assert str(PurePath(filemanager.result_dir).name) == result_dir
    assert filemanager.result_dir.exists()
    assert filemanager.result_dir.is_dir()


@pytest.mark.parametrize("temp_dir", test_dirs)
def test_clean_up_temporary_directory(temp_dir):
    filemanager.temp_dir = temp_dir
    assert str(PurePath(filemanager.temp_dir).name) == temp_dir
    assert filemanager.temp_dir.exists()
    assert filemanager.temp_dir.is_dir()

    filemanager.clean_up_temporary_directory()
    assert not filemanager.temp_dir.exists()


@pytest.mark.parametrize("dir_, file_name", test_join)
def test_result_path(dir_, file_name):
    filemanager.result_dir = dir_
    assert str(PurePath(filemanager.result_dir).name) == dir_
    assert filemanager.result_dir.exists()
    assert filemanager.result_dir.is_dir()

    dir_file = filemanager.result_path(file_name)
    # check that we landed in correct parent dir
    assert dir_file.parent.absolute() == filemanager.result_dir.absolute()

    # since we don't write anything, test if file basename was rendered correctly
    assert dir_file.name == file_name


@pytest.mark.parametrize("dir_, file_name", test_join)
def test_temp_path(dir_, file_name):
    filemanager.temp_dir = dir_
    assert str(PurePath(filemanager.temp_dir).name) == dir_
    assert filemanager.temp_dir.exists()
    assert filemanager.temp_dir.is_dir()

    dir_file = filemanager.temp_path(file_name)
    # check that we landed in correct parent dir
    assert dir_file.parent.absolute() == filemanager.temp_dir.absolute()

    # since we don't write anything, test if file basename was rendered correctly
    assert dir_file.name == file_name
