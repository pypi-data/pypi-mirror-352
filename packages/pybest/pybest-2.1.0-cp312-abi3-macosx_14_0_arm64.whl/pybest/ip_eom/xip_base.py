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
# 2025-02: unification of variables and type hints (Julian Świerczyński)

"""Ionization Potential Equation of Motion Coupled Cluster implementations

   Variables used in this module:
    :ncore:     number of frozen core orbitals
    :nocc:      number of occupied orbitals in the principal configuration
    :nacto:     number of active occupied orbitals in the principal configuration
    :nvirt:     number of virtual orbitals in the principal configuration
    :nactv:     number of active virtual orbitals in the principal configuration
    :nbasis:    total number of basis functions
    :nact:      total number of active orbitals (nacto+nactv)
    :alpha:     number of unpaired electrons; for alpha=0, the spin-integrated
                equations target all possible m_s=0 states (singlet, triplet,
                quintet), for alpha=1, m_s=1/2 states are accessible (doublet,
                quartet), for alpha=2, m_s=1 states (triplet, quintet), for
                alpha=3, m_s=3/2 states (quartet), and for alpha=4, m_s=2 states
                (quintet)
    :e_ip:      the energy correction for IP
    :civ_ip:    the CI amplitudes from a given EOM model
    :e_ref:     the total energy of the (CC) reference wave function
    :alpha:     number of unpaired electrons

   Indexing convention:
    :i,j,k,..: occupied orbitals of principal configuration
    :a,b,c,..: virtual orbitals of principal configuration
    :p,q,r,..: general indices (occupied, virtual)

Abbreviations used (if not mentioned in doc-strings):
 :L_pqrs: 2<pq|rs>-<pq|sr>
 :g_pqrs: <pq|rs>
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray

from pybest import filemanager
from pybest.cache import Cache
from pybest.exceptions import ArgumentError, NonEmptyData
from pybest.featuredlists import OneBodyHamiltonian, TwoBodyHamiltonian
from pybest.iodata import CheckPoint, IOData
from pybest.linalg import (
    DenseFourIndex,
    DenseLinalgFactory,
    DenseOneIndex,
    DenseOrbital,
    DenseThreeIndex,
    DenseTwoIndex,
    FourIndex,
    LinalgFactory,
    TwoIndex,
)
from pybest.log import log, timer
from pybest.occ_model import AufbauOccModel
from pybest.solvers.davidson import Davidson
from pybest.units import electronvolt, invcm
from pybest.utility import (
    check_options,
    split_core_active,
    transform_integrals,
    unmask,
    unmask_orb,
)


class RXIPCC(ABC):
    """Restricted Ionization Potential Equation of Motion Coupled Cluster base class

    Purpose:
    Determine the excitation energies from a given EOMCC model
    (a) Build the non-symmetric effective EOM Hamiltonian
    (b) Diagonalize EOM Hamiltonian

    Currently supported wavefunction models:
     * RpCCD (SIP, DIP)
     * CCD (SIP)
     * CCSD (SIP)
     * LCCD (SIP)
     * LCCSD (SIP)
     * fpCCD (SIP)
     * fpCCSD (SIP)
     * fpLCCD aka pCCD-LCCD (SIP)
     * fpLCCSD aka pCCD-LCCSD (SIP)

    """

    long_name = ""
    acronym = ""
    reference = ""
    order = ""
    alpha = -1

    def __init__(
        self,
        lf: DenseLinalgFactory,
        occ_model: AufbauOccModel,
        **kwargs: dict[str, Any],
    ):
        """
        **Arguments:**

        lf
            A LinalgFactory instance.

        occ_model
            The occupation model.
        """
        self._lf = lf
        self._denself = DenseLinalgFactory(lf.default_nbasis)
        # occ_model stores all information on nacto, nactv, ncore, etc.
        self._occ_model = occ_model
        # Cache instance to store effective Hamiltonian etc.
        self._cache = Cache()
        # e_core is not required to be assigned
        self._e_core = 0.0
        self._to_disk = False
        self._dump_cache = self._occ_model.nact[0] > 300
        self._checkpoint = CheckPoint({})
        self._checkpoint_fn = f"checkpoint_{self.acronym}.h5"
        # Spin-free implementation only for testing purposes
        self._spin_free = kwargs.get("spinfree", False)
        # Used only internally
        self._s_z = 0
        # Set number of holes
        self._nhole = None

        log.cite(
            "the (D)IP-EOM-pCCD-based methods",
            "boguslawski2021",
            "pandey2025",
        )
        log.cite(
            "IP-EOM-CC-based methods",
            "galynska2024",
        )

    @property
    def cache(self) -> Cache:
        """An Cache instance used to store auxiliary tensors"""
        return self._cache

    @property
    def dump_cache(self) -> bool:
        """Decide whether intermediates are dumped to disk or kept in memory"""
        return self._dump_cache

    @dump_cache.setter
    def dump_cache(self, new) -> None:
        self._dump_cache = new

    @property
    def lf(self) -> LinalgFactory:
        """The linalg factory"""
        return self._lf

    @property
    def denself(self) -> DenseLinalgFactory:
        """The dense linalg factory"""
        return self._denself

    @property
    def occ_model(self) -> AufbauOccModel:
        """The occupation model. Contains information about active occupied
        and virtual orbitals.
        """
        return self._occ_model

    @property
    def e_core(self) -> float:
        """Core energy"""
        return self._e_core

    @property
    def checkpoint(self) -> CheckPoint:
        """The iodata container that contains all data dump to disk"""
        return self._checkpoint

    @property
    def checkpoint_fn(self) -> str:
        """The filename that will be dumped to disk"""
        return self._checkpoint_fn

    @property
    def spin_free(self) -> dict[str, Any] | bool:
        """The spinfree implementation"""
        return self._spin_free

    @spin_free.setter
    def spin_free(self, new) -> None:
        self._spin_free = new

    @property
    def s_z(self) -> int:
        """The spin projection"""
        return self._s_z

    @s_z.setter
    def s_z(self, new: int) -> None:
        """Translate number of unpaired electrons `new` to spin projection"""
        mask = [0.0, 0.5, 1.0, 1.5, 2.0]
        self._s_z = mask[new]

    @property
    def to_disk(self) -> bool:
        """Davidson stores vectors on disk"""
        return self._to_disk

    @to_disk.setter
    def to_disk(self, new) -> None:
        self._to_disk = new

    @property
    def nhole(self) -> int | None:
        """The number of hole operators"""
        return self._nhole

    @nhole.setter
    @abstractmethod
    def nhole(self, new):
        raise NotImplementedError

    @property
    @abstractmethod
    def dimension(self):
        """Total number of unknowns of chosen IP model"""

    @abstractmethod
    def print_ci_vector(self, ci_dict):
        """Print eigenvectors for for various S_z"""

    @abstractmethod
    def print_weights(self, e_vec_j):
        """Print weights of R operators for various S_z"""

    @abstractmethod
    def compute_h_diag(self, *args):
        """Used by Davidson module for pre-conditioning"""

    @abstractmethod
    def build_subspace_hamiltonian(self, b_vector, h_diag, *args):
        """Used by the Davidson module to construct subspace Hamiltonian"""

    @abstractmethod
    def get_mask(self, select):
        """Get unique indices that are returned during diagonalization"""

    @abstractmethod
    def get_index_of_mask(self, select):
        """Get unique indices of mask to assign during diagonalization"""

    #
    # Cache operations
    #

    @abstractmethod
    def set_hamiltonian(self, mo1, mo2):
        """Saves blocks of the Hamiltonian to cache for a specific IP model
        from one (mo1) and two (mo2) electron integrals in the MO basis.
        """

    def from_cache(
        self, select: str
    ) -> tuple[Any, Literal[True]] | tuple[Any, Literal[False]] | Any:
        """Get a matrix/tensor from the cache.

        **Arguments:**

        select
            (str) some object stored in the Cache.
        """
        return self.cache.load(select)

    def init_cache(
        self, select: str, *args: Any, **kwargs: dict[str, Any]
    ) -> DenseOneIndex | DenseTwoIndex | DenseThreeIndex | DenseFourIndex:
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
        """Clear the Cache instance

        **Keyword arguments:**

        tags
            The tag used for storing some matrix/tensor in the Cache (default
            `h`).
        """
        for name in kwargs:
            check_options(name, name, "tags")
        tags = kwargs.get("tags", "h")

        self.cache.clear(tags=tags, dealloc=True)

    #
    # Functions used for I/O operations
    #

    def unmask_args(
        self, *args: Any, **kwargs: dict[str, Any]
    ) -> tuple[DenseTwoIndex | Any, DenseFourIndex | Any, list]:
        """Resolve arguments passed to function call"""
        #
        # olp
        #
        olp = unmask("olp", *args, **kwargs)
        if olp is None:
            raise ArgumentError(
                "Cannot find overlap integrals in IP function call."
            )
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
        #
        # t_1, t_p, t_2, etc. if not found, None is returned
        #
        t_1 = unmask("t_1", *args, **kwargs)
        t_p = unmask("t_p", *args, **kwargs)
        t_2 = unmask("t_2", *args, **kwargs)
        # if found, store amplitudes in checkpoint instance
        self.resolve_t({"t_1": t_1, "t_p": t_p, "t_2": t_2})
        return one, two, orbs

    #
    # Extracting model-specific T amplitudes from arguments
    #
    def resolve_t(self, t_dict: dict) -> None:
        """Resolve CC amplitudes and store them in the self.checkpoint
        instance. We store only the T amplitudes that are contained in a
        specific CC model.

        **Arguments:**

        args:
            (tuple of DenseIndexObjects) contains t_1, t_p, t_2, etc. amplitudes
        """
        mask = {
            "pCCD": ("t_p",),
            "CCD": ("t_2",),
            "CCSD": ("t_1", "t_2"),
            "LCCD": ("t_2",),
            "LCCSD": ("t_1", "t_2"),
            "fpCCD": ("t_2",),
            "fpCCSD": ("t_1", "t_2"),
            "fpLCCD": ("t_p", "t_2"),
            "fpLCCSD": ("t_1", "t_p", "t_2"),
        }
        for label in mask[self.reference]:
            if t_dict[label] is None:
                raise ArgumentError(f"Cannot find {label} amplitudes.")
            self.checkpoint.update(label, t_dict[label])
        # Store t_p as well
        if self.reference in ["CCD", "CCSD", "fpCCD", "fpCCSD"]:
            t_2 = self.checkpoint["t_2"]
            t_p = t_2.contract("abab->ab")
            self.checkpoint.update("t_p", t_p)

    @staticmethod
    def check_input(**kwargs) -> None:
        """Check input parameters passed as keyword arguments."""
        for name in kwargs:
            check_options(
                name,
                name,
                "threshold",
                "maxiter",
                "indextrans",
                "tolerance",
                "tolerancev",
                "nguessv",
                "maxvectors",
                "todisk",
                "spinfree",
                "nroot",
                "nhole",
                "dump_cache",
                "restart",
            )
        #
        # check number of roots
        #
        nroot = kwargs.get("nroot", 0)
        if nroot <= 0:
            raise ValueError("At least one root has to be calculated!")

    def print_info(self, **kwargs: dict[str, Any]) -> None:
        """Print some basic information"""
        nroot = kwargs.get("nroot", 0)
        if log.do_medium:
            log(" ")
            log("Entering IP-EOM-CC module")
            log(" ")
            log.hline("~")
            log(f"{self.acronym} framework selected")
            log.hline("~")
            log("OPTIMIZATION PARAMETERS:")
            log(f"Reference Function:            {self.reference}")
            log(f"Number of frozen cores:        {self.occ_model.ncore[0]}")
            log(f"Number of active occupied:     {self.occ_model.nacto[0]}")
            log(f"Number of active virtuals:     {self.occ_model.nactv[0]}")
            log(f"Number of hole operators:      {self.nhole}")
            log(f"Number of unpaired electrons:  {self.alpha}")
            log(f"Spin-free implementation:      {self.spin_free}")
            log(f"Number of roots:               {nroot}")
            log(f"Total number of roots:         {self.dimension}")
            log("Diagonalization:               Davidson")
            log("Tensor contraction engine:     automatic")
            log.hline("~")

    def print_results(self, **kwargs: dict[str, Any]) -> None:
        """Print output of final results

        **Keyword arguments:**

        threshold:
            (float) all CI coefficients above threshold are printed
        """
        log(f"Final results for spin projection {self.s_z}:")
        log(" ")

        threshold = kwargs.get("threshold", 0.1)
        e_vals = self.checkpoint[f"e_ip_{self.alpha}"]
        #
        # Enumerate through energy eigenvalues of all states
        #
        for ind, e_ip in enumerate(e_vals):
            # Read vectors from disk or from memory
            if self.to_disk:
                filename = filemanager.temp_path(f"evecs_{ind}.h5")
                v = IOData.from_file(str(filename))
                e_vec_j = v.vector
            else:
                e_vec_j = self.checkpoint[f"civ_ip_{self.alpha}"][:, ind]
            e_ip_tot = self.checkpoint["e_ref"] + e_ip.real
            log(
                f"Ionization energy:          {e_ip.real: e} [au]  /  "
                f"{e_ip.real / electronvolt: e} [eV]  /  "
                f"{e_ip.real / invcm: e} [cm-1]"
            )
            log(
                f"Energy of ionized state:    {e_ip_tot: 4.10f} [au]  /  "
                f"{e_ip_tot / electronvolt: 8.4f} [eV]  /  "
                f"{e_ip_tot / invcm: 8.3f} [cm-1]"
            )
            #
            # Sort CI vector for printing (only print elements above threshold)
            #
            ci_dict = self.sort_ci_vector(e_vec_j, threshold)
            #
            # Print solution
            #
            self.print_ci_vector(ci_dict)
            #
            # Print weights
            #
            self.print_weights(e_vec_j)

        log.hline()
        log.hline("=")

    @staticmethod
    def sort_ci_vector(
        e_vec_j: NDArray[np.float64], threshold: float
    ) -> OrderedDict:
        """Sort CI vector according the absolute value. Only elements above
        a threshold are considered during the sorting (in absolute value).

        **Returns:**
            an OrderedDict with indices as keys and CI coefficients as values
        """
        valid_inds = np.where(abs(e_vec_j[:]) > threshold)[0]
        e_vec_dict = {}
        for ind in valid_inds:
            e_vec_dict.update({ind: e_vec_j[ind]})

        sorted_e_vec = sorted(
            e_vec_dict.items(), key=lambda k: abs(k[1]), reverse=True
        )
        ordered_dict = OrderedDict(sorted_e_vec)

        return ordered_dict

    #
    # Indexing, ranges, etc.
    #

    def get_range(self, string: str, start: int = 0) -> dict:
        """Returns dictionary with keys beginX, endX, begin(X+1), etc.
        *  string - any sequence of 'o' (occupied) and 'v' (virtual)
        """
        range_ = {}
        ind = start
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

    def get_size(self, string: str) -> tuple:
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

    def transform_integrals(
        self,
        one_ao: DenseTwoIndex,
        two_ao: DenseFourIndex,
        mos: DenseOrbital,
        **kwargs,
    ) -> tuple[DenseTwoIndex, DenseFourIndex]:
        """Saves Hamiltonian terms in cache.

        Arguments:
        one_body_ham : DenseTwoIndex
            Sum of one-body elements of the electronic Hamiltonian in AO
            basis, e.g. kinetic energy, nuclei--electron attraction energy

        two_body_ham : DenseFourIndex
            Sum of two-body elements of the electronic Hamiltonian in AO
            basis, e.g. electron repulsion integrals.

        mos : DenseOrbital
            Molecular orbitals, e.g. RHF orbitals or pCCD orbitals.
        """
        indextrans = kwargs.get("indextrans", None)
        if self.occ_model.ncore[0] > 0:
            cas = split_core_active(
                one_ao,
                two_ao,
                mos,
                e_core=self.e_core,
                ncore=self.occ_model.ncore[0],
                nactive=self.occ_model.nact[0],
                indextrans=indextrans,
            )
            mo1 = cas.one
            mo2 = cas.two
        else:
            t_ints = transform_integrals(
                one_ao, two_ao, mos, indextrans=indextrans
            )
            mo1 = t_ints.one[0]
            mo2 = t_ints.two[0]

        return mo1, mo2

    # TODO: this desing choice breaks B027,
    # per > ruff rule B027
    # Empty methods in abstract base classes without an abstract decorator may be
    # be indicative of a mistake. If the method is meant to be abstract, add an
    # `@abstractmethod` decorator to the method.
    # NOTE: This function needs to be overwritten by anything that resets seniority sectors
    def set_seniority_0(self):  # noqa: B027
        """Set all seniority-0 elements of excitation amplitudes (iaia) to some value.

        **Arguments:**

        :other: DenseFourIndex object

        **Optional arguments:**

        :value: some Linalg object or some value to be assigned
        """

    # TODO: this desing choice breaks B027,
    # per > ruff rule B027
    # Empty methods in abstract base classes without an abstract decorator may be
    # be indicative of a mistake. If the method is meant to be abstract, add an
    # `@abstractmethod` decorator to the method.
    # NOTE: This function needs to be overwritten by anything that resets seniority sectors
    def reset_seniority_0(self):  # noqa: B027
        """Set all seniority-0 elements of excitation amplitudes (iaia) to some value.

        **Arguments:**

        :other: DenseFourIndex object

        **Optional arguments:**

        :value: some Linalg object or some value to be assigned
        """

    #
    # Functions required for diagonalization
    #

    def build_guess_vectors(self, nguess: int, to_disk: bool, *args: Any):
        """
        Build (orthonormal) set of guess vectors for each root.
        Search space contains excitations according to increasing values of
        h_diag. This function is used by the Davidson module and the same for
        all XIP models.

        **Arguments:**

        nguess
            Total number of guess vectors. If nguess is larger than the
            amount of degrees of freedom, nguess is automatically reduced

        to_disk
            if True vectors are stored to disk to files
            {filemanager.temp_dir}/b_vector_#int.h5

        args
            Contains diagonal approximation to Hamiltonian labeled as h_diag
            (OneIndex object)
        """
        b_vector = []
        dim = self.dimension
        h_diag = unmask("h_diag", *args)
        if h_diag is None:
            raise ArgumentError(
                "Cannot find diagonal approximation to Hamiltonian."
            )
        sortedind = h_diag.sort_indices(True)
        #
        # Construct guess vectors according to h_diag
        #
        guess_v = self.lf.create_one_index(dim)
        count = 0
        for ind in range(nguess):
            if ind >= dim:
                if log.do_medium:
                    log.warn(f"Maximum number of guess vectors reached: {dim}")
                break
            guess_v.clear()
            guess_v.set_element(sortedind[ind], 1)
            if to_disk:
                dump_v = IOData(vector=guess_v)
                filename = filemanager.temp_path(f"b_vector_{ind}.h5")
                dump_v.to_file(filename)
                count += 1
            else:
                # have to append a copy
                b_vector.append(guess_v.copy())
        if to_disk:
            return None, count
        return b_vector, len(b_vector)

    @timer.with_section("XIPCC: Diagonalize")
    def diagonalize(self, **kwargs: dict[str, Any]) -> None:
        """
        Solve for eomham, return eigenvalues and eigenvectors (stored in
        IOData container of class)

        **Keywords:**

            Function uses the following keyword arguments:
             * nroot:       number of roots for each spin projection
             * tolerance:   tolerance for energies (default 1e-6)
             * tolerancev:  tolerance for eigenvectors (default 1e-5)
             * maxiter:     maximum number of iterations (default 200)
             * nguessv:     number of guess vectors (default 5 per root)
             * maxvectors:  maximum number of vectors in Davidson (default 20 per root)
             * restart:     filename for restart purposes (default "")
        """
        if log.do_medium:
            log("Starting diagonalization...")
            log.hline()
        #
        # Set default keyword arguments:
        #
        tol = kwargs.get("tolerance", 1e-6)
        tolv = kwargs.get("tolerancev", 1e-5)
        maxiter = kwargs.get("maxiter", 200)
        nroot = kwargs.get("nroot", 0)
        nguessv = kwargs.get("nguessv", 5 * nroot)
        maxvectors = kwargs.get("maxvectors", 20 * nroot)
        restart_fn = kwargs.get("restart", "")

        if log.do_medium:
            log(
                f"Starting diagonalization for {self.alpha} unpaired electrons"
            )
            log.hline()
        davidson = Davidson(
            self.lf,
            nroot,
            nguessv,
            maxiter=maxiter,
            tolerance=tol,
            tolerancev=tolv,
            maxvectors=maxvectors,
            skipgs=False,
            todisk=self.to_disk,
            restart_fn=restart_fn,
        )
        e_excitation, eigen_vector_real = davidson(self)

        self.checkpoint.update(f"e_ip_{self.alpha}", e_excitation[:nroot])
        self.checkpoint.update(
            f"civ_ip_{self.alpha}", eigen_vector_real[:, :nroot]
        )
        if not self.to_disk:
            self.checkpoint.update(
                f"civ_ip_{self.alpha}", eigen_vector_real[:, :nroot]
            )
        else:
            # Store 0 (float), otherwise we cannot dump to hdf5
            self.checkpoint.update(f"civ_ip_{self.alpha}", 0)

    @timer.with_section("XIPCC: call")
    def __call__(self, *args: Any, **kwargs: dict[str, Any]) -> IOData:
        """Solve the non-symmetric eigenvalue problem in IP-EOM

        Currently supported CC models:
         * RpCCD (SIP, DIP)
         * CCD (SIP)
         * CCSD (SIP)
         * LCCD (SIP)
         * LCCSD (SIP)
         * fpCCD (SIP)
         * fpCCSD (SIP)
         * fpLCCD aka pCCD-LCCD (SIP)
         * fpLCCSD aka pCCD-LCCSD (SIP)

        Currently supported CI operators:
         * spin-dependent hole operator (SIP, DIP)
         * spin-dependent hole-particle-hole operator (SIP, DIP)
         * spin-summed hole operator (SIP)
         * spin-summed hole-particle-hole operator (SIP)

        **Arguments:**

        args
            Contains various arguments: One- and two-body integrals
            (some Hamiltonian matrix elements) expressed in the AO basis,
            an IOData container containing the wave function information
            of the reference state (the AO/MO coefficients, CC amplitudes,
            etc.)

        **Keywords:**

            Contains the following keyword arguments:
             * nroot:       number of roots to target
             * tolerance:   tolerance for energies (default 1e-6)
             * tolerancev:  tolerance for eigenvectors (default 1e-5)
             * threshold:   printing threshold for amplitudes (default 0.1)
             * maxiter:     maximum number of iterations (default 200)
             * indextrans:  4-index Transformation (str). Choice between
                            ``tensordot`` (default), ``cupy``, ``einsum``,
                            ``cpp``, ``opt_einsum``, or ``einsum_naive``. If
                            ``cupy`` is not available, we switch to ``tensordot``.
             * nguessv:     number of guess vectors (default 5 per root)
             * maxvectors:  maximum number of vectors in Davidson (default 20 per root)
             * dump_cache:  dump effective Hamiltonian to disk if not needed
                            (default True if nact > 300). Only arrays that are
                            at least of size o^2v^2 are dumped. Thus, the keyword
                            has no effect if the IP model in question does not
                            feature any arrays of size o^2v^2 or larger. In each
                            Davidson step, these arrays are read from disk and
                            deleted from memory afterwards.
             * restart:     filename for restart purposes (default "")

        **Returns**

            An IOData container containing all results of the calculation
             * e_ip_{alpha}:    IP energies (wrt reference energy) for {alpha}
                                unpaired electrons
             * civ_ip_{alpha}:  Eigenvectors for each root of IP state for
                                {alpha} unpaired electrons
             * e_ref:           The total energy of the reference wave function
        """
        #
        # Check input parameters:
        #
        self.check_input(**kwargs)
        #
        # Set default keyword arguments used in call function:
        #
        # Choose optimal internal contraction schemes (select=None)
        self.s_z = self.alpha
        self.nhole = kwargs.get("nhole", None)
        self.to_disk = kwargs.get("todisk", self.to_disk)
        self.spin_free = kwargs.get("spinfree", self.spin_free)
        # Dump all intermediates to disk if number of active orbitals is
        # greater than 300
        self.dump_cache = kwargs.get(
            "dump_cache", (self.occ_model.nact[0] > 300)
        )
        #
        # Print method specific information
        #
        self.print_info(**kwargs)
        #
        # Unmask arguments
        #
        one, two, orbs = self.unmask_args(*args, **kwargs)
        #
        # Get total energy of reference state, store as e_ref
        #
        e_ref = unmask("e_tot", *args, **kwargs)
        self.checkpoint.update("e_ref", e_ref)
        #
        # Transform integrals:
        #
        mo1, mo2 = self.transform_integrals(one, two, orbs, **kwargs)
        #
        # Dump AO eri to save memory
        #
        two.dump_array(two.label)
        #
        # Set seniority sectors
        #
        self.set_seniority_0()
        #
        # Construct auxiliary matrices (checks also type of arguments):
        #
        if log.do_medium:
            log("Building effective Hamiltonian...")
        self.clear_cache()
        self.set_hamiltonian(mo1, mo2)
        if log.do_medium:
            log("...done.")
        #
        # Diagonalize for a specific S_z value
        #
        self.diagonalize(**kwargs)
        #
        # Do Checkpoint
        #
        self.checkpoint.to_file(self.checkpoint_fn)
        #
        # Print final results
        #
        if log.do_medium:
            self.print_results(**kwargs)
        #
        # Clean up and finish
        #
        self.clear_cache()
        #
        # Read again eri
        #
        two.load_array(two.label)
        #
        # reset seniority sectors
        #
        self.reset_seniority_0()

        return self.checkpoint()
