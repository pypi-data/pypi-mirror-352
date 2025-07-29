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

"""Linear Response Coupled Cluster implementations of a base class for LR with
single and double excitations.

Variables used in this module:
:ncore:     number of frozen core orbitals
:nocc:      number of occupied orbitals in the principle configuration
:nacto:     number of active occupied orbitals in the principle configuration
:nvirt:     number of virtual orbitals in the principle configuration
:nactv:     number of active virtual orbitals in the principle configuration
:nbasis:    total number of basis functions
:nact:      total number of active orbitals (nacto+nactv)

Indexing convention:
:i,j,k,..: occupied orbitals of principle configuration
:a,b,c,..: virtual orbitals of principle configuration
:p,q,r,..: general indices (occupied, virtual)

Abbreviations used (if not mentioned in doc-strings):
:l_pqrs: 2<pq|rs>-<pq|sr>
:g_pqrs: <pq|rs>
"""

from abc import abstractmethod
from typing import Any

import numpy as np

from pybest.auxmat import get_fock_matrix
from pybest.exceptions import ArgumentError
from pybest.featuredlists import OneBodyHamiltonian, TwoBodyHamiltonian
from pybest.linalg import FourIndex, TwoIndex
from pybest.log import log
from pybest.units import debye, electronvolt, invcm
from pybest.utility import (
    check_options,
    check_type,
    split_core_active,
    transform_integrals,
    unmask,
    unmask_orb,
)

from .properties_base import PropertyBase
from .property_utility import lr_utility


