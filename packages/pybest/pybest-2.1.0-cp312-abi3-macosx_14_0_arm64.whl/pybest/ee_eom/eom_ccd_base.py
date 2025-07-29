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
"""Equation of Motion Coupled Cluster implementations of a common base class
for EOM-CCD-type methods, like

    - EOM-LCCD
    - EOM-pCCD-LCCD
    - EOM-CCD

Child class of REOMCC class.
"""

import gc
from typing import Any

import numpy as np

from pybest.auxmat import get_fock_matrix
from pybest.exceptions import ArgumentError
from pybest.linalg import (
    CholeskyLinalgFactory,
    FourIndex,
    OneIndex,
    Orbital,
    TwoIndex,
)
from pybest.log import log
from pybest.utility import unmask

from .eom_base import REOMCC


class REOMCCDBase(REOMCC):
    """Base class for various EOM-CCD methods"""

    long_name = "Equation of Motion Coupled Cluster Doubles"
    acronym = ""
    reference = "any CCD wave function"
    singles_ref = False
    pairs_ref = ""
    doubles_ref = True
    singles_ci = False
    pairs_ci = ""
    doubles_ci = True

    disconnected = True

    @property
    def dimension(self) -> int:
        """The number of unknowns (total number of excited states incl. ground
        state) for each EOM-CCD flavor. Variable used by the Davidson module.
        """
        return (
            self.occ_model.nacto[0]
            * self.occ_model.nactv[0]
            * (self.occ_model.nacto[0] * self.occ_model.nactv[0] + 1)
            // 2
            + 1
        )

    def build_full_hamiltonian(self, *args: Any) -> TwoIndex:
        """Construct full Hamiltonian matrix used in exact diagonalization.
        Not supported here.
        """
        raise NotImplementedError

    def unmask_args(self, *args: Any, **kwargs: Any) -> Any:
        #
        # t_p
        #
        if self.pairs_ref:
            t_p = unmask("t_p", *args, **kwargs)
            if t_p is None:
                raise ArgumentError("Cannot find Tp amplitudes.")
            self.checkpoint.update("t_p", t_p)
        #
        # t_2
        #
        t_2 = unmask("t_2", *args, **kwargs)
        if t_2 is None:
            raise ArgumentError("Cannot find T2 amplitudes.")
        self.checkpoint.update("t_2", t_2)
        #
        # Call base class method
        #
        return REOMCC.unmask_args(self, *args, **kwargs)

    def print_ci_vectors(self, index: int, ci_vector: np.ndarray) -> None:
        """Print information on CI vector (excitation and its coefficient).

        **Arguments:**

        index:
            (int) the composite index that corresponds to a specific excitation

        ci_vector:
            (np.array) the CI coefficient vector that contains all coefficients
            for one specific state
        """
        #
        # Remove reference state index
        #
        index_ = index - 1
        #
        # Print contribution
        #
        #
        # Get double excitation
        #
        i, a, j, b = self.get_index_d(index_)
        # Account for frozen core, occupied orbitals, and numpy index convention
        i, a, j, b = (
            i + self.occ_model.ncore[0] + 1,
            a + self.occ_model.ncore[0] + self.occ_model.nacto[0] + 1,
            j + self.occ_model.ncore[0] + 1,
            b + self.occ_model.ncore[0] + self.occ_model.nacto[0] + 1,
        )
        log(
            f"          t_iajb:  ({i:3d},{a:3d},{j:3d},{b:3d})   {ci_vector[index]: 1.5f}"
        )

    def print_weights(self, ci_vector: np.ndarray) -> None:
        """Print weights of excitations.

        **Arguments:**

        ci_vector:
            (np.array) the CI coefficient vector that contains all coefficients
            for one specific state
        """
        log(
            f"          weight(d): {np.dot(ci_vector[1:], ci_vector[1:]): 1.5f}"
        )

    def compute_h_diag(self, *args: Any) -> OneIndex:
        """Used by Davidson module for pre-conditioning.

        **Arguments:**

        args:
            required for Davidson module (not used here)
        """
        t_iajb = self.checkpoint["t_2"]
        #
        # Output objects
        #
        h_diag_d = t_iajb.new()
        #
        # Get auxiliary matrices
        #
        x_jk = self.from_cache("x_jk")
        x_bd = self.from_cache("x_bd")
        x_ijkl = self.from_cache("x_ijkl")
        # Generate diagonal copies of effective H elements
        loovv = self.from_cache("loovv")
        tmp_iaj = t_iajb.contract("abcd,acbd->abc", loovv)
        tmp_iab = t_iajb.contract("abcd,acbd->abd", loovv)
        if self.dump_cache:
            self.cache.dump("loovv")
        #
        # Doubles (h_diag_d[i,a,j,b])
        #
        # - L_ijad t_iajd
        tmp_iaj.expand("abc->abcd", h_diag_d, factor=-1.0)
        # - L_ilab t_ialb
        tmp_iab.expand("abd->abcd", h_diag_d, factor=-1.0)
        # X_jk(j,j)
        tmp = x_jk.copy_diagonal()
        tmp.expand("a->abcd", h_diag_d)
        # X_bd(b,b)
        tmp = x_bd.copy_diagonal()
        tmp.expand("b->abcd", h_diag_d)
        # - 2 X_iakc(i,a,i,a) + X_ajkc(a,i,a,i) + X_ajkc(a,j,a,j)
        x_iakc = self.from_cache("x_iakc")
        x_iaia = x_iakc.contract("abab->ab")
        if self.dump_cache:
            self.cache.dump("x_iakc")
        # - 2 X_iakc(i,a,i,a)
        x_iaia.expand("ab->abcd", h_diag_d, factor=-2.0)
        x_ajkc = self.from_cache("x_ajkc")
        x_jaja = x_ajkc.contract("abba->ba")
        if self.dump_cache:
            self.cache.dump("x_ajkc")
        # X_ajkc(a,i,a,i) + X_ajkc(a,j,a,j)
        x_jaja.expand("ab->abcd", h_diag_d)
        x_jaja.expand("cb->abcd", h_diag_d)
        # X_ijkl(i,j,i,j)
        tmp = x_ijkl.contract("abab->ab", clear=True)
        tmp.expand("ac->abcd", h_diag_d)
        # X_abcd(a,b,a,b)
        tmp = self.get_h_diag_x_acac_term()
        tmp.expand("bd->abcd", h_diag_d)

        # Add permutation as we only considered (iajb), not (jbia)
        # P^+_iajb = 1 + P(ia,jb)
        h_diag_d.iadd_transpose((2, 3, 0, 1))

        return h_diag_d

    def get_h_diag_x_acac_term(self) -> TwoIndex:
        """Calculate the diagonal H part of the X_abcd effective term.

        Returns:
            DenseTwoIndex: the X_abcd[a,b,a,b] part of the X_abcd array
        """
        if isinstance(self.lf, CholeskyLinalgFactory):
            # Get data and ranges
            t_iajb = self.checkpoint["t_2"]
            gvvvv = self.from_cache("gvvvv")
            # 0.5 <ab|ab>
            tmp = gvvvv.contract("abab->ab", factor=0.5)
            # 0.5 <kl|ab> tkalb
            goovv = self.from_cache("goovv")
            goovv.contract("abcd,acbd->cd", t_iajb, tmp, factor=0.5)
            if self.dump_cache:
                self.cache.dump("goovv")
            return tmp
        # Use effective Hamiltonian if available
        x_abcd = self.from_cache("x_abcd")
        tmp = x_abcd.contract("abab->ab")
        if self.dump_cache:
            self.cache.dump("x_abcd")
        return tmp

    def build_subspace_hamiltonian(
        self, bvector: OneIndex, hdiag: OneIndex, *args: Any
    ) -> tuple[float, FourIndex, FourIndex]:
        """Used by Davidson module to construct subspace Hamiltonian.
        Includes all terms that are similar for all EOM-CC flavors.
        The doubles contributions do not include any permutations due to
        non-equivalent lines.

        **Arguments:**

        bvector:
            (OneIndex object) contains current approximation to CI coefficients

        hdiag:
            Diagonal Hamiltonian elements required in Davidson module (not used
            here)

        args:
            Set of arguments passed by the Davidson module (not used here)
        """
        t_iajb = self.checkpoint["t_2"]
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        #
        # Get auxiliary matrices and effective Hamiltonian terms
        #
        x_jk = self.from_cache("x_jk")
        x_bd = self.from_cache("x_bd")
        x_ijkl = self.from_cache("x_ijkl")
        #
        # Calculate sigma vector (H.bvector)_kc
        #
        # doubles
        sigma_d = self.dense_lf.create_four_index(nacto, nactv, nacto, nactv)
        to_d = {"out": sigma_d, "clear": False}
        bv_d = self.dense_lf.create_four_index(nacto, nactv, nacto, nactv)
        #
        # reshape bvector
        #
        bv_d.assign_triu(bvector, begin4=1)
        bv_p = bv_d.contract("abab->ab", clear=True)
        bv_d.iadd_transpose((2, 3, 0, 1))
        self.set_seniority_0(bv_d, bv_p)
        #
        # Reference vector R_0
        #
        # X0,kc rkc
        loovv = self.from_cache("loovv")
        sum0_ = bv_d.contract("abcd,acbd", loovv)
        if self.dump_cache:
            self.cache.dump("loovv")
        #
        # All double excitations
        #
        # [5] P X_jk riakb
        bv_d.contract("abcd,ec->abed", x_jk, **to_d)
        # [4] P X_bd riajd
        bv_d.contract("abcd,ed->abce", x_bd, **to_d)
        # [7] P X_abcd ricjd
        self.get_effective_hamiltonian_term_abcd(bv_d, sigma_d)
        # [6] P X_ijkl rkalb
        x_ijkl.contract("abcd,cedf->aebf", bv_d, **to_d)
        # [8-3] P X_ajkc rkbic
        x_ajkc = self.from_cache("x_ajkc")
        x_ajkc.contract("abcd,cefd->fabe", bv_d, **to_d)
        # [8-1] P X_ajkc(aikc) rjbkc
        x_ajkc.contract("abcd,efcd->baef", bv_d, **to_d)
        if self.dump_cache:
            self.cache.dump("x_ajkc")
        # [8-1] P -2 X_iakc rjbkc
        x_iakc = self.from_cache("x_iakc")
        x_iakc.contract("abcd,efcd->abef", bv_d, **to_d, factor=-2.0)
        # [8-2] P X_iakc rkbjc
        x_iakc.contract("abcd,cefd->abfe", bv_d, **to_d)
        if self.dump_cache:
            self.cache.dump("x_iakc")
        # [9] + [10] P (X_klcdiab rjdkc + X_klcdija rlbkc)
        # [9] - L_lkdc rkcjd t_ialb -> - (jl) t_ialb
        # [10] - L_klcd rlbkc t_iajd -> - (bd) t_iajd
        loovv = self.from_cache("loovv")
        # @[9] L_lkdc rjdkc = (jl)
        tmp_jl = loovv.contract("abcd,bdec->ae", bv_d)
        # @[10] L_lkdc rlbkc = (bd)
        tmp_bd = loovv.contract("abcd,aebd->ce", bv_d)
        if self.dump_cache:
            self.cache.dump("loovv")
        # @[9] - (jl) t_ialb
        t_iajb.contract("abcd,ce->abed", tmp_jl, **to_d, factor=-1.0)
        # @[10] - (bd) t_iajd
        t_iajb.contract("abcd,de->abce", tmp_bd, **to_d, factor=-1.0)
        tmp_jl, tmp_bd = None, None

        return sum0_, sigma_d, bv_d

    def update_hamiltonian(self, mo1: TwoIndex, mo2: FourIndex) -> None:
        """Derive all auxiliary matrices. Derive all matrices that are common
        for all EOM-CCD flavours.

        **Arguments:**

        mo1, mo2
             one- and two-electron integrals to be sorted.
        """
        t_iajb = self.checkpoint["t_2"]
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        nact = self.occ_model.nact[0]
        #
        # Get ranges
        #
        ov2 = self.get_range("ov", offset=2)
        oo2 = self.get_range("oo", offset=2)
        vv2 = self.get_range("vv", offset=2)
        ov4 = self.get_range("ov", offset=4)
        oooo = self.get_range("oooo")
        ooov = self.get_range("ooov")
        oovo = self.get_range("oovo")
        oovv = self.get_range("oovv")
        ovvo = self.get_range("ovvo")
        ovov = self.get_range("ovov")
        ovvv = self.get_range("ovvv")
        #
        # Get auxiliary matrices
        # Inactive Fock matrix
        #
        fock = self.init_cache("fock", nact, nact)
        get_fock_matrix(fock, mo1, mo2, nacto)
        #
        # <oo||vv>+<oo|vv>
        # We will keep the loovv array in memory to prevent loading it from disk
        # It will be deleted once it is not used anymore. If you can do EOM-CCD,
        # storing loovv during the construction of the effective Hamiltonian
        # should not be an issue.
        # This can always be adjusted in the future by dumping/reading arrays
        loovv = self.init_cache("loovv", nacto, nacto, nactv, nactv)
        mo2.contract("abcd->abcd", loovv, factor=2.0, **oovv)
        mo2.contract("abcd->abdc", loovv, factor=-1.0, **oovv)
        # temporary matrix; will be deleted afterward (not stored in Cache)
        gooov = mo2.contract("abcd->abcd", **ooov)
        #
        # Get expensive effective Hamiltonian arrays, which include arrays of
        # dimension ovvv and vvvv.
        #
        if not isinstance(self.lf, CholeskyLinalgFactory):
            self.get_effective_hamiltonian_xvvv(fock, gooov, mo2)
        #
        # <oo||ov>+<oo|ov>
        #
        looov = self.init_cache("looov", nacto, nacto, nacto, nactv)
        looov.iadd(gooov, factor=2.0)
        mo2.contract("abcd->abdc", looov, factor=-1.0, **oovo)
        #
        # (2) X_ik
        #
        x_ik = self.init_cache("x_ik", nacto, nacto)
        # - F_ki
        x_ik.iadd(fock, -1.0, **oo2)
        # - L_klcd ticld
        t_iajb.contract("abcd,aebd->ce", loovv, x_ik, factor=-1.0)
        #
        # (3) X_ac
        #
        x_ac = self.init_cache("x_ac", nactv, nactv)
        # F_ac
        x_ac.iadd(fock, 1.0, **vv2)
        # - L_klcd tkald
        t_iajb.contract("abcd,acbe->de", loovv, x_ac, factor=-1.0)
        #
        # (1) X_iakc
        #
        x1_iakc = self.init_cache("x1_iakc", nacto, nactv, nacto, nactv)
        # L_icak
        mo2.contract("abcd->acdb", x1_iakc, factor=2.0, **ovvo)
        mo2.contract("abcd->adcb", x1_iakc, factor=-1.0, **ovov)
        # L_klcd (2t_iald-tidla)
        loovv.contract("abcd,efbd->efac", t_iajb, x1_iakc, factor=2.0)
        loovv.contract("abcd,edbf->efac", t_iajb, x1_iakc, factor=-1.0)
        if self.dump_cache:
            self.cache.dump("x1_iakc")
        #
        # (6) X_ilkc
        x_ilkc = self.init_cache("x_ilkc", nacto, nacto, nacto, nactv)
        # - L_lkic
        looov.contract("abcd->cabd", x_ilkc, factor=-1.0)
        # Distinguish between linearized and nonlinearized CC
        if not self.disconnected:
            _ = self.init_cache("x_ilkc_linear", alloc=x_ilkc.copy)
        #
        # (4/5) X_kc
        #
        x_kc = self.init_cache("x_kc", nacto, nactv)
        # F_kc
        x_kc.iadd(fock, 1.0, **ov2)
        #
        # (11) X_jk
        #
        x_jk = self.init_cache("x_jk", nacto, nacto)
        # (1) - F_jk
        x_jk.iadd(fock, -1.0, **oo2)
        # (4) - L_klcd tjcld
        loovv.contract("abcd,ecbd->ea", t_iajb, x_jk, factor=-1.0)
        #
        # (12) X_bd
        #
        x_bd = self.init_cache("x_bd", nactv, nactv)
        # (1) F_bc
        x_bd.iadd(fock, 1.0, **vv2)
        # (4) - L_klcd tkclb
        loovv.contract("abcd,acbe->ed", t_iajb, x_bd, factor=-1.0)
        #
        # (14) X_iakc
        #
        x_iakc = self.init_cache("x_iakc", nacto, nactv, nacto, nactv)
        # (1) - <ic|ak>
        mo2.contract("abcd->acdb", x_iakc, factor=-1.0, **ovvo)
        # (4) - L_klcd tiald
        loovv.contract("abcd,efbd->efac", t_iajb, x_iakc, factor=-1.0)
        # loovv not needed anymore
        if self.dump_cache:
            self.cache.dump("loovv")
        # temporary matrix needed for some contractions
        goovv = self.init_cache("goovv", nacto, nacto, nactv, nactv)
        mo2.contract("abcd->abcd", goovv, **oovv)
        # (4) <kl|cd> tidla
        goovv.contract("abcd,edbf->efac", t_iajb, x_iakc)
        if self.dump_cache:
            self.cache.dump("x_iakc")
        #
        # (15) X_ajkc
        #
        x_ajkc = self.init_cache("x_ajkc", nactv, nacto, nacto, nactv)
        # (1) - <ka|jc>
        mo2.contract("abcd->bcad", x_ajkc, factor=-1.0, **ovov)
        # (4) <lk|cd> tjdla
        goovv.contract("abcd,ecbf->fead", t_iajb, x_ajkc)
        if self.dump_cache:
            self.cache.dump("x_ajkc")
        #
        # (17) X_ijkl
        #
        x_ijkl = self.init_cache("x_ijkl", nacto, nacto, nacto, nacto)
        # (1) 0.5 <ij|kl>
        mo2.contract("abcd->abcd", x_ijkl, factor=0.5, **oooo)
        # (3) 0.5 <kl|cd> ticjd
        goovv.contract("abcd,ecfd->efab", t_iajb, x_ijkl, factor=0.5)
        if self.dump_cache:
            self.cache.dump("goovv")
        #
        # (9) X_ijbl
        #
        x_ijbl = self.init_cache("x_ijbl", nacto, nacto, nactv, nacto)
        # (1) - <ij|lb>
        mo2.contract("abcd->abdc", x_ijbl, factor=-1.0, **ooov)
        # (4) - F_lc t_icjb
        t_iajb.contract("abcd,eb->acde", fock, x_ijbl, factor=-1.0, **ov4)
        # (6) - <lb|cd> ticjd
        mo2.contract("abcd,ecfd->efba", t_iajb, x_ijbl, factor=-1.0, **ovvv)
        # (5) - L_lkic t_jbkc
        looov.contract("abcd,efbd->cefa", t_iajb, x_ijbl, factor=-1.0)
        # (5) <ik|lc> tjckb
        gooov.contract("abcd,edbf->aefc", t_iajb, x_ijbl)
        # (5) <jl|kc> tickb
        gooov.contract("abcd,edcf->eafb", t_iajb, x_ijbl)
        # Remove from Cache
        del gooov

        gc.collect()

    def get_effective_hamiltonian_xvvv(
        self, fock: TwoIndex, gooov: FourIndex, mo2: Orbital
    ) -> None:
        """Generate all expensive effective Hamiltonian terms.
        This function is called if we work in the DenseLinalgFactory picture.
        All effective Hamiltonian elements of size xvvv are calculated here,
        where x is either occupied (ov^3) or virtual (v^4).

        Args:
            fock (TwoIndex): The inactive Fock matrix in the MO basis
            gooov (FourIndex): A slice of the two-electron integrals in the MO basis
            mo2 (FourIndex): The two-electron integrals in the MO basis
        """
        t_iajb = self.checkpoint["t_2"]
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        #
        # Get ranges
        #
        ov4 = self.get_range("ov", offset=4)
        oovv = self.get_range("oovv")
        ovvv = self.get_range("ovvv")
        vvvv = self.get_range("vvvv")
        # Most expensive operation. Do first to have largest amount of memory
        # available
        # X_abcd
        x_abcd = self.init_cache("x_abcd", nactv, nactv, nactv, nactv)
        # 0.5 <ab|cd>
        mo2.contract("abcd->abcd", x_abcd, factor=0.5, **vvvv)
        # 0.5 <kl|cd> tkalb
        mo2.contract("abcd,aebf->efcd", t_iajb, x_abcd, factor=0.5, **oovv)
        if self.dump_cache:
            self.cache.dump("x_abcd")
        #
        # lovvv = <ov||vv>+<ov|vv>
        # Temporary array; only used to construct effective Hamiltonian
        lovvv = mo2.contract("abcd->abcd", factor=2.0, **ovvv)
        mo2.contract("abcd->abdc", lovvv, factor=-1.0, **ovvv)
        #
        # (7) X_adkc
        #
        x_adkc = self.init_cache("x_adkc", nactv, nactv, nacto, nactv)
        # L_kacd
        lovvv.contract("abcd->bdac", x_adkc)
        # Distinguish between linearized and nonlinearized CC
        if not self.disconnected:
            # x_adkc_linear = L_kacd = x_adkc
            _ = self.init_cache("x_adkc_linear", alloc=x_adkc.copy)
            if self.dump_cache:
                self.cache.dump("x_adkc_linear")
        if self.dump_cache:
            self.cache.dump("x_adkc")
        #
        # (8) X_iabd
        #
        x_iabd = self.init_cache("x_iabd", nacto, nactv, nactv, nactv)
        # (1) <id|ab>
        mo2.contract("abcd->acdb", x_iabd, **ovvv)
        # (4) - F_ld t_ialb
        t_iajb.contract("abcd,ce->abde", fock, x_iabd, factor=-1.0, **ov4)
        # (5) L_kbcd t_iakc
        lovvv.contract("abcd,efac->efbd", t_iajb, x_iabd)
        # remove temporary array
        del lovvv
        # (5) - <kb|cd> ticka
        mo2.contract("abcd,ecaf->efbd", t_iajb, x_iabd, factor=-1.0, **ovvv)
        # (5) - <ka|dc> tickb
        mo2.contract("abcd,edaf->ebfc", t_iajb, x_iabd, factor=-1.0, **ovvv)
        # (6) <id|lk> tlakb = <ik|ld> tlakb
        gooov.contract("abcd,cebf->aefd", t_iajb, x_iabd)
        gc.collect()

    #
    # Expensive effective Hamiltonian terms
    #

    def get_effective_hamiltonian_term_abcd(
        self, bv_d: FourIndex, sigma: FourIndex
    ) -> None:
        """Compute effective Hamiltonian term involving a vvvv block

        **Arguments:**

        :bv_d: (DenseFourIndex) the current approximation to the CI doubles
               coefficient

        :sigma: (DenseFourIndex) the output sigma vector
        """
        to_d = {"out": sigma, "clear": False}
        if isinstance(self.lf, CholeskyLinalgFactory):
            # get ranges and data
            t_iajb = self.checkpoint["t_2"]
            gnnvv = self.from_cache("gnnvv")
            oooo = self.get_range("oooo")
            ovov = self.get_range("ovov")
            # (16) X_abcd ricjd
            # Creating expensive intermediate of size o^2a^2 (occupied/active)
            # to reduce the number of operations
            # tmp[i,act,j,act] = <act act|cd> ricjd
            tmp = gnnvv.contract("abcd,ecfd->eafb", bv_d)
            # 0.5 <ab|cd> ricjd -> 0.5 tmp[i,a,j,b]
            tmp.contract("abcd->abcd", **to_d, factor=0.5, **ovov)
            # 0.5 <kl|cd> tkalb ricjd -> 0.5 tmp[i,k,j,l] tkalb
            tmp.contract("abcd,bedf->aecf", t_iajb, **to_d, factor=0.5, **oooo)
        else:
            x_abcd = self.from_cache("x_abcd")
            bv_d.contract("abcd,efbd->aecf", x_abcd, **to_d)
            if self.dump_cache:
                self.cache.dump("x_abcd")
