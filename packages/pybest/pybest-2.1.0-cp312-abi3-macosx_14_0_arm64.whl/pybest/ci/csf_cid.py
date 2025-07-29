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

from math import sqrt

from pybest.log import log

from .csf_base import CSF
from .rcid import RCIDBase


class CSFRCID(CSF, RCIDBase):
    """Configuration State Function Restricted Configuration Interaction Doubles (CSFRCID) class.
    Contains all required methods to diagonalize the RCID Hamiltonian using CSF basis.
    """

    @CSF.dimension.setter
    def dimension(self, new=None):
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        if new is not None:
            self._dimension = CSF.set_dimension(new, nacto, nactv)
        else:
            log.warn(
                "The dimension may be wrong!"
                "Please set the dimension property with one of the strings (RCIS, RCID, RCISD)"
            )

    def compute_h_diag(self, *args):
        """Calculating the guess vector for CSF basis.

        hdiag:
            (OneIndex object) contains guess vector for CSF basis.
        """
        #
        # Auxiliary self.cts
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

        end_1 = nacto * nactv + 1
        end_2 = end_1 + nacto * (nactv * (nactv - 1)) // 2
        end_3 = end_2 + nacto * (nacto - 1) // 2 * nactv
        end_4 = end_3 + (nacto * (nacto - 1) // 2 * nactv * (nactv - 1) // 2)

        g_ijij = self.lf.create_two_index(nacto, nacto)
        goooo.contract("abab->ab", clear=True)
        g_ijji = self.lf.create_two_index(nacto, nacto)
        goooo.contract("abba->ab", factor=-1.0)

        g_abab = self.lf.create_two_index(nactv, nactv)
        gvvvv.contract("abab->ab")
        g_abba = self.lf.create_two_index(nactv, nactv)
        gvvvv.contract("abba->ab", factor=-1.0)

        g_iiii = g_ijij.copy_diagonal()
        g_aaaa = g_abab.copy_diagonal()

        g_iaia = self.lf.create_two_index(nacto, nactv)
        govov.contract("abab->ab", clear=True)
        g_iaai = self.lf.create_two_index(nacto, nactv)
        govvo.contract("abba->ab", factor=-1.0, clear=True)

        g_ajaj = self.lf.create_two_index(nactv, nacto)
        govov.contract("abab->ba", clear=True)

        g_ajja = self.lf.create_two_index(nactv, nacto)
        govvo.contract("abba->ba", factor=-1.0, clear=True)

        #
        # Pairs spin block
        #
        r_ia = self.denself.create_two_index(nacto, nactv)
        #
        # -2f_ii
        #
        fii.expand("a->ab", out=r_ia, factor=-2.0)
        #
        # +2f_aa
        #
        faa.expand("b->ab", out=r_ia, factor=2.0)
        #
        # -4 <ia|ia> + 2 <ii|aa>
        #
        r_ia.iadd(g_iaia, factor=-4.0)
        r_ia.iadd(g_iaai, factor=2.0)
        #
        # <ii|ii>
        #
        g_iiii.expand("a->ab", r_ia)
        #
        # <aa|aa>
        #
        g_aaaa.expand("b->ab", r_ia)
        #
        #
        # Assign pairs spin block
        hdiag.assign(r_ia.array.ravel(), begin0=1, end0=end_1)
        del r_ia
        # ovv spin block
        r_iab = self.denself.create_three_index(nacto, nactv, nactv)
        #
        # All terms with P+_ab
        # 1/2<ab|ab>
        #
        g_abab.expand("bc->abc", r_iab)
        #
        # + f_aa
        #
        faa.expand("b->abc", r_iab)
        faa.expand("c->abc", r_iab)
        #
        # - f_ii
        #
        fii.expand("a->abc", r_iab, factor=-2.0)
        #
        # <ii|ii>
        #
        g_iiii.expand("a->abc", r_iab)
        #
        # -2 <ib|ib> + <ii|bb>
        #
        g_iaia.expand("ab->abc", r_iab, factor=-2.0)
        g_iaai.expand("ab->abc", r_iab, factor=1.0)
        g_iaia.expand("ac->abc", r_iab, factor=-2.0)
        g_iaai.expand("ac->abc", r_iab, factor=1.0)
        #
        # Assign ovv spin block
        #
        tmp = self.denself.create_four_index(nacto, nactv, nacto, nactv)
        r_iab.expand("abc->abac", tmp)
        hdiag.assign(
            tmp.array[self.get_mask_csf("iab")],
            begin0=end_1,
            end0=end_2,
        )
        del r_iab
        #
        # oov spin block
        #
        r_iaj = self.denself.create_three_index(nacto, nactv, nacto)
        #
        # All terms with P+_ij
        # -f_ii -f_jj
        #
        fii.expand("a->abc", r_iaj, factor=-1.0)
        fii.expand("c->abc", r_iaj, factor=-1.0)
        #
        # +f_aa
        #
        faa.expand("b->abc", r_iaj, factor=2.0)
        #
        # <aa|aa>
        #
        g_aaaa.expand("b->abc", r_iaj)
        #
        # <ij|ij>
        #
        g_ijij.expand("ac->abc", r_iaj)
        #
        # <ia|ai> - 2 <ai|ai>
        #
        g_iaai.expand("ab->abc", r_iaj, factor=1.0)
        g_iaia.expand("ab->abc", r_iaj, factor=-2.0)
        g_ajja.expand("bc->abc", r_iaj, factor=1.0)
        g_ajaj.expand("bc->abc", r_iaj, factor=-2.0)

        tmp.clear()
        r_iaj.expand("abc->abcb", tmp)
        hdiag.assign(
            tmp.array[self.get_mask_csf("iaj")],
            begin0=end_2,
            end0=end_3,
        )
        del r_iaj, tmp
        #
        # ovov spin block A
        #
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
        # 1/2 <ab||ab>
        #
        g_abab.expand("bd->abcd", r_iajb, factor=0.5)
        g_abba.expand("bd->abcd", r_iajb, factor=-0.5)
        #
        # 1/2 <ij||ij>
        #
        g_ijij.expand("ac->abcd", r_iajb, factor=0.5)
        g_ijji.expand("ac->abcd", r_iajb, factor=-0.5)
        #
        # <jb||bj> + 1/2 <jb|bj>
        #
        g_iaia.expand("cd->abcd", r_iajb, factor=-1.0)
        g_iaai.expand("cd->abcd", r_iajb, factor=1.5)
        #
        # <ib||bi> + 1/2 <ib|bi>
        #
        g_iaia.expand("ad->abcd", r_iajb, factor=-1.0)
        g_iaai.expand("ad->abcd", r_iajb, factor=1.5)
        #
        # <ja||aj> + 1/2 <ja|aj>
        #
        g_iaia.expand("cb->abcd", r_iajb, factor=-1.0)
        g_iaai.expand("cb->abcd", r_iajb, factor=1.5)
        #
        # <ia||ai> + 1/2 <ia|ai>
        #
        g_iaia.expand("ab->abcd", r_iajb, factor=-1.0)
        g_iaai.expand("ab->abcd", r_iajb, factor=1.5)
        #
        # Assign ovov spin blocks
        #
        hdiag.iadd(
            r_iajb.array[self.get_mask_csf("iajb")],
            begin0=end_3,
            end0=end_4,
        )
        #
        # ovov spin block B
        #
        r_iajb.clear()
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
        # 1/2 (<jb||bj> - <jb|jb>)
        #
        g_iaia.expand("cd->abcd", r_iajb, factor=-1.0)
        g_iaai.expand("cd->abcd", r_iajb, factor=0.5)
        #
        # 1/2 (<ib||bi> - <ib|ib>)
        #
        g_iaia.expand("ad->abcd", r_iajb, factor=-1.0)
        g_iaai.expand("ad->abcd", r_iajb, factor=0.5)
        #
        # 1/2 (<ja||aj> - <ja|ja>)
        #
        g_iaia.expand("cb->abcd", r_iajb, factor=-1.0)
        g_iaai.expand("cb->abcd", r_iajb, factor=0.5)
        #
        # 1/2 (<ia||ai> - <ia|ia>)
        #
        g_iaia.expand("ab->abcd", r_iajb, factor=-1.0)
        g_iaai.expand("ab->abcd", r_iajb, factor=0.5)
        #
        #
        # Assign ovov spin blocks
        #
        hdiag.iadd(
            r_iajb.array[self.get_mask_csf("iajb")],
            begin0=end_4,
        )
        return hdiag

    def build_subspace_hamiltonian(self, bvector, hamiltonian, *args):
        """
        Constructing Hamiltonian subspace for CSF basis

        **Arguments:**

        bvector:
            (OneIndex object) contains current approximation to CI coefficients
            in the CSF basis

        """
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        sigma = self.lf.create_one_index(self.dimension)
        bvectors = {"bvect_0": bvector.array[0]}
        end_1 = nacto * nactv + 1

        if nacto >= 1 and nactv >= 1:
            bvect_ia = self.lf.create_two_index(nacto, nactv)
            bvect_ia.assign(bvector, begin2=1, end2=end_1)
            bvectors["bvect_ia"] = bvect_ia

        if nacto >= 1 and nactv >= 2:
            end_2 = end_1 + nacto * (nactv * (nactv - 1)) // 2
            bvect_iaib = self.denself.create_four_index(
                nacto, nactv, nacto, nactv
            )
            bvect_iaib.assign(
                bvector,
                ind=self.get_index_of_mask_csf("iab"),
                begin4=end_1,
                end4=end_2,
            )
            bvectors["bvect_iab"] = bvect_iaib.contract("abac->abc")
            bvectors["bvect_iab"].iadd(bvect_iaib.contract("abac->acb"))

        if nacto >= 2 and nactv >= 1:
            end_3 = end_2 + nacto * (nacto - 1) // 2 * nactv
            bvect_iaja = self.denself.create_four_index(
                nacto, nactv, nacto, nactv
            )
            bvect_iaja.assign(
                bvector,
                ind=self.get_index_of_mask_csf("iaj"),
                begin4=end_2,
                end4=end_3,
            )
            bvectors["bvect_iaj"] = bvect_iaja.contract("abcb->abc")
            bvectors["bvect_iaj"].iadd(bvect_iaja.contract("abcb->cba"))

        if nacto >= 2 and nactv >= 2:
            end_4 = end_3 + nacto * (nacto - 1) * nactv * (nactv - 1) // 4
            bvect_iajb = self.denself.create_four_index(
                nacto, nactv, nacto, nactv
            )

            bvect_iajb.assign(
                bvector,
                ind=self.get_index_of_mask_csf("iajb"),
                begin4=end_3,
                end4=end_4,
            )

            tmp = bvect_iajb.copy()
            bvectors["bvect_iajb_A"] = bvect_iajb
            bvectors["bvect_iajb_A"].iadd_transpose(
                (2, 1, 0, 3), other=tmp, factor=-1.0
            )
            bvectors["bvect_iajb_A"].iadd_transpose(
                (0, 3, 2, 1), other=tmp, factor=-1.0
            )
            bvectors["bvect_iajb_A"].iadd_transpose((2, 3, 0, 1), other=tmp)

            bvect_iajb = self.denself.create_four_index(
                nacto, nactv, nacto, nactv
            )
            bvect_iajb.assign(
                bvector,
                ind=self.get_index_of_mask_csf("iajb"),
                begin4=end_4,
            )
            tmp = bvect_iajb.copy()
            bvectors["bvect_iajb_B"] = bvect_iajb
            bvectors["bvect_iajb_B"].iadd_transpose((2, 1, 0, 3), other=tmp)
            bvectors["bvect_iajb_B"].iadd_transpose((0, 3, 2, 1), other=tmp)
            bvectors["bvect_iajb_B"].iadd_transpose((2, 3, 0, 1), other=tmp)
            del tmp

        CSFRCID.calculate_csf(self, bvectors, sigma)
        return sigma

    def calculate_csf(self, bvectors, out):
        """Constructs  Hamiltonian subspace for CSF"""
        #
        # Integrals
        #
        fock = self.from_cache("fock")
        govvo = self.from_cache("govvo")
        govov = self.from_cache("govov")
        goooo = self.from_cache("goooo")
        gvvvv = self.from_cache("gvvvv")
        gppqq = self.from_cache("gppqq")

        #
        # Ranges
        #
        oo = self.get_range("oo")
        vv = self.get_range("vv")
        ov = self.get_range("ov")

        #
        # local variables
        #
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        factor1 = 1 / (sqrt(2))
        bvect_0 = bvectors["bvect_0"]
        bvect_ia = bvectors["bvect_ia"]
        if nactv > 1:
            bvect_iab = bvectors["bvect_iab"]
        if nacto > 1:
            bvect_iaj = bvectors["bvect_iaj"]
        if nacto > 1 and nactv > 1:
            bvect_iajb_A = bvectors["bvect_iajb_A"]
            bvect_iajb_B = bvectors["bvect_iajb_B"]

        #
        # TEMP OBJ.
        #
        f_oo = fock.copy(**oo)
        f_vv = fock.copy(**vv)
        f_aa = f_vv.copy_diagonal()
        f_ii = f_oo.copy_diagonal()

        t_ov = self.denself.create_two_index(nacto, nactv)
        t_ovo = self.denself.create_three_index(nacto, nactv, nacto)
        t_ooo = self.denself.create_three_index(nacto, nacto, nacto)
        t_ovv = self.denself.create_three_index(nacto, nactv, nactv)

        g_ia = gppqq.copy(**ov)
        g_vv = gppqq.copy(**vv)
        g_oo = gppqq.copy(**oo)

        value_0 = 0.0
        #
        # sigma_0
        #
        #   1) <kC|cK> r_kcKC
        #
        value_0 = bvect_ia.contract("ab,ab", g_ia)
        #
        #   2) <kc|dk> r_kckd
        #
        govvo.contract("abca->abc", out=t_ovv, clear=True)
        value_0 += bvect_iab.contract("abc,abc", t_ovv) * factor1
        if nacto > 1:
            #
            # 1) 1/sqrt(2) <kc|cl> r_kclc
            #
            govvo.contract("abbc->abc", out=t_ovo, clear=True)
            value_0 += bvect_iaj.contract("abc,abc", t_ovo) * factor1
        if nacto > 1 and nactv > 1:
            #
            # 2) sqrt(3)/4 <kl||cd>(kdcl/kcdl) r_kcld
            #
            value_0 += bvect_iajb_A.contract("abcd,adbc", govvo) * (
                2 / (sqrt(12))
            )
            value_0 += bvect_iajb_A.contract("abcd,abdc", govvo) * (
                -1 / (sqrt(12))
            )
            #
            # 3) 1/2(<kd|cl> + <kc|dl>) r_kcld
            #
            value_0 += bvect_iajb_B.contract("abcd,adbc", govvo) * 0.5
        # sigma_iaia
        sigma_ia = self.denself.create_two_index(nacto, nactv)
        #
        #   1) <kc|kc> * r_0
        #
        g_ia.contract("ab->ab", out=sigma_ia, factor=bvect_0)
        #
        #   2) +2f_aa r_ia
        #
        bvect_ia.contract("ab,b->ab", f_aa, out=sigma_ia, factor=2.0)
        #
        #   3) -2f_ii r_ia
        #
        bvect_ia.contract("ab,a->ab", f_ii, out=sigma_ia, factor=-2.0)
        #
        #   4) +<aA|cC> r_ic
        #
        bvect_ia.contract("ab,cb->ac", g_vv, out=sigma_ia, factor=1.0)
        #
        #   5) +<ii|kk> r_ka
        #
        bvect_ia.contract("ab,ca->cb", g_oo, out=sigma_ia, factor=1.0)
        #
        #   6) +<ia||ia> r_ia
        #
        bvect_ia.contract("ab,ab->ab", g_ia, out=sigma_ia, factor=2.0)
        govov.contract("abab->ab", out=t_ov, clear=True)
        bvect_ia.contract("ab,ab->ab", t_ov, out=sigma_ia, factor=-4.0)
        #
        #   7) -2/sqrt(2) f_ac r_iaic
        #
        bvect_iab.contract(
            "abc,bc->ab", f_vv, out=sigma_ia, factor=2.0 * factor1
        )
        #
        #   8) 1/sqrt(2) <aa|cd> r_icid
        #
        gvvvv.contract("aabc,dbc->da", bvect_iab, out=sigma_ia, factor=factor1)
        #
        #   9) -4/sqrt(2)<ia|ic> r_iaic
        #
        govov.contract("abac->abc", out=t_ovv, clear=True)
        bvect_iab.contract(
            "abc,abc->ab", t_ovv, out=sigma_ia, factor=-4.0 * factor1
        )
        #
        #   10) +2/sqrt(2)<ii|ac> r_iaic
        #
        govvo.contract("abca->acb", out=t_ovv, clear=True)
        bvect_iab.contract(
            "abc,abc->ab", t_ovv, out=sigma_ia, factor=2.0 * factor1
        )
        if nacto > 1:
            #
            # 11a) 1/sqrt(2)<kl|ii> r_kala
            #
            goooo.contract("abcc->abc", out=t_ooo, clear=True)
            bvect_iaj.contract("abc,acd->db", t_ooo, sigma_ia, factor=factor1)
            # 11b) 2/sqrt(2)(-f_ki r_kaia)
            f_oo.contract(
                "ab,acb->bc", bvect_iaj, sigma_ia, factor=-2 * factor1
            )
            # 11c)1/sqrt(2)(2<la|ai> - 4<la|ia>) c_iala
            tmp_ovo = govvo.contract("abbc->abc", clear=True)
            bvect_iaj.contract(
                "abc,cba->ab", tmp_ovo, sigma_ia, factor=2 * factor1
            )
            tmp_ovo = govov.contract("abcb->abc", clear=True)
            bvect_iaj.contract(
                "abc,cba->ab", tmp_ovo, sigma_ia, factor=-4 * factor1
            )
            #
            # 12a) sqrt(3)<la|di>r_iald
            #
            bvect_iajb_A.contract(
                "abcd,cbda->ab", govvo, sigma_ia, factor=sqrt(3)
            )
            #
            # 13a)  <la||di>r_iald
            #
            bvect_iajb_B.contract("abcd,cbda->ab", govvo, sigma_ia, factor=1.0)
            bvect_iajb_B.contract(
                "abcd,cbad->ab", govov, sigma_ia, factor=-2.0
            )
        #
        # sigma_iaib
        #
        sigma2 = self.denself.create_three_index(nacto, nactv, nactv)
        sigma3 = self.denself.create_three_index(nacto, nactv, nactv)
        #
        #   1) +2/sqrt(2)<ia|bi> * r_0
        #
        govvo.contract(
            "abca->abc", out=sigma3, factor=(bvect_0 * factor1 * 2.0)
        )
        #
        #   2) +2/sqrt(2)f_ab r_iaia
        #
        bvect_ia.contract("ab,bc->abc", f_vv, out=sigma2, factor=2 * factor1)
        #
        #   3) +2/sqrt(2)<ab|cc> r_icic
        #
        gvvvv.contract(
            "abcc,dc->dab", bvect_ia, out=sigma3, factor=2 * factor1
        )
        #
        #   4) -4/sqrt(2)<ia|ib> r_iaia
        #
        govov.contract("abac->abc", out=t_ovv, clear=True)
        bvect_ia.contract(
            "ab,abc->abc", t_ovv, out=sigma2, factor=-4.0 * factor1
        )
        #
        #   5) +2/sqrt(2)<ii|ab> r_iaia
        #
        govvo.contract("abca->acb", out=t_ovv, clear=True)
        bvect_ia.contract(
            "ab,abc->abc", t_ovv, out=sigma2, factor=2.0 * factor1
        )
        #
        #   6) +f_ac r_ibic
        #
        bvect_iab.contract("abc,dc->adb", f_vv, out=sigma2, factor=1.0)
        #
        #   7) -f_ii r_iaib
        #
        bvect_iab.contract("abc,a->abc", f_ii, out=sigma2, factor=-1.0)
        #
        #   8) +0.5<ii|kk> r_kakb
        #
        bvect_iab.contract("abc,da->dbc", g_oo, out=sigma2, factor=0.5)
        #
        #   9) +<ab|cd> r_icid
        #
        gvvvv.contract("abcd,ecd->eab", bvect_iab, out=sigma2, factor=0.5)
        #
        #   10) -2<ib|ic> r_iaic
        #
        govov.contract("abac->abc", out=t_ovv, clear=True)
        bvect_iab.contract("abc,adc->abd", t_ovv, out=sigma2, factor=-2.0)
        #
        #
        #   11) +1<ii|bc> r_iaic
        govvo.contract("abca->acb", out=t_ovv, clear=True)
        bvect_iab.contract("abc,adc->abd", t_ovv, out=sigma2, factor=1.0)
        if nacto > 1:
            # sigma_iaib
            #
            # 12a)  (-2<lb|ia> + <lb|ai>)r_iala
            #
            bvect_iaj.contract("abc,cdab->abd", govov, sigma3, factor=-2.0)
            bvect_iaj.contract("abc,cdba->abd", govvo, sigma3)
            # 12b)  (-2<la|ib> + <la|bi>)r_lbib
            bvect_iaj.contract("abc,adcb->cdb", govov, sigma3, factor=-2.0)
            bvect_iaj.contract("abc,adbc->cdb", govvo, sigma3)
            #
            # 13)  sqrt(3/2)P_ab<lb|di> r_iald
            #
            bvect_iajb_A.contract(
                "abcd,ceda->abe", govvo, sigma2, factor=sqrt(3 / 2)
            )
            #
            # 14a) 1/sqrt(2) <kl|ii> r_kalb
            #
            goooo.contract("abcc->abc", out=t_ooo, clear=True)
            bvect_iajb_B.contract(
                "abcd,ace->ebd", t_ooo, sigma3, factor=factor1
            )
            # 14b) 1/sqrt(2) P_ab <lb||di> r_iald
            bvect_iajb_B.contract(
                "abcd,ceda->abe", govvo, sigma2, factor=factor1
            )
            bvect_iajb_B.contract(
                "abcd,cead->abe", govov, sigma2, factor=-factor1
            )
            # 14c) -1/sqrt(2) P_ab <kb|id> r_kaid
            bvect_iajb_B.contract(
                "abcd,aecd->cbe", govov, sigma2, factor=-factor1
            )
            # 14d) -1/sqrt(2) P_ab f_li r_ialb
            bvect_iajb_B.contract(
                "abcd,ca->abd", f_oo, sigma2, factor=-factor1
            )
            #
            # sigma_iaja
            #
            sigma4 = self.denself.create_three_index(nacto, nactv, nacto)
            sigma5 = self.denself.create_three_index(nacto, nactv, nacto)
            #
            # 1)  2/sqrt(2) <ja|ai> r_0
            #
            govvo.contract(
                "abbc->cba", out=sigma4, factor=2 * factor1 * bvect_0
            )
            #
            # 2a)  2/sqrt(2) <kk|ij> r_kaka
            #
            tmp_ooo = goooo.contract("aabc->abc")
            bvect_ia.contract(
                "ab,acd->cbd", tmp_ooo, sigma4, factor=2 * factor1
            )
            # 2b)  1/sqrt(2) P_ij (2<ia|aj> - 4<ia|ja>)c_iaia
            tmp_ovo = govvo.contract("abbc->abc")
            bvect_ia.contract(
                "ab,abc->abc", tmp_ovo, sigma5, factor=2 * factor1
            )
            tmp_ovo = govov.contract("abcb->abc")
            bvect_ia.contract(
                "ab,abc->abc", tmp_ovo, sigma5, factor=-4 * factor1
            )
            # 2c)  -2/sqrt(2) P_ij f_ij c_iaia
            bvect_ia.contract("ab,ac->abc", f_oo, sigma5, factor=-2 * factor1)
            #
            # 3)  P_ij (<ia|dj> - 2<ia|jd>)c_iaid
            #
            bvect_iab.contract("abc,abcd->abd", govvo, sigma5)
            bvect_iab.contract("abc,abdc->abd", govov, sigma5, factor=-2.0)
            #
            # 4a)  <aa|cc> r_icjc
            #
            bvect_iaj.contract("abc,db->adc", g_vv, sigma4)
            # 4b)  <kl|ij> r_kala
            bvect_iaj.contract("abc,acde->dbe", goooo, sigma4)
            # 4c)  -P_ij f_ki r_kaja
            bvect_iaj.contract("abc,ad->dbc", f_oo, sigma5, factor=-1.0)
            # 4d)  P_ij(<la|aj> - 2<la|ja>)c_iala
            tmp_ovo = govvo.contract("abbc->abc")
            bvect_iaj.contract("abc,cbd->abd", tmp_ovo, sigma5)
            tmp_ovo = govov.contract("abcb->abc")
            bvect_iaj.contract("abc,cbd->abd", tmp_ovo, sigma5, factor=-2.0)
            # 4e)  f_aa r_iaja
            bvect_iaj.contract("abc,b->abc", f_aa, sigma5, factor=1.0)
            #
            # 5)  P_ij sqrt(3/2) <la|dj> r_iald
            #
            bvect_iajb_A.contract(
                "abcd,cbde->abe", govvo, sigma5, factor=sqrt(3 / 2)
            )
            #
            # 6a)  1/sqrt(2) <aa|cd> r_icjd
            #
            gvvvv.contract(
                "aabc,dbec->dae", bvect_iajb_B, sigma4, factor=factor1
            )
            # 6b)  1/sqrt(2) P_ij <la||dj> r_iald
            bvect_iajb_B.contract(
                "abcd,cbde->abe", govvo, sigma5, factor=factor1
            )
            bvect_iajb_B.contract(
                "abcd,cbed->abe", govov, sigma5, factor=-factor1
            )
            # 6c)  -1/sqrt(2) P_ij <la|jc> r_icla
            bvect_iajb_B.contract(
                "abcd,cdeb->ade", govov, sigma5, factor=-factor1
            )
            # 6d)  1/sqrt(2) P_ij f_ad r_iajd
            bvect_iajb_B.contract("abcd,bd->abc", f_vv, sigma5, factor=factor1)
            #
            # sigma_iajb^A
            #
            sigma6 = self.denself.create_four_index(nacto, nactv, nacto, nactv)
            sigma7 = self.denself.create_four_index(nacto, nactv, nacto, nactv)
            #
            # 1)  sqrt(3) (<ab|ij> - <ab|ji>)->jabi - iabj
            #
            govvo.contract("abcd->acdb", out=sigma6, factor=sqrt(3) * bvect_0)
            govvo.contract("abcd->abdc", out=sigma6, factor=-sqrt(3) * bvect_0)
            #
            # 2)  sqrt(3) P_ij/ab(<ib|aj>)c_iaia
            #
            bvect_ia.contract("ab,acbd->abdc", govvo, sigma7, factor=sqrt(3))
            #
            # 3)  sqrt(3/2)P_ij/ab (<ib|dj>)c_iaid
            #
            bvect_iab.contract(
                "abc,adce->abed", govvo, sigma7, factor=sqrt(3) / sqrt(2)
            )
            #
            # 4)  sqrt(3/2)P_ij/ab <lb|aj> r_iala
            #
            bvect_iaj.contract(
                "abc,cdbe->abed", govvo, sigma7, factor=sqrt(3) / sqrt(2)
            )
            #
            # 5a)  1/2 <ab||cd> r_icjd
            #
            gvvvv.contract("abcd,ecfd->eafb", bvect_iajb_A, sigma6, factor=0.5)
            gvvvv.contract(
                "abcd,edfc->eafb", bvect_iajb_A, sigma6, factor=-0.5
            )
            # 5b)  1/2 <kl||ij> r_kalb
            bvect_iajb_A.contract("abcd,acef->ebfd", goooo, sigma6, factor=0.5)
            bvect_iajb_A.contract(
                "abcd,acef->fbed", goooo, sigma6, factor=-0.5
            )
            # 5c)  f_bd r_iajd
            bvect_iajb_A.contract("abcd,ed->abce", f_vv, sigma6)
            # 5d)  f_ad r_jbid
            bvect_iajb_A.contract("abcd,ed->ceab", f_vv, sigma6)
            # 5e)  -f_ik r_kajb
            bvect_iajb_A.contract("abcd,ea->ebcd", f_oo, sigma6, factor=-1.0)
            # 5e)  -f_jl r_ialb
            bvect_iajb_A.contract("abcd,ec->abed", f_oo, sigma6, factor=-1.0)
            # 5f)  P_ij/ab[(<lb||dj> +1/2<lb|dj>)r_iald]
            bvect_iajb_A.contract(
                "abcd,cedf->abfe", govvo, sigma7, factor=3 / 2
            )
            bvect_iajb_A.contract(
                "abcd,cefd->abfe", govov, sigma7, factor=-1.0
            )
            #
            # 6)  sqrt(3)<lb|dj> r_iald
            #
            bvect_iajb_B.contract(
                "abcd,cedf->abfe", govvo, sigma7, factor=sqrt(3) / 2
            )
            #
            # sigma_iajb^B
            #
            sigma8 = self.denself.create_four_index(nacto, nactv, nacto, nactv)
            sigma9 = self.denself.create_four_index(nacto, nactv, nacto, nactv)
            #
            # 1)(<ab|ij> + <ab|ji>)->jabi + iabj
            #
            govvo.contract("abcd->acdb", out=sigma8, factor=bvect_0)
            govvo.contract("abcd->abdc", out=sigma8, factor=bvect_0)
            #
            # 2a)P_ab(<ib|aj>-2<ib|ja>)r_iaia
            #
            bvect_ia.contract("ab,acbd->abdc", govvo, sigma9)
            bvect_ia.contract("ab,acdb->abdc", govov, sigma9, factor=-2.0)
            # 2b)P_ab(<jb|ai>-2<jb|ia>)r_jaja
            bvect_ia.contract("ab,acbd->dbac", govvo, sigma9)
            bvect_ia.contract("ab,acdb->dbac", govov, sigma9, factor=-2.0)
            #
            # 3a) 1/sqrt(2)P_ab(<kk|ij>)r_kakb
            #
            tmp_ooo = goooo.contract("aabc->abc", clear=True)
            bvect_iab.contract(
                "abc,ade->dbec", tmp_ooo, sigma9, factor=1 / sqrt(2)
            )
            # 3b) -1/sqrt(2)P_ab f_ij r_iaib
            bvect_iab.contract(
                "abc,ad->abdc", f_oo, sigma9, factor=-1 / sqrt(2)
            )
            # 3c) -1/sqrt(2)P_ab f_ij r_jajb
            bvect_iab.contract(
                "abc,da->dbac", f_oo, sigma9, factor=-1 / sqrt(2)
            )
            # 3d) 1/sqrt(2)P_ab (<ib|dj> - 2<ib|jd>)r_iaid
            bvect_iab.contract(
                "abc,adce->abed", govvo, sigma9, factor=1 / sqrt(2)
            )
            bvect_iab.contract(
                "abc,adec->abed", govov, sigma9, factor=-2 * 1 / sqrt(2)
            )
            # 3e) 1/sqrt(2)P_ab (<jb|di> - 2<jb|id>)r_jajd
            bvect_iab.contract(
                "abc,adce->ebad", govvo, sigma9, factor=1 / sqrt(2)
            )
            bvect_iab.contract(
                "abc,adec->ebad", govov, sigma9, factor=-2 * 1 / sqrt(2)
            )
            #
            # 4a) 1/sqrt(2)P_ab (<ab|cc>r_icjc)
            #
            gvvvv.contract(
                "abcc,dce->daeb", bvect_iaj, sigma9, factor=1 / sqrt(2)
            )
            # 4b) 2/sqrt(2)P_ab f_ab r_iaja
            bvect_iaj.contract(
                "abc,bd->abcd", f_vv, sigma9, factor=2 * 1 / sqrt(2)
            )
            # 4b) 1/sqrt(2)P_ab(<lb|aj> - <lb|ja>)r_iala
            bvect_iaj.contract(
                "abc,cdbe->abed", govvo, sigma9, factor=1 / sqrt(2)
            )
            bvect_iaj.contract(
                "abc,cdeb->abed", govov, sigma9, factor=-2 * 1 / sqrt(2)
            )
            # 4c) sqrt(2)P_ab(<lb|ai> - <lb|ia>)r_laja
            bvect_iaj.contract(
                "abc,adbe->ebcd", govvo, sigma9, factor=1 / sqrt(2)
            )
            bvect_iaj.contract(
                "abc,adeb->ebcd", govov, sigma9, factor=-2 * 1 / sqrt(2)
            )
            #
            # 5) sqrt(3)/2 P_ab(<lb|dj>r_iald + <lb|di>r_jald)
            #
            bvect_iajb_A.contract(
                "abcd,cedf->abfe", govvo, sigma9, factor=sqrt(3) / 2
            )
            bvect_iajb_A.contract(
                "abcd,cedf->fbae", govvo, sigma9, factor=sqrt(3) / 2
            )
            #
            # 6a) <ab|cd> r_icjd
            #
            gvvvv.contract("abcd,ecfd->eafb", bvect_iajb_B, sigma8)
            # 6b) <kl|ij> r_kalb
            bvect_iajb_B.contract("abcd,acef->ebfd", goooo, sigma8, factor=1.0)
            # 6c) 1/2P_ab(<lb||dj> - <lb|jd>)r_iald
            bvect_iajb_B.contract("abcd,cedf->abfe", govvo, sigma9, factor=0.5)
            bvect_iajb_B.contract(
                "abcd,cefd->abfe", govov, sigma9, factor=-1.0
            )
            # 6d) 1/2P_ab(<la||di> - <la|id>)r_jbld
            bvect_iajb_B.contract("abcd,cedf->feab", govvo, sigma9, factor=0.5)
            bvect_iajb_B.contract(
                "abcd,cefd->feab", govov, sigma9, factor=-1.0
            )
            # 6e) f_bd r_iajd
            bvect_iajb_B.contract("abcd,ed->abce", f_vv, sigma8, factor=1.0)
            # 6e) f_ac r_icjb
            bvect_iajb_B.contract("abcd,eb->aecd", f_vv, sigma8, factor=1.0)
            # 6f) -f_ki r_kajb
            bvect_iajb_B.contract("abcd,ae->ebcd", f_oo, sigma8, factor=-1.0)
            # 6g) -f_lj r_ialb
            bvect_iajb_B.contract("abcd,ce->abed", f_oo, sigma8, factor=-1.0)

        end_1 = nacto * nactv + 1
        end_2 = end_1 + nacto * (nactv * (nactv - 1)) // 2
        end_3 = end_2 + nacto * (nacto - 1) // 2 * nactv
        end_4 = end_3 + (nacto * (nacto - 1) // 2 * nactv * (nactv - 1) // 2)

        out.set_element(0, value_0)
        out.iadd(sigma_ia.array.ravel(), begin0=1, end0=nacto * nactv + 1)

        tmp = self.denself.create_four_index(nacto, nactv, nacto, nactv)
        sigma2.expand("abc->abac", tmp)
        out.assign(
            tmp.array[self.get_mask_csf("iab")], begin0=end_1, end0=end_2
        )
        tmp.itranspose([0, 3, 2, 1])
        out.iadd(tmp.array[self.get_mask_csf("iab")], begin0=end_1, end0=end_2)
        tmp.clear()
        sigma3.expand("abc->abac", tmp)
        out.iadd(tmp.array[self.get_mask_csf("iab")], begin0=end_1, end0=end_2)
        if nacto > 1:
            tmp.clear()
            sigma5.expand("abc->abcb", tmp)
            out.assign(
                tmp.array[self.get_mask_csf("iaj")], begin0=end_2, end0=end_3
            )
            tmp.itranspose([2, 1, 0, 3])
            out.iadd(
                tmp.array[self.get_mask_csf("iaj")], begin0=end_2, end0=end_3
            )
            tmp.clear()
            sigma4.expand("abc->abcb", tmp)
            out.iadd(
                tmp.array[self.get_mask_csf("iaj")], begin0=end_2, end0=end_3
            )
            out.assign(
                sigma6.array[self.get_mask_csf("iajb")],
                begin0=end_3,
                end0=end_4,
            )
            sigma6.clear()
            sigma6.iadd_transpose((0, 1, 2, 3), other=sigma7)
            sigma6.iadd_transpose((2, 3, 0, 1), other=sigma7)
            sigma6.iadd_transpose((2, 1, 0, 3), other=sigma7, factor=-1.0)
            sigma6.iadd_transpose((0, 3, 2, 1), other=sigma7, factor=-1.0)
            out.iadd(
                sigma6.array[self.get_mask_csf("iajb")],
                begin0=end_3,
                end0=end_4,
            )
            out.assign(sigma8.array[self.get_mask_csf("iajb")], begin0=end_4)
            sigma8.clear()
            sigma8.iadd_transpose((0, 1, 2, 3), other=sigma9)
            sigma8.iadd_transpose((0, 3, 2, 1), other=sigma9)
            out.iadd(sigma8.array[self.get_mask_csf("iajb")], begin0=end_4)
