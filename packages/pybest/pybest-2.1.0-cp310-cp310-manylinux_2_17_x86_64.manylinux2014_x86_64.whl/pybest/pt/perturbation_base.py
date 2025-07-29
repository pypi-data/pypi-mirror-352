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
# This module has been originally written and updated by Katharina Boguslawski (see CHANGELOG)
# Its current version contains updates from the PyBEST developer team.
#
# Part of this implementation can also be found in `Horton 2.0.0`.
# However, this file has been updated and debugged. Compatibility with Horton is NOT
# guaranteed.
#
# Detailed changes (see also CHANGELOG):
# 2020-07-01: update class structure and init procedure
# 2020-07-01: make function call more user friendly and black box by passing IOData instance
# 2020-07-01: update to new python features, including f-strings
# 2020-07-01: use PyBEST standards, including naming convention and filemanager

"""Perturbation theory module

Variables used in this module:
 :ncore:      number of frozne core orbitals
 :nocc:       number of occupied orbitals in the principle configuration
 :nacto:      number of active occupied orbitals in the principle configuration
 :nvirt:      number of virtual orbitals in the principle configuration
 :nactv:      number of active virtual orbitals in the principle configuration
 :nbasis:     total number of basis functions
 :nact:       total number of active orbitals (nacto+nactv)
 :energy:     the energy correction, dictionary that can contain different
              contributions
 :amplitudes: the optimized amplitudes, list that can contain different
              contributions
 :singles:    the singles amplitudes, bool used to determine whether singles
              are to be included or not

 Indexing convention:
  :i,j,k,..: occupied orbitals of principle configuration
  :a,b,c,..: virtual orbitals of principle configuration
  :p,q,r,..: general indices (occupied, virtual)
"""

from abc import ABC, abstractmethod

from pybest.cache import Cache
from pybest.exceptions import (
    ArgumentError,
    EmptyData,
    NonEmptyData,
    UnknownOption,
)
from pybest.featuredlists import OneBodyHamiltonian
from pybest.helperclass import PropertyHelper
from pybest.iodata import CheckPoint
from pybest.linalg import DenseLinalgFactory, FourIndex, Orbital, TwoIndex
from pybest.log import log, timer
from pybest.utility import (
    check_lf,
    split_core_active,
    transform_integrals,
    unmask,
    unmask_orb,
)


