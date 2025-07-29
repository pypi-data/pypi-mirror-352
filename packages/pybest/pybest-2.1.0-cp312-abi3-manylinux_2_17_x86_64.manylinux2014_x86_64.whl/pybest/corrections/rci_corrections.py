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
"""RCI Corrections Module"""

from pybest.iodata import CheckPoint
from pybest.log import log
from pybest.utility import check_options


class RCICorrections:
    """Restricted Configuration Interaction Corrections class"""

    acronym = ""

    def __init__(self, nacto):
        """
        **Arguments:**

        nacto
            number of active occupied orbitals in the principle configuration
        """
        log.cite(
            "the size consistency corrections",
            "davidson-corr",
            "scc-overview",
            "meissner-overview",
            "duch1994",
        )
        self._n_e = 2 * nacto
        self._checkpoint = CheckPoint({})
        self._e_scc = {}
        self._e_ref = 0
        self._display = True

    #
    # Properties
    #
    @property
    def c_0(self):
        """The value of the reference coefficient"""
        return self._c_0

    @c_0.setter
    def c_0(self, new):
        if (1 - new**2) > self.threshold_c_0:
            log.warn(
                f"{'Reference state coefficient is suspiciously low: '}"
                f"{new:>.8f}"
            )
            log.warn(
                "Targeted State might have multireference character or "
                "might not be the ground state!"
            )
            log(
                "Try to set more guess vectors (nguessv) and/or more roots (nroot)"
            )
        self._c_0 = new

    @property
    def e_ci(self):
        """The energy value of determined ground state of CI Hamiltonian.
        Precisely, the difference in energy between the reference and post-reference method
        """
        return self._e_ci

    @e_ci.setter
    def e_ci(self, new):
        self._e_ci = new

    @property
    def n_e(self):
        """The number of electrons for chosen system"""
        return self._n_e

    @property
    def e_ref(self):
        """Energy of the reference method (HF Energy)"""
        return self._e_ref

    @e_ref.setter
    def e_ref(self, new):
        self._e_ref = new

    @property
    def e_scc(self):
        """The values of size-consistency corrections (dict):
        Currently supported Davidson-type corrections:
         * Davidson
         * Renormalized Davidson
         * Modified Pople
         * Meissner
        * Duch and Diercksen
        """
        return self._e_scc

    @e_scc.setter
    def e_scc(self, new):
        self._e_scc = new

    @property
    def display(self):
        """(boolean) True: prints the results of size-consistency correction"""
        return self._display

    @display.setter
    def display(self, new):
        self._display = new

    @property
    def checkpoint(self):
        """The iodata container that contains size-consistency corrections
        dump to disk.
        """
        return self._checkpoint

    @checkpoint.setter
    def checkpoint(self, new):
        self._checkpoint = new

    @property
    def threshold_c_0(self):
        """The threshold used to check the accuracy of Davidson-type corrections."""
        return self._threshold_c_0

    @threshold_c_0.setter
    def threshold_c_0(self, new):
        self._threshold_c_0 = new

    def read_input(self, ci_vector_0, e_ci_0, **kwargs):
        """Reads and sets up input parameters."""
        for name in kwargs:
            check_options(
                name,
                name,
                "threshold_c_0",
                "display",
                "e_ref",
                "acronym",
            )
        self.threshold_c_0 = kwargs.get("threshold_c_0", 0.3)
        self.display = kwargs.get("display", True)
        self.e_ref = kwargs.get("e_ref", 0)
        self.acronym = kwargs.get("acronym", "")
        self.c_0 = ci_vector_0
        self.e_ci = e_ci_0

    def compute_davidson_correction(self):
        """Calculates Davidson-type corrections.
        Currently supported are the Davidson-type corrections:
            * Davidson
            * Renormalized Davidson
            * Modified Pople
            * Meissner
            * Duch and Diercksen
        """
        e_ci = self.e_ci
        c_0 = self.c_0
        n_e = self.n_e
        coeff = 1 - c_0**2
        # 1) Davidson correction
        e_dc = coeff * (e_ci)
        # 2) Renormalized Davidson correction
        e_rdc = e_dc / (c_0**2)
        # 3) Modified Pople correction
        e_pc = e_rdc * (1 - 2 / (n_e))
        # 4) Meissner correction
        e_mc = e_rdc * ((n_e - 2) * (n_e - 3) / (n_e * (n_e - 1)))
        # 5) Duch and Diercksen correction
        e_ddc = e_ci * coeff / (2 * (n_e - 1) / (n_e - 2) * c_0**2 - 1)
        return {
            "Davidson": float(e_dc),
            "Renormalized Davidson": float(e_rdc),
            "Modified Pople": float(e_pc),
            "Meissner": float(e_mc),
            "Duch and Diercksen": float(e_ddc),
        }

    def __call__(self, ci_vector_0, e_ci_0, **kwargs):
        """Calculates the size-consistency corrections

        **Arguments:**
            ci_vector_0
                      The value of the reference coefficient

            e_ci_0
                      The energy values of determined ground state of
                      CI Hamiltonian. Precisely, the difference between
                      reference and post-reference method

        **Keywords:**

            Contains the following keyword arguments:
             * threshold_c_0:  threshold that helps verifing the accuracy of
                               Davidson-type corrections
             * display:        (boolean) True: prints the results of size-consistency correction
             * e_ref:          Energy of the reference method (HF Energy)
             * acronym:        Name of the method which requires size-consistency correction

        **Returns**

            An IOData container containing names of Davidson-type corrections (str)
            and values of each correction (float)
        """
        self.read_input(ci_vector_0, e_ci_0, **kwargs)
        self.e_scc = self.compute_davidson_correction()
        if self.display:
            self.printer()
        self.checkpoint.update("e_ci_scc", self.e_scc)
        return self.checkpoint()

    def printer(self):
        """Displays the calculated Davidson-type corrections."""
        e_ci = self.e_ci
        log(f"{'Davidson-type Corrections':>33s}")
        log(
            f"{'type:':>22} {'E(Q)[au]:':>24s}"
            f"\t{'E_':>15s}{self.acronym:>s}{'(Q)[au]:'}"
        )
        for key, value in self.e_scc.items():
            log(
                f"\t{key:>22s}:"
                f"\t{value:> 16.8f}"
                f"\t{self.e_ref + e_ci + value:> 16.8f}"
            )
        log.hline(".")
