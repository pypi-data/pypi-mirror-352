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
"""Equation of Motion Coupled Cluster implementations of a base class for EOM with
single and double excitations.

Variables used in this module:
 :ncore:     number of frozen core orbitals
 :nocc:      number of occupied orbitals in the principle configuration
 :nacto:     number of active occupied orbitals in the principle configuration
 :nvirt:     number of virtual orbitals in the principle configuration
 :nactv:     number of active virtual orbitals in the principle configuration
 :nbasis:    total number of basis functions
 :nact:      total number of active orbitals (nacto+nactv)

 Indexing convention:
  :i,j,k,..: occupied orbitals of principle configuration
  :a,b,c,..: virtual orbitals of principle configuration
  :p,q,r,..: general indices (occupied, virtual)

 P^bc_jk performs a pair permutation, i.e., P^bc_jk o_(bcjk) = o_(cbkj)

 Abbreviations used (if not mentioned in doc-strings):
  :L_pqrs: 2<pq|rs>-<pq|sr>
  :g_pqrs: <pq|rs>
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np
from scipy import linalg as LA

from pybest import filemanager
from pybest.cache import Cache
from pybest.constants import CACHE_DUMP_ACTIVE_ORBITAL_THRESHOLD as CACHE_THR
from pybest.exceptions import ArgumentError, NonEmptyData
from pybest.featuredlists import OneBodyHamiltonian, TwoBodyHamiltonian
from pybest.iodata import CheckPoint, IOData
from pybest.linalg import (
    DenseFourIndex,
    DenseLinalgFactory,
    FourIndex,
    LinalgFactory,
    OneIndex,
    ThreeIndex,
    TwoIndex,
)
from pybest.log import log, timer
from pybest.occ_model.occ_base import OccupationModel
from pybest.solvers import Davidson
from pybest.units import electronvolt, invcm
from pybest.utility import (
    check_options,
    split_core_active,
    transform_integrals,
    unmask,
    unmask_orb,
)


class REOMCC(ABC):
    """Restricted Equation of Motion Coupled Cluster base class. Not intended
    to be used as a standalone class.

    Purpose:
    Determine the excitation energies from a given EOMCC model
    (a) Build the non-symmetruc EOM Hamiltonian
    (b) Diagonalize EOM Hamiltonian

    Currently supported wavefunction models:
     * REOM-pCCD
     * REOM-pCCD+S
     * REOM-pCCD-CCS
     * REOM-CCS
     * REOM-LCCD
     * REOM-LCCSD
     * REOM-pCCD-LCCD
     * REOM-pCCD-LCCSD
     * REOM-CCD
     * REOM-CCSD

    """

    long_name = ""
    acronym = ""
    reference = ""
    singles_ref = ""
    pairs_ref = ""
    doubles_ref = ""
    singles_ci = ""
    pairs_ci = ""
    doubles_ci = ""

    def __init__(self, lf: LinalgFactory, occ_model: OccupationModel):
        """
        **Arguments:**

        lf
             A LinalgFactory instance.

        occ_model
             The occupation model.

        """
        self._lf = lf
        self._dense_lf = DenseLinalgFactory(lf.default_nbasis)
        # Occupation model includes information of nacto, nactv, nact, etc.
        self._occ_model = occ_model
        # Intermediate Hamiltonian as an instance of Cache
        self._cache = Cache()
        self._dump_cache = self._occ_model.nact[0] > CACHE_THR
        # e_core is not required to be assigned
        self._e_core = 0.0
        self._omega = None
        self._gamma = None
        self._checkpoint = CheckPoint({})
        self._checkpoint_fn = f"checkpoint_{self.acronym}.h5"
        self._todisk = False
        # Include occupation model into checkpoint file (IOData container)
        self.checkpoint.update("occ_model", self.occ_model)

    @property
    def lf(self) -> LinalgFactory:
        """The linalg factory"""
        return self._lf

    @property
    def dense_lf(self) -> DenseLinalgFactory:
        """The dense linalg factory"""
        return self._dense_lf

    @property
    def cache(self) -> Cache:
        """The Cache instance used to store the intermediate Hamiltonian in
        memory
        """
        return self._cache

    @property
    def dump_cache(self) -> bool:
        """Decide whether intermediates are dumped to disk or kept in memory"""
        return self._dump_cache

    @dump_cache.setter
    def dump_cache(self, new: bool) -> None:
        self._dump_cache = new

    @property
    def occ_model(self) -> OccupationModel:
        """The occupation model"""
        return self._occ_model

    @property
    def e_core(self) -> float:
        """Core energy"""
        return self._e_core

    @property
    def omega(self) -> None:
        """Used in linear response module"""
        return self._omega

    @property
    def gamma(self) -> None:
        """Used in linear response module"""
        return self._gamma

    @property
    def checkpoint(self) -> CheckPoint:
        """The iodata container that contains all data dump to disk"""
        return self._checkpoint

    @property
    def checkpoint_fn(self) -> str:
        """The filename that will be dumped to disk"""
        return self._checkpoint_fn

    @property
    def todisk(self) -> bool:
        """Davidson dumps vectors to disk if True"""
        return self._todisk

    @todisk.setter
    def todisk(self, new: bool) -> None:
        if not isinstance(new, bool):
            raise ValueError("Option 'todisk' has to be of boolean type!")
        self._todisk = new

    @property
    def nroot(self) -> int:
        """Number of excited state roots to target. The ground state roots is also
        included (by the setter) as all EOM flavors do require it during the
        optimization
        """
        return self._nroot

    @nroot.setter
    def nroot(self, new: int) -> None:
        if not isinstance(new, int):
            raise ValueError("Option 'nroot' has to be of integer type!")
        if new <= 0:
            raise ValueError("Number of roots must be larger than 1!")
        # Add ground state to total number of roots
        self._nroot = new + 1

    @property
    @abstractmethod
    def dimension(self) -> int:
        """The number of unknowns (total number of excited states incl. ground
        state) for each EOM-CC flavor. Variable used by the Davidson module.
        """

    @abstractmethod
    def build_full_hamiltonian(self) -> TwoIndex:
        """Construct full Hamiltonian matrix used in exact diagonalization
        (expensive; supported only for some EOM flavours)
        """

    @abstractmethod
    def update_hamiltonian(self, mo1, mo2):
        """Update/Calculate all auxiliary matrices and tensors (intermediates).
        The actual matrices/tensors are method-specific.
        """

    @abstractmethod
    def print_ci_vectors(self, index: int, ci_vector: np.ndarray) -> None:
        """Print information on CI vector (excitation and its coefficient)."""

    @abstractmethod
    def print_weights(self, ci_vector: np.ndarray) -> None:
        """Print weights of excitations."""

    def unmask_args(self, *args: Any, **kwargs: Any) -> Any:
        """Extract all tensors/quantities from function arguments and keyword
        arguments. Arguments/kwargs may contain:
        * olp: overlap integrals
        * orb_a: orbitals
        * t_x: some CC amplitudes
        * one/two: one- and two-electron integrals
        """
        #
        # olp
        #
        olp = unmask("olp", *args, **kwargs)
        if olp is None:
            raise ArgumentError(
                "Cannot find overlap integrals in EOM-CC function call."
            )
        self.checkpoint.update("olp", olp)
        #
        # orb; we have to use unmask_orb here
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
        return one, two, orbs

    #
    # Cache operations
    #

    def clear_cache(self, **kwargs: dict[str, str]) -> None:
        """Clear some Cache instance

        **Keyword Arguments:**

        tags
             The tag used for storing some matrix/tensor in the Cache (default
             `h`).
        """
        for name in kwargs:
            check_options(name, name, "tags")
        tags = kwargs.get("tags", "h")

        self.cache.clear(tags=tags, dealloc=True)

    def from_cache(
        self, select: str
    ) -> OneIndex | TwoIndex | ThreeIndex | FourIndex:
        """Get some tensor from a Cache instance.

        **Arguments:**

        select
             any auxiliary object supported by each EOM-CC flavour.
        """
        return self.cache.load(select)

    def set_hamiltonian(self, mo1: TwoIndex, mo2: FourIndex) -> None:
        """Compute intermediate Hamiltonian and store it to some Cache instance

        **Arguments:**

        mo1, mo2
             One- and two-electron integrals (some Hamiltonian matrix
             elements) in the MO basis.
             List of arguments. Only geminal coefficients [1], one- [2] and
             two-body [3] integrals are used.

        """
        self.clear_cache()
        self.update_hamiltonian(mo1, mo2)

    def init_cache(
        self, select: str, *args: Any, **kwargs: Any
    ) -> OneIndex | TwoIndex | ThreeIndex | FourIndex:
        """Initialize some cache instance

        **Arguments:**

        select

            (str) label of the auxiliary tensor

        args
            The size of the auxiliary matrix in each dimension. The number of given
            arguments determines the order and sizes of the tensor.
            Either a tuple or a string (oo, vv, ovov, etc.) indicating the sizes.
            Not required if ``alloc`` is specified.

        **Keyword Arguments:**

        tags
            The tag used for storing some matrix/tensor in the Cache (default
            `h`).

        alloc
            Specify alloc function explicitly. If not defined some flavor of
            `self.lf.create_N_index` is taken depending on the length of args.

        nvec
            Number of Cholesky vectors. Only required if Cholesky-decomposed ERI
            are used. In this case, only ``args[0]`` is required as the Cholesky
            class does not support different sizes of the arrays.
        """
        for name in kwargs:
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
            alloc = (self.dense_lf.create_four_index, *args)
        # load into the cache
        matrix, new = self.cache.load(select, alloc=alloc, tags=tags)
        if not new:
            raise NonEmptyData(
                f"The Cache instance {select} already exists. "
                "Call clear prior to updating the Cache instance."
            )

        return matrix

    #
    # General utility functions
    #

    def check_input(self, **kwargs: Any) -> None:
        """Check input parameters."""
        for name in kwargs:
            check_options(
                name,
                name,
                "threshold",
                "davidson",
                "maxiter",
                "indextrans",
                "nroot",
                "tolerance",
                "tolerancev",
                "nguessv",
                "todisk",
                "maxvectors",
                "dump_cache",
                "restart",
            )
        self.todisk = kwargs.get("todisk", False)

    def print_info(self, **kwargs: Any) -> None:
        """Print initial information of the calculation"""
        dim = self.dimension
        davidson = kwargs.get("davidson", True)
        # Print only number of excited state roots
        nroot = self.nroot - 1
        if log.do_medium:
            log(" ")
            log("Entering EOM-CC module")
            log(" ")
            log.hline("~")
            log(f"{self.acronym} framework selected")
            log.hline("~")
            log("OPTIMIZATION PARAMETERS:")
            log(f"Reference function:                 {self.reference}")
            log(
                f"Number of frozen occupied orbitals: {self.occ_model.ncore[0]}"
            )
            log(
                f"Number of active occupied orbitals: {self.occ_model.nacto[0]}"
            )
            log(f"Total number of electrons:          {self.occ_model.nel}")
            log(
                f"Number of active electrons:         {self.occ_model.nacto[0] * 2}"
            )
            log(
                f"Number of active virtual orbitals:  {self.occ_model.nactv[0]}"
            )
            log(f"Number of roots:                    {nroot}")
            log(f"Total number of roots:              {dim}")
            if davidson:
                log("Diagonalization:                    Davidson")
            else:
                log(
                    "Diagonalization:                    Exact Diagonalization"
                )
            log("Tensor contraction engine:          automatic")
            log(f"Dumping cached arrays:              {self.dump_cache}")
            log.hline("~")

    def get_index_d(self, index: int) -> tuple[int, int, int, int]:
        """Get index for double excitation in dense representation from upper
        triangular block. Indices are returned for active orbitals only.
        """
        triu = np.triu_indices(
            self.occ_model.nacto[0] * self.occ_model.nactv[0]
        )
        row = triu[0][index]
        col = triu[1][index]
        i, a = self.get_index_s(row)
        j, b = self.get_index_s(col)
        return int(i), int(a), int(j), int(b)

    def get_index_s(self, index: int) -> tuple[int, int]:
        """Get index for single excitation. Indices are returned for active
        orbitals only.
        """
        b = index % self.occ_model.nactv[0]
        j = ((index - b) / self.occ_model.nactv[0]) % self.occ_model.nacto[0]
        return int(j), int(b)

    def set_seniority_0(
        self, other: DenseFourIndex, value: float | TwoIndex = 0.0
    ) -> DenseFourIndex:
        """Set all seniority-0 elements of excitation amplitudes (iaia) to some
        value.

        **Arguments:**

        :other: DenseFourIndex object

        **Optional arguments:**

        :value: some Linalg object or some value to be assigned
        """
        ind1, ind2 = np.indices(
            (self.occ_model.nacto[0], self.occ_model.nactv[0])
        )
        indices = [ind1, ind2, ind1, ind2]
        other.assign(value, indices)
        return other

    def get_range(self, string: str, offset: int = 0) -> dict[str, int]:
        """Returns dictionary with keys beginX, endX, begin(X+1), etc.
        *  string - any sequence of 'o' (occupied), 'v' (virtual)
                    'V' (virtual starting with index 0),
                    'n' (all active basis functions)
        """
        range_ = {}
        ind = offset
        for char in string:
            if char == "o":
                range_[f"begin{ind}"] = 0
                range_[f"end{ind}"] = self.occ_model.nacto[0]
            elif char == "v":
                range_[f"begin{ind}"] = self.occ_model.nacto[0]
                range_[f"end{ind}"] = self.occ_model.nact[0]
            elif char == "V":
                range_[f"begin{ind}"] = 0
                range_[f"end{ind}"] = self.occ_model.nactv[0]
            elif char == "n":
                range_[f"begin{ind}"] = 0
                range_[f"end{ind}"] = self.occ_model.nact[0]
            else:
                raise ValueError(f"Do not know how to handle choice {char}")
            ind += 1
        return range_

    def get_size(self, string: str) -> tuple[int, ...]:
        """Returns list of arguments containing sizes of tensors

        **Arguments:**

        string : string or int
            any sequence of "o" (occupied) and "v" (virtual) OR a tuple of
            integers indicating the sizes of an array
        """
        args = []
        for char in string:
            if char == "o":
                args.append(self.occ_model.nacto[0])
            elif char == "v":
                args.append(self.occ_model.nactv[0])
            elif isinstance(char, int):
                args.append(char)
            else:
                raise ArgumentError(f"Do not know how to handle size {char}.")
        return tuple(args)

    def print_results(self, threshold: float) -> None:
        """Print final results of the calculation"""
        e_vals = self.checkpoint["e_ee"]
        e_vecs = self.checkpoint["civ_ee"]
        if log.do_medium:
            log("Final results:")
            log(" ")
            for ind, e_val in enumerate(e_vals):
                #
                # Get ci vector
                #
                log(
                    f"Excitation energy:      {e_val.real: 20.8f} [au]  /  "
                    f"{e_val.real / electronvolt: e} [eV]  /  "
                    f"{e_val.real / invcm: e} [cm-1]"
                )
                if self.todisk:
                    filename = filemanager.temp_path(f"evecs_{ind}.h5")
                    v = IOData.from_file(str(filename))
                    e_vecs_j = v.vector
                else:
                    e_vecs_j = e_vecs[:, ind]
                kc = np.where(abs(e_vecs_j) > threshold)[0]
                for ind2 in kc:
                    #
                    # Print reference state
                    #
                    if ind2 == 0:
                        log(
                            f"             t_0:                      {e_vecs_j[ind2]: 1.5f}  "
                        )
                    #
                    # Print all remaining states
                    #
                    else:
                        self.print_ci_vectors(ind2, e_vecs_j)
                #
                # Print weights of single and double excitations
                #
                self.print_weights(e_vecs_j)
            log.hline()
            log.hline("=")

    #
    # Functions used for diagonalization
    #

    def build_guess_vectors(
        self, nguess: int, todisk: bool, *args: Any
    ) -> tuple[None, int] | tuple[list[OneIndex], int]:
        """Build (orthonormal) set of guess vectors for each root.
        Search space contains excitations according to increasing values of
        Hdiag.

        todisk
             if True vectors are stored to disk to files
             {filemanager.temp_dir}/bvector_#int.h5
        """
        bvector = []
        dim = self.dimension
        hdiag = unmask("h_diag", *args)
        if hdiag is None:
            raise ArgumentError(
                "Cannot find diagonal approximation to Hamiltonian."
            )
        sorted_ind = hdiag.sort_indices(True)
        #
        # Move CC reference state to be first element (this is required for
        # some EOM flavours)
        #
        np.delete(sorted_ind, np.where(sorted_ind == 0))
        np.insert(sorted_ind, 0, 0)
        #
        # Construct Guess vectors according to hdiag
        #
        b_v = self.lf.create_one_index(dim)
        count = 0
        for ind in range(nguess):
            if ind >= dim:
                if log.do_medium:
                    log.warn(f"Maximum number of guess vectors reached: {dim}")
                break
            b_v.clear()
            b_v.set_element(sorted_ind[ind], 1)
            if todisk:
                b_v_ = IOData(vector=b_v)
                filename = filemanager.temp_path(f"bvector_{ind}.h5")
                b_v_.to_file(filename)
                count += 1
            else:
                # have to append a copy
                bvector.append(b_v.copy())
        if todisk:
            return None, count
        return bvector, len(bvector)

    @timer.with_section("EOMCC: Diagonalize")
    def diagonalize(self, **kwargs: Any) -> None:
        """Solve for eomham, return eigenvalues and eigenvectors

        **Arguments:**

        arg
             The one- and two-electron integrals, overlap integrals, orbitals,
             and some IOData container containing the solution of the
             reference calculation

        **Keywords**

         :tofile: If True, Davidson diagonalization is performed by writing all
                  vectors to disk (very I/O intensive and thus slow)

         :tolerance: Optimization threshold in Davidson module for the energy

         :tolerancev: Optimization threshold in Davidson module for the CI
                      vectors

         :maxiter: Maximum number of Davidson iterations

         :davidson: If True, Davidson diagonalization is used

         :nroot: Number of excited state roots to target

         :nguessv: Number of guess vectors in Davidson diagonalization

         :maxvectors: Maximum number of Davidson vectors before subspace
                      collapse is performed

         :restart: Filename for restart purposes (default "")
        """
        if log.do_medium:
            log("Starting diagonalization...")
            log.hline()
        #
        # Set default keyword arguments:
        #
        tol = kwargs.get("tolerance", 1e-6)
        tolv = kwargs.get("tolerancev", 1e-4)
        maxiter = kwargs.get("maxiter", 200)
        davidson = kwargs.get("davidson", True)
        nguessv = kwargs.get("nguessv", None)
        maxvectors = kwargs.get("maxvectors", None)
        restart_fn = kwargs.get("restart", "")

        if davidson:
            davidson = Davidson(
                self.lf,
                self.nroot,
                nguessv,
                maxiter=maxiter,
                maxvectors=maxvectors,
                tolerance=tol,
                tolerancev=tolv,
                todisk=self.todisk,
                restart_fn=restart_fn,
            )
            e_excitation, eigen_vector_real = davidson(self, [])
        else:
            log("Building Hamiltonian matrix...")
            eom_ham = self.build_full_hamiltonian()
            log("...done")
            self.clear_cache()
            # Diagonalize using scipy
            e_excitation, eigen_vector_real = LA.eig(
                eom_ham.array,
                b=None,
                left=False,
                right=True,
                overwrite_a=False,
                overwrite_b=False,
                check_finite=True,
            )
            ind = np.argsort(e_excitation)
            e_excitation = e_excitation[ind].real
            eigen_vector_real = eigen_vector_real[:, ind].real

        self.checkpoint.update("e_ee", e_excitation[: self.nroot])
        if not self.todisk:
            self.checkpoint.update(
                "civ_ee", eigen_vector_real[:, : self.nroot]
            )
        else:
            # Store 0 (float), otherwise we cannot dump to hdf5
            self.checkpoint.update("civ_ee", 0)

    @timer.with_section("EOMCC: call")
    def __call__(self, *args: Any, **kwargs: Any) -> IOData:
        """Solve the non-symmetric eigenvalue problem in EOM-CC

        Currently supported wavefunction models (Psi_0):
         * RLCCD
         * RLCCSD
         * RpCCD
         * RpCCD-CCS
         * RpCCD-LCCD
         * RpCCD-LCCSD
         * RCCS
         * RCCD
         * RCCSD

        Currently supported CI operators:
         * Pair excitation operator
         * Single excitation operator
         * Double excitation operator

        **Arguments:**

        args
             One- and two-body integrals (some Hamiltonian matrix elements)
             expressed in the AO basis.
             It contains the AO/MO coefficients and the geminal coefficients
             (if Psi_0 = pCCD) as second arguement.

        **Keywords:**

             Contains reference energy and solver specific input parameters:
             * davidson:    default True
             * tolerance:   tolerance for energies (default 1e-6)
             * tolerancev:  tolerance for eigenvectors (default 1e-5)
             * threshold:   printing threshold for amplitudes (default 0.1)
             * maxiter:     maximum number of iterations (default 200)
             * indextrans:  4-index Transformation (str). Choice between
                            ``tensordot`` (default), ``cupy``, ``einsum``,
                            ``cpp``, ``opt_einsum``, or ``einsum_naive``. If
                            ``cupy`` is not available, we switch to ``tensordot``.
             * dump_cache:  dump effective Hamiltonian to disk if not needed
                            (default True if nact > 300). Only arrays that are
                            at least of size o^2v^2 are dumped. Thus, the keyword
                            has no effect if the IP model in question does not
                            feature any arrays of size o^2v^2 or larger. In each
                            Davidson step, these arrays are read from disk and
                            deleted from memory afterwards.
             * restart:     filename for restart purposes (default "")

        **Returns**

             An IOData instance containing all results of the EOM calculation

        """
        #
        # Check input parameters:
        #
        self.check_input(**kwargs)
        #
        # Set default keyword arguments:
        #
        thresh = kwargs.get("threshold", 0.1)
        indextrans = kwargs.get("indextrans", None)
        self.nroot = kwargs.get("nroot", 1)
        # Dump all intermediates to disk if number of active orbitals is
        # greater than CACHE_THR defined in constants.py
        self.dump_cache = kwargs.get(
            "dump_cache", (self.occ_model.nact[0] > CACHE_THR)
        )
        #
        # Unmask arguments
        #
        one, two, orbs = self.unmask_args(*args, **kwargs)
        #
        # Print method specific information
        #
        self.print_info(**kwargs)
        #
        # Transform integrals:
        #
        if self.occ_model.ncore[0] > 0:
            cas = split_core_active(
                one,
                two,
                orbs,
                e_core=self.e_core,
                ncore=self.occ_model.ncore[0],
                nactive=self.occ_model.nact[0],
                indextrans=indextrans,
            )
            mo1 = cas.one
            mo2 = cas.two
        else:
            t_i = transform_integrals(one, two, orbs, indextrans=indextrans)
            mo1 = t_i.one[0]
            mo2 = t_i.two[0]
        #
        # Dump ERI in AO basis to disk and delete array explicitly
        #
        two.dump_array("eri", "checkpoint_eri.h5")
        #
        # Construct auxiliary matrices (checks also type of arguments):
        #
        log("Building effective Hamiltonian...")
        self.set_hamiltonian(mo1, mo2)
        log("...done.")
        #
        # Diagonalize CI matrix
        #
        self.diagonalize(**kwargs)
        #
        # Do Checkpoint
        #
        self.checkpoint.to_file(self.checkpoint_fn)
        #
        # Print final results
        #
        self.print_results(thresh)
        #
        # Clean up and finish (remove from memory)
        #
        self.clear_cache()
        #
        # Read again eri (AOs)
        #
        two.load_array("eri", "checkpoint_eri.h5")

        return self.checkpoint()
