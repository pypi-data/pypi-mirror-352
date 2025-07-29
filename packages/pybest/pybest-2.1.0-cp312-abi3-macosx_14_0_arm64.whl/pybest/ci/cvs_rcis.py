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
# 2025-01-26: created based on the RCIS module by Iulia Emilia Brumboiu


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

from functools import partial
from math import sqrt

import numpy as np

from pybest.auxmat import get_fock_matrix
from pybest.linalg import CholeskyFourIndex
from pybest.log import log

from .rci_base import RCI
from .rci_utils import display, display_csf


class CVSRCISBase(RCI):
    """Restricted Configuration Interaction Singles module
    for Slater Determinant (SD) and Configuration State Function (CSF) basis.
    """

    long_name = "Restricted Configuration Interaction Singles"
    acronym = "CIS"
    reference = "any single-reference wavefunction"
    cvs = True

    def __init__(self, lf, occ_model):
        super().__init__(lf, occ_model)
        self.dimension = self.acronym
        # Flag for using the CVS approximation

    @RCI.dimension.setter
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

    @RCI.nroot.setter
    def nroot(self, new):
        self._nroot = new + 1

    @RCI.size_consistency_correction.setter
    def size_consistency_correction(self, new):
        self._size_consistency_correction = False

    @RCI.threshold_c_0.setter
    def threshold_c_0(self, new):
        self._threshold_c_0 = False

    def calculate_exact_hamiltonian(self):
        """Calculate exact Hamiltonian of the CIS model."""
        #
        # Auxiliary objects
        #
        fock = self.from_cache("fock")
        gcvvc = self.from_cache("gcvvc")
        gcvcv = self.from_cache("gcvcv")

        #
        # Hamiltonian
        #
        hamiltonian = self.lf.create_two_index(self.dimension, self.dimension)

        #
        # Scale matrix elements if CSF are used
        #
        scale_factor_1 = 1.0
        scale_factor_2 = 1.0
        if self.csf:
            scale_factor_1 = 1.0 / sqrt(2.0)
            scale_factor_2 = 2.0 / sqrt(2.0)

        nactc = self.occ_model.nactc[0]
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]

        start_v = nactc + nacto

        for i in range(nactc):
            for a in range(nactv):
                i_a = i * nactv + a
                hamiltonian.set_element(
                    0,
                    i_a + 1,
                    fock.get_element(i, a + start_v) * 2.0 * scale_factor_1,
                    symmetry=1,
                )
                hamiltonian.set_element(
                    i_a + 1,
                    0,
                    fock.get_element(i, a + start_v) * scale_factor_2,
                    symmetry=1,
                )
                for j in range(nactc):
                    for b in range(nactv):
                        tmp = 0.0
                        j_b = j * nactv + b
                        if a == b:
                            tmp -= fock.get_element(i, j)
                        if i == j:
                            tmp += fock.get_element(a + start_v, b + start_v)
                        tmp += 2 * gcvvc.get_element(j, a, b, i)
                        tmp -= gcvcv.get_element(j, a, i, b)
                        hamiltonian.set_element(
                            i_a + 1, j_b + 1, tmp, symmetry=1
                        )
        return hamiltonian

    def set_hamiltonian(self, mo1, mo2):
        """Compute auxiliary matrices.

        **Arguments:**

        mo1, mo2
            One- and two-electron integrals (some Hamiltonian matrix
            elements) in the MO basis.
        """
        self.clear_cache()

        # 1) Fock matrix: fpq
        nact = self.occ_model.nact[0]
        nactc = self.occ_model.nactc[0]
        nacto = self.occ_model.nacto[0]

        fock = self.init_cache("fock", nact, nact)
        get_fock_matrix(fock, mo1, mo2, nactc + nacto)

        #
        # 4-Index slices of ERI
        #
        def alloc(arr, block):
            """Determines alloc keyword argument for init_cache method."""
            # We keep one whole CholeskyFourIndex to rule them all.
            # Non-redundant blocks are accessed as views.
            if isinstance(arr, CholeskyFourIndex):
                return (partial(arr.view, **self.get_range(block)),)
            # But we store only non-redundant blocks of DenseFourIndex
            return (partial(arr.copy, **self.get_range(block)),)

        #
        # Get blocks
        #
        slices = ["cvcv", "cvvc"]
        for slice_ in slices:
            self.init_cache(f"g{slice_}", alloc=alloc(mo2, slice_))

    def setup_dict(self):
        """Initializes the proper dictionary to store the data for SD or CSF."""
        if self.print_csf:
            return {
                "spin_block_1",
                "c_1",
            }
        return {
            "spin_block_a",
            "spin_block_b",
            "c_a",
            "c_b",
        }

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
            nactc = np.where(abs(evecsj) > threshold)[0]
            log(
                f"{ind:>3d} {val:> 16.6e} {e_ref + val:> 17.8f}"
                f"{np.dot(evecsj[1:], evecsj[1:]):> 17.6f}"
            )
            log(" ")
            for ind2 in nactc:
                if ind2 == 0:
                    log(f"{'Reference state   C_0:':>30s}")
                    log(f"{evecsj[ind2]:> 34.5f}")
                else:
                    self.collect_data(ind2, data, evecsj)

            if self.print_csf:
                if len(data["spin_block_1"]) > 0:
                    log(" ")
                    log(f"{'(i->a):':>15s} {'C_ia:':>16s}")
                display_csf(data, "1", self.acronym)
            else:
                if len(data["spin_block_a"]) > 0:
                    log(" ")
                    log(f"{'(i->a):':>15s} {'C_ia:':>16s}")
                display(data, "a", alpha)
                display(data, "b", beta)

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
        ncore = self.occ_model.ncore[0]
        nactc = self.occ_model.nactc[0]
        nacto = self.occ_model.nacto[0]
        if (self.csf and self.print_csf) or (not self.csf and self.print_csf):
            if abs(evecsj[index]) > self.threshold:
                i, a = self.get_index_s(index - 1)
                data["spin_block_1"].append(
                    [
                        i + ncore + 1,
                        a + ncore + 1 + nactc + nacto,
                    ]
                )
                data["c_1"].append(evecsj[index])

        if self.csf and not self.print_csf:
            if abs(evecsj[index] / sqrt(2)) > self.threshold:
                i, a = self.get_index_s(index - 1)
                data["spin_block_a"].append(
                    [
                        i + ncore + 1,
                        a + ncore + 1 + nactc + nacto,
                    ]
                )
                data["c_a"].append(evecsj[index] / sqrt(2))
                data["spin_block_b"].append(
                    [
                        i + ncore + 1,
                        a + ncore + 1 + nactc + nacto,
                    ]
                )
                data["c_b"].append(evecsj[index] / sqrt(2))

        if not self.csf and not self.print_csf:
            if abs(evecsj[index] / sqrt(2)) > self.threshold:
                i, a = self.get_index_s(index - 1)
                data["spin_block_a"].append(
                    [
                        i + ncore + 1,
                        a + ncore + 1 + nactc + nacto,
                    ]
                )
                data["c_a"].append(evecsj[index] / sqrt(2))
                data["spin_block_b"].append(
                    [
                        i + ncore + 1,
                        a + ncore + 1 + nactc + nacto,
                    ]
                )
                data["c_b"].append(evecsj[index] / sqrt(2))

        return data

    def get_index_s(self, index):
        """Get index for single excitation."""
        nactc = self.occ_model.nactc[0]
        nactv = self.occ_model.nactv[0]
        b = index % nactv
        j = ((index - b) / nactv) % nactc
        return int(j), int(b)