class Perturbation(ABC):
    """Perturbation class

    Purpose:
    Optimize amplitudes and determine energy correction to some
    reference wavefunction.

    Currently supported wavefunction models:
     * RHF
     * RpCCD

    Currently supported Perturbation Theory models:
     * MP2 (if Psi_0 = RHF)
     * PT2SDd (if Psi_0 = RpCCD, diagonal H_0, dual <0|)
     * PT2MDd (if Psi_0 = RpCCD, diagonal H_0, dual <pCCD|)
     * PT2SDo (if Psi_0 = RpCCD, off-diagonal H_0, dual <0|)
     * PT2MDo (if Psi_0 = RpCCD, off-diagonal H_0, dual <pCCD|)
     * PT2b (if Psi_0 = RpCCD, off-diagonal H_0, dual <pCCD|, approximate V')
    """

    long_name = ""
    acronym = ""
    reference = ""

    def __init__(self, lf, occ_model):
        """
        **Arguments:**

        lf
            A LinalgFactory instance.

        occ_model
            Aufbau model

        **Optional arguments:**

        ncore
            (int) number of frozen core orbitals (doubly occupied)
        """
        self._lf = lf
        self._denself = DenseLinalgFactory(lf.default_nbasis)
        self._occ_model = occ_model
        self._nocc = occ_model.nocc[0]
        ncore = occ_model.ncore[0]
        self._nacto = occ_model.nocc[0] - ncore
        self._ncore = ncore
        if self._nacto <= 0 or self._nacto > occ_model.nocc[0]:
            raise ValueError(
                f"Impossible number of frozen core orbitals! You have chosen {ncore} "
                f"frozen core orbitals out of {occ_model.nocc[0]} occupied orbitals."
            )
        # total number of basis functions
        self._nbasis = lf.default_nbasis
        # total number of active orbitals (only frozen core supported)
        self._nact = lf.default_nbasis - self._ncore
        # total number of virtuals
        self._nvirt = self._nbasis - self._nocc
        # total number of active virtuals
        self._nactv = self._nact - self._nacto
        if (
            self._nvirt <= 0
            or self._nvirt > lf.default_nbasis - occ_model.nocc[0]
        ):
            raise ValueError(
                f"Impossible number of virtual orbitals: {self._nvirt}!"
            )
        if (
            self._nactv <= 0
            or self._nactv > lf.default_nbasis - occ_model.nocc[0]
        ):
            raise ValueError(
                f"Impossible number of active virtual orbitals: {self._nactv}!"
            )
        self._cache = Cache()
        self._energy = {}
        self._amplitudes = []
        self._doubles = True
        self._singles = False
        self._natorb = False
        self._relaxation = False
        self._e_ref = 0.0
        self._e_core = 0.0
        self._checkpoint = CheckPoint({})
        # include occupation model in checkpoint file
        self.checkpoint.update("occ_model", self.occ_model)

    @property
    def lf(self):
        """The linalg factory"""
        return self._lf

    @property
    def denself(self):
        """The dense linalg factory"""
        return self._denself

    @property
    def occ_model(self):
        """The occupation model"""
        return self._occ_model

    @property
    def cache(self):
        """The Cache. Used to store module dependent objects in memory."""
        return self._cache

    @property
    def nbasis(self):
        """The number of basis functions"""
        return self._nbasis

    @property
    def nocc(self):
        """The number of occupied orbitals"""
        return self._nocc

    @property
    def ncore(self):
        """The number of frozen core orbitals"""
        return self._ncore

    @property
    def nvirt(self):
        """The number of virtual orbitals"""
        return self._nvirt

    @property
    def nacto(self):
        """The number of active occupied orbitals"""
        return self._nacto

    @property
    def nactv(self):
        """The number of active virtual orbitals"""
        return self._nactv

    @property
    def nact(self):
        """The number of active basis functions"""
        return self._nact

    @property
    def energy(self):
        """The PT energy"""
        return self._energy

    @energy.setter
    def energy(self, new):
        self._energy.update(new)
        for key in new:
            self.checkpoint.update(key, new[key])

    @energy.deleter
    def energy(self):
        self._energy = {}

    @property
    def e_core(self):
        """Reference energy"""
        return self._e_core

    @e_core.setter
    def e_core(self, new):
        self._e_core = new

    @property
    def e_ref(self):
        """Reference energy"""
        return self._e_ref

    @e_ref.setter
    def e_ref(self, new):
        self._e_ref = new

    @property
    def amplitudes(self):
        """The PT amplitudes"""
        return self._amplitudes

    @amplitudes.setter
    def amplitudes(self, new):
        if new:
            if self._amplitudes:
                raise NonEmptyData("Warning: List of PT amplitudes not empty!")
            for new_ in new:
                self._amplitudes.append(new_)
        else:
            self._amplitudes = []

    @amplitudes.deleter
    def amplitudes(self):
        """Clear amplitude information"""
        del self._amplitudes[:]
        self._amplitudes = []

    @property
    def checkpoint(self):
        """The iodata container that contains all data dump to disk"""
        return self._checkpoint

    @property
    def singles(self):
        """Switch for PT singles amplitudes"""
        return self._singles

    @singles.setter
    def singles(self, new):
        self._singles = new

    @property
    def doubles(self):
        """Switch for PT doubles amplitudes"""
        return self._doubles

    @doubles.setter
    def doubles(self, new):
        self._doubles = new

    @property
    def natorb(self):
        """Switch for natural orbitals"""
        return self._natorb

    @natorb.setter
    def natorb(self, new):
        self._natorb = new

    @property
    def relaxation(self):
        """Switch for natural orbitals"""
        return self._relaxation

    @relaxation.setter
    def relaxation(self, new):
        self._relaxation = new

    def update_ndm(self, ndm=None):
        """Update 1-RDM

        **Optional arguments:**

        ndm
             When provided, this n-RDM is stored.
        """
        raise NotImplementedError

    def get_ndm(self, select):
        """Get a density matrix (n-RDM). If not available, it will be created
        (if possible)

        **Arguments:**

        """
        if select not in self.cache:
            self.update_ndm()
        return self.cache.load(select)

    def init_ndm(self, select):
        """Initialize n-RDM as TwoIndex object

        **Arguments**

        """
        alloc_size = {
            "one_dm": (self.lf.create_two_index, self.lf.default_nbasis)
        }
        dm, new = self._cache.load(
            select,
            alloc=alloc_size[select],
            tags="d",
        )
        if not new:
            raise NonEmptyData(
                f"The density matrix {select} already exists. "
                "Call one_dm.clear prior to updating the 1DM."
            )
        return dm

    one_dm = PropertyHelper(get_ndm, "one_dm", "Alpha 1-RDM")

    @abstractmethod
    def calculate_aux_matrix(self, mo1, mo2):
        """Generate auxiliary matrices/tensors used in optimization of PT
        amplitudes.
        """

    @abstractmethod
    def solve(self, *args, **kwargs):
        """Solve for energy and amplitudes of a given PT flavour."""

    @abstractmethod
    def print_results(self, **kwargs):
        """Print final results to standard output."""

    @abstractmethod
    def check_result(self, **kwargs):
        """Check results of PT model for consistencies."""

    @abstractmethod
    def check_input(self, **kwargs):
        """Check input keyword arguments during function call."""

    @abstractmethod
    def print_info(self, **kwargs):
        """Print information on keyword arguments and other properties of a
        given PT flavour.
        """

    def clear(self):
        """Clear all wavefunction information"""
        self._cache.clear()

    def clear_dm(self):
        """Clear RDM information"""
        self._cache.clear(tags="d", dealloc=True)

    def clear_aux_matrix(self):
        """Clear the auxiliary matrices"""
        self._cache.clear(tags="m", dealloc=True)

    def get_aux_matrix(self, select):
        """Get an auxiliary matrix.

        **Arguments:**

        select
             Suffix of auxiliary matrix. See :py:meth:`RMP2.init_aux_matrix`,
             :py:meth:`pCCDPT2.init_aux_matrix` for possible choices
        """
        if select not in self.cache:
            raise EmptyData(
                f"The auxmatrix {select} not found in cache. "
                "Did you use init_aux_matrix?"
            )
        return self.cache.load(select)

    def get_checkpoint_fn(self):
        """Get filename for checkpointing. Contains acronym of PT flavour."""
        if self.singles:
            return f"checkpoint_{self.acronym}.h5"
        return f"checkpoint_{self.acronym}.h5"

    def get_range(self, string, start=0):
        """Returns dictionary with keys beginX, endX, begin(X+1), etc.
        *  string - any sequence of
            'o' (occupied)
            'v' (nacto to nact)
            'n' (0 to nact)
            'V' (0 to nactv)
        """
        range_ = {}
        ind = start
        for char in string:
            if char == "o":
                range_[f"begin{ind}"] = 0
                range_[f"end{ind}"] = self.nacto
            elif char == "c":
                range_[f"begin{ind}"] = self.ncore
                range_[f"end{ind}"] = self.nocc
            elif char == "C":
                range_[f"begin{ind}"] = self.nocc
                range_[f"end{ind}"] = self.nbasis
            elif char == "v":
                range_[f"begin{ind}"] = self.nacto
                range_[f"end{ind}"] = self.nact
            elif char == "V":
                range_[f"begin{ind}"] = 0
                range_[f"end{ind}"] = self.nactv
            elif char == "n":
                range_[f"begin{ind}"] = 0
                range_[f"end{ind}"] = self.nbasis
            else:
                raise UnknownOption(
                    f"Do not know how to handle choice {char}."
                )
            ind += 1
        return range_

    def unmask_args(self, *args, **kwargs):
        """Resolve arguments and keyword arguments passed to function call."""
        # orb
        orbs = unmask_orb(*args)
        if orbs:
            orbs = orbs[0]
            self.checkpoint.update("orb_a", orbs.copy())
        else:
            raise ArgumentError("Cannot find orbitals in functional call")
        # 1-e ints and 2-e ints
        one = self.lf.create_two_index(label="one")
        for arg in args:
            if isinstance(arg, TwoIndex):
                if arg.label in OneBodyHamiltonian:
                    one.iadd(arg)
            elif isinstance(arg, FourIndex):
                check_lf(self.lf, arg)
                two = arg
        # overlap (optional)
        olp = unmask("olp", *args, **kwargs)
        if olp is not None:
            self.checkpoint.update("olp", olp)
        return one, two, orbs

    @timer.with_section("PT: Base")
    def __call__(self, *args, **kwargs):
        """Performs a perturbation theory calculation.

        **Arguments:**

        args
            One- (TwoIndex) and two-body (FourIndex) integrals (some
            Hamiltonian matrix elements), the MO coefficient matrix
            (Orbital instance), the geminal coefficient matrix (TwoIndex)
            in any order.

        **Keywords:**
            Contains reference energy and solver specific input parameters:
             * e_ref: (float) reference energy (default float('nan'))
             * threshold: (float) tolerance for amplitudes (default 1e-6)
             * maxiter: (int) maximum number of iterations (default 200)
             * guess: (np.array) initial guess (default None)
             * singels: (bool) include singles (default False)
             * overlap: (float) approximat overlap used in PT2MD (default nan)
             * freeze:  (2-d np.array) frozen amplitudes stored as array
                        containing indices and amplitudes (default empty array).
                        Only supported for MP2 module.
             * indextrans: 4-index Transformation (str). Choice between
                           ``tensordot`` (default), ``cupy``, ``einsum``,
                           ``cpp``, ``opt_einsum``, or ``einsum_naive``. If
                           ``cupy`` is not available, we switch to ``tensordot``.

        **Returns**
             List of energy contributions (total energy, seniority-0,
             seniority-2, seniority-4, singles (if required)) and PT
             amplitudes (doubles, singles (if required))

        """
        self.natorb = kwargs.get("natorb", False)
        self.relaxation = kwargs.get("relaxation", False)
        indextrans = kwargs.get("indextrans", None)
        self.e_core = unmask("e_core", *args, **kwargs)
        # Reference energy is total energy (RHF or RpCCD); it does not work for e_tot=0
        self.e_ref = unmask("e_tot", *args, **kwargs) or unmask(
            "e_ref", *args, **kwargs
        )
        # If e_ref is still None, set it to 0, this feature is used by other modules
        if self.e_ref is None:
            self.e_ref = 0.0
            log.warn("Reference energy 'e_ref' not found. Setting to 0.0 a.u.")
        if self.e_core is None:
            # Do not save None, if not provided set to zero
            self.e_core = 0
            log.warn("Core energy 'e_core' not found. Setting to 0.0 a.u.")
        #
        # Clear everything
        #
        del self.amplitudes
        del self.energy
        if log.do_medium:
            log.hline("=")
            log(" ")
            log("Entering perturbation theory module")
            log(" ")
            log.hline("~")

        #
        # Unmask arguments
        #
        fargs = []
        one, two, orbs = self.unmask_args(*args, **kwargs)

        #
        # Check input parameters
        #
        self.check_input(**kwargs)

        #
        # Print method specific information
        #
        self.print_info(**kwargs)

        #
        # Append arguments, used as arguments in root finding:
        #
        fargs.append(orbs)

        #
        # Transform integrals:
        #
        if self.ncore > 0:
            cas = split_core_active(
                one,
                two,
                orbs,
                e_core=self.e_core,
                ncore=self.ncore,
                nactive=self.nact,
                indextrans=indextrans,
            )
            mo1 = cas.one
            mo2 = cas.two
            self.e_core = cas.e_core
        else:
            ti = transform_integrals(one, two, orbs, indextrans=indextrans)
            mo1 = ti.one[0]
            mo2 = ti.two[0]

        #
        # Construct auxiliary matrices (checks also type of arguments):
        # delete mo integrals after using
        #
        self.calculate_aux_matrix(mo1, mo2)
        del mo1, mo2

        #
        # Solve for energy and amplitudes:
        #
        energy, amplitudes = self.solve(*fargs, **kwargs)
        del self.energy
        self.energy = energy
        self.amplitudes = amplitudes

        #
        # Update density matrices (response 1-RDM) and calculate
        # natural orbitals (if wanted) and occupation numbers
        #
        self.clear_dm()
        self.update_ndm()
        if self.natorb:
            natocc = self.lf.create_one_index()
            #
            # Check if args has orbitals as argument, if yes, overwrite
            # orbitals. Otherwise, we assume that the orbitals have been passed
            # using an IOData container. Then we have to create a copy
            #
            orbs_ = orbs.copy()
            for arg in args:
                if isinstance(arg, Orbital):
                    orbs_ = arg
            orbs_.derive_naturals(self.one_dm, sort=True, backtrafo=True)
            natocc.assign(orbs_.occupations)
            self.clear_dm()
            self.update_ndm(natocc)
            self.checkpoint.update("orb_a", orbs_.copy())
        try:
            self.checkpoint.update("dm_1", self.one_dm)
        except AttributeError:
            pass

        #
        # Print some output information for user:
        #
        self.print_results(**kwargs)

        #
        # Make sanity checks. If somethings is wrong, abort calculation:
        #
        self.check_result(**kwargs)

        #
        # Clean up after execution:
        #
        self.clear_aux_matrix()

        #
        # Do Checkpoint
        #
        checkpoint_fn = self.get_checkpoint_fn()
        self.checkpoint.to_file(checkpoint_fn)

        if log.do_medium:
            log(" ")
            log.hline("=")

        return self.checkpoint()
