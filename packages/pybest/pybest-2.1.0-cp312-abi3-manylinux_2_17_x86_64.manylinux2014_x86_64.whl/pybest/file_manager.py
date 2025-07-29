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
"""Dumping files to disk

The dumping manager decides to which directories PyBEST results are written.
We can choose between two directories

 :result_dir: Contains all final results of a PyBEST calculation, for instance,
              checkpoint files, dat files, etc. These directory contains all
              checkpoint files that can be used for restarts.
 :temp_dir:   Contains all intermediate files generated during code execution, for
              instance, Hamiltonian integrals, eigenvectors, etc.
              It does not contain restartable data, that is, checkpoint files.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from pybest.exceptions import ArgumentError, DirectoryError

__all__ = ["FileManager"]


# NOTE: re-do this as a decorator
def handle_dir_args(new_dir: str | Path) -> Path:
    """Helper function that does some common logic for checking `new_dir`

    Args:
        new_dir (str | Path): new dir candidate

    Raises:
        ArgumentError: if `new_dir` cannot be interpreted as a pathlib.Path()

    Returns:
        Path: new_dir normalized to pathlib.Path
    """
    if not isinstance(new_dir, str) and not isinstance(new_dir, Path):
        raise ArgumentError(f"Do not know how to handle argument {new_dir}")

    if isinstance(new_dir, str) and not new_dir:
        raise ArgumentError("Directory name cannot be empty.")

    return Path(f"{new_dir}/") if isinstance(new_dir, str) else new_dir


# NOTE: prefix can be used in compute job, as a way to customize target directory by a user
class FileManager:
    """The output directory manager.
    Keeps track and manages lifetime of :
    * temporary directory, where temporary results i.e. checkpoints are written to
    * results dir, where the requested results are written
    """

    def __init__(
        self,
        result_dir: str | Path,
        temp_dir: str | Path,
        prefix: str | Path | None = None,
    ):
        self.prefix = Path(prefix) if prefix else None
        self._temp_list: list = []  # list of tmpdirs for later delete
        self.result_dir: Path = result_dir
        self.temp_dir: Path = temp_dir
        self.keep_temp: bool = False

    @property
    def result_dir(self) -> Path:
        """Result dir property getter."""
        return self._result_dir

    @result_dir.setter
    def result_dir(self, new_dir: str | Path) -> None:
        """Result dir property setter, creates directory if not existing.
        Normalizes `new_dir` to pathlib.Path if necessary.
        """
        self._result_dir = handle_dir_args(new_dir=new_dir)
        if self.prefix:
            self._result_dir = self.prefix / self._result_dir
        self.create_dir(self._result_dir)

    @property
    def temp_dir(self) -> Path:
        """Temporary dir property getter."""
        return self._temp_dir

    @temp_dir.setter
    def temp_dir(self, new_dir: str | Path) -> None:
        """Temporary dir property setter, creates directory if not existing.
        Normalizes `new_dir` to pathlib.Path if necessary.
        """
        self._temp_dir = handle_dir_args(new_dir=new_dir)
        if self.prefix:
            self._temp_dir = self.prefix / self._temp_dir
        self.create_dir(self._temp_dir)
        # register new temporary directory (will be cleaned at exit)
        self._temp_list.append(self._temp_dir)

    @property
    def keep_temp(self) -> bool:
        """keep_temp property"""
        return self._keep_temp

    @keep_temp.setter
    def keep_temp(self, new: bool) -> None:
        """keep_temp property setter with type validation"""
        if not isinstance(new, bool):
            raise TypeError("keep_temp can only be boolean type")
        self._keep_temp = new

    @staticmethod
    def create_dir(pathlib_dir: Path) -> None:
        """Creates dir, and skips if the directory already exists

        Args:
            pathlib_dir (Path): path for the temporary directory

        Raises:
            DirectoryError: raised if cannot create directory
        """
        pathlib_dir.mkdir(parents=True, exist_ok=True)
        if not pathlib_dir.exists() and not pathlib_dir.is_dir():
            raise DirectoryError(f"Cannot create directory {pathlib_dir!s}!")

    def result_path(self, file_name: str) -> Path:
        """Concatenates `file_name` within the result directory

        Args:
            file_name (str): user requested filename

        Returns:
            Path: Path object pointing to user provided filename
        """
        # be sure that result_dir exists:
        self.create_dir(self.result_dir)
        return self.result_dir.joinpath(file_name)

    def temp_path(self, file_name: str) -> Path:
        """Concatenates `file_name` within the temporary directory

        Args:
            file_name (str): user requested filename

        Returns:
            Path: Path object pointing to user provided filename
        """
        # be sure that temp_dir exists:
        self.create_dir(self.temp_dir)
        return self.temp_dir.joinpath(file_name)

    def clean_up_temporary_directory(self):
        """Cleans up the temporary dir"""
        # FIXME: this is not thread-safe
        # if we don't keep tmpdir delete it
        if not self.keep_temp:
            for temp_dir in self._temp_list:
                if temp_dir.exists():
                    try:
                        shutil.rmtree(temp_dir)
                    except FileNotFoundError:
                        if not temp_dir.exists():
                            print(f"Directory {temp_dir=} already deleted!")
                        else:
                            print(f"Failed to delete {temp_dir.absolute()}!")
