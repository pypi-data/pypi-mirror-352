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
"""Definition of all exceptions in PyBEST"""


class PyBestException(Exception):
    """Base class for all the exceptions raised within the PyBest package"""


class ProjectionError(PyBestException):
    """Exception raised when projection of orbitals was unsuccessful"""


class BasisError(PyBestException, ValueError):
    """Exception raised when Basis set was read in unsuccessful"""


class ElectronCountError(PyBestException, ValueError):
    """Exception raised when a negative number of electron is encountered, or
    when more electrons than basis functions are requested
    """


class NoConvergence(PyBestException):
    """Exception raised when an optimization algorithm does not reach the convergence
    threshold in the specified number of iterations
    """


class NoSCFConvergence(PyBestException):
    """Exception raised when an SCF algorithm does not reach the convergence
    threshold in the specified number of iterations
    """


class UnknownHamiltonian(PyBestException, ValueError):
    """Exception raised when the Hamiltonian contains unknown terms"""


class UnknownOption(PyBestException, ValueError):
    """Exception raised when unknown value is provided"""


class EmptyData(PyBestException, ValueError):
    """Exception raised when input data is empty/not provided"""


class NonEmptyData(PyBestException, ValueError):
    """Exception raised when input data is not empty"""


class SymmetryError(PyBestException, ValueError):
    """Exception raised when object does not have proper symmetry"""


class ConsistencyError(PyBestException, ValueError):
    """Exception raised when calculation results in unexpected outcome"""


class ArgumentError(PyBestException):
    """Exception raised when unknown argument is provided"""


class RestartError(PyBestException):
    """Exception raised when restarting from checkpoint fails"""


class MissingFileError(PyBestException, FileNotFoundError):
    """Exception raised when required file is not found"""


class DirectoryError(PyBestException):
    """Exception raised when directory is not found nor created"""


class MatrixShapeError(PyBestException):
    """Exception raised when matrix shape does not allow to make operation."""


class FeasibilityError(PyBestException):
    """Error raised when the problem appears to be infeasible"""


class BoundedError(PyBestException):
    """Error raised when the problem appears to be unbounded"""


class LinalgFactoryError(PyBestException, ValueError):
    """Error raised when we want to access unsupported features of LinalgFactory"""


class FactoryError(PyBestException, ValueError):
    """Error raised when we want to automatically calculate frozen core orbitals using something other than Basis."""
