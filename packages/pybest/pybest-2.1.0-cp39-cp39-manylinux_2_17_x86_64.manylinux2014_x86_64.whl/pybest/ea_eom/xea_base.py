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
# 2024: Originally written by Katharina Boguslawski
# 2025: Set seniority zero sectors in T2 amplitudes (Saman Behjou)

"""Electron Affinity Equation of Motion Coupled Cluster implementations

   Variables used in this module:
    :ncore:     number of frozen core orbitals
    :nocc:      number of occupied orbitals in the principle configuration
    :nacto:     number of active occupied orbitals in the principle configuration
    :nvirt:     number of virtual orbitals in the principle configuration
    :nactv:     number of active virtual orbitals in the principle configuration
    :nbasis:    total number of basis functions
    :nact:      total number of active orbitals (nacto+nactv)
    :alpha:     the number of unpaired electrons, determines s_z
    :e_ea:      the energy correction for EA
    :civ_ea:    the CI amplitudes from a given EOM model
    :e_ref:     the total energy of the (CC) reference wave function

    Indexing convention:
     :i,j,k,..: occupied orbitals of principal configuration (alpha spin)
     :a,b,c,..: virtual orbitals of principal configuration (alpha spin)
     :p,q,r,..: general indices (occupied, virtual; alpha spin)
     :I,J,K,..: occupied orbitals of principal configuration (beta spin)
     :A,B,C,..: virtual orbitals of principal configuration (beta spin)
     :P,Q,R,..: general indices (occupied, virtual; beta spin)

This module has been written by:
2023: Katharina Boguslawski
"""

from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Any, Union

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
    DenseTwoIndex,
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


