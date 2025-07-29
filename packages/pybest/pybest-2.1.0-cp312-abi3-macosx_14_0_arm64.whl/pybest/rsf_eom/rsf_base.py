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
# The RSF-CC sub-package has been originally written and updated by Aleksandra Leszczyk (see CHANGELOG)
# Its current version contains updates from the PyBEST developer team.
#
# 2023/24:
# This file has been written by Emil Sujkowski (original version)
#
# The RSFBase class was created as a base class for other flavors of RSF implementations such as MS2, MS1

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Any

import numpy as np
from numpy.typing import NDArray

from pybest import filemanager
from pybest.cache import Cache
from pybest.exceptions import ArgumentError
from pybest.iodata import CheckPoint, IOData
from pybest.linalg import (
    CholeskyLinalgFactory,
    DenseLinalgFactory,
    DenseOneIndex,
)
from pybest.log import log, timer
from pybest.occ_model import AufbauOccModel
from pybest.solvers.davidson import Davidson
from pybest.units import electronvolt, invcm
from pybest.utility import (
    check_options,
    unmask,
    unmask_onebody_hamiltonian,
    unmask_orb,
    unmask_twobody_hamiltonian,
)


class RSFBase(ABC):
    """A collection of reversed spin flip models and optimization routines.

    This is just a base class that serves as a template for
    specific implementations.
    """

    acronym = ""
    long_name = ""
    reference = ""

    def __init__(
        self,
        lf: DenseLinalgFactory | CholeskyLinalgFactory,
        occ_model: AufbauOccModel,
        **kwargs: Any,
    ) -> None:
        """
        **Arguments:**

        lf
            A LinalgFactory instance.

        occ_model
            The occupation model.
        """
        self._lf = lf
        self._occ_model = occ_model

        self._converged = False
        self._e_core = 0.0
        self._e_ref = 0.0
        self._filename = f"checkpoint_{self.acronym}.h5"
        self._maxiter = 100
        self._checkpoint = CheckPoint({})
        self._checkpoint_fn = f"checkpoint_{self.acronym}.h5"
        self.nroot = 1
        self.todisk = False

    @timer.with_section("RSFEOMCC")
    def __call__(self, *args: Any, **kwargs: Any) -> IOData:
        """Solve the non-symmetric eigenvalue problem in RSF-EOM-CC

        Currently supported wavefunction models (Psi_0):
         * RCCSD (Ms=0)

        Currently supported CI operators:
         * Double excitation operator (Ms=2)

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
             * indextrans: (str) 4-index transformation. One of ``einsum``,
                           ``tensordot`` (default ``tensordot``)
             * restart:     filename for restart purposes (default "")

        **Returns**

             An IOData instance containing all results of the EOM calculation

        """
        # Set default keyword arguments:
        self.nroot = kwargs.get("nroot", self.nroot)

        # Print some basic information
        self.print_info()

        # Unmask arguments
        orb_a = unmask_orb(*args)[0]
        one = unmask_onebody_hamiltonian(args)
        two = unmask_twobody_hamiltonian(args)
        # Change to rcc
        self.rcc_iodata = self.unmask_rcc(args)

        #
        # Get total energy of reference state, store as e_ref
        #
        e_ref = unmask("e_tot", *args, **kwargs)
        self.checkpoint.update("e_ref", e_ref)

        if hasattr(self.rcc_iodata, "t_p"):
            # set seniority 0
            self.set_seniority_0()

        self.cache = self.set_hamiltonian(one, two, orb_a)

        # Diagonalize CI matrix
        self.diagonalize(**kwargs)

        # Do Checkpoint
        self.checkpoint.to_file(self.checkpoint_fn)

        if log.do_medium:
            self.print_results(**kwargs)

        # Clean up and finish (remove from memory)
        self.clear_cache()

        # Read again eri (AOs)
        two.load_array("eri", "checkpoint_eri.h5")

        if hasattr(self.rcc_iodata, "t_p"):
            # reset seniority 0
            self.reset_seniority_0()

        return self.checkpoint()

    @property
    def e_ref(self) -> float:
        """The CC reference energy."""
        return self._e_ref

    @property
    def occ_model(self) -> AufbauOccModel:
        """The occupation model."""
        return self._occ_model

    @property
    def cache(self) -> Cache:
        """The Cache instance used to store the intermediate Hamiltonian in
        memory
        """
        return self._cache

    @cache.setter
    def cache(self, new: Cache) -> None:
        """Set cache, raises TypeError if argument is not a cache instance"""
        if not isinstance(new, Cache):
            raise TypeError(f"Expected a Cache instance, got {new} instead")
        self._cache = new

    @property
    def lf(self) -> DenseLinalgFactory | CholeskyLinalgFactory:
        """The LinalgFactory instance"""
        return self._lf

    @property
    def checkpoint(self) -> CheckPoint:
        """The IOdata container that contains all data dump to disk"""
        return self._checkpoint

    @property
    def checkpoint_fn(self) -> str:
        """The filename that will be dumped to disk"""
        return self._checkpoint_fn

    def set_seniority_0(self) -> None:
        """Set all seniority-0 elements of excitation amplitudes (iaia) to the
        pCCD pair amplitudes.

        **Arguments:**

        :other: DenseFourIndex object

        **Optional arguments:**

        :value: some Linalg object or some value to be assigned
        """
        t_p = self.rcc_iodata.t_p
        t_2 = self.rcc_iodata.t_2
        ind1, ind2 = np.indices(
            (self.occ_model.nacto[0], self.occ_model.nactv[0])
        )
        indices = [ind1, ind2, ind1, ind2]
        t_2.assign(t_p, indices)

    def reset_seniority_0(self) -> None:
        """Set all seniority-0 elements of excitation amplitudes (iaia) back to
        zero.

        **Arguments:**

        :other: DenseFourIndex object

        **Optional arguments:**

        :value: some Linalg object or some value to be assigned
        """
        t_2 = self.rcc_iodata.t_2
        ind1, ind2 = np.indices(
            (self.occ_model.nacto[0], self.occ_model.nactv[0])
        )
        indices = [ind1, ind2, ind1, ind2]
        t_2.assign(0.0, indices)

    def clear_cache(self, **kwargs: Any) -> None:
        """Clear the Cache instance

        **Keyword arguments:**

        tags
            The tag used for storing some matrix/tensor in the Cache (default
            `h`).
        """
        for name in kwargs:
            check_options(name, name, "tags")
        tags = kwargs.get("tags", "EOM")

        self.cache.clear(tags=tags, dealloc=True)

    def print_info(self) -> None:
        """Print initial information of the calculation"""
        dim = self.dimension
        occ_model = self.occ_model
        davidson = True
        # Print only number of excited state roots
        if log.do_medium:
            log(" ")
            log("Entering RSF-EOM-CC module")
            log(" ")
            log.hline("~")
            log(f"{self.acronym} framework selected")
            log.hline("~")
            log("OPTIMIZATION PARAMETERS:")
            log(f"Reference function:                 {self.reference}")
            log(f"Number of frozen occupied orbitals: {occ_model.ncore[0]}")
            log(f"Number of active occupied orbitals: {occ_model.nact[0]}")
            log(
                f"Total number of electrons: {' ' * 8}  {2 * occ_model.nacto[0]}"
            )
            log(f"Number of active electrons:         {2 * occ_model.nact[0]}")
            log(f"Number of active virtual orbitals:  {occ_model.nactv[0]}")
            log(f"Number of roots:                    {self.nroot - 1}")
            log(f"Total number of roots:              {dim}")
            if davidson:
                log("Diagonalization:                    Davidson")
            else:
                log(
                    "Diagonalization:                    Exact Diagonalization"
                )
            log.hline("~")

    def print_results(self, **kwargs: Any) -> None:
        """Print output of final results

        **Keyword arguments:**

        threshold:
            (float) all CI coefficients above threshold are printed
        """
        log(f"Final results for {self.alpha} unpaired electrons:")
        log(" ")

        threshold = kwargs.get("threshold", 0.1)
        e_vals = self.checkpoint[f"e_ee_{self.alpha}"]
        #
        # Enumerate through energy eigenvalues of all states
        #
        for ind, e_ee in enumerate(e_vals):
            # Read vectors from disk or from memory
            if self.todisk:
                filename = filemanager.temp_path(f"evecs_{ind}.h5")
                v = IOData.from_file(str(filename))
                e_vec_j = v.vector
            else:
                e_vec_j = self.checkpoint[f"civ_ee_{self.alpha}"][:, ind]
            e_ee_tot = self.checkpoint["e_ref"] + e_ee.real
            log(
                f"Excitation energy:          {e_ee.real: e} [au]  /  "
                f"{e_ee.real / electronvolt: e} [eV]  /  "
                f"{e_ee.real / invcm: e} [cm-1]"
            )
            log(
                f"Energy of excited state:    {e_ee_tot: 4.10f} [au]  /  "
                f"{e_ee_tot / electronvolt: 8.4f} [eV]  /  "
                f"{e_ee_tot / invcm: 8.3f} [cm-1]"
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
            log(" ")
        log.hline()
        log.hline("=")

    @staticmethod
    def sort_ci_vector(
        e_vec_j: NDArray[np.float64], threshold: float
    ) -> OrderedDict:
        """Sort CI vector according to the absolute value.
        Only elements above a threshold are considered during the sorting
        (in absolute value).


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

    def unmask_rcc(self, args: Any) -> IOData | None:
        """Return an instance of the IOData container that contains
        the output of coupled cluster calculation
        """
        for arg in args:
            if hasattr(arg, "t_1") or (
                hasattr(arg, "t_2") and hasattr(arg, "e_ref")
            ):
                self._e_ref = arg.e_ref
                return arg
        raise ArgumentError("The RCC amplitudes were not found!")

    @timer.with_section("RSF-EOM-CC-Diag")
    def diagonalize(self, **kwargs: Any) -> None:
        """Solve for rsfeomham, return eigenvalues and eigenvectors

        **Keywords**

         :todisk: If True, Davidson diagonalization is performed by writing all
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

         :restart: filename for restart purposes (default "")
        """
        if log.do_medium:
            log("Starting diagonalization...")
            log.hline()

        # Set default keyword arguments:
        tol = kwargs.get("tolerance", 1e-8)
        tolv = kwargs.get("tolerancev", 1e-4)
        maxiter = kwargs.get("maxiter", 200)
        davidson = kwargs.get("davidson", True)
        nguessv = kwargs.get("nguessv", 5 * self.nroot)
        maxvectors = kwargs.get("maxvectors", 20 * self.nroot)
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
                skipgs=False,
                restart_fn=restart_fn,
            )
            e_excitation, eigen_vector_real = davidson(self, [])
        else:
            raise NotImplementedError(
                "Exact diagonalization is not implemented. Come back later."
            )

        self.checkpoint.update(
            f"e_ee_{self.alpha}", e_excitation[: self.nroot]
        )
        if not self.todisk:
            self.checkpoint.update(
                f"civ_ee_{self.alpha}", eigen_vector_real[:, : self.nroot]
            )
        else:
            # Store 0 (float), otherwise we cannot dump to hdf5
            self.checkpoint.update("civ_ee_{self.alpha}", 0)

    def build_guess_vectors(
        self, nguess: int, todisk: bool, *args: Any
    ) -> tuple[None, int] | tuple[list[DenseOneIndex], int]:
        """Build (orthonormal) set of guess vectors for each root.
        Search space contains excitations according to increasing values of
        Hdiag.

        nguess:
            number of guess vectors (int)

        todisk
             if True vectors are stored to disk to files
             {filemanager.temp_dir}/bvector_#int.h5
        """
        dim = self.dimension
        if nguess > dim and log.do_medium:
            log.warn(f"The number of guess vectors has been set to {dim}.")
            nguess = dim

        bvectors = []
        hdiag = unmask("h_diag", *args)
        if hdiag is None:
            raise ArgumentError(
                "Cannot find diagonal approximation to Hamiltonian."
            )

        sorted_ind = hdiag.sort_indices(True)
        vector = DenseOneIndex(dim)

        for num, index in enumerate(sorted_ind):
            if num >= nguess:
                break
            vector.clear()
            vector.set_element(index, 1.0)
            if todisk:
                filename = filemanager.temp_path(f"bvector_{num}.h5")
                IOData(vector=vector).to_file(filename)
            else:
                # have to append a copy
                bvectors.append(vector.copy())

        if todisk:
            return None, nguess
        return bvectors, len(bvectors)

    @abstractmethod
    def print_ci_vector(self, ci_dict: OrderedDict) -> None:
        """Print eigenvectors for various S_z

        Args:
            ci_dict (OrderedDict): composite index as key, CI vector as value
        """

    @abstractmethod
    def print_weights(self, e_vec_j: NDArray[np.float64]) -> None:
        """Print weights of R operators for various S_z

        Args:
            e_vec_j (np.ndarray): The eigenvector array whose weights will be printed.
        """

    @abstractmethod
    def set_hamiltonian(self, ham_1_ao, ham_2_ao, mos):
        """Saves Hamiltonian terms in cache."""

    @abstractmethod
    def compute_h_diag(self, *args):
        """Used by Davidson module for pre-conditioning."""

    @abstractmethod
    def build_subspace_hamiltonian(self, bvector, hdiag, *args):
        """
        Used by Davidson module to construct subspace Hamiltonian. Includes all
        terms that are similar for all RSF-EOM flavors.
        """
