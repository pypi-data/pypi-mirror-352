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
"""Dense one- and two-body integrals."""

from __future__ import annotations

from typing import Any

from pybest.core import basis as module_basis
from pybest.core import ints
from pybest.io.embedding import load_embedding
from pybest.io.external_charges import load_charges

# To prevent circular imports, we can either import Dense or Cholesky objects
# This can be fixed by passing an lf instance, which requires a rewrite
from pybest.linalg import DenseFourIndex, DenseTwoIndex
from pybest.log import log, timer

# nanobind classes
from . import Basis, ExternalCharges, StaticEmbedding

__all__ = [
    "compute_dipole",
    "compute_eri",
    "compute_kinetic",
    "compute_nuclear",
    "compute_nuclear_repulsion",
    "compute_overlap",
    "compute_pvp",
    "compute_quadrupole",
]


PYBEST_PVP_ENABLED = hasattr(ints, "compute_pvp_cpp")

#
# Get external point charges
#


@timer.with_section("Ints: ReadPointChar")
def get_charges(filename: str) -> ExternalCharges:
    """Get point charges from some .pc file.
    The structure of the .pc file is assumed to be similar to the .xyz file.
    Specifically:
        - the first line is the number of point charges in the file [int]
        - the second line is reserved for comments [str]
        - the following lines (each line for point charge) are composed of
        four columns:
            - first three columns are the xyz coordinates in Angstroms [float]
            - the 4-th column is the charge in a.u. [float]

    **Arguments:**

    filename
        filename containing the point charges (IOData instance : str)

    """
    # Get external charges from a .pc file
    data = load_charges(filename)
    charges = data["charges"]
    coords = data["coordinates"]
    x, y, z = coords[:, 0], coords[:, 1], coords[:, 2]
    return ExternalCharges(charges, x, y, z)


#
# Get static embedding potential
#


@timer.with_section("Ints: ReadEmbPot")
def get_embedding(filename: str) -> StaticEmbedding:
    """Get embedding potential from *.emb file.
    The structure of the .emb file is assumed to be similar to the .xyz file.
    Specifically:
        - the first line is the number of points in the file [int]
        - the second line is reserved for comments [str]
        - the following lines (each line for point charge) are composed of
        five columns:
            * the 1-st column contains charges [float]
            * the 2-nd, 3-rd, and 4-th columns include the xyz coordinates
            in Angstroms [float]
            * the 5-th column contains the wights [float]

    **Arguments:**

    filename
        filename containing the embedding potential (IOData instance : str)
    """
    log.cite(
        "the static embedding potential",
        "gomes2008embedding",
        "chakraborty2023",
    )

    # Get embedding potential from .emb file
    data = load_embedding(filename)
    charges = data["charges"]
    coords = data["coordinates"]
    weights = data["weights"]
    x_coord, y_coord, z_coord = coords[:, 0], coords[:, 1], coords[:, 2]
    return StaticEmbedding(charges, x_coord, y_coord, z_coord, weights)


#
# External potentials
#


@timer.with_section("Ints: NucNuc")
def compute_nuclear_repulsion(basis0: Basis, basis1: Basis | None = None):
    """Compute the nuclear repulsion energy

    **Arguments:**

    basis0, basis1
         A Basis instance

    **Returns:** A number (float)
    """
    if basis1 is None:
        basis1 = basis0
    return ints.compute_nuclear_repulsion_cpp(basis0, basis1)


@timer.with_section("Ints: ChargesNuc")
def compute_nuclear_pc(basis0: Basis, charges: ExternalCharges):
    """Compute the interaction of external charges with nuclear potential

    **Arguments:**

    basis0
         A Basis instance

    charges
         An ExternalCharges instance

    **Returns:** A number (float)
    """
    return ints.compute_nuclear_pc_cpp(basis0, charges)


#
# 1- and 2-body integrals
#


@timer.with_section("Ints: Olp")
def compute_overlap(
    basis0: Basis, basis1: Basis | None = None, uncontract: bool = False
):
    """Compute the overlap integrals in a Gaussian orbital basis

    **Arguments:**

    basis0, basis1
         A Basis instance

    **Returns:** ``TwoIndex`` object
    """
    if basis1 is None:
        basis1 = basis0
    nbasis0 = basis0.nbasis
    nbasis1 = basis1.nbasis
    if uncontract:
        nbasis0 = module_basis.get_nubf(basis0, True)
        nbasis1 = module_basis.get_nubf(basis1, True)
    out = DenseTwoIndex(nbasis0, nbasis1, "olp")
    # call the low-level routine
    ints.compute_overlap_cpp(basis0, basis1, out.array, uncontract)
    # done
    return out


