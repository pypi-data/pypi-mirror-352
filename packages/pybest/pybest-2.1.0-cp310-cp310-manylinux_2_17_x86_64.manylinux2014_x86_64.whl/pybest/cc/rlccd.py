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
"""Restricted Linearized Coupled Cluster Doubles Class with a Single Slater
Determinant reference function (RLCCD) and a pCCD reference function (RpCCDLCCD).

   Variables used in this module:
    :nocc:      number of occupied orbitals in the principle configuration
    :nvirt:     number of virtual orbitals in the principle configuration
    :ncore:     number of frozen core orbitals in the principle configuration
    :nbasis:    total number of basis functions
    :energy:    the LCC energy, dictionary that contains different
                contributions
    :t_2:       the optimized amplitudes

    Indexing convention:
    :o:        matrix block corresponding to occupied orbitals of principle
               configuration
    :v:        matrix block corresponding to virtual orbitals of principle
               configuration

    EXAMPLE APPLICATION

    lcc_solver = RLCCD(linalg_factory, occupation_model)
    lcc_result = lcc_solver(
        AO_one_body_ham, AO_two_body_ham, hf_io_data_container
    )

    or

    pccd_solver = RpCCD(linalg_factory, occupation_model)
    pccd_result - pccd_solver(
        AO_one_body_ham, AO_two_body_ham, hf_io_data_container
    )

    lcc_solver = RpCCDLCCD(linalg_factory, occupation_model)
    lcc_result = lcc_solver(
        AO_one_body_ham, AO_two_body_ham, pccd_result
    )
"""

# Detailed changelog:
# 03/2025:
# This file has been modified by Somayeh Ahmadkhani and Lena Szczuczko
from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

from pybest.cc import RCCD
from pybest.cc.rcc import RCC
from pybest.cc.rlccd_base import RLCCDBase
from pybest.exceptions import ArgumentError
from pybest.helperclass import PropertyHelper
from pybest.linalg import (
    DenseFourIndex,
    DenseOneIndex,
    DenseOrbital,
    DenseTwoIndex,
)
from pybest.linalg.base import NIndexObject
from pybest.log import log, timer
from pybest.utility import unmask

from .rdm_lcc import (
    compute_1dm_pccdlccd,
    compute_2dm_pccdlccd,
    compute_3dm_pccdlccd,
    compute_4dm_pccdlccd,
)


class RLCCD(RLCCDBase, RCCD):
    """Restricted Linearized Coupled Cluster Doubles"""

    acronym = "RLCCD"
    long_name = "Restricted Linearized Coupled Cluster Doubles"
    cluster_operator = "T2"


class RHFLCCD(RLCCDBase, RCCD):
    """Restricted Linearized Coupled Cluster Doubles. Similar to RLCCD class.
    Allows for backwards compability to older versions.
    """

    acronym = "RLCCD"
    long_name = "Restricted Linearized Coupled Cluster Doubles"
    cluster_operator = "T2"