class RXEACC(ABC):
    """Restricted Electron Affinity Equation of Motion Coupled Cluster base class

    Purpose:
    Determine the excitation energies from a given EOMCC model
    (a) Build the non-symmetric EOM Hamiltonian
    (b) Diagonalize EOM Hamiltonian

    Currently supported wavefunction models:
     * R-EA-EOM-pCCD
     * R-DEA-EOM-pCCD

    """

    acronym = ""
    long_name = (
        "Restricted Electron Affinity Equation of Motion Coupled Cluster"
    )
    cluster_operator = ""
    particle_hole_operator = ""
    reference = ""
    order = ""
    alpha = -1

    def __init__(
        self,
        lf: LinalgFactory,
        occ_model: OccupationModel,
        **kwargs: dict[str, Any],
    ) -> None:
        """
        **Arguments:**

        lf
             A LinalgFactory instance.

        occ_model
             The occupation model.
        """
        self._lf = lf
        self._denself = DenseLinalgFactory(lf.default_nbasis)
        self._occ_model = occ_model
        self._cache = Cache()
        # e_core is not required to be assigned
        self._e_core = 0.0
        self._to_disk = False
        self._dump_cache = self._occ_model.nact[0] > 300
        self._checkpoint = CheckPoint({})
        self._checkpoint_fn = f"checkpoint_{self.order}EOM{self.reference}.h5"
        # Spin-free implementation only for testing purposes
        self._spin_free = kwargs.get("spinfree", False)
        # Used only internally
        self._s_z = 0
        # set number of particles
        self._n_particle_operator = None

    @property
    def cache(self) -> Cache:
        """A Cache instance used to store auxiliary tensors"""
        return self._cache

    @property
    def dump_cache(self) -> bool:
        """Decide whether intermediates are dumped to disk or kept in memory"""
        return self._dump_cache

    @dump_cache.setter
    def dump_cache(self, new: bool) -> None:
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
    def occ_model(self) -> OccupationModel:
        """The occupation model. It contains all information on the number of
        active occupied, virtual, and frozen core orbitals.
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
    def spin_free(self) -> bool:
        """The spin-free implementation"""
        return bool(self._spin_free)

    @spin_free.setter
    def spin_free(self, new: bool) -> None:
        self._spin_free = bool(new)

    @property
    def s_z(self) -> float:
        """The spin projection"""
        if self.alpha < 0:
            raise ValueError(
                f"Spin projection not supported for {self.alpha} unpaired electrons"
            )
        return self.alpha / 2.0

    @property
    def n_particle_operator(self) -> None:
        """The maximum number of particles defined in the R operator"""
        return self._n_particle_operator

    @n_particle_operator.setter
    @abstractmethod
    def n_particle_operator(self, new: int) -> None:
        """Set the maximum number of particle operators (method-dependent)"""

    @property
    def to_disk(self) -> bool:
        """Davidson stores vectors on disk"""
        return self._to_disk

    @to_disk.setter
    def to_disk(self, new: bool) -> None:
        self._to_disk = new

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Total number of unknowns of chosen EA model"""

    @abstractmethod
    def print_ci_vector(self, ci_dict: OrderedDict) -> None:
        """Print eigenvectors for various S_z"""

    @abstractmethod
    def print_weights(self, e_vec_j: NDArray[np.float64]) -> None:
        """Print weights of R operators for various S_z"""

    @abstractmethod
    def compute_h_diag(self, *args: Any) -> OneIndex:
        """Used by Davidson module for pre-conditioning"""

    @abstractmethod
    def build_subspace_hamiltonian(
        self, b_vector: DenseOneIndex, h_diag: DenseOneIndex, *args: Any
    ) -> DenseOneIndex:
        """Used by Davidson module to construct subspace Hamiltonian"""

    @abstractmethod
    def get_mask(self, select: bool) -> NDArray[np.integer]:
        """Get unique indices that are returned during diagonalization"""

    @abstractmethod
    def get_index_of_mask(
        self, select: bool
    ) -> tuple[NDArray[np.integer], ...]:
        """Get unique indices of mask to assign during diagonalization"""

    #
    # Cache operations
    #

    def clear_cache(self, **kwargs: dict[str, str]) -> None:
        """Clear objects stored in cache"""
        tags = kwargs.get("tags", "h")
        self.cache.clear(tags=tags, dealloc=True)

    def from_cache(
        self, select: str
    ) -> Union[OneIndex, TwoIndex, ThreeIndex, FourIndex]:
        """Get a matrix.

        **Arguments:**

        select
            any auxiliary matrix supported by each module.
        """
        return self.cache.load(f"{select}")

    def init_cache(
        self, select: str, *args: Any, **kwargs: dict[str, Any]
    ) -> Union[OneIndex, TwoIndex, ThreeIndex, FourIndex]:
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
            alloc = (self.denself.create_four_index, *args)
        # load into the cache
        matrix, new = self.cache.load(select, alloc=alloc, tags=tags)
        if not new:
            raise NonEmptyData(
                f"The Cache instance {select} already exists. "
                "Call clear prior to updating the Cache instance."
            )

        return matrix

    @abstractmethod
    def set_hamiltonian(
        self,
        mo1: DenseTwoIndex,
        mo2: FourIndex,
    ) -> None:
        """Compute effective Hamiltonian elements (not larger than o2v2),
        otherwise the ERI are stored

        **Arguments:**

        mo1, mo2
            One- and two-electron integrals (some Hamiltonian matrix
            elements) in the MO basis.
        """

    #
    # Some basic I/O operations
    #

    def unmask_args(self, *args: Any, **kwargs: dict[str, Any]) -> Any:
        """Resolve arguments passed to function call"""
        #
        # olp
        #
        olp = unmask("olp", *args, **kwargs)
        if olp is None:
            raise ArgumentError(
                "Cannot find overlap integrals in CC function call."
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
    def resolve_t(self, t_dict: dict[str, Any]) -> None:
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
        # store t_p as well
        if self.reference in ["CCD", "CCSD", "fpCCD", "fpCCSD"]:
            t_2 = self.checkpoint["t_2"]
            t_p = t_2.contract("abab->ab")
            self.checkpoint.update("t_p", t_p)

    @staticmethod
    def check_input(**kwargs: dict[str, Any]) -> None:
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
                "nparticle",
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
        log(" ")
        log("Entering EA-EOM-CC module")
        log(" ")
        log.hline("~")
        log(f"EOM-{self.reference} framework selected")
        log.hline("~")
        log("OPTIMIZATION PARAMETERS:")
        log(f"Reference Function:            {self.reference}")
        log(f"Number of frozen cores:        {self.occ_model.ncore[0]}")
        log(f"Number of active occupied:     {self.occ_model.nacto[0]}")
        log(f"Number of active virtuals:     {self.occ_model.nactv[0]}")
        log(f"Number of unpaired electrons:  {self.alpha}")
        log(f"Spin projection:               {self.s_z}")
        log(f"Number of particle operators:  {self.n_particle_operator}")
        log(f"Number of targeted roots:      {nroot}")
        log(f"Total number of roots:         {self.dimension}")
        log("Diagonalization:               Davidson")
        log(f"Dumping cache:                 {self.dump_cache}")
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
        e_vals = self.checkpoint[f"e_ea_{self.alpha}"]
        #
        # Enumerate through energy eigenvalues of all states
        #
        for ind, e_ea in enumerate(e_vals):
            # Read vectors from disk or from memory
            if self.to_disk:
                filename = filemanager.temp_path(f"evecs_{ind}.h5")
                v = IOData.from_file(str(filename))
                e_vec_j = v.vector
            else:
                e_vec_j = self.checkpoint[f"civ_ea_{self.alpha}"][:, ind]
            e_ea_tot = self.checkpoint["e_ref"] + e_ea.real
            log(
                f"Attachment energy:          {e_ea.real: e} [au]  /  "
                f"{e_ea.real / electronvolt: e} [eV]  /  "
                f"{e_ea.real / invcm: e} [cm-1]"
            )
            log(
                f"Energy of attached state:    {e_ea_tot: 4.8f} [au]  /  "
                f"{e_ea_tot / electronvolt: 8.4f} [eV]  /  "
                f"{e_ea_tot / invcm: 8.3f} [cm-1]"
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
        """Sort CI vector according to the absolute value. Only elements above
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

    def get_range(self, string: str, start: int = 0) -> dict[str, int]:
        """Return dictionary with keys beginX, endX, begin(X+1), etc.
        *  string - any sequence of 'o' (occupied), 'v' (virtual)
                    'V' (virtual, starting from index 0), and 'n' (active)
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

    def get_size(self, string: str) -> tuple[int, ...]:
        """Return list of arguments containing sizes of tensors

        **Arguments:**

        string -- string or int
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
        two_ao: FourIndex,
        mos: DenseOrbital,
        **kwargs: Any,
    ) -> tuple[DenseTwoIndex, FourIndex]:
        """Transform Hamiltonian terms into MO basis.

        Arguments:
        one_ao -- DenseTwoIndex
            Sum of one-body elements of the electronic Hamiltonian in AO
            basis, e.g., kinetic energy, nuclei--electron attraction energy

        two_ao -- DenseFourIndex or CholeskyFourIndex
            Sum of two-body elements of the electronic Hamiltonian in AO
            basis, e.g., electron repulsion integrals.

        mos -- DenseOrbital
            Molecular orbitals, e.g., RHF orbitals or pCCD orbitals.
        """
        indextrans = kwargs.get("indextrans", "tensordot")
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

    #
    # Diagonalize and call functions
    #
    @staticmethod
    def set_seniority_0(
        amplitudes: DenseFourIndex, value: Union[float, TwoIndex] = 0.0
    ) -> None:
        """Overwrite seniority zero amplitudes of t_2 with some value.

        **Arguments:**

        amplitudes:
            (dict) containing t_2 amplitudes

        value:
            (float or array or FourIndex) used to substitute seniority zero amplitudes
        """
        t_2 = amplitudes["t_2"]
        occ = t_2.nbasis
        vir = t_2.nbasis1
        ind1, ind2 = np.indices((occ, vir))
        indices = [ind1, ind2, ind1, ind2]
        t_2.assign(value, indices)

    def build_guess_vectors(
        self, nguess: int, to_disk: bool, *args: Any
    ) -> Union[tuple[None, int], tuple[list[OneIndex], int]]:
        """Build (orthonormal) set of guess vectors for each root.
        Search space contains excitations according to increasing values of
        Hdiag.

        nguess
             Total number of guess vectors. If nguess is larger than the
             amount of degrees of freedom, nguess is automatically reduced

        to_disk
             if True vectors are stored to disk to files
             {filemanager.temp_dir}/bvector_#int.h5
        """
        bvector = []
        dim = self.dimension
        #
        # Only H_diag is supported
        #
        h_diag = unmask("h_diag", *args)
        # Convert to list to manipulate elements
        sorted_indices = list(h_diag.sort_indices(True))
        #
        # Include a pre-defined number of R_a... vectors into the guess
        #
        for ind_a in range(min(nguess // 10, self.dimension)):
            # First, remove all occurances of [0, 1, ...]
            index_to_remove = sorted_indices.index(ind_a)
            sorted_indices.pop(index_to_remove)
            # Now, add (e.g., sorted_indeces[0] = 0)
            sorted_indices.insert(ind_a, ind_a)
        #
        # Construct guess vectors according to h_diag
        #
        b = self.lf.create_one_index(dim)
        count = 0
        for ind in range(nguess):
            if ind >= dim:
                if log.do_medium:
                    log.warn(f"Maximum number of guess vectors reached: {dim}")
                break
            b.clear()
            b.set_element(sorted_indices[ind], 1)
            if to_disk:
                bv = IOData(vector=b)
                filename = filemanager.temp_path(f"bvector_{ind}.h5")
                bv.to_file(filename)
                count += 1
            else:
                # have to append a copy
                bvector.append(b.copy())
        if to_disk:
            return None, count
        return bvector, len(bvector)

    @timer.with_section("EACC: Diagonalize")
    def diagonalize(self, *arg: Any, **kwargs: Any) -> None:
        """
        Solve for eomham, return eigenvalues and eigenvectors (stored in
        the IOData container of the class)

        **Arguments:**

        args
             Contains various arguments: One- and two-body integrals
             (some Hamiltonian matrix elements) expressed in the AO basis,
             an IOData container containing the wave function information
             of the reference state (the AO/MO coefficients, CC amplitudes,
             etc.)

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
        # Set default keyword arguements:
        #
        tol = kwargs.get("tolerance", 1e-6)
        tolv = kwargs.get("tolerancev", 1e-5)
        maxiter = kwargs.get("maxiter", 200)
        nroot = kwargs.get("nroot", 0)
        nguessv = kwargs.get("nguessv", 10 * nroot)
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
        e_excitation, eigen_vector_real = davidson(self, *arg)

        self.checkpoint.update(f"e_ea_{self.alpha}", e_excitation[:nroot])
        if not self.to_disk:
            self.checkpoint.update(
                f"civ_ea_{self.alpha}", eigen_vector_real[:, :nroot]
            )
        else:
            # Store 0 (float), otherwise we cannot dump to hdf5
            self.checkpoint.update(f"civ_ea_{self.alpha}", 0)

    @timer.with_section("EACC: call")
    def __call__(self, *args: Any, **kwargs: dict[str, Any]) -> IOData:
        """Solve the non-symmetric eigenvalue problem in EA-EOM-pCCD

        Currently supported CC models:
         * RpCCD

        Currently supported CI operators:
         * spin-dependent particle operator
         * spin-dependent particle-hole-particle operator

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
             * indextrans:  (str) 4-index transformation. One of ``einsum``,
                            ``tensordot`` (default ``tensordot``)
             * nguessv:     number of guess vectors (default 10 per root)
             * maxvectors:  maximum number of vectors in Davidson (default 20 per root)
             * todisk:      (boolean) if True, Davidson dumps vectors to disk
                            (very slow!; default ``False``)
             * dump_cache:  dump effective Hamiltonian to disk if not needed
                            (default True if nact > 300). Only arrays that are
                            at least of size o^2v^2 are dumped. Thus, the keyword
                            has no effect if the IP model in question does not
                            feature any arrays of size o^2v^2 or larger. In each
                            Davidson step, these arrays are read from disk and
                            deleted from memory afterward.
             * restart:     filename for restart purposes (default "")

        **Returns**

            An IOData container containing all results of the calculation
             * e_ea_{alpha}:    EA energies (wrt reference energy) for {alpha}
                                unpaired electrons
             * civ_ea_{alpha}:  Eigenvectors for each root of EA state for
                                {alpha} unpaired electrons
             * e_ref:           The total energy of the reference wave function
        """
        #
        # Check input parameters:
        #
        self.check_input(**kwargs)
        #
        # Set default keyword arguments:
        #
        self.to_disk = kwargs.get("todisk", self.to_disk)
        self.n_particle_operator = kwargs.get("nparticle")
        self.spin_free = kwargs.get("spinfree", self.spin_free)
        # Dump all intermediates to disk if number of active orbitals is
        # greater than 300
        self.dump_cache = kwargs.get("dump_cache", self.dump_cache)
        #
        # Get total energy of reference state, stored as e_ref
        #
        e_ref = unmask("e_tot", *args, **kwargs)
        self.checkpoint.update("e_ref", e_ref)
        #
        # Print method-specific information
        #
        if log.do_medium:
            self.print_info(**kwargs)
        #
        # Unmask arguments
        #
        one, two, orbs = self.unmask_args(*args, **kwargs)
        #
        # Transform integrals:
        #
        mo1, mo2 = self.transform_integrals(one, two, orbs, **kwargs)
        #
        # Set seniority sectors
        #
        if self.reference in ["fpLCCD", "fpLCCSD"]:
            t_p = self.checkpoint["t_p"]
            self.set_seniority_0(self.checkpoint, t_p)

        #
        # Dump AO eri to save memory
        #
        two.dump_array(two.label)
        #
        # Construct effective Hamiltonian
        #
        if log.do_medium:
            log("Building effective Hamiltonian...")
        self.set_hamiltonian(mo1, mo2)
        if log.do_medium:
            log("...done.")
        #
        # Diagonalize for specific Sz, no args required
        #
        self.diagonalize([], **kwargs)
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
        if self.reference in ["fpLCCD", "fpLCCSD"]:
            self.set_seniority_0(self.checkpoint, 0.0)

        return self.checkpoint()
