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

from pybest.ci.sd_base import SD
from pybest.ci.sd_cid import SDRCID
from pybest.ci.sd_cis import SDRCIS
from pybest.log import log

from .rcisd import RCISDBase


class SDRCISD(SD, RCISDBase):
    """Slater Determinant Restricted Configuration Interaction Singles and Doubles child class.
    Contains all required methods to diagonalize the RCISD Hamiltonian using SD basis.
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
        """Used by the davidson module for pre-conditioning.

        **Returns:**
            (OneIndex object) contains guess vector to davidson diagonalization.

        """
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        hdiag = self.lf.create_one_index(self.dimension)
        hdiag_s = self.h_diag_singles()
        hdiag_d = self.h_diag_doubles()
        hdiag.set_element(0, hdiag_s.get_element(0) + hdiag_d.get_element(0))
        hdiag.assign(hdiag_s.array[1:], begin0=1, end0=2 * nactv * nacto + 1)
        hdiag.assign(hdiag_d.array[1:], begin0=2 * nactv * nacto + 1)
        return hdiag

    def h_diag_singles(self):
        """Calculating the guess vector for SD basis.

        hdiag:
            (OneIndex object) contains guess vector for SD basis.
        """
        self.dimension = "CIS"
        hdiag = self.lf.create_one_index(2 * self.dimension - 1)
        hdiag_a = SDRCIS.compute_h_diag(self)
        hdiag.assign(hdiag_a, end0=self.dimension)
        hdiag.assign(hdiag_a.array[1:], begin0=self.dimension)
        self.dimension = "CISD"
        return hdiag

    def h_diag_doubles(self):
        """Calculating the guess vector for SD basis.

        hdiag:
            (OneIndex object) contains guess vector for SD basis.
        """
        self.dimension = "CID"
        hdiag = SDRCID.compute_h_diag(self)
        self.dimension = "CISD"
        return hdiag

    def build_subspace_hamiltonian(self, bvector, hamiltonian, *args):
        """
        Used by the davidson module to construct subspace Hamiltonian in SD basis.

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
        end_jb = end_ia + nacto * nactv
        end_ab = end_jb + nacto**2 * nactv**2
        #
        # Sigma Vectors
        #
        sigma = self.lf.create_one_index(self.dimension)
        sigma_s = self.denself.create_two_index(nacto, nactv)
        #
        # Bvectors
        #
        b_sa = self.lf.create_two_index(nacto, nactv)
        b_dab = self.denself.create_four_index(nacto, nactv, nacto, nactv)
        b_daa = self.denself.create_four_index(nacto, nactv, nacto, nactv)
        #
        # Bvectors assignment
        #
        b_sa.assign(bvector, begin2=1, end2=end_ia)
        b_dab.assign(bvector, begin4=end_jb, end4=end_ab)

        #
        # Assign Singles and Doubles block
        #
        singles = self.build_subspace_hamiltonian_singles(
            bvector.copy(begin=0, end=end_jb), hamiltonian, *args
        )
        doubles = self.build_subspace_hamiltonian_doubles(
            bvector, hamiltonian, *args
        )
        sigma.set_element(0, singles.get_element(0) + doubles.get_element(0))
        sigma.assign(singles.array[1:], begin0=1, end0=end_jb)
        sigma.assign(doubles.array[1:], begin0=end_jb)

        del singles, doubles
        self.dimension = "CISD"

        #
        # Calculating Singles-Doubles Coupling terms.
        #
        for shift in [0, end_ia - 1]:
            sigma_d = self.denself.create_four_index(
                nacto, nactv, nacto, nactv
            )
            sigma_s.clear()
            b_sa.clear()
            b_sa.assign(bvector, begin2=1 + shift, end2=end_ia + shift)

            if shift == 0:
                # 1a)
                # block alpha: f_kc r_iakc
                b_dab.contract("abcd,cd->ab", fia, out=sigma_s, factor=1.0)
                # 2a)
                # block alpha: <la|dc> r_icld
                govvv.contract("abcd,edac->eb", b_dab, out=sigma_s, factor=1.0)
                # 3a)
                # block alpha: -<kl|id> r_kald
                b_dab.contract(
                    "abcd,aced->eb", gooov, out=sigma_s, factor=-1.0
                )
                # 4a)
                # block alpha-beta: <ab|cj>r_ic (jcba,ic)
                govvv.contract("abcd,eb->edac", b_sa, out=sigma_d, factor=1.0)
                # 5)
                # block alpha-beta: -<kb|ij>r_ka
                b_sa.contract("ab,cdae->cbde", gooov, out=sigma_d, factor=-1.0)
            else:
                # 1b)
                # block beta:  f_kc r_iakc
                b_dab.contract("abcd,cd->ab", fia, out=sigma_s, factor=1.0)
                # 2b)
                # block beta:  <ka|cd> r_kcid
                govvv.contract("abcd,aced->eb", b_dab, out=sigma_s, factor=1.0)
                # 3b)
                # block beta:  -<lk|ic> r_kcla
                b_dab.contract(
                    "abcd,caeb->ed", gooov, out=sigma_s, factor=-1.0
                )
                # 4b)
                # block alpha-beta: <ab|ic>r_jc (icab)
                govvv.contract("abcd,eb->aced", b_sa, out=sigma_d, factor=1.0)
                # 5b)
                # block alpha-beta: -<ka|ji>r_kb
                b_sa.contract("ab,cdae->decb", gooov, out=sigma_d, factor=-1.0)

            sigma.iadd(sigma_s.ravel(), begin0=1 + shift, end0=end_ia + shift)
            sigma.iadd(sigma_d.array.ravel(), begin0=end_jb, end0=end_ab)

        if nacto > 1:
            end_aa = end_ab + nacto * (nacto - 1) * nactv * (nactv - 1) // 4
            for shift, shift2 in zip([0, end_aa - end_ab], [0, end_ia - 1]):
                b_sa.clear()
                sigma_d.clear()
                sigma_s.clear()
                b_daa.clear()
                #
                # Bvectors assignment
                #
                b_sa.assign(bvector, begin2=1 + shift2, end2=end_ia + shift2)
                b_daa.assign(
                    bvector,
                    ind=self.get_index_of_mask(),
                    begin4=end_ab + shift,
                    end4=end_aa + shift,
                )
                tmp = b_daa.copy()
                b_daa.iadd_transpose((2, 1, 0, 3), other=tmp, factor=-1.0)
                b_daa.iadd_transpose((0, 3, 2, 1), other=tmp, factor=-1.0)
                b_daa.iadd_transpose((2, 3, 0, 1), other=tmp, factor=1.0)
                del tmp

                # 1) 1/2f_kc r_iakc
                # block alpha/beta:
                b_daa.contract("abcd,cd->ab", fia, out=sigma_s, factor=0.5)
                # 2) 1/2<la|dc> r_icld
                # block alpha/beta:
                govvv.contract("abcd,edac->eb", b_daa, out=sigma_s, factor=0.5)
                # 3) -1/2<la|cd> r_icld
                # block alpha/beta:
                govvv.contract(
                    "abcd,ecad->eb", b_daa, out=sigma_s, factor=-0.5
                )
                # 4) -1/2<kl|id> r_kald
                # block alpha/beta:
                b_daa.contract(
                    "abcd,aced->eb", gooov, out=sigma_s, factor=-0.5
                )
                # 5) 1/2<lk|id> r_kald
                # block alpha/beta:
                b_daa.contract("abcd,caed->eb", gooov, out=sigma_s, factor=0.5)

                # 6) <ab||cj> r_ic
                # block alpha-alpha/beta-beta:
                govvv.contract("abcd,eb->edac", b_sa, out=sigma_d, factor=1.0)
                govvv.contract("abcd,eb->ecad", b_sa, out=sigma_d, factor=-1.0)
                # 6) -<ab||ci> r_jc
                # block alpha-alpha/beta-beta:
                govvv.contract("abcd,eb->adec", b_sa, out=sigma_d, factor=-1.0)
                govvv.contract("abcd,eb->aced", b_sa, out=sigma_d, factor=1.0)
                # 7) <ka||ij> r_kb
                # block alpha-alpha/beta-beta:
                b_sa.contract("ab,cdae->cedb", gooov, out=sigma_d, factor=1.0)
                b_sa.contract("ab,cdae->decb", gooov, out=sigma_d, factor=-1.0)
                # 8) -<kb||ij> r_ka
                # block alpha-alpha/beta-beta:
                b_sa.contract("ab,cdae->cbde", gooov, out=sigma_d, factor=-1.0)
                b_sa.contract("ab,cdae->dbce", gooov, out=sigma_d, factor=1.0)

                sigma.iadd(
                    sigma_s.ravel(), begin0=1 + shift2, end0=end_ia + shift2
                )
                sigma.iadd(
                    sigma_d.array[self.get_mask()],
                    begin0=end_ab + shift,
                    end0=end_aa + shift,
                    factor=1.0,
                )
        return sigma

    def build_subspace_hamiltonian_singles(self, bvector, hamiltonian):
        """
        Constructing Hamiltonian subspace for Slater Determinant basis for CIS
        wavefunction

        **Arguments:**

        bvector:
            (OneIndex object) contains current approximation to CIS block
            coefficients in the SD basis.
        """
        self.dimension = "CIS"
        sigma = self.lf.create_one_index(2 * self.dimension - 1)
        b_sa = self.lf.create_one_index(self.dimension)
        b_sa.assign(bvector.array[: self.dimension])
        sigma_a = SDRCIS.build_subspace_hamiltonian(self, b_sa, hamiltonian)
        sigma.assign(sigma_a, end0=self.dimension)
        b_sa.clear()
        b_sa.set_element(0, bvector.get_element(0))
        b_sa.assign(bvector.array[self.dimension :], begin0=1)
        b_sa.assign(bvector.array[self.dimension :], begin0=1)
        sigma_a = SDRCIS.build_subspace_hamiltonian(self, b_sa, hamiltonian)
        sigma.assign(sigma_a.array[1:], begin0=self.dimension)
        self.dimension = "CISD"
        return sigma

    def build_subspace_hamiltonian_doubles(self, bvector, hamiltonian, *args):
        """
        Constructing Hamiltonian subspace for Slater Determinant basis for CID
        wavefunction

        **Arguments:**

        bvector:
            (OneIndex object) contains current approximation to CID block
            coefficients in the SD basis.
        """
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        self.dimension = "CID"
        sigma = self.lf.create_one_index(self.dimension)
        b_d = self.lf.create_one_index(self.dimension)
        b_d.set_element(0, bvector.get_element(0))
        b_d.assign(bvector.array[2 * nacto * nactv + 1 :], begin0=1)
        sigma = SDRCID.build_subspace_hamiltonian(
            self, b_d, hamiltonian, *args
        )
        self.dimension = "CISD"
        return sigma
