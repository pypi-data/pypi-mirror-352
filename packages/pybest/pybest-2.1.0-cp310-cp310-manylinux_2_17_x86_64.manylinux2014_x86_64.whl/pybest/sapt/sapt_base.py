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
"""Symmetry Adapted Perturbation theory module

Variables used in this module:
 :noccX:      number of occupied orbitals in the principle configuration of
              X monomere (A or B)
 :nvirtX:     number of virtual orbitals in the principle configuration of
              X monomere (A or B)
 :nbasisX:    total number of basis functions, current implementation of
              SAPT0 support only dimer centered basis sets (nbasisA == nbasisB)

 Indexing convention:
  :a,b,..: occupied orbitals of principle configuration of corresponding
           monomere: a for A, b for B
  :r,s,..: virtual orbitals of principle configuration of corresponding
           monomere: r for A, s for B
  :k,l,..: general indices (occupied, virtual)
"""

import abc

# package imports
from pybest.cache import Cache
from pybest.exceptions import UnknownOption
from pybest.linalg import DenseLinalgFactory
from pybest.log import log, timer

# module imports
from .sapt_utils import transform_integrals_SAPT


class SAPTBase(abc.ABC):
    """Symmetry Adapted Perturbation Theory base class

    Purpose:
    Precalculate SAPT type integrals (one and two electron) common for SAPT theories.

    Currently supported wavefunction models:
     * RHF (orbital energies and coefficients are required)

    Currently supported Perturbation Theory models:
     * SAPT0 (if Psi_0 = RHF)
    """

    def __init__(self, mon_A, mon_B):
        """
        **Arguments:**

        mon_A, mon_B
             A IOData molecule instance for mon A/B.

        """
        self._lfA = mon_A.lf
        self._denselfA = DenseLinalgFactory(self.lfA.default_nbasis)
        self._noccA = mon_A.occ_model.nocc[0]
        self._nbasisA = self.lfA.default_nbasis
        self._nvirtA = self.nbasisA - self.noccA

        self._lfB = mon_B.lf
        self._denselfB = DenseLinalgFactory(self.lfB.default_nbasis)
        self._noccB = mon_B.occ_model.nocc[0]
        self._nbasisB = self.lfB.default_nbasis
        self._nvirtB = self.nbasisB - self.noccB

        self._cache = Cache()
        self._energy = []
        self._amplitudes = []
        self._nucnuc = 0
        self._result = dict()

    @property
    def lfA(self):
        """The linalg factory of monomer A"""
        return self._lfA

    @property
    def lfB(self):
        """The linalg factory of monomer B"""
        return self._lfB

    @property
    def denselfA(self):
        """The dense linalg factory, monomer A"""
        return self._denselfA

    @property
    def denselfB(self):
        """The dense linalg factory, monomer B"""
        return self._denselfB

    @property
    def nbasisA(self):
        """The number of basis functions, monomer A"""
        return self._nbasisA

    @property
    def nbasisB(self):
        """The number of basis functions, monomer A"""
        return self._nbasisB

    @property
    def noccA(self):
        """The number of occupied orbitals on monomer A"""
        return self._noccA

    @property
    def noccB(self):
        """The number of occupied orbitals on monomer B"""
        return self._noccB

    @property
    def nvirtA(self):
        """The number of virtual orbitals on monomer A"""
        return self._nvirtA

    @property
    def nvirtB(self):
        """The number of virtual orbitals on monomer B"""
        return self._nvirtB

    def clear_aux_matrix(self):
        """Clear the auxiliary matrices"""
        self._cache.clear(tags="m", dealloc=True)

    def get_aux_matrix(self, select):
        """Get an auxiliary matrix.

        **Arguments:**

        select
             Suffix of auxiliary matrix. See :py:meth:`Sapt0.init_aux_matrix`
        """
        if select not in self._cache:
            raise UnknownOption(
                f"The auxmatrix {select} not found in cache. Did you use init_aux_matrix?"
            )
        return self._cache.load(select)

    @property
    def nucnuc(self):
        """Intramonomer nuclear-nuclear repulsion"""
        return self._nucnuc

    @nucnuc.setter
    def nucnuc(self, value):
        """Intramonomer nuclear-nuclear repulsion"""
        self._nucnuc = value

    @property
    def result(self):
        """Returns result dictionary"""
        return self._result

    @abc.abstractmethod
    def calculate_aux_matrix(self):
        """Calculates all necessary integrals,
        should be overridden in child class
        """

    @abc.abstractmethod
    def update_aux_matrix(self):
        """Updates all necessary integrals,
        should be overridden in child class
        """

    @abc.abstractmethod
    def solve(self):
        """Solves given perturbation orders,
        should be overridden in child class
        """

    @staticmethod
    def log_out_correction(name, value, unit=""):
        """Helper method to logout single correction value"""
        msg_str = f"{name:<30s} =>  {value:>+.8f} {unit}"
        log(msg_str)

    @timer.with_section("SAPT")
    def __call__(self, mon_A, mon_B, dimer, indextrans="cupy"):
        """SAPT0 functor method invoking SAPT0(RHF) computations

        **Arguments:**

        mon_A, mon_B, dimer
            A IOData molecule instance for mon A/B and dimer.

        **Optional arguments:**

        indextrans
            4-index Transformation (str). Choice between
            ``tensordot`` (default), ``cupy``, ``einsum``,
            ``cpp``, ``opt_einsum``, or ``einsum_naive``.
            If ``cupy`` is not available, we switch to ``tensordot``.

        """
        log.hline("=")
        log(" ")
        log("Entering SAPT0(RHF) theory module")
        log(" ")
        log.hline("~")

        # set constant nuclear repulsion term
        self.nucnuc = dimer.nuc - mon_A.nuc - mon_B.nuc

        #
        # Integral Transformations
        #
        # Overlap transformation
        olp_AB = dimer.olp.new()
        olp_AB.assign_two_index_transform(dimer.olp, mon_A.orb, mon_B.orb)

        # nuclear attraction integrals transformation #
        na_A_BB = mon_A.na.new()
        na_B_AA = mon_B.na.new()
        na_A_BB.assign_two_index_transform(mon_A.na, mon_B.orb)
        na_B_AA.assign_two_index_transform(mon_B.na, mon_A.orb)

        # Two electron integrals transformation #
        (two_ABAB,) = transform_integrals_SAPT(
            dimer.eri, mon_A.orb, mon_B.orb, indextrans, simple=True
        )
        # Combing one electron integrals #
        na_transformed = (na_A_BB, na_B_AA)
        olp_transformed = olp_AB
        two_transformed = two_ABAB

        # Calculating auxillary matricies
        self.calculate_aux_matrix(
            na_transformed,
            olp_transformed,
            two_transformed,
            (mon_A.orb, mon_B.orb, dimer.orb),
        )

        self.solve()
        self.clear_aux_matrix()

        del two_ABAB, na_transformed, olp_transformed
