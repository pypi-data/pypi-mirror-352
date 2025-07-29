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
# 2024: This module has been originally written by Saman Behjou
#
"""Electron Attachment Equation of Motion Coupled Cluster implementations for
a CCSD reference function

Variables used in this module:
:ncore:     number of frozen core orbitals
:nocc:      number of occupied orbitals in the principle configuration
:nacto:     number of active occupied orbitals in the principle configuration
(abbreviated as no)
:nvirt:     number of virtual orbitals in the principle configuration
:nactv:     number of active virtual orbitals in the principle configuration
(abbreviated as nv)
:nbasis:    total number of basis functions
:nact:      total number of active orbitals (nacto+nactv)
(abbreviated as na)
:e_ea:      the energy correction for SEA
:civ_ea:    the CI amplitudes from a given EOM model
:alpha:     number of unpaired electrons
:t_p:      the pCCD pair amplitudes (T_p)
:t_1:       the CCSD T_1 amplitudes
:t_2:       the CCSD T_2 amplitudes


Indexing convention:
:i,j,k,..: occupied orbitals of principal configuration (alpha spin)
:a,b,c,..: virtual orbitals of principal configuration (alpha spin)
:p,q,r,..: general indices (occupied, virtual; alpha spin)

Abbreviations used (if not mentioned in doc-strings; all ERI are in
physicists' notation):
:<pq||rs>: <pq|rs>-<pq|sr>
"""

from __future__ import annotations

from functools import partial
from typing import Any

from pybest.auxmat import get_fock_matrix
from pybest.ea_eom.sea_base import RSEACC1
from pybest.linalg import (
    CholeskyFourIndex,
    CholeskyLinalgFactory,
    DenseFourIndex,
    DenseOneIndex,
    DenseThreeIndex,
    DenseTwoIndex,
)
from pybest.log import timer


