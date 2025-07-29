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
"""Gaussian basis sets"""

import h5py

# cpp defined object
from pybest.core import Basis, ExternalCharges, StaticEmbedding
from pybest.core import basis as m_basis

# NOTE: this import order is necessary for monkeypatching to work


# NOTE: this is dumper to hdf5, behaves like an ordinary method
def __pybasis_to_hdf5(self, group: h5py.Group) -> None:
    """Method implementing Basis.to_hdf5 dumper

    Args:
        group (h5py.Group): group in which Basis object information will be dumped
    """
    # string attributes
    group.attrs["basisname"] = self.basisname
    group.attrs["molfile"] = self.molfile
    group.attrs["basisdir"] = self.basisdir

    # integer attributes
    group["nbasis"] = self.nbasis
    group["nshell"] = self.nshell
    group["ncenter"] = self.ncenter

    # arrays
    group["nprim"] = self.nprim
    group["alpha"] = self.alpha
    group["contraction"] = self.contraction
    group["shell2atom"] = self.shell2atom
    group["shell_types"] = self.shell_types
    group["atom"] = self.atom
    group["coordinates"] = self.coordinates


# NOTE: this is from hdf5 constructor, behaves like a static method
def __pybasis_from_hdf5(group: h5py.Group) -> Basis:
    """Method used as a class method, in monkeypatched core.Basis (nanobind export)
    return an instance of core.Basis object from hdf5 dump.

    Args:
        group (h5py.Group): group in which Basis object information is stored

    Returns:
        Basis: core.Basis object (nanobind export)
    """
    # nanobind autoconverts std::vector to list, so we must cast all np.ndarray instances
    atomic_numbers = list(group["atom"])
    # cast 2D ndarray to list of lists
    coordinates = [list(coord) for coord in group["coordinates"][:]]
    primitives = list(group["nprim"][:])
    shell2atom = list(group["shell2atom"][:])
    shell_types = list(group["shell_types"][:])
    alphas = list(group["alpha"][:])
    contractions = list(group["contraction"][:])
    return m_basis.from_coordinates(
        atomic_numbers,
        coordinates,
        primitives,
        shell2atom,
        shell_types,
        alphas,
        contractions,
    )


# monkey patch the class Basis with python defined methods
Basis.from_hdf5 = __pybasis_from_hdf5  # type: ignore
Basis.to_hdf5 = __pybasis_to_hdf5  # type: ignore


# define test runner
from pybest._pytesttester import PytestTester
from pybest.gbasis.cholesky_eri import compute_cholesky_eri
from pybest.gbasis.dense_ints import (
    compute_dipole,
    compute_eri,
    compute_kinetic,
    compute_nuclear,
    compute_nuclear_pc,
    compute_nuclear_repulsion,
    compute_overlap,
    compute_point_charges,
    compute_ppcp,
    compute_pvp,
    compute_quadrupole,
    compute_static_embedding,
    get_charges,
    get_embedding,
)

# NOTE: basis imports must be after Basis class has been monkeypatched
from pybest.gbasis.gobasis import get_gobasis
from pybest.gbasis.gobasis_helper import shell_int2str, shell_str2int

__all__ = [
    "Basis",
    "ExternalCharges",
    "StaticEmbedding",
    "compute_cholesky_eri",
    "compute_dipole",
    "compute_eri",
    "compute_kinetic",
    "compute_nuclear",
    "compute_nuclear_pc",
    "compute_nuclear_repulsion",
    "compute_overlap",
    "compute_point_charges",
    "compute_ppcp",
    "compute_pvp",
    "compute_quadrupole",
    "compute_static_embedding",
    "get_charges",
    "get_embedding",
    "get_gobasis",
    "shell_int2str",
    "shell_str2int",
]

test = PytestTester(__name__)
del PytestTester
