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
from .spin_free_pccdcid import RpCCDCID
from .spin_free_pccdcis import RpCCDCIS


class RpCCDCISD(SpinFree):
    """Spin Free pair Coupled Cluster Doubles Configuration Interaction Singles
    and Doubles module
    """

    long_name = "Restricted pCCDCISD"
    acronym = "pCCD-CISD"
    reference = "pCCD"

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
        hdiag.assign(hdiag_s.array[1:], begin0=1, end0=nactv * nacto + 1)
        hdiag.assign(hdiag_d.array[1:], begin0=nactv * nacto + 1)
        return hdiag

    def h_diag_singles(self):
        """Calculating the guess vector for SD basis.

        hdiag:
            (OneIndex object) contains guess vector for SD basis.
        """
        self.dimension = "pCCD-CIS"
        hdiag = self.lf.create_one_index(self.dimension)
        hdiag = RpCCDCIS.compute_h_diag(self)
        self.dimension = "pCCD-CISD"
        return hdiag

    def h_diag_doubles(self):
        """Calculating the guess vector for SD basis.

        hdiag:
            (OneIndex object) contains guess vector for SD basis.
        """
        self.dimension = "pCCD-CID"
        hdiag = RpCCDCID.compute_h_diag(self)
        self.dimension = "pCCD-CISD"
        return hdiag

    def build_subspace_hamiltonian(self, bvector, hamiltonian, *args):
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
        tp = self.t_p
        fia = fock.copy(**ov)
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        end_ia = nacto * nactv + 1
        #
        # Bvectors
        #
        b_s = self.lf.create_two_index(nacto, nactv)
        b_d = self.denself.create_four_index(nacto, nactv, nacto, nactv)
        #
        # Bvectors assignment
        #
        b_s.assign(bvector, begin2=1, end2=end_ia)
        if self.pairs:
            b_d.assign_triu(bvector, begin4=end_ia, k=0)
            b_p = b_d.contract("abab->ab")
            b_d.iadd_transpose((2, 3, 0, 1))
            b_d = self.set_seniority_0(b_d, b_p)
        else:
            b_d.assign_triu(bvector, begin4=end_ia, k=1)
            b_d.iadd_transpose((2, 3, 0, 1))
        #
        # Sigma Vectors
        #
        sigma = self.lf.create_one_index(self.dimension)
        sigma_s = self.denself.create_two_index(nacto, nactv)
        sigma_d = self.denself.create_four_index(nacto, nactv, nacto, nactv)
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
        sigma.assign(singles.array[1:], begin0=1, end0=end_ia)
        sigma.assign(doubles.array[1:], begin0=end_ia)
        del singles, doubles
        self.dimension = "pCCD-CISD"

        #
        # <S|H|D>
        #
        # 1) f_kc(2 r_kcia - r_kaic)
        fia.contract("ab,abcd->cd", b_d, out=sigma_s, factor=2.0)
        b_d.contract("abcd,ad->cb", fia, out=sigma_s, factor=-1.0)
        #
        #
        # 2)  -(2<lk|ic> - <kl|ic>)r_kcla (lkic)
        gooov.contract("abcd,bdae->ce", b_d, out=sigma_s, factor=-2.0)
        gooov.contract("abcd,adbe->ce", b_d, out=sigma_s, factor=1.0)

        # 3)  (2<ka|cd> - <ka|dc>)r_kcid
        govvv.contract("abcd,aced->eb", b_d, out=sigma_s, factor=2.0)
        govvv.contract("abcd,adec->eb", b_d, out=sigma_s, factor=-1.0)

        #
        # <D|H|S>
        #
        # 1)P_iajb <ab|ic> r_jc (icab)
        govvv.contract("abcd,eb->aced", b_s, out=sigma_d, factor=1.0)
        # 2)-P_iajb <kb|ij> r_ka (ijkb)
        gooov.contract("abcd,ce->aebd", b_s, out=sigma_d, factor=-1.0)

        #
        # delta_ab
        # 3)-P_iajb fic t_iaia r_jc delta_ab
        tmp = fia.contract("ab,cb->ac", b_s)  # ij
        tmp_iaj = tmp.contract("ab,ac->acb", tp, factor=-1.0)  # iaj
        # 5)-P_iajb 2<jk|ic> - <kj|ic> t_jaja r_kc delta_ab
        tmp = gooov.contract("abcd,bd->ca", b_s, factor=2.0)  # ij
        gooov.contract("abcd,ad->cb", b_s, tmp, factor=-1.0)  # ij
        tmp.contract("ab,bc->acb", tp, tmp_iaj, factor=-1.0)  # iaj
        # 12)P_iajb <kk|jc>  t_kaka r_ic delta_ab
        tmp = gooov.contract("aabc,dc->adb", b_s)  # kij
        tmp.contract("abc,ad->bdc", tp, tmp_iaj, factor=1.0)  # iaj

        tmp_iaj.expand("abc->abcb", sigma_d)
        #
        # delta_ij
        # 4)-P_iajb fka t_iaia r_kb delta_ij
        tmp = fia.contract("ab,ac->bc", b_s)  # ab
        tmp_iab = tmp.contract("ab,ca->cab", tp, factor=-1.0)  # iab
        # 6)P_iajb 2<ka|cb> - <ka|bc> t_jbjb r_kc delta_ij
        tmp = govvv.contract("abcd,ac->bd", b_s, factor=2.0)  # ab
        govvv.contract("abcd,ad->bc", b_s, tmp, factor=-1.0)  # ab
        tmp.contract("ab,cb->cab", tp, tmp_iab)  # jab
        # 11)-P_iajb <kb|cc>  t_icic r_ka delta_ij
        tmp = govvv.contract("abcc,dc->adb", tp)  # kib
        tmp.contract("abc,ad->bdc", b_s, tmp_iab, factor=-1.0)  # iab

        tmp_iab.expand("abc->abac", sigma_d)

        # 7)P_iajb -<lj||ib>  t_jbjb r_la (jl|ib)
        tmp = gooov.contract("abcd,bd->acbd", tp, factor=-1.0)  # lijb
        gooov.contract("abcd,ad->bcad", tp, tmp)  # lijb
        tmp.contract("abcd,ae->becd", b_s, out=sigma_d)

        # 8)P_iajb <il|jb>  t_ibib r_la
        tmp = gooov.contract("abcd,ad->abcd", tp)  # iljb
        tmp.contract("abcd,be->aecd", b_s, out=sigma_d)

        # 9)P_iajb <ja||bd>  t_jbjb r_id
        tmp = govvv.contract("abcd,ed->ebac", b_s)  # iajb
        govvv.contract("abcd,ec->ebad", b_s, tmp, factor=-1.0)  # iajb
        tmp.contract("abcd,cd->abcd", tp, out=sigma_d)

        # 10)-P_iajb <jb|da>  t_jaja r_id
        tmp = govvv.contract("abcd,ec->edab", b_s)  # iajb
        tmp.contract("abcd,cb->abcd", tp, out=sigma_d, factor=-1.0)

        sigma_d.iadd_transpose((2, 3, 0, 1))
        if self.pairs:
            sigma.iadd(sigma_s.array.ravel(), begin0=1, end0=end_ia)
            sigma.iadd(sigma_d.get_triu(0), begin0=end_ia)
            return sigma

        sigma.iadd(sigma_s.array.ravel(), begin0=1, end0=end_ia)
        sigma.iadd(sigma_d.get_triu(1), begin0=end_ia)

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
        self.dimension = "pCCD-CIS"
        sigma = self.lf.create_one_index(self.dimension)
        b_sa = self.lf.create_one_index(self.dimension)
        b_sa.assign(bvector.array[: self.dimension])
        sigma = RpCCDCIS.build_subspace_hamiltonian(self, b_sa, hamiltonian)
        self.dimension = "pCCD-CISD"
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
        self.dimension = "pCCD-CID"
        sigma = self.lf.create_one_index(self.dimension)
        b_d = self.lf.create_one_index(self.dimension)
        b_d.set_element(0, bvector.get_element(0))
        b_d.assign(bvector.array[nacto * nactv + 1 :], begin0=1)
        sigma = RpCCDCID.build_subspace_hamiltonian(
            self, b_d, hamiltonian, *args
        )
        self.dimension = "pCCD-CISD"
        return sigma

    def printer(self):
        """Printing the results."""
        #
        # Local variables
        #
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        evals = self.checkpoint["e_ci"]
        evecs = self.checkpoint["civ"]
        e_ref = self.checkpoint["e_ref"]
        end_s = nacto * nactv + 1
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
            f" {'Weight(d)':>15s}"
        )
        log.hline("_")
        for ind, val in enumerate(evals):
            data = {key: [] for key in data}
            evecsj = evecs[:, ind]
            ncore = np.where(abs(evecsj) > threshold)[0]
            log(
                f"{ind:>3d} {val:> 17.6e} {e_ref + val:> 16.8f}"
                f"{np.dot(evecsj[1:end_s], evecsj[1:end_s]):> 17.6f}"
                f"{np.dot(evecsj[end_s:self.dimension], evecsj[end_s:self.dimension]):> 16.6f}"
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

            if len(data["spin_block_a"]) > 0:
                log(" ")
                log(f"{'(i->a):':>15s} {'C_ia:':>16s}")
                display(data, "a", alpha)
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
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        ncore = self.occ_model.ncore[0]
        end_s = nacto * nactv + 1
        if index < end_s:
            i, a = RpCCDCIS.get_index_s(self, index - 1)
            data["spin_block_a"].append([i + ncore + 1, a + ncore + 1 + nacto])
            data["c_a"].append(evecsj[index])

            return data
        i, a, j, b = self.get_index_d(index - end_s)
        i, a, j, b = (i + ncore, a + ncore, j + ncore, b + ncore)
        data["spin_block_ab"].append([i, a, j, b])
        data["c_ab"].append(evecsj[index])
        return data

    @staticmethod
    def setup_dict():
        """Initializes the proper dictionary to store the data for SD or CSF."""
        return {
            "spin_block_a",
            "spin_block_ab",
            "c_a",
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
