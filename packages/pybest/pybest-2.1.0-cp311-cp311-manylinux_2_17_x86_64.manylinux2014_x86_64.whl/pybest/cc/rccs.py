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
# 03/2025:
# This file has been modified by Somayeh Ahmadkhani and Lena Szczuczko
"""Restricted Coupled Cluster Singles Class

Variables used in this module:
 :nocc:       total number of occupied orbitals
 :nvirt:      total number of virtual orbitals
 :ncore:      number of frozen core orbitals in the principle configuration
 :nacto:      number of active occupied orbitals
 :nactv:      number of active virtual orbitals
 :energy:     the CCS energy, dictionary containing different contributions
 :amplitudes: the CCS amplitudes (dict), contains t_1
 :t_1:        the single-excitation amplitudes

 Indexing convention:
 :o:        matrix block corresponding to occupied orbitals of principle
            configuration
 :v:        matrix block corresponding to virtual orbitals of principle
            configuration

 EXAMPLE APPLICATION

 cc_solver = RCCS(linalg_factory, occupation_model)
 cc_result = cc_solver(
     AO_one_body_ham, AO_two_body_ham, hf_io_data_container
 )
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
from pybest.utility import check_options, unmask

from .rcc import RCC


class RCCS(RCC):
    """Restricted Coupled Cluster Singles for arbitrary single-determinant
    reference function.
    """

    acronym = "RCCS"
    long_name = "Restricted Coupled Cluster Singles"
    reference = "any single-reference wavefunction"
    cluster_operator = "T1"
    singles = True
    pairs = False
    doubles = False

    @property
    def t_1(self):
        """Single excitation cluster amplitudes."""
        return self._t_1

    @t_1.setter
    def t_1(self, t_1: DenseTwoIndex):
        if isinstance(t_1, DenseTwoIndex):
            self._t_1 = t_1
        else:
            raise TypeError("t_1 must be DenseTwoIndex instance.")

    @property
    def l_1(self):
        """Single de-excitation lambda amplitudes."""
        return self._l_1

    @l_1.setter
    def l_1(self, l_1: DenseTwoIndex):
        if isinstance(l_1, DenseTwoIndex):
            self._l_1 = l_1
        else:
            raise TypeError("l_1 must be DenseTwoIndex instance.")

    @property
    def amplitudes(self) -> dict[str, Any]:
        """Dictionary of amplitudes."""
        return {"t_1": self.t_1}

    @amplitudes.setter
    def amplitudes(self, amplitudes: dict[str, Any]) -> None:
        if isinstance(amplitudes, dict):
            iterable = amplitudes.values()
        else:
            iterable = amplitudes
        for value in iterable:
            if isinstance(value, DenseTwoIndex):
                self.t_1 = value

    def get_max_amplitudes(
        self, threshold: float = 0.01, limit: None | int = None
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
        return {"t_1": max_t1}

    @property
    def l_amplitudes(self) -> dict[str, Any]:
        """Dictionary of amplitudes."""
        return {"l_1": self.l_1}

    @l_amplitudes.setter
    def l_amplitudes(self, amplitudes: dict[str, Any]):
        if isinstance(amplitudes, dict):
            iterable = amplitudes.values()
        else:
            iterable = amplitudes
        for value in iterable:
            if isinstance(value, DenseTwoIndex):
                self.l_1 = value

    @property
    def freeze(self) -> tuple[str, ...]:
        """The freezed coupled cluster amplitudes"""
        return self._freeze

    @freeze.setter
    def freeze(self, args: tuple[str, ...]):
        self._freeze = args

    # Define property setter
    @RCC.jacobian_approximation.setter
    def jacobian_approximation(self, new: int):
        # Check for possible options
        check_options("jacobian_approximation", new, 1, 2)
        self._jacobian_approximation = new

    def read_input(
        self, *args: Any, **kwargs: dict[str, Any]
    ) -> tuple[DenseTwoIndex, DenseFourIndex, DenseOrbital]:
        """Looks for Hamiltonian terms, orbitals, and overlap."""
        one_mo, two_mo, orb = RCC.read_input(self, *args, **kwargs)
        #
        # Overwrite defaults
        #
        self.initguess = kwargs.get("initguess", "mp2")
        self.freeze = kwargs.get("freeze", [])
        # Choose optimal internal contraction schemes (select=None)
        self.e_core = unmask("e_core", *args, **kwargs)

        return one_mo, two_mo, orb

    def set_hamiltonian(
        self,
        ham_1_ao: DenseTwoIndex,
        ham_2_ao: DenseFourIndex,
        mos: DenseOrbital,
    ) -> None:
        """Saves Hamiltonian terms in cache.

        Arguments:
        ham_1_ao : TwoIndex
            Sum of one-body elements of the electronic Hamiltonian in AO
            basis, e.g. kinetic energy, nuclei--electron attraction energy

        ham_2_ao : FourIndex
            Sum of two-body elements of the electronic Hamiltonian in AO
            basis, e.g. electron repulsion integrals.

        mos : Orbital
            Molecular orbitals, e.g. RHF orbitals or pCCD orbitals.
        """
        #
        # Transform integrals
        #
        mo1, mo2 = self.transform_integrals(ham_1_ao, ham_2_ao, mos)
        ham_2_ao.dump_array(ham_2_ao.label)
        #
        # Clear cache
        #
        self.clear_cache()
        #
        # Update aux matrices
        #
        self.update_hamiltonian(mo1, mo2)
        #
        # Clean up (should get deleted anyways)
        #
        mo2.__del__()

    def set_dm(self, *args: Any) -> None:
        """Determine all supported RDMs and put them into the cache."""
        raise NotImplementedError

    @timer.with_section("RCCS: Hamiltonian")
    def update_hamiltonian(
        self, mo1: DenseTwoIndex, mo2: DenseFourIndex
    ) -> None:
        """Derive all auxiliary matrices.

        **Arguments:**

        mo1, mo2
             one- and two-electron integrals to be sorted.

        cia
             The geminal coefficients. A TwoIndex instance
        """
        if log.do_medium:
            log("Computing auxiliary matrices and effective Hamiltonian.")
        #
        # Get ranges for contract
        #
        nacto = self.occ_model.nacto[0]
        nact = self.occ_model.nact[0]
        #
        # Inactive Fock matrix
        #
        fock = self.init_cache("fock", nact, nact)
        get_fock_matrix(fock, mo1, mo2, nacto)

        #
        # 4-Index slices of ERI
        #
        def alloc(
            arr: DenseFourIndex, block: str
        ) -> None | tuple[partial[Any]]:
            """Determines alloc keyword argument for init_cache method."""
            # We keep one whole CholeskyFourIndex to rule them all.
            # Non-redundant blocks are accessed as views.
            if isinstance(arr, CholeskyFourIndex):
                return (partial(arr.view, **self.get_range(block)),)
            # But we store only non-redundant blocks of DenseFourIndex
            return (partial(arr.copy, **self.get_range(block)),)

        #
        # Get blocks
        #
        slices = ["ovvo", "ovov", "oooo", "vooo", "ovvv"]
        for slice_ in slices:
            self.init_cache(f"g{slice_}", alloc=alloc(mo2, slice_))

    @staticmethod
    def compute_t1_diagnostic(t_1, nocc: int) -> float:
        """Computes T1 diagnostic = |t_1| / sqrt(2 * nocc)."""
        return sqrt(t_1.contract("ab,ab", t_1)) / sqrt(2 * nocc)

    def generate_random_single_amplitudes(self) -> DenseTwoIndex:
        """Generate random guess for t_1 ov matrix."""
        nov = self.occ_model.nacto[0] * self.occ_model.nactv[0]
        t_1 = DenseTwoIndex(self.occ_model.nacto[0], self.occ_model.nactv[0])
        t_1.randomize()
        t_1.iscale(-1.0 / nov)
        return t_1

    def generate_random_guess(self) -> dict[str, Any]:
        """Generate random guess for t_1 ov matrix."""
        t_1 = self.generate_random_single_amplitudes()
        return {"t_1": t_1}

    def generate_constant_guess(self, constant: float) -> dict[str, Any]:
        """Generate constant guess for t_1 ov matrix."""
        t_1 = DenseTwoIndex(self.occ_model.nacto[0], self.occ_model.nactv[0])
        t_1.assign(constant)
        return {"t_1": t_1}

    def read_guess_from_file(self):
        """Reads guess from file self.initguess."""
        data = IOData.from_file(self.initguess)
        return self.get_amplitudes_from_iodata(data)

    def get_amplitudes_from_dict(
        self, dictionary: dict[str, Any]
    ) -> dict[str, Any]:
        """Reads available amplitudes from dict instance. Generates random
        amplitudes for missing terms.
        Amplitudes in dict are recognized by key:
         * 't_1' or 'c_2' for single excitation amplitudes (DenseTwoIndex).
        """
        t_1 = None
        if "t_1" in dictionary:
            t_1 = dictionary["t_1"]
        elif "c_1" in dictionary:
            t_1 = dictionary["c_1"]
        if t_1 is None:
            raise ArgumentError("Initial amplitudes not found.")
        return {"t_1": t_1}

    def get_amplitudes_from_iodata(self, iodata: IOData) -> dict[str, Any]:
        """Reads available amplitudes from IOData instance. Generates random
        amplitudes for missing terms.
        Amplitudes in iodata are recognized by attribute name:
         * 't_2' or 'c_2' for double excitatation amplitudes (DenseFourIndex),
         * 't_1' or 'c_2' for single excitation amplitudes (DenseTwoIndex).
        """
        t_1 = None
        if hasattr(iodata, "amplitudes"):
            return self.get_amplitudes_from_dict(iodata.amplitudes)
        if hasattr(iodata, "t_1"):
            t_1 = iodata.t_1
        elif hasattr(iodata, "c_1"):
            t_1 = iodata.c_1
        if t_1 is None:
            raise ArgumentError("Initial amplitudes not found.")
        return {"t_1": t_1}

    @timer.with_section("RCCS: MP2 guess")
    def generate_mp2_guess(self) -> dict[str, Any]:
        """Generate the MP2 initial guess for CC amplitudes"""
        if log.do_medium:
            log("Performing an MP2 calculations for an initial guess.")
        no = self.occ_model.nacto[0]
        # Get Fock matrix
        t_1 = self.from_cache("fock").copy(end0=no, begin1=no)
        # get slices
        fi = self.from_cache("fock").copy_diagonal(end=no)
        fa = self.from_cache("fock").copy_diagonal(begin=no)
        # get eps[ia] (fa - fi)
        eps_1 = get_epsilon(
            self.denself, [fi, fa], singles=True, doubles=False
        )
        # determine amplitudes
        t_1.idivide(eps_1, factor=-1.0)
        if log.do_medium:
            log("Resuming CC calculation.")
            log.hline("~")
        return {"t_1": t_1}

    @timer.with_section("RCCS: Energy")
    def calculate_energy(
        self, e_ref: float, e_core: float = 0.0, **amplitudes: dict[str, Any]
    ) -> dict[str, Any]:
        """Returns a dictionary of energies:
        e_tot: total energy,
        e_corr: correlation energy,
        e_ref: energy of reference function,
        e_corr_s: part of correlation energy,
        """
        energy = {
            "e_ref": e_ref,
            "e_tot": 0.0,
            "e_corr": 0.0,
            "e_corr_s": 0.0,
            "e_corr_d": 0.0,
        }
        #
        # Get amplitudes and integrals
        #
        fock = self.from_cache("fock")
        govvo = self.from_cache("govvo")
        try:
            t_1 = amplitudes.get("t_1", self.t_1)
        except AttributeError:
            t_1 = amplitudes.get("t_1")
        #
        # E_singles
        # 2 F_md t_md
        ov2 = self.get_range("ov", offset=2)
        e_1 = 2.0 * t_1.contract("ab,ab", fock, **ov2)
        # tia tjb L_ijab
        tmp_ov = self.lf.create_two_index(
            self.occ_model.nacto[0], self.occ_model.nactv[0]
        )
        govvo.contract("abcd,ac->db", t_1, tmp_ov, factor=2.0)
        govvo.contract("abcd,ab->dc", t_1, tmp_ov, factor=-1.0)
        e_11 = tmp_ov.contract("ab,ab", t_1)
        #
        energy["e_corr_s"] = e_1 + e_11
        energy["e_corr"] = energy["e_corr_s"]

        energy["e_tot"] = e_ref + e_core + energy["e_corr"]
        return energy

    def print_energy_details(self) -> None:
        """Prints energy contributions."""
        log(f"{'Singles':21} {self.energy['e_corr_s']:16.8f} a.u.")

    def print_amplitudes(self, threshold=1e-4, limit=None):
        """Prints highest amplitudes."""
        nacto = self.occ_model.nacto[0]
        amplitudes = self.get_max_amplitudes(threshold=threshold, limit=limit)
        max_single = amplitudes["t_1"]

        if max_single:
            log("\nLeading single excitation amplitudes\n")
            log(f"{'amplitude':>13}{'i':>4}  ->{'a':>4}\n")
            for index, value in max_single:
                i, a = index
                log(f"{value:13.6f}{i:>4}  ->{a:4}")
            log.hline("-")
        t1_diagnostic = self.compute_t1_diagnostic(self.t_1, nacto)
        log(f"T1 diagnostic: {t1_diagnostic:4.6f}")

    def ravel(self, amplitudes: dict[str, Any]) -> DenseOneIndex:
        """Return a one-dimensional numpy.ndarray or a DenseOneIndex containing
        flatten data from input operands. Note that operand arrays stored in
        the `amplitudes` argument are deleted.

        Arguments:
            amplitudes : dict
                contains:
                - t_1 : DenseTwoIndex

         Returns:
            vector/vector._array : DenseOneIndex/numpy.ndarray
                - t_1 [:]

        """
        t_1 = None
        nov = self.occ_model.nacto[0] * self.occ_model.nactv[0]
        for value in amplitudes.values():
            if isinstance(value, DenseTwoIndex):
                t_1 = value
        if t_1 is None:
            raise ArgumentError("DenseTwoIndex object not found!")
        vector = DenseOneIndex(nov)
        vector.assign(t_1.array.ravel())
        if self.solver in ["pbqn"]:
            return vector
        return vector.array

    def unravel(
        self, vector: DenseOneIndex | NDArray[np.float64]
    ) -> dict[str, Any]:
        """Returns DenseTwoIndex and DenseFourIndex instances filled out with
        data from input flat_ndarray.

        Arguments:
            vector : DenseOneIndex or numpy.array. If DenseOneIndex is passed,
                     its elements get deleted after the operation is done
        """
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        t_1 = DenseTwoIndex(nacto, nactv)
        t_1.assign(vector)
        # clear memory
        if isinstance(vector, DenseOneIndex):
            vector.__del__()
        gc.collect()
        return {"t_1": t_1}

    @timer.with_section("RCCS: T_1 VecFct")
    def vfunction(
        self, vector: DenseOneIndex | NDArray[np.float64]
    ) -> DenseOneIndex | NDArray[np.float64]:
        """1D vector function of CC residual vector (numpy.ndarray)."""
        amplitudes = self.unravel(vector)
        return self.ravel(self.cc_residual_vector(amplitudes))

    def cc_residual_vector(self, amplitudes: dict[str, Any]) -> dict[str, Any]:
        """Residual vector of Coupled Cluster equations. Needs to be zero.

        Arguments:
            amplitudes : numpy.ndarray
                vector containing double cluster amplitudes.

        Abbreviations:

        * o - number of active occupied orbitals
        * v - number of active virtual orbitals
        * t_1 - current solution for CC amplitudes
        * out_s - vector function
        """
        t_1 = amplitudes["t_1"]
        #
        # Get ranges
        #
        oo2 = self.get_range("oo", offset=2)
        vv2 = self.get_range("vv", offset=2)
        ov2 = self.get_range("ov", offset=2)
        vo2 = self.get_range("vo", offset=2)
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        #
        # Get auxiliary matrices
        #
        fock = self.from_cache("fock")
        govvo = self.from_cache("govvo")
        govov = self.from_cache("govov")
        gvooo = self.from_cache("gvooo")
        govvv = self.from_cache("govvv")
        #
        # temporary storage
        #
        tmp_vv = self.lf.create_two_index(nactv, nactv)
        tmp_oo = self.lf.create_two_index(nacto, nacto)
        tmp_ov = self.lf.create_two_index(nacto, nactv)
        to_oo = {"out": tmp_oo}
        to_ov = {"out": tmp_ov}
        to_vv = {"out": tmp_vv}
        #
        # singles
        #
        out_s = t_1.new()
        to_s = {"out": out_s, "clear": False}
        #
        # t_kc L<ic|ak> (s4)
        #
        govvo.contract("abcd,db->ac", t_1, **to_s, factor=2.0)
        govov.contract("abcd,cb->ad", t_1, **to_s, factor=-1.0)
        #
        # Fac tic; Fki tka (s2,3)
        #
        t_1.contract("ab,bc->ac", fock, **to_s, **vv2)
        t_1.contract("ab,ac->cb", fock, **to_s, factor=-1.0, **oo2)
        #
        # F_ia (s1)
        #
        out_s.iadd(fock, 1.0, **ov2)
        #
        # quadratic terms
        #
        # tic Fck tka = fik tka
        t_1.contract("ab,bc->ac", fock, **to_oo, clear=True, **vo2)
        tmp_oo.contract("ab,bc->ac", t_1, **to_s, factor=-1.0)
        #
        # <ci||lk> tlc tka = gik tka
        #
        gvooo.contract("abcd,ca->bd", t_1, **to_oo, factor=2.0, clear=True)
        gvooo.contract("abcd,da->bc", t_1, **to_oo, factor=-1.0)
        tmp_oo.contract("ab,bc->ac", t_1, **to_s, factor=-1.0)
        #
        # <ka||cd> tkc tid = tid gad
        #
        govvv.contract("abcd,ac->bd", t_1, **to_vv, factor=2.0, clear=True)
        govvv.contract("abcd,ad->bc", t_1, **to_vv, factor=-1.0)
        t_1.contract("ab,cb->ac", tmp_vv, **to_s)
        #
        # cubic terms
        #
        # <kl||cd> tld tic tka = tic Lkc tka = tLik tka
        govvo.contract("abcd,db->ac", t_1, **to_ov, factor=2.0, clear=True)
        govvo.contract("abcd,dc->ab", t_1, **to_ov, factor=-1.0)
        t_1.contract("ab,cb->ac", tmp_ov, **to_oo, clear=True)
        tmp_oo.contract("ab,bc->ac", t_1, **to_s, factor=-1.0)
        #
        # Freeze some amplitudes if required
        #
        for row in self.freeze:
            out_s.set_element(row[0], row[1], 0.0, symmetry=1)

        return {"out_s": out_s}

    @timer.with_section("RCCS: Jacobian")
    def jacobian(
        self, amplitudes: dict[str, Any], *args: Any
    ) -> DenseOneIndex:
        """Jacobian approximation to find coupled cluster singles amplitudes.

        **Arguments:**

        amplitudes
             Cluster amplitudes.

        args
             All function arguments needed to calculate the vector function
        """
        if log.do_medium:
            log("Computing Jacobian approximation for Quasi-Newton solver.")
        fock = self.from_cache("fock")
        nacto = self.occ_model.nacto[0]
        nov = self.occ_model.nacto[0] * self.occ_model.nactv[0]
        fi = fock.copy_diagonal(end=nacto)
        fa = fock.copy_diagonal(begin=nacto)
        #
        # Output
        #
        out = self.lf.create_one_index(nov)
        # The function returns fi-fa and fi-fa+fj-fb
        fia, _ = get_epsilon(
            self.denself,
            [fi, fa],
            singles=self.singles,
            shift=[1e-12, 1e-12],
        )
        fia.iscale(-1.0)
        eps1 = fia.array.reshape(nov)
        out.assign(eps1, end0=nov)
        return out

    def vfunction_l(self, vector: DenseOneIndex | NDArray[np.float64]) -> None:
        """Shorter version of residual vector to accelerate solving."""
        raise NotImplementedError

    def l_residual_vector(self, amplitudes: dict[str, Any]):
        """Residual vector of Lambda equations. Needs to be zero.

        Arguments:
            amplitudes : numpy.ndarray
                vector containing double Lambda amplitudes.

        """
        raise NotImplementedError


class RpCCDCCS(RCCS):
    """Restricted pair Coupled Cluster Doubles with Coupled Cluster Singles"""

    acronym = "RpCCDCCS"
    long_name = (
        "Restricted pair Coupled Cluster Doubles Coupled Cluster Singles"
    )
    cluster_operator = "T1"

    @property
    def t_p(self) -> DenseTwoIndex:
        """Pair amplitudes - DenseTwoIndex instance"""
        return self._t_p

    @t_p.setter
    def t_p(self, t_p: DenseTwoIndex) -> None:
        if isinstance(t_p, DenseTwoIndex):
            self._t_p = t_p
        else:
            raise TypeError("t_p must be a DenseTwoIndex instance.")

    @property
    def iodata(self) -> IOData:
        """Container for output data"""
        iodata = super().iodata
        iodata.update({"t_p": self.t_p})
        return iodata

    def read_input(
        self, *args: Any, **kwargs: dict[str, Any]
    ) -> tuple[DenseTwoIndex, DenseFourIndex, DenseOrbital]:
        """Looks for Hamiltonian terms, orbitals, and overlap."""
        #
        # Call parent class method
        #
        one_mo, two_mo, orb = RCCS.read_input(self, *args, **kwargs)
        #
        # Read electron pair amplitudes
        #
        self.t_p = unmask("t_p", *args, **kwargs)
        #
        # Overwrite reference energy
        #
        self.e_ref = unmask("e_tot", *args, **kwargs)

        return one_mo, two_mo, orb

    def print_energy(self) -> None:
        """Prints energy terms."""
        if log.do_medium:
            log.hline("-")
            log(f"{self.acronym} energy")
            log(f"{'Total energy':24} {self.energy['e_tot']:14.8f} a.u.")
            log(
                f"{'Reference wavefunction':24} {self.energy['e_ref']:14.8f} a.u."
            )
            log(
                f"{'Total correlation energy':24} {self.energy['e_corr']:14.8f} a.u."
            )
            log.hline("~")
            self.print_energy_details()
            log.hline("-")
            log(" ")

    def print_energy_details(self) -> None:
        """Prints energy contributions."""
        log(f"{'Singles':24} {self.energy['e_corr_s']:14.8f} a.u.")

    def set_hamiltonian(
        self,
        ham_1_ao: DenseTwoIndex,
        ham_2_ao: DenseFourIndex,
        mos: DenseOrbital,
    ) -> None:
        """Compute auxiliary matrices

        **Arguments:**

        ham_1_ao, ham_2_ao
             One- and two-electron integrals (some Hamiltonian matrix
             elements) in the AO basis.

        mos
             The molecular orbitals.
        """
        #
        # Transform integrals
        #
        mo1, mo2 = self.transform_integrals(ham_1_ao, ham_2_ao, mos)
        ham_2_ao.dump_array(ham_2_ao.label)
        #
        # Clear cache
        #
        self.clear_cache()
        #
        # Update aux matrices
        #
        # Child class
        self.update_hamiltonian(mo1, mo2)
        # Base class
        RCCS.update_hamiltonian(self, mo1, mo2)
        #
        # Clean up (should get deleted anyways)
        #
        mo2.__del__()

    @timer.with_section("RpCCDCCS: Ham")
    def update_hamiltonian(
        self, mo1: DenseTwoIndex, mo2: DenseFourIndex
    ) -> None:
        #
        # Get ranges and variables
        #
        oov = self.get_range("oov")
        ovo = self.get_range("ovo")
        ovv = self.get_range("ovv")
        vvo = self.get_range("vvo")
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        nact = self.occ_model.nact[0]
        t_p = self.t_p
        #
        # pCCD reference function:
        #
        # use 3-index intermediate (will be used several times)
        # This also works with Cholesky
        # <pq|rr>
        gpqrr = self.lf.create_three_index(nact)
        mo2.contract("abcc->abc", out=gpqrr)
        #
        # vc_ij = sum_d <ij|dd> c_j^d
        #
        vcij = self.init_cache("vcij", nacto, nacto)
        gpqrr.contract("abc,bc->ab", t_p, vcij, **oov)
        #
        # oc_ab = sum_m <ab|mm> c_m^a
        #
        ocab = self.init_cache("ocab", nactv, nactv)
        gpqrr.contract("abc,ca->ab", t_p, ocab, **vvo)
        #
        # oc_jb = sum_m <jb|mm> c_m^b
        #
        ocjb = self.init_cache("ocjb", nacto, nactv)
        gpqrr.contract("abc,cb->ab", t_p, ocjb, **ovo)
        #
        # vc_jb = sum_d <jb|dd> c_j^d
        #
        vcjb = self.init_cache("vcjb", nacto, nactv)
        gpqrr.contract("abc,ac->ab", t_p, vcjb, **ovv)

    @timer.with_section("RpCCDCCS: T_1 VecFct")
    def vfunction(
        self, vector: DenseOneIndex | NDArray[np.float64]
    ) -> DenseOneIndex | NDArray[np.float64]:
        """Shorter version of residual vector to accelerate solving."""
        amplitudes = self.unravel(vector)
        #
        # RLCCD part
        #
        residual = RCCS.cc_residual_vector(self, amplitudes)
        #
        # Coupling to pCCD reference
        #
        residual = self.cc_residual_vector(amplitudes, residual)
        return self.ravel(residual)

    def cc_residual_vector(
        self, amplitudes: dict[str, Any], output: None | dict = None
    ) -> dict[str, Any]:
        """Residual vector of Coupled Cluster equations. Needs to be zero.

        Arguments:
            amplitudes : numpy.ndarray
                vector containing double cluster amplitudes.

        Abbreviations:

        * o - number of active occupied orbitals
        * v - number of active virtual orbitals
        * t_1  - current solution for CC amplitudes
        * out_s - vector function
        """
        t_1 = amplitudes["t_1"]
        t_p = self.t_p
        #
        # Get ranges
        #
        ov2 = self.get_range("ov", offset=2)
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        #
        # Get auxiliary matrices
        #
        fock = self.from_cache("fock")
        ocjb = self.from_cache("ocjb")
        vcjb = self.from_cache("vcjb")
        vcij = self.from_cache("vcij")
        ocab = self.from_cache("ocab")
        govvo = self.from_cache("govvo")
        #
        # singles
        #
        out_s = output["out_s"]
        to_s = {"out": out_s, "clear": False}
        #
        # temporary storage
        #
        tmp_ov = self.lf.create_two_index(nacto, nactv)
        #
        # pCCD reference function
        #
        # L<ik|ac> c_ia t_kc (s12) (icak, iack)
        #
        govvo.contract("abcd,db->ac", t_1, tmp_ov, factor=2.0)
        govvo.contract("abcd,dc->ab", t_1, tmp_ov, factor=-1.0)
        tmp_ov.imul(t_p, 1.0)
        out_s.iadd(tmp_ov)
        #
        # tic (a,c) (s14)
        #
        t_1.contract("ab,cb->ac", ocab, **to_s, factor=-1.0)
        #
        # tka (k,i) (s13)
        #
        t_1.contract("ab,ac->cb", vcij, **to_s, factor=-1.0)
        #
        # Fia cia (s9-3)
        #
        out_s.iadd_mult(t_p, fock, 1.0, **ov2)
        #
        # (i,a) (s11-2)
        # <ia|kk> cka = ocia
        #
        out_s.iadd(ocjb, -1.0)
        #
        # (i,a) (s10-2)
        # <ia|cc> cic = vcia
        #
        out_s.iadd(vcjb, 1.0)
        #
        # Set all diagonal amplitudes zero
        #
        for row in self.freeze:
            out_s.set_element(row[0], row[1], 0.0, symmetry=1)

        return {"out_s": out_s}

    @timer.with_section("RpCCDCCS: Jacobian")
    def jacobian(
        self, amplitudes: dict[str, Any], *args: Any
    ) -> DenseOneIndex:
        """Jacobian approximation to find coupled cluster doubles amplitudes.

        **Arguments:**

        amplitudes
             Cluster amplitudes.

        args
             All function arguments needed to calculated the vector
        """
        #
        # RCCS part
        #
        jacobian = self.unravel(super().jacobian(amplitudes, *args).array)
        jacobian_1 = jacobian["t_1"]
        #
        # Get auxiliary matrices and other intermediates
        #
        t_p = self.t_p
        govvo = self.from_cache("govvo")
        giaai = govvo.contract("abba->ab")
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        nov = self.occ_model.nacto[0] * self.occ_model.nactv[0]
        #
        # Output
        #
        out = self.lf.create_one_index(nov)

        if self.jacobian_approximation == 2:
            #
            # T_1
            #
            tmp = self.lf.create_one_index(nacto)
            giaai.contract("ab,ab->a", t_p, tmp)
            tmp.expand("a->ab", out=jacobian_1, factor=-1.0)
            tmp = self.lf.create_one_index(nactv)
            giaai.contract("ab,ab->b", t_p, tmp)
            tmp.expand("b->ab", out=jacobian_1, factor=-1.0)

        eps1 = jacobian_1.array.reshape(nov)
        out.assign(eps1, end0=nov)

        return out
