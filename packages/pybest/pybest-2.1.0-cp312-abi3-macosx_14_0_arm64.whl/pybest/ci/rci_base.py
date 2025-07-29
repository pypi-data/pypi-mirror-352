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
#
# Changelog:
# 05/2025: This file has been updated by Iulia Emilia Brumboiu to enable
# the use of active core orbitals, required for X-ray absorption calculations.
#
# Detailed changes:
# See CHANGELOG

"""
Variables used in this module:
 :ncore:     number of frozen core orbitals
 :nocc:      number of occupied orbitals in the principal configuration
 :nactc:     number of active core orbitals for the core-valence separation approximation (zero by default)
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

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np

from pybest import filemanager
from pybest.cache import Cache
from pybest.corrections.rci_corrections import RCICorrections
from pybest.exceptions import ArgumentError, NonEmptyData
from pybest.featuredlists import OneBodyHamiltonian, TwoBodyHamiltonian
from pybest.iodata import CheckPoint, IOData
from pybest.linalg import DenseLinalgFactory, LinalgFactory
from pybest.linalg.base import FourIndex, OneIndex, ThreeIndex, TwoIndex
from pybest.log import log
from pybest.occ_model import AufbauOccModel
from pybest.solvers import Davidson
from pybest.utility import (
    check_options,
    split_core_active,
    transform_integrals,
    unmask,
    unmask_orb,
)


class RCI(ABC):
    """Configuration Interaction base class"""

    long_name = ""
    acronym = ""
    reference = ""
    cvs = ""

    def __init__(self, lf: LinalgFactory, occ_model: AufbauOccModel) -> None:
        """Initialize all CI models with common properties.

        Args:
            lf (LinalgFactory): The linalg factory instance
            occ_model (AufbauOccModel): The Aufbau occupation model
        """
        #
        # Variables
        #
        self._lf = lf
        self._denself = DenseLinalgFactory(lf.default_nbasis)
        self._nocc = occ_model.nocc[0]

        self._occ_model = occ_model

        self._cache = Cache()
        self._checkpoint = CheckPoint({})
        self._checkpoint_fn = f"checkpoint_{self.acronym}.h5"
        self._todisk = False
        self._nroot = 1
        self._dimension = 0
        self._print_csf = False
        # Include occupation model into checkpoint file (IOData container)
        self.checkpoint.update("occ_model", self.occ_model)
        # Include core energy into checkpoint file (IOData container)
        self.checkpoint.update("e_core", 0.0)

    #
    #  Properties
    #
    @property
    def occ_model(self):
        """The occupation model."""
        return self._occ_model

    @property
    def rci_corrections(self):
        """Instance of RCICorrections class"""
        return self._rci_corrections

    @rci_corrections.setter
    def rci_corrections(self, new):
        self._rci_corrections = new

    @property
    def threshold_c_0(self):
        """The threshold for Davidson-type corrections.
        Forwarded to RCICorrections module.
        """
        return self._threshold_c_0

    @threshold_c_0.setter
    def threshold_c_0(self, new):
        self._threshold_c_0 = new

    @property
    def threshold(self):
        """The threshold for printing CI coefficients"""
        return self._threshold

    @threshold.setter
    def threshold(self, new):
        self._threshold = new

    @property
    def lf(self):
        """The linalg factory"""
        return self._lf

    @property
    def denself(self):
        """The dense linalg factory"""
        return self._denself

    @property
    def size_consistency_correction(self):
        """A boolean variable (default: True):
        -True: perform Davidson-type corrections
        """
        return self._size_consistency_correction

    @size_consistency_correction.setter
    def size_consistency_correction(self, new):
        if not isinstance(new, bool):
            raise ArgumentError(
                "Unkown type for keyword correction. Boolean type required."
            )
        self._size_consistency_correction = new

    @property
    def davidson(self):
        """A boolean variable (default: True):
        -True: perform Davidson diagonalization
        -False: perform exact diagonalization.
        """
        return self._davidson

    @davidson.setter
    def davidson(self, new):
        if not isinstance(new, bool):
            raise ArgumentError(
                "Unkown type for keyword davidson. Boolean type required."
            )
        self._davidson = new

    @property
    def print_csf(self):
        """A boolean variable (default: False):
        -True: print the results in CSF basis
        -False: print the results in SD basis.
        """
        return self._print_csf

    @print_csf.setter
    def print_csf(self, new):
        self._print_csf = new

    @property
    def cache(self):
        """A Cache instance."""
        return self._cache

    @property
    def checkpoint(self):
        """The iodata container that contains all data dump to disk."""
        return self._checkpoint

    @checkpoint.setter
    def checkpoint(self, new):
        self._checkpoint = new

    @property
    def checkpoint_fn(self):
        """The filename that will be dumped to disk."""
        return self._checkpoint_fn

    @property
    def todisk(self):
        """Dumping the eigenvectors to disk
        (default: False, True-currently not supported)
        """
        return self._todisk

    @todisk.setter
    def todisk(self, new):
        self._todisk = new

    @property
    def nroot(self):
        """The number of targeted states."""
        return self._nroot

    @nroot.setter
    @abstractmethod
    def nroot(self, new):
        raise NotImplementedError

    @property
    def dimension(self):
        """The dimension of the Hamiltonian matrix."""
        return self._dimension

    @dimension.setter
    @abstractmethod
    def dimension(self, new=None):
        raise NotImplementedError

    @abstractmethod
    def collect_data(self, index, data, evecsj):
        """Collects the data and prepares them for printing"""

    @abstractmethod
    def set_hamiltonian(self, mo1, mo2):
        """Computation of auxiliary matrices."""

    @abstractmethod
    def calculate_exact_hamiltonian(self):
        """Calculates the exact Hamiltonian for the chosen model."""

    @abstractmethod
    def printer(self):
        """Printing the results."""

    #
    # Cache methods
    #
    def from_cache(self, select):
        """Get a matrix/tensor from the cache.

        **Arguments:**

        select
            (str) some object stored in the Cache.
        """
        if select in self.cache:
            return self.cache.load(select)
        raise NotImplementedError

    def init_cache(
        self, select: str, *args: Any, **kwargs: dict[str, Any]
    ) -> OneIndex | TwoIndex | ThreeIndex | FourIndex:
        """Initialize some cache instance.

        Args:
            select (str): label of the auxiliary tensor
            args (Any): The size of the auxiliary matrix in each dimension.
                        The number of given arguments determines the order and
                        sizes of the tensor. Either a tuple or a string
                        (oo, vv, ovov, etc.) indicating the sizes.
                        Not required if ``alloc`` is specified.

        Keyword Args:
            tags (str): The tag used for storing some matrix/tensor in the Cache
                        (default `h`).
            alloc: Specify alloc function explicitly. If not defined some flavor
                   of `self.lf.create_N_index` is taken depending on the length
                   of args.
            nvec (int) : Number of Cholesky vectors. Only required if
                         Cholesky-decomposed ERI are used. In this case, only
                         ``args[0]`` is required as the Cholesky class does not
                         support different sizes of arrays. Default is None.

        Raises:
            ArgumentError: If allocation method is not known
            NonEmptyData: If element already exists in self.cache (has to be deleted first)

        Returns:
            NIndex: Eithe One, Two, Three, or Cholesky index
        """
        for name, _ in kwargs.items():
            check_options(name, name, "tags", "nvec", "alloc")
        tags = kwargs.get("tags", "h")
        nvec = kwargs.get("nvec", None)
        alloc = kwargs.get("alloc", None)
        # resolve args: either pass dimensions or string indicating dimensions
        args = self.get_size(args)

        if len(args) == 0 and not alloc:
            raise ArgumentError(
                "At least one dimension or a user-defined allocation function "
                "have to be specified"
            )
        if alloc:
            pass
        elif nvec is not None:
            alloc = (self.lf.create_four_index, args[0], nvec)
        elif len(args) == 1:
            alloc = (self.lf.create_one_index, *args)
        elif len(args) == 2:
            alloc = (self.lf.create_two_index, *args)
        elif len(args) == 3:
            alloc = (self.lf.create_three_index, *args)
        else:
            alloc = (self.denself.create_four_index, *args)
        # load into the cache
        matrix, new = self.cache.load(select, alloc=alloc, tags=tags)
        if not new:
            raise NonEmptyData(
                f"The Cache instance {select} already exists. "
                "Call clear prior to updating the Cache instance."
            )

        return matrix

    def clear_cache(self, **kwargs: dict[str, Any]) -> None:
        """Clear the Cache instance.

        Keyword arguments:
            tags: The tag used for storing some matrix/tensor in the Cache (default
                  `h`).
        """
        for name in kwargs:
            check_options(name, name, "tags")
        tags = kwargs.get("tags", "m")

        self.cache.clear(tags=tags, dealloc=True)

    #
    # FUNCTIONS
    #
    def print_info(self):
        """Print information about the CI calculations."""
        log(" ")
        log(f"Entering {self.long_name} ")
        log(" ")
        log.hline("~")
        log(f"{self.acronym} framework selected")
        log.hline("~")
        log("OPTIMIZATION PARAMETERS:")
        log(f"CI model:                          {self.acronym}")
        log(f"Reference function:                {self.reference}")
        log(f"Number of frozen cores:            {self.occ_model.ncore[0]}")
        log(f"Number of active core:             {self.occ_model.nactc[0]}")
        log(f"Number of active occupied:         {self.occ_model.nacto[0]}")
        log(f"Number of active virtuals:         {self.occ_model.nactv[0]}")
        log(f"Number of targeted roots:          {self.nroot}")
        log(f"Total number of roots:             {self.dimension}")
        log(f"Spin-adapted configurations (CSF): {self.csf}")
        log(
            f"Davidson-type corrections:         {self.size_consistency_correction}"
        )
        log(f"Core-valence separation approx.:   {self.cvs}")
        if self.cvs:
            log(
                f"Core orbitals in the CVS space:    {self.occ_model.nactc[0]}"
            )
        if self.davidson:
            log("Diagonalization:                   Davidson")
        else:
            log("Diagonalization:                   Exact Diagonalization")
        log("Tensor contraction engine:         automatic")
        log.hline("~")

    def get_range(self, string, start=0):
        """Returns dictionary with keys beginX, endX, begin(X+1), etc.
        *  string - any sequence of 'o' (occupied), 'c' (active core), and 'v' (virtual)
        """
        range_ = {}
        ind = start
        for char in string:
            if char == "c":
                range_["begin" + str(ind)] = 0
                range_["end" + str(ind)] = self.occ_model.nactc[0]
            elif char == "o":
                # by default, nactc is zero
                range_["begin" + str(ind)] = self.occ_model.nactc[0]
                range_["end" + str(ind)] = (
                    self.occ_model.nactc[0] + self.occ_model.nacto[0]
                )
            elif char == "v":
                range_["begin" + str(ind)] = (
                    self.occ_model.nacto[0] + self.occ_model.nactc[0]
                )
                range_["end" + str(ind)] = self.occ_model.nact[0]
            elif char == "V":
                range_["begin" + str(ind)] = 0
                range_["end" + str(ind)] = self.occ_model.nactv[0]
            elif char == "n":
                range_["begin" + str(ind)] = 0
                range_["end" + str(ind)] = self.occ_model.nact[0]
            else:
                raise ArgumentError(
                    f"Do not know how to handle choice {char}."
                )
            ind += 1
        return range_

    def get_size(self, string):
        """Returns list of arguments containing sizes of tensors

        **Arguments:**

        string : string or int
            any sequence of "o" (occupied), "c" (active core), and "v" (virtual) OR a tuple of
            integers indicating the sizes of an array
        """
        args = []
        for char in string:
            if char == "o":
                args.append(self.occ_model.nacto[0])
            elif char == "c":
                args.append(self.occ_model.nactc[0])
            elif char == "v":
                args.append(self.occ_model.nactv[0])
            elif isinstance(char, int):
                args.append(char)
            else:
                raise ArgumentError(f"Do not know how to handle size {char}.")
        return tuple(args)

    def read_input(self, **kwargs):
        """Reads and sets up input parameters."""
        for name in kwargs:
            check_options(
                name,
                name,
                "threshold",
                "maxiter",
                "nroot",
                "e_ref",
                "tolerance",
                "tolerancev",
                "nguessv",
                "maxvectors",
                "davidson",
                "scc",
                "threshold_c_0",
                "print_csf",
                "restart",
            )
        #
        # Set default keyword arguments:
        #
        self.threshold = kwargs.get("threshold", 0.1)
        self.davidson = kwargs.get("davidson", True)
        self.print_csf = kwargs.get("print_csf", False)
        self.size_consistency_correction = kwargs.get("scc", True)
        self.threshold_c_0 = kwargs.get("threshold_c_0", 0.3)
        self.nroot = kwargs.get("nroot", 1)
        if self.nroot <= 0:
            raise ValueError("Number of roots must be larger than 0!")

    def unmask_args(self, *args, **kwargs):
        """Resolve arguments passed to function call"""
        #
        # olp
        #
        olp = unmask("olp", *args, **kwargs)
        if olp is None:
            raise ArgumentError("Cannot find overlap integrals.")
        self.checkpoint.update("olp", olp)
        #
        # orb
        #
        orbs = unmask_orb(*args, **kwargs)
        if orbs:
            orbs = orbs[0]
            self.checkpoint.update("orb_a", orbs.copy())
        else:
            raise ArgumentError("Cannot find orbitals.")
        #
        # 1-e ints and 2-e ints
        #
        one = self.lf.create_two_index(label="one")
        for arg in args:
            if isinstance(arg, TwoIndex):
                if arg.label in OneBodyHamiltonian:
                    one.iadd(arg)
            elif isinstance(arg, FourIndex):
                if arg.label in TwoBodyHamiltonian:
                    two = arg

        if self.acronym in ["pCCD-CIS", "pCCD-CID", "pCCD-CISD"]:
            self.t_p = unmask("t_p", *args)
            if self.t_p is None:
                raise ArgumentError("You have to provide the pCCD IOData")
        return one, two, orbs

    def __call__(self, *args, **kwargs):
        """Solve the symmetric eigenvalue problem in CI method

        Currently supported CI techniques of solving:
         * Slater Determinant (SD)
         * Configuration State Function (CSF)

        **Arguments:**

        args
            Contains various arguments: One- and two-body integrals
            (some Hamiltonian matrix elements) expressed in the AO basis,
            an IOData container containing the wave function information
            of the reference state (the AO/MO coefficients, CC amplitudes,
            etc.)

        **Keywords:**

            Contains the following keyword arguments:
             * tolerance:   tolerance for energies (default 1e-6)
             * tolerancev:  tolerance for eigenvectors (default 1e-5)
             * threshold:   printing threshold for contributions of CI wave function (default 0.1)
             * maxiter:     maximum number of iterations (default 200)
             * nroot :      the number of targeted states (default depends on model)
             * nguessv:     total number of guess vectors (default (nroot-1)*4+1)
             * maxvectors:  maximum number of Davidson vectors (default (nroot-1)*10)
             * davidson:    A boolean variable (default True):
                                -True: perform Davidson diagonalization
                                -False: perform exact diagonalization.
             * csf:         (boolean) take spin-adapted configurations (configuration
                            state functions) as basis instead of working with
                            Slater determinants (default False)
            * scc:          (boolean) True option will calculate the size-consistency
                            correction (default True)
            * threshold_c_0:
                            threshold that helps verifying the accuracy of
                            Davidson-type corrections
            * restart:      filename for restart purposes (default "")

        **Returns**

            An IOData container containing all eigenvalues and eigenvectors
            for targeted states.
        """
        #
        # Read input:
        #
        self.read_input(**kwargs)
        #
        # Setup:
        #
        one, two, orbs = self.unmask_args(*args, **kwargs)
        e_ref = unmask("e_tot", *args, **kwargs) or unmask(
            "e_ref", *args, **kwargs
        )
        self.checkpoint.update("e_ref", e_ref)
        #
        # Print Info:
        #
        if log.do_medium:
            self.print_info()
        #
        # Transform of integrals:
        #
        if self.occ_model.ncore[0] > 0:
            cas = split_core_active(
                one,
                two,
                orbs,
                e_core=self.checkpoint["e_core"],
                ncore=self.occ_model.ncore[0],
                nactive=self.occ_model.nact[0],
            )
            mo1 = cas.one
            mo2 = cas.two
        else:
            t_i = transform_integrals(one, two, orbs)
            (mo1,) = t_i.one
            (mo2,) = t_i.two
        #
        # Auxiliary objects
        #
        self.clear_cache()
        self.set_hamiltonian(mo1, mo2)
        del mo1, mo2

        self.diagonalize(**kwargs)
        self.clear_cache()

        if log.do_medium:
            self.printer()

        return self.checkpoint()

    def diagonalize(self, **kwargs):
        """
        Solve for CI Hamiltonian, returns eigenvalues and eigenvectors (stored in
        IOData container of class)

        **Arguments:**

        args
             Contains various arguments: One- and two-body integrals
             (some Hamiltonian matrix elements) expressed in the AO basis,
             an IOData container containing the wave function information
             of the reference state (the AO/MO coefficients, CC amplitudes,
             etc.)

        **Keywords:**

             * tolerance:   tolerance for energies (default 1e-6)
             * tolerancev:  tolerance for eigenvectors (default 1e-5)
             * threshold:   printing threshold for contributions of CI wave function  (default 0.1)
             * maxiter:     maximum number of iterations (default 200)
             * nroot :      the number of targeted states (default depends on model)
             * nguessv:     total number of guess vectors (default (nroot-1)*4+1)
             * maxvectors:  maximum number of Davidson vectors (default (nroot-1)*10)
             * davidson:    A boolean variable (default True):
                                -True: perform Davidson diagonalization
                                -False: perform exact diagonalization.
             * restart:     filename for restart purposes (default "")
        """
        #
        # Set default keyword arguments:
        #
        tol = kwargs.get("tolerance", 1e-6)
        tolv = kwargs.get("tolerancev", 1e-4)
        maxiter = kwargs.get("maxiter", 200)
        nguessv = kwargs.get("nguessv", self.nroot * 4)
        maxvectors = kwargs.get("maxvectors", self.nroot * 10)
        restart_fn = kwargs.get("restart", "")
        #
        # Diagonalization
        #
        if self.davidson:
            davidson = Davidson(
                self.lf,
                self.nroot,
                nguess=nguessv,
                maxiter=maxiter,
                maxvectors=maxvectors,
                tolerance=tol,
                tolerancev=tolv,
                todisk=self.todisk,
                skipgs=False,
                restart_fn=restart_fn,
            )
            e_ci, eigen_act_vector_real = davidson(self)
        else:
            hamiltonian = self.calculate_exact_hamiltonian()
            e_ci, eigen_act_vector_real = np.linalg.eigh(hamiltonian.array)
        #
        # Do Checkpoint
        #
        self.checkpoint.to_file(self.checkpoint_fn)
        self.checkpoint.update("e_ci", e_ci[: self.nroot])
        self.checkpoint.update("civ", eigen_act_vector_real[:, : self.nroot])
        #
        # Perform a size-consistency correction
        #
        # FIXME: probably does not work for CVS!
        if self.size_consistency_correction:
            self.rci_corrections = RCICorrections(self.occ_model.nacto[0])
            self.rci_corrections(
                eigen_act_vector_real[0][0],
                e_ci[0],
                threshold_c_0=self.threshold_c_0,
                display=False,
                e_ref=self.checkpoint["e_ref"],
                acronym=self.acronym,
            )

    def build_guess_vectors(self, nguess, todisk, *args):
        """Used by the Davidson module to construct guess"""
        bvector = []
        hdiag = args[0]
        sortedind = hdiag.sort_indices(True)
        dim = self.dimension
        #
        # Construct Guess vectors according to hdiag
        #
        b = self.lf.create_one_index(dim)
        count = 0
        for ind in range(nguess):
            if ind >= dim:
                if log.do_medium:
                    log.warn(f"Maximum number of guess vectors reached: {dim}")
                break
            b.clear()
            b.set_element(sortedind[ind], 1)
            if todisk:
                b_v = IOData(vector=b)
                filename = filemanager.temp_path(f"bvector_{ind}.h5")
                b_v.to_file(filename)
                count += 1
            else:
                # have to append a copy
                bvector.append(b.copy())
        if todisk:
            return None, count
        return bvector, len(bvector)

    def get_index_s(self, index):
        """Get index for single excitation."""
        b = index % self.occ_model.nactv[0]
        nacto = (
            self.occ_model.nacto[0]
            if self.occ_model.nactc[0] == 0
            else self.occ_model.nactc[0]
        )
        j = ((index - b) / self.occ_model.nactv[0]) % nacto
        return int(j), int(b)
