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
#
# The original version of this module was written by Aleksandra Leszczyk
#
# Detailed changelog:
# 2024: Added new feature to calculate D_1 diagnostic made by Julian Świerczyński
# 03/2025: This file has been modified by Somayeh Ahmadkhani and Lena Szczuczko
"""Restricted Coupled Cluster Singles Doubles Class

Variables used in this module:
 :nocc:       total number of occupied orbitals
 :nvirt:      total number of virtual orbitals
 :ncore:      number of frozen core orbitals in the principle configuration
 :nacto:      number of active occupied orbitals
 :nactv:      number of active virtual orbitals
 :energy:     the CCSD energy, dictionary containing different contributions
 :amplitudes: the CCSD amplitudes (dict), contains t_1 and t_2
 :t_2:        the double-excitation amplitudes
 :t_1:        the single-excitation amplitudes

 Indexing convention:
 :o:        matrix block corresponding to occupied orbitals of principle
            configuration
 :v:        matrix block corresponding to virtual orbitals of principle
            configuration

 EXAMPLE APPLICATION (see pybest/data/examples/rccsd for complete code)

 #  1) Orbitals and reference energy are given explicitly
 solver = RCCSD(linalg_factory, occupation_model)
 result = solver(AO_one_body_ham, AO_two_body_ham, orbitals, eref=hf_energy)

 #  2) Orbitals and reference energy come from the RHF solver
 rhf_solver = RHF(linalg_factory, occupation_model)
 rhf_data = hf(AO_one_body_ham, AO_two_body_ham, initial_orbitals)
 solver = RCCSD(linalg_factory, occupation_model)
 result = solver(AO_one_body_ham, AO_two_body_ham, rhf_data)
"""

from __future__ import annotations

import gc
from functools import partial
from math import sqrt
from typing import Any

import numpy as np
from numpy.typing import NDArray

from pybest.auxmat import get_fock_matrix
from pybest.exceptions import ArgumentError
from pybest.iodata import IOData
from pybest.linalg import (
    CholeskyFourIndex,
    DenseFourIndex,
    DenseOneIndex,
    DenseOrbital,
    DenseTwoIndex,
)
from pybest.log import log, timer
from pybest.pt.perturbation_utils import get_epsilon

from .rcc import RCC


