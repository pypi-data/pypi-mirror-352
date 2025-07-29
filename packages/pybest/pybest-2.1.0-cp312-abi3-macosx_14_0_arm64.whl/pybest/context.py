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
# Detailed changes (see also CHANGELOG):
# 2020-07-01: update to new python features, including f-string, pathlib
# 2020-07-01: update to PyBEST standards, including exception class
# 2020-07-01: major clean up, got rid of reduntant operations and file paths

"""The context in which PyBEST is used

This module controls global parameters that are purely technical, e.g. the
location of data files. It is certainly not meant to keep track of input
parameters for a computation.

This module contains a context object, an instance of the :class:`Context`
class. For now, its functionality is rather limited. It tries to figure
out the location of the data directory. If it is not specified in the
environment variable ``PyBESTDATA``, it is assumed that the data is located
in a directory called ``data``. If the data directory does not exist, an
error is raised.
"""

import os
from pathlib import Path

from pybest.exceptions import DirectoryError

__all__ = ["context"]


class Context:
    """Finds out where the data directory is located etc.

    The data directory contains data files with standard basis sets and
    pseudo potentials.
    """

    def __init__(self):
        # Determine data directory (environment variable > pybest/data)
        self.data_dir = os.getenv("PyBESTDATA")
        if self.data_dir is None:
            pybest_src = Path(__file__).resolve().parent
            self.data_dir = pybest_src.joinpath("data/").resolve()
        if not self.data_dir.is_dir():
            raise DirectoryError(
                f"Can not find the data files. The directory {self.data_dir}"
                " does not exist."
            )

    def get_fn(self, filename):
        """Return the full path to the given filename in the data directory."""
        return str(self.data_dir.joinpath(filename))

    def glob(self, pattern, sub_dir=""):
        """Return all files in the data (sub)directory that match the given pattern."""
        return sorted(self.data_dir.joinpath(sub_dir).glob(pattern))

    def check_fn(self, filename):
        """Check whether given filename exists in the data directory."""
        return self.data_dir.joinpath(filename).exists()


context = Context()
