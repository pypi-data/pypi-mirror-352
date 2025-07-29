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
# This implementation has been taken from `Horton 2.0.0`.
# However, this file has been updated and debugged. Compatibility with Horton is NOT
# guaranteed.
# Its current version contains updates from the PyBEST developer team.
#
# Detailed changes:
# 2020-07-01: use pathlib.Path instead of filename
# 2020-07-01: special routine to dump/load PyBEST basis set instance
# 2020-07-01: use utf8 encoding
# 2025-03: Docstrings and type hints (Kacper Cieslak)

"""PyBEST internal file format"""

from __future__ import annotations

import pathlib
from typing import Any

import h5py as h5
import numpy as np

from pybest.exceptions import UnknownOption

from .lockedh5 import LockedH5File

__all__ = ["dump_h5", "load_h5"]


def load_h5(item: pathlib.Path | h5.Dataset | h5.Group) -> Any:
    """Load a (PyBEST) object from an h5py File/Group

    Args:
        item (pathlib.Path | h5.Dataset | h5.Group): Containing the Pybest object.

    Returns: FIXME

    Raises:
        UnknownOption: Doesn't know how to handle loading of the item.
    """
    if isinstance(item, pathlib.Path):
        with LockedH5File(item, "r") as f:
            return load_h5(f)

    elif isinstance(item, h5.Dataset):
        if len(item.shape) > 0:
            # convert to a numpy array
            return np.array(item)

        # convert to a scalar
        return item[()]
    elif isinstance(item, h5.Group):
        class_name = item.attrs.get("class")
        if class_name is None:
            # assuming that an entire dictionary must be read.
            result = {}
            for key, subitem in item.items():
                result[key] = load_h5(subitem)
            return result

        # special constructor. the class is found with the imp module
        cls = __import__("pybest", fromlist=[class_name]).__dict__[class_name]
        return cls.from_hdf5(item)

    raise UnknownOption(f"Doesn't know how to handle loading of item {item}")


def dump_h5(grp: h5.Group | pathlib.Path, data: Any) -> None:
    """Dump a (PyBEST) object to a HDF5 file.

    Args:
        grp: A HDF5 group or a filename of a new HDF5 file.
        data: The object to be written. This can be a dictionary of objects or
         an instance of a PyBEST class that has a ``to_hdf5`` method. The
         dictionary my contain numpy arrays
    """
    if isinstance(grp, pathlib.Path):
        with LockedH5File(grp, "w") as f:
            dump_h5(f, data)

    elif isinstance(data, dict):
        for key, value in data.items():
            # Simply overwrite old data
            if key in grp:
                del grp[key]
            if isinstance(value, (int, float, str)):
                grp[key] = value

            # handle numpy arrays
            elif isinstance(value, np.ndarray):
                # encode other types first
                if value.dtype != float and value.dtype != int:
                    grp[key] = [a.encode("utf8") for a in value]
                else:
                    grp[key] = value

            # Some class instance
            else:
                sub_grp = grp.require_group(key)
                dump_h5(sub_grp, value)
    else:
        # clear the group if anything was present
        for key in grp.keys():
            del grp[key]
        for key in grp.attrs.keys():
            del grp.attrs[key]

        # call dumping method
        data.to_hdf5(grp)

        # The following is needed to create object of the right type when
        # reading from the checkpoint:
        grp.attrs["class"] = data.__class__.__name__
