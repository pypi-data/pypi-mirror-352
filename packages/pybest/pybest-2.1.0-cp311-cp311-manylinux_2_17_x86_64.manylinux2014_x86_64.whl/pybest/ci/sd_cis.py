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
 :nacto:     number of active occupied orbitals in the principal configuration
 :nvirt:     number of virtual orbitals in the principal configuration
 :nactv:     number of active virtual orbitals in the principal configuration
 :nact:      total number of active orbitals (nacto+nactv)
 :e_ci:      eigenvalues of CI Hamiltonian (IOData container attribute)
 :civ:       eigenvectors of CI Hamiltonian (IOData container attribute)

 Indexing convention:
  :i,j,k,..: occupied orbitals of principal configuration
  :a,b,c,..: virtual orbitals of principal configuration
"""

from __future__ import annotations

from typing import Any

from pybest.linalg import OneIndex
from pybest.log import log

from .rcis import RCISBase
from .sd_base import SD


class SDRCIS(SD, RCISBase):
    """Slater Determinant Restricted Configuration Interaction Singles child class.
    Contains all required methods to diagonalize the RCIS Hamiltonian using SD basis.
    """

    @SD.dimension.setter
    def dimension(self, new: str | None = None) -> None:
        """Set total number of unknowns in CI model

        Args:
            new (str | None, optional): A CI flavor (CIS, CID, CISD). Defaults to None.
        """
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        if new is not None:
            self._dimension = self.set_dimension(new, nacto, nactv)
        else:
            log.warn(
                "The dimension may be wrong!"
                "Please set the dimension property with RCIS"
            )

    def compute_h_diag(self, *args: Any) -> OneIndex:
        """Used by the davidson module for pre-conditioning."""
        #
        # Auxiliary objects
        #
        fock = self.from_cache("fock")
        govvo = self.from_cache("govvo")
        govov = self.from_cache("govov")
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]

        hdiag = self.lf.create_one_index(self.dimension)
        tmp = self.lf.create_two_index(nacto, nactv)

        # 1 <ia|ai>
        govvo.contract("abba->ab", out=tmp, factor=1.0)

        # 2 <ia|ia>
        govov.contract("abab->ab", out=tmp, factor=-2.0)

        # 3 fii
        fii = self.lf.create_one_index(nacto)
        fock.copy_diagonal(out=fii, end=nacto)
        fii.expand("a->ab", tmp, factor=-1.0)

        # 4 faa
        faa = self.lf.create_one_index(nactv)
        fock.copy_diagonal(out=faa, begin=nacto)
        faa.expand("b->ab", tmp, factor=1.0)

        hdiag.set_element(0, 0)
        hdiag.assign(tmp.ravel(), begin0=1)

        return hdiag

    def build_subspace_hamiltonian(
        self, bvector: OneIndex, hamiltonian: OneIndex, *args: Any
    ) -> OneIndex:
        """Construct subspace Hamiltonian used by the Davidson module.

        Args:
            bvector (OneIndex): contains current approximation to CI coefficients
            hamiltonian (OneIndex): contains diagonal approximation to the full matrix

        Returns:
            OneIndex: the current approximation to the sigma vector
        """
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        #
        # Integrals
        #
        fock = self.from_cache("fock")
        govvo = self.from_cache("govvo")
        govov = self.from_cache("govov")

        #
        # Ranges
        #
        ov = self.get_range("ov")
        oo = self.get_range("oo")
        vv = self.get_range("vv")
        ov2 = self.get_range("ov", start=2)

        sigma_s = self.lf.create_one_index(self.dimension)
        b_s = self.lf.create_two_index(nacto, nactv)
        sigma = self.lf.create_two_index(nacto, nactv)

        #
        # local variables
        #
        b_s.assign(bvector, begin2=1)
        c_0 = bvector.get_element(0)

        # 1) fjb * cjb
        sum0 = fock.contract("ab,ab", b_s, **ov) * 2.0
        # 2) <aj|ib> * cjb
        govvo.contract("abcd,ac->db", b_s, sigma, factor=2.0)
        # 3) <aj|bi> * cjb
        govov.contract("abcd,ad->cb", b_s, sigma, factor=-1.0)
        # 4) fab * cib
        fock.contract("ab,cb->ca", b_s, sigma, factor=1.0, **vv)
        # 5) fij * cja
        fock.contract("ab,bc->ac", b_s, sigma, factor=-1.0, **oo)
        # 6) fia * c0
        sigma.iadd(fock, factor=c_0, **ov2)

        sigma_s.set_element(0, sum0)
        sigma_s.assign(sigma.ravel(), begin0=1)
        return sigma_s