@timer.with_section("Ints: Kin")
def compute_kinetic(
    basis0: Basis, basis1: Basis | None = None, uncontract: bool = False
):
    """Compute the kinetic energy integrals in a Gaussian orbital basis

    **Arguments:**

    basis0, basis1
         A Basis instance

    **Returns:** ``TwoIndex`` object
    """
    if basis1 is None:
        basis1 = basis0
    nbasis0 = basis0.nbasis
    nbasis1 = basis1.nbasis
    if uncontract:
        nbasis0 = module_basis.get_nubf(basis0, True)
        nbasis1 = module_basis.get_nubf(basis1, True)
    out = DenseTwoIndex(nbasis0, nbasis1, "kin")
    # call the low-level routine
    ints.compute_kinetic_cpp(basis0, basis1, out.array, uncontract)
    # done
    return out


@timer.with_section("Ints: Nuc")
def compute_nuclear(
    basis0: Basis, basis1: Basis | None = None, uncontract: bool = False
):
    """Compute the nuclear integrals in a Gaussian orbital basis

    **Arguments:**

    basis0, basis1
         A Basis instance

    **Returns:** ``TwoIndex`` object
    """
    if basis1 is None:
        basis1 = basis0
    nbasis0 = basis0.nbasis
    nbasis1 = basis1.nbasis
    if uncontract:
        nbasis0 = module_basis.get_nubf(basis0, True)
        nbasis1 = module_basis.get_nubf(basis1, True)
    out = DenseTwoIndex(nbasis0, nbasis1, "ne")
    # call the low-level routine
    ints.compute_nuclear_cpp(basis0, basis1, out.array, uncontract)
    # done
    return out


@timer.with_section("Ints: PointCharges")
def compute_point_charges(
    basis0: Basis,
    charges: Any,
    basis1: Basis | None = None,
    uncontract: bool = False,
):
    """Compute the interaction of point charges with electrons

    **Arguments:**

    basis0, basis1
         A Basis instance

    charges
        An External Charges instance

    uncontract
        Uncontracted basis is needed for DKH

    **Returns:** ``TwoIndex`` object
    """
    if basis1 is None:
        basis1 = basis0
    nbasis0 = basis0.nbasis
    nbasis1 = basis1.nbasis
    if uncontract:
        nbasis0 = module_basis.get_nubf(basis0, True)
        nbasis1 = module_basis.get_nubf(basis1, True)
    out = DenseTwoIndex(nbasis0, nbasis1, "pc")
    # call the low-level routine
    ints.compute_point_charges_cpp(
        basis0, basis1, charges, out.array, uncontract
    )
    # done
    return out


@timer.with_section("Ints: StaticEmbed")
def compute_static_embedding(
    basis0: Basis,
    embedding: Any,
    basis1: Basis | None = None,
    uncontract: bool = False,
):
    """Compute the static embedding

    **Arguments:**

    basis0, basis1
         A Basis instance

    embedding
         An StaticEmbedding instance

    uncontract
        Uncontracted basis is needed for DKH

    **Returns:** ``TwoIndex`` object
    """
    if basis1 is None:
        basis1 = basis0
    nbasis0 = basis0.nbasis
    nbasis1 = basis1.nbasis
    if uncontract:
        nbasis0 = module_basis.get_nubf(basis0, True)
        nbasis1 = module_basis.get_nubf(basis1, True)
    out = DenseTwoIndex(nbasis0, nbasis1, "emb")
    # call the low-level routine
    embedding.compute_static_embedding_cpp(basis0, basis1, out.array)
    # done
    return out


@timer.with_section("Ints: Dipole")
def compute_dipole(
    basis0: Basis,
    basis1: Basis | None = None,
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
):
    """Compute the dipole integrals in a Gaussian orbital basis

    **Arguments:**

    basis0, basis1
         A Basis instance

    **Returns:** ``TwoIndex`` object
    """
    if basis1 is None:
        basis1 = basis0
    nbasis0 = basis0.nbasis
    nbasis1 = basis1.nbasis
    olp = DenseTwoIndex(nbasis0, nbasis1, label="olp")
    mu_x = DenseTwoIndex(nbasis0, nbasis1, label="mu_x")
    mu_y = DenseTwoIndex(nbasis0, nbasis1, label="mu_y")
    mu_z = DenseTwoIndex(nbasis0, nbasis1, label="mu_z")
    # call the low-level routine
    ints.compute_dipole_cpp(
        basis0, basis1, olp.array, mu_x.array, mu_y.array, mu_z.array, x, y, z
    )

    # done
    return olp, mu_x, mu_y, mu_z, {"origin_coord": [x, y, z]}


