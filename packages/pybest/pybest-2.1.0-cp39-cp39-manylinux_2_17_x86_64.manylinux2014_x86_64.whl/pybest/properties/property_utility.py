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
# 03/2025: This file has been written by Somayeh Ahmadkhani (original version)
# See CHANGELOG
from typing import Any

import numpy as np
from numpy.typing import NDArray

from pybest.exceptions import ArgumentError
from pybest.linalg import DenseTwoIndex, OneIndex, TwoIndex
from pybest.utility import check_type
from pybest.wrappers.multipole import unfolding_dm


def nuclear_moment(obj: Any) -> list:
    """Calculate nuclear dipole moment
    Note: This will be removed after implementing `properties.multipole`.

    Parameter:
        - obj (Any): Functions and objects from the CC-base classes.

    Returns:
        list: nuclear dipole moment in [x, y, z direction, norm and, 0 for oscillator strength]
    """
    if not hasattr(obj, "occ_model"):
        raise AttributeError("occ_model attribute is missing.")
    if not hasattr(obj, "property_options"):
        raise AttributeError("property_options attribute is missing.")
    basis = obj.occ_model.factory
    nuc_dm = (
        (
            np.array([basis.coordinates])
            - np.array([obj.property_options.get("coordinates")])
        )
        * np.array([basis.atom]).T
    ).sum(axis=1)[0]

    # listing nuclear dipole moment in x, y, z directions
    mu_n = [nuc_dm[0], nuc_dm[1], nuc_dm[2]]

    # calculate norm of nuclear dipole moment
    mu_n.append(np.linalg.norm(mu_n))

    # considering zero value for nuclear oscilator strength
    mu_n.append(0.0)

    return mu_n


def ground_state_dm(
    obj: Any,
) -> tuple[list[float], list[float], list[float]]:
    """Calculate the ground-state dipole moments.

    Note:
        This function will be changed after implementing `properties.multipole`.

    Parameter:
        - obj (Any): Functions and objects from the CC-base classes.

    Raises:
        ArgumentError: If the density matrix cannot be found.
        ArgumentError: If the density matrix is missing from the dictionary.

    Returns:
        tuple[list[float], list[float], list[float]]: A tuple containing:
            - mu_e list[float]: Electronic dipole moments (mu_g for ground state).
            - mu_n list[float]: Nuclear dipole moments.
            - mu_t list[float]: Total dipole moments of the ground state.

        Each list includes:
            - Dipole moment components along x, y, and z directions (mu_x, mu_y, mu_z).
            - The norm of the dipole moment (|mu|).
            - A value of 0.0 for the ground-state oscillator strength (OS).
    """
    if not hasattr(obj, "checkpoint"):
        raise AttributeError("checkpoint attribute is missing.")

    ncore = obj.occ_model.ncore[0]
    nbasis = obj.occ_model.nbasis[0]
    density_matrix_unmask = obj.checkpoint["dm_1"]
    mu_n = nuclear_moment(obj)
    if "mu_g" in obj.checkpoint:
        mu_e = obj.checkpoint["mu_g"]
        mu_t = mu_n + mu_e

    else:
        orb = obj.checkpoint["orb_a"]
        momentum_integrals = [
            obj.transition_matrix_operator_A[1],
            obj.transition_matrix_operator_A[2],
            obj.transition_matrix_operator_A[3],
        ]

        # Transforming density matrix to AO basis
        if density_matrix_unmask is None:
            raise ArgumentError("Cannot find density matrix")

        check_type("dm_1", density_matrix_unmask, OneIndex, TwoIndex, dict)

        if isinstance(density_matrix_unmask, dict):
            try:
                dm_1 = density_matrix_unmask["pq"].copy()
            except KeyError as error_key:
                raise ArgumentError(
                    "Density matrix missing in dictionary"
                ) from error_key
        else:
            dm_1 = density_matrix_unmask.copy()

        if isinstance(
            dm_1,
            OneIndex,
        ):
            dm_1 = unfolding_dm(dm_1, nbasis=nbasis, ncore=ncore)

        dm_1_tmp = DenseTwoIndex(obj.occ_model.nbasis[0])
        dm_1_tmp.assign_diagonal(1.0, end=ncore)
        dm_1_tmp.assign(
            dm_1,
            begin0=ncore,
            begin1=ncore,
        )
        dm_1 = dm_1_tmp

        orb.itranspose()
        dm_1_tmp.assign_two_index_transform(dm_1, orb)
        dm_1.iscale(2.0)
        obj.checkpoint.update("dm_1", dm_1)

        # listing ground state dipole moment in x, y and, z directions.
        mu_e = [
            -momentum_integrals[i].contract("ab,ab", dm_1) for i in range(3)
        ]
        # storing the norm of electronic dipole moments
        mu_e.append(np.linalg.norm(mu_e))

        mu_t = [mu_n[i] + mu_e[i] for i in range(3)]

        # storing the norm of total dipole moments
        mu_t.append(np.linalg.norm(mu_t))

        # considering zero value for ground state oscilator strength
        mu_e.append(0.0)
        mu_t.append(0.0)

        obj.checkpoint.update("mu_g", mu_e)

    return mu_e, mu_n, mu_t


