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
"""
Variables used in this module:
 :ncore:     number of frozen core orbitals
 :nocc:      number of occupied orbitals in the principal configuration
 :nactc:     number of active core orbitals for the core-valence separation
             approximation (zero by default)
 :nacto:     number of active occupied orbitals in the principal configuration
 :nvirt:     number of virtual orbitals in the principal configuration
 :nactv:     number of active virtual orbitals in the principal configuration
 :nbasis:    total number of basis functions
 :nact:      total number of active orbitals (nactc+nacto+nactv)
 :e_ci:      eigenvalues of CI Hamiltonian (IOData container attribute)
 :civ:       eigenvectors of CI Hamiltonian (IOData container attribute)
 :t_p:       The pair coupled cluster amplitudes of pCCD

Indexing convention:
 :i,j,k,..:  occupied orbitals of principal configuration
 :a,b,c,..:  virtual orbitals of principal configuration
 :p,q,r,..:  any orbital in the principal configuration (occupied or virtual)

Intermediates:
 :<pq||rs>:  <pq|rs>-<pq|sr> (Coulomb and exchange terms of ERI)
 :fock:      h_pp + sum_i(2<pi|pi>-<pi|ip>) (the inactive Fock matrix)
"""

import numpy as np

from pybest.log import log

from .rci_utils import display
from .spin_free_base import SpinFree


