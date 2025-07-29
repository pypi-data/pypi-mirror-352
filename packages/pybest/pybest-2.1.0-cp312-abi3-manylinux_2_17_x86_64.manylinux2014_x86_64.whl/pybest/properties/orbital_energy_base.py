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
# 11/2024:
# This file has been written by Seyedehdelaram Jahani (original version)
#
# Detailed changes:
# See CHANGELOG

"""Base class for single and pair orbital energies from a restricted wavefunction.

This is a base class to determine orbital energies from Koopmans', Modified Koopmans' and
extended Koopmans' theorem.

Variables used in this module:
 :nacto:     number of electron pairs (abbreviated as no)
 :nactv:     number of (active) virtual orbitals in the principal configuration
             (abbreviated as nv)
 :ncore:     number of core orbitals (abbreviated as nc)
 :nact:      total number of basis functions (abbreviated as na)

 Indexing convention:
  :i,j,k,..: occupied orbitals of principal configuration
  :a,b,c,..: virtual orbitals of principal configuration
  :p,q,r,..: general indices (occupied, virtual)

 For more information see doc-strings.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

import numpy as np

from pybest.auxmat import get_diag_fock_matrix
from pybest.exceptions import ArgumentError
from pybest.featuredlists import OneBodyHamiltonian, TwoBodyHamiltonian
from pybest.linalg import FourIndex, TwoIndex
from pybest.log import log
from pybest.units import electronvolt
from pybest.utility import (
    check_options,
    check_type,
    split_core_active,
    transform_integrals,
    unmask,
)

from .properties_base import PropertyBase


class OrbitalEnergyBase(PropertyBase):
    """Base module for orbital energies.

    Args:
       PropertyBase (class): Inherits from the PropertyBase class, which provides basic properties handling.
    """

    acronym = ""
    long_name = ""
    reference = ""
    comment = "Works for closed-shell systems (restricted)"

    def unmask_args(self, *args: Any, **kwargs: Any) -> Any:
        """Resolve and process arguments passed to the function call.
        Extending the method in the base class to update checkpoint values for various
        Hamiltonian terms and amplitudes.

        This method manages and processes two-index (`one-body`) and four-index
        (`two-body`) Hamiltonian terms, along with specific amplitude values,
        updating the checkpoint with the necessary parameters for further
        calculations.

        **Arguments:**

        *args:
            Positional arguments containing instances of `TwoIndex` and
            `FourIndex` objects, representing one-body and two-body Hamiltonian terms:

            - `TwoIndex` objects with labels in `OneBodyHamiltonian` are
            added to the `one` term in the Hamiltonian.
            - `FourIndex` objects with labels in `TwoBodyHamiltonian` are
            assigned to the `two` term in the Hamiltonian.

        **Keyword Arguments:**

        - `t_p` (DenseTwoIndex): The `T_p` amplitudes, labeled as `"t_p"`.
        - `fock` (Optional): The Fock matrix, often a two-index Hamiltonian component.
        - `gppqq` (Optional): A two-electron integral, `<pp|qq>`, involving paired orbitals.
        - `gpqpq` (Optional): Another two-electron integral, `<pq|pq>`, representing cross-term orbital interactions.

        **Checkpoint Updates:**
        Updates the following checkpoint entries based on processed arguments:
        - `t_p`, `fock`, `gppqq`, `gpqpq`, `two`, and `one`.

        Returns:
        Any: The result from the `unmask_args` method of the base `PropertyBase` class.
        """
        #
        # t_p
        #
        t_p = unmask("t_p", *args, **kwargs)
        if t_p is not None:
            self.checkpoint.update("t_p", t_p)

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
        including Fock and two-electron integral intermediates in the molecular orbital (MO) basis.

        This method calculates or retrieves key intermediates used in constructing the Hamiltonian:
        - `gppqq`: Two-electron integral <pp|qq>, involving pair-pair interactions.
        - `gpqpq`: Two-electron integral <pq|pq>, involving cross-term interactions.
        - `fock`: Fock matrix for the active space, calculated as h_pp + sum_i (2 <pi|pi> - <pi|ip>).

        If these intermediates are already available in the checkpoint, they are loaded from the
        checkpoint cache and reused. Otherwise, they are calculated using the provided two-electron
        integrals in the MO basis.

        **Arguments:**
        - `mo2`: A `FourIndex` instance holding two-electron integrals in the MO basis.
        - `mo1`: A `TwoIndex` instance holding one-electron integrals in the MO basis.

        **Cache and Checkpoint Operations:**
        - The checkpoint is first cleared of any previously stored `fock`, `gppqq`, or `gpqpq` data.
        - After calculation, results are stored in the cache to avoid redundant calculations in subsequent calls.

        Returns:
            None
        """
        # Remove data from checkpoint
        fock = self.checkpoint._data.pop("fock")
        gppqq = self.checkpoint._data.pop("gppqq")
        gpqpq = self.checkpoint._data.pop("gpqpq")
        mo1 = self.checkpoint._data.pop("one")
        mo2 = self.checkpoint._data.pop("two")
        if all(var is not None for var in [fock, gppqq, gpqpq]):
            # Load data to cache
            self.init_cache("fock", alloc=fock)
            self.init_cache("gppqq", alloc=gppqq)
            self.init_cache("gpqpq", alloc=gpqpq)
            # Done, return and do nothing
            return

        na = self.occ_model.nact[0]
        no = self.occ_model.nacto[0]
        #
        # <pp|qq>
        #
        gppqq = self.init_cache("gppqq", na, na)
        mo2.contract("aabb->ab", gppqq)
        #
        # <pq|pq>
        #
        gpqpq = self.init_cache("gpqpq", na, na)
        mo2.contract("abab->ab", gpqpq)
        #
        # Inactive diagonal Fock = h_pp + sum_i (<pi||pi>+<pi|pi>)
        #
        fock = self.init_cache("fock", na)
        get_diag_fock_matrix(fock, mo1, mo2, no)

    @abstractmethod
    def get_property(self) -> None:
        """Compute single and pair orbital energies based on a specific reference wave function."""

    def read_input(self, *args: Any, **kwargs: Any) -> Any:
        """Read input parameters and keyword options for transforming electron integrals and
           return the transformed integrals.

            **Positional Arguments** (passed via `args`):
                one (DenseOneIndex): The sum of all one-electron integrals, such as kinetic energy
                    and potential energy contributions.
                two (DenseTwoIndex, CholeskyIndex): Two-electron integrals in a chosen representation,
                    used to describe electron repulsion interactions.
                orb (DenseOrbital): An expansion instance containing Molecular Orbital (MO) coefficients.

            **Keyword Arguments** (passed via `kwargs`):
                - `printoptions` (dict, optional): Dictionary for controlling print options, with the
                following keys:
                    * `orb_range_o` (int): Specifies the range of occupied orbital energies to display.
                    Default is 10.
                    * `orb_range_v` (int): Specifies the range of virtual orbital energies to display.
                    Default is 20.
                    * `all` (str): Controls the range of all orbital energies. Specific values may
                    vary depending on the calculation requirements.

                - `warning` (bool, optional): Controls whether warning messages are printed during the
                execution. The default is False.
                - `indextrans` (Any, optional): Optional parameter specifying a transformation index for
                integral transformation.

            **Returns**:
                Any: Returns transformed integrals, typically including the updated one-electron and
                    two-electron integrals, or `None` if no transformation was applied.

        ```
        """
        if log.do_medium:
            log.hline("=")
            # FIXME: update later
            log.cite("Jahani2024")

        #
        # Assign keyword arguments
        #
        names = []
        nc = self.occ_model.ncore[0]
        na = self.occ_model.nact[0]

        # Helper function to retrieve values from kwargs with a default fallback
        def _helper(x, y):
            if x in kwargs:
                names.append(x)
                return kwargs.pop(
                    x
                )  # Pop the key from kwargs after retrieving the value
            return y

        warning = _helper("warning", False)
        indextrans = kwargs.get("indextrans", None)
        _printoptions = _helper("printoptions", {})
        _printoptions.setdefault("orb_range_o", 10)
        _printoptions.setdefault("orb_range_v", 20)
        self.printoptions = _printoptions

        #
        # Check kwargs
        #
        for key, _value in kwargs.items():
            if key not in names:
                raise ArgumentError(f"Unknown keyword argument {key}")

        #
        # Check dictionaries in keyword arguments
        #
        self.check_keywords(_printoptions)
        #
        # Check and validate 'warning' and print option types
        #
        check_options("warning", warning, False, True, 0, 1)
        check_type("orb_range_o", _printoptions["orb_range_o"], int, str)
        check_type("orb_range_v", _printoptions["orb_range_v"], int, str)

        one = self.checkpoint._data.pop("one")
        two = self.checkpoint._data.pop("two")
        orb = self.checkpoint._data.pop("orb_a")
        # If one and two are present, transform them
        if one is None and two is None:
            # We do not transform them.
            # Put them back to checkpoint as otherwise code will break
            self.checkpoint.update("one", None)
            self.checkpoint.update("two", None)
            # Finish
            return None
        #
        # Transform of integrals:
        #
        if nc > 0:
            cas = split_core_active(
                one,
                two,
                orb,
                e_core=0.0,
                ncore=nc,
                nactive=na,
                indextrans=indextrans,
            )
            self.checkpoint.update("one", cas.one)
            self.checkpoint.update("two", cas.two)
            # Done and return
            return None
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
                "printoptions",
                key,
                "orb_range_o",
                "orb_range_v",
            )
            if key == "orb_range_o":
                check_type("printoptions.orb_range_o", value, int, str)
            elif key == "orb_range_v":
                check_type("printoptions.orb_range_v", value, int, str)

    def print_single_orbital_energies(
        self, printoptions: Any, select: str
    ) -> None:
        """Print an array of single orbital energies based on a given method (HF and pCCD orbitals).

        **Arguments:**

        printoptions (Any): Options for printing, with 'orb_range_o' and 'orb_range_v'

        select: string (defines the level of approximation)
            'e_orb_ks': (1d array) single (s) orbital energies based on
         Koopmans' (k) theorem.
            'e_orb_mks': (1d array) modification (m) 'e_orb_ks' to single (s) orbital energies based on
         Koopmans' (k) theorem

        method: string
            ``Koopmans`` and ``Modified Koopmans``.
        """
        no = self.occ_model.nacto[0]
        nv = self.occ_model.nactv[0]
        nc = self.occ_model.ncore[0]

        # Sort orbital energies and return the sorted indices
        sort_indices = self.checkpoint[select].sort_indices(reverse=True)

        # Extract 'orb_range_o' and 'orb_range_v' or 'all' orbital energies from 'printoptions'.
        orbrange_o = printoptions.get("orb_range_o")
        orbrange_o = no if orbrange_o == "all" else orbrange_o
        orbrange_v = printoptions.get("orb_range_v")
        orbrange_v = nv if orbrange_v == "all" else orbrange_v

        # Initialize list to store selected orbital energies with sequential indices
        single_orbital_energy = []

        # Iterate through the sorted indices
        for counter, index in enumerate(sort_indices):
            # Include indices within the specified range only
            if (no - orbrange_o) <= counter < (no + orbrange_v):
                energy_eV = self.checkpoint[select].array[index] / electronvolt

                # HOMO and LUMO labels based on original indices
                orbital_type = str(index + 1 + nc)
                if counter == no - 1:
                    orbital_type += ",H"
                elif counter == no:
                    orbital_type += ",L"
                single_orbital_energy.append(
                    (
                        orbital_type,
                        self.checkpoint[select].array[index],
                        energy_eV,
                    )
                )

        # Only print if there are valid orbital energies
        if single_orbital_energy:
            log(
                f"Printing orbital energies from the HF/pCCD wavefunction for {self.acronym}:"
            )
            log.hline(" ")
            log("Orbital energies")

            log(
                f"\t {'orb_index':} \t {'Energy [E_h]':25} \t {'Energy [eV]':17}\n"
            )
            for o_t, e_eh, e_eV in single_orbital_energy:
                log(f"\t {o_t:>6} \t {e_eh:>10.7f} \t {e_eV:>24.3f}")

    def print_pair_orbital_energies(
        self, printoptions: Any, select: str, spin_case: str
    ) -> None:
        """
        Print an array of diagonal (singlet) and off-diagonal open-shell (singlet and triplet) pair orbital
        energies based on a given method (HF and pCCD orbitals) for a given spin case.

        **Arguments:**
        printoptions (Any): Options for printing, with 'orb_range_o' and 'orb_range_v'

        select: string (defines the level of approximation)
            'e_orb_kp_0': (2d array) diagaonal singlet and Off-diagonal open-shell singlet pair (p) orbital
         energies based on Koopmans' (k) theorem
            'e_orb_mkp_0': (2d array) modification (m) 'e_orb_kp_0' to diagaonal singlet and Off-diagonal
         open-shell singlet pair (p) orbital energies based on Koopmans' (k) theorem
            'e_orb_kp_1': (2d array) diagaonal triplet and off-diagonal open-shell triplet pair (p) orbital
         energies based on Koopmans' (k) theorem
            'e_orb_mkp_1': (2d array) modification (m) 'e_orb_kp_1' to Koopmans' (k) theorem (p) orbital
         energies based on Koopmans' (k) theorem

        method: string
            ``Koopmans`` and ``Modified Koopmans``

        spin_case: string
            The spin case, either ``singlet`` or ``triplet``.
        """
        no = self.occ_model.nacto[0]
        nv = self.occ_model.nactv[0]
        nc = self.occ_model.ncore[0]

        # Define the level of approximation for orbital energy
        energy_array = self.checkpoint[select].array

        # Get lower triangular indices, including diagonal for singlet, excluding triplets
        tril_indices = (
            np.tril_indices(no + nv, k=0)
            if spin_case == "singlet"
            else np.tril_indices(no + nv, k=-1)
        )
        rows, cols = tril_indices

        energy_array = energy_array[tril_indices]
        sorted_ind = np.argsort(energy_array)

        # Extract 'orb_range_o' and 'orb_range_v' from printoptions or use defaults.
        orbrange_o = printoptions.get("orb_range_o")
        orbrange_o = no if orbrange_o == "all" else orbrange_o
        orbrange_v = printoptions.get("orb_range_v")
        orbrange_v = nv if orbrange_v == "all" else orbrange_v

        # Define the hamiltonian range
        begin = no - orbrange_o
        end = no + orbrange_v

        # Initialize result containers
        diagonal_results = []
        off_diagonal_results_oo = []  # Off-diagonal occupied orbitals
        off_diagonal_results_vv = []  # Off-diagonal virtual orbitals)

        count_ls = 0
        count_hs = 0
        # Diagonal singlet homo
        diagonal_energies_s_h = [
            energy_array[i] / electronvolt
            for i in filter(
                lambda i: rows[i] == cols[i] and rows[i] < no, sorted_ind
            )
        ]
        # Diagonal singlet lumo
        diagonal_energies_s_l = [
            energy_array[i] / electronvolt
            for i in filter(
                lambda i: rows[i] == cols[i] and rows[i] >= no, sorted_ind
            )
        ]
        # Find the max and min diagonal energy among those collected
        max_energy_diag = max(diagonal_energies_s_h, default=None)
        min_energy_diag = min(diagonal_energies_s_l, default=None)

        for _i, index in enumerate(sorted_ind):
            row, col = (rows[index]), (cols[index])
            _row, _col = rows[_i], cols[_i]
            energy_value = energy_array[index]

            # Print the energy matrix (optional)
            if begin <= _row <= end and begin <= _col <= end:
                orbital_type = f"({row + nc + 1:>3},{col + nc + 1:>3})"
                result_line = f" {orbital_type:>17} {energy_value:>30.7f} {energy_value / electronvolt:>21.3f}"
                # Diagonal elements
                if row == col:
                    if col >= no:
                        if (
                            energy_value / electronvolt
                        ) == min_energy_diag and count_ls == 0:
                            orbital_type += ",L_S"
                            count_ls = +1
                            result_line = f"{orbital_type:>22} {energy_value:>26.7f} {energy_value / electronvolt:>21.3f}"

                    elif row < no:
                        if (
                            energy_value / electronvolt
                        ) == max_energy_diag and count_hs == 0:
                            orbital_type += ",H_S"

                            count_hs = +1
                            result_line = f"{orbital_type:>22} {energy_value:>26.7f} {energy_value / electronvolt:>21.3f}"

                    diagonal_results.append(result_line)
                # Off-diagonal occupied orbitals
                elif _row < no:
                    off_diagonal_results_oo.append(result_line)
                # Off-diagonal virtual orbitals
                else:
                    off_diagonal_results_vv.append(result_line)

        # Print diagonal results
        if spin_case == "singlet" and diagonal_results:
            log("Diagonal singlet pair orbital energies:")
            log(
                f"\t {'orb_index':>8} \t {'Energy [E_h]':>25} \t {'Energy [eV]':>17}"
            )
            for line in diagonal_results:
                log(line)
            log.hline("-")

        # Print off-diagonal occupied results
        if off_diagonal_results_oo:
            log.hline(" ")
            log(
                f"Off-diagonal open-shell {spin_case} pair orbital energies for occupied orbital pairs:"
            )
            log(
                f"\t {'orb_index':>8} \t {'Energy [E_h]':>25} \t {'Energy [eV]':>17}"
            )
            for line in off_diagonal_results_oo:
                log(line)
            log.hline("-")
        # If the variable `no` is equal to 1 (possibly indicating a special condition)
        # Log a message indicating no data is available for display
        if no == 1:
            log(
                f"No off-diagonal open-shell {spin_case} pair orbital energies for occupied orbitals to display!"
            )
            log.hline("-")

        # Print off-diagonal virtual results
        if off_diagonal_results_vv:
            log.hline(" ")
            log(
                f"Off-diagonal open-shell {spin_case} pair orbital energies for remaining orbital pairs:"
            )
            log(
                f"\t {'orb_index':>8} \t {'Energy [E_h]':>25} \t {'Energy [eV]':>17}"
            )
            for line in off_diagonal_results_vv:
                log(line)

        log.hline("-")
        log.hline("-")

    def print_results(self) -> None:
        """Print all information about the single and pair orbital energies based on HF/pCCD methods
        printoptions:
             A dictionary. See :py:meth:`OrbitalEnergyBase.read_input.`
        """
        energy_properties = {
            "Koopmans": ["e_orb_ks", "e_orb_kp_0", "e_orb_kp_1"],
            "Modified Koopmans": ["e_orb_mks", "e_orb_mkp_0", "e_orb_mkp_1"],
        }

        print_options = self.printoptions

        # Print single orbital energies
        self.print_single_orbital_energies(
            print_options, energy_properties[self.acronym][0]
        )
        #
        # Print results for diagonal singlet and off-diagonal singlet and triplet pair orbital energies separately
        #
        log.hline("-")
        log.hline(" ")
        log(
            f"Printing pair orbital energies from the HF/pCCD wavefunction for {self.acronym}:"
        )
        # Print singlet pair orbital energies
        self.print_pair_orbital_energies(
            print_options,
            energy_properties[self.acronym][1],
            spin_case="singlet",
        )
        # Print triplet pair orbital energies
        self.print_pair_orbital_energies(
            print_options,
            energy_properties[self.acronym][2],
            spin_case="triplet",
        )