def lr_utility(
    obj: Any,
    threshold: float,
    index: int,
    e_vals: NDArray[np.float64],
    e_vecs: NDArray[np.float64],
) -> tuple[list[float], list[float], list[float]]:
    """The utility function for linear response properties.

    Parameters:
       - obj (Any): Functions and objects from the CC-base classes.
       - threshold (float, optional): Printing threshold for amplitudes (default: `0.1`).
       - index (int): Index of the electronic state.
       - e_vecs (np.ndarray): Eigenvectors for the response equations.
       - e_vals (float): Eigenvalues for the response equations.
    LR keywords:
       - transition_dipole_moment
       - excited_dipole_moment
       - static_polarizability
       - transition_density_matrix
    """
    if obj.property_options.get("transition_dipole_moment"):
        return lr_transition_dipole(obj, threshold, index, e_vals, e_vecs)
    elif obj.property_options.get("excited_dipole_moment"):
        return lr_excited_dipole(obj, threshold, index, e_vals, e_vecs)
    elif obj.property_options.get("static_polarizability"):
        return lr_polarizability(obj, threshold, index, e_vals, e_vecs)
    elif obj.property_options.get("transition_density_matrix"):
        return lr_transition_1rdm(obj, threshold, index, e_vals, e_vecs)
    else:
        raise ValueError("Invalid linear response property specified.")


def lr_transition_dipole(
    obj: Any,
    threshold: float,
    index: int,
    e_vals: NDArray[np.float64],
    e_vecs: NDArray[np.float64],
) -> tuple[list[float], list[float], list[float]]:
    """Calculate electronic, nuclear, and total dipole moments.

    Parameters:
        - obj (Any): Functions and objects from the CC-base classes.
        - threshold (float, optional): Printing threshold for amplitudes (default: `0.1`).
        - index (int): Index of the electronic state.
        - e_vecs (np.ndarray): Eigenvectors for the response equations.
        - e_vals (float): Eigenvalues for the response equations.

    Returns:
        tuple[list[float], list[float], list[float]]: A tuple containing:
            - mu_e list[float]: Electronic dipole moments (mu_g for ground state).
            - mu_n list[float]: Nuclear dipole moments.
            - mu_t list[float]: Total dipole moments of the ground state.

        Each list includes:
            - Dipole moment components along x, y, and z directions (mu_x, mu_y, mu_z).
            - The norm of the dipole moment (|mu|).
            - A value of 0.0 for the ground-state oscillator strength (OS).
    """
    momentum_integrals = [
        obj.transition_matrix_operator_A[1],
        obj.transition_matrix_operator_A[2],
        obj.transition_matrix_operator_A[3],
    ]

    mu_n = nuclear_moment(obj)

    # Ground state dipole moment
    if index == 0:
        mu_e, mu_n, mu_t = ground_state_dm(obj)
    else:
        mu_g = obj.checkpoint["mu_g"]
        mu_e, mu_t = [], []
        if index == 1:
            for i, val in enumerate(momentum_integrals):
                tm = obj.transition_matrix(
                    threshold, index, val, None, e_vals, e_vecs
                )
                tdm = tm * mu_g[i] - mu_g[i]
                mu_e.append(tdm)
                mu_t.append(mu_e[i] + mu_n[i])
                obj.checkpoint.update("mu_e", mu_e)
        else:
            for i, val in enumerate(momentum_integrals):
                tm = obj.transition_matrix(
                    threshold, index, val, None, e_vals, e_vecs
                )
                mu_e_0 = obj.checkpoint["mu_e"]
                tdm = tm * mu_g[i] - mu_e_0[i]
                mu_e.append(tdm)
                mu_t.append(mu_e[i] + mu_n[i])
                obj.checkpoint.update(f"mu_e{i}", mu_e)

        # Norm of electronic and total dipole moments
        mu_t.append(np.linalg.norm(mu_t))
        mu_e.append(np.linalg.norm(mu_e))

        # Oscillator strength calculations
        mu_t.append(2 * e_vals * pow(mu_t[3], 2) / 3)
        mu_e.append(2 * e_vals * pow(mu_e[3], 2) / 3)
        mu_n[-1] = 2 * e_vals * pow(mu_n[3], 2) / 3

    return mu_e, mu_n, mu_t


def lr_excited_dipole(
    obj: Any,
    threshold: float,
    index: int,
    e_vals: NDArray[np.float64],
    e_vecs: NDArray[np.float64],
):
    """The function for linear response excited dipole moment calculations.
    Parameters:
    - obj (Any): Functions and objects from the CC-base classes.
    - threshold (float, optional): Printing threshold for amplitudes (default: `0.1`).
    - index (int): Index of the electronic state.
    - e_vecs (np.ndarray): Eigenvectors for the response equations.
    - e_vals (float): Eigenvalues for the response equations.

    Returns:
        tuple[list[float], list[float], list[float]]: A tuple containing:
            - mu_e list[float]: Electronic dipole moments (mu_g for ground state).
            - mu_n list[float]: Nuclear dipole moments.
            - mu_t list[float]: Total dipole moments of the ground state.
    """
    pass


def lr_polarizability(
    obj: Any,
    threshold: float,
    index: int,
    e_vals: NDArray[np.float64],
    e_vecs: NDArray[np.float64],
):
    """The function for linear response static polarizability calculations.
    Parameters:
    - obj (Any): Functions and objects from the CC-base classes.
    - threshold (float, optional): Printing threshold for amplitudes (default: `0.1`).
    - index (int): Index of the electronic state.
    - e_vecs (np.ndarray): Eigenvectors for the response equations.
    - e_vals (float): Eigenvalues for the response equations.

    Returns:
        not implemented yet
    """
    pass


def lr_transition_1rdm(
    obj: Any,
    threshold: float,
    index: int,
    e_vals: NDArray[np.float64],
    e_vecs: NDArray[np.float64],
):
    """The function for linear response transition density matrix calculations.
    Parameters:
    - obj (Any): Functions and objects from the CC-base classes.
    - threshold (float, optional): Printing threshold for amplitudes (default: `0.1`).
    - index (int): Index of the electronic state.
    - e_vecs (np.ndarray): Eigenvectors for the response equations.
    - e_vals (float): Eigenvalues for the response equations.

    Returns:
        not implemented yet
    """
    pass