class RpCCDCID(SpinFree):
    """Restricted Spin-Free pair Coupled Cluster Doubles Configuration Interaction Doubles module"""

    long_name = "pCCD-CID"
    acronym = "pCCD-CID"
    reference = "pCCD"

    def compute_h_diag(self, *arg):
        """Used by davidson module for pre-conditioning."""
        #
        # Auxiliary objects
        #
        fock = self.from_cache("fock")
        govvo = self.from_cache("govvo")
        govov = self.from_cache("govov")
        goooo = self.from_cache("goooo")
        gvvvv = self.from_cache("gvvvv")
        #
        # local variables
        #
        hdiag = self.lf.create_one_index(self.dimension)
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]

        #
        # Intermediates
        #
        fii = self.lf.create_one_index(nacto)
        fock.copy_diagonal(out=fii, end=nacto)
        faa = self.lf.create_one_index(nactv)
        fock.copy_diagonal(out=faa, begin=nacto)

        g_ijij = self.lf.create_two_index(nacto, nacto)
        goooo.contract("abab->ab", g_ijij)
        g_ijji = self.lf.create_two_index(nacto, nacto)
        goooo.contract("abba->ab", g_ijji, factor=-1.0)

        g_abab = self.lf.create_two_index(nactv, nactv)
        gvvvv.contract("abab->ab", g_abab)
        g_abba = self.lf.create_two_index(nactv, nactv)
        gvvvv.contract("abba->ab", g_abba, factor=-1.0)

        g_iaia = self.lf.create_two_index(nacto, nactv)
        govov.contract("abab->ab", g_iaia)
        g_iaai = self.lf.create_two_index(nacto, nactv)
        govvo.contract("abba->ab", g_iaai, factor=-1.0)

        r_iajb = self.denself.create_four_index(nacto, nactv, nacto, nactv)
        #
        # -f_ii - f_jj
        #
        fii.expand("a->abcd", r_iajb, factor=-1.0)
        fii.expand("c->abcd", r_iajb, factor=-1.0)

        #
        # +f_aa + f_bb
        #
        faa.expand("b->abcd", r_iajb)
        faa.expand("d->abcd", r_iajb)

        #
        # <ab|ab>
        #
        g_abab.expand("bd->abcd", r_iajb)
        #
        # <ij|ij>
        #
        g_ijij.expand("ac->abcd", r_iajb)

        #
        # - <jb||jb>
        #
        g_iaia.expand("cd->abcd", r_iajb, factor=-1.0)
        g_iaai.expand("cd->abcd", r_iajb, factor=1.0)
        #
        # - <ib|ib>
        #
        g_iaia.expand("ad->abcd", r_iajb, factor=-1.0)
        #
        # - <ja|ja>
        #
        g_iaia.expand("cb->abcd", r_iajb, factor=-1.0)
        #
        # - <ia||ia>
        #
        g_iaia.expand("ab->abcd", r_iajb, factor=-1.0)
        g_iaai.expand("ab->abcd", r_iajb, factor=1.0)
        #
        # Assign opposite spin block
        #
        if self.pairs:
            hdiag.assign(r_iajb.get_triu(k=0).ravel(), begin0=1)
            return hdiag
        hdiag.assign(r_iajb.get_triu(k=1).ravel(), begin0=1)
        return hdiag

    def build_subspace_hamiltonian(self, bvector, hamiltonian, *args):
        """
        Used by davidson module to construct subspace Hamiltonian

        **Arguments:**

        bvector:
            (OneIndex object) contains current approximation to CI coefficients

        hamiltonian:
            (OneIndex object) used by davidson module and contains
            diagonal approximation to the full matrix
        """
        tp = self.t_p
        #
        # Integrals
        #
        fock = self.from_cache("fock")
        govvo = self.from_cache("govvo")
        govov = self.from_cache("govov")
        gppqq = self.from_cache("gppqq")
        goooo = self.from_cache("goooo")
        gvvvv = self.from_cache("gvvvv")

        #
        # Ranges
        #
        oo = self.get_range("oo")
        ov = self.get_range("ov")
        vv = self.get_range("vv")
        #
        # TEMP OBJ.
        #
        f_oo = fock.copy(**oo)
        f_vv = fock.copy(**vv)
        #
        # local variables
        #
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        #
        # Bvectors
        #
        b_d = self.denself.create_four_index(nacto, nactv, nacto, nactv)
        #
        # Bvectors assignment
        #
        if self.pairs:
            b_d.assign_triu(bvector, begin4=1, k=0)
            b_p = b_d.contract("abab->ab")
            b_d.iadd_transpose((2, 3, 0, 1))
            b_d = self.set_seniority_0(b_d, b_p)
        else:
            b_d.assign_triu(bvector, begin4=1, k=1)
            b_d.iadd_transpose((2, 3, 0, 1))
        #
        # Sigma vector
        #
        sigma_p = self.denself.create_four_index(nacto, nactv, nacto, nactv)
        sigma = self.denself.create_one_index(self.dimension)

        # c_0
        c_0 = bvector.get_element(0)
        #
        # <0|H|cdlk>
        #
        # 1) <kl||cd> r_kcld (2<kd|cl> - <kc|dl>)
        value_0 = b_d.contract("abcd,adbc", govvo, factor=2.0)
        value_0 += b_d.contract("abcd,abdc", govvo, factor=-1.0)
        #
        #  <ijab|H|0>
        #
        # 2) 1/2 Pia/jb <ja|bi> * r_0
        govvo.contract("abcd->dbac", out=sigma_p, factor=c_0 / 2.0)

        #
        # delta_ij
        # 3) Pia/jb[f_ab t_iaia delta_ij]c_0
        tmp_iab = fock.contract("ab,ca->cab", tp, **vv)  # iab

        # 6) 1/2 Pia/jb[<ab|cc> t_icic delta_ij]c_0
        gvvvv.contract("abcc,dc->dab", tp, tmp_iab, factor=0.5)  # iab

        # 11) -1/2 Pia/jb[<kk|ab> (t_kaka t_ibib + t_kbkb t_iaia)delta_ij ]c_0 (kbak)
        tmp = govvo.contract("abca,ac->cb", tp)  # (ab)
        tp.contract("ac,bc->abc", tmp, tmp_iab, factor=-0.5)  # (iab)

        tmp = govvo.contract("abca,ab->cb", tp)  # (ab)
        tp.contract("ab,bc->abc", tmp, tmp_iab, factor=-0.5)  # (iab)

        tmp_iab.expand("abc->abac", sigma_p, factor=c_0)
        del tmp_iab

        #
        # delta_ab
        # 4)-Pia/jb[f_ij t_iaia delta_ab]c_0
        tmp_iaj = fock.contract("ab,ac->acb", tp, **oo, factor=-1.0)  # iaj

        # 5) 1/2 Pia/jb[<ij|kk> t_kaka delta_ab]c_0
        goooo.contract("abcc,cd->adb", tp, tmp_iaj, factor=0.5)  # iaj

        # 10) -1/2Pia/jb[<ij|cc> (t_icic t_jaja + t_jcjc t_iaia)delta_ab ]c_0 (iccj)
        tmp = govvo.contract("abbc,ab->ac", tp)  # (ij)
        tmp.contract("ab,bc->acb", tp, tmp_iaj, factor=-0.5)  # (iaj)

        tmp = govvo.contract("abbc,cb->ac", tp)  # (ij)
        tmp.contract("ab,ac->acb", tp, tmp_iaj, factor=-0.5)  # (iaj)

        tmp_iaj.expand("abc->abcb", sigma_p, factor=c_0)
        del tmp_iaj

        #
        # delta_ij delta_ab
        # 12) 1/2 Pia/jb[<kk|cc> (t_icic t_kaka)delta_ij delta_ab ]c_0 (kc)
        tmp = gppqq.contract("ab,cb->ca", tp, **ov)  # (ik)
        tmp = tmp.contract("ab,bc->ac", tp, factor=0.5)  # (ia)
        tmp.expand("ab->abab", sigma_p, factor=c_0)

        #
        # (iajb)
        # 7) Pia/jb[<ib||aj> t_iaia]c_0
        govvo.contract("abcd,ac->acdb", tp, out=sigma_p, factor=c_0)
        govov.contract("abcd,ad->adcb", tp, out=sigma_p, factor=-c_0)

        # 8) -Pia/jb[<jb|ia> t_jaja]c_0
        govov.contract("abcd,ad->cdab", tp, out=sigma_p, factor=-c_0)

        # 9) 1/2Pia/jb[<ij|ab> (t_iaia t_jbjb + t_jaja t_ibib) ]c_0 (ibaj)
        tmp = govvo.contract("abcd,ac->abcd", tp)
        tmp.contract("abcd,db->acdb", tp, out=sigma_p, factor=0.5 * c_0)

        tmp = govvo.contract("abcd,dc->abcd", tp)
        tmp.contract("abcd,ab->acdb", tp, out=sigma_p, factor=0.5 * c_0)

        # <ijab|H|cdlk>
        #
        # 13 -Pia/jb fjl c_ialb
        b_d.contract("abcd,ce->abed", f_oo, out=sigma_p, factor=-1.0)

        # 14 Pia/jb fac c_icjb
        b_d.contract("abcd,eb->aecd", f_vv, out=sigma_p)

        # 15) +L_kaci r_kcJB
        b_d.contract("abcd,aebf->fecd", govvo, out=sigma_p, factor=2.0)

        b_d.contract("abcd,aefb->fecd", govov, out=sigma_p, factor=-1.0)

        # 16) -<ka|di> r_kbjd
        b_d.contract("abcd,aedf->fecb", govvo, out=sigma_p, factor=-1.0)

        # 17) -Pia/jb<ka|jd> r_kbid
        b_d.contract("abcd,aefd->cefb", govov, out=sigma_p, factor=-1.0)

        # 18) 1/2Pia/jb<ab|cd> r_icjd
        gvvvv.contract("abcd,ecfd->eafb", b_d, out=sigma_p, factor=0.5)
        # 19) 1/2Pia/jb<kl|ij> r_kalb
        goooo.contract("abcd,aebf->cedf", b_d, out=sigma_p, factor=0.5)

        # 20) Pia/jb Lilad t_iaia c_jbld  (idal) (iadl)
        tmp = govvo.contract("abcd,efdb->acef", b_d, factor=2.0)  # iajb
        govvo.contract("abcd,efdc->abef", b_d, tmp, factor=-1.0)  # iajb
        tmp.contract("abcd,ab->abcd", tp, out=sigma_p)

        # 21) Pia/jb -<il||ad> t_iaia c_jdlb  (idal) (iadl)
        tmp = govvo.contract("abcd,ebdf->acef", b_d, factor=-1.0)  # iajb
        govvo.contract("abcd,ecdf->abef", b_d, tmp)  # iajb
        tmp.contract("abcd,ab->abcd", tp, out=sigma_p)

        # 22) Pia/jb <il|cb> t_ibib c_jcla  (ibcl)
        tmp = govvo.contract("abcd,ecdf->afeb", b_d)  # iajb
        tmp.contract("abcd,ad->abcd", tp, out=sigma_p)

        # 23) Pia/jb -Lkicd t_iaia c_kcjd delta_ab  (kdci) (kcdi)
        tmp = govvo.contract("abcd,aceb->de", b_d, factor=-2.0)  # ij
        govvo.contract("abcd,abec->de", b_d, tmp)  # ij

        tmp_iaj = tp.contract("ab,ac->abc", tmp)  # iaj)
        tmp_iaj.expand("abc->abcb", sigma_p)
        del tmp_iaj

        # 24) Pia/jb -Lklca t_iaia c_kclb delta_ij  (kacl) (kcal) c_kclb
        tmp = govvo.contract("abcd,acde->be", b_d, factor=-2.0)  # ab
        govvo.contract("abcd,abde->ce", b_d, tmp)  # ab

        tmp_iab = tp.contract("ab,bc->abc", tmp)  # iab)
        tmp_iab.expand("abc->abac", sigma_p)
        del tmp_iab

        # 25) Pia/jb -<il|cc> t_icic c_lajb  (iccl)
        tmp = govvo.contract("abbc,ab->ac", tp)  # il
        tmp.contract("ab,bcde->acde", b_d, out=sigma_p, factor=-1.0)  # ab

        # 26) Pia/jb -<kk|ad> t_kaka c_jbid  (kdak)
        tmp = govvo.contract("abca,ac->cb", tp)  # ad
        tmp.contract("ab,cdeb->eacd", b_d, out=sigma_p, factor=-1.0)  # ab

        # 27) 1/2Pia/jb<kl|cc> t_icic c_kalb delta_ij  (kccl)
        tmp = govvo.contract("abbc,db->acd", tp)  # kli
        tmp = tmp.contract("abc,adbe->cde", b_d)  # iab
        tmp.expand("abc->abac", sigma_p, factor=0.5)

        # 28) 1/2Pia/jb<kk|cd> t_kaka c_icjd delta_ab (kdck)
        tmp = govvo.contract("abca,dceb->ade", b_d)  # kij
        tmp = tmp.contract("abc,ad->bdc", tp)  # iaj
        tmp.expand("abc->abcb", sigma_p, factor=0.5)

        sigma.set_element(0, value_0)
        sigma_p.iadd_transpose((2, 3, 0, 1))

        if self.pairs:
            sigma.iadd(sigma_p.get_triu(k=0), begin0=1)
            return sigma

        sigma.iadd(sigma_p.get_triu(k=1), begin0=1)

        return sigma

    def printer(self):
        """Printing the results."""
        #
        # Local variables
        #
        evals = self.checkpoint["e_ci"]
        evecs = self.checkpoint["civ"]
        e_ref = self.checkpoint["e_ref"]
        threshold = self.threshold
        alpha = "\u03b1"
        beta = "\u03b2"
        data = self.setup_dict()
        #
        # Printing
        #
        log.hline("*")
        log(f"RESULTS OF {self.acronym}")
        log.hline("*")
        log(
            f"{'Root':>5s} {'Exc.Energy[au]':>16s} {'Tot.Energy[au]':>17s}"
            f" {'Weight(s)':>15s}"
        )
        log.hline("_")
        for ind, val in enumerate(evals):
            data = {key: [] for key in data}
            evecsj = evecs[:, ind]
            ncore = np.where(abs(evecsj) > threshold)[0]
            log(
                f"{ind:>3d} {val:> 16.6e} {e_ref + val:> 17.8f}"
                f"{np.dot(evecsj[1:], evecsj[1:]):> 17.6f}"
            )
            log(" ")
            for ind2 in ncore:
                if ind2 == 0:
                    if self.size_consistency_correction:
                        self.rci_corrections.printer()
                    log(f"{'Reference state   C_0:':>30s}")
                    log(f"{evecsj[ind2]:> 34.5f}")
                else:
                    self.collect_data(ind2, data, evecsj)
            if (len(data["spin_block_ab"])) > 0:
                log(" ")
                log(f"{'(i->a   j->b):':>22s} {'C_iajb:':>11s}")
            display(data, "ab", alpha, beta)
            log.hline("-")
            log.hline("*")

    def collect_data(self, index, data, evecsj):
        """Collect data and prepare for printing:

        **Arguments:**

        *index:
            (int) Number indicating the SD contribution in the CI solution.

        *data:
            (dictionary) Contains two types of data:
            indices (spin_block_[ab]) of the proper SD spin block
            contributions and the corresponding coefficients (c_[ab]).

        *evecsj:
            Eigenvectors of CI Hamiltonian (without the reference
            state contribution).
        """
        ncore = self.occ_model.ncore[0]
        i, a, j, b = self.get_index_d(index - 1)
        i, a, j, b = (i + ncore, a + ncore, j + ncore, b + ncore)
        data["spin_block_ab"].append([i, a, j, b])
        data["c_ab"].append(evecsj[index])
        return data

    @staticmethod
    def setup_dict():
        """Initializes the proper dictionary to store the data."""
        return {
            "spin_block_ab",
            "c_ab",
        }

    def set_seniority_0(self, matrix, value=0.0):
        """Set all seniority 0 t_2 amplitudes to some value.
        matrix - DenseFourIndex object
        """
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        ind1, ind2 = np.indices((nacto, nactv))
        indices = [ind1, ind2, ind1, ind2]
        matrix.assign(value, indices)
        return matrix