class LRCC(PropertyBase):
    """Linear Response Coupled Cluster base class. Not intended
    to be used as a standalone class.

    Purpose:
        Determine the excitation energies from a given LRCC model
        (a) Build the non-symmetric LR Hamiltonian
        (b) Diagonalize LR Hamiltonian

    Currently supported wavefunction models:
        * LR-pCCD
        * LR-pCCD+S

    """

    long_name = ""
    acronym = ""
    reference = ""
    singles_ref = ""
    pairs_ref = ""
    doubles_ref = ""
    singles_ci = ""
    pairs_ci = ""
    doubles_ci = ""

    def tm_results(
        self, threshold: float, index: int, e_vals: float, e_vecs: np.ndarray
    ) -> tuple[list[float], list[float], list[float]]:
        """Calculate the electronic, nuclear, and total dipole moments.

        Parameters:
            threshold (float):   printing threshold for amplitudes (default 0.1).
            index (int):         Index of the electronic state.
            e_vecs (np.ndarray): Eigenvectors for the response equations.
            e_vals (float):      Eigenvalues for the response equations.

        Returns:
            store in checkpoint {"mu_e": list[float], "mu_n": list[float], "mu_t": list[float]}:
                - mu_e is the electronic dipole moment.
                - mu_n is the nuclear dipole moment.
                - mu_t is the total dipole moment.
        """
        return lr_utility(self, threshold, index, e_vals, e_vecs)

    @abstractmethod
    def update_hamiltonian(self, mo1: TwoIndex, mo2: FourIndex) -> None:
        """Prepare effective Hamiltonian elements required for electronic structure calculations,
        including Fock and two-electron integral intermediates in the molecular orbital (MO) basis.

        Args:
        - `mo1`: A `TwoIndex` instance holding one-electron integrals in the MO basis.
        - `mo2`: A `FourIndex` instance holding two-electron integrals in the MO basis.

        This method calculates or retrieves key intermediates used in constructing the Hamiltonian.

        **Cache and Checkpoint Operations:**
        - The checkpoint is first cleared of any previously stored `fock` and blocks of `gpqrs` data.
        - After calculation, results are stored in the cache to avoid redundant calculations in subsequent calls.

        Returns:
            None
        """

    @property
    def transition_matrix_operator_A(self) -> TwoIndex:
        """Return the first operator (A) in the transition matrix <<A;B>>.

        This operator is used in the computation of the transition matrix,
        which describes how a system transitions between states based on
        the operators A and B.

        Returns:
            TwoIndex: The first transition matrix operator A.
        """
        nact = self.occ_model.nact[0]
        if self.property_options.get("operator_A") is None:
            return self.lf.create_two_index(nact)
        return self.property_options.get("operator_A")

    @property
    def transition_matrix_operator_B(self) -> TwoIndex:
        """Return the second operator (B) in the transition matrix <<A;B>>.

        This operator is used in the computation of the transition matrix,
        which describes how a system transitions between states based on
        the operators A and B.

        Returns:
            TwoIndex: The second transition matrix operator B.
        """
        nact = self.occ_model.nact[0]
        if self.property_options.get("operator_B") is None:
            return self.lf.create_two_index(nact)
        return self.property_options.get("operator_B")

    def jacobian(self) -> TwoIndex:
        """Calling Jacobian from the ee_jacobian module checkpoint

        Returns:
            TwoIndex: Jacobian matrix
        """
        e_val = self.checkpoint["e_ee"]
        e_vec = self.checkpoint["civ_ee"]
        if "jacobian" in self._cache:
            jacobian = self.checkpoint["jacobian"]
        else:
            # Reconstruct the Jacobian using eigenvalues and eigenvectors
            jacobian = self.init_cache("jacobian", len(e_val), len(e_val))
            Lambda = np.diag(e_val)
            e_vec_inv = np.linalg.inv(e_vec)

            # matrix-matrix multiplication  V.Lambda.V-1
            jacobian.array = np.dot(np.dot(e_vec, Lambda), e_vec_inv)

            self.checkpoint.update("jacobian", jacobian)
        return jacobian

    def get_property(self) -> None:
        """Get the peroperty from related submodule"""
        e_vals = self.checkpoint["e_ee"]
        e_vecs = self.checkpoint["civ_ee"]
        nroot = self.printoptions.get("nroot")
        # listing electronic, nuclear and total dipole muments
        mu_e, mu_n, mu_t = [], [], []
        for index in range(nroot):
            # eigenvectors \psi_mk where m index is dimension of hamiltonian and 'index' is excitation index(k).
            evec = e_vecs[:, index]
            # The transition matrix function (tm_results) calculate and saves excited dipole moments in the checkpoint
            # under the keywords mu_e_1, mu_n_1, and mu_t_1 for electronic, nuclear, and total dipole moments for each excitation energy.
            mu_e_1, mu_n_1, mu_t_1 = self.tm_results(
                threshold=self.threshold,
                index=index,
                e_vals=e_vals[index],
                e_vecs=evec,
            )
            # mu_e, mu_n, and mu_t for electronic, nuclear, and total dipole moments for all excitation energies.
            mu_t.append(mu_t_1)
            mu_e.append(mu_e_1)
            mu_n.append(mu_n_1)
        # updating chackpoint for sorting all (nroot) excited dipole moments
        self.checkpoint.update("mu_e", mu_e)
        self.checkpoint.update("mu_n", mu_n)
        self.checkpoint.update("mu_t", mu_t)

    def unmask_args(self, *args: Any, **kwargs: Any) -> Any:
        """Resolve and process arguments passed to the function call.
        Extending the method in the base class to update checkpoint values for various
        Hamiltonian terms and amplitudes.

        This method manages and processes two-index (`one-body`) and four-index
        (`two-body`) Hamiltonian terms, along with specific amplitude values,
        updating the checkpoint with the necessary parameters for further
        calculations.

        args:
            Positional arguments containing instances of `TwoIndex` and
            `FourIndex` objects, representing one-body and two-body Hamiltonian terms:

            - `TwoIndex` objects with labels in `OneBodyHamiltonian` are
            added to the `one` term in the Hamiltonian.
            - `FourIndex` objects with labels in `TwoBodyHamiltonian` are
            assigned to the `two` term in the Hamiltonian.

        Keyword Arguments:
            - `e_ee` (TwoIndex):            Matrix of excitation energies.
            - `civ_ee`(TwoIndex):           Matrix of eigen vectors.
            - `dm_1`(TwoIndex):             One particle density matrix.
            - `orbs`:                       Orbitals.
            - `one`/`two` (Two/FourIndex):  One- and two-electron integrals
            - `fock` (Optional):            The Fock matrix, often a two-index Hamiltonian component.
            - `gppqq` (Optional):           A two-electron integral, `<pp|qq>`, involving paired orbitals.
            - `gpqpq` (Optional): Another two-electron integral, `<pq|pq>`, representing cross-term orbital interactions.

        Checkpoint Updates:
        Updates the following checkpoint entries based on processed arguments:
            - `e_ee`,`civ_ee`,`dm_1`, `fock`, `gppqq`, `gpqpq`, `two`, and `one`.

        Returns:
            Any: The result from the `unmask_args` method of the base `PropertyBase` class.
        """
        # The threshold for amplitudes (default 0.1)
        self.threshold = kwargs.get("threshold", 0.1)

        e_ee = unmask("e_ee", *args, **kwargs)
        if e_ee is not None:
            self.checkpoint.update("e_ee", e_ee)

        civ_ee = unmask("civ_ee", *args, **kwargs)
        if civ_ee is not None:
            self.checkpoint.update("civ_ee", civ_ee)

        # The Hartree-Fock spin independent 1-particle RDM (dm_1) or 1-particle RDM for alpha electrons (dm_1_a)
        dm_1 = unmask("dm_1", *args) or unmask("dm_1_a", *args)
        if dm_1 is not None:
            self.checkpoint.update("dm_1", dm_1)
        else:
            raise ArgumentError("Cannot find one particle density matrix.")

        orbs = unmask_orb(*args, **kwargs)
        if orbs:
            orbs = orbs[0]
            self.checkpoint.update("orb_a", orbs.copy())
        else:
            raise ArgumentError("Cannot find orbitals.")

        # Initialize "one" body term in the Hamiltonian as a TwoIndex object.
        one = self.lf.create_two_index(label="one")
        # Initialize the "two" (two-body term), "fock", "gppqq", and "gpqpq" terms and set them to None
        # These will be set either directly from arguments or from keyword arguments (kwargs).
        two = None
        fock = None
        gppqq = None
        gpqpq = None
        # Iterate over all positional arguments passed to the function.
        for arg in args:
            if isinstance(arg, TwoIndex):
                if arg.label in OneBodyHamiltonian:
                    one.iadd(arg)
            elif isinstance(arg, FourIndex):
                if arg.label in TwoBodyHamiltonian:
                    two = arg
        if two is None:
            # Overwrite one
            one = None
            # Read data from kwargs instead
            fock = kwargs.get("fock", None)
            gppqq = kwargs.get("gppqq", None)
            gpqpq = kwargs.get("gpqpq", None)
            if fock is None or gppqq is None or gpqpq is None:
                raise ArgumentError(
                    "fock, gppqq, and gpqpq have to be provided!"
                )
        # Update the checkpoint dictionary with the latest values of "fock", "gppqq", "gpqpq", "two", and "one".
        self.checkpoint.update("fock", fock)
        self.checkpoint.update("gppqq", gppqq)
        self.checkpoint.update("gpqpq", gpqpq)
        self.checkpoint.update("two", two)
        self.checkpoint.update("one", one)
        #
        # Use unmask_args method from the base class
        #

        return PropertyBase.unmask_args(self, *args, **kwargs)

    def prepare_intermediates(self, *args: Any, **kwargs: Any) -> None:
        """Prepare effective Hamiltonian elements required for electronic structure calculations,
        including Fock, one- and two-electron integral intermediates in the molecular orbital (MO) basis.

        This method calculates or retrieves key intermediates used in constructing the Hamiltonian:
        - `fock`: Fock matrix for the active space, calculated as h_pp + sum_i (2 <pi|pi> - <pi|ip>).

        **Arguments:**
        - `mo1`: A `TwoIndex` instance holding one-electron integrals in the MO basis.
        - `mo2`: A `FourIndex` instance holding two-electron integrals in the MO basis.

        **Cache and Checkpoint Operations:**
        - The checkpoint is first cleared of any previously stored `fock` and `one` and `two` data.
        - After calculation, results are stored in the cache to avoid redundant calculations in subsequent calls.

        Returns:
            None
        """
        # Remove data from checkpoint

        fock = self.checkpoint._data.pop("fock")

        mo1 = self.checkpoint._data.pop("one")
        mo2 = self.checkpoint._data.pop("two")

        if all(var is not None for var in [fock]):
            # Load data to cache
            self.init_cache("fock", alloc=fock)

            # Done, return and do nothing
            return

        # Get ranges
        nact = self.occ_model.nact[0]
        nacto = self.occ_model.nacto[0]

        #
        # Fock matrix
        #
        fock = self.init_cache("fock", nact, nact)
        fock = get_fock_matrix(fock, mo1, mo2, nacto)

        self.update_hamiltonian(mo1, mo2)

    def read_input(self, *args: Any, **kwargs: Any) -> Any:
        """Read input parameters and keyword options for transforming electron integrals and
        returns the transformed integrals.

        **Positional Arguments** (passed via `args`):
            one (DenseOneIndex): The sum of all one-electron integrals, such as kinetic energy
                and potential energy contributions.
            two (DenseTwoIndex, CholeskyIndex): Two-electron integrals in a chosen representation,
                used to describe electron repulsion interactions.
            orb (DenseOrbital): An expansion instance containing Molecular Orbital (MO) coefficients.

        **Keyword Arguments** (passed via `kwargs`):
            - `printoptions` (dict, optional): Dictionary for controlling print options, with the
            following keys:
                * `n_root` (int): Specifies the range of excited energies to display.
                Default is 5.
            - `warning` (bool, optional): Controls whether warning messages are printed during the
            execution. The default is False.
            - `indextrans` (Any, optional): Optional parameter specifying a transformation index for
            integral transformation.

        Return:
            Any: Returns transformed integrals, typically including the updated one-electron and
                two-electron integrals, or `None` if no transformation was applied.
        """
        if log.do_medium:
            log.hline("=")
            log.cite(
                "pCCD dipole moments using Linear response method",
                "ahmadkhani2024",
            )

        #
        # Assign keyword arguments
        #
        names = []
        ncore = self.occ_model.ncore[0]
        nact = self.occ_model.nact[0]

        # Helper function to retrieve values from kwargs with a default fallback, while tracking used names
        def _helper(x: str, y: Any) -> Any:
            """Helper function that appends 'x' to the 'names' list and returns
            the corresponding value from 'kwargs' if 'x' exists, otherwise returns 'y'.

            Args:
                x (str): The key to look up in kwargs.
                y (Any): The default value to return if 'x' is not found in kwargs.

            Returns:
                Any: The value from kwargs corresponding to 'x' or 'y'.
            """
            names.append(x)
            return kwargs.get(x, y)

        warning = _helper("warning", False)
        indextrans = kwargs.get("indextrans", None)
        _printoptions = _helper("printoptions", {})
        _printoptions.setdefault("nroot", 5)

        _property_options = _helper("property_options", {})
        _property_options.setdefault("coordinates", [])
        _property_options.setdefault("operator_A", ())
        _property_options.setdefault("operator_B", ())
        _property_options.setdefault("operator_B", ())
        _property_options.setdefault("transition_dipole_moment", ())

        self.printoptions = _printoptions
        self.property_options = _property_options

        #
        # Check kwargs
        #
        for key, _value in kwargs.items():
            if key not in names:
                raise ArgumentError(f"Unknown keyword argument {key}")

        #
        # Check dictionaries in keyword arguments
        #
        self.check_keywords(_property_options)
        self.check_keywords(_printoptions)

        #
        # Check and validate 'warning' and print option types
        #
        check_options("warning", warning, False, True, 0, 1)
        check_type("n_root", _printoptions["nroot"], int)

        check_type("coordinates", _property_options["coordinates"], list)
        check_type("operator_A", _property_options["operator_A"], tuple)
        check_type("operator_B", _property_options["operator_B"], tuple)
        check_type(
            "transition_dipole_moment",
            _property_options["transition_dipole_moment"],
            bool,
        )

        one = self.checkpoint._data.pop("one")
        two = self.checkpoint._data.pop("two")
        orb = self.checkpoint["orb_a"]

        # If one and two are present, transform them
        if one is None and two is None:
            # We do not transform them.
            # Put them back to checkpoint otherwise code will break
            self.checkpoint.update("one", None)
            self.checkpoint.update("two", None)
            # Finish
            return None
        #
        # Transform of integrals:
        #
        if ncore > 0:
            cas = split_core_active(
                one,
                two,
                orb,
                e_core=0.0,
                ncore=ncore,
                nactive=nact,
                indextrans=indextrans,
            )
            self.checkpoint.update("one", cas.one)
            self.checkpoint.update("two", cas.two)
            # Done and return
            return None
        # ti --> transformed_integrals
        ti = transform_integrals(one, two, orb, indextrans=indextrans)
        self.checkpoint.update("one", ti.one[0])
        self.checkpoint.update("two", ti.two[0])

    def check_keywords(self, printoptions: Any) -> None:
        """Check dictionaries if they contain proper keys.

        **Arguments:**
             printoptions (Any)
             See :py:meth:`OrbitalEnergyBase.read_input.`
        """
        #
        # Check printoptions
        #

        for key, value in printoptions.items():
            check_options(
                str(printoptions),
                key,
                "nroot",
                "coordinates",
                "operator_A",
                "operator_B",
                "transition_dipole_moment",
            )

            if key == "nroot":
                check_type("printoptions.nroot", value, int)
            elif key == "coordinates":
                check_type("property_options.coordinates", value, list)
            elif key == "operator_A":
                check_type("property_options.operator_A", value, tuple)
            elif key == "operator_B":
                check_type("property_options.operator_B", value, tuple)
            elif key == "transition_dipole_moment":
                check_type(
                    "property_options.transition_dipole_moment", value, bool
                )
            else:
                raise ArgumentError(f"keyword {key} is not defined.")

    def print_results(self) -> None:
        """Print excitation energies and dipole moments.

        Parameters:
            threshold (float):   Printing threshold for amplitudes (default 0.1)
            index (int):         Index of the electronic state.
            e_vals (float):      Eigenvalue for the state of interest.
            e_vecs (np.ndarray): Eigenvectors for the response equations.
        """
        e_vals = self.checkpoint["e_ee"]
        nroot = self.printoptions.get("nroot")

        mu_e = self.checkpoint["mu_e"]
        mu_n = self.checkpoint["mu_n"]
        mu_t = self.checkpoint["mu_t"]

        # Define units and their conversion factors
        units = [
            ("a.u.", 1.0),
            (" db ", debye),
        ]
        # title of results each title containe x, y, z component and norm (|mu|) of dipole moments and,  oscillator strengths
        titles = [
            "Nuclear dipole moment   ",
            "Electronic dipole moment",
            "Total dipole moment     ",
        ]

        for i in range(nroot):
            log(
                f"Excitation energy: {e_vals[i]:.6e} [au]  /  "
                f"{e_vals[i] / electronvolt:.6e} [eV]  /  "
                f"{e_vals[i] / invcm:.6e} [cm^-1]"
            )

            moments = [mu_n[i], mu_e[i], mu_t[i]]
            log.hline(" ")
            log(
                "Dipole moment components:             mu_x      mu_y      mu_z      |mu|     OS(f)"
            )

            for title, moment in zip(titles, moments):
                for unit, conversion in units:
                    formatted_moments = [
                        f"{m / conversion:>10.4f}" for m in moment
                    ]
                    log(f"{title} ({unit}): {''.join(formatted_moments)}")
                log.hline(" ")

            log.hline("-")

    log.hline("=")
    log.hline("~")
