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


class RpCCDCIS(SpinFree):
    """Spin-Free pair Coupled Cluster Doubles Configuration Interaction Singles module"""

    long_name = "Spin-Free pair Coupled Cluster Doubles Configuration Interaction Singles module"
    acronym = "pCCD-CIS"
    reference = "pCCD"

    def compute_h_diag(self, *arg):
        """Used by davidson module for pre-conditioning."""
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
        govvo.contract("abba->ab", tmp, factor=1.0, clear=False)

        # 2 <ia|ia>
        govov.contract("abab->ab", tmp, factor=-2.0, clear=False)

        # 3 fii
        fii = self.lf.create_one_index(nacto)
        fock.copy_diagonal(out=fii, begin=0, end=nacto)
        fii.expand("a->ab", tmp, factor=-1.0)

        # 4 faa
        faa = self.lf.create_one_index(nactv)
        fock.copy_diagonal(out=faa, begin=nacto, end=nacto + nactv)
        faa.expand("b->ab", tmp, factor=1.0)

        hdiag.set_element(0, 0)
        hdiag.assign(tmp.ravel(), begin0=1)
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
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        tp = self.t_p
        #
        # Integrals
        #
        fock = self.from_cache("fock")
        govvo = self.from_cache("govvo")
        govov = self.from_cache("govov")

        gooov = self.from_cache("gooov")
        govvv = self.from_cache("govvv")

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
        # 7) 2<il|ad>t_iaia c_ld-> idal
        tmp = govvo.contract("abcd,db->ac", b_s)
        tmp.contract("ab,ab->ab", tp, sigma, factor=2.0)
        # 8) -<il|da>t_iaia c_ld-> iadl
        tmp = govvo.contract("abcd,dc->ab", b_s)
        tmp.contract("ab,ab->ab", tp, sigma, factor=-1.0)
        # 9) -<il|cc>t_icic c_la-> iccl
        tmp = govvo.contract("abbc,ab->ac", tp)
        tmp.contract("ab,bc->ac", b_s, out=sigma, factor=-1.0)
        # 10) -<kk|ac>t_kaka c_ic-> kcak
        tmp = govvo.contract("abca,ac->bc", tp)
        tmp.contract("ab,ca->cb", b_s, out=sigma, factor=-1.0)
        # 11) f_ia t_iaia * c0
        fock.contract("ab,ab->ab", tp, out=sigma, factor=c_0, **ov)
        # 12) <ai|cc>t_icic *c0 (iacc)
        govvv.contract("abcc,ac->ab", tp, out=sigma, factor=c_0)
        # 13) <kk|ia>t_kaka *c0
        gooov.contract("aabc,ac->bc", tp, out=sigma, factor=-c_0)

        sigma_s.set_element(0, (sum0))
        sigma_s.assign(sigma.ravel(), begin0=1)
        return sigma_s

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
                    log(f"{'Reference state   C_0:':>30s}")
                    log(f"{evecsj[ind2]:> 34.5f}")
                else:
                    self.collect_data(ind2, data, evecsj)
            if len(data["spin_block_a"]) > 0:
                log(" ")
                log(f"{'(i->a):':>15s} {'C_ia:':>16s}")

            display(data, "a", alpha)
            log.hline("-")
            log.hline("*")

    def collect_data(self, index, data, evecsj):
        """Collect the data and prepare them for printing:

        **Arguments:**

        *index:
            (int) Number indicating the SD contribution in the CI solution.

        *data:
            (dictionary) Contains two types of data:
            indices (spin_block_a) of the proper SD spin block contributions
            and the corresponding coefficients (c_a).

        *evecsj:
            Eigenvectors of CI Hamiltonian (without the reference
            state contribution).
        """
        nacto = self.occ_model.nacto[0]
        i, a = self.get_index_s(index - 1)
        data["spin_block_a"].append(
            [i + self.ncore + 1, a + self.ncore + 1 + nacto]
        )
        data["c_a"].append(evecsj[index])

        return data

    @staticmethod
    def setup_dict():
        """Initializes the proper dictionary to store the data."""
        return {
            "spin_block_a",
            "c_a",
        }
