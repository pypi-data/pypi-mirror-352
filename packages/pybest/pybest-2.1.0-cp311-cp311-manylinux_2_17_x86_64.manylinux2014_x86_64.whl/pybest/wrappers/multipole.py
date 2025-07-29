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
"""Wrapper for multipole calculations"""

from __future__ import annotations

import numpy as np

from pybest.exceptions import ArgumentError
from pybest.linalg import DenseTwoIndex, OneIndex, Orbital, TwoIndex
from pybest.log import log
from pybest.units import debye
from pybest.utility import check_type, unmask, unmask_orb


def compute_dipole_moment(
    *args,
    molecular_orbitals: bool = False,
    name: str | None = None,
    scale: float = 2.0,
):
    """Calculates the dipole moment for any density matrix in AO or MO basis.

    **Arguments:**

    args: arguments containing:
        integrals
             The electric dipole moment integrals. A list of TwoIndex objects
             for each Cartesian coordinate vector. In Libint, also the overlap
             integrals are calculated and returned. Thus, by default PyBEST
             also returns them. The default order of the dipole moment integrals
             is [olp, mux, muy, muz]. The integrals are recognized wrt their
             labels.

        dm_1
             A 1-particle reduced density matrix. For restricted orbitals, dm_1 has to correspond to
             the full density matrix. A TwoIndex object.

    **Keyword Arguments:**

    molecular_orbitals
         (boolean) if True, the dipole moment is transformed into new MO
         basis of orb.

    name
         (str) if provided prints 'name' in the header.

    scale
         (float) a scaling factor for the 1DM. If provided, the 1DM is scaled
         accordingly. Default=2.0 (assuming restricted orbitals)
    """
    if log.do_medium:
        log.hline("=")
        name = "" if name is None else f"for {name}"
        log(f"Calculating dipole moment {name}")

    ints = check_ints(*args)
    origin_coord = check_coord(*args)
    orb = check_orb(*args, molecular_orbitals=molecular_orbitals)
    occ_model = unmask("occ_model", *args)
    if occ_model is None:
        raise ArgumentError("Cannot find basis")
    basis = occ_model.factory

    nbasis = occ_model.nbasis[0]
    ncore = occ_model.ncore[0]

    # density_matrix from IOData, create a copy as we scale the density_matrix afterwards
    density_matrix_unmask = unmask("dm_1", *args) or unmask("dm_1_a", *args)

    if density_matrix_unmask is None:
        raise ArgumentError("Cannot find density matrix")

    # Check arguments
    check_type("dm_1", density_matrix_unmask, OneIndex, TwoIndex, dict)
    dm_1 = None
    # 1-DMs from pCCD-LCCD-type methods are saved in a dictionary
    if isinstance(density_matrix_unmask, dict):
        try:
            # pq index denotes the whole dm_1 (1-RDM)
            dm_1 = density_matrix_unmask["pq"].copy()
            try:
                # In case a pCCD contribution is present, `pq` only contains
                # the (L)CC part and the pCCD part has to be added a posteriori
                dm_1_pp = density_matrix_unmask["pccd_pp"].copy()
                dm_1.iadd_diagonal(dm_1_pp)
                if log.do_medium:
                    log("Adding pCCD part to 1-RDM")
            except KeyError:
                pass
        except KeyError as error_key:
            raise ArgumentError(
                "Cannot find density matrix in dictionary"
            ) from error_key
    else:
        dm_1 = density_matrix_unmask.copy()

    if log.do_medium:
        log("All post-HF density matrices are saved in MO basis")

    if isinstance(dm_1, OneIndex):
        dm_1 = unfolding_dm(dm_1, nbasis, ncore)

    if molecular_orbitals:
        dm_1 = transform_dm(dm_1, nbasis, ncore, orb)
    # The density matrix (in AO/MO both basis) is scaled by a factor of 2.0, assuming restricted spatial orbitals.
    dm_1.iscale(scale)

    # DM is given in AO basis: do nothing
    # Calculating total dipole moment
    el_dm = np.array(
        [
            -ints["mu_x"].contract("ab,ab", dm_1),
            -ints["mu_y"].contract("ab,ab", dm_1),
            -ints["mu_z"].contract("ab,ab", dm_1),
        ]
    )
    # (coordinates * atomic_number) and summed by columns
    nuc_dm = (
        (np.array([basis.coordinates]) - np.array([origin_coord]))
        * np.array([basis.atom]).T
    ).sum(axis=1)[0]

    # Print output
    if log.do_medium:
        log.hline("~")
        log(f"{'Component':>10s} {'a.u.':>14s} {'Debye':>14s}")
        log.hline("-")

        log(f"{'Nuclear part':>6s}")
        for pos, pos_name in zip(
            nuc_dm,
            ["dm_x", "dm_y", "dm_z"],
        ):
            log(f"{pos_name !s:>6s} {pos:>19.7f} {(pos / debye):>15.7f}")

        log(f"{'Electronic part':>6s}")
        for pos, pos_name in zip(
            el_dm,
            ["dm_x", "dm_y", "dm_z"],
        ):
            log(f"{pos_name !s:>6s} {pos:>19.7f} {(pos / debye):>15.7f}")
        log(f"{'Total dipole moment':>6s}")
        for pos, pos_name in zip(
            el_dm + nuc_dm,
            ["dm_x", "dm_y", "dm_z"],
        ):
            log(f"{pos_name !s:>6s} {pos:>19.7f} {(pos / debye):>15.7f}")

        log.hline("=")

    # Return in Debye
    return el_dm[0] / debye, el_dm[1] / debye, el_dm[2] / debye