class SEACCD1(RSEACC1):
    """
    Restricted Single Electron Attachment Equation of Motion Coupled Cluster (RSEACC1)

    This class implements the EA-EOM-CCD model for a CCD reference function with one
    unpaired electron (S_z = 0.5). It provides methods to define and manipulate the
    effective Hamiltonian and related computations.

    Args:
        RSEACC1 (object): The RSEACC1 class object for EA-EOM-CCD computations.

    Returns:
        object: An initialized instance of the RSEACC1 class.

    Methods:
        set_hamiltonian: Calculates the effective Hamiltonian (stores at most O(o^2v^2)).
        compute_h_diag: Computes the pre-conditioner used by the Davidson algorithm.
        build_subspace_hamiltonian: Constructs the subspace Hamiltonian for diagonalization.
    """

    long_name = (
        "Single Electron Attachment Equation of Motion Coupled Cluster Doubles"
    )
    acronym = "SEA-EOM-CCD"
    reference = "CCD"
    order = "EA"
    alpha = 1

    @timer.with_section(f"EA{reference}1: H_diag")
    def compute_h_diag(self, *args: Any) -> DenseOneIndex:
        """Compute the diagonal of the effective Hamiltonian for pre-conditioning.

        This method is used by the Davidson module to provide a pre-conditioner,
        which helps accelerate the convergence of eigenvalue calculations.
        The `args` parameter is required by the Davidson module but is not directly
        utilized within this method.

        **Arguments:**

        args:
            required for the Davidson module (not used here)

        Returns:
            DenseOneIndex: The diagonal of the effective Hamiltonian as a DenseOneIndex object.
        """
        h_diag = self.lf.create_one_index(self.dimension, label="h_diag")
        #
        # Get auxiliary matrices
        #
        nactv = self.occ_model.nactv[0]
        #
        # H_a,a = I_bd(a,a)
        #
        # I_bd(a,a) = I_bd_aa
        I_bd = self.from_cache("I_bd")
        I_bd_aa = I_bd.copy_diagonal()
        h_diag.assign(I_bd_aa, end0=nactv)
        #
        # 2-particle terms
        #
        if self.n_particle_operator >= 2:
            self.get_2_particle_terms_h_diag(h_diag)
        return h_diag

    def compute_h_diag_term_abcd(self, h_diag_d: DenseThreeIndex) -> None:
        """Compute the diagonal term involving the vvvv block.

        Args:
            h_diag_d (DenseThreeIndex): The current value of the diagonal, represented as a DenseThreeIndex object.
        """
        if isinstance(self.lf, CholeskyLinalgFactory):
            gvvvv = self.from_cache("gvvvv")
            goovv = self.from_cache("goovv")
            t_2 = self.checkpoint["t_2"]
            #
            # I_abcd = I_abab
            #
            # I_abcd = [ 1/4<ab||cd> + 1/8<km||dc> (t_makb - t_kamb) ]
            #
            # 1/4<ab||cd> -> c=a,d=b -> <ab|ab>
            tmp_ab = gvvvv.contract("abab->ab", factor=0.25)
            # Exchange term (-1/4<ab|ba>)
            gvvvv.contract("abba->ab", out=tmp_ab, factor=-0.25)
            # 1/8 <mk||cd> ( t_makb - t_kamb) = 1/4 <mk||cd> t_makb -> c=a,d=b
            # --> 1/4 <mk||ab> t_makb
            goovv.contract("abcd,acbd->cd", t_2, out=tmp_ab, factor=0.25)
            # Exchange term (-1/4 <mk|ba>)
            goovv.contract("abcd,adbc->dc", t_2, out=tmp_ab, factor=-0.25)

            tmp_ab.expand("ab->abc", out=h_diag_d, factor=1.0)
            tmp_ab.__del__()

        else:
            I_abcd = self.from_cache("I_abcd")
            H_ab = I_abcd.contract("abab->ab", factor=1.0)
            if self.dump_cache:
                self.cache.dump("I_abcd")
            H_ab.expand("ab->abc", out=h_diag_d, factor=1.0)  # ab->abj

    def compute_h_diag_term_aBcD(self, h_diag_d: DenseThreeIndex) -> None:
        """Compute the diagonal term involving the vvvv block.

        Args:
            h_diag_d (DenseThreeIndex): The current value of the diagonal, represented as a DenseThreeIndex object.
        """
        if isinstance(self.lf, CholeskyLinalgFactory):
            gvvvv = self.from_cache("gvvvv")
            goovv = self.from_cache("goovv")
            t_2 = self.checkpoint["t_2"]
            #
            # I_aBcD = I_aBaB
            #
            # I_aBcD = [ <ab|cd> + <km|cd> t_kamb ]
            #
            # <ab|cd> -> c=a , d=b -> <ab|ab>
            tmp_ab = gvvvv.contract("abab->ab", factor=1.0)
            # <km|cd> t_kamb -> c=a , d=b -> <km|ab> t_kamb
            goovv.contract("abcd,acbd->cd", t_2, out=tmp_ab, factor=1.0)

            tmp_ab.expand("ab->abc", out=h_diag_d, factor=1.0)
            tmp_ab.__del__()

        else:
            I_aBcD = self.from_cache("I_aBcD")
            H_aB = I_aBcD.contract("abab->ab", factor=1.0)
            if self.dump_cache:
                self.cache.dump("I_aBcD")
            H_aB.expand("ab->abc", out=h_diag_d, factor=1.0)  # ab->abj

    def get_2_particle_terms_h_diag(self, h_diag: DenseThreeIndex) -> None:
        """Determine all contributions involving two-particle operators in the spin-dependent representation.

        Args:
            h_diag (DenseThreeIndex): The diagonal elements of the Hamiltonian.
        """
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        #
        # Get auxiliary matrices
        #
        goovv = self.from_cache("goovv")
        t_iajb = self.checkpoint["t_2"]
        #
        # H_abj,abj = P^+_(ab) * [I_bd(b,b) + 1/2 I_jm(j,j) + I_abcd(a,b,a,b) + I_jbkc(j,b,j,b)
        #               - 1/4 <mj||ab>(t_majb - t_jamb)]
        #
        h_abj = self.lf.create_three_index(nactv, nactv, nacto)

        # I_bd(b,b) = I_bd_bb
        I_bd = self.from_cache("I_bd")
        I_bd.expand("bb->abc", h_abj, factor=1.0)  # bb->abj
        # 1/2 I_jm(j,j) = I_jm_jj
        I_jm = self.from_cache("I_jm")
        I_jm.expand("cc->abc", h_abj, factor=0.5)  # jj->abj
        # I_abcd(a,b,a,b) = I_abcd_abcd
        self.compute_h_diag_term_abcd(h_abj)

        # I_jbkc(j,b,j,b) = I_jbkc_jbjb
        # I_jbkc = I_jbKC + I_JaKc --> I_jbkc_jbjb = I_jbKC_jbjb + I_JaKc_jbjb
        I_jbKC = self.from_cache("I_jbKC")
        I_jbKC_jbjb = I_jbKC.contract("abab->ab")
        if self.dump_cache:
            self.cache.dump("I_jbKC")
        I_JaKc = self.from_cache("I_JaKc")
        I_JaKc_JaJa = I_JaKc.contract("abab->ab")
        if self.dump_cache:
            self.cache.dump("I_JaKc")
        I_jbKC_jbjb.expand("cb->abc", out=h_abj, factor=1.0)
        I_JaKc_JaJa.expand("ca->abc", out=h_abj, factor=1.0)

        # - 1/4 <mj||ab> * t_majb
        goovv.contract("abcd,acbd->cdb", t_iajb, factor=-0.25, out=h_abj)
        # Exchange term :- 1/4  <mj|ba> * t_majb
        goovv.contract("abcd,adbc->dcb", t_iajb, factor=+0.25, out=h_abj)

        # + 1/4 <mj||ab> * t_jamb
        goovv.contract("abcd,bcad->cdb", t_iajb, factor=+0.25, out=h_abj)
        # Exchange term : (-1/4  <mj|ba> * t_jamb)
        goovv.contract("abcd,bdac->dcb", t_iajb, factor=-0.25, out=h_abj)

        # P(ab)
        h_abj.iadd_transpose((1, 0, 2))

        # Assign using mask
        #
        end_3aa = nactv + (nactv - 1) * nactv * nacto // 2
        h_diag.assign(
            h_abj.array[self.get_mask(0)], begin0=nactv, end0=end_3aa
        )
        #
        # H_aBJ,aBJ = I_bd(b,b) + I_bd(b,b) + I_jm(j,j) + I_aBcD(a,b,a,b)
        #               + I_jbkc(j,b,j,b) + I_JaKc(j,a,j,a)  - <mj|ab> * t_majb
        #
        h_abj.clear()

        # I_bd(b,b) = I_bd_bb
        I_bd.expand("bb->abc", out=h_abj, factor=1.0)

        # I_bd(a,a) = I_bd_aa
        I_bd.expand("aa->abc", out=h_abj, factor=1.0)

        # I_jm(j,j) = I_jm_jj
        I_jm.expand("cc->abc", out=h_abj, factor=1.0)

        # I_aBcD(a,b,a,b) = I_aBcD_abab
        self.compute_h_diag_term_aBcD(h_abj)

        # I_jbkc(j,b,j,b) = I_jbkc_jbjb
        # I_jbkc = I_jbKC + I_JaKc --> I_jbkc_jbjb = I_jbKC_jbjb + I_JaKc_jbjb
        I_jbKC_jbjb.expand("cb->abc", out=h_abj, factor=1.0)
        # I_JaKc(j,b,j,b) = I_JaKc_JbJb
        I_JaKc = self.from_cache("I_JaKc")
        I_JaKc_JbJb = I_JaKc.contract("abab->ab")
        I_JaKc_JbJb.expand("cb->abc", out=h_abj, factor=1.0)

        # I_JaKc(j,a,j,a) = I_JaKc_jaja
        I_JaKc = self.from_cache("I_JaKc")
        # store as [a,j,a,j]
        I_JaKc_ajaj = I_JaKc.contract("abab->ba")
        if self.dump_cache:
            self.cache.dump("I_JaKc")
        I_JaKc_ajaj.expand("ac->abc", out=h_abj, factor=1.0)

        # - <mj|ab> * t_majb
        goovv.contract("abcd,acbd->cdb", t_iajb, factor=-1.0, out=h_abj)
        #
        # Assign using mask
        #
        h_diag.assign(h_abj, begin0=end_3aa)

    @timer.with_section(f"EA{reference}1: H_sub")
    def build_subspace_hamiltonian(
        self, b_vector: DenseOneIndex, h_diag: DenseOneIndex, *args: Any
    ) -> DenseOneIndex:
        """Construct the subspace Hamiltonian for S_z=0.5 states, used by the Davidson module.

        Args:
            b_vector (DenseOneIndex): Contains the current approximation to the CI coefficients.
            h_diag (DenseOneIndex): Diagonal Hamiltonian elements required by the Davidson module (not used here).
            args (Any): Additional arguments passed by the Davidson module (not used here).

        Returns:
            DenseOneIndex: The constructed subspace Hamiltonian.
        """
        #
        # Get ranges
        #
        nactv = self.occ_model.nactv[0]
        #
        # Calculate sigma vector (H.b_vector)_a
        #
        # output
        #
        s_1 = self.lf.create_one_index(nactv)
        to_s_1 = {"out": s_1, "clear": False}
        sigma = self.lf.create_one_index(self.dimension)
        #
        # Input
        #
        b_1 = self.lf.create_one_index(nactv)
        #
        # Assign R_a
        #
        b_1.assign(b_vector, end1=nactv)
        #
        # R_a
        #
        # (1) I_bd rd
        I_bd = self.from_cache("I_bd")
        I_bd.contract("ab,b->a", b_1, **to_s_1)
        #
        # R_abj/R_aBJ including coupling terms
        #
        if self.n_particle_operator >= 2:
            self.get_2_particle_terms(b_1, s_1, b_vector, sigma)
        #
        # Assign to sigma vector
        #
        sigma.assign(s_1, begin0=0, end0=nactv)
        del s_1

        return sigma

    def get_2_particle_terms(
        self,
        b_1: DenseOneIndex,
        s_1: DenseOneIndex,
        b_vector: DenseOneIndex,
        sigma: DenseOneIndex,
    ) -> None:
        """Determine all contributions involving two-particle operators, including:
            * Coupling terms to R_a
            * R_abj
            * R_aBJ

        Args:
            b_1 (DenseOneIndex): B vector used in Davidson diagonalization.
            s_1 (DenseOneIndex): Sigma vector used in Davidson diagonalization.
            b_vector (DenseOneIndex): B vector used in Davidson diagonalization..
            sigma (DenseOneIndex): Sigma vector used in Davidson diagonalization.
        """
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        #
        # Calculate sigma vector (H.b_vector) of 2-particle terms
        #
        # output
        #
        s_3 = self.lf.create_three_index(nactv, nactv, nacto)
        #
        # Input
        #
        b_3aa = self.lf.create_three_index(nactv, nactv, nacto)
        b_3ab = self.lf.create_three_index(nactv, nactv, nacto)
        #
        # Final index of b_3aa in b_vector
        #
        end = nactv + (nactv - 1) * nactv * nacto // 2
        #
        # Reshape b_vector
        #
        # Assign rabj
        #
        b_3aa.assign(
            b_vector, begin3=nactv, end3=end, ind0=self.get_index_of_mask(0)
        )
        b_3aa.iadd_transpose((1, 0, 2), factor=-1.0)
        #
        # Assign raBJ
        #
        b_3ab.assign(b_vector, begin3=end)
        #
        # Get coupling terms to R_a
        #
        self.get_2_particle_r_a_terms(b_3aa, b_3ab, s_1)
        #
        # R_abj
        #
        if nactv > 1:
            self.get_2_particle_r_3ss_terms(b_1, b_3aa, b_3ab, s_3)
            #
            # Assign to sigma vector using mask
            #
            sigma.assign(s_3.array[self.get_mask(0)], begin0=nactv, end0=end)
        #
        # R_aBJ
        #
        self.get_2_particle_r_3os_terms(b_1, b_3aa, b_3ab, s_3)
        #
        # Assign to sigma vector
        #
        sigma.assign(s_3, begin0=end)

    def get_2_particle_r_a_terms(
        self,
        b_3aa: DenseThreeIndex,
        b_3ab: DenseThreeIndex,
        s_1: DenseOneIndex,
    ) -> None:
        """Determine contributions involving two-particle operators, specifically coupling terms to R_a.

        Args:
            b_3aa (DenseThreeIndex): B vector corresponding to one R operator used in Davidson diagonalization.
            b_3ab (DenseThreeIndex): B vector corresponding to another R operator used in Davidson diagonalization.
            s_1 (DenseOneIndex): Sigma vector corresponding to R_a used in Davidson diagonalization.
        """
        to_s_1 = {"out": s_1, "clear": False}
        #
        # Get auxiliary matrices
        #
        gvovv = self.from_cache("gvovv")
        # (2) + 1/2 * <ak||dc> * r_dcK
        # + 1/2 sum_kcd <ak|dc> * r_dcK => s_1[a]
        gvovv.contract("abcd,cdb->a", b_3aa, factor=+0.5, **to_s_1)
        # Exchange term :- 1/2  <ak|cd> * r_dcK
        # - 1/2 sum_kcd <ak|cd> * r_dcK => s_1[a]
        gvovv.contract("abcd,dcb->a", b_3aa, factor=-0.5, **to_s_1)
        # (4)  <ak̅|dc̅> * r_dc̅k̅
        # sum_kcd <ak̅|dc̅> * r_dc̅k̅ => s_1[a]
        gvovv.contract("abcd,cdb->a", b_3ab, factor=+1.0, **to_s_1)
        # (6) I_ck * r_ack
        I_ck = self.from_cache("I_ck")
        b_3aa.contract("abc,bc->a", I_ck, **to_s_1, factor=1.0)
        # (7) I_ck * r_ac̅k̅
        b_3ab.contract("abc,bc->a", I_ck, **to_s_1, factor=1.0)

    def get_2_particle_r_3ss_terms(
        self,
        b_1: DenseOneIndex,
        b_3aa: DenseThreeIndex,
        b_3ab: DenseThreeIndex,
        s_3: DenseThreeIndex,
    ) -> None:
        """Determine contributions involving two-particle operators, specifically R_abj (same spin - ss).

        Args:
            b_1 (DenseOneIndex): B vector corresponding to an R operator used in Davidson diagonalization.
            b_3aa (DenseThreeIndex): B vector corresponding to one R operator used in Davidson diagonalization.
            b_3ab (DenseThreeIndex): B vector corresponding to another R operator used in Davidson diagonalization.
            s_3 (DenseThreeIndex): Sigma vector corresponding to R_abj used in Davidson diagonalization.
        """
        s_3.clear()
        to_s_3 = {"out": s_3, "clear": False}
        #
        # Get auxiliary matrices
        #
        goovv = self.from_cache("goovv")
        t_iajb = self.checkpoint["t_2"]
        # (8) I_abjd * r_d
        self.get_effective_hamiltonian_term_abjd(b_1, s_3)
        # (9) I_bd * r_adj
        I_bd = self.from_cache("I_bd")
        b_3aa.contract("abc,db->adc", I_bd, **to_s_3, factor=1.0)
        # (10) 1/2(I_jm * r_abm)
        I_jm = self.from_cache("I_jm")
        b_3aa.contract("abc,dc->abd", I_jm, **to_s_3, factor=0.5)
        # (11) I_abcd * r_c
        self.get_effective_hamiltonian_term_abcd(b_3aa, s_3)
        # (12) I_jbkc * r_ack
        #      = [ I_jbKC + I_JaKc[j,b,k,c] ] * r_ack
        I_jbKC = self.from_cache("I_jbKC")
        I_jbKC.contract("abcd,edc->eba", b_3aa, **to_s_3, factor=1.0)
        # (13) I_jbKC *  r_aC̅K̅
        I_jbKC.contract("abcd,edc->eba", b_3ab, **to_s_3, factor=1.0)
        if self.dump_cache:
            self.cache.dump("I_jbKC")
        # @(12): I_JaKc[j,b,k,c] * r_ack
        I_JaKc = self.from_cache("I_JaKc")
        I_JaKc.contract("abcd,edc->eba", b_3aa, **to_s_3, factor=1.0)
        if self.dump_cache:
            self.cache.dump("I_JaKc")
        # (14) - 1/4 * <mk||dc> * t_majb * r_dcK
        # (15) + 1/4 * <mk||dc> * t_jamb * r_dcK
        # (16) - 1/2 * <mk̅|dc̅> * t_majb * r_dCK
        # (17) + 1/2 * <mk̅|dc̅> * t_jamb * r_dCK
        # with tmp[m] = - 1/4 * <mk||dc> r_dcK - 1/2 * <mk̅|dc̅> * r_dCK
        # => (14) + (15) + (16) + (17) = tmp[m] * [ t_majb - t_jamb ]

        # - 1/4 sum_kcd <mk||dc> * r_dcK => [m]
        tmp = goovv.contract("abcd,cdb->a", b_3aa, factor=-0.25)
        goovv.contract("abcd,dcb->a", b_3aa, factor=+0.25, out=tmp)
        # - 1/2 sum_kcd <mk̅|dc̅> * r_dCK => [m]
        goovv.contract("abcd,cdb->a", b_3ab, factor=-0.5, out=tmp)
        # tmp[m] * t_majb
        t_iajb.contract("abcd,a->bdc", tmp, **to_s_3)
        # - tmp[m] * t_jamb
        t_iajb.contract("abcd,c->bda", tmp, **to_s_3, factor=-1.0)
        tmp.__del__()
        #
        # P(ab)
        #
        s_3.iadd_transpose((1, 0, 2), factor=-1.0)

    def get_effective_hamiltonian_term_abjd(
        self, b_1: DenseOneIndex, s_3: DenseThreeIndex
    ) -> None:
        """Compute the effective Hamiltonian term involving a vvvv block.

        Args:
            b_1 (DenseOneIndex): The current approximation to the CI coefficient.
            s_3 (DenseThreeIndex): The output sigma vector.
        """
        if isinstance(self.lf, CholeskyLinalgFactory):
            ov = self.get_range("ov")
            fock = self.from_cache("fock")
            f_ov = fock.contract("ab->ab", factor=1.0, **ov)

            vvo = self.get_range("vvo")
            vov4 = self.get_range("vov", 4)
            ooo4 = self.get_range("ooo", 4)
            gnnnv = self.from_cache("gnnnv")
            gnnvn = self.from_cache("gnnvn")
            gnvnn = self.from_cache("gnvnn")
            t_iajb = self.checkpoint["t_2"]
            #
            # I_abjd *r_d = [ 1/2<ab||dj> - 1/2 f_kd(t_kajb - t_jakb) + <ak||dc>(t_jbkc - t_jckb )
            #           + <ak|dc>t_jbkc + 1/4 <mk||dj>(t_makb - t_kamb) ] *r_d
            #
            # I_abj
            #
            # <pq|rd>.r^d -> tmp[p,q,r]
            tmp_aaan = gnnnv.contract("abcd,d->abc", b_1)
            # <pq|dr>.r^d -> tmp[p,q,r]
            tmp_aana = gnnvn.contract("abcd,c->abd", b_1)
            # <pd|qr>.r^d -> tmp[p,q,r]
            tmp_anaa = gnvnn.contract("abcd,b->acd", b_1)
            tmp_f = f_ov.contract("ab,b->a", b_1)
            # 1/2 <ab||dj> *r_d -> 1/2 <abj>
            tmp_aana.contract("abc->abc", factor=0.5, **vvo, out=s_3)
            # Exchange term : 1/2 <ab|jd> *r_d -> -1/2 <abj>
            tmp_aaan.contract("abc->abc", factor=-0.5, **vvo, out=s_3)
            # [ - 1/2 f_k * t_kajb  ] *r_d
            t_iajb.contract("abcd,a->bdc", tmp_f, factor=-0.5, out=s_3)
            # [ + 1/2 f_k * t_jakb  ] *r_d
            t_iajb.contract("abcd,c->bda", tmp_f, factor=+0.5, out=s_3)
            tmp_f.__del__()
            # <ak||dc>(t_jbkc - t_jckb )  + <ak|dc>t_jbkc
            # ( <ak||dc>t_jbkc + <ak|dc>t_jbkc )*r_d
            t_iajb.contract(
                "abcd,ecd->eba", tmp_aana, factor=2, **vov4, out=s_3
            )
            # Exchange term
            t_iajb.contract(
                "abcd,ecd->eba", tmp_aaan, factor=-1, **vov4, out=s_3
            )
            # - <ak||dc>t_jckb *r_d -> - <akc>t_jckb
            t_iajb.contract(
                "abcd,ecb->eda", tmp_aana, factor=-1, **vov4, out=s_3
            )
            # Exchange term
            t_iajb.contract(
                "abcd,ecb->eda", tmp_aaan, factor=1, **vov4, out=s_3
            )

            # 1/4 <mk||dj> (t_makb - t_kamb)
            #     = 1/4 <mk||dj> t_makb - 1/4 <mk||dj> t_kamb
            #     = 1/4 <mk||dj> t_makb + 1/4 <mk||dj> t_makb
            #     = 1/2 <mk||dj> t_makb
            # 1/2 <mk||dj> t_makb *r_d -> 1/2 <mkj> t_makb
            t_iajb.contract(
                "abcd,ace->bde", tmp_aana, factor=0.5, **ooo4, out=s_3
            )
            # Exchange term
            t_iajb.contract(
                "abcd,ace->bde", tmp_aaan, factor=-0.5, **ooo4, out=s_3
            )

            tmp_aaan.__del__()
            tmp_aana.__del__()
            tmp_anaa.__del__()

        else:
            to_s_3 = {"out": s_3, "clear": False}
            # (8) I_abjd * r_d
            I_abjd = self.from_cache("I_abjd")
            I_abjd.contract("abcd,d->abc", b_1, **to_s_3, factor=1.0)
            if self.dump_cache:
                self.cache.dump("I_abjd")

    def get_effective_hamiltonian_term_abcd(
        self, b_3aa: DenseThreeIndex, s_3: DenseThreeIndex
    ) -> None:
        """Compute the effective Hamiltonian term involving a vvvv block.

        Args:
            b_3aa (DenseThreeIndex): The current approximation to the CI coefficient.
            s_3 (DenseThreeIndex): The output sigma vector.
        """
        if isinstance(self.lf, CholeskyLinalgFactory):
            vvo = self.get_range("vvo")
            ooo4 = self.get_range("ooo", 4)
            gnnvv = self.from_cache("gnnvv")
            t_iajb = self.checkpoint["t_2"]
            #
            # I_abcd *r_cdj = [ 1/4<ab||cd> + 1/8<km||dc> (t_makb - t_kamb) ] *r_cdj
            #
            # I_abc
            #
            # <pq|cd>.r^cdj -> tmp[p,q,j]
            tmp_aacd = gnnvv.contract("abcd,cdj->abj", b_3aa)
            # <pq|dd>.r^cdj -> tmp[p,q,j]
            tmp_aadc = gnnvv.contract("abdc,cdj->abj", b_3aa)
            # 1/4<ab||cd> *r_cdj  -> 1/4 <abj>
            tmp_aacd.contract("abc->abc", factor=0.25, **vvo, out=s_3)
            # Exchange term
            tmp_aadc.contract("abc->abc", factor=-0.25, **vvo, out=s_3)
            # <km||dc> = <mk||cd>
            # [ 1/8 <mk||cd> ( t_makb - t_kamb) = 1/4 <mk||cd> t_makb ] *r_cdj
            # 1/8 <mkj> ( t_makb - t_kamb) = 1/4 <mkj> t_makb ]
            t_iajb.contract(
                "abcd,ace->bde", tmp_aacd, factor=0.25, **ooo4, out=s_3
            )
            # Exchange term
            t_iajb.contract(
                "abcd,ace->bde", tmp_aadc, factor=-0.25, **ooo4, out=s_3
            )

            tmp_aacd.__del__()
            tmp_aadc.__del__()

        else:
            to_s_3 = {"out": s_3, "clear": False}
            # (11) I_abcd * r_cdj
            I_abcd = self.from_cache("I_abcd")
            I_abcd.contract("abcd,cde->abe", b_3aa, **to_s_3, factor=1.0)
            if self.dump_cache:
                self.cache.dump("I_abcd")

    def get_2_particle_r_3os_terms(
        self,
        b_1: DenseOneIndex,
        b_3aa: DenseThreeIndex,
        b_3ab: DenseThreeIndex,
        s_3: DenseThreeIndex,
    ) -> None:
        """Determine contributions involving two-particle operators, specifically R_aBJ (opposite spin - os).

        Args:
            b_1 (DenseOneIndex): B vector corresponding to an R operator used in Davidson diagonalization.
            b_3aa (DenseThreeIndex): B vector corresponding to one R operator used in Davidson diagonalization.
            b_3ab (DenseThreeIndex): B vector corresponding to another R operator used in Davidson diagonalization.
            s_3 (DenseThreeIndex): Sigma vector corresponding to R_aBJ used in Davidson diagonalization.
        """
        s_3.clear()
        to_s_3 = {"out": s_3, "clear": False}
        #
        # Get auxiliary matrices
        #
        goovv = self.from_cache("goovv")
        t_iajb = self.checkpoint["t_2"]
        # (18) I_aBJd * r_d
        self.get_effective_hamiltonian_term_aBJd(b_1, s_3)
        # (19) I_bd * r_aDJ
        I_bd = self.from_cache("I_bd")
        b_3ab.contract("abc,db->adc", I_bd, **to_s_3, factor=1.0)
        # (20) I_bd(a,d) * r_dBJ
        I_bd = self.from_cache("I_bd")
        b_3ab.contract("abc,da->dbc", I_bd, **to_s_3, factor=1.0)
        # (21) I_jm * r_aBM
        I_jm = self.from_cache("I_jm")
        b_3ab.contract("abc,dc->abd", I_jm, **to_s_3, factor=1.0)
        # (22) I_aBcD * r_cDJ
        self.get_effective_hamiltonian_term_aBcD(b_3ab, s_3)
        # (23) I_jbKC * r_ack
        I_jbKC = self.from_cache("I_jbKC")
        I_jbKC.contract("abcd,edc->eba", b_3aa, **to_s_3, factor=1.0)
        # (24)  ( I_jbKC[j,b,k,c] + I_JaKc[j,b,k,c] ) * r_aCK
        # I_jbKC[j,b,k,c] * r_aCK
        # I_JaKc[j,b,k,c] * r_aCK
        I_JaKc = self.from_cache("I_JaKc")
        I_JaKc.contract("abcd,edc->eba", b_3ab, **to_s_3, factor=1.0)
        I_jbKC.contract("abcd,edc->eba", b_3ab, **to_s_3, factor=1.0)
        if self.dump_cache:
            self.cache.dump("I_jbKC")
        # (25) I_JaKc *  r_cBK
        I_JaKc.contract("abcd,dec->bea", b_3ab, **to_s_3, factor=1.0)
        if self.dump_cache:
            self.cache.dump("I_JaKc")
        # (26) - 1/2 * <mk||dc> * t_majb * r_dck
        # - 1/2 sum_kcd <mk||dc> * r_dck => [m]
        tmp = goovv.contract("abcd,cdb->a", b_3aa, factor=-0.5)
        goovv.contract("abcd,dcb->a", b_3aa, factor=0.5, out=tmp)
        # [m] * t_majb (done below)
        # (27) -  <mk̅|dc̅> * t_majb * r_dKC
        # - sum_kcd <mk̅|dc̅> * r_dKC => [m]
        goovv.contract("abcd,cdb->a", b_3ab, factor=-1.0, out=tmp)
        # [m] * t_majb
        t_iajb.contract("abcd,a->bdc", tmp, **to_s_3)
        tmp.__del__()

    def get_effective_hamiltonian_term_aBJd(
        self, b_1: DenseOneIndex, s_3: DenseThreeIndex
    ) -> None:
        """Compute the effective Hamiltonian term involving a vvvv block.

        Args:
            b_1 (DenseOneIndex): The current approximation to the CI coefficient.
            s_3 (DenseThreeIndex): The output sigma vector.
        """
        if isinstance(self.lf, CholeskyLinalgFactory):
            ov = self.get_range("ov")
            vvo = self.get_range("vvo")
            vov4 = self.get_range("vov", 4)
            ovv4 = self.get_range("ovv", 4)
            ooo4 = self.get_range("ooo", 4)
            gnnnv = self.from_cache("gnnnv")
            gnnvn = self.from_cache("gnnvn")
            t_iajb = self.checkpoint["t_2"]
            fock = self.from_cache("fock")
            f_ov = fock.contract("ab->ab", factor=1.0, **ov)
            #
            # I_aBJd *r_d  = [ <ab|dj> - f_kd * t_kajb + <ak||dc>(t_jbkc )
            #           + <ak|dc>(t_jbkc - t_kbjc ) - <mb|dc>t_majc + <mk|dj>t_makb ] *r_d
            #
            # I_aBJ
            #
            # <pq|rd>.r^d -> tmp[p,q,r]
            tmp_aaan = gnnnv.contract("abcd,d->abc", b_1)
            # <pq|dr>.r^d -> tmp[p,q,r]
            tmp_aana = gnnvn.contract("abcd,c->abd", b_1)
            tmp_f = f_ov.contract("ab,b->a", b_1)
            # <ab|dj> *r_d  -> <abj>
            tmp_aana.contract("abc->abc", factor=1.0, **vvo, out=s_3)
            # [-f_k * t_kajb ] *r_d
            t_iajb.contract("abcd,a->bdc", tmp_f, factor=-1.0, out=s_3)
            tmp_f.__del__()
            # [ <ak||dc>(t_jbkc ) + <ak|dc>(t_jbkc - t_kbjc ) ] *r_d

            # <akc>t_jbkc + <akc>t_jbkc
            t_iajb.contract(
                "abcd,ecd->eba", tmp_aana, factor=2.0, **vov4, out=s_3
            )
            # Exchange term (-<akc>t_jbkc)
            t_iajb.contract(
                "abcd,ecd->eba", tmp_aaan, factor=-1.0, **vov4, out=s_3
            )
            # - <akc>t_kbjc
            t_iajb.contract(
                "abcd,ead->ebc", tmp_aana, factor=-1.0, **vov4, out=s_3
            )
            # - <mbc>t_majc
            t_iajb.contract(
                "abcd,aed->bec", tmp_aana, factor=-1.0, **ovv4, out=s_3
            )
            # <mkj>t_makb
            t_iajb.contract(
                "abcd,ace->bde", tmp_aana, factor=1.0, **ooo4, out=s_3
            )

            tmp_aaan.__del__()
            tmp_aana.__del__()

        else:
            to_s_3 = {"out": s_3, "clear": False}
            # (18) I_aBJd * r_d
            I_aBJd = self.from_cache("I_aBJd")
            I_aBJd.contract("abcd,d->abc", b_1, **to_s_3, factor=1.0)
            if self.dump_cache:
                self.cache.dump("I_aBJd")

    def get_effective_hamiltonian_term_aBcD(
        self, b_3ab: DenseThreeIndex, s_3: DenseThreeIndex
    ) -> None:
        """Compute the effective Hamiltonian term involving a vvvv block.

        Args:
            b_3ab (DenseThreeIndex): The current approximation to the CI coefficient.
            s_3 (DenseThreeIndex): The output sigma vector.
        """
        if isinstance(self.lf, CholeskyLinalgFactory):
            ooo4 = self.get_range("ooo", 4)
            vvo = self.get_range("vvo")
            gnnvv = self.from_cache("gnnvv")
            t_iajb = self.checkpoint["t_2"]
            #
            # I_aBcD *r_cDJ = [ <ab|cd> + <km|cd> t_kamb ] *r_cDJ
            #
            # I_aBc
            #
            # <pq|cd>.r^cdj -> tmp[p,q,j]
            tmp_aacd = gnnvv.contract("abcd,cdj->abj", b_3ab)
            # <ab|cd> *r_cDJ  -> <abj>
            tmp_aacd.contract("abc->abc", factor=1.0, **vvo, out=s_3)
            # <km|cd> t_kamb *r_cDJ -> <kmj> t_kamb
            t_iajb.contract(
                "abcd,ace->bde", tmp_aacd, factor=1.0, **ooo4, out=s_3
            )
            tmp_aacd.__del__()

        else:
            to_s_3 = {"out": s_3, "clear": False}
            # (22) I_aBcD * r_cDJ
            I_aBcD = self.from_cache("I_aBcD")
            I_aBcD.contract("abcd,cde->abe", b_3ab, **to_s_3, factor=1.0)
            if self.dump_cache:
                self.cache.dump("I_aBcD")

    @timer.with_section(f"EA{reference}1: H_eff")
    def set_hamiltonian(
        self,
        mo1: DenseTwoIndex,
        mo2: DenseFourIndex,
    ) -> None:
        """Derive all effective Hamiltonian terms, such as fock_pq/f: mo1_pq + sum_m(2<pm|qm> - <pm|mq>).

        Args:
            mo1 (DenseTwoIndex): The one-electron integrals.
            mo2 (DenseFourIndex): The two-electron integrals.

        Returns:
            None: This method does not return any value, but modifies the Hamiltonian terms internally.
        """
        nacto = self.occ_model.nacto[0]
        nact = self.occ_model.nact[0]
        nactv = self.occ_model.nactv[0]
        #
        # Get ranges
        #
        vv = self.get_range("vv")
        oo = self.get_range("oo")
        ov = self.get_range("ov")
        ooov = self.get_range("ooov")
        oovo = self.get_range("oovo")
        oovv = self.get_range("oovv")
        ovov = self.get_range("ovov")
        vovv = self.get_range("vovv")
        ovvv = self.get_range("ovvv")
        vvov = self.get_range("vvov")
        vvvo = self.get_range("vvvo")
        vvvv = self.get_range("vvvv")
        fock = self.init_cache("fock", nact, nact)
        get_fock_matrix(fock, mo1, mo2, nacto)
        f_vv = fock.contract("ab->ab", factor=1.0, **vv)
        f_ov = fock.contract("ab->ab", factor=1.0, **ov)
        f_oo = fock.contract("ab->ab", factor=1.0, **oo)
        t_iajb = self.checkpoint["t_2"]
        #
        # Get effective Hamiltonian elements
        #
        # I_abjd
        #
        if not isinstance(mo2, CholeskyFourIndex):
            # don't calculate Cholesky blocks of size >= ov^3
            I_abjd = self.init_cache("I_abjd", nactv, nactv, nacto, nactv)
            #
            # I_abjd = [ 1/2<ab||dj> - 1/2 f_kd(t_kajb - t_jakb) + <ak||dc>(t_jbkc - t_jckb )
            #           + <ak|dc>t_jbkc + 1/4 <mk|dj>(t_makb - t_kamb) ]
            #
            # 1/2 <ab||dj>
            mo2.contract("abcd->abdc", factor=0.5, **vvvo, out=I_abjd)
            # Exchange term : 1/2 <ab|jd>
            mo2.contract("abcd->abcd", factor=-0.5, **vvov, out=I_abjd)
            # - 1/2 f_kd * t_kajb
            t_iajb.contract("abcd,ae->bdce", f_ov, factor=-0.5, out=I_abjd)
            # + 1/2 f_kd * t_jakb
            t_iajb.contract("abcd,ce->bdae", f_ov, factor=+0.5, out=I_abjd)
            # <ak||dc>(t_jbkc - t_jckb )  + <ak|dc>t_jbkc

            # <ak||dc>t_jbkc + <ak|dc>t_jbkc
            mo2.contract(
                "abcd,efbd->afec", t_iajb, factor=2, **vovv, out=I_abjd
            )
            # Exchange term
            mo2.contract(
                "abcd,efbc->afed", t_iajb, factor=-1, **vovv, out=I_abjd
            )
            # - <ak||dc>t_jckb
            mo2.contract(
                "abcd,edbf->afec", t_iajb, factor=-1, **vovv, out=I_abjd
            )
            # Exchange term
            mo2.contract(
                "abcd,ecbf->afed", t_iajb, factor=1, **vovv, out=I_abjd
            )

            # 1/4 <mk||dj> (t_makb - t_kamb)
            #     = 1/4 <mk||dj> t_makb - 1/4 <mk||dj> t_kamb
            #     = 1/4 <mk||dj> t_makb + 1/4 <mk||dj> t_makb
            #     = 1/2 <mk||dj> t_makb
            mo2.contract(
                "abcd,aebf->efdc", t_iajb, factor=0.5, **oovo, out=I_abjd
            )
            # Exchange term (-1/2 <mk|jd> t_makb)
            mo2.contract(
                "abcd,aebf->efcd", t_iajb, factor=-0.5, **ooov, out=I_abjd
            )
            if self.dump_cache:
                self.cache.dump("I_abjd")
        #
        # I_aBJd
        #
        if not isinstance(mo2, CholeskyFourIndex):
            # don't calculate Cholesky blocks of size >= ov^3
            I_aBJd = self.init_cache("I_aBJd", nactv, nactv, nacto, nactv)
            #
            # I_aBJd = [ <ab|dj> - f_kd * t_kajb + <ak||dc>(t_jbkc )
            #           + <ak|dc>(t_jbkc - t_kbjc ) - <mb|dc>t_majc + <mk|dj>t_makb ]
            #
            # <ab|dj>
            mo2.contract("abcd->abdc", factor=1.0, **vvvo, out=I_aBJd)
            # -f_kd * t_kajb
            t_iajb.contract("abcd,ae->bdce", f_ov, factor=-1.0, out=I_aBJd)
            # <ak||dc>(t_jbkc ) + <ak|dc>(t_jbkc - t_kbjc )

            # <ak||dc>t_jbkc + <ak|dc>t_jbkc
            mo2.contract(
                "abcd,efbd->afec", t_iajb, factor=2.0, **vovv, out=I_aBJd
            )
            # Exchange term (-<ak|cd>t_jbkc)
            mo2.contract(
                "abcd,efbc->afed", t_iajb, factor=-1.0, **vovv, out=I_aBJd
            )
            # - <ak|dc>t_kbjc
            mo2.contract(
                "abcd,befd->aefc", t_iajb, factor=-1.0, **vovv, out=I_aBJd
            )
            # - <mb|dc>t_majc
            mo2.contract(
                "abcd,aefd->ebfc", t_iajb, factor=-1.0, **ovvv, out=I_aBJd
            )
            # <mk|dj>t_makb
            mo2.contract(
                "abcd,aebf->efdc", t_iajb, factor=1.0, **oovo, out=I_aBJd
            )
            if self.dump_cache:
                self.cache.dump("I_aBJd")
        #
        # I_ck
        #
        I_ck = self.init_cache("I_ck", nactv, nacto)
        # I_ck = [ f_kc ]
        # f_kc
        f_ov.contract("ab->ba", out=I_ck, factor=1.0)
        #
        # I_bd
        #
        I_bd = self.init_cache("I_bd", nactv, nactv)
        # I_bd = [ f_bd -1/2<mk||dc>(t_mbkc - t_kbmc) - <mk|dc>(t_mbkc)]
        # f_bd
        I_bd.iadd(f_vv, factor=1.0)
        # -1/2<mk||dc>(t_mbkc - t_kbmc) - <mk|dc>(t_mbkc)
        #    = - <mk||dc> t_mbkc - <mk|dc>(t_mbkc)
        mo2.contract("abcd,aebd->ec", t_iajb, factor=-2.0, **oovv, out=I_bd)
        # Exchange term
        mo2.contract("abcd,aebc->ed", t_iajb, factor=1.0, **oovv, out=I_bd)
        #
        # I_jm
        #
        I_jm = self.init_cache("I_jm", nacto, nacto)
        # I_jm = [ -f_mj -1/2<mk||dc>(t_jdkc - t_kdjc ) - <mk|dc>t_jdkc ]
        # -f_mj
        f_oo.contract("ab->ba", out=I_jm, factor=-1.0)
        # -1/2 <mk||dc> ( t_jdkc - t_jckd ) - <mk|dc>t_jdkc
        #     = -1/2 <mk||dc> t_jdkc - 1/2 <mk||dc> t_jdkc ) - <mk|dc>t_jdkc
        #     = - <mk||dc> t_jdkc - <mk|dc>t_jdkc
        mo2.contract("abcd,ecbd->ea", t_iajb, factor=-2.0, **oovv, out=I_jm)
        # Exchange term
        mo2.contract("abcd,edbc->ea", t_iajb, factor=1.0, **oovv, out=I_jm)
        #
        # I_abcd
        #
        if not isinstance(mo2, CholeskyFourIndex):
            # don't calculate Cholesky blocks of size >= ov^3
            I_abcd = self.init_cache("I_abcd", nactv, nactv, nactv, nactv)
            #
            # I_abcd = [ 1/4<ab||cd> + 1/8<km||dc> (t_makb - t_kamb)]
            #
            # 1/4<ab||cd>
            mo2.contract("abcd->abcd", factor=0.25, out=I_abcd, **vvvv)
            # Exchange term
            mo2.contract("abcd->abdc", factor=-0.25, **vvvv, out=I_abcd)
            # 1/8 <mk||cd> ( t_makb - t_kamb) = 1/4 <mk||cd> t_makb
            mo2.contract(
                "abcd,aebf->efcd", t_iajb, factor=0.25, **oovv, out=I_abcd
            )
            # Exchange term
            mo2.contract(
                "abcd,aebf->efdc", t_iajb, factor=-0.25, **oovv, out=I_abcd
            )
            if self.dump_cache:
                self.cache.dump("I_abcd")
        #
        # I_aBcD
        #
        if not isinstance(mo2, CholeskyFourIndex):
            # don't calculate Cholesky blocks of size >= ov^3
            I_aBcD = self.init_cache("I_aBcD", nactv, nactv, nactv, nactv)
            #
            # I_aBcD = [ <ab|cd> + <km|cd> t_kamb ]
            #
            # <ab|cd>
            mo2.contract("abcd->abcd", factor=1.0, **vvvv, out=I_aBcD)
            # <km|cd> t_kamb
            mo2.contract(
                "abcd,aebf->efcd", t_iajb, factor=1.0, **oovv, out=I_aBcD
            )
            if self.dump_cache:
                self.cache.dump("I_aBcD")
        #
        # I_jbKC
        #
        I_jbKC = self.init_cache("I_jbKC", nacto, nactv, nacto, nactv)
        #
        # I_jbKC = [ <Kb|Cj> + <kl|cd>(t_jbld - t_lbjd) - <kl||cd>(t_jbld) ]
        #
        # <Kb|Cj> = <Kj|Cb>
        mo2.contract("abcd->bdac", factor=1.0, **oovv, out=I_jbKC)
        # <kl|cd>(t_jbld - t_lbjd) + <kl||cd>(t_jbld)
        # ( 2 <kl|cd> - <kl|dc>) t_jbld
        mo2.contract("abcd,efbd->efac", t_iajb, factor=2.0, **oovv, out=I_jbKC)
        # Exchange term
        mo2.contract(
            "abcd,efbc->efad", t_iajb, factor=-1.0, **oovv, out=I_jbKC
        )
        # -<kl|cd>(t_lbjd)
        mo2.contract(
            "abcd,befd->feac", t_iajb, factor=-1.0, **oovv, out=I_jbKC
        )
        if self.dump_cache:
            self.cache.dump("I_jbKC")
        #
        # I_JaKc
        #
        I_JaKc = self.init_cache("I_JaKc", nacto, nactv, nacto, nactv)
        # I_JaKc = [ -<ka|jc> + <kl|dc> t_jdla ]
        # -<ka|jc>
        mo2.contract("abcd->cbad", factor=-1.0, **ovov, out=I_JaKc)
        # <kl|dc> t_jdla
        mo2.contract("abcd,ecbf->efad", t_iajb, factor=1.0, **oovv, out=I_JaKc)
        if self.dump_cache:
            self.cache.dump("I_JaKc")

        #
        # 4-Index slices of ERI
        #

        def alloc(
            arr: CholeskyFourIndex | DenseFourIndex, block: Any
        ) -> tuple[partial[CholeskyFourIndex | DenseFourIndex]]:
            """Determines the alloc keyword argument for the init_cache method.

            Args:
                arr (CholeskyFourIndex | DenseFourIndex): The array, which could be of type CholeskyFourIndex or DenseFourIndex.
                block (Any): The block specifying the range of the array.

            Returns:
                tuple: A tuple containing the partial function (view or copy) for the specified block,
                    depending on the type of the array.
            """
            # We keep one whole CholeskyFourIndex to rule them all.
            # Non-redundant blocks are accessed as views.
            if isinstance(arr, CholeskyFourIndex):
                return (partial(arr.view, **self.get_range(block)),)
            # But we store only non-redundant blocks of DenseFourIndex
            return (partial(arr.copy, **self.get_range(block)),)

        #
        # Get blocks (for the systems we can treat with Dense, it does not
        # matter that we store vvvv blocks)
        #
        slices = [
            "oovv",
            "vovv",
            "nnnv",
            "nnvn",
            "nvnn",
            "vvvv",
            "nnvv",
        ]
        for slice_ in slices:
            self.init_cache(f"g{slice_}", alloc=alloc(mo2, slice_))
        #
        # Clean up
        #
        mo1.__del__()
        mo2.__del__()