class RpCCDLCCD(RLCCDBase, RCCD):
    """Restricted pair Coupled Cluster Doubles with Linearized Coupled Cluster
    Doubles
    """

    acronym = "RpCCDLCCD"
    long_name = "Restricted pair Coupled Cluster Doubles Linearized Coupled Cluster Doubles"
    cluster_operator = "T2 - Tp"

    def get_ndm(self, select: NIndexObject) -> NIndexObject:
        if select not in self.cache:
            raise ArgumentError(f"Density matrix {select} not found.")
        return self.cache.load(select)

    dm_1_pccd_pp = PropertyHelper(
        get_ndm, "dm_1_pccd_pp", "Diagonal 1-RDM for alpha/beta spin for pCCD"
    )
    dm_2_pccd_ppqq = PropertyHelper(
        get_ndm, "dm_2_pccd_ppqq", "2-RDM for alpha/beta spin for pCCD"
    )
    dm_2_pccd_pqpq = PropertyHelper(
        get_ndm, "dm_2_pccd_pqpq", "2-RDM for alpha/beta spin for pCCD"
    )

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
    def iodata(self):
        """Container for output data"""
        iodata = super().iodata
        iodata.update({"t_p": self.t_p})
        if self._converged_l:
            iodata["dm_1"].update({"pccd_pp": self.dm_1_pccd_pp})
            iodata["dm_2"].update({"pccd_ppqq": self.dm_2_pccd_ppqq})
            iodata["dm_2"].update({"pccd_pqpq": self.dm_2_pccd_pqpq})
        return iodata

    def read_input(
        self, *args: Any, **kwargs: dict[str, Any]
    ) -> tuple[DenseTwoIndex, DenseFourIndex, DenseOrbital]:
        """Looks for Hamiltonian terms, orbitals, and overlap."""
        #
        # Call parent class method
        #
        one_mo, two_mo, orb = RLCCDBase.read_input(self, *args, **kwargs)
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
        log(f"{'Doubles':24} {self.energy['e_corr_d']:14.8f} a.u.")
        log(f"{'Seniority 2':24} {self.energy['e_corr_s4']:14.8f} a.u.")
        log(f"{'Seniority 4':24} {self.energy['e_corr_s2']:14.8f} a.u.")

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
        RLCCDBase.update_hamiltonian(self, mo1, mo2)
        #
        # Clean up (should get deleted anyways)
        #
        mo2.__del__()

    def set_dm(self, *args: Any) -> None:
        """Determine all supported RDMs and put them into the cache."""
        #
        # Call parent class
        #
        RLCCDBase.set_dm(self, *args)
        #
        # Update RDMs of pCCD
        #
        options = {"tags": "d"}
        nacto = self.occ_model.nacto[0]
        nact = self.occ_model.nact[0]
        # 1-RDM
        dm_1_pp = self.init_cache("dm_1_pccd_pp", nact, **options)
        dm_1_pp.assign(unmask("dm_1", *args))
        dm_1_pp.iadd(-1.0, end0=nacto)
        # 2-RDM
        dm_2_ppqq = self.init_cache("dm_2_pccd_ppqq", nact, nact, **options)
        dm_2_ppqq.assign(unmask("dm_2", *args)["ppqq"])
        dm_2_pqpq = self.init_cache("dm_2_pccd_pqpq", nact, nact, **options)
        dm_2_pqpq.assign(unmask("dm_2", *args)["pqpq"])
        dm_2_pqpq.iadd(-1.0, end0=nacto, end1=nacto)

    def update_ndm(
        self, select: str, option: str, *args: Any, **kwargs: dict[str, Any]
    ) -> None:
        """Wrapper function that is used to update all supported N-particle
        RDMs.

        **Arguments:**

        select:
            (str) name of DM stored in the cache

        option:
            (str) specific block of DM to be calculated

        args:
            tuple of (int) indicating the dimensions of the DM to be calculated.
            Used for initializing the cache instance.

        **Keyword arguments:**
            passed to the utility functions. Currenlty not used here.

        """
        options = {"tags": "d"}
        cached_ndm = self.init_cache(select, *args, **options)
        method = {
            "dm_1": compute_1dm_pccdlccd,
            "dm_2": compute_2dm_pccdlccd,
            "dm_3": compute_3dm_pccdlccd,
            "dm_4": compute_4dm_pccdlccd,
        }
        for key in method:
            if key in select:
                method_ = method[key]
        method_(
            option,
            cached_ndm,
            self.l_amplitudes,
            self.amplitudes,
            1.0,
            *args,
            **kwargs,
            **{"t_p": self.t_p},
        )

    def generate_guess(self, **kwargs: dict[str, Any]) -> Any:
        """Generates initial guess for amplitudes and fills it with 0."""
        initguess = RCC.generate_guess(self, **kwargs)
        for item in initguess.values():
            if isinstance(item, DenseFourIndex):
                RCC.set_seniority_0(self, item, 0.0)
        return initguess

    @timer.with_section("RfpLCCD: Hamiltonian")
    def update_hamiltonian(
        self, mo1: DenseTwoIndex, mo2: DenseFourIndex
    ) -> None:
        #
        # Get ranges
        #
        oov = self.get_range("oov")
        vvo = self.get_range("vvo")
        vvv = self.get_range("vvv")
        ooo = self.get_range("ooo")
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        nact = self.occ_model.nact[0]
        t_p = self.t_p
        #
        # pCCD reference function:
        #
        # use 3-index intermediate (will be used several times)
        # This also works with Cholesky
        #
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
        # oc_jbc = sum_m <mm|bc> c_jm^bc
        #
        tmp = self.lf.create_two_index(nactv, nactv)
        ocjbc = self.init_cache("ocjbc", nacto, nactv, nactv)
        gpqrr.contract("abc,cb->ab", t_p, tmp, clear=True, **vvo)
        t_p.contract("ab,bc->abc", tmp, ocjbc)
        # P_jm
        gpqrr.contract("abc,ca->ab", t_p, tmp, clear=True, **vvo)
        t_p.contract("ac,bc->abc", tmp, ocjbc)
        #
        # vc_jkb = sum_d <dd|jk> c_jk^bd
        #
        vcjkb = self.init_cache("vcjkb", nacto, nacto, nactv)
        # tmp storage
        tmp = self.lf.create_two_index(nacto, nacto)
        gpqrr.contract("abc,bc->ab", t_p, tmp, clear=True, **oov)
        tmp.contract("ab,ac->abc", t_p, vcjkb)
        # P_jm
        gpqrr.contract("abc,ac->ab", t_p, tmp, clear=True, **oov)
        tmp.contract("ab,bc->abc", t_p, vcjkb)
        #
        # vc_jbc = sum_d <bc|dd> c_j^d
        #
        vcjbc = self.init_cache("vcjbc", nacto, nactv, nactv)
        gpqrr.contract("abc,dc->dab", t_p, vcjbc, **vvv)
        #
        # oc_jkb = sum_m <mm|jk> c_m^b
        #
        ocjkb = self.init_cache("ocjkb", nacto, nacto, nactv)
        gpqrr.contract("abc,cd->abd", t_p, ocjkb, **ooo)
        #
        # vc_jkl = sum_d <jk|dd> c_l^d
        #
        vcjkl = self.init_cache("vcjkl", nacto, nacto, nacto)
        gpqrr.contract("abc,dc->abd", t_p, vcjkl, **oov)
        #
        # oc_abc = sum_m <bc|mm> c_m^a
        #
        ocabc = self.init_cache("ocabc", nactv, nactv, nactv)
        gpqrr.contract("abc,cd->dab", t_p, ocabc, **vvo)

        if self.lambda_equations:
            gpqrr_ = self.init_cache("gpqrr", nact, nact, nact)
            gpqrr_.assign(gpqrr)
        gpqrr.__del__()

    @timer.with_section("RfpLCCD: VectFct")
    def vfunction(
        self, vector: NDArray[np.float64]
    ) -> NDArray[np.float64] | DenseOneIndex:
        """Shorter version of residual vector to accelerate solving."""
        amplitudes = self.unravel(vector)
        #
        # RLCCD part
        #
        residual = RLCCDBase.cc_residual_vector(self, amplitudes)
        #
        # Coupling to pCCD reference
        #
        residual = self.cc_residual_vector(amplitudes, residual)
        #
        # Delete electron pair residuals
        #
        RCC.set_seniority_0(self, residual["out_d"], 0.0)
        return self.ravel(residual)

    def cc_residual_vector(
        self, amplitudes: dict[str, Any], output: Any | None = None
    ) -> Any:
        """Residual vector of Coupled Cluster equations. Needs to be zero.

        Arguments:
            amplitudes : numpy.ndarray
                vector containing double cluster amplitudes.

        Abbreviations:

        * o - number of active occupied orbitals
        * v - number of active virtual orbitals
        * t_2 - current solution for CC amplitudes
        * out_d - vector function
        """
        t_2 = amplitudes["t_2"]
        t_p = self.t_p
        #
        # Get ranges
        #
        oo2 = self.get_range("oo", offset=2)
        vv2 = self.get_range("vv", offset=2)
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        #
        # Get auxiliary matrices
        #
        fock = self.from_cache("fock")
        vcij = self.from_cache("vcij")
        ocab = self.from_cache("ocab")
        ocjbc = self.from_cache("ocjbc")
        vcjkb = self.from_cache("vcjkb")
        vcjbc = self.from_cache("vcjbc")
        ocjkb = self.from_cache("ocjkb")
        vcjkl = self.from_cache("vcjkl")
        ocabc = self.from_cache("ocabc")
        govov = self.from_cache("govov")
        #
        # doubles
        #
        out_d = output["out_d"]
        out_d.iscale(0.5)
        to_d = {"out": out_d, "clear": False}
        #
        # temporary storage
        #
        t_ovv = self.lf.create_three_index(nacto, nactv, nactv)
        t_oov = self.lf.create_three_index(nacto, nacto, nactv)
        t_vv = self.lf.create_two_index(nactv, nactv)
        t_oo = self.lf.create_two_index(nacto, nacto)
        to_oo = {"out": t_oo}
        to_vv = {"out": t_vv}
        do_c = {"clear": True}

        # (d-d8-1):
        # NOTE: slowest contraction
        # sum_kc t_iakc L_kjcb c_jb
        # (iajb, cjb)
        # jcbk iakc
        goovv = self.from_cache("goovv")
        tmp = goovv.contract("abcd,efbd->efac", t_2)
        # (iajb, cjb)
        tmp.contract("abcd,cd->abcd", t_p, **to_d, factor=2.0)
        tmp.__del__()
        # jbck iakc
        # NOTE: current memory peak in tensor contraction
        # NOTE: slow contraction
        govvo = self.from_cache("govvo")
        tmp = govvo.contract("abcd,efdc->efab", t_2)
        tmp.contract("abcd,cd->abcd", t_p, **to_d, factor=-1.0)
        tmp.__del__()
        # (d-d8-3)
        # NOTE: second slowest contraction
        # sum_kc t_kajc g_ikcb c_ib
        # (ibaj,ib)
        # NOTE: current memory peak in tensor contraction
        # NOTE: slow contraction
        tmp = govvo.contract("abcd,defc->aefb", t_2)
        tmp.contract("abcd,ad->abcd", t_p, **to_d)
        tmp.__del__()
        # part of (d-d8-2)
        # NOTE: second slowest contraction
        # sum_kc t_kaic g_jkcb c_jb
        # (iajb,jb)
        # NOTE: current memory peak in tensor contraction
        # NOTE: slow contraction
        tmp = govvo.contract("abcd,ecdf->efab", t_2)
        tmp.contract("abcd,cd->abcd", t_p, **to_d)
        tmp.__del__()
        #
        # (d-d9)
        # c_iajb <ib|aj>
        # (iajb)
        # NOTE: current memory peak in tensor contraction
        tmp = govvo.contract("abcd,ac->acdb", t_p)
        tmp.contract("abcd,cd->abcd", t_p, **to_d, factor=0.5)
        tmp.__del__()
        tmp = govvo.contract("abcd,ab->acdb", t_p)
        tmp.contract("abcd,cb->abcd", t_p, **to_d, factor=0.5)
        tmp.__del__()
        #
        # (d-d7)
        # c_jb <ja||bi>
        #
        govvo.contract("abcd,db->acdb", t_p, **to_d)
        govov.contract("abcd,cb->adcb", t_p, **to_d, factor=-1.0)
        # (d-d14)
        # delta_ij [ sum_klc t_lakc L_lkbc c_ib ]
        # (ab,ib)
        # lcbk lakc
        govvo.contract("abcd,aedb->ec", t_2, **to_vv, **do_c)
        t_p.contract("ac,bc->abc", t_vv, t_ovv, factor=-2.0)
        # lbck lakc
        govvo.contract("abcd,aedc->eb", t_2, **to_vv, **do_c)
        t_p.contract("ac,bc->abc", t_vv, t_ovv)
        # (d-d11)
        # delta_ab [ sum_kcd t_idkc L_jkdc c_ja ]
        # (ij,ja)
        # jcdk idkc
        govvo.contract("abcd,ecdb->ea", t_2, **to_oo, **do_c)
        t_oo.contract("ab,bc->abc", t_p, t_oov, factor=-2.0)
        # jdck idkc
        govvo.contract("abcd,ebdc->ea", t_2, **to_oo, **do_c)
        if self.dump_cache:
            self.cache.dump("govvo")
        # (d-d8-2)
        # sum_kc t_kaic g_jkbc c_jb -> (jkbc,kaic) -> (ikac,kbjc)
        # (iajb,jb) -> (iajb,ia)
        goovv = self.from_cache("goovv")
        tmp = goovv.contract("abcd,befd->acfe", t_2)
        tmp.contract("abcd,ab->abcd", t_p, **to_d, factor=-1.0)
        tmp.__del__()
        #
        # -c_ib <ia|jb>
        #
        govov.contract("abcd,ab->adcb", t_p, **to_d, factor=-1.0)
        #
        # (d-d2-2)
        # delta_ij [ c_jb F_ab ]
        t_p.contract("ac,bc->abc", fock, t_ovv, **vv2)
        # (d-d16)
        # delta_ij [ oc_jbc ]
        # (iba) = (iab)
        t_ovv.iadd(ocjbc, -0.5)
        # (d-d5-2)
        # delta_ij [ vc_jbc ]
        # (iab)
        t_ovv.iadd(vcjbc, 0.5)
        # (d-d3-2)
        # delta_ac [ c_ia F_ij ]
        #
        t_p.contract("ab,ac->acb", fock, t_oov, factor=-1.0, **oo2)
        # (d-d13)
        # delta_ab [ vc_jkb ]
        # (ija)
        t_oov.iadd(vcjkb, -0.5)
        # (d-d4-2)
        # delta_bc [ oc_jkb ]
        # (ija)
        t_oov.iadd(ocjkb, 0.5)
        # (d-d12)
        # sum_k t_iakb*vc_ik
        # (kj)
        t_2.contract("abcd,ce->abed", vcij, **to_d, factor=-1.0)
        # (d-d15)
        # sum_c t_iajc oc_ca
        # (bc)
        t_2.contract("abcd,ed->abce", ocab, **to_d, factor=-1.0)
        # (d-d18)
        # delta_ij [ sum_kl t_kalb vc_jkl ]
        # (kli, kalb)
        t_2.contract("abcd,ace->ebd", vcjkl, t_ovv, factor=0.5)
        # (d-d17)
        # delta_ab [ sum_cd t_icjd vc_abc ]
        # (acd, ticjd)
        t_2.contract("abcd,ebd->ace", ocabc, t_oov, factor=0.5)
        # clear storage
        t_2.__del__()
        t_oo.contract("ab,bc->abc", t_p, t_oov)

        t_ovv.expand("abc->abac", out_d)
        t_oov.expand("abc->acbc", out_d)
        #
        # Add permutation
        #
        out_d.iadd_transpose((2, 3, 0, 1))
        #
        # Freeze selected doubles amplitudes
        #
        for row in self.freeze:
            out_d.set_element(row[0], row[1], row[2], row[3], 0.0, symmetry=1)
            out_d.set_element(row[2], row[3], row[0], row[1], 0.0, symmetry=1)

        return {"out_d": out_d}

    @timer.with_section("RfpLCCD: Jacobian")
    def jacobian(self, amplitudes: dict[str, Any], *args: Any) -> Any:
        """Jacobian approximation to find coupled cluster doubles amplitudes.

        **Arguments:**

        amplitudes
             Cluster amplitudes.

        args
             All function arguments needed to calculated the vector
        """
        #
        # RLCCD part
        #
        return RLCCDBase.jacobian(self, amplitudes, *args)

    @timer.with_section("RfpLCCD: L VecFct")
    def vfunction_l(
        self, vector: NDArray[np.float64]
    ) -> NDArray[np.float64] | DenseOneIndex:
        """Shorter version of residual vector to accelerate solving."""
        amplitudes = self.unravel(vector)
        #
        # RLCCD part
        #
        residual = RLCCDBase.l_residual_vector(self, amplitudes)
        #
        # Coupling to pCCD reference
        #
        residual = self.l_residual_vector(amplitudes, residual)
        #
        # Delete electron pair residuals
        #
        RCC.set_seniority_0(self, residual["out_d"], 0.0)
        return self.ravel(residual)

    def l_residual_vector(
        self, amplitudes: dict[str, Any], output: Any = None
    ) -> Any:
        """Residual vector of Lambda equations. Needs to be zero.

        Arguments:
            amplitudes : numpy.ndarray
                vector containing double Lambda amplitudes.

        Abbreviations:

        * o - number of active occupied orbitals
        * v - number of active virtual orbitals
        * l_1, l_1 - current solution for Lambda amplitudes
        * out_s, out_d - vector function
        * c_kc - t_p[k,c]
        """
        l_2 = amplitudes["t_2"]
        t_p = self.t_p
        #
        # Get ranges
        #
        vvo = self.get_range("vvo")
        oov = self.get_range("oov")
        #
        # Get auxiliary matrices
        #
        gpqrr = self.from_cache("gpqrr")
        #
        # Lambda_iajb
        #
        out_d = output["out_d"]
        to_d = {"out": out_d, "clear": False}
        #
        # (12) 0.5 P [ 0.5 <ij|cc> c_kc l_kakc ] -> tmp[i,j,k] l_kakc
        # NOTE: 0.5 P added at the end
        tmp = gpqrr.contract("abc,dc->abd", t_p, out=None, **oov)
        l_2.contract("abac,efa->ebfc", tmp, out_d, factor=0.5)
        #
        # (13) 0.5 P [ 0.5 <ab|kk> c_kc l_icjc ] -> <ab|kk> tmp[i,j,k]
        #
        tmp = l_2.contract("abcb,db->acd", t_p, out=None)
        gpqrr.contract("abc,efc->eafb", tmp, **to_d, factor=0.5, **vvo)
        #
        # (14) 0.5 P [ - <ac|kk> c_kc l_icjb ] -> tmp[a,c] l_icjb
        #
        tmp = gpqrr.contract("abc,cb->ab", t_p, out=None, factor=-1.0, **vvo)
        l_2.contract("abcd,eb->aecd", tmp, **to_d)
        #
        # (15) 0.5 P [ - <ik|cc> c_kc l_kajb ] -> tmp[i,k] l_kajb
        #
        tmp = gpqrr.contract("abc,bc->ab", t_p, out=None, factor=-1.0, **oov)
        l_2.contract("abcd,ea->ebcd", tmp, **to_d)
        #
        # (16) 0.5 P [ ( -2 <ij|cb> + <ij|bc> ) c_kc l_kakc ]
        # c_kc l_kakc -> tmp[a,c]
        tmp = l_2.contract("abac,ac->bc", t_p, out=None, factor=1.0)
        govvo = self.from_cache("govvo")
        # ( -2 <ib|cj> + <ic|bj> ) tmp[a,c]
        govvo.contract("abcd,ec->aedb", tmp, **to_d, factor=-2.0)
        govvo.contract("abcd,eb->aedc", tmp, **to_d)
        #
        # (17) 0.5 P [ ( -2 <jk|ba> + <kj|ba> ) c_kc l_ickc ]
        # c_kc l_ickc -> tmp[i,k]
        tmp = l_2.contract("abcb,cb->ac", t_p, out=None)
        # ( -2 <ja|bk> + <jb|ak> ) tmp[i,k]
        govvo.contract("abcd,ed->ebac", tmp, **to_d, factor=-2.0)
        govvo.contract("abcd,ed->ecab", tmp, **to_d)
        #
        # (18) 0.5 P [ <ja|ck> c_kc l_ickb ]
        # <ja|ck> c_kc -> tmp[j,a,k,c]
        tmp = govvo.contract("abcd,dc->abdc", t_p, out=None)
        # tmp[j,a,k,c] l_ickb
        l_2.contract("abcd,efcb->afed", tmp, **to_d)
        #
        # (19) 0.5 P [ ( - <jc|ak> + <ja|ck> ) c_kc l_ibkc ]
        # - <jc|ak> c_kc -> tmp[j,a,k,c]
        tmp = govvo.contract("abcd,db->acdb", t_p, out=None, factor=-1.0)
        # <ja|ck> c_kc -> tmp[j,a,k,c]
        govvo.contract("abcd,dc->abdc", t_p, tmp)
        # tmp[j,a,k,c] l_ibkc
        l_2.contract("abcd,efcd->ebaf", tmp, **to_d)
        #
        # (20) 0.5 P [ ( 2 <jk|bc> - <jb|ck> ) c_kc l_iakc ]
        # ( 2 <jc|bk> - <jb|ck> ) c_kc -> tmp[j,b,k,c]
        tmp = govvo.contract("abcd,db->acdb", t_p, out=None, factor=2.0)
        govvo.contract("abcd,dc->abdc", t_p, tmp, factor=-1.0)
        # tmp[j,b,k,c] l_iakc
        l_2.contract("abcd,efcd->abef", tmp, **to_d)
        if self.dump_cache:
            self.cache.dump("govvo")

        del tmp
        #
        # Add permutation
        #
        out_d.iadd_transpose((2, 3, 0, 1))
        out_d.iscale(0.5)
        #
        # Freeze selected doubles amplitudes
        #
        for row in self.freeze:
            out_d.set_element(row[0], row[1], row[2], row[3], 0.0, symmetry=1)
            out_d.set_element(row[2], row[3], row[0], row[1], 0.0, symmetry=1)

        return {"out_d": out_d}


class RfpLCCD(RpCCDLCCD):
    """Restricted frozen-pair Linearized Coupled Cluster Doubles"""

    acronym = "RfpLCCD"
    long_name = "Restricted frozen-pair Linearized Coupled Cluster Doubles"
    cluster_operator = "T2 - Tp"
