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

from pybest.log import log

from .rcid import RCIDBase
from .sd_base import SD


class SDRCID(SD, RCIDBase):
    """Slater Determinant Restricted Configuration Interaction Doubles child class.
    Contains all required methods to diagonalize the RCID Hamiltonian using SD basis.
    """

    @SD.dimension.setter
    def dimension(self, new=None):
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        if new is not None:
            self._dimension = self.set_dimension(new, nacto, nactv)
        else:
            log.warn(
                "The dimension may be wrong!"
                "Please set the dimension property with one of the strings (RCIS, RCID, RCISD)"
            )

    def compute_h_diag(self, *args):
        """Calculating the guess vector for SD basis.

        hdiag:
            (OneIndex object) contains guess vector for SD basis.
        """
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
        nact = self.occ_model.nact[0]

        #
        # Ranges
        #
        end_ab = nacto * nacto * nactv * nactv + 1
        if nacto > 1:
            end_aa = nacto * (nacto - 1) * nactv * (nactv - 1) // 4 + end_ab

        #
        # Intermediates
        #
        fii = self.lf.create_one_index(nacto)
        fock.copy_diagonal(out=fii, end=nacto)
        faa = self.lf.create_one_index(nactv)
        fock.copy_diagonal(out=faa, begin=nacto, end=nact)

        g_ijij = self.lf.create_two_index(nacto, nacto)
        goooo.contract("abab->ab", out=g_ijij)
        g_ijji = self.lf.create_two_index(nacto, nacto)
        goooo.contract("abba->ab", out=g_ijji, factor=-1.0)

        g_abab = self.lf.create_two_index(nactv, nactv)
        gvvvv.contract("abab->ab", out=g_abab)
        g_abba = self.lf.create_two_index(nactv, nactv)
        gvvvv.contract("abba->ab", out=g_abba, factor=-1.0)

        g_iaia = self.lf.create_two_index(nacto, nactv)
        govov.contract("abab->ab", out=g_iaia)
        g_iaai = self.lf.create_two_index(nacto, nactv)
        govvo.contract("abba->ab", out=g_iaai, factor=-1.0)

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
        hdiag.assign(r_iajb.array.ravel(), begin0=1, end0=end_ab)

        #
        # Assign same spin block
        #
        if nacto > 1:
            #
            # same spin terms
            #
            # <ab|ba>
            #
            g_abba.expand("bd->abcd", r_iajb)
            #
            # <ij|ji>
            #
            g_ijji.expand("ac->abcd", r_iajb)
            hdiag.assign(
                r_iajb.array[self.get_mask()], begin0=end_ab, end0=end_aa
            )
            hdiag.assign(r_iajb.array[self.get_mask()], begin0=end_aa)
        return hdiag

    def build_subspace_hamiltonian(self, bvector, hamiltonian, *args):
        """
        Used by the davidson module to construct subspace Hamiltonian.

        **Arguments:**

        bvector:
            (OneIndex object) contains current approximation to CI coefficients.

        hamiltonian:
            (OneIndex object) used by the Davidson module and contains
            diagonal approximation to the full matrix.
        """
        #
        # Integrals
        #
        fock = self.from_cache("fock")
        govvo = self.from_cache("govvo")
        govov = self.from_cache("govov")
        goooo = self.from_cache("goooo")
        gvvvv = self.from_cache("gvvvv")

        #
        # Ranges
        #
        oo = self.get_range("oo")
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
        end_ab = nacto * nacto * nactv * nactv + 1
        size_aa = nacto * (nacto - 1) * nactv * (nactv - 1) // 4
        #
        # Bvectors
        #
        b_dab = self.denself.create_four_index(nacto, nactv, nacto, nactv)
        #
        # Bvectors assignment
        #
        b_dab.assign(bvector, begin4=1, end4=end_ab)
        #
        # Sigma vector
        #
        sigma_d = self.denself.create_four_index(nacto, nactv, nacto, nactv)
        #
        # block alpha-beta (Opposite spins (iaJB))
        #
        # 1) <Ja|Bi> * r_0
        govvo.contract(
            "abcd->dbac", out=sigma_d, factor=bvector.get_element(0)
        )

        # 2) <kD|cL> r_kcLD
        value_0 = b_dab.contract("abcd,adbc", govvo)

        # 3) -f_ki r_kajb
        b_dab.contract("abcd,ae->ebcd", f_oo, out=sigma_d, factor=-1.0)

        # 4) -f_lj r_ialb
        b_dab.contract("abcd,ce->abed", f_oo, out=sigma_d, factor=-1.0)

        # 5) +f_ac r_icjb
        b_dab.contract("abcd,eb->aecd", f_vv, out=sigma_d)

        # 6) +f_bd r_iajd
        b_dab.contract("abcd,ed->abce", f_vv, out=sigma_d)

        # 7) +<ka|ci> r_kcJB
        b_dab.contract("abcd,aebf->fecd", govvo, out=sigma_d)

        # 8) -<ka|ic> r_kcJB
        b_dab.contract("abcd,aefb->fecd", govov, out=sigma_d, factor=-1.0)

        # 9) +<LB|DJ> r_iaLD
        b_dab.contract("abcd,cedf->abfe", govvo, out=sigma_d)

        # 10) -<LB|JD> r_iaLD
        b_dab.contract("abcd,cefd->abfe", govov, out=sigma_d, factor=-1.0)

        # 11) <aB|cD> r_icJD
        gvvvv.contract("abcd,ecfd->eafb", b_dab, out=sigma_d)

        # 12) <kl|ij> r_kaLB
        b_dab.contract("abcd,acef->ebfd", goooo, out=sigma_d)

        # 13) -<kB|iD> r_kaJD
        b_dab.contract("abcd,aefd->fbce", govov, out=sigma_d, factor=-1.0)

        # 14) -<La|Jc> r_icLB
        b_dab.contract("abcd,cefb->aefd", govov, out=sigma_d, factor=-1.0)
        #
        # Assign to sigma vector
        #
        sigma = self.lf.create_one_index(self.dimension)
        sigma.assign(sigma_d.array.ravel(), begin0=1, end0=end_ab)

        if nacto > 1:
            #
            # block alpha-alpha (iajb) / beta-beta (IAJB)
            #
            b_daa = self.denself.create_four_index(nacto, nactv, nacto, nactv)
            end_aa = nacto * (nacto - 1) * nactv * (nactv - 1) // 4 + end_ab
            for shift in [0, size_aa]:
                sigma_d.clear()
                b_daa.clear()
                b_daa.assign(
                    bvector,
                    ind=self.get_index_of_mask(),
                    begin4=end_ab + shift,
                    end4=end_aa + shift,
                )
                # create tmp object to account for symmetry
                tmp = b_daa.copy()
                b_daa.iadd_transpose((2, 1, 0, 3), other=tmp, factor=-1.0)
                b_daa.iadd_transpose((0, 3, 2, 1), other=tmp, factor=-1.0)
                b_daa.iadd_transpose((2, 3, 0, 1), other=tmp)
                del tmp
                # 1) <kl||cd> r_kcld (<kd|cl> - <kc|dl>)
                value_0 += b_daa.contract("abcd,adbc", govvo, factor=0.25)
                value_0 += b_daa.contract("abcd,abdc", govvo, factor=-0.25)
                # 2) <ab||ij> * r_0 (<ib|aj> - <ia|bj>)
                govvo.contract(
                    "abcd->acdb", out=sigma_d, factor=bvector.get_element(0)
                )
                govvo.contract(
                    "abcd->abdc", out=sigma_d, factor=-bvector.get_element(0)
                )
                # 3) -f_ki r_kajb
                b_daa.contract("abcd,ae->ebcd", f_oo, sigma_d, factor=-1.0)
                # 4) -f_lj r_ialb
                b_daa.contract("abcd,ce->abed", f_oo, sigma_d, factor=-1.0)
                # 5) f_ad r_idjb
                b_daa.contract("abcd,eb->aecd", f_vv, sigma_d)
                # 6) f_bd r_iajd
                b_daa.contract("abcd,ed->abce", f_vv, sigma_d)
                # 7) <ab||cd> r_icjd
                gvvvv.contract("abcd,ecfd->eafb", b_daa, sigma_d, factor=0.5)
                gvvvv.contract("abcd,edfc->eafb", b_daa, sigma_d, factor=-0.5)
                # 8) <ij||kl> r_kalb
                goooo.contract("abcd,cedf->aebf", b_daa, sigma_d, factor=0.5)
                goooo.contract("abcd,decf->aebf", b_daa, sigma_d, factor=-0.5)
                # 9) <lb||dj> r_iald (<lb|dj> - <lb|jd>)
                b_daa.contract("abcd,cedf->abfe", govvo, sigma_d)
                b_daa.contract("abcd,cefd->abfe", govov, sigma_d, factor=-1.0)
                # 10) -<lb||di> r_jald (-<lb|di> + <lb|id>)
                b_daa.contract("abcd,cedf->fbae", govvo, sigma_d, factor=-1.0)
                b_daa.contract("abcd,cefd->fbae", govov, sigma_d)
                # 11) <ka||ci> r_kcjb (+<ka|ci> - <ka|ic>)
                b_daa.contract("abcd,aebf->fecd", govvo, sigma_d)
                b_daa.contract("abcd,aefb->fecd", govov, sigma_d, factor=-1.0)
                # 12) -<ka||cj> r_kcib (-<ka|cj> + <ka|jc>))
                b_daa.contract("abcd,aebf->cefd", govvo, sigma_d, factor=-1.0)
                b_daa.contract("abcd,aefb->cefd", govov, sigma_d)
                #
                # Coupling terms between same spin and opposite spin
                #
                # 13) <iajb|H|kcLD> and <iajb|H|KCld>
                #
                if shift == 0:
                    # a) -<La|Dj>(r_ibLD) * bvector
                    b_dab.contract(
                        "abcd,cedf->aefb", govvo, sigma_d, factor=-1.0
                    )
                    # b) +<La|Di>(r_jbLD) * bvector
                    b_dab.contract(
                        "abcd,cedf->feab", govvo, sigma_d, factor=1.0
                    )
                    # c) <Lb|Dj>(r_iaLD) * bvector
                    b_dab.contract(
                        "abcd,cedf->abfe", govvo, sigma_d, factor=1.0
                    )
                    # d) -<Lb|Di>(r_jaLD) * bvector
                    b_dab.contract(
                        "abcd,cedf->fbae", govvo, sigma_d, factor=-1.0
                    )
                else:
                    # a) -<Ka|Cj>(r_KCib) * bvector
                    b_dab.contract(
                        "abcd,aebf->cefd", govvo, sigma_d, factor=-1.0
                    )
                    # b) +<Ka|Ci>(r_KCjb) * bvector
                    b_dab.contract(
                        "abcd,aebf->fecd", govvo, sigma_d, factor=1.0
                    )
                    # c) <Kb|Cj>(r_KCia) * bvector
                    b_dab.contract(
                        "abcd,aebf->cdfe", govvo, sigma_d, factor=1.0
                    )
                    # d) -<Kb|Ci>(r_KCja) * bvector
                    b_dab.contract(
                        "abcd,aebf->fdce", govvo, sigma_d, factor=-1.0
                    )
                sigma.assign(
                    sigma_d.array[self.get_mask()],
                    begin0=end_ab + shift,
                    end0=end_aa + shift,
                )
                sigma_d.clear()
                #
                # Coupling terms between opposite spin and same spin
                #
                # 14) <iaJB|H|kcld> and <iaJB|H|KCLD>
                #
                if shift == 0:
                    b_daa.contract("abcd,cedf->abfe", govvo, sigma_d)
                else:
                    b_daa.contract("abcd,aebf->fecd", govvo, sigma_d)
                sigma.iadd(sigma_d.array.ravel(), begin0=1, end0=end_ab)

        sigma.set_element(0, value_0)
        return sigma