@timer.with_section("Ints: Quadrupole")
def compute_quadrupole(
    basis0: Basis,
    basis1: Basis | None = None,
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
):
    """Compute the quadrupole integrals in a Gaussian orbital basis

    **Arguments:**

    basis0, basis1
         A Basis instance

    **Returns:** ``TwoIndex`` object
    """
    if basis1 is None:
        basis1 = basis0
    nbasis0 = basis0.nbasis
    nbasis1 = basis1.nbasis

    olp = DenseTwoIndex(nbasis0, nbasis1, label="olp")
    mu_x = DenseTwoIndex(nbasis0, nbasis1, label="mu_x")
    mu_y = DenseTwoIndex(nbasis0, nbasis1, label="mu_y")
    mu_z = DenseTwoIndex(nbasis0, nbasis1, label="mu_z")
    mu_xx = DenseTwoIndex(nbasis0, nbasis1, label="mu_xx")
    mu_xy = DenseTwoIndex(nbasis0, nbasis1, label="mu_xy")
    mu_xz = DenseTwoIndex(nbasis0, nbasis1, label="mu_xz")
    mu_yy = DenseTwoIndex(nbasis0, nbasis1, label="mu_yy")
    mu_yz = DenseTwoIndex(nbasis0, nbasis1, label="mu_yz")
    mu_zz = DenseTwoIndex(nbasis0, nbasis1, label="mu_zz")
    # call the low-level routine
    ints.compute_quadrupole_cpp(
        basis0,
        basis1,
        olp.array,
        mu_x.array,
        mu_y.array,
        mu_z.array,
        mu_xx.array,
        mu_xy.array,
        mu_xz.array,
        mu_yy.array,
        mu_yz.array,
        mu_zz.array,
        x,
        y,
        z,
    )
    # done
    return (
        olp,
        mu_x,
        mu_y,
        mu_z,
        mu_xx,
        mu_xy,
        mu_xz,
        mu_yy,
        mu_yz,
        mu_zz,
    )


@timer.with_section("Ints: PVP")
def compute_pvp(
    basis0: Basis, basis1: Basis | None = None, uncontract: bool = True
):
    """Compute the pvp integrals in a Gaussian orbital basis

    **Arguments:**

    basis0, basis1
         A Basis instance

    **Returns:** ``TwoIndex`` object
    """
    if basis1 is None:
        basis1 = basis0
    nbasis0 = basis0.nbasis
    nbasis1 = basis1.nbasis
    if uncontract:
        nbasis0 = module_basis.get_nubf(basis0, True)
        nbasis1 = module_basis.get_nubf(basis1, True)
    out = DenseTwoIndex(nbasis0, nbasis1, "pvp")
    # call the low-level routine
    ints.compute_pvp_cpp(basis0, basis1, out.array, uncontract)
    # done
    return out


@timer.with_section("Ints: PPCP")
def compute_ppcp(
    basis0: Basis,
    charges: Any,
    basis1: Basis | None = None,
    uncontract: bool = True,
):
    """Compute the pPCp integrals to correct for picture changes
    when using, for instance, the DKH Hamiltonian.

    **Arguments:**

    basis0, basis1
         A Basis instance

    **Returns:** ``TwoIndex`` object
    """
    if basis1 is None:
        basis1 = basis0
    nbasis0 = basis0.nbasis
    nbasis1 = basis1.nbasis
    if uncontract:
        nbasis0 = module_basis.get_nubf(basis0, True)
        nbasis1 = module_basis.get_nubf(basis1, True)
    out = DenseTwoIndex(nbasis0, nbasis1, "ppcp")
    # call the low-level routine
    ints.compute_ppcp_cpp(basis0, basis1, charges, out.array, uncontract)
    # done
    return out


@timer.with_section("Ints: ERI")
def compute_eri(
    basis0: Basis,
    basis1: Basis | None = None,
    basis2: Basis | None = None,
    basis3: Basis | None = None,
    symmetry: bool = True,
):
    """Compute the electron repulsion integrals in a Gaussian orbital basis

    **Arguments:**

    basis0, basis1
         A Basis instance

    **Returns:** ``FourIndex`` object
    """
    if basis1 is None:
        basis1 = basis0
    if basis2 is None:
        basis2 = basis0
    if basis3 is None:
        basis3 = basis0
    nbasis0 = basis0.nbasis
    nbasis1 = basis1.nbasis
    nbasis2 = basis2.nbasis
    nbasis3 = basis3.nbasis
    if symmetry:
        log("Computing only symmetry-unique elements of ERI.")
    else:
        log("Computing all elements of ERI.")
    out = DenseFourIndex(nbasis0, nbasis1, nbasis2, nbasis3, "eri")
    # call the low-level routine
    ints.compute_eri_cpp(basis0, basis1, basis2, basis3, out.array, symmetry)
    # done
    return out
