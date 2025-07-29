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
"""Symmetry Adapted Perturbation theory module

Implements SAPT0(RHF) with second-quantized exchange corrections.
Current implementation consists of uncoupled amplitudes for second
order induction and dispersion.
It serves as a educational resource as well as a sandbox for prototyping
other methods related to SAPT framework.

"""

from __future__ import annotations

from typing import ClassVar

import numpy as np

# c-extension
from pybest.core import sapt_core

# package imports
from pybest.linalg import DenseOrbital, FourIndex, TwoIndex
from pybest.log import log, timer
from pybest.utility import check_type

# module imports
from .sapt_base import SAPTBase


class SAPT0(SAPTBase):
    """Uncoupled SAPT0 solver class class"""

    correction_names: ClassVar[list[str]] = [
        "E^{(10)}_{elst}",
        "E^{(10)}_{exch}(S^2)",
        "E^{(20)}_{ind},unc",
        "E^{(20)}_{exch-ind}(S^2),unc",
        "E^{(20)}_{disp},unc",
        "E^{(20)}_{exch-disp}(S^2),unc",
    ]

    @timer.with_section("SAPT0(RHF)solver")
    def solve(self):
        """Solve for SAPT0 uncoupled energy for restricted theories."""
        self.result[self.correction_names[0]] = self.elst10()
        self.result[self.correction_names[1]] = self.exch10()
        self.result[self.correction_names[2]] = self.ind20()
        self.result[self.correction_names[3]] = self.exch_ind_20()
        self.result[self.correction_names[4]] = self.disp20()
        self.result[self.correction_names[5]] = self.exch_disp_20()

        self.result["SAPT0,unc"] = np.sum(list(self.result.values()))

        self.log_summary()
        return self.result["SAPT0,unc"]

    def log_summary(self):
        """Logs out energy correction summary."""
        log.hline("~")
        log("SUMMARY OF SAPT0 ENERGY")
        log("Correction              Energy (mE_h)")
        for name in self.correction_names:
            self.log_out_correction(name, 1000 * self.result.get(name))
        log.hline("-*")
        first_order = self.result["E^{(10)}_{elst}"]
        first_order += self.result["E^{(10)}_{exch}(S^2)"]

        self.log_out_correction("E^{(10)}_{POL+EXCH}", 1000 * first_order)

        second_order_ind = self.result["E^{(20)}_{ind},unc"]
        second_order_ind += self.result["E^{(20)}_{exch-ind}(S^2),unc"]
        self.log_out_correction("E^{(20)}_{IND},unc", 1000 * second_order_ind)

        second_order_disp = self.result["E^{(20)}_{disp},unc"]
        second_order_disp += self.result["E^{(20)}_{exch-disp}(S^2),unc"]
        self.log_out_correction(
            "E^{(20)}_{DISP},unc", 1000 * second_order_disp
        )
        log("")
        self.log_out_correction(
            "E^{(20)}_{SAPT0},unc",  # noqa: RUF027
            1000 * self.result["SAPT0,unc"],
        )
        log.hline("~")

    def elst10(self):
        """
        E_{elst}^{(10)} e.q. 39 (spin summed) in
        'Many-body symmetry-adapted perturbation theory of intermolecular interactions.
        H2O and HF dimers'
        The Journal of Chemical Physics 95, 6576 (1991); doi: 10.1063/1.461528
        """
        # NOTICE: already using minimum number of integrals
        v_abab = self.get_aux_matrix("v_abab")
        va_bb = self.get_aux_matrix("va_bb")
        vb_aa = self.get_aux_matrix("vb_aa")
        v0 = self.nucnuc

        # v_abab
        tmp1_ab = v_abab.contract("abab->ab", clear=True, select="einsum")
        term1 = tmp1_ab.sum()

        # va_bb
        term2 = va_bb.trace()

        # vb_aa
        term3 = vb_aa.trace()

        # spin-orbital summation in refered equation
        return 4 * term1 + 2 * term2 + 2 * term3 + v0

    def exch10(self):
        """E_{exch}^{(10)} correction according to eq. 58. in

        'Many-body theory of exchange effects in intermolecular interactions.
        Second-quantization approach and comparison with full configuration
        interaction results',

        Journal of Chemical Physics, 100, 1312 (1994)

        SECOND-QUANTIZED APPROACH
        """
        v_rsab = self.get_aux_matrix("v_rsab")

        wb_ra = self.get_aux_matrix("wb_ra")
        wa_sb = self.get_aux_matrix("wa_sb")

        s_ab = self.get_aux_matrix("s_ab")
        s_br = self.get_aux_matrix("s_br")
        s_as = self.get_aux_matrix("s_as")

        energy_terms = []

        # first term
        tmp_ar = self.denselfA.create_two_index(self.noccA, self.nvirtA)
        s_br.contract("ab,ca->cb", s_ab, out=tmp_ar, clear=True)
        tmp_contraction1 = wb_ra.contract("ab,ba", tmp_ar)
        energy_terms.append((-2) * tmp_contraction1)
        del tmp_ar, tmp_contraction1

        # second term
        tmp_bs = self.denselfA.create_two_index(self.noccB, self.nvirtB)
        s_as.contract("ab,ac->cb", s_ab, out=tmp_bs, clear=True)
        tmp_contraction2 = wa_sb.contract("ab,ba", tmp_bs)
        energy_terms.append((-2) * tmp_contraction2)
        del tmp_bs, tmp_contraction2

        # third term
        tmp_sa = self.denselfA.create_two_index(self.nvirtB, self.noccA)
        v_rsab.contract("abcd,da->bc", s_br, out=tmp_sa, clear=True)
        tmp_contraction3 = tmp_sa.contract("ab,ba", s_as)
        energy_terms.append((-2) * tmp_contraction3)
        del tmp_sa, tmp_contraction3

        return np.sum(energy_terms)

    def ind20(self):
        """
        E_{ind}^{(20)} = E_{ind}^{20}(A<-B) + E_{ind}^{20}(B<-A)
        eq. 62 in
        'Many-body symmetry-adapted perturbation theory of intermolecular interactions.
        H2O and HF dimers'
        The Journal of Chemical Physics 95, 6576 (1991); doi: 10.1063/1.461528
        """
        wb_ra = self.get_aux_matrix("wb_ra")
        wa_sb = self.get_aux_matrix("wa_sb")
        t_ra = self.get_aux_matrix("t_ra")
        t_sb = self.get_aux_matrix("t_sb")

        # <V|Sa>
        energy1 = t_ra.contract("ab,ab", wb_ra)

        # <V|Sb>
        energy2 = t_sb.contract("ab,ab", wa_sb)
        return 2 * (energy1 + energy2)

    def exch_ind_20(self):
        """
        E_{exch-ind}^{(20)} correction according to eq. 11 in
        'Frozen core and effective core potentials in symmetry-adapted
        perturbation theory' THE JOURNAL OF CHEMICAL PHYSICS 127, 164103 2007"

        SECOND-QUANTIZED APPROACH

        **no, response**
        coupled Hartree-Fock amplitudes (C_ar and C_bs) substituted by induction
        amplitudes (t_ra and t_sb)
        """
        v_rsab = self.get_aux_matrix("v_rsab")

        t_ra = self.get_aux_matrix("t_ra")
        t_sb = self.get_aux_matrix("t_sb")

        wb_ra = self.get_aux_matrix("wb_ra")
        wa_sb = self.get_aux_matrix("wa_sb")

        s_rs = self.get_aux_matrix("s_rs")

        s_as = self.get_aux_matrix("s_as")

        s_br = self.get_aux_matrix("s_br")

        s_ab = self.get_aux_matrix("s_ab")

        terms = []
        # exch_ind A<-B
        # 2t_ar (...)
        # (...):
        #
        # - v_(r'a)(sb) S_br' S_rs
        #
        # V_r'sab S_br' S_rs
        tmp_sa = self.lfA.create_two_index(self.nvirtB, self.noccA)
        tmp_ra = self.lfA.create_two_index(self.nvirtA, self.noccA)
        v_rsab.contract("abcd,da->bc", s_br, out=tmp_sa, clear=True)
        tmp_sa.contract("ab,ca->cb", s_rs, out=tmp_ra, clear=True)

        tmp_contraction1 = -2 * t_ra.contract("ab,ab", tmp_ra)
        terms.append(tmp_contraction1)

        del tmp_sa, tmp_ra
        #
        # v_(ra')(sb) S_a's S_ba
        #
        # V_rsa'b S_a's S_ba
        tmp_rb = self.lfA.create_two_index(self.nvirtA, self.noccB)
        tmp_ra = self.lfA.create_two_index(self.nvirtA, self.noccA)
        v_rsab.contract("abcd,cb->ad", s_as, out=tmp_rb, clear=True)
        tmp_rb.contract("ab,cb->ac", s_ab, out=tmp_ra, clear=True)

        tmp_contraction2 = 2 * t_ra.contract("ab,ab", tmp_ra)
        terms.append(tmp_contraction2)

        del tmp_rb, tmp_ra
        #
        # -2 v_(ra)(sb) S_a's S_ba'
        #
        # V_rsab S_a's S_ba'
        tmp_bs = self.lfA.create_two_index(self.noccB, self.nvirtB)
        tmp_ra = self.lfA.create_two_index(self.nvirtA, self.noccA)
        s_as.contract("ab,ac->cb", s_ab, out=tmp_bs, clear=True)
        v_rsab.contract("abcd,db->ac", tmp_bs, out=tmp_ra, clear=True)

        tmp_contraction3 = -4 * t_ra.contract("ab,ab", tmp_ra)
        terms.append(tmp_contraction3)

        del tmp_bs, tmp_ra
        #
        # - w(A)_sb S_ba S_rs
        #
        # wa_sb s_ba s_rs
        tmp_sa = self.lfA.create_two_index(self.nvirtB, self.noccA)
        tmp_ra = self.lfA.create_two_index(self.nvirtA, self.noccA)
        wa_sb.contract("ab,cb->ac", s_ab, out=tmp_sa, clear=True)
        tmp_sa.contract("ab,ca->cb", s_rs, out=tmp_ra, clear=True)

        tmp_contraction4 = -2 * t_ra.contract("ab,ab", tmp_ra)
        terms.append(tmp_contraction4)

        del tmp_sa, tmp_ra
        #
        # + w(B)_ra' S_ba S_a'b
        #
        # wb_ra' s_ba s_a'b
        tmp_rb = self.lfA.create_two_index(self.nvirtA, self.noccB)
        tmp_ra = self.lfA.create_two_index(self.nvirtA, self.noccA)

        wb_ra.contract("ab,bc->ac", s_ab, out=tmp_rb, clear=True)
        tmp_rb.contract("ab,cb->ac", s_ab, out=tmp_ra, clear=True)

        tmp_contraction5 = 2 * t_ra.contract("ab,ab", tmp_ra)
        terms.append(tmp_contraction5)

        del tmp_rb, tmp_ra
        #
        # - w(B)_r'a S_rb S_br'
        #
        # wb_r'a s_rb s_br'
        tmp_ba = self.lfA.create_two_index(self.noccB, self.noccA)
        tmp_ra = self.lfA.create_two_index(self.nvirtA, self.noccA)

        wb_ra.contract("ab,ca->cb", s_br, out=tmp_ba, clear=True)
        tmp_ba.contract("ab,ac->cb", s_br, out=tmp_ra, clear=True)

        tmp_contraction6 = -2 * t_ra.contract("ab,ab", tmp_ra)
        terms.append(tmp_contraction6)

        del tmp_ba, tmp_ra
        # exch_ind B<-A
        # 2t_bs (...)
        # (...):
        # '''
        # r->s, a->b, s->r, b->a
        # '''
        #
        # - v_(s'b)(ra) S_as' S_sr
        #
        # v_rs'ab s_as' s_sr
        tmp_rb = self.lfA.create_two_index(self.nvirtA, self.noccB)
        tmp_sb = self.lfA.create_two_index(self.nvirtB, self.noccB)
        v_rsab.contract("abcd,cb->ad", s_as, out=tmp_rb, clear=True)
        tmp_rb.contract("ab,ac->cb", s_rs, out=tmp_sb, clear=True)

        tmp_contraction7 = -2 * t_sb.contract("ab,ab", tmp_sb)
        terms.append(tmp_contraction7)
        del tmp_rb, tmp_sb
        #
        # v_(sb')(ra) S_b'r S_ba
        #
        # v_rsab' s_b'r s_ba
        tmp_sb = self.lfA.create_two_index(self.nvirtB, self.noccB)
        tmp_sa = self.lfA.create_two_index(self.nvirtB, self.noccA)
        v_rsab.contract("abcd,da->bc", s_br, out=tmp_sa, clear=True)
        tmp_sa.contract("ab,bc->ac", s_ab, out=tmp_sb, clear=True)

        tmp_contraction8 = 2 * t_sb.contract("ab,ab", tmp_sb)
        terms.append(tmp_contraction8)
        del tmp_sb, tmp_sa
        #
        # -2 v_(sb)(ra) S_b'r S_ab'
        #
        # v_rsab s_b'r s_ab'
        tmp_sb = self.lfA.create_two_index(self.nvirtB, self.noccB)
        tmp_ar = self.lfA.create_two_index(self.noccA, self.nvirtA)
        s_br.contract("ab,ca->cb", s_ab, out=tmp_ar, clear=True)
        v_rsab.contract("abcd,ca->bd", tmp_ar, out=tmp_sb, clear=True)

        tmp_contraction9 = -4 * t_sb.contract("ab,ab", tmp_sb)
        terms.append(tmp_contraction9)
        del tmp_sb, tmp_ar
        #
        # - w(B)_ra S_ab S_sr
        #
        # wb_ra s_ab s_sr
        tmp_sb = self.lfA.create_two_index(self.nvirtB, self.noccB)
        tmp_rb = self.lfA.create_two_index(self.nvirtA, self.noccB)
        wb_ra.contract("ab,bc->ac", s_ab, out=tmp_rb, clear=True)
        tmp_rb.contract("ab,ac->cb", s_rs, out=tmp_sb, clear=True)

        tmp_contraction10 = -2 * t_sb.contract("ab,ab", tmp_sb)
        terms.append(tmp_contraction10)
        del tmp_sb, tmp_rb
        #
        # + w(A)_sb' S_ab S_b'a
        #
        # wa_sb' s_ab s_b'a
        tmp_sb = self.lfA.create_two_index(self.nvirtB, self.noccB)
        tmp_sa = self.lfA.create_two_index(self.nvirtB, self.noccA)
        wa_sb.contract("ab,cb->ac", s_ab, out=tmp_sa, clear=True)
        tmp_sa.contract("ab,bc->ac", s_ab, out=tmp_sb, clear=True)

        tmp_contraction11 = 2 * t_sb.contract("ab,ab", tmp_sb)
        terms.append(tmp_contraction11)
        del tmp_sb, tmp_sa
        #
        # - w(A)_s'b S_sa S_as'
        #
        # wa_s'b s_sa s_as'
        tmp_sb = self.lfA.create_two_index(self.nvirtB, self.noccB)
        tmp_ab = self.lfA.create_two_index(self.noccA, self.noccB)
        wa_sb.contract("ab,ca->cb", s_as, out=tmp_ab, clear=True)
        tmp_ab.contract("ab,ac->cb", s_as, out=tmp_sb, clear=True)

        tmp_contraction12 = -2 * t_sb.contract("ab,ab", tmp_sb)
        terms.append(tmp_contraction12)
        del tmp_sb, tmp_ab

        return np.sum(terms)

    def disp20(self):
        """E_{disp}^{(20)} correction according to eq. 63 in

        'Many-body symmetry-adapted perturbation theory of intermolecular interactions.
        H2O and HF dimers'
        The Journal of Chemical Physics 95, 6576 (1991); doi: 10.1063/1.461528
        """
        v_rsab = self.get_aux_matrix("v_rsab")
        t_rsab = self.get_aux_matrix("t_rsab")

        # E_disp_20
        energy = t_rsab.contract("abcd,abcd", v_rsab, factor=4.0)
        return energy

    def exch_disp_20(
        self,
    ):
        """Exch-disp20 correction according to eq. 12 in
        'Frozen core and effective core potentials in symmetry-adapted
        perturbation theory' THE JOURNAL OF CHEMICAL PHYSICS 127, 164103 2007"

        SECOND-QUANTIZED APPROACH
        """
        # terms in order given in eq. 12 of above ref.
        energy_terms = []

        v_rsab = self.get_aux_matrix("v_rsab")

        wb_ra = self.get_aux_matrix("wb_ra")
        wa_sb = self.get_aux_matrix("wa_sb")

        s_rs = self.get_aux_matrix("s_rs")

        s_as = self.get_aux_matrix("s_as")

        s_br = self.get_aux_matrix("s_br")

        s_ab = self.get_aux_matrix("s_ab")

        t_rsab = self.get_aux_matrix("t_rsab")
        #
        # v_(r'a)(s'b) S_sr' S_rs'
        #
        tmp_rrab = self.denselfA.create_four_index(
            self.nvirtA, self.nvirtA, self.noccA, self.noccB
        )
        tmp_rrab.clear()
        tmp_srab = self.denselfA.create_four_index(
            self.nvirtB, self.nvirtA, self.noccA, self.noccB
        )

        v_rsab.contract("abcd,eb->aecd", s_rs, out=tmp_rrab, clear=True)
        tmp_rrab.contract("abcd,ae->ebcd", s_rs, out=tmp_srab, clear=True)

        tmp_contraction1 = t_rsab.contract("abcd,bacd", tmp_srab, factor=-2.0)

        energy_terms.append(tmp_contraction1)

        del tmp_rrab, tmp_srab
        #
        # v_(ra')(s'b) S_sa S_a's'
        #
        tmp_rb = self.denselfA.create_two_index(self.nvirtA, self.noccB)
        tmp_as = self.denselfA.create_two_index(self.noccA, self.nvirtB)

        v_rsab.contract("abcd,cb->ad", s_as, out=tmp_rb)
        t_rsab.contract("abcd,ad->cb", tmp_rb, out=tmp_as)

        tmp_contraction2 = tmp_as.contract("ab,ab", s_as)

        energy_terms.append(2 * tmp_contraction2)

        del tmp_as, tmp_rb

        #
        # -2 v_(ra)(s'b) S_sa' S_a's'
        #
        tmp_rsab = v_rsab.copy()
        tmp_rsab.clear()
        tmp_ss = self.denselfA.create_two_index(self.nvirtB, self.nvirtB)

        s_as.contract("ab,ac->bc", s_as, out=tmp_ss, clear=True)
        v_rsab.contract("abcd,eb->aecd", tmp_ss, out=tmp_rsab, clear=True)

        tmp_contraction3 = t_rsab.contract("abcd,abcd", tmp_rsab, factor=-4.0)

        energy_terms.append(tmp_contraction3)

        del tmp_rsab, tmp_ss
        #
        # + v_(r'a)(sb') S_rb S_b'r'
        #
        tmp_sa = self.denselfA.create_two_index(self.nvirtB, self.noccA)
        tmp_as = s_as.copy()
        tmp_as.clear()

        v_rsab.contract("abcd,da->bc", s_br, out=tmp_sa, clear=True)
        t_rsab.contract("abcd,da->cb", s_br, out=tmp_as, clear=True)
        tmp_contraction4 = tmp_as.contract("ab,ba", tmp_sa)

        energy_terms.append(2 * tmp_contraction4)
        del tmp_sa, tmp_as

        #
        # -2 v_(r'a)(sb) S_rb' S_b'r'
        #
        tmp_rsab = v_rsab.copy()
        tmp_rsab.clear()
        tmp_rr = self.denselfA.create_two_index(self.nvirtA, self.nvirtA)

        s_br.contract("ab,ac->bc", s_br, out=tmp_rr, clear=True)
        v_rsab.contract("abcd,ae->ebcd", tmp_rr, out=tmp_rsab, clear=True)
        tmp_contraction5 = t_rsab.contract("abcd,abcd", tmp_rsab, factor=-4.0)

        energy_terms.append(tmp_contraction5)

        del tmp_rsab, tmp_rr
        #
        # - v_(ra')(sb') S_b'a S_a'b
        #
        tmp_rsba = self.denselfA.create_four_index(
            self.nvirtA, self.nvirtB, self.noccB, self.noccA
        )
        tmp_rsaa = self.denselfA.create_four_index(
            self.nvirtA, self.nvirtB, self.noccA, self.noccA
        )

        v_rsab.contract("abcd,ed->abce", s_ab, out=tmp_rsaa, clear=True)
        tmp_rsaa.contract("abcd,ce->abed", s_ab, out=tmp_rsba, clear=True)

        tmp_contraction6 = t_rsab.contract("abcd,abdc", tmp_rsba, factor=-2.0)

        energy_terms.append(tmp_contraction6)

        del tmp_rsba, tmp_rsaa
        #
        # - v_(ra)(sb') S_b'a' S_a'b
        #
        tmp_rsab = v_rsab.copy()
        tmp_rsab.clear()
        tmp_bb = self.denselfA.create_two_index(self.noccB, self.noccB)

        s_ab.contract("ab,ac->cb", s_ab, out=tmp_bb, clear=True)

        v_rsab.contract("abcd,ed->abce", tmp_bb, out=tmp_rsab, clear=True)

        tmp_contraction7 = t_rsab.contract("abcd,abcd", tmp_rsab, factor=4.0)

        energy_terms.append(tmp_contraction7)

        del tmp_rsab, tmp_bb
        #
        # - v_(ra')(sb) S_b'a S_a'b'
        #
        tmp_rsab = v_rsab.copy()
        tmp_rsab.clear()
        tmp_aa = self.denselfA.create_two_index(self.noccA, self.noccA)

        s_ab.contract("ab,cb->ca", s_ab, out=tmp_aa, clear=True)

        v_rsab.contract("abcd,ce->abed", tmp_aa, out=tmp_rsab, clear=True)

        tmp_contraction8 = t_rsab.contract("abcd,abcd", tmp_rsab, factor=4.0)

        energy_terms.append(tmp_contraction8)

        del tmp_rsab, tmp_aa
        #
        # -2 w(b)_ra S_sa' S_a'b
        #
        tmp_sb = self.denselfA.create_two_index(self.nvirtB, self.noccB)
        tmp_ar = self.denselfA.create_two_index(self.noccA, self.nvirtA)

        s_as.contract("ab,ac->bc", s_ab, out=tmp_sb, clear=True)
        t_rsab.contract("abcd,bd->ca", tmp_sb, out=tmp_ar, clear=True)
        tmp_contraction9 = tmp_ar.contract("ab,ba", wb_ra)

        energy_terms.append((-4) * tmp_contraction9)

        del tmp_sb, tmp_ar, tmp_contraction9
        #
        # - w(b)_ra' S_sa S_a'b
        #
        tmp_rb = self.denselfA.create_two_index(self.nvirtA, self.noccB)
        tmp_br = self.denselfA.create_two_index(self.noccB, self.nvirtA)

        wb_ra.contract("ab,bc->ac", s_ab, out=tmp_rb, clear=True)
        t_rsab.contract("abcd,cb->da", s_as, out=tmp_br, clear=True)
        tmp_contraction10 = tmp_br.contract("ab,ba", tmp_rb)

        energy_terms.append(2 * tmp_contraction10)

        del tmp_rb, tmp_br, tmp_contraction10

        #
        # - w(b)_r'a S_sr' S_rb
        #
        tmp_sa = self.denselfA.create_two_index(self.nvirtB, self.noccA)
        tmp_as = self.denselfA.create_two_index(self.noccA, self.nvirtB)

        wb_ra.contract("ab,ac->cb", s_rs, out=tmp_sa, clear=True)
        t_rsab.contract("abcd,da->cb", s_br, out=tmp_as, clear=True)
        tmp_contraction11 = tmp_as.contract("ab,ba", tmp_sa)

        energy_terms.append(-2 * tmp_contraction11)
        del tmp_sa, tmp_as, tmp_contraction11
        #
        # -2 w(a)_sb S_rb' S_b'a
        #
        tmp_ra = self.denselfA.create_two_index(self.nvirtA, self.noccA)
        tmp_bs = self.denselfA.create_two_index(self.noccB, self.nvirtB)

        s_br.contract("ab,ca->bc", s_ab, out=tmp_ra, clear=True)
        t_rsab.contract("abcd,ac->db", tmp_ra, out=tmp_bs, clear=True)
        tmp_contraction12 = tmp_bs.contract("ab,ba", wa_sb)

        energy_terms.append(-4 * tmp_contraction12)

        del tmp_ra, tmp_bs

        #
        # w(a)_sb' S_rb S_b'a
        #
        tmp_sa = self.denselfA.create_two_index(self.nvirtB, self.noccA)
        tmp_as = self.denselfA.create_two_index(self.noccA, self.nvirtB)

        wa_sb.contract("ab,cb->ac", s_ab, out=tmp_sa, clear=True)
        t_rsab.contract("abcd,da->cb", s_br, out=tmp_as, clear=True)
        tmp_contraction13 = tmp_as.contract("ab,ba", tmp_sa)

        energy_terms.append(2 * tmp_contraction13)

        del tmp_sa, tmp_as

        #
        # - w(a)_s'b S_sa S_rs'
        #
        tmp_rb = self.denselfA.create_two_index(self.nvirtA, self.noccB)
        tmp_br = self.denselfA.create_two_index(self.noccB, self.nvirtA)

        wa_sb.contract("ab,ca->cb", s_rs, out=tmp_rb, clear=True)
        t_rsab.contract("abcd,cb->da", s_as, out=tmp_br, clear=True)
        tmp_contraction14 = tmp_br.contract("ab,ba", tmp_rb)

        energy_terms.append(-2 * tmp_contraction14)
        del tmp_rb, tmp_br
        return np.sum(energy_terms)

    def update_aux_matrix(self, one, olp, two, orbs):
        """Calculates all necessary intermediates
        **Arguments:**

        one
            list effective coulomb potentials operators (DenseTwoIndex).
            First element is potential of monB nuclei influencing monA electrons,
            second is potential of monA atomic nuclei influencing monB electrons.

        olp
            inter-monomer (AB) overlap MO integrals

        two
            Sliced 2-el ABAB MO integrals

        orbs
            list of orbital AO/MO coefficients
            First element is monA, second monB.
        """
        # unpack
        oneA, oneB = one
        olpAB = olp

        check_type("oneA", oneA, TwoIndex)
        check_type("oneB", oneB, TwoIndex)
        check_type("olpAB", olpAB, TwoIndex)
        check_type("two", two, FourIndex)
        check_type("orbA", orbs[0], DenseOrbital)
        check_type("orbB", orbs[1], DenseOrbital)

        # orbs stores DenseExpansion(orbital coeffs).
        # v_rsab
        auxmat2 = self.init_aux_matrix("v_rsab")
        two.contract(
            "abcd->abcd",
            out=auxmat2,
            clear=True,
            select="einsum",
            begin0=self.noccA,
            end0=self.nbasisA,
            begin1=self.noccB,
            end1=self.nbasisB,
            begin2=0,
            end2=self.noccA,
            begin3=0,
            end3=self.noccB,
        )

        # v_abab
        auxmat3 = self.init_aux_matrix("v_abab")
        two.contract(
            "abcd->abcd",
            out=auxmat3,
            clear=True,
            select="einsum",
            end0=self.noccA,
            end1=self.noccB,
            end2=self.noccA,
            end3=self.noccB,
        )

        # one electron coulomb

        # va_bb
        auxmat4 = self.init_aux_matrix("va_bb")
        auxmat4.iadd(
            oneA, 1.0, begin2=0, end2=self.noccB, begin3=0, end3=self.noccB
        )
        # vb_aa
        auxmat9 = self.init_aux_matrix("vb_aa")
        auxmat9.iadd(
            oneB, 1.0, begin2=0, end2=self.noccA, begin3=0, end3=self.noccA
        )

        # omega_b_kl (k,l - general indicies of monomer A - occupied or virtual)
        auxmat13 = self.init_aux_matrix("wb_kl")
        # v_kblb
        tmp_kblb = self.denselfA.create_four_index(
            self.nbasisA, self.noccB, self.nbasisB, self.noccB
        )

        two.contract(
            "abcd->abcd",
            out=tmp_kblb,
            clear=True,
            select="einsum",
            end0=self.nbasisA,
            end1=self.noccB,
            end2=self.nbasisA,
            end3=self.noccB,
        )
        tmp_kblb.contract("abcb->ac", out=auxmat13, factor=2.0)
        auxmat13.iadd(oneB)
        del tmp_kblb

        # omega_a_kl (k,l - general indicies of monomer B - occupied or virtual)
        auxmat14 = self.init_aux_matrix("wa_kl")
        # v_akal
        tmp_akal = self.denselfA.create_four_index(
            self.noccA, self.nbasisB, self.noccA, self.nbasisB
        )

        two.contract(
            "abcd->abcd",
            out=tmp_akal,
            clear=True,
            select="einsum",
            end0=self.noccA,
            end1=self.nbasisB,
            end2=self.noccA,
            end3=self.nbasisB,
        )
        tmp_akal.contract("abac->bc", out=auxmat14, factor=2.0, clear=True)
        auxmat14.iadd(oneA)
        del tmp_akal

        # omega_B_ra
        auxmat15 = self.init_aux_matrix("wb_ra")
        wb_kl = self.get_aux_matrix("wb_kl")
        auxmat15.iadd(
            wb_kl,
            1.0,
            begin2=self.noccA,
            end2=self.nbasisA,
            begin3=0,
            end3=self.noccA,
        )

        # omega_A_sb
        auxmat16 = self.init_aux_matrix("wa_sb")
        wa_kl = self.get_aux_matrix("wa_kl")
        auxmat16.iadd(
            wa_kl,
            1.0,
            begin2=self.noccB,
            end2=self.nbasisB,
            begin3=0,
            end3=self.noccB,
        )

        # S_ab
        auxmat18 = self.init_aux_matrix("s_ab")
        auxmat18.iadd(
            olpAB,
            factor=1.0,
            begin2=0,
            end2=self.noccA,
            begin3=0,
            end3=self.noccB,
        )

        # S_rs
        auxmat19 = self.init_aux_matrix("s_rs")
        auxmat19.iadd(
            olpAB,
            factor=1.0,
            begin2=self.noccA,
            end2=self.nbasisA,
            begin3=self.noccB,
            end3=self.nbasisB,
        )

        # S_as
        auxmat20 = self.init_aux_matrix("s_as")
        auxmat20.iadd(
            olpAB,
            factor=1.0,
            begin2=0,
            end2=self.noccA,
            begin3=self.noccB,
            end3=self.nbasisB,
        )

        # olpAB transpose
        olpAB.itranspose()

        # S_br
        auxmat22 = self.init_aux_matrix("s_br")
        auxmat22.iadd(
            olpAB,
            factor=1.0,
            begin2=0,
            end2=self.noccB,
            begin3=self.noccA,
            end3=self.nbasisA,
        )

        # t_rsab
        auxmat25 = self.init_aux_matrix("t_rsab")
        v_rsab = self.get_aux_matrix("v_rsab")
        omegab_ra = self.get_aux_matrix("wb_ra")
        omegaa_sb = self.get_aux_matrix("wa_sb")
        tmp_rsab, t_ra, t_sb = self.calculate_amplitudes(
            v_rsab, (omegab_ra, omegaa_sb), orbs
        )
        auxmat25.assign(tmp_rsab)

        # t_ra
        auxmat27 = self.init_aux_matrix("t_ra")
        auxmat27.assign(t_ra)

        # t_sb
        auxmat28 = self.init_aux_matrix("t_sb")
        auxmat28.assign(t_sb)
        del oneA, oneB, olpAB, two

    def calculate_aux_matrix(self, *args, **kwargs):
        """Clears existing cache and re-computes is via self.update_aux_matrix"""
        self.clear_aux_matrix()
        self.update_aux_matrix(*args, **kwargs)

    @timer.with_section("SAPT0(RHF)Amplitudes")
    def calculate_amplitudes(self, two_ABAB, one_coulombs, orbs, out=None):
        """Calculates SAPT amplitudes: dispersion & induction amplitudes.
        Dispersion is FourIndex, both Induction are TwoIndex.
            **Arguments:**

            two_ABAB
                Sliced 2-el ABAB MO integrals

            one_coulombs
                list effective coulomb potentials operators.
                First element is potential of monB, second potential of monA.

            orbs
                list of orbital AO/MO coefficients
                First element is monA, second monB.
        """
        check_type("two_ABAB", two_ABAB, FourIndex)
        check_type("one_coulombs[0]", one_coulombs[0], TwoIndex)
        check_type("one_coulombs[1]", one_coulombs[1], TwoIndex)
        check_type("orbs[0]", orbs[0], DenseOrbital)
        check_type("orbs[1]", orbs[1], DenseOrbital)

        if out is None:
            RETURN = True
        else:
            RETURN = False
            check_type("out", out, FourIndex)

        # orbital energies of monomers
        en_mon_A_occ = orbs[0].energies[: self.noccA].copy()
        en_mon_A_virt = orbs[0].energies[self.noccA :].copy()

        en_mon_B_occ = orbs[1].energies[: self.noccB].copy()
        en_mon_B_virt = orbs[1].energies[self.noccB :].copy()

        # effective culomb potential of monomers
        omega_B = one_coulombs[0]
        omega_A = one_coulombs[1]

        # some logs
        log.hline("~")
        log("Orbital Energies (a.u.):")
        log("monA:\n" + " ".join([f"{en:.5f}" for en in orbs[0].energies]))
        log("\n")
        log("monB:\n" + " ".join([f"{en:.5f}" for en in orbs[1].energies]))
        log(" ")
        log("Ocuppations of monomers:")
        log(f"A: occ: {self.noccA:d}; virt: {self.nvirtA}")
        log(f"B: occ: {self.noccB:d}; virt: {self.nvirtB}")
        log.hline("~")

        t_ra = self.denselfA.create_two_index(self.nvirtA, self.noccA)
        t_sb = self.denselfA.create_two_index(self.nvirtB, self.noccB)

        if out is None:
            out = self.denselfA.create_four_index(
                self.nvirtA, self.nvirtB, self.noccA, self.noccB
            )

        #
        # C - Routine Start
        #
        # NOTE: it only provides the denominators
        sapt_core.get_amplitudes(
            out.array,
            t_ra.array,
            t_sb.array,
            en_mon_A_occ,
            en_mon_A_virt,
            en_mon_B_occ,
            en_mon_B_virt,
            self.noccA,
            self.noccB,
            self.nvirtA,
            self.nvirtB,
        )
        # multiply energy denominators by operator matricies
        out.imul(two_ABAB)
        t_ra.imul(omega_B)
        t_sb.imul(omega_A)
        #
        # C - Routine End
        #
        if RETURN:
            return out, t_ra, t_sb

    def init_aux_matrix(self, select):
        """Initialize auxiliary matrices
        **Arguments:**
        select
             One of 'wb_ra','wa_sb','s_pq','s_ba','s_ab','s_br','s_rb',
             's_sa','s_as','s_sr','s_rs','v_pqrs','v_abrs'
        """
        alloc_sizes = {
            "va_bb": (self.lfB.create_two_index, self.noccB, self.noccB),
            "va_ab": (self.lfA.create_two_index, self.noccA, self.noccB),
            "va_rb": (self.lfA.create_two_index, self.nvirtA, self.noccB),
            "va_sa": (self.lfA.create_two_index, self.nvirtB, self.noccA),
            "va_sb": (self.lfB.create_two_index, self.nvirtB, self.noccB),
            "vb_aa": (self.lfA.create_two_index, self.noccA, self.noccA),
            "vb_ab": (self.lfA.create_two_index, self.noccA, self.noccB),
            "vb_sa": (self.lfA.create_two_index, self.nvirtB, self.noccA),
            "vb_ra": (self.lfA.create_two_index, self.nvirtA, self.noccA),
            "wb_ra": (self.lfA.create_two_index, self.nvirtA, self.noccA),
            "wb_kl": (
                self.lfA.create_two_index,
                self.nbasisA,
                self.nbasisA,
            ),
            "wa_sb": (self.lfB.create_two_index, self.nvirtB, self.noccB),
            "wa_kl": (
                self.lfB.create_two_index,
                self.nbasisB,
                self.nbasisB,
            ),
            "s_pq": (
                self.lfA.create_two_index,
                self.nbasisA,
                self.nbasisA,
            ),
            "s_ba": (self.lfA.create_two_index, self.noccB, self.noccA),
            "s_ab": (self.lfA.create_two_index, self.noccA, self.noccB),
            "s_rb": (self.lfA.create_two_index, self.nvirtA, self.noccB),
            "s_br": (self.lfA.create_two_index, self.noccB, self.nvirtA),
            "s_sa": (self.lfA.create_two_index, self.nvirtB, self.noccA),
            "s_as": (self.lfA.create_two_index, self.noccA, self.nvirtB),
            "s_sr": (self.lfA.create_two_index, self.nvirtB, self.nvirtA),
            "s_rs": (self.lfA.create_two_index, self.nvirtA, self.nvirtB),
            "t_ra": (self.lfA.create_two_index, self.nvirtA, self.noccA),
            "t_sb": (self.lfA.create_two_index, self.nvirtB, self.noccB),
            # NOTE: it's dense (ov)^2 tensor
            "t_rsab": (
                self.denselfA.create_four_index,
                self.nvirtA,
                self.nvirtB,
                self.noccA,
                self.noccB,
            ),
            "v_rsab": (
                self.denselfA.create_four_index,
                self.nvirtA,
                self.nvirtB,
                self.noccA,
                self.noccB,
            ),
            "v_abab": (
                self.denselfA.create_four_index,
                self.noccA,
                self.noccB,
                self.noccA,
                self.noccB,
            ),
        }

        # grab from the cache
        matrix, new = self._cache.load(
            select,
            alloc=alloc_sizes[select],
            tags="m",
        )
        if not new:
            raise RuntimeError(
                f"The matrix {select} already exists. Call clear prior"
                "to updating the wfn."
            )
        return matrix