def unfolding_dm(dm_1: OneIndex, nbasis: int, ncore: int) -> TwoIndex:
    """Unfolding DM from OneIndex to TwoIndex object"""
    # first copy into a temporary object
    log("Unfolding DM from OneIndex to TwoIndex object")
    dm_1_tmp = dm_1.copy()
    # then overwrite with properly sized object
    dm_1_u = DenseTwoIndex(nbasis - ncore)
    # assign final object
    dm_1_u.assign_diagonal(dm_1_tmp)
    return dm_1_u


def transform_dm(
    dm_1: TwoIndex, nbasis: int, ncore: int, orb: list
) -> TwoIndex:
    """Transform dm_1 to AO basis"""
    # check if 1DM has the proper shape; otherwise, add frozen core part
    if dm_1.shape != (nbasis, nbasis):
        dm_1_tmp = DenseTwoIndex(nbasis)
        # Frozen core orbitals assigned value 1.0 in the DM.
        dm_1_tmp.assign_diagonal(1.0, end=ncore)
        dm_1_tmp.assign(dm_1, begin0=ncore, begin1=ncore)
        dm_1 = dm_1_tmp
    orb = orb[0].copy()
    orb.itranspose()
    log("Transforming DM from MO to AO")
    dm_1_tmp = DenseTwoIndex(nbasis)
    dm_1_tmp.assign_two_index_transform(dm_1, orb)
    dm_1 = dm_1_tmp
    return dm_1


def check_ints(*args) -> dict:
    """Checking dipole ints"""
    # dipole ints
    ints = {}
    mus = ["mu_x", "mu_y", "mu_z"]
    for arg in args:
        if isinstance(arg, TwoIndex):
            if arg.label in mus:
                ints[arg.label] = arg
        # overwrite with list
        if isinstance(arg, (list, tuple)):
            for arg_ in arg:
                if isinstance(arg_, TwoIndex):
                    if arg_.label in mus:
                        ints[arg_.label] = arg_
    # Check if all are found:
    if not all(mus_ in ints for mus_ in mus):
        raise ArgumentError(
            "Cannot find all components of the dipole moment integrals!"
        )
    return ints


def check_coord(*args) -> list | None:
    """Checking the origin coordinates"""
    origin_coord = None
    for arg in args:
        # Checking for origin coordinates
        if isinstance(arg, dict):
            if "origin_coord" in arg:
                origin_coord = arg["origin_coord"]
                if origin_coord is None or len(origin_coord) != 3:
                    raise ArgumentError("Cannot find all origin coordinates!")
                return origin_coord
        if isinstance(arg, (list, tuple)):
            for arg_ in arg:
                # Checking for origin coordinates
                if isinstance(arg_, dict):
                    if "origin_coord" in arg_:
                        origin_coord = arg_["origin_coord"]
                        if origin_coord is None or len(origin_coord) != 3:
                            raise ArgumentError(
                                "Cannot find all origin coordinates!"
                            )
                        return origin_coord
    # check if origin_coord are found (x,y,z)
    if origin_coord is None:
        raise ArgumentError("Cannot find all origin coordinates!")

    return None


def check_orb(*args, molecular_orbitals: bool = False) -> tuple[Orbital, ...]:
    """Checking orbital"""
    # orb
    orb = unmask_orb(*args)
    if molecular_orbitals and not orb:
        raise ArgumentError(
            f"Cannot find orbitals in function arguments {args!s}."
        )
    return orb
