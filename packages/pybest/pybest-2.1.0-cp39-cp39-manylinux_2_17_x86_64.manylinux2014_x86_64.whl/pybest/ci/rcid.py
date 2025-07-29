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

from functools import partial
from math import sqrt

import numpy as np

from pybest.auxmat import get_fock_matrix
from pybest.exceptions import ArgumentError
from pybest.linalg import CholeskyFourIndex
from pybest.log import log
from pybest.utility import check_options

from .rci_base import RCI
from .rci_utils import display, display_csf


class RCIDBase(RCI):
    """Restricted Configuration Interaction Doubles module
    for Slater Determinant (SD) and Configuration State Function (CSF) basis.
    """

    long_name = "Restricted Configuration Interaction Doubles"
    acronym = "CID"
    reference = "any single-reference wavefunction"
    cvs = False

    def __init__(self, lf, occ_model):
        super().__init__(lf, occ_model)
        self.dimension = self.acronym

    @RCI.dimension.setter
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

    @RCI.nroot.setter
    def nroot(self, new):
        self._nroot = new

    @RCI.davidson.setter
    def davidson(self, new):
        if not isinstance(new, bool):
            raise ArgumentError(
                "Unkown type for keyword davidson. Boolean type required."
            )
        self._davidson = new

    def set_hamiltonian(self, mo1, mo2):
        """Compute auxiliary matrices.

        **Arguments:**

        mo1, mo2
            One- and two-electron integrals (some Hamiltonian matrix
            elements) in the MO basis.
        """
        self.clear_cache()
        nacto = self.occ_model.nacto[0]
        nact = self.occ_model.nact[0]

        # 1) Fock matrix: fpq
        fock = self.init_cache("fock", nact, nact)
        get_fock_matrix(fock, mo1, mo2, nacto)

        # 2) temporary matrix: gppqq
        gppqq = self.init_cache("gppqq", nact, nact)
        mo2.contract("aabb->ab", out=gppqq)

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
        slices = ["ovvo", "ovov", "oooo", "vvvv"]
        for slice_ in slices:
            self.init_cache(f"g{slice_}", alloc=alloc(mo2, slice_))

    def setup_dict(self):
        """Initializes the proper dictionary to store the data for SD or CSF."""
        if self.print_csf:
            return {
                "spin_block_1",
                "spin_block_2",
                "spin_block_3",
                "spin_block_4",
                "spin_block_5",
                "c_1",
                "c_2",
                "c_3",
                "c_4",
                "c_5",
            }
        return {
            "spin_block_aa",
            "spin_block_bb",
            "spin_block_ab",
            "c_ab",
            "c_aa",
            "c_bb",
        }

    def check_index(self, ind2, unique, data, evecsj):
        """Selects the indices and leads to collect the proper data results."""
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]

        shift = nacto * (nacto - 1) // 2 * nactv * (nactv - 1) // 2
        end_1 = nacto * nactv + 1
        end_2 = end_1 + nacto * (nactv * (nactv - 1)) // 2
        end_3 = end_2 + nacto * (nacto - 1) // 2 * nactv

        if (ind2 in unique) or ((ind2 - shift) in unique):
            pass
        else:
            self.collect_data(ind2, data, evecsj)
            if ind2 > end_3:
                unique.append(ind2)

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
            f" {'Weight(d)':>15s}"
        )
        log.hline("_")
        for ind, val in enumerate(evals):
            unique = []
            data = {key: [] for key in data}
            evecsj = evecs[:, ind]
            ncore = np.where(abs(evecsj) > threshold)[0]
            log(
                f"{ind:>3d} {val:> 17.6e} {e_ref + val:> 16.8f}"
                f"{np.dot(evecsj[1:], evecsj[1:]):> 17.6f}"
            )
            log(" ")
            for ind2 in ncore:
                if ind2 == 0:
                    if self.size_consistency_correction:
                        self.rci_corrections.printer()
                    log(f"{'Reference state    C_0:':>31s}")
                    log(f"{evecsj[ind2]:> 34.5f}")
                else:
                    if self.csf:
                        self.check_index(ind2, unique, data, evecsj)
                    else:
                        self.collect_data(ind2, data, evecsj)

            if self.print_csf:
                for index in range(1, len(data) // 2 + 1):
                    if len(data["spin_block_" + f"{index}"]) > 0:
                        log(" ")
                        if index == 1:
                            log(f"{'(i->a   i->a):':>22s} {'C_iaia:':>11s}")
                            display_csf(data, "1", self.acronym)
                        if index == 2:
                            log(f"{'(i->a   i->b):':>22s} {'C_iaib:':>11s}")
                            display_csf(data, "2", self.acronym)
                        if index == 3:
                            log(f"{'(i->a   j->a):':>22s} {'C_iaja:':>11s}")
                            display_csf(data, "3", self.acronym)
                        if index == 4:
                            log(f"{'(i->a   j->b):':>22s} {'C_iajb_A:':>13s}")
                            display_csf(data, "4", self.acronym)
                        if index == 5:
                            log(f"{'(i->a   j->b):':>22s} {'C_iajb_B:':>13s}")
                            display_csf(data, "5", self.acronym)
            else:
                if (
                    len(data["spin_block_aa"]) > 0
                    or len(data["spin_block_ab"]) > 0
                ):
                    log(" ")
                    log(f"{'(i->a   j->b):':>22s} {'C_iajb:':>11s}")
                display(data, "ab", alpha, beta)
                display(data, "aa", alpha, alpha)
                display(data, "bb", beta, beta)

            log.hline("-")
            log.hline("*")

    def collect_data(self, index, data, evecsj):
        """Collect data and prepare for printing:

        **Arguments:**

        *index:
            (int) Number indicating the SD contribution in the CI solution.

        *data:
            (dictionary) Contains two types of data:
            indices (spin_block_[aa, bb or ab]) of the proper SD spin block
            contributions and the corresponding coefficients (c_[aa, bb or ab]).

        *evecsj:
            Eigenvectors of CI Hamiltonian (without the reference
            state contribution).
        """
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        ncore = self.occ_model.ncore[0]
        shift = nacto * (nacto - 1) // 2 * nactv * (nactv - 1) // 2
        end_1 = nacto * nactv + 1
        end_2 = end_1 + nacto * (nactv * (nactv - 1)) // 2
        end_3 = end_2 + nacto * (nacto - 1) // 2 * nactv
        end_4 = end_3 + shift

        i, a, j, b = self.get_index_d(index - 1)
        i, a, j, b = (i + ncore, a + ncore, j + ncore, b + ncore)
        if self.csf and self.print_csf:
            if 0 < index < end_1:
                data["spin_block_1"].append([i, a, j, b])
                data["c_1"].append(evecsj[index])
            elif index < end_2:
                data["spin_block_2"].append([i, a, j, b])
                data["c_2"].append(evecsj[index])
            elif index < end_3:
                data["spin_block_3"].append([i, a, j, b])
                data["c_3"].append(evecsj[index])
            elif index < end_4:
                data["spin_block_4"].append([i, a, j, b])
                data["c_4"].append(evecsj[index])
            else:
                data["spin_block_5"].append([i, a, j, b])
                data["c_5"].append(evecsj[index])

        if not self.csf and not self.print_csf:
            end_ab = nacto * nacto * nactv * nactv
            end_aa = end_ab + ((nacto * (nacto - 1)) // 2) * (
                (nactv * (nactv - 1)) // 2
            )
            if index < end_ab:
                data["spin_block_ab"].append([i, a, j, b])
                data["c_ab"].append(evecsj[index])
            elif index < end_aa:
                data["spin_block_aa"].append([i, a, j, b])
                data["c_aa"].append(evecsj[index])
            else:
                data["spin_block_bb"].append([i, a, j, b])
                data["c_bb"].append(evecsj[index])

        if self.csf and not self.print_csf:
            return self.transform_from_csf_to_sd(index, data, evecsj)

        if not self.csf and self.print_csf:
            raise NotImplementedError

        return data

    def transform_from_sd_to_csf(self, index, data, evecsj):
        """Transforms the results from Slater Determinant basis to Configuration State Function."""
        raise NotImplementedError

    def transform_from_csf_to_sd(self, index, data, evecsj):
        """Transforms the results from Configuration State Function basis to Slater Determinant."""
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        ncore = self.occ_model.ncore[0]
        shift = nacto * (nacto - 1) // 2 * nactv * (nactv - 1) // 2
        end_1 = nacto * nactv + 1
        end_2 = end_1 + nacto * (nactv * (nactv - 1)) // 2
        end_3 = end_2 + nacto * (nacto - 1) // 2 * nactv
        end_4 = end_3 + shift

        i, a, j, b = self.get_index_d(index - 1)
        i, a, j, b = (i + ncore, a + ncore, j + ncore, b + ncore)

        if 0 < index < end_1:
            data["spin_block_ab"].append([i, a, j, b])
            data["c_ab"].append(evecsj[index])
        elif index < end_2:
            if abs(evecsj[index] / sqrt(2)) > self.threshold:
                data["spin_block_ab"].append([i, a, j, b])
                data["c_ab"].append(evecsj[index] / sqrt(2))
                data["spin_block_ab"].append([i, b, j, a])
                data["c_ab"].append(evecsj[index] / sqrt(2))
        elif index < end_3:
            if abs(evecsj[index] / sqrt(2)) > self.threshold:
                data["spin_block_ab"].append([i, a, j, b])
                data["c_ab"].append(evecsj[index] / sqrt(2))
                data["spin_block_ab"].append([j, a, i, b])
                data["c_ab"].append(evecsj[index] / sqrt(2))
        elif index < end_4:
            if abs(evecsj[index] / sqrt(3)) > self.threshold:
                data["spin_block_aa"].append([i, a, j, b])
                data["c_aa"].append(evecsj[index] / sqrt(3))
                data["spin_block_bb"].append([i, a, j, b])
                data["c_bb"].append(evecsj[index] / sqrt(3))
            Cx = (
                (evecsj[index] * sqrt(12) - 4 * evecsj[index] / sqrt(3)) / 2
                + evecsj[index + shift]
            ) / 2
            Cy = evecsj[index + shift] - Cx
            if abs(Cx) > self.threshold:
                data["spin_block_ab"].append([i, a, j, b])
                data["c_ab"].append(Cx)
                data["spin_block_ab"].append([j, b, i, a])
                data["c_ab"].append(Cx)
            if abs(Cy) > self.threshold:
                data["spin_block_ab"].append([j, a, i, b])
                data["c_ab"].append(Cy)
                data["spin_block_ab"].append([i, b, j, a])
                data["c_ab"].append(Cy)
        else:
            Cx = (
                (
                    evecsj[index - shift] * sqrt(12)
                    - 4 * evecsj[index - shift] / sqrt(3)
                )
                / 2
                + evecsj[index]
            ) / 2
            Cy = evecsj[index] - Cx
            if abs(Cx) > self.threshold:
                data["spin_block_ab"].append([i, a, j, b])
                data["c_ab"].append(Cx)
                data["spin_block_ab"].append([j, b, i, a])
                data["c_ab"].append(Cx)
            if abs(Cy) > self.threshold:
                data["spin_block_ab"].append([j, a, i, b])
                data["c_ab"].append(Cy)
                data["spin_block_ab"].append([i, b, j, a])
                data["c_ab"].append(Cy)

        return data

    def get_index_d(self, index):
        """Get the unique indices of some doubly excited CSF. Returns the set of
        active orbital indices without adding shift related to the frozen core
        orbitals.

        **Arguments:**

        *index:
            (int) The number that indicates doubly excited CSF which
            is contributing in the CI solution.
        """
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        if self.csf:
            end_1 = nacto * nactv
            end_2 = end_1 + nacto * (nactv * (nactv - 1)) // 2
            end_3 = end_2 + nacto * (nacto - 1) // 2 * nactv
            end_4 = end_3 + (
                nacto * (nacto - 1) // 2 * nactv * (nactv - 1) // 2
            )
            if index < end_1:
                i = index // (nactv) + 1
                j = i
                a = index % nactv + nacto + 1
                b = a
                return i, a, j, b
            if index < end_2:
                index = index - end_1
                indices = np.where(self.get_mask("iab"))

            elif index < end_3:
                index = index - end_2
                indices = np.where(self.get_mask("iaj"))

            elif index < end_4:
                index = index - end_3
                indices = np.where(self.get_mask("iajb"))
            else:
                index = index - end_4
                indices = np.where(self.get_mask("iajb"))

            i, a, j, b = (
                indices[0][index],
                indices[1][index],
                indices[2][index],
                indices[3][index],
            )
            return (
                i + 1,
                a + 1 + nacto,
                j + 1,
                b + 1 + nacto,
            )
        # Case 1) C_iaJB:
        end_ab = nacto * nacto * nactv * nactv
        # Case 2) C_iajb:
        end_aa = ((nacto * (nacto - 1)) // 2) * ((nactv * (nactv - 1)) // 2)
        if index < end_ab:
            (i, a, j, b) = np.unravel_index(
                index, (nacto, nactv, nacto, nactv)
            )
            i, a, j, b = (
                i + 1,
                a + 1 + nacto,
                j + 1,
                b + 1 + nacto,
            )
            return i, a, j, b
        index = index - end_ab
        if index > end_aa:
            index = index - end_aa
        ind = np.where(self.get_mask("iajb"))
        i, a, j, b = (
            ind[0][index],
            ind[1][index],
            ind[2][index],
            ind[3][index],
        )
        return (
            i + 1,
            a + 1 + nacto,
            j + 1,
            b + 1 + nacto,
        )

    def get_index_of_mask(self, select):
        """Get the indices where the True values are assigned."""
        mask = self.get_mask(select)
        indices = np.where(mask)
        return indices

    def get_mask(self, select):
        """The function returns a 4-dimensional boolean np.array. True values
        are assigned to all nacton-redundant and symmetry-unique elements of the
        CI coefficient tensor for double excitations.
        """
        check_options(
            "select",
            select,
            "iab",
            "iaj",
            "iajb",
        )

        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        mask = np.zeros((nacto, nactv, nacto, nactv), dtype=bool)

        if select in ["iab"]:
            indices_o = np.triu_indices(nacto, 0)
            indices_v = np.triu_indices(nactv, 1)

            # TODO: Check if this is correct, iterates over i,j but sets only based on i
            for i, j in zip(indices_o[0], indices_o[1]):  # noqa: B007
                mask[i, indices_v[0], i, indices_v[1]] = True

        elif select in ["iaj"]:
            indices_o = np.triu_indices(nacto, 1)
            indices_v = np.triu_indices(nactv, 0)

            for a in indices_v[0]:
                mask[indices_o[0], a, indices_o[1], a] = True

        else:
            indices_o = np.triu_indices(nacto, 1)
            indices_v = np.triu_indices(nactv, 1)
            for i, j in zip(indices_o[0], indices_o[1]):
                mask[i, indices_v[0], j, indices_v[1]] = True

        return mask

    def calculate_exact_hamiltonian(self):
        """Calculate the exact Hamiltonian of the CID model."""
        raise NotImplementedError