class SEAfpCCD1(SEACCD1):
    """
    Restricted Single Electron Attachment Equation of Motion Coupled Cluster Doubles
    class restricted to Single EA for a fpCCD reference function
    """

    long_name = "Single Electron Attachment Equation of Motion frozen pair Coupled Cluster Doubles"
    acronym = "SEA-EOM-fpCCD"
    reference = "fpCCD"
    order = "EA"
    alpha = 1

    disconnected_t1 = False


class SEALCCD1(SEACCD1):
    """
    Restricted Single Electron Attachment Equation of Motion Linearized Coupled Cluster Doubles
    class restricted to Single EA for a LCCD/pCCD-LCCD reference function

    This class (re)defines only the function that are unique for the EA-LCCD
    model:

        * setting/resetting the seniority 0 sector
        * redefining effective Hamiltonian elements to include only T1.Tp terms
    """

    long_name = (
        "Single Electron Attachment Equation of Motion Linearized Coupled "
        "Cluster Doubles"
    )
    acronym = "SEA-EOM-LCCD"
    reference = "LCCD"
    order = "EA"
    alpha = 1

    disconnected_t1 = False


class SEAfpLCCD1(SEACCD1):
    """
    Restricted Single Electron Attachment Equation of Motion Coupled Cluster Doubles
    class restricted to Single EA for a fpLCCD/pCCD-LCCD reference function
    and 1 unpaired electron (S_z = 0.5)
    """

    long_name = (
        "Electron Attachment Equation of Motion frozen pair Linearized Coupled "
        "Cluster Doubles"
    )
    acronym = "EA-EOM-fpLCCD"
    reference = "fpLCCD"
    order = "EA"
    alpha = 1
    disconnected_t1 = False
