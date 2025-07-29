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

from math import sqrt

from pybest.log import log

from .csf_base import CSF
from .csf_cid import CSFRCID
from .csf_cis import CSFRCIS
from .rcisd import RCISDBase


class CSFRCISD(CSF, RCISDBase):
    """Configuration State Function Restricted Configuration Interaction Singles
    and Doubles (CSFRCISD) class. Contains all required methods to diagonalize
    the RCISD Hamiltonian using CSF basis.
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

    def h_diag_singles(self):
        """Calculating the CIS part of CISD guess vector in CSF basis.

        hdiag:
            (OneIndex object) contains guess vector for CSF basis.
        """
        self.dimension = "CIS"
        hdiag = self.denself.create_one_index(self.dimension)
        hdiag_a = CSFRCIS.compute_h_diag(self)
        hdiag.assign(hdiag_a, end0=self.dimension)
        self.dimension = "CISD"
        return hdiag

    def h_diag_doubles(self, *args):
        """Calculating the CID part of CISD guess vector in CSF basis.

        hdiag:
            (OneIndex object) contains a guess vector for CSF basis.
        """
        self.dimension = "CID"
        hdiag = CSFRCID.compute_h_diag(self, *args)
        self.dimension = "CISD"
        return hdiag

    def compute_h_diag(self, *args):
        """Collects the CIS, and CID part of the guess vector in CSF basis
        and merges into CISD guess vector
        """
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        hdiag = self.denself.create_one_index(self.dimension)
        hdiag_s = self.h_diag_singles()
        hdiag_d = self.h_diag_doubles(*args)
        hdiag.set_element(0, hdiag_s.get_element(0) + hdiag_d.get_element(0))
        hdiag.assign(hdiag_s.array[1:], begin0=1, end0=nactv * nacto + 1)
        hdiag.iadd(hdiag_d.array[1:], begin0=nactv * nacto + 1)
        return hdiag

    def build_subspace_hamiltonian(self, bvector, hamiltonian, *args):
        """
        Constructing Hamiltonian subspace for CSF basis

        **Arguments:**

        bvector:
            (OneIndex object) contains current approximation to CI coefficients
            in the SD basis

        """
        #
        # Integrals
        #
        fock = self.from_cache("fock")
        gooov = self.from_cache("gooov")
        govvv = self.from_cache("govvv")
        #
        # Ranges
        #
        ov = self.get_range("ov")
        #
        # Local variables
        #
        fia = fock.copy(**ov)
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        end_ia = nacto * nactv + 1
        end_p = end_ia + end_ia - 1
        end_iab = end_p + nacto * (nactv * (nactv - 1)) // 2
        end_iaj = end_iab + nactv * (nacto * (nacto - 1)) // 2
        end_iajb = (
            end_iaj + nactv * (nactv - 1) // 2 * (nacto * (nacto - 1)) // 2
        )
        #
        # Sigma Vectors
        #
        sigma = self.denself.create_one_index(self.dimension)
        sigma_s = self.denself.create_two_index(nacto, nactv)
        sigma_ia = self.denself.create_two_index(nacto, nactv)
        sigma_iab = self.denself.create_three_index(nacto, nactv, nactv)
        sigma_iaj = self.denself.create_three_index(nacto, nactv, nacto)
        sigma_iajb_a = self.denself.create_four_index(
            nacto, nactv, nacto, nactv
        )
        sigma_iajb_b = self.denself.create_four_index(
            nacto, nactv, nacto, nactv
        )
        #
        # Bvectors
        #
        b_sa = self.denself.create_two_index(nacto, nactv)
        bvect_ia = self.denself.create_two_index(nacto, nactv)
        bvect_iaib = self.denself.create_four_index(nacto, nactv, nacto, nactv)
        #
        # Bvectors assignment
        #
        b_sa.assign(bvector, begin2=1, end2=end_ia)
        bvect_ia.assign(bvector, begin2=end_ia, end2=end_p)
        bvect_iaib.assign(
            bvector,
            ind=CSF.get_index_of_mask_csf(self, "iab"),
            begin4=end_p,
            end4=end_iab,
        )
        bvect_iab = bvect_iaib.contract("abac->abc", clear=True)
        bvect_iab.iadd(bvect_iaib.contract("abac->acb", clear=True))
        if nacto >= 2 and nactv >= 1:
            bvect_iaja = self.denself.create_four_index(
                nacto, nactv, nacto, nactv
            )
            end_iaj = end_iab + nactv * (nacto * (nacto - 1)) // 2
            bvect_iaja.assign(
                bvector,
                ind=CSFRCID.get_index_of_mask_csf(self, "iaj"),
                begin4=end_iab,
                end4=end_iaj,
            )
            bvect_iaj = bvect_iaja.contract("abcb->abc", clear=True)
            bvect_iaj.iadd(bvect_iaja.contract("abcb->cba", clear=True))
            del bvect_iaja

        if nacto >= 2 and nactv >= 2:
            end_iajb_a = (
                end_iaj + nacto * (nacto - 1) * nactv * (nactv - 1) // 4
            )
            bvect_iajb = self.denself.create_four_index(
                nacto, nactv, nacto, nactv
            )

            bvect_iajb.assign(
                bvector,
                ind=CSFRCID.get_index_of_mask_csf(self, "iajb"),
                begin4=end_iaj,
                end4=end_iajb_a,
            )

            tmp = bvect_iajb.copy()
            bvect_iajb_a = bvect_iajb
            bvect_iajb_a.iadd_transpose((2, 1, 0, 3), other=tmp, factor=-1.0)
            bvect_iajb_a.iadd_transpose((0, 3, 2, 1), other=tmp, factor=-1.0)
            bvect_iajb_a.iadd_transpose((2, 3, 0, 1), other=tmp)

            bvect_iajb = self.denself.create_four_index(
                nacto, nactv, nacto, nactv
            )
            bvect_iajb.assign(
                bvector,
                ind=CSFRCID.get_index_of_mask_csf(self, "iajb"),
                begin4=end_iajb_a,
            )
            tmp = bvect_iajb.copy()
            bvect_iajb_b = bvect_iajb
            bvect_iajb_b.iadd_transpose((2, 1, 0, 3), other=tmp)
            bvect_iajb_b.iadd_transpose((0, 3, 2, 1), other=tmp)
            bvect_iajb_b.iadd_transpose((2, 3, 0, 1), other=tmp)
            del tmp, bvect_iajb
        #
        # Assign Singles and Doubles block
        #
        singles = self.build_subspace_hamiltonian_singles(
            bvector.copy(begin=0, end=end_ia), hamiltonian, *args
        )
        doubles = self.build_subspace_hamiltonian_doubles(
            bvector, hamiltonian, *args
        )
        sigma.set_element(0, singles.get_element(0) + doubles.get_element(0))
        sigma.iadd(singles.array[1:], begin0=1, end0=end_ia)
        sigma.iadd(doubles.array[1:], begin0=end_ia)
        del singles, doubles
        self.dimension = "CISD"

        #
        # Calculating Singles-Doubles Coupling terms.
        #
        #
        # sigma_ia sector
        #

        # 1a) 2/sqrt(2)fia *c_iaia
        bvect_ia.contract("ab,ab->ab", fia, out=sigma_s, factor=2 / (sqrt(2)))
        # 1b) 2/sqrt(2)<ia|cc> *c_icic
        govvv.contract(
            "abcc,ac->ab", bvect_ia, out=sigma_s, factor=2.0 / sqrt(2)
        )
        # 1c) -2/sqrt(2)<kk|ia> *c_kaka
        bvect_ia.contract(
            "ab,aacb->cb", gooov, out=sigma_s, factor=-2.0 / sqrt(2)
        )
        # 2a) fid *c_iaid
        bvect_iab.contract("abc,ac->ab", fia, out=sigma_s, factor=1.0)
        # 2b) (<ia|dc>) *c_icid
        govvv.contract("abcd,adc->ab", bvect_iab, out=sigma_s, factor=1.0)
        # 2c) -<kk|id> *c_kakd
        bvect_iab.contract("abc,aadc->db", gooov, out=sigma_s, factor=-1.0)
        #
        # sigma_pairs sector
        #
        # 1) 2/sqrt(2) (<aa|ci>c_ic - <ka|ii>c_ka)(iika)
        govvv.contract("abcc,ab->ac", b_sa, out=sigma_ia, factor=2.0 / sqrt(2))
        b_sa.contract(
            "ab,ccab->cb", gooov, out=sigma_ia, factor=-2.0 / sqrt(2)
        )
        #
        # sigma_iaib sector
        #
        # 1a) (<ab|ci> + <ab|ic>)c_ic (icba)/(icab)
        govvv.contract("abcd,ab->adc", b_sa, out=sigma_iab, factor=1)
        govvv.contract("abcd,ab->acd", b_sa, out=sigma_iab, factor=1)
        # 1b) -P_ab(<ka|ii>c_kb (iika) (iikb)
        gooov.contract("aabc,bd->acd", b_sa, out=sigma_iab, factor=-1)
        gooov.contract("aabc,bd->adc", b_sa, out=sigma_iab, factor=-1)
        if nacto > 1:
            #
            # sigma_s
            #
            # 1a) fla *c_iala
            bvect_iaj.contract("abc,cb->ab", fia, out=sigma_s)
            # 1b) <la|cc> *c_iclc
            govvv.contract("abcc,dca->db", bvect_iaj, out=sigma_s)
            # 1c) -<kl|ia> *c_kala
            bvect_iaj.contract("abc,acdb->db", gooov, out=sigma_s, factor=-1.0)
            #
            #
            # 2a) sqrt(3/2)fld *c_iald
            bvect_iajb_a.contract(
                "abcd,cd->ab", fia, out=sigma_s, factor=sqrt(3 / 2)
            )
            # 2b) sqrt(3/8)<la||dc> *c_icld
            govvv.contract(
                "abcd,edac->eb", bvect_iajb_a, out=sigma_s, factor=sqrt(3 / 8)
            )
            govvv.contract(
                "abcd,ecad->eb", bvect_iajb_a, out=sigma_s, factor=-sqrt(3 / 8)
            )
            # 2c) -sqrt(3/8)<kl||id> *c_kald
            bvect_iajb_a.contract(
                "abcd,aced->eb", gooov, out=sigma_s, factor=-sqrt(3 / 8)
            )
            bvect_iajb_a.contract(
                "abcd,caed->eb", gooov, out=sigma_s, factor=sqrt(3 / 8)
            )
            #
            #
            #
            # 3a) sqrt(1/2)fld *c_iald
            bvect_iajb_b.contract(
                "abcd,cd->ab", fia, out=sigma_s, factor=sqrt(1 / 2)
            )
            # 3b) 1/2*sqrt(1/2)(<la|dc> + <la|cd>) *c_icld
            govvv.contract(
                "abcd,edac->eb", bvect_iajb_b, out=sigma_s, factor=sqrt(1 / 2)
            )
            # 3c) -1/2*sqrt(1/2)(<kl|id> + <kl|di>) *c_kald (lkid)
            bvect_iajb_b.contract(
                "abcd,aced->eb",
                gooov,
                out=sigma_s,
                factor=-sqrt(1 / 2),
            )
            #
            # sigma_iaj
            #
            # 1a) (<aa|ci>(iaac)c_jc +<aa|cj>c_ic (jaac)
            govvv.contract("abbc,dc->abd", b_sa, out=sigma_iaj, factor=1)
            govvv.contract("abbc,dc->dba", b_sa, out=sigma_iaj, factor=1)
            # 1b) -(<ka|ij> +<ka|ji>)c_ka (ijka/jika)
            b_sa.contract("ab,cdab->cbd", gooov, out=sigma_iaj, factor=-1)
            b_sa.contract("ab,cdab->dbc", gooov, out=sigma_iaj, factor=-1)
            #
            # sigma_iajb_a
            #
            # 2a) -sqrt(3/2) (<ab||ci>)c_jc (icba/icab)
            govvv.contract(
                "abcd,eb->adec", b_sa, out=sigma_iajb_a, factor=-sqrt(3 / 2)
            )
            govvv.contract(
                "abcd,eb->aced", b_sa, out=sigma_iajb_a, factor=sqrt(3 / 2)
            )
            # 2b) sqrt(3/2) (<ab||cj>)c_ic (jcba/jcab)
            govvv.contract(
                "abcd,eb->edac", b_sa, out=sigma_iajb_a, factor=sqrt(3 / 2)
            )
            govvv.contract(
                "abcd,eb->ecad", b_sa, out=sigma_iajb_a, factor=-sqrt(3 / 2)
            )
            # 2c) sqrt(3/2) (<ka||ij>)c_kb (ijka/jika)
            gooov.contract(
                "abcd,ce->adbe", b_sa, out=sigma_iajb_a, factor=sqrt(3 / 2)
            )
            gooov.contract(
                "abcd,ce->bdae", b_sa, out=sigma_iajb_a, factor=-sqrt(3 / 2)
            )
            # 2d) -sqrt(3/2) (<kb||ij>)c_ka (ijkb/jikb)
            gooov.contract(
                "abcd,ce->aebd", b_sa, out=sigma_iajb_a, factor=-sqrt(3 / 2)
            )
            gooov.contract(
                "abcd,ce->bead", b_sa, out=sigma_iajb_a, factor=sqrt(3 / 2)
            )
            #
            # sigma_iajb_b
            #
            # 3a) sqrt(1/2) (<ab|ci> + <ab|ic>) c_jc (icba/icab)
            govvv.contract(
                "abcd,eb->adec", b_sa, out=sigma_iajb_b, factor=sqrt(1 / 2)
            )
            govvv.contract(
                "abcd,eb->aced", b_sa, out=sigma_iajb_b, factor=sqrt(1 / 2)
            )
            # 3b) sqrt(1/2) (<ab|cj> + <ab|jc>)c_ic (jcba/jcab)
            govvv.contract(
                "abcd,eb->edac", b_sa, out=sigma_iajb_b, factor=sqrt(1 / 2)
            )
            govvv.contract(
                "abcd,eb->ecad", b_sa, out=sigma_iajb_b, factor=sqrt(1 / 2)
            )
            # 3c) -sqrt(1/2) (<ka|ij> + <ka|ji>)c_kb (ijka/jika)
            gooov.contract(
                "abcd,ce->adbe", b_sa, out=sigma_iajb_b, factor=-sqrt(1 / 2)
            )
            gooov.contract(
                "abcd,ce->bdae", b_sa, out=sigma_iajb_b, factor=-sqrt(1 / 2)
            )
            # 4d) -sqrt(1/2) (<kb|ij>+<kb|ji>)c_ka (ijkb/jikb)
            gooov.contract(
                "abcd,ce->aebd", b_sa, out=sigma_iajb_b, factor=-sqrt(1 / 2)
            )
            gooov.contract(
                "abcd,ce->bead", b_sa, out=sigma_iajb_b, factor=-sqrt(1 / 2)
            )

        sigma.iadd(sigma_s.ravel(), begin0=1, end0=end_ia)
        sigma.iadd(sigma_ia.ravel(), begin0=end_ia, end0=end_p)

        tmp = self.denself.create_four_index(nacto, nactv, nacto, nactv)
        sigma_iab.expand("abc->abac", tmp)
        sigma.iadd(
            tmp.array[CSFRCID.get_mask_csf(self, "iab")],
            begin0=end_p,
            end0=end_iab,
        )
        if nacto > 1:
            tmp = self.denself.create_four_index(nacto, nactv, nacto, nactv)
            sigma_iaj.expand("abc->abcb", tmp)
            sigma.iadd(
                tmp.array[CSFRCID.get_mask_csf(self, "iaj")],
                begin0=end_iab,
                end0=end_iaj,
            )
            sigma.iadd(
                sigma_iajb_a.array[CSFRCID.get_mask_csf(self, "iajb")],
                begin0=end_iaj,
                end0=end_iajb,
            )
            sigma.iadd(
                sigma_iajb_b.array[CSFRCID.get_mask_csf(self, "iajb")],
                begin0=end_iajb,
            )
        return sigma

    def build_subspace_hamiltonian_singles(self, bvector, hamiltonian, *args):
        """
        Constructing Hamiltonian subspace for Configuration State Function for CIS
        wavefunction

        **Arguments:**

        bvector:
            (OneIndex object) contains current approximation to CIS block
            coefficients in the CSF basis.
        """
        self.dimension = "CIS"
        sigma = self.lf.create_one_index(self.dimension)
        b_sa = self.lf.create_one_index(self.dimension)
        b_sa.assign(bvector.array[: self.dimension])
        sigma_a = CSFRCIS.build_subspace_hamiltonian(
            self, b_sa, hamiltonian, *args
        )
        sigma.assign(sigma_a.array[1:], begin0=1)
        self.dimension = "CISD"
        return sigma

    def build_subspace_hamiltonian_doubles(self, bvector, hamiltonian, *args):
        """
        Constructing Hamiltonian subspace for Configuration State Function for CID
        wavefunction

        **Arguments:**

        bvector:
            (OneIndex object) contains current approximation to CID block
            coefficients in the CSF basis.
        """
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        self.dimension = "CID"
        sigma = self.lf.create_one_index(self.dimension)
        b_d = self.lf.create_one_index(self.dimension)
        b_d.set_element(0, bvector.get_element(0))
        b_d.assign(bvector.array[nacto * nactv + 1 :], begin0=1)
        sigma = CSFRCID.build_subspace_hamiltonian(
            self, b_d, hamiltonian, *args
        )
        self.dimension = "CISD"
        return sigma