class RCCSD(RCC):
    """Restricted Coupled Cluster Singles Doubles
    for arbitrary single-determinant reference function.
    """

    acronym: str = "RCCSD"
    long_name: str = "Restricted Coupled Cluster Singles Doubles"
    reference: str = "any single-reference wavefunction"
    cluster_operator: str = "T1 + T2"

    @property
    def t_1(self) -> DenseTwoIndex:
        """Single excitation cluster amplitudes."""
        return self._t_1

    @t_1.setter
    def t_1(self, t_1: DenseTwoIndex):
        if isinstance(t_1, DenseTwoIndex):
            self._t_1 = t_1
        else:
            raise TypeError("t_1 must be DenseTwoIndex instance.")

    @property
    def t_2(self) -> DenseFourIndex:
        """Double excitation cluster amplitudes."""
        return self._t_2

    @t_2.setter
    def t_2(self, t_2: DenseFourIndex):
        if isinstance(t_2, DenseFourIndex):
            self._t_2 = t_2
        else:
            raise TypeError("t_2 must be DenseFourIndex instance.")

    @property
    def l_1(self) -> DenseTwoIndex:
        """Single de-excitation lambda amplitudes."""
        return self._l_1

    @l_1.setter
    def l_1(self, l_1: DenseTwoIndex):
        if isinstance(l_1, DenseTwoIndex):
            self._l_1 = l_1
        else:
            raise TypeError("l_1 must be DenseTwoIndex instance.")

    @property
    def l_2(self) -> DenseFourIndex:
        """Double de-excitation lambda amplitudes."""
        return self._l_2

    @l_2.setter
    def l_2(self, l_2: DenseFourIndex) -> None:
        if isinstance(l_2, DenseFourIndex):
            self._l_2 = l_2
        else:
            raise TypeError("l_2 must be DenseFourIndex instance.")

    @property
    def amplitudes(self) -> dict[str, Any]:
        """Dictionary of amplitudes."""
        return {"t_1": self.t_1, "t_2": self.t_2}

    @amplitudes.setter
    def amplitudes(self, amplitudes: dict[str, Any] | Any) -> None:
        if isinstance(amplitudes, dict):
            iterable = amplitudes.values()
        else:
            iterable = amplitudes
        for value in iterable:
            if isinstance(value, DenseTwoIndex):
                self.t_1 = value
            elif isinstance(value, DenseFourIndex):
                self.t_2 = value

    def get_max_amplitudes(
        self, threshold: float = 0.01, limit: Any | int = None
    ) -> dict[str, Any]:
        """Returns a dictionary with list of amplitudes and their indices."""
        # Single-excitation amplitudes
        t_1 = self.t_1.get_max_values(
            limit, absolute=True, threshold=threshold
        )
        max_t1 = []
        for index, value in t_1:
            i, a = index
            i += self.occ_model.ncore[0] + 1
            a += self.occ_model.nocc[0] + 1
            max_t1.append(((i, a), value))
        # Double-excitation amplitudes
        t_2 = self.t_2.get_max_values(
            limit, absolute=True, threshold=threshold
        )
        max_t2 = []
        for index, value in t_2:
            i, a, j, b = index
            i += self.occ_model.ncore[0] + 1
            j += self.occ_model.ncore[0] + 1
            a += self.occ_model.nocc[0] + 1
            b += self.occ_model.nocc[0] + 1
            max_t2.append(((i, a, j, b), value))
        return {"t_1": max_t1, "t_2": max_t2}

    @property
    def l_amplitudes(self) -> dict[str, Any]:
        """Dictionary of amplitudes."""
        return {"l_1": self.l_1, "l_2": self.l_2}

    @l_amplitudes.setter
    def l_amplitudes(self, amplitudes: dict[str, Any]):
        if isinstance(amplitudes, dict):
            iterable = amplitudes.values()
        else:
            iterable = amplitudes
        for value in iterable:
            if isinstance(value, DenseTwoIndex):
                self.l_1 = value
            elif isinstance(value, DenseFourIndex):
                self.l_2 = value
            else:
                raise TypeError(
                    "Value must be a DenseTwoIndex or DenseFourIndex instance."
                )

    # Define property setter
    @RCC.jacobian_approximation.setter
    def jacobian_approximation(self, new: int) -> None:
        if new != 1:
            log.warn(
                "Only simple Jacobian approximation is supported. "
                "`jacobian` keyword argument is reseted to 1."
            )
        self._jacobian_approximation = 1

    def set_hamiltonian(
        self,
        ham_1_ao: DenseTwoIndex,
        ham_2_ao: DenseFourIndex,
        mos: DenseOrbital,
    ) -> None:
        """Saves Hamiltonian terms in cache.

        Arguments:
        ham_1_ao : DenseTwoIndex
            Sum of one-body elements of the electronic Hamiltonian in AO
            basis, e.g. kinetic energy, nuclei--electron attraction energy

        ham_2_ao : DenseFourIndex
            Sum of two-body elements of the electronic Hamiltonian in AO
            basis, e.g. electron repulsion integrals.

        mos : DenseOrbital
            Molecular orbitals, e.g. RHF orbitals or pCCD orbitals.
        """
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        # Transform integrals
        ham_1, ham_2 = self.transform_integrals(ham_1_ao, ham_2_ao, mos)
        ham_2_ao.dump_array(ham_2_ao.label)
        fock = DenseTwoIndex(nacto + nactv)
        fock = get_fock_matrix(fock, ham_1, ham_2, nacto)

        self.clear_cache()

        def alloc(string: str, arr: DenseFourIndex) -> tuple[partial[Any]]:
            """Determines alloc argument for cache.load method."""
            # We keep one whole CholeskyFourIndex to rule them all.
            # Non-redundant blocks are accessed as views.
            if isinstance(arr, CholeskyFourIndex):
                return (partial(arr.view, **self.get_range(string)),)
            # But we store only non-redundant blocks of DenseFourIndex
            return (partial(arr.copy, **self.get_range(string)),)

        # Blocks of Fock matrix
        for block in ["oo", "ov", "vv"]:
            self.init_cache(f"fock_{block}", alloc=alloc(block, fock))

        # Blocks of two-body Hamiltonian
        for block in [
            "oooo",
            "ooov",
            "oovo",
            "ovov",
            "oovv",
            "ovvv",
            "vovv",
            "vvvv",
        ]:
            self.init_cache(f"eri_{block}", alloc=alloc(block, ham_2))

        # Exchange terms from CC equations
        def alloc_exc(string: str) -> tuple[partial[Any]]:
            """Determines alloc argument for cache.load method."""
            kwargs = self.get_range(string)
            return (partial(ham_2.contract, "abcd->abcd", **kwargs),)

        # exchange_oovv = <ijka> - 2 <ikja>
        mat = self.init_cache("exchange_ooov", alloc=alloc_exc("ooov"))
        mat.iadd_transpose((0, 2, 1, 3), factor=-2)

        # exchange_ooov = <ijab> - 2 <ijba>
        mat = self.init_cache("exchange_oovv", alloc=alloc_exc("oovv"))
        mat.iadd_transpose((0, 1, 3, 2), factor=-2)
        if self.dump_cache:
            self.cache.dump("exchange_oovv")

        ham_2.__del__()
        gc.collect()

    def set_dm(self, *args: Any) -> None:
        """Determine all supported RDMs and put them into the cache."""
        raise NotImplementedError

    @staticmethod
    def compute_t1_diagnostic(t_1: DenseTwoIndex, nocc: int) -> float:
        """Computes T1 diagnostic = |t_1| / sqrt(2 * nocc)."""
        return sqrt(t_1.contract("ab,ab", t_1)) / sqrt(2 * nocc)

    @staticmethod
    def compute_d1_diagnostic(t_1: DenseTwoIndex) -> float:
        """Compute D_1 diagnostic.
           According to the equation:
           D_1 = sqrt( max_eigvals_value(T_1 * T_1.Transpose) )

        Args:
            t_1 (DenseTwoIndex): The T_1 amplitudes

        Returns:
            float: The value of the D_1 diagnostic
        """
        t1_t1T = t_1.contract("ab,cb->ac", t_1)
        # We diagonalize a symmetric matrix (set use_eigh=True)
        e_t_1 = t1_t1T.diagonalize(use_eigh=True)

        return sqrt(np.max(e_t_1.array))

    def generate_random_single_amplitudes(self) -> DenseTwoIndex:
        """Generate random guess for t_1 ov matrix."""
        nov = self.occ_model.nacto[0] * self.occ_model.nactv[0]
        t_1 = DenseTwoIndex(self.occ_model.nacto[0], self.occ_model.nactv[0])
        t_1.randomize()
        t_1.iscale(-1.0 / nov)
        return t_1

    def generate_random_double_amplitudes(self) -> DenseFourIndex:
        """Generate random guess for t_2 ovov matrix."""
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        nov = self.occ_model.nacto[0] * self.occ_model.nactv[0]
        t_2 = DenseFourIndex(nacto, nactv, nacto, nactv)
        t_2.randomize()
        t_2.iscale(-1.0 / nov)
        t_2.iadd_transpose((2, 3, 0, 1))
        return t_2

    def generate_random_guess(self) -> dict[str, Any]:
        """Generate random guess for t_1 ov matrix and t_2 ovov matrix."""
        t_1 = self.generate_random_single_amplitudes()
        t_2 = self.generate_random_double_amplitudes()
        return {"t_1": t_1, "t_2": t_2}

    def generate_constant_guess(self, constant: int | float) -> dict[str, Any]:
        """Generate constant guess for t_1 ov matrix and t_2 ovov matrix."""
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        t_1 = DenseTwoIndex(nacto, nactv)
        t_1.assign(constant)
        t_2 = DenseFourIndex(nacto, nactv, nacto, nactv)
        t_2.assign(constant)
        return {"t_1": t_1, "t_2": t_2}

    def read_guess_from_file(self, select: str = "t") -> dict[str, Any]:
        """Reads guess from file self.initguess."""
        data = IOData.from_file(self.initguess)
        return self.get_amplitudes_from_iodata(data, select)

    def get_amplitudes_from_dict(
        self, dictionary: dict, select: str = "t"
    ) -> dict[str, Any]:
        """Reads available amplitudes from dict instance. Generates random
        amplitudes for missing terms.
        Amplitudes in dict are recognized by key:
         * 't_2' or 'c_2' for double excitatation amplitudes (DenseFourIndex),
         * 't_1' or 'c_1' for single excitation amplitudes (DenseTwoIndex).
        """
        t_1 = None
        t_2 = None
        if f"{select}_2" in dictionary:
            if log.do_medium:
                log(
                    f"   Reading {select}_2 amplitudes from file {self.initguess}"
                )
            t_2 = dictionary[f"{select}_2"]
        elif "c_2" in dictionary:
            if log.do_medium:
                log(f"   Reading C_2 amplitudes from file {self.initguess}")
            t_2 = dictionary["c_2"]
        if f"{select}_1" in dictionary:
            if log.do_medium:
                log(
                    f"   Reading {select}_1 amplitudes from file {self.initguess}"
                )
            t_1 = dictionary[f"{select}_1"]
        elif "c_1" in dictionary:
            if log.do_medium:
                log(f"   Reading C_1 amplitudes from file {self.initguess}")
            t_1 = dictionary["c_1"]
        if t_1 is None and t_2 is None:
            raise ArgumentError("Initial amplitudes not found.")
        if t_1 is None:
            t_1 = self.generate_mp2_single_amplitudes()
        if t_2 is None:
            t_2 = self.generate_mp2_double_amplitudes()
        # we have to return t_1 and t_2 otherwise the code breaks
        return {"t_1": t_1, "t_2": t_2}

    def get_amplitudes_from_iodata(
        self, iodata: IOData, select: str = "t"
    ) -> dict[str, Any]:
        """Reads available amplitudes from IOData instance. Generates random
        amplitudes for missing terms.
        Amplitudes in iodata are recognized by attribute name:
         * 't_2' or 'c_2' for double excitatation amplitudes (DenseFourIndex),
         * 't_1' or 'c_1' for single excitation amplitudes (DenseTwoIndex).

        If 't_1' or 't_2' is missing, they will be replaced by an MP2 guess
        """
        t_1 = None
        t_2 = None
        if hasattr(iodata, "amplitudes"):
            return self.get_amplitudes_from_dict(iodata.amplitudes)
        if hasattr(iodata, f"{select}_2"):
            if log.do_medium:
                log(
                    f"   Reading {select}_2 amplitudes from file {self.initguess}"
                )
            t_2 = iodata.t_2 if select == "t" else iodata.l_2
        elif hasattr(iodata, "c_2"):
            if log.do_medium:
                log(f"   Reading C_2 amplitudes from file {self.initguess}")
            t_2 = iodata.c_2
        if hasattr(iodata, f"{select}_1"):
            if log.do_medium:
                log(
                    f"   Reading {select}_1 amplitudes from file {self.initguess}"
                )
            t_1 = iodata.t_1 if select == "t" else iodata.l_1
        elif hasattr(iodata, "c_1"):
            if log.do_medium:
                log(f"   Reading C_1 amplitudes from file {self.initguess}")
            t_1 = iodata.c_1
        if t_1 is None and t_2 is None:
            raise ArgumentError("Initial amplitudes not found.")
        if t_1 is None:
            t_1 = self.generate_mp2_single_amplitudes()
        if t_2 is None:
            t_2 = self.generate_mp2_double_amplitudes()
        return {"t_1": t_1, "t_2": t_2}

    @timer.with_section("RCCSD: MP2 guess")
    def generate_mp2_guess(self) -> dict[str, Any]:
        """Generate the MP2 initial guess for CC amplitudes"""
        if log.do_medium:
            log("Performing an MP2 calculations for an initial guess.")
        t_1 = self.generate_mp2_single_amplitudes()
        t_2 = self.generate_mp2_double_amplitudes()
        if log.do_medium:
            log("Resuming CC calculation.")
            log.hline("~")
        return {"t_1": t_1, "t_2": t_2}

    @timer.with_section("RCCSD: T_1 MP2 guess")
    def generate_mp2_single_amplitudes(self):
        """Generate the MP2 T_1 initial guess for CC amplitudes"""
        if log.do_medium:
            log("   Generating MP2 guess for T_1.")
        no = self.occ_model.nacto[0]
        # Get effective Hamiltonian
        try:
            t_1 = self.from_cache("fock_ov")
            fi = self.from_cache("fock_oo").copy_diagonal()
            fa = self.from_cache("fock_vv").copy_diagonal()
        except KeyError:
            t_1 = self.from_cache("fock").copy(end0=no, begin1=no)
            fi = self.from_cache("fock").copy_diagonal(end=no)
            fa = self.from_cache("fock").copy_diagonal(begin=no)
        eps_1 = get_epsilon(
            self.denself, [fi, fa], singles=True, doubles=False
        )
        # Determine amplitudes
        return t_1.divide(eps_1)

    @timer.with_section("RCCSD: T_2 MP2 guess")
    def generate_mp2_double_amplitudes(self) -> DenseFourIndex:
        """Generate the MP2 T_2 initial guess for CC amplitudes"""
        if log.do_medium:
            log("   Generating MP2 guess for T_2.")
        no = self.occ_model.nacto[0]
        nv = self.occ_model.nactv[0]
        # Get effective Hamiltonian
        try:
            eri_oovv = self.from_cache("eri_oovv")
            self.from_cache("fock_ov")
            fi = self.from_cache("fock_oo").copy_diagonal()
            fa = self.from_cache("fock_vv").copy_diagonal()
        except KeyError:
            eri_oovv = self.from_cache("goovv")
            self.from_cache("fock").copy(end0=no, begin1=no)
            fi = self.from_cache("fock").copy_diagonal(end=no)
            fa = self.from_cache("fock").copy_diagonal(begin=no)
        # Get eps[ia,jb] (fa + fb - fi - fj)
        # Requires us to store dense ovov object
        # NOTE: this part of the code can be moved to C++
        eps_2 = get_epsilon(
            self.denself, [fi, fa], singles=False, doubles=True
        )
        # Determine amplitudes
        # Get giajb from gijab
        t_2 = eri_oovv.contract("abcd->acbd")
        t_2.array[:] /= eps_2.array.reshape(no, nv, no, nv)
        # free memory
        eps_2.__del__()
        gc.collect()
        return t_2

    @timer.with_section("RCCSD: Energy")
    def calculate_energy(
        self,
        e_ref: float,
        e_core: float = 0.0,
        skip_seniority: bool = True,
        **amplitudes: dict[str, Any],
    ) -> dict[str, Any]:
        """Returns a dictionary of energies:
        e_tot: total energy,
        e_corr: correlation energy,
        e_ref: energy of reference determinant,
        e_corr_s: part of correlation energy,
        e_corr_d: part of correlation energy.
        """
        energy = {
            "e_ref": e_ref,
            "e_tot": 0.0,
            "e_corr": 0.0,
            "e_corr_s": 0.0,
            "e_corr_d": 0.0,
        }

        try:
            t_2 = amplitudes.get("t_2", self.t_2)
        except AttributeError:
            t_2 = amplitudes.get("t_2")
        try:
            t_1 = amplitudes.get("t_1", self.t_1)
        except AttributeError:
            t_1 = amplitudes.get("t_1")

        fock_ov = self.from_cache("fock_ov")
        exchange_oovv = self.from_cache("exchange_oovv")

        energy["e_corr_d"] -= exchange_oovv.contract("abcd,adbc", t_2)

        e_1 = 2 * fock_ov.contract("ab,ab", t_1)
        tmp_ov = DenseTwoIndex(
            self.occ_model.nacto[0], self.occ_model.nactv[0]
        )
        exchange_oovv.contract("abcd,bc->ad", t_1, out=tmp_ov)
        if self.dump_cache:
            self.cache.dump("exchange_oovv")
        e_11 = tmp_ov.contract("ab,ab", t_1)
        energy["e_corr_s"] = e_1 - e_11

        energy["e_corr"] = energy["e_corr_d"] + energy["e_corr_s"]
        energy["e_tot"] = e_ref + e_core + energy["e_corr"]
        return energy

    def print_energy_details(self):
        """Prints energy contributions."""
        log(f"{'Singles':21} {self.energy['e_corr_s']:16.8f} a.u.")
        log(f"{'Doubles':21} {self.energy['e_corr_d']:16.8f} a.u.")

    def print_amplitudes(
        self, threshold: float = 1e-3, limit: None | int = None
    ) -> None:
        """Prints highest amplitudes."""
        amplitudes = self.get_max_amplitudes(threshold=threshold, limit=limit)
        max_double = amplitudes["t_2"]
        max_single = amplitudes["t_1"]

        if max_double:
            log("Leading double excitation amplitudes\n")
            log(f"{'amplitude':>13}{'i':>4}{'j':>4}  ->{'a':>4}{'b':>4}\n")
            for index, value in max_double:
                i, a, j, b = index
                log(f"{value:13.6f}{i:>4}{j:>4}  ->{a:4}{b:4}")
            log.hline("-")

        if max_single:
            log("\nLeading single excitation amplitudes\n")
            log(f"{'amplitude':>13}{'i':>4}  ->{'a':>4}\n")
            for index, value in max_single:
                i, a = index
                log(f"{value:13.6f}{i:>4}  ->{a:4}")
            log.hline("-")
        t1_diagnostic = self.compute_t1_diagnostic(
            self.t_1, self.occ_model.nacto[0]
        )
        d1_diagnostic = self.compute_d1_diagnostic(self.t_1)
        log(f"T1 diagnostic: {t1_diagnostic:4.6f}")
        log(f"D1 diagnostic: {d1_diagnostic:4.6f}")

    def ravel(
        self, amplitudes: dict[str, Any]
    ) -> DenseOneIndex | NDArray[np.float64]:
        """Return a one-dimensional numpy.ndarray or a DenseOneIndex containing
        flatten data from input operands. Note that operand arrays stored in
        the `amplitudes` argument are deleted.

        Arguments:
            amplitudes : dict
                contains:
                - t_1 : DenseTwoIndex
                - t_2 : DenseFourIndex

         Returns:
            vector/vector._array : DenseOneIndex/numpy.ndarray
                - t_1 [:nacto * nactv]
                - t_2 [nacto * nactv:]

        """
        t_1 = None
        t_2 = None
        nov = self.occ_model.nacto[0] * self.occ_model.nactv[0]
        for value in amplitudes.values():
            if isinstance(value, DenseTwoIndex):
                t_1 = value
            elif isinstance(value, DenseFourIndex):
                t_2 = value
        if t_1 is None:
            raise ArgumentError("DenseTwoIndex object not found!")
        if t_2 is None:
            raise ArgumentError("DenseFourIndex object not found!")
        t_2_triu = t_2.get_triu()
        variable_number = nov + len(t_2_triu)
        vector = DenseOneIndex(variable_number)
        vector.assign(t_1.array.ravel(), end0=nov)
        vector.assign(t_2_triu, begin0=nov)
        # delete arrays
        t_1.__del__()
        t_2.__del__()
        if self.solver in ["pbqn"]:
            return vector
        return vector.array

    def unravel(
        self, vector: DenseOneIndex | NDArray[np.float64]
    ) -> dict[str, Any]:
        """Return DenseTwoIndex and DenseFourIndex instances filled out with
        data from input flat_ndarray.

        Arguments:
            vector : DenseOneIndex or numpy.array. If DenseOneIndex is passed,
                     its elements get deleted after the operation is done
        """
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        nov = self.occ_model.nacto[0] * self.occ_model.nactv[0]
        t_1 = DenseTwoIndex(nacto, nactv)
        t_2 = DenseFourIndex(nacto, nactv, nacto, nactv)
        t_1.assign(vector, end2=nov)
        t_2.assign_triu(vector, begin4=nov)
        t_p = t_2.contract("abab->ab")
        t_2.iadd_transpose((2, 3, 0, 1))
        ind1, ind2 = np.indices((nacto, nactv))
        indp = [ind1, ind2, ind1, ind2]
        t_2.assign(t_p, indp)
        # clear memory
        if isinstance(vector, DenseOneIndex):
            vector.__del__()
        gc.collect()
        return {"t_1": t_1, "t_2": t_2}

    @timer.with_section("RCCSD: VecFct")
    def vfunction(
        self, vector: DenseOneIndex | NDArray[np.float64]
    ) -> DenseOneIndex | NDArray[np.float64]:
        """Shorter version of residual vector to accelerate solving."""
        amplitudes = self.unravel(vector)
        return self.ravel(self.cc_residual_vector(amplitudes))

    def cc_residual_vector(self, amplitudes: dict[str, Any]) -> dict[str, Any]:
        """Residual vector of coupled cluster equations. Needs to be zero.

        Arguments:
            amplitudes : numpy.ndarray
                vector containing singles and doubles cluster amplitudes.

        Abbreviations

        * o - number of active occupied orbitals
        * v - number of active virtual orbitals
        * t_1, t_2 - current solution for CC amplitudes
        * out_s, out_d - vector function containers (singles, doubles)
        * aux - auxilary matrix t_ia_jb + t_ia * t_jb
        * mat_ov - two-index temporary matrix (ov is occupied x virtual)
        * exchange_oovv - four index integrals with exchange part
        """
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        t_1 = amplitudes["t_1"]
        t_2 = amplitudes["t_2"]

        # Fock matrix, ERI, exchange terms

        fock_oo = self.from_cache("fock_oo")
        fock_ov = self.from_cache("fock_ov")
        fock_vv = self.from_cache("fock_vv")
        eri_oooo = self.from_cache("eri_oooo")
        eri_ooov = self.from_cache("eri_ooov")
        eri_oovv = self.from_cache("eri_oovv")
        eri_ovov = self.from_cache("eri_ovov")
        eri_vovv = self.from_cache("eri_vovv")
        eri_vvvv = self.from_cache("eri_vvvv")
        exchange_ooov = self.from_cache("exchange_ooov")

        # SINGLES equations
        # 6.0  f_ia
        out_s = fock_ov.copy()
        to_s = {"out": out_s, "clear": False}

        # 7.0  -<ia|kc> t_k^c
        eri_ovov.contract("abcd,cd->ab", t_1, out_s, factor=-1)
        # 7.1  2 <ik|ac> t_k^c
        eri_oovv.contract("abcd,bd->ac", t_1, out_s, factor=2)
        # 5 intermediate matrix  Z_dk = f_dk - (<kl|cd> - 2 <kl|dc>) t_l^c
        Z_kd = fock_ov.copy()
        exchange_oovv = self.from_cache("exchange_oovv")
        exchange_oovv.contract("abcd,bc->ad", t_1, out=Z_kd, factor=-1)
        # 7.2  Z_dk (2 t_ik^ad - T_ik^da)
        # a) 7.2  Z_dk (2 t_ik^ad)
        t_2.contract("abcd,cd->ab", Z_kd, factor=2, **to_s)
        # 3 intermediate matrix  X_il = - f_il + (<kl|cd> - 2 <kl|dc>) t_ik^cd
        mat_oo = fock_oo.copy()
        mat_oo.iscale(-1)
        to_o = {"out": mat_oo, "clear": False}
        exchange_oovv.contract("abcd,ecad->eb", t_2, **to_o)
        # 7.3  X_il t_l^a
        mat_oo.contract("ab,bc->ac", t_1, **to_s)
        # 4 intermediate matrix  Y_ac = f_ac + (<kl|cd> - 2 <kl|dc>) t_lk^ad
        mat_vv = fock_vv.copy()
        to_v = {"out": mat_vv, "clear": False}
        exchange_oovv.contract("abcd,bead->ec", t_2, **to_v)
        # 7.4  Y_ac t_i^c
        t_1.contract("ab,cb->ac", mat_vv, **to_s)

        # DOUBLES equations
        # Create doubles vector function ovov
        out_d = DenseFourIndex(nacto, nactv, nacto, nactv)
        to_d = {"out": out_d, "clear": False}
        # 8.1 update intermediate X_il: -f_lc t_i^c
        t_1.contract("ab,cb->ac", fock_ov, factor=-1, **to_o)
        # 8.2 update intermediate X_il: +(<il|kc> -2<ik|lc>) t_k^c
        exchange_ooov.contract("abcd,cd->ab", t_1, **to_o)
        # 8.3 update intermediate X_il: (<kl|cd> -2<kl|dc>) t_k^d t_i^c
        mat_ov = exchange_oovv.contract("abcd,ad->bc", t_1)
        t_1.contract("ab,cb->ac", mat_ov, **to_o)
        mat_ov.__del__()
        # 12.0 X_il t_jl^ba
        t_2.contract("abcd,ec->edab", mat_oo, **to_d)
        # 9.3 update intermediate Y_ac:  (<kl|cd> -2<kl|dc>) t_k^d t_i^c
        mat_ov = exchange_oovv.contract("abcd,ad->bc", t_1)
        if self.dump_cache:
            self.cache.dump("exchange_oovv")
        t_1.contract("ab,ac->bc", mat_ov, factor=1, **to_v)
        mat_ov.__del__()
        # 9.1 update intermediate Y_ac: -f_lc t_l^a
        t_1.contract("ab,ac->bc", fock_ov, factor=-1, **to_v)
        # 9.2 update intermediate Y_ac: -(<ak|dc> - 2 <ak|cd>) t_k^d
        eri_vovv.contract("abcd,bc->ad", t_1, mat_vv, factor=-1)
        eri_vovv.contract("abcd,bd->ac", t_1, mat_vv, factor=2)
        # 12.1 Y_ac t_ji^bc
        t_2.contract("abcd,ed->ceab", mat_vv, **to_d)
        mat_vv.__del__()

        # 13.0  <ib|ac> t_j^c
        eri_vovv.contract("abcd,ec->bdea", t_1, out_d)
        # 13.5 -<ak|cd> t_i^c t_kj^bd
        intmat = eri_vovv.contract("abcd,ec->eabd", t_1)
        intmat.contract("abcd,cefd->abfe", t_2, factor=-1, **to_d)
        intmat.__del__()
        # 14.0 0.5 <kl|cd> t_kj^bc t_li^ad
        intmat = eri_oovv.contract("abcd,befd->feac", t_2)
        intmat.contract("abcd,cefd->abfe", t_2, **to_d, factor=0.5)
        intmat.__del__()
        # 14.1 0.5 <kl|cd> t_lj^ac t_ki^bd
        intmat = eri_oovv.contract("abcd,edaf->efbc", t_2)
        intmat.contract("abcd,cefd->aefb", t_2, **to_d, factor=0.5)
        intmat.__del__()

        # 10 intermediate W_jibk
        intmat = self.get_intermediate_w_jibk(t_1, t_2)
        # 12.2 W_jibk t_k^a
        intmat.contract("abcd,de->beac", t_1, **to_d)
        intmat.__del__()

        # 11 intermediate U_iakc
        intmat = self.get_intermediate_u_iakc(t_1, t_2)
        # 12.3 U_iakc t_jk^bc
        intmat.contract("abcd,efcd->abef", t_2, **to_d)
        intmat.__del__()

        # b) 11.3  (<kl|dc> - 2 <kl|cd>) t_jk^bc (T_li^ad)
        exchange_oovv = self.from_cache("exchange_oovv")
        intmat = exchange_oovv.contract("abcd,efad->efbc", t_2)
        if self.dump_cache:
            self.cache.dump("exchange_oovv")
        # create t_x intermediate and store in t_2 (not needed anymore)
        t_1.contract("ab,cd->abcd", t_1, out=t_2)
        # @b) 11.3  jbld[(<kl|dc> - 2 <kl|cd>) t_jk^bc] (T_li^ad)
        # iajb=jbia
        intmat.contract("abcd,edcf->abef", t_2, **to_d)
        intmat.__del__()

        # t_x contributions to singles
        # 6.1  (<ik|lc> - 2 <il|kc>) T_kl^ac
        exchange_ooov.contract("abcd,becd->ae", t_2, **to_s)
        # 6.2  -(<ak|cd> - 2 <ak|dc>) T_ik^dc
        eri_vovv.contract("abcd,edbc->ea", t_2, out_s, factor=-1)
        eri_vovv.contract("abcd,ecbd->ea", t_2, out_s, factor=2)
        # 7.2  Z_dk (2 t_ik^ad - T_ik^da)
        # b) 7.2  Z_dk (- T_ik^da)
        t_2.contract("abcd,cb->ad", Z_kd, factor=-1.0, **to_s)
        # t_x contribution to doubles
        # 13.1 -<ik|ac> T_kj^bc
        eri_oovv.contract("abcd,befd->acfe", t_2, out_d, factor=-1)
        # 13.2 -<ib|kc> T_kj^ac
        eri_ovov.contract("abcd,cefd->aefb", t_2, out_d, factor=-1)
        # 13.3  <ik|lc> t_j^c T_kl^ba
        intmat = eri_ooov.contract("abcd,ed->aebc", t_1)
        intmat.contract("abcd,cedf->afbe", t_2, **to_d)
        intmat.__del__()
        # 13.4 -<ak|cd> t_j^d T_ki^bc
        intmat = eri_vovv.contract("abcd,ed->eabc", t_1)
        intmat.contract("abcd,cefd->fbae", t_2, factor=-1, **to_d)
        intmat.__del__()

        # Permutation
        out_d.iadd_transpose((2, 3, 0, 1))

        # 14.2 and 14.5 (<kl|cd> T_ij^cd + <ij|kl>) T_kl^ab
        intmat = eri_oovv.contract("abcd,ecfd->efab", t_2)
        eri_oooo.contract("abcd->abcd", out=intmat)
        intmat.contract("abcd,cedf->aebf", t_2, **to_d)
        intmat.__del__()
        # 14.3  <ij|ab>
        eri_oovv.contract("abcd->acbd", out=out_d)
        # 14.4 bottleneck contraction  <ab|cd> T_ij^cd
        eri_vvvv.contract("abcd,ecfd->eafb", t_2, out=out_d)

        # clear storage
        t_1.__del__()
        t_2.__del__()

        return {"out_s": out_s, "out_d": out_d}

    def get_intermediate_w_jibk(
        self, t_1: DenseTwoIndex, t_2: DenseFourIndex
    ) -> DenseFourIndex:
        """Computes part of CC equation."""
        eri_ooov = self.from_cache("eri_ooov")
        eri_oovo = self.from_cache("eri_oovo")
        eri_oovv = self.from_cache("eri_oovv")
        eri_vovv = self.from_cache("eri_vovv")
        exchange_ooov = self.from_cache("exchange_ooov")
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        w_oovo = DenseFourIndex(nacto, nacto, nactv, nacto)
        to_w = {"out": w_oovo, "clear": False}
        # 10.0  -<ji|bk>
        eri_oovo.contract("abcd->abcd", w_oovo, factor=-1)
        # 10.1  (<ik|lc> - 2 <il|kc>) t_jl^bc
        exchange_ooov.contract("abcd,efcd->eafb", t_2, **to_w)
        # 10.2  <il|kc> t_lj^bc
        eri_ooov.contract("abcd,befd->faec", t_2, w_oovo)
        # 10.3  <jk|lc> t_li^bc
        eri_ooov.contract("abcd,cefd->afeb", t_2, w_oovo)
        # 10.4  -<bk|cd> t_ji^cd
        eri_vovv.contract("abcd,ecfd->efab", t_2, w_oovo, factor=-1)
        # 10.5  <kl|cd> t_i^d t_lj^bc
        t_ooov = DenseFourIndex(nacto, nacto, nacto, nactv)
        eri_oovv.contract("abcd,ec->eabd", t_1, out=t_ooov, clear=True)
        t_ooov.contract("abcd,cefd->faeb", t_2, **to_w)
        # 10.6  <kl|cd> t_j^c t_li^bd
        eri_oovv.contract("abcd,ed->eabc", t_1, out=t_ooov, clear=True)
        t_ooov.contract("abcd,cefd->afeb", t_2, **to_w)
        return w_oovo

    def get_intermediate_u_iakc(
        self, t_1: DenseTwoIndex, t_2: DenseFourIndex
    ) -> DenseFourIndex:
        """Computes part of CC equation."""
        eri_ovov = self.from_cache("eri_ovov")
        eri_oovv = self.from_cache("eri_oovv")
        eri_vovv = self.from_cache("eri_vovv")
        # 11.0  -<ia|kc>
        u_ovov = eri_ovov.contract("abcd->abcd")
        u_ovov.iscale(-1)
        to_u = {"out": u_ovov, "clear": False}
        # 11.1  2 <ik|ac>
        eri_oovv.contract("abcd->acbd", factor=2, **to_u)
        # 11.2  -(<ak|cd> - 2 <ak|dc>) t_i^d
        eri_vovv.contract("abcd,ed->eabc", t_1, factor=-1, **to_u)
        eri_vovv.contract("abcd,ec->eabd", t_1, factor=2, **to_u)
        # 11.3  (<kl|dc> - 2 <kl|cd>) (T_li^ad - t_il^ad)
        exchange_oovv = self.from_cache("exchange_oovv")
        # a) 11.3  (<kl|dc> - 2 <kl|cd>) (- t_il^ad)
        # part b) is handled externally
        exchange_oovv.contract("abcd,efbc->efad", t_2, **to_u, factor=-1.0)
        if self.dump_cache:
            self.cache.dump("exchange_oovv")
        return u_ovov

    def vfunction_l(self, vector: DenseOneIndex | NDArray[np.float64]) -> None:
        """Shorter version of residual vector to accelerate solving."""
        raise NotImplementedError

    def l_residual_vector(self, amplitudes: dict[str, Any]) -> Any:
        """Residual vector of Lambda equations. Needs to be zero.

        Arguments:
            amplitudes : numpy.ndarray
                vector containing double Lambda amplitudes.

        """
        raise NotImplementedError

    @timer.with_section("RCCSD: Jacobian")
    def jacobian(self, amplitudes: Any, *args: Any) -> DenseOneIndex:
        """Jacobian approximation to find coupled cluster singles and doubles
        amplitudes.

        **Arguments:**

        amplitudes
             Cluster amplitudes.

        args
             All function arguments needed to calculate the vector
        """
        if log.do_medium:
            log("Computing Jacobian approximation for Quasi-Newton solver.")
        # We do not support more advanced (amplitude-free) Jacobians, yet
        # 1: only Fock matrix elements (f_i - f_a)
        # 2: additional ERI terms
        if self.jacobian_approximation >= 2:
            raise NotImplementedError
        #
        # Get auxiliary matrices and other intermediates
        #
        nov = self.occ_model.nacto[0] * self.occ_model.nactv[0]
        fi = self.from_cache("fock_oo").copy_diagonal()
        fa = self.from_cache("fock_vv").copy_diagonal()
        unknowns = nov * (nov + 1) // 2 + nov
        #
        # Output
        #
        out = self.lf.create_one_index(unknowns)
        #
        # Approximate Jacobian
        #
        # The function returns fi-fa and fi-fa+fj-fb
        fia, fiajb = get_epsilon(
            self.denself, [fi, fa], singles=True, shift=[1e-12, 1e-12]
        )
        fia.iscale(-1.0)
        fiajb.iscale(-1.0)
        # Assign Jacobian for singles
        out.assign(fia.array.reshape(nov), end0=nov)
        fia.__del__()
        # Assign Jacobian for doubles (only unique elements)
        out.assign(fiajb.get_triu(), begin0=nov)
        fiajb.__del__()

        return out
