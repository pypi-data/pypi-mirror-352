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
"""PyBEST's internal checkpoint class to generate output files and dump to disk"""

from __future__ import annotations

from collections import UserDict
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, overload

if TYPE_CHECKING:
    from _typeshed import SupportsKeysAndGetItem

from pybest import filemanager
from pybest.exceptions import ArgumentError

from .iodata import IOData


class CheckPoint(UserDict):
    """Base class for class performing checkpoints, that is, writing numerically
    useful data to disk. It stores all data in an IOData container and
    can dump this information to disk using PyBEST's internal format.
    """

    def __init__(self, data_dict: dict[str, Any] | None = None) -> None:
        """Initialize all attributes with default values

        Args:
            data_dict (dict | None, optional): a dictionary containing some data. Defaults to None.
        """
        # Empty dictionary, will be passed to IOData container
        if data_dict is None:
            data_dict = dict()
        self._data = data_dict
        self._iodata = IOData()

    @property
    def data(self) -> dict:
        """The dict from UserDict that contains all data dump to disk"""
        return self._data

    @data.setter
    def data(self, new_dict: dict[str, Any]) -> None:
        """Replace the whole dictionary stored in the data attribute"""
        self._data = new_dict

    def clear(self) -> None:
        """Clear all information stored in data and iodata attributes"""
        self._data = {}
        self._iodata = IOData()

    #
    # Overload update function as we did not use the supported overloads.
    # We might change this in the future, but it will affect the whole codebase
    #

    @overload
    def update(
        self, arg: SupportsKeysAndGetItem[Any, Any], /, **kwargs: Any
    ) -> None: ...
    @overload
    def update(
        self, arg: Iterable[tuple[Any, Any]], /, **kwargs: Any
    ) -> None: ...
    @overload
    def update(self, /, **kwargs: Any) -> None: ...
    @overload
    def update(self, key: str, value: Any) -> None: ...

    def update(self, key: str, value: Any) -> None:
        """Update or include a key-value pair in the data dictionary.

        Args:
            key (str): the key of the new item in the dictionary to be stored
            value (Any): the value to be stored or updated in the data dictionary
        """
        self._data.update({key: value})

    def to_file(self, filename: str) -> None:
        """Write checkpoint file to disk in PyBEST's result path defined in filemanage

        Args:
            filename (str): the name of the file to dump checkpoint information

        Raises:
            ArgumentError: raised if file suffix is different from .h5
        """
        fname = filemanager.result_path(filename)
        if fname.suffix == ".h5":
            self._iodata = IOData(**self._data)
            self._iodata.to_file(fname)
        else:
            raise ArgumentError("Checkpoint can only dump to h5 format.")

    def from_file(self, filename: str) -> IOData:
        """Load data from file and store as IOData instance

        Args:
            filename (str): the filename to load

        Raises:
            ArgumentError: raised if file suffix differes from .h5

        Returns:
            IOData: an instance if IOData containing all data as attributes
        """
        if filename.endswith(".h5"):
            return IOData.from_file(filename)
        else:
            raise ArgumentError("Checkpoint can only read from h5 format.")

    def __call__(self) -> IOData:
        """Update iodata attribute with data information stored as IOData instance

        Returns:
            IOData: all output information stored during a calculation
        """
        self._iodata = IOData(**self._data)
        return self._iodata
