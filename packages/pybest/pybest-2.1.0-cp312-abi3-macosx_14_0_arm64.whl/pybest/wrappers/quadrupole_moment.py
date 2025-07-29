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
"""Wrapper for quadrupole calculations"""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

from pybest.exceptions import ArgumentError
from pybest.linalg import DenseTwoIndex, OneIndex, TwoIndex
from pybest.log import log
from pybest.units import buckingham
from pybest.utility import check_type, unmask, unmask_orb


def compute_quadrupole_moment(
    *args,
    molecular_orbitals: bool = False,
    name: str | None = None,
    scale_1dm: float = 2.0,
):
    """Calculates the quadrupole moment for any density matrix in AO or MO basis.
       Currently, we only support if the quadrupole integrals are determined
       with respect to the origin of the coordinate frame (0, 0, 0).


    **Arguments:**

    args: arguments containing:
        integrals
             The electric and nuclear quadrupole moment integrals. A list of TwoIndex objects
             for each Cartesian coordinate vector. In Libint, also the overlap
             integrals are calculated and returned. Thus, by default PyBEST
             also returns them. The default order of the quadrupole moment integrals
             is [olp, mu_x, mu_y, mu_z, mu_xx, mu_xy, mu_xz, mu_yy, mu_yz, mu_zz].
             The integrals are recognized wrt their labels.

        dm_1
             A 1-particle reduced density matrix. For restricted orbitals, dm_1 has to correspond to
             the full density matrix. A TwoIndex object.

        orb_a
             The molecular orbitals. Only required if molecular_orbitals=True

    **Keyword Arguments:**

    molecular_orbitals
         (boolean) if True, the quadrupole moment is transformed into new molecular_orbitals
         basis of orb.

    name
         (str) if provided prints 'name' in the header.

    scale_1dm
         (float) a scaling factor for the 1DM. If provided, the 1DM is scaled
         accordingly. Default=2.0 (assuming restricted orbitals)
    """
    if log.do_medium:
        log.hline("=")
        name = "" if name is None else f"for {name}"
        log(f"Calculating quadrupole moment {name}")
    # Check arguments
    occ_model = unmask("occ_model", *args)
    if occ_model is None:
        raise ArgumentError("Cannot find basis")
    basis = occ_model.factory

    nbasis = occ_model.nbasis[0]
    ncore = occ_model.ncore[0]
    ints = check_ints(*args)
    orb = check_orb(*args, molecular_orbitals=molecular_orbitals)
    # dm_1 from IOData, create a copy as we scale the dm_1 afterwards
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
        log(" All post-HF density matrices are saved in MO basis")

    density_matrix_unmask = dm_1

    if isinstance(dm_1, OneIndex):
        log("Unfolding DM from OneIndex to TwoIndex object")
        # first copy into a temporary object
        dm_1_tmp = dm_1.copy()
        # then overwrite with properly sized object
        dm_1 = DenseTwoIndex(nbasis - ncore)
        # assign final object
        dm_1.assign_diagonal(dm_1_tmp)

    if molecular_orbitals:
        # check if 1DM has the proper shape; otherwise, add frozen core part
        if dm_1.shape != (nbasis, nbasis):
            dm_1_tmp = DenseTwoIndex(nbasis)
            # Frozen core orbitals assigned value 1.0 in the DM
            dm_1_tmp.assign_diagonal(1.0, end=ncore)
            dm_1_tmp.assign(dm_1, begin0=ncore, begin1=ncore)
            dm_1 = dm_1_tmp
        orb = orb[0].copy()
        orb.itranspose()
        # Transform dm_1 to AO basis
        log("Transforming DM from MO to AO")
        dm_1_tmp = dm_1.new()
        dm_1_tmp.assign_two_index_transform(dm_1, orb)
        dm_1 = dm_1_tmp
    # The density matrix (in AO/MO both basis) is scaled by a factor of 2.0, assuming restricted spatial orbitals.
    dm_1.iscale(scale_1dm)

    # Calculating nuclear part (nuc <=> nuclear)
    nuc_part = nuc_part_qm(basis)

    # Calculating electronic part (el <=> eletronic)
    el_part = el_part_qm(ints=ints, dm_1=dm_1)
    # Total quadrupole moment is just sum of nuclear and eletronic

    # Print output
    if log.do_medium:
        log.hline("~")
        log(f"{'Component':>10s} {'a.u.':>13s} {'Buckingham':>17s}")
        log.hline("-")

        log(f"{'Nuclear part':>6s}")
        for pos, pos_name in zip(
            nuc_part,
            ["qm_xx", "qm_yy", "qm_zz", "qm_xy", "qm_xz", "qm_yz", "qm_rr"],
        ):
            log(f"{pos_name!s:>6s} {pos:>19.7f} {(pos / buckingham):>15.7f}")

        log(f"{'Electronic part':>6s}")
        for pos, pos_name in zip(
            el_part,
            ["qm_xx", "qm_yy", "qm_zz", "qm_xy", "qm_xz", "qm_yz", "qm_rr"],
        ):
            log(f"{pos_name!s:>6s} {pos:>19.7f} {(pos / buckingham):>15.7f}")

        log(f"{'Total quadrupole moment':>6s}")
        for pos, pos_name in zip(
            nuc_part + el_part,
            ["qm_xx", "qm_yy", "qm_zz", "qm_xy", "qm_xz", "qm_yz", "qm_rr"],
        ):
            log(f"{pos_name !s:>6s} {pos:>19.7f} {(pos / buckingham):>15.7f}")

        log.hline("=")
    # Return in Atomic units
    return (
        el_part[0],
        el_part[1],
        el_part[2],
        el_part[3],
        el_part[4],
        el_part[5],
    )


