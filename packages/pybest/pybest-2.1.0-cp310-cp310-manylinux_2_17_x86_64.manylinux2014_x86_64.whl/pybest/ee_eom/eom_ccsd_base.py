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
for EOM-CCSD-type methods, like

    - EOM-LCCSD
    - EOM-pCCD-LCCSD
    - EOM-CCSD

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
    TwoIndex,
)
from pybest.log import log
from pybest.utility import unmask

from .eom_base import REOMCC


class REOMCCSDBase(REOMCC):
    """Base class for various EOM-CCSD methods"""

    long_name = "Equation of Motion Coupled Cluster Singles Doubles"
    acronym = ""
    reference = "any CCSD wave function"
    singles_ref = True
    pairs_ref = ""
    doubles_ref = True
    singles_ci = True
    pairs_ci = ""
    doubles_ci = True

    disconnected = True

    @property
    def dimension(self) -> int:
        """The number of unknowns (total number of excited states incl. ground
        state) for each EOM-CC flavor. Variable used by the Davidson module.
        """
        return (
            self.occ_model.nacto[0]
            * self.occ_model.nactv[0]
            * (self.occ_model.nacto[0] * self.occ_model.nactv[0] + 1)
            // 2
            + self.occ_model.nacto[0] * self.occ_model.nactv[0]
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
        # t_1
        #
        t_1 = unmask("t_1", *args, **kwargs)
        if t_1 is None:
            raise ArgumentError("Cannot find T1 amplitudes.")
        self.checkpoint.update("t_1", t_1)
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
        # Either single or double excitation
        #
        doubles = (
            index_ - self.occ_model.nacto[0] * self.occ_model.nactv[0] >= 0
        )
        #
        # Print contribution
        #
        if doubles:
            #
            # Shift by single excitations
            #
            index_ -= self.occ_model.nacto[0] * self.occ_model.nactv[0]
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
        else:
            #
            # Get single excitation
            #
            i, a = self.get_index_s(index_)
            # Account for frozen core, occupied orbitals, and numpy index convention
            i, a = (
                i + self.occ_model.ncore[0] + 1,
                a + self.occ_model.ncore[0] + self.occ_model.nacto[0] + 1,
            )
            log(
                f"            t_ia:          ({i:3d},{a:3d})   {ci_vector[index]: 1.5f}"
            )

    def print_weights(self, ci_vector: np.ndarray) -> None:
        """Print excitation weights.

        **Arguments:**

        ci_vector:
            (np.array) the CI coefficient vector that contains all coefficients
            for one specific state
        """
        nov = self.occ_model.nacto[0] * self.occ_model.nactv[0] + 1
        log(
            f"          weight(s): {np.dot(ci_vector[1:nov], ci_vector[1:nov]): 1.5f}"
        )
        log(
            f"          weight(d): {np.dot(ci_vector[nov:], ci_vector[nov:]): 1.5f}"
        )

    def compute_h_diag(self, *args: Any) -> tuple[TwoIndex, FourIndex]:
        """Used by Davidson module for pre-conditioning.

        **Arguments:**

        args:
            required for Davidson module (not used here)
        """
        t_ia = self.checkpoint["t_1"]
        t_iajb = self.checkpoint["t_2"]
        #
        # Output objects
        #
        h_diag_s = t_ia.new()
        h_diag_d = t_iajb.new()
        #
        # Get auxiliary matrices
        #
        x_ik = self.from_cache("x_ik")
        x_ac = self.from_cache("x_ac")
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
        # Singles (h_diag_s[i,a])
        #
        # X_iakc(i,a,i,a)
        x1_iakc = self.from_cache("x1_iakc")
        x1_iakc.contract("abab->ab", out=h_diag_s)
        if self.dump_cache:
            self.cache.dump("x1_iakc")
        # X_ik(i,i)
        tmp = x_ik.copy_diagonal()
        tmp.expand("a->ab", h_diag_s)
        # X_ac(a,a)
        tmp = x_ac.copy_diagonal()
        tmp.expand("b->ab", h_diag_s)
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

        return h_diag_s, h_diag_d

    def get_h_diag_x_acac_term(self) -> TwoIndex:
        """Calculate the diagonal H part of the X_abcd effective term.

        Returns:
            DenseTwoIndex: the X_abcd[a,b,a,b] part of the X_abcd array
        """
        if isinstance(self.lf, CholeskyLinalgFactory):
            # Get data and ranges
            t_ia = self.checkpoint["t_1"]
            t_iajb = self.checkpoint["t_2"]
            gvvvv = self.from_cache("gvvvv")
            govvv = self.from_cache("govvv")
            # 0.5 <ab|ab>
            tmp = gvvvv.contract("abab->ab", factor=0.5)
            govv = govvv.contract("abcb->abc")
            # -1.0 <kb|ab> tka
            govv.contract("abc,ac->cb", t_ia, tmp, factor=-1.0)
            # 0.5 <kl|ab> tkalb
            goovv = self.from_cache("goovv")
            goovv.contract("abcd,acbd->cd", t_iajb, tmp, factor=0.5)
            if self.disconnected:
                # 0.5 <kl|ab> tka tlb -> 0.5 tmp_lab[l,a,b] tlb
                tmp_lab = goovv.contract("abcd,ac->bcd", t_ia)
                # 0.5 tmp_lab[l,a,b] tlb
                tmp_lab.contract("abc,ac->bc", t_ia, tmp, factor=0.5)
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
    ) -> tuple[float, TwoIndex, FourIndex, TwoIndex, FourIndex]:
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
        t_ia = self.checkpoint["t_1"]
        t_iajb = self.checkpoint["t_2"]
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        #
        # Get ranges
        #
        ov2 = self.get_range("ov", offset=2)
        #
        # Get auxiliary matrices and effective Hamiltonian terms
        #
        fock = self.from_cache("fock")
        x_ik = self.from_cache("x_ik")
        x_ac = self.from_cache("x_ac")
        x_ilkc = self.from_cache("x_ilkc")
        x_kc = self.from_cache("x_kc")
        x_ijbl = self.from_cache("x_ijbl")
        x_jk = self.from_cache("x_jk")
        x_bd = self.from_cache("x_bd")
        x_ijkl = self.from_cache("x_ijkl")
        #
        # Calculate sigma vector (H.bvector)_kc
        #
        end_s = nacto * nactv + 1
        # singles
        sigma_s = self.lf.create_two_index(nacto, nactv)
        to_s = {"out": sigma_s, "clear": False}
        bv_s = self.dense_lf.create_two_index(nacto, nactv)
        # doubles
        sigma_d = self.dense_lf.create_four_index(nacto, nactv, nacto, nactv)
        to_d = {"out": sigma_d, "clear": False}
        bv_d = self.dense_lf.create_four_index(nacto, nactv, nacto, nactv)
        #
        # reshape bvector
        #
        bv_s.assign(bvector, begin2=1, end2=end_s)
        bv_d.assign_triu(bvector, begin4=end_s)
        bv_p = bv_d.contract("abab->ab", clear=True)
        bv_d.iadd_transpose((2, 3, 0, 1))
        self.set_seniority_0(bv_d, bv_p)
        #
        # Reference vector R_0
        #
        # X0,kc rkc
        sum0_ = bv_s.contract("ab,ab", fock, **ov2) * 2.0
        tmp = self.lf.create_two_index(nacto, nactv)
        loovv = self.from_cache("loovv")
        loovv.contract("abcd,bd->ac", t_ia, tmp)
        sum0_ += bv_s.contract("ab,ab", tmp) * 2.0
        sum0_ += bv_d.contract("abcd,acbd", loovv)
        if self.dump_cache:
            self.cache.dump("loovv")
        #
        # Single excitations
        #
        sigma_s.clear()
        # [3] X_iakc rkc
        x1_iakc = self.from_cache("x1_iakc")
        x1_iakc.contract("abcd,cd->ab", bv_s, **to_s)  # iakc,kc->ia
        if self.dump_cache:
            self.cache.dump("x1_iakc")
        # [2] X_ik rka
        x_ik.contract("ab,bc->ac", bv_s, **to_s)
        # [1] X_ac ric
        bv_s.contract("ab,cb->ac", x_ac, **to_s)  # ic,ac->ia
        # [5] X_ilkc rlakc
        x_ilkc.contract("abcd,becd->ae", bv_d, **to_s)
        # [6] X_adkc ridkc
        self.get_effective_hamiltonian_term_adkc(bv_d, sigma_s)
        # [4] X_kc Riakc/Rkaic
        bv_d.contract("abcd,cd->ab", x_kc, **to_s, factor=2.0)
        bv_d.contract("abcd,ad->cb", x_kc, **to_s, factor=-1.0)
        #
        # All remaining double excitations
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
        #
        # Coupling to singles
        # [2] P X_ijbl rla
        x_ijbl.contract("abcd,de->aebc", bv_s, sigma_d)  # ijak,kb->iajb
        # [1] P X_iabd rjd
        self.get_effective_hamiltonian_term_iabd(bv_s, sigma_d)
        # [3] P (X_ilkc tlajb + x_adkc tidjb) rkc
        self.get_effective_hamiltonian_term_ijabkc(bv_s, sigma_d)
        if not self.disconnected:
            # Get rid of disconnected terms T1.T2
            x_ilkc = self.from_cache("x_ilkc_linear")
        tmp = x_ilkc.contract("ilkc,kc->il", bv_s)
        tmp.contract("il,lajb->iajb", t_iajb, sigma_d)

        return sum0_, sigma_s, sigma_d, bv_s, bv_d

    def update_hamiltonian(self, mo1: TwoIndex, mo2: FourIndex) -> None:
        """Derive all auxiliary matrices. Derive all matrices that are common
        for all EOM-CCSD flavours.

        **Arguments:**

        mo1, mo2
             one- and two-electron integrals to be sorted.
        """
        t_ia = self.checkpoint["t_1"]
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
        vovv = self.get_range("vovv")
        #
        # Get auxiliary matrices
        # Inactive Fock matrix
        #
        fock = self.init_cache("fock", nact, nact)
        get_fock_matrix(fock, mo1, mo2, nacto)
        #
        # <oo||vv>+<oo|vv>
        # We will keep the loovv array in memory to prevent loading it from disk
        # It will be deleted once it is not used anymore. If you can do EOM-CCSD,
        # storing loovv during the construction of the effective Hamiltonian
        # should not be an issue.
        # This can always be adjusted in the future by dumping/reading arrays
        loovv = self.init_cache("loovv", nacto, nacto, nactv, nactv)
        mo2.contract("abcd->abcd", loovv, factor=2.0, **oovv)
        mo2.contract("abcd->abdc", loovv, factor=-1.0, **oovv)
        # temporary matrix; will be deleted afterward (not stored in Cache)
        gooov = mo2.contract("abcd->abcd", **ooov)
        # Get ov intermediate frequently used for disconnected contractions
        # L_klcd tld -> L_t_kc (lt_ov[k,c])
        lt_ov = self.init_cache("lt_ov", nacto, nactv)
        loovv.contract("abcd,bd->ac", t_ia, lt_ov)
        #
        # Get expensive effective Hamiltonian arrays, which include arrays of
        # dimension ovvv and vvvv.
        #
        if not isinstance(self.lf, CholeskyLinalgFactory):
            self.get_effective_hamiltonian_xvvv(fock, gooov, loovv, lt_ov, mo2)
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
        # - tic F_kc
        t_ia.contract("ab,cb->ac", fock, out=x_ik, factor=-1.0, **ov2)
        # - L_klid t_ld
        looov.contract("abcd,bd->ca", t_ia, x_ik, factor=-1.0)
        # - L_klcd ticld
        t_iajb.contract("abcd,aebd->ce", loovv, x_ik, factor=-1.0)
        if self.disconnected:
            # - ( L_klcd tld ) tic -> - lt_ov[k,c] tic
            # tic (kc)
            t_ia.contract("ab,cb->ac", lt_ov, x_ik, factor=-1.0)
        #
        # (3) X_ac
        #
        x_ac = self.init_cache("x_ac", nactv, nactv)
        # F_ac
        x_ac.iadd(fock, 1.0, **vv2)
        # - tka fkc
        t_ia.contract("ab,ac->bc", fock, x_ac, factor=-1.0, **ov2)
        # L_kadc t_kd
        mo2.contract("abcd,ac->bd", t_ia, x_ac, factor=2.0, **ovvv)
        mo2.contract("abcd,ad->bc", t_ia, x_ac, factor=-1.0, **ovvv)
        # - L_klcd tkald
        t_iajb.contract("abcd,acbe->de", loovv, x_ac, factor=-1.0)
        if self.disconnected:
            # - ( L_klcd tld ) tka -> - lt_ov[k,c] tka
            # tka (kc)
            t_ia.contract("ab,ac->bc", lt_ov, x_ac, factor=-1.0)
        #
        # (1) X_iakc
        #
        x1_iakc = self.init_cache("x1_iakc", nacto, nactv, nacto, nactv)
        # L_icak
        mo2.contract("abcd->acdb", x1_iakc, factor=2.0, **ovvo)
        mo2.contract("abcd->adcb", x1_iakc, factor=-1.0, **ovov)
        # - L_lkic t_la
        looov.contract("abcd,ae->cebd", t_ia, x1_iakc, factor=-1.0)
        # L_kacd t_id
        mo2.contract("abcd,ed->ebac", t_ia, x1_iakc, factor=2.0, **ovvv)
        mo2.contract("abcd,ec->ebad", t_ia, x1_iakc, factor=-1.0, **ovvv)
        # L_klcd (2t_iald-tidla)
        loovv.contract("abcd,efbd->efac", t_iajb, x1_iakc, factor=2.0)
        loovv.contract("abcd,edbf->efac", t_iajb, x1_iakc, factor=-1.0)
        if self.disconnected:
            # - L_klcd tid tla
            # L_klcd tid = tmp[i,k,c,l]
            tmp = loovv.contract("abcd,ed->eacb", t_ia)
            # - tmp[i,k,c,l] tla
            tmp.contract("abcd,de->aebc", t_ia, x1_iakc, factor=-1.0)
            del tmp
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
        # - L_klcd tid
        loovv.contract("abcd,ed->ebac", t_ia, x_ilkc, factor=-1.0)
        #
        # (4/5) X_kc
        #
        x_kc = self.init_cache("x_kc", nacto, nactv)
        # F_kc
        x_kc.iadd(fock, 1.0, **ov2)
        # L_klcd tld = lt_ov[k,c]
        x_kc.iadd(lt_ov, 1.0)
        #
        # (11) X_jk
        #
        x_jk = self.init_cache("x_jk", nacto, nacto)
        # (1) - F_jk
        x_jk.iadd(fock, -1.0, **oo2)
        # (2) - L_kljc tlc
        looov.contract("abcd,bd->ca", t_ia, x_jk, factor=-1.0)
        # (3) - tjc F_kc
        t_ia.contract("ab,cb->ac", fock, x_jk, factor=-1.0, **ov2)
        # (4) - L_klcd tjcld
        loovv.contract("abcd,ecbd->ea", t_iajb, x_jk, factor=-1.0)
        if self.disconnected:
            # (5) - L_klcd tld tjc -> lt_ov[k,c] tjc
            t_ia.contract("ab,cb->ac", lt_ov, x_jk, factor=-1.0)
        #
        # (12) X_bd
        #
        x_bd = self.init_cache("x_bd", nactv, nactv)
        # (1) F_bc
        x_bd.iadd(fock, 1.0, **vv2)
        # (2) L_kbcd tkc
        mo2.contract("abcd,ac->bd", t_ia, x_bd, factor=2.0, **ovvv)
        mo2.contract("abcd,ad->bc", t_ia, x_bd, factor=-1.0, **ovvv)
        # (3) - F_kd tkb
        t_ia.contract("ab,ac->bc", fock, x_bd, factor=-1.0, **ov2)
        # (4) - L_klcd tkclb
        loovv.contract("abcd,acbe->ed", t_iajb, x_bd, factor=-1.0)
        if self.disconnected:
            # (5) - L_klcd tld tkb -> lt_ov[k,c] tkb
            t_ia.contract("ab,ac->bc", lt_ov, x_bd, factor=-1.0)
        #
        # (14) X_iakc
        #
        x_iakc = self.init_cache("x_iakc", nacto, nactv, nacto, nactv)
        # (1) - <ic|ak>
        mo2.contract("abcd->acdb", x_iakc, factor=-1.0, **ovvo)
        # (2) <lk|ic> tla = <ik|lc> tla
        gooov.contract("abcd,ce->aebd", t_ia, x_iakc)
        # (3) - <ak|dc> tid
        mo2.contract("abcd,ec->eabd", t_ia, x_iakc, factor=-1.0, **vovv)
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
        # Get intermediates used for disconnected terms
        if self.disconnected:
            # <kl|cd> tic -> gt_ooov[i,k,l,d]
            gt_ooov = goovv.contract("abcd,ec->eabd", t_ia)
            # (5) <lk|dc> tid tla = gt_ooov[i,l,k,c] tla
            gt_ooov.contract("abcd,be->aecd", t_ia, x_iakc)
        if self.dump_cache:
            self.cache.dump("x_iakc")
        #
        # (15) X_ajkc
        #
        x_ajkc = self.init_cache("x_ajkc", nactv, nacto, nacto, nactv)
        # (1) - <ka|jc>
        mo2.contract("abcd->bcad", x_ajkc, factor=-1.0, **ovov)
        # (2) <kl|jc> tla
        mo2.contract("abcd,be->ecad", t_ia, x_ajkc, **ooov)
        # (3) - <ka|dc> tjd
        mo2.contract("abcd,ec->bead", t_ia, x_ajkc, factor=-1.0, **ovvv)
        # (4) <lk|cd> tjdla
        goovv.contract("abcd,ecbf->fead", t_iajb, x_ajkc)
        if self.disconnected:
            # (5) <kl|dc> tjd tla = gt_ooov[j,k,l,c] tla
            gt_ooov.contract("abcd,ce->eabd", t_ia, x_ajkc)
        if self.dump_cache:
            self.cache.dump("x_ajkc")
        #
        # (17) X_ijkl
        #
        x_ijkl = self.init_cache("x_ijkl", nacto, nacto, nacto, nacto)
        # (1) 0.5 <ij|kl>
        mo2.contract("abcd->abcd", x_ijkl, factor=0.5, **oooo)
        # (2) <kl|cj> tic
        mo2.contract("abcd,ec->edab", t_ia, x_ijkl, **oovo)
        # (3) 0.5 <kl|cd> ticjd
        goovv.contract("abcd,ecfd->efab", t_iajb, x_ijkl, factor=0.5)
        if self.disconnected:
            # (4) 0.5 <kl|cd> tjd tic = gt_ooov[i,k,l,c] tjc
            gt_ooov.contract("abcd,ed->aebc", t_ia, x_ijkl, factor=0.5)
        #
        # (9) X_ijbl
        #
        x_ijbl = self.init_cache("x_ijbl", nacto, nacto, nactv, nacto)
        # (1) - <ij|lb>
        mo2.contract("abcd->abdc", x_ijbl, factor=-1.0, **ooov)
        # (4) - F_lc t_icjb
        t_iajb.contract("abcd,eb->acde", fock, x_ijbl, factor=-1.0, **ov4)
        # (3) - <jl|bc> tic
        mo2.contract("abcd,ed->eacb", t_ia, x_ijbl, factor=-1.0, **oovv)
        # (3) - <ib|lc> tjc
        mo2.contract("abcd,ed->aebc", t_ia, x_ijbl, factor=-1.0, **ovov)
        # (2) <ij|lk> tkb
        mo2.contract("abcd,de->abec", t_ia, x_ijbl, **oooo)
        # (6) - <lb|cd> ticjd
        mo2.contract("abcd,ecfd->efba", t_iajb, x_ijbl, factor=-1.0, **ovvv)
        # (5) - L_lkic t_jbkc
        looov.contract("abcd,efbd->cefa", t_iajb, x_ijbl, factor=-1.0)
        # (5) <ik|lc> tjckb
        gooov.contract("abcd,edbf->aefc", t_iajb, x_ijbl)
        # (5) <jl|kc> tickb
        gooov.contract("abcd,edcf->eafb", t_iajb, x_ijbl)
        if self.disconnected:
            # (7) - L_lkdc tkc tidjb -> - lt_ov[l,d] tidjb
            # - tidjb (ld)
            t_iajb.contract("abcd,eb->acde", lt_ov, x_ijbl, factor=-1.0)
            # (8) - L_klcd tid tjbkc = - [2 <kl|cd> - <kl|dc>] tid tjbkc
            # (8) - [ 2 gt_ooov(i,l,k,c) - gt_ooov(i,k,l,c) ]tjbkc
            gt_ooov.contract("abcd,efcd->aefb", t_iajb, x_ijbl, factor=-2.0)
            gt_ooov.contract("abcd,efbd->aefc", t_iajb, x_ijbl)
            # (8) <kl|dc> tjd tickb = - gt_ooov(j,k,l,c) tickb
            gt_ooov.contract("abcd,edbf->eafc", t_iajb, x_ijbl)
            # (8) <lk|dc> tid tjckb = - gt_ooov(i,l,k,c) tjckb
            gt_ooov.contract("abcd,edcf->aefb", t_iajb, x_ijbl)
            # temporary matrix needed for some contractions
            # gt_oooo(i,j,l,k) = <lk|ic> tjc
            gt_oooo = gooov.contract("abcd,ed->ceab", t_ia)
            # (10) <lk|ic> tjc tkb = gt_oooo[i,j,l,k] tkb
            # add all [i,j,l,k] terms together: tmp[i,j,l,k]
            tmp = gt_oooo.copy()
            # (10) <kl|jc> tic tkb = gt_oooo[j,i,k,l] tkb
            gt_oooo.contract("abcd->badc", tmp)
            # (9) <lk|dc> tidjc tkb = [ijlk] tkb
            goovv.contract("abcd,ecfd->efab", t_iajb, tmp)
            # (12) <kl|cd> tjc tid tkb = gt_ooov[j,k,l,d] tid tkb -> [ijlk] tkb
            gt_ooov.contract("abcd,ed->eacb", t_ia, tmp)
            # tmp[i,j,l,k] tkb -> x_ijbl
            tmp.contract("abcd,de->abec", t_ia, x_ijbl)
            # (11) - <lb|cd> tjd tic = (jblc) tic
            tmp = mo2.contract("abcd,ed->ebac", t_ia, **ovvv)
            tmp.contract("abcd,ed->eabc", t_ia, x_ijbl, factor=-1.0)
            del gt_ooov
        # Remove from Cache
        if self.dump_cache:
            self.cache.dump("goovv")
        del gooov

        gc.collect()

    def get_effective_hamiltonian_xvvv(
        self,
        fock: TwoIndex,
        gooov: FourIndex,
        loovv: FourIndex,
        lt_ov: TwoIndex,
        mo2: FourIndex,
    ) -> None:
        """Generate all expensive effective Hamiltonian terms.
        This function is called if we work in the DenseLinalgFactory picture.
        All effective Hamiltonian elements of size xvvv are calculated here,
        where x is either occupied (ov^3) or virtual (v^4).

        Args:
            fock (TwoIndex): The inactive Fock matrix in the MO basis
            gooov (FourIndex): A slice of the two-electron integrals in the MO basis
            loovv (FourIndex): A slice of 2<pq|rs>-<pq|sr> in the MO basis
            lt_ov (TwoIndex): [2<pq|rs>-<pq|sr>] t_qs in the MO basis
            mo2 (FourIndex): The two-electron integrals in the MO basis
        """
        t_ia = self.checkpoint["t_1"]
        t_iajb = self.checkpoint["t_2"]
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        #
        # Get ranges
        #
        ov4 = self.get_range("ov", offset=4)
        oovv = self.get_range("oovv")
        ovvo = self.get_range("ovvo")
        ovov = self.get_range("ovov")
        ovvv = self.get_range("ovvv")
        vovv = self.get_range("vovv")
        vvvv = self.get_range("vvvv")
        # Most expensive operation. Do first to have largest amount of memory
        # available
        # X_abcd
        x_abcd = self.init_cache("x_abcd", nactv, nactv, nactv, nactv)
        # 0.5 <ab|cd>
        mo2.contract("abcd->abcd", x_abcd, factor=0.5, **vvvv)
        # - <kb|cd> tka
        mo2.contract("abcd,ae->ebcd", t_ia, x_abcd, factor=-1.0, **ovvv)
        # 0.5 <kl|cd> tkalb
        mo2.contract("abcd,aebf->efcd", t_iajb, x_abcd, factor=0.5, **oovv)
        if self.disconnected:
            # 0.5 <kl|cd> tka tlb
            # <kl|cd> tka = (alcd)
            tmp = mo2.contract("abcd,ae->ebcd", t_ia, **oovv)
            # 0.5 (alcd) tlb
            tmp.contract("abcd,be->aecd", t_ia, x_abcd, factor=0.5)
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
        # L_lkdc tla
        loovv.contract("abcd,ae->ecbd", t_ia, x_adkc, factor=-1.0)
        if self.dump_cache:
            self.cache.dump("x_adkc")
        #
        # (8) X_iabd
        #
        x_iabd = self.init_cache("x_iabd", nacto, nactv, nactv, nactv)
        # (1) <id|ab>
        mo2.contract("abcd->acdb", x_iabd, **ovvv)
        # (2) <ab|cd> tic
        mo2.contract("abcd,ec->eabd", t_ia, x_iabd, **vvvv)
        # (3) - <id|al> tlb
        mo2.contract("abcd,de->aceb", t_ia, x_iabd, factor=-1.0, **ovvo)
        # (3) - <id|lb> tla
        mo2.contract("abcd,ce->aedb", t_ia, x_iabd, factor=-1.0, **ovov)
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
        if self.disconnected:
            # (7) - L_lkdc tkc tialb -> - lt_ov[l,d] tialb
            t_iajb.contract("abcd,ce->abde", lt_ov, x_iabd, factor=-1.0)
            # intermediate <kl|cd> tlb = gt_ovvv[b,k,c,d]
            gt_ovvv = mo2.contract("abcd,be->eacd", t_ia, **oovv)
            # (8) - L_klcd tlb tiakc = - [ 2 <kl|cd> - <kl|dc> ] tlb tiakc
            # - 2 gt_ovvv[b,k,c,d] tiakc
            gt_ovvv.contract("abcd,efbc->efad", t_iajb, x_iabd, factor=-2.0)
            # gt_ovvv[b,k,d,c] tiakc
            gt_ovvv.contract("abcd,efbd->efac", t_iajb, x_iabd)
            # (8) <lk|cd> tkb ticla = gt_ovvv[b,l,c,d] ticla
            gt_ovvv.contract("abcd,ecbf->efad", t_iajb, x_iabd)
            # (8) <lk|dc> tka ticlb = gt_ovvv[a,l,d,c) ticlb
            gt_ovvv.contract("abcd,edbf->eafc", t_iajb, x_iabd)
            # (12) <lk|cd> tic tkb tla = gt_ooov[i,l,k,d] tla tkb
            # (11) <lk|id>     tkb tla =        [i,l,k,d] tla tkb
            # @(12) <lk|cd> tic = gt_ooov[i,l,k,d]
            tmp_ilkd = mo2.contract("abcd,ec->eabd", t_ia, **oovv)
            # @(11) <ik|ld> -> [i,l,k,d]
            gooov.contract("abcd->acbd", tmp_ilkd)
            # (11)+(12) tmp_ilkd tla tkb
            tmp = tmp_ilkd.contract("abcd,be->aecd", t_ia)
            tmp.contract("abcd,ce->abed", t_ia, x_iabd)
            del gt_ovvv, tmp_ilkd, tmp
            # (9) ( <lk|dc> tic ) tkalb = tmp[i,d,l,k] tkalb
            tmp = mo2.contract("abcd,ed->ecab", t_ia, **oovv)
            tmp.contract("abcd,decf->aefb", t_iajb, x_iabd)
            # (10) - ( <bk|dc> tic ) tka = - tmp[i,b,d,k) tka
            tmp = mo2.contract("abcd,ed->eacb", t_ia, **vovv)
            tmp.contract("abcd,de->aebc", t_ia, x_iabd, factor=-1.0)
            # (10) - ( <ak|cd> tic ) tkb = - tmp[i,a,d,k) tkb
            tmp = mo2.contract("abcd,ec->eadb", t_ia, **vovv)
            tmp.contract("abcd,de->abec", t_ia, x_iabd, factor=-1.0)
            del tmp
        gc.collect()

    #
    # Expensive effective Hamiltonian terms
    #

    def get_effective_hamiltonian_term_adkc(
        self, bv_d: FourIndex, sigma: FourIndex
    ) -> None:
        """Compute effective Hamiltonian term involving an vvov block.
        Equivalent contraction schemes for CC with and without disconnected
        terms.

        **Arguments:**

        :bv_d: (DenseFourIndex) the current approximation to the CI doubles
               coefficient

        :sigma: (DenseFourIndex) the output sigma vector
        """
        to_s = {"out": sigma, "clear": False}
        t_ia = self.checkpoint["t_1"]
        if isinstance(self.lf, CholeskyLinalgFactory):
            govvv = self.from_cache("govvv")
            # L_kacd rkcid
            govvv.contract("abcd,aced->eb", bv_d, **to_s, factor=2.0)
            govvv.contract("abcd,adec->eb", bv_d, **to_s, factor=-1.0)
            # - L_klcd tla rkcid
            loovv = self.from_cache("loovv")
            tmp = loovv.contract("abcd,aced->be", bv_d)
            if self.dump_cache:
                self.cache.dump("loovv")
            tmp.contract("ab,ac->bc", t_ia, **to_s, factor=-1.0)
        else:
            # X_adkc ridkc
            x_adkc = self.from_cache("x_adkc")
            x_adkc.contract("abcd,ebcd->ea", bv_d, **to_s)
            if self.dump_cache:
                self.cache.dump("x_adkc")

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
            t_ia = self.checkpoint["t_1"]
            t_iajb = self.checkpoint["t_2"]
            gnnvv = self.from_cache("gnnvv")
            oooo = self.get_range("oooo")
            ooov = self.get_range("ooov")
            ovov = self.get_range("ovov")
            # (16) X_abcd ricjd
            # Creating expensive intermediate of size o^2a^2 (occupied/active)
            # to reduce the number of operations
            # tmp[i,act,j,act] = <act act|cd> ricjd
            tmp = gnnvv.contract("abcd,ecfd->eafb", bv_d)
            # 0.5 <ab|cd> ricjd -> 0.5 tmp[i,a,j,b]
            tmp.contract("abcd->abcd", **to_d, factor=0.5, **ovov)
            # - <kb|cd> tka ricjd -> - tmp[i,k,j,b] tka
            tmp.contract("abcd,be->aecd", t_ia, **to_d, factor=-1.0, **ooov)
            # 0.5 <kl|cd> tkalb ricjd -> 0.5 tmp[i,k,j,l] tkalb
            tmp.contract("abcd,bedf->aecf", t_iajb, **to_d, factor=0.5, **oooo)
            if self.disconnected:
                # 0.5 <kl|cd> rijcd tka tlb -> 0.5 [ tmp[i,k,j,l] tka ] tlb
                tmp_iajl = tmp.contract("abcd,be->aecd", t_ia, **oooo)
                del tmp
                # 0.5 tmp_iajl tlb
                tmp_iajl.contract("abcd,de->abce", t_ia, **to_d, factor=0.5)
                del tmp_iajl
        else:
            x_abcd = self.from_cache("x_abcd")
            bv_d.contract("abcd,efbd->aecf", x_abcd, **to_d)
            if self.dump_cache:
                self.cache.dump("x_abcd")

    def get_effective_hamiltonian_term_iabd(
        self, bv_s: TwoIndex, sigma: FourIndex
    ) -> None:
        """Compute effective Hamiltonian term involving an ovvv block

        **Arguments:**

        :bv_s: (DenseTwoIndex) the current approximation to the CI singles
               coefficient

        :sigma: (DenseFourIndex) the output sigma vector
        """
        to_d = {"out": sigma, "clear": False}
        if isinstance(self.lf, CholeskyLinalgFactory):
            t_ia = self.checkpoint["t_1"]
            t_iajb = self.checkpoint["t_2"]
            ov2 = self.get_range("ov", offset=2)
            oovo = self.get_range("oovo")
            ooov = self.get_range("ooov")
            oooo = self.get_range("oooo")
            oovv = self.get_range("oovv")
            fock = self.from_cache("fock")
            govvv = self.from_cache("govvv")
            gvvvv = self.from_cache("gvvvv")
            govnn = self.from_cache("govnn")
            # (1) <ja|bc> tic
            govvv.contract("abcd,ed->ebac", bv_s, **to_d)
            # (2) <ab|cd> rjd tic
            gvvvv.contract("abcd,ec,fd->eafb", t_ia, bv_s, **to_d)
            # (4) -rjd fkd tkbia -> (jk) tiakb
            tmp = bv_s.contract("ab,cb->ac", fock, **ov2)
            t_iajb.contract("abcd,ea->abed", tmp, **to_d, factor=-1.0)
            # Creating expensive intermediate of size o^2a^2 (occupied/active)
            # to reduce the number of operations
            # tmp[i,j,act,act] = <id|act act> rjd
            tmp = govnn.contract("abcd,eb->aecd", bv_s)
            # (3) - <id|ak> rjd tkb -> - <ij|ak> tkb
            tmp.contract("abcd,de->acbe", t_ia, **to_d, factor=-1.0, **oovo)
            # (3) - <bk|di> rjd tka -> - <ij|kb> tka
            tmp.contract("abcd,ce->aebd", t_ia, **to_d, factor=-1.0, **ooov)
            # (6) <lk|di> rjd tkalb -> <ij|kl> tkalb
            tmp.contract("abcd,cedf->aebf", t_iajb, **to_d, **oooo)
            # (5) - <kd|cb> rjd ticka -> - <kj|cb> ticka
            tmp.contract(
                "abcd,ecaf->efbd", t_iajb, **to_d, factor=-1.0, **oovv
            )
            # (5) L_kbcd rjd tiakc -> 2 <kb|cd> rjd tiakc - <kb|dc> rjd tiakc
            # @(5) 2 <kb|cd> rjd tiakc -> 2 <kj|cb> tiakc
            tmp.contract("abcd,efac->efbd", t_iajb, **to_d, factor=2.0, **oovv)
            tmp = None
            # Redefine expensive intermediate of size o^2v^2
            # to reduce the number of operations (for exchange term)
            # tmp[j,b,k,c] = <kb|dc> rjd
            tmp = govvv.contract("abcd,ec->ebad", bv_s)
            # @(5) - <kb|dc> rjd tkcia -> - <jb|kc> tkcia
            tmp.contract("abcd,cdef->efab", t_iajb, **to_d, factor=-1.0)
            # (5) - <ka|dc> rjd tickb -> - <ja|kc> tickb
            tmp.contract("abcd,edcf->ebaf", t_iajb, **to_d, factor=-1.0)
            del tmp
            if self.disconnected:
                # (7) - L_lkdc tkc rjd tialb -> - lt_ov[l,d] rjd tialb
                lt_ov = self.from_cache("lt_ov")
                # tmp[j,l] = lt_ov[l,d] rjd
                tmp = bv_s.contract("ab,cb->ac", lt_ov)
                # tmp[j,l] tialb
                t_iajb.contract("abcd,ec->abed", tmp, **to_d, factor=-1.0)
                # Intermediate <kl|cd> rjd -> gr_ooov[j,k,l,c]
                goovv = self.from_cache("goovv")
                gr_ooov = goovv.contract("abcd,ed->eabc", bv_s)
                if self.dump_cache:
                    self.cache.dump("goovv")
                # Intermediate gr_ooov[j,k,l,c] tlb -> grt_oovv[j,b,k,c]
                grt_oovv = gr_ooov.contract("abcd,ce->aebd", t_ia)
                # (8) - L_klcd rjd tlb tiakc = - [ 2 <kl|cd> - <kl|dc> ] rjd tlb tiakc
                # @(8) - [ 2 <kl|cd> rjd tlb ] tiakc -> -2 grt_oovv[j,b,k,c] tiakc
                t_iajb.contract("abcd,efcd->abef", grt_oovv, **to_d, factor=-2)
                # (8) [ <kl|cd> rjd tlb ] ticka -> grt_oovv[j,b,k,c] ticka
                t_iajb.contract("abcd,efcb->adef", grt_oovv, **to_d)
                # (12) [ <kl|cd> rjd tlb ] tic tka = grt_oovv[j,b,k,c] tic tka
                # tmp[i,j,b,k] = grt_oovv[j,b,k,c] tic
                tmp = grt_oovv.contract("abcd,ed->eabc", t_ia)
                del grt_oovv
                # tmp[i,j,b,k] tka
                tmp.contract("abcd,de->aebc", t_ia, **to_d)
                # Intermediate grt_ovov[j,b,k,c] = gr_ooov[j,l,k,c] tlb
                grt_ovov = gr_ooov.contract("abcd,be->aecd", t_ia)
                # @(8) [ <lk|cd> rjd tlb ] tiakc -> grt_ovov[j,b,k,c] tiakc
                t_iajb.contract("abcd,efcd->abef", grt_ovov, **to_d)
                # (8) [ <kl|cd> rjd tka ] ticlb = grt_ovov[j,a,l,c) ticlb
                t_iajb.contract("abcd,efcb->afed", grt_ovov, **to_d)
                del grt_ovov
                # (9) [ <kl|cd> rjd ] tic tkalb = gr_ooov[j,k,l,c] tic tkalb
                # tmp[i,j,k,l] = gr_ooov[j,k,l,c] tic
                tmp = gr_ooov.contract("abcd,ed->eabc", t_ia)
                del gr_ooov
                # tmp[i,j,k,l] tkalb
                tmp.contract("abcd,cedf->aebf", t_iajb, **to_d)
                # (11) [ <kl|id> rjd ] tlb tka = tmp[i,j,k,l] tka tlb
                # tmp[i,j,k,l]
                gooov = self.from_cache("gooov")
                tmp = gooov.contract("abcd,ed->ceab", bv_s)
                # [i,a,j,l] = tmp[i,j,k,l] tka
                tmp = tmp.contract("abcd,ce->aebd", t_ia)
                # [i,a,j,l] tlb
                tmp.contract("abcd,de->abce", t_ia, **to_d)
                # (10) - [ <bk|dc> tic ] tka rjd = - tmp[i,b,k,d] rjd tka
                gvovv = self.from_cache("gvovv")
                tmp = gvovv.contract("abcd,ed->eabc", t_ia)
                # tmp[i,j,b,k] = tmp[i,b,k,d] rjd
                tmp = tmp.contract("abcd,ed->aebc", bv_s)
                # - tmp[i,j,b,k] tka
                tmp.contract("abcd,de->aebc", t_ia, **to_d, factor=-1.0)
                # (10) - [ <ak|cd> tic ] tkb rjd = - tmp[i,a,k,d] rjd tkb
                tmp = gvovv.contract("abcd,ec->eabd", t_ia)
                # tmp[i,j,a,k] = tmp[i,a,k,d] rjd
                tmp = tmp.contract("abcd,ed->aebc", bv_s)
                # - tmp[i,j,a,k] tkb
                tmp.contract("abcd,de->acbe", t_ia, **to_d, factor=-1.0)
                tmp = None
                del tmp
        else:
            x_iabd = self.from_cache("x_iabd")
            # X_iabd rjd
            x_iabd.contract("abcd,ed->abec", bv_s, **to_d)
            if self.dump_cache:
                self.cache.dump("x_iabd")

    def get_effective_hamiltonian_term_ijabkc(
        self, bv_s: TwoIndex, sigma: FourIndex
    ) -> None:
        """Compute effective Hamiltonian term involving an ovvv block

        **Arguments:**

        :bv_s: (DenseTwoIndex) the current approximation to the CI singles
               coefficient

        :sigma: (DenseFourIndex) the output sigma vector
        """
        t_iajb = self.checkpoint["t_2"]
        tmp = self.lf.create_two_index(self.occ_model.nactv[0])
        to_d = {"out": sigma, "clear": False}
        to_t = {"out": tmp, "clear": False}
        if isinstance(self.lf, CholeskyLinalgFactory):
            govvv = self.from_cache("govvv")
            # 2.0 L_kacd rkc
            # 2.0 <ka|cd> rkc -> tmp[a,d]
            govvv.contract("abcd,ac->bd", bv_s, **to_t, factor=2.0)
            # - <ka|dc> rkc -> tmp[a,d]
            govvv.contract("abcd,ad->bc", bv_s, **to_t, factor=-1.0)
            if self.disconnected:
                t_ia = self.checkpoint["t_1"]
                # - [ L_klcd rkc ] tla tidjb -> - tmp_ld[l,d] tla tidjb
                loovv = self.from_cache("loovv")
                tmp_ld = loovv.contract("abcd,ac->bd", bv_s)
                if self.dump_cache:
                    self.cache.dump("loovv")
                # - tmp_ld[l,d] tla tidjb -> tmp[a,d] tidjb
                tmp_ld.contract("ab,ac->cb", t_ia, factor=-1.0, **to_t)
        else:
            x_adkc_str = "x_adkc" if self.disconnected else "x_adkc_linear"
            x_adkc = self.from_cache(x_adkc_str)
            # X_adkc rkc
            x_adkc.contract("abcd,cd->ab", bv_s, **to_t)
            if self.dump_cache:
                self.cache.dump(x_adkc_str)
        # idjb,ad->iajb
        t_iajb.contract("abcd,eb->aecd", tmp, **to_d)
