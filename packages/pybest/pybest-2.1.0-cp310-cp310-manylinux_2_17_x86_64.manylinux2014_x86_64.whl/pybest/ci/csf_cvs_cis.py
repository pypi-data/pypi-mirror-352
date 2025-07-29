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
#
# 2025-01-26: created based on the CSFRCIS module by Iulia Emilia Brumboiu


"""
Variables used in this module:
 :ncore:     number of frozen core orbitals
 :nacto:       number of active occupied orbitals in the principal configuration
 :ncore:       number of active core orbitals used in the core-valence separation approximation
 :nactv:       number of active virtual orbitals in the principal configuration
 :nact:       total number of active orbitals (ncore+nacto+nactv)
 :e_ci:      eigenvalues of CI Hamiltonian (IOData container attribute)
 :civ:       eigevectors of CI Hamiltonian (IOData container attribute)

 Indexing convention:
  :i,j,k,..: occupied orbitals of principal configuration
  :a,b,c,..: virtual orbitals of principal configuration
"""

from math import sqrt

from pybest.log import log

from .csf_base import CSF
from .cvs_rcis import CVSRCISBase


class CSFCVSRCIS(CSF, CVSRCISBase):
    """Configuration State Function Restricted Configuration Interaction Singles (CSFRCIS) class.
    Contains all required methods to diagonalize the RCIS Hamiltonian using CSF basis.
    """

    @CSF.dimension.setter
    def dimension(self, new=None):
        nactc = self.occ_model.nactc[0]
        nactv = self.occ_model.nactv[0]
        if new is not None:
            self._dimension = self.set_dimension(new, nactc, nactv)
        else:
            log.warn(
                "The dimension may be wrong!"
                "Please set the dimension property with one of the strings (RCIS)"
            )

    def compute_h_diag(self, *args):
        """Used by the Davidson module for pre-conditioning."""
        #
        # Auxiliary objects
        #
        fock = self.from_cache("fock")
        gcvvc = self.from_cache("gcvvc")
        gcvcv = self.from_cache("gcvcv")

        nactc = self.occ_model.nactc[0]
        nactv = self.occ_model.nactv[0]
        nacto = self.occ_model.nacto[0]

        hdiag = self.lf.create_one_index(self.dimension)
        tmp = self.lf.create_two_index(nactc, nactv)

        # 1 <ia|ai>
        gcvvc.contract("abba->ab", out=tmp)

        # 2 <ia|ia>
        gcvcv.contract("abab->ab", out=tmp, factor=-2.0)

        # 3 fii
        fii = self.lf.create_one_index(nactc)
        fock.copy_diagonal(out=fii, begin=0, end=nactc)
        fii.expand("a->ab", tmp, factor=-1.0)

        # 4 faa
        start_v = nactc + nacto
        faa = self.lf.create_one_index(nactv)
        fock.copy_diagonal(out=faa, begin=start_v)
        faa.expand("b->ab", tmp, factor=1.0)

        hdiag.set_element(0, 0)
        hdiag.assign(tmp.ravel(), begin0=1)

        return hdiag

    def build_subspace_hamiltonian(self, bvector, hamiltonian, *args):
        """
        Used by the Davidson module to construct subspace Hamiltonian

        **Arguments:**

        bvector:
            (OneIndex object) contains current approximation to CI coefficients

        hamiltonian:
            (OneIndex object) used by the Davidson module and contains
            diagonal approximation to the full matrix
        """
        nactc = self.occ_model.nactc[0]
        nactv = self.occ_model.nactv[0]

        #
        # Integrals
        #
        fock = self.from_cache("fock")
        gcvvc = self.from_cache("gcvvc")
        gcvcv = self.from_cache("gcvcv")

        #
        # Ranges
        #
        cv = self.get_range("cv")
        cc = self.get_range("cc")
        vv = self.get_range("vv")
        cv2 = self.get_range("cv", start=2)

        sigma_s = self.lf.create_one_index(self.dimension)
        b_s = self.lf.create_two_index(nactc, nactv)
        sigma = self.lf.create_two_index(nactc, nactv)

        #
        # local variables
        #
        scale_factor_1 = 1.0 / sqrt(2.0)
        scale_factor_2 = 2.0 / sqrt(2.0)
        b_s.assign(bvector, begin2=1)
        c_0 = bvector.get_element(0) * scale_factor_2

        # 1) fjb * cjb
        sum0 = fock.contract("ab,ab", b_s, **cv) * 2.0 * scale_factor_1
        # 2) <aj|ib> * cjb
        gcvvc.contract("abcd,ac->db", b_s, sigma, factor=2.0)
        # 3) <aj|bi> * cjb
        gcvcv.contract("abcd,ad->cb", b_s, sigma, factor=-1.0)
        # 4) fab * cib
        fock.contract("ab,cb->ca", b_s, sigma, factor=1.0, **vv)
        # 5) fij * cja
        fock.contract("ab,bc->ac", b_s, sigma, factor=-1.0, **cc)
        # 6) fia * c0
        sigma.iadd(fock, factor=c_0, **cv2)

        sigma_s.set_element(0, sum0)
        sigma_s.assign(sigma.ravel(), begin0=1)
        return sigma_s