def nuc_part_qm(basis) -> NDArray[np.float64]:
    """Calculating nuclear part of quadrupole moments
    equation: Nuclear_part = sum_N Atomic_Number_N * POSITION_N^2; POSITION = (X,Y,Z);
    qm_nuc_rr = qmxx + qmyy + qmzz
    Definition of traceless quadrupole moments in Molpro:
        qmxx=0.5*(3*xx-qm_nuc_rr)
        qmyy=0.5*(3*yy-qm_nuc_rr)
        qmzz=0.5*(3*zz-qm_nuc_rr)
        qmxy=1.5*xy etc.
    **Arguments**
    basis
        a Basis instance. Contains the nuclear coordinates
    """
    # Calculating nuclear part and total quadrupole moment (nuc <=> nuclear)

    qm_nuc_pos = [
        (
            np.square(np.array(basis.coordinates)[:, 0])
            * np.array(basis.atom)[:]
        ).sum(axis=0),
        (
            np.square(np.array(basis.coordinates)[:, 1])
            * np.array(basis.atom)[:]
        ).sum(axis=0),
        (
            np.square(np.array(basis.coordinates)[:, 2])
            * np.array(basis.atom)[:]
        ).sum(axis=0),
        (
            np.array(basis.coordinates)[:, 0]
            * np.array(basis.coordinates)[:, 1]
            * np.array(basis.atom)[:]
        ).sum(axis=0),
        (
            np.array(basis.coordinates)[:, 0]
            * np.array(basis.coordinates)[:, 2]
            * np.array(basis.atom)[:]
        ).sum(axis=0),
        (
            np.array(basis.coordinates)[:, 1]
            * np.array(basis.coordinates)[:, 2]
            * np.array(basis.atom)[:]
        ).sum(axis=0),
    ]
    qm_nuc_rr = qm_nuc_pos[0] + qm_nuc_pos[1] + qm_nuc_pos[2]
    return np.array(
        [
            (0.5 * (3 * qm_nuc_pos[0] - qm_nuc_rr)),
            (0.5 * (3 * qm_nuc_pos[1] - qm_nuc_rr)),
            (0.5 * (3 * qm_nuc_pos[2] - qm_nuc_rr)),
            (1.5 * qm_nuc_pos[3]),
            (1.5 * qm_nuc_pos[4]),
            (1.5 * qm_nuc_pos[5]),
            qm_nuc_rr,
        ]
    )


def el_part_qm(ints: dict, dm_1: TwoIndex) -> NDArray[np.float64]:
    """Calculating eletronic part of quadrupole moments
    equations:
    Eletronic part = -sum_i POSITION_i^2 ; POSITION = (X,Y,Z)
    qm_el_rr = qmxx + qmyy + qmzz
    Definition of traceless quadrupole moments in Molpro:
    qmxx=0.5*(3*xx-rr)
    qmyy=0.5*(3*yy-rr)
    qmzz=0.5*(3*zz-rr)
    qmxy=1.5*xy etc.
       **Arguments:**
    ints
        (dictionary) contains all quadrupole integrals

    dm_1
        (TwoIndex) the 1-particle reduced density matrix
    """
    e_pos = [
        -ints["mu_xx"].contract("ab,ab", dm_1),
        -ints["mu_yy"].contract("ab,ab", dm_1),
        -ints["mu_zz"].contract("ab,ab", dm_1),
        -ints["mu_xy"].contract("ab,ab", dm_1),
        -ints["mu_xz"].contract("ab,ab", dm_1),
        -ints["mu_yz"].contract("ab,ab", dm_1),
    ]
    qm_el_rr = e_pos[0] + e_pos[1] + e_pos[2]
    return np.array(
        [
            0.5 * (3 * e_pos[0] - qm_el_rr),
            0.5 * (3 * e_pos[1] - qm_el_rr),
            0.5 * (3 * e_pos[2] - qm_el_rr),
            1.5 * e_pos[3],
            1.5 * e_pos[4],
            1.5 * e_pos[5],
            qm_el_rr,
        ]
    )


def check_ints(*args) -> dict[str, Any]:
    """Checking ints"""
    # quadrupole ints
    ints = {}
    mus = [
        "mu_x",
        "mu_y",
        "mu_z",
        "mu_xx",
        "mu_xy",
        "mu_xz",
        "mu_yy",
        "mu_yz",
        "mu_zz",
    ]
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
            "Cannot find all components of the quadrupole moment integrals"
        )

    return ints


def check_orb(
    *args,
    molecular_orbitals: bool = False,
) -> list:
    """Checking orbital"""
    # orb
    orb = unmask_orb(*args)
    if molecular_orbitals and not orb:
        raise ArgumentError(
            f"Cannot find orbitals in function arguments: {args!s}"
        )

    return orb
