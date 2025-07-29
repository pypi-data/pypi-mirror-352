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
"""Optimization methods

Davidson diagonalization
"""

from __future__ import annotations

from typing import Any

import numpy as np
import scipy
from numpy.typing import NDArray

from pybest import filemanager
from pybest.exceptions import ArgumentError, UnknownOption
from pybest.iodata import CheckPoint, IOData
from pybest.linalg import LinalgFactory, OneIndex, TwoIndex
from pybest.log import log, timer

__all__ = [
    "Davidson",
]


class Davidson:
    """Davidson diagonalization to perform an iterative diagonalization.
    Determines the eigenvalues and right eigenvectors of a (non)symmetric
    matrix.

    Raises:
        UnknownOption: If number of roots (< 0) or iterations (< 0) is unreasonable
        ArgumentError: If Davidson vectors are of wrong type (list, array, None)
        AttributeError:  If acronym (class attribute) is nowhere defined

    Returns:
        np.array, float: the eigenvectors and eigenvalues (real parts only)
    """

    acronym = "Davidson"

    def __init__(
        self,
        lf: LinalgFactory,
        nroots: int,
        nguess: int | None = None,
        maxiter: int = 200,
        tolerance: float = 1e-6,
        tolerancev: float = 1e-4,
        maxvectors: int | None = None,
        skipgs: bool = True,
        todisk: bool = True,
        restart_fn: str = "",
    ) -> None:
        """Davidson Diagonalizer
        Diagonalizes a (non)symmetric matrix and returns the (right)
        eigenvectors.
        Matrix of search space is constructed on-the-fly and must be defined in
        ``build_subspace_hamiltonian`` as a class method.
        To use this class, one needs to define four functions/properties:

        - ``build_subspace_hamiltonian``: computes A.b (function)
        - ``build_guess_vectors``: generates b_0 (or a list thereof; function)
        - ``compute_h_diag``: computes A_ii (used as pre-conditioner; function)
        - ``dimension``: the number of unknowns (property)

        Args:
            lf (LinalgFactory): the linalg factory instance used
            nroots (int): number of roots to target
            nguess (int | None, optional): number of guess vectors. Defaults to None.
            maxiter (int, optional): number of Davidson steps. Defaults to 200.
            tolerance (float, optional): convergence threshold for energy.
                                         Defaults to 1e-6.
            tolerancev (float, optional): convergence threshold for residual.
                                          Defaults to 1e-4.
            maxvectors (int | None, optional): maximum number of Davidson vectros
                                               before subspace collapse is performed.
                                               Defaults to None.
            skipgs (bool, optional): Do not print first root. Defaults to True.
            todisk (bool, optional): Save all vectors to disk during diagonalizatoin.
                                     Defaults to True.
            restart_fn (str, optional): name of restart file. If specified, guess
                                        vectors are read from file instead.
                                        Defaults to "" (no restart).

        Raises:
            UnknownOption: If number of roots (< 0) or iterations (< 0) is unreasonable

        Returns:
            eigval (np.ndarray):   eigenvalues
            eigvec (np.ndarray):   eigenvectors
        """
        #
        # Set private attributes (fixed during execution)
        #
        self._lf = lf
        if maxiter < 0:
            raise UnknownOption("Number of iterations has to be positive.")
        self._maxiter = maxiter
        self._tol = tolerance
        self._tolv = tolerancev
        if nroots < 0:
            raise UnknownOption("Number of roots has to be positive.")
        self._nroots = nroots
        self._skipgs = skipgs
        self._todisk = todisk
        #
        # Set number of guess vectors if not defined by user
        #
        if nguess is None:
            nguess = int((nroots - 1) * 4 + 1)
        if maxvectors is None:
            maxvectors = int(nroots - 1) * 10
        self._nguess = nguess
        self._maxvectors = maxvectors
        self.nbvector = 0
        self.nsigmav = 0
        # Restart option
        self._restart_fn = restart_fn
        #
        # Davidson-internal checkpointing (to make restarts possible)
        #
        self._checkpoint = CheckPoint({})

    @property
    def lf(self) -> LinalgFactory:
        """The linalg factory"""
        return self._lf

    @property
    def maxiter(self) -> int:
        """The maximum number of Davidson steps"""
        return self._maxiter

    @property
    def tol(self) -> float:
        """The convergence threshold for the energy"""
        return self._tol

    @property
    def tolv(self) -> float:
        """The convergence threshold for the wave function"""
        return self._tolv

    @property
    def nroots(self) -> int:
        """The total number of roots to target"""
        return self._nroots

    @property
    def skipgs(self) -> bool:
        """
        Skip printing information of ground state wave function/lowest root
        (boolean)
        """
        return self._skipgs

    @property
    def todisk(self) -> bool:
        """Write sigma and b vectors to disk (boolean)"""
        return self._todisk

    @property
    def nguess(self) -> int:
        """The total number of guess vectors"""
        return self._nguess

    @property
    def maxvectors(self) -> int:
        """The maximum number of Davidson vectors before subspace collapse"""
        return self._maxvectors

    @property
    def nbvector(self) -> int:
        """The number of b vectors used to construct the subspace Hamiltonian"""
        return self._nbvector

    @nbvector.setter
    def nbvector(self, new: int) -> None:
        self._nbvector = new

    @property
    def nsigmav(self) -> int:
        """The number of sigma vectors used to construct the subspace Hamiltonian"""
        return self._nsigmav

    @nsigmav.setter
    def nsigmav(self, new: int):
        self._nsigmav = new

    @property
    def checkpoint(self) -> CheckPoint:
        """The iodata container that contains all data dump to disk"""
        return self._checkpoint

    @property
    def restart_fn(self) -> str:
        """The filename used to perform restarts"""
        return self._restart_fn

    def read_from_disk(
        self, inp: np.ndarray | list | None, select: str, ind: int
    ) -> OneIndex | np.ndarray | ArgumentError:
        """Reads input vectors from disk if inp is None, otherwise it returns
        element inp[ind] from list

        Args:
            inp (np.ndarray | list | None): the list of vectors containing the
                                            vector of interest
            select (str): the name of the vector stored on disk
            ind (int): the element/root to be accessed from the list of vectors

        Raises:
            ArgumentError: If type of b vectors cannot be handled

        Returns:
            OneIndex | np.ndarray | ArgumentError: The current b_ind vector taken from [b_0, b_1, ...]
        """
        if inp is None:
            fname = f"{select}_{ind}.h5"
            filename = filemanager.temp_path(fname)
            bv = IOData.from_file(filename)
            return bv.vector
        elif isinstance(inp, list):
            return inp[ind]
        elif isinstance(inp, np.ndarray):
            return inp[:, ind]
        else:
            raise ArgumentError("Do not know how to handle input")

    def push_vector(
        self,
        inp: np.ndarray | list | None,
        new: np.ndarray | OneIndex,
        select: str,
        ind: int,
    ) -> None | np.ndarray | list[np.ndarray] | ArgumentError:
        """Appends new vector to list of previous vectors inp.
        If inp is None, vector is pushed to disk.

        Args:
            inp (np.ndarray | list | None): list of vectors to be updated
            new (np.ndarray | OneIndex): the new vector to be added
            select (str): the name of vectors stored on disk
            ind (int): the index of the new vector to be stored

        Raises:
            ArgumentError: If type of b vectors cannot be handled

        Returns:
            None | np.ndarray | list[np.ndarray] | ArgumentError: updated list/array of vectors
        """
        if inp is None:
            fname = f"{select}_{ind}.h5"
            filename = filemanager.temp_path(fname)
            v = IOData(vector=new)
            v.to_file(filename)
            v = None
            return None
        elif isinstance(inp, np.ndarray):
            inp[:, ind] = new[:]
        elif isinstance(inp, list):
            inp.append(new)
        else:
            raise ArgumentError("Do not know how to handle input")
        return inp

    def reset_vector(
        self, inp: None | np.ndarray | list[np.ndarray]
    ) -> None | list[np.ndarray] | np.ndarray:
        """Resets input vectors to empty list. If vectors are dump to disk,
        returns None.

        Args:
            inp (None | np.ndarray | list[np.ndarray]): the list of vectors to
                                                        be deleted/reset

         Raises:
            ArgumentError: if vectors are of unsupported type

        Returns:
            None | list[np.ndarray] | np.ndarray: cleaned list/array of vectors
        """
        if inp is None:
            return None
        elif isinstance(inp, np.ndarray):
            inp[:] = 0.0
        elif isinstance(inp, list):
            inp = []
        else:
            raise ArgumentError("Do not know how to handle input")
        return inp

    def normalize_correction_vector(
        self, inp: None | np.ndarray, dim: int
    ) -> None | np.ndarray:
        """Normalize vectors using QR.
        If vectors are stored to disk, we read them in first and store solution
        vectors to disk.

        Args:
            inp (None | np.ndarray): vectors to be normalized
            dim (int): the dimension of each vector

        Raises:
            ArgumentError: if vectors are of unsupported type

        Returns:
            None | np.ndarray: np.ndarray of normalized vectors
        """
        if inp is None:
            #
            # Use GS instead of np.qr to save memory
            #
            for j in range(self.nroots):
                bj = self.lf.create_one_index(dim)
                evecj = self.read_from_disk(None, "residual", j)
                bj.assign(evecj)
                if j != 0:
                    bjortho = self.gramschmidt(
                        None, bj, j, "residualortho", threshold=0.0
                    )
                    if bjortho is not None:
                        self.push_vector(None, bjortho, "residualortho", j)
                    bjortho = None
                else:
                    normbj = bj.norm()
                    if normbj > 0.0:
                        bj.iscale(1.0 / normbj)
                    else:
                        bj.clear()
                        bj.set_element(0, 1.0)
                    self.push_vector(None, bj, "residualortho", j)
            bj = None
            evecj = None
            return None
        elif isinstance(inp, np.ndarray):
            deltak, _ = np.linalg.qr(inp.real)
        else:
            raise ArgumentError("Don't know how to handle input vectors")
        return deltak

    #   def check_real(self, eigval, eigvec):
    def sort_eig(
        self, eigval: np.ndarray, eigvec: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """Sort eigenvalues and eigenvectors

        Args:
            eigval (np.ndarray): the eigenvalues to be sorted
            eigvec (np.ndarray): the eigenvectors to be sorted

        Returns:
            tuple[np.ndarray, np.ndarray]: sorted np.ndarrays of eigenvalues
                                           and eigenvectors
        """
        idx = eigval.argsort()
        esort = eigval[idx]
        vsort = eigvec[:, idx]
        #
        # Right now, simply push them up in the spectrum to improve convergence
        #
        (imag_,) = np.where(esort.imag)
        if not np.isreal(eigval).all():
            if np.amin(imag_) < self.nroots:
                for i in range(self.nroots):
                    if abs(esort[i].imag) > 1e-4:
                        log(
                            f"Imaginary eigenvalues found for root {i}. "
                            f"Taking only real part."
                        )
            if log.do_high:
                log(f"Imaginary eigenvalues found for roots {imag_}.")
                log("Eigenvalue spectrum:")
                log(f"{*esort, }")
        for i in imag_:
            esort[i] = esort[i].real

        #
        # Get all (almost) degenerate states and orthogonalize them
        #
        _ue, uind, uinv, _ucount = np.unique(
            esort.round(decimals=6), True, True, True
        )
        for i in range(len(esort)):
            if i not in uind:
                deg = uind[uinv[i]]
                log(
                    f"Orthogonalization of (almost) degenerate vectors {i} {deg}"
                )
                v1 = vsort[:, deg]
                #
                # Degenerate eigenvalues should show up as complex conjugate pairs
                #
                if np.allclose(vsort[:, deg], vsort[:, i].conjugate()):
                    if log.do_high and deg < self.nroots:
                        log(
                            f"norm of real part, norm of imaginary part: "
                            f"{np.linalg.norm(vsort[:, deg].real, ord=2)}, "
                            f"{np.linalg.norm(vsort[:, deg].imag, ord=2)}"
                        )
                    v1 = vsort[:, deg].real
                    v2 = vsort[:, deg].imag
                else:
                    v2 = vsort[:, i]
                proj = np.dot(v1.conjugate(), v2) / np.dot(v1, v1.conjugate())
                v2 = v2[:] - v1[:] * proj
                vsort[:, deg] = v1 / np.linalg.norm(v1, ord=2)
                vsort[:, i] = v2 / np.linalg.norm(v2, ord=2)
                if log.do_high:
                    if not np.isreal(vsort[:, deg]).all():
                        log(
                            f"Imaginary part of eigenvector non-zero {vsort[:, deg]}"
                        )
                    if not np.isreal(vsort[:, i]).all():
                        log(
                            f"Imaginary part of eigenvector non-zero {vsort[:, i]}"
                        )
                    if deg < self.nroots:
                        log(
                            f"root {deg} (after normalization) {*vsort[:, deg], }"
                        )
                        log(f"root {i} (after normalization) {*vsort[:, i], }")
                v1 = None
                v2 = None

        return esort.real, vsort.real

    def build_guess_vectors(
        self, obj: Any, *args: Any
    ) -> list[Any | OneIndex]:
        """Build (orthonormal) set of guess vectors for each root

        Calls method-dependent function defined in class obj to construct
        optimal guess vector of the search space.

        If self.todisk is True, subroutine has to store vectors to
        {filemanager.temp_dir}/bvector_#int.h5

        Args:
            obj (Any): an instance of some method class containing all method-
                       specific implementations (h_diag, subspace hamiltonian,
                       dimension)

        Returns:
            list[Any | OneIndex]: List of OneIndex instances (guess vectors)
        """
        if self.restart_fn != "":
            # Read data from disk
            restart_data = IOData.from_file(self.restart_fn)
            # Get civ_[...] attribute in restart file
            # We assume that all vectors are stored in some civ_[...] attribute
            h5_group = None
            for attr in dir(restart_data):
                # We will take just the last of them as PyBEST dumps each
                # method to a separate checkpoint file
                if attr.find("civ") != -1:
                    h5_group = attr
            # Raise error if restart data has not been found
            if h5_group is None:
                raise ArgumentError(
                    f"Could not find restart data in {self.restart_fn}"
                )
            civ = getattr(restart_data, h5_group)
            # Normalize vectors (just to make sure, otherwise algorithm breaks)
            if civ.ndim > 1:
                civ, _ = np.linalg.qr(civ.real)
            # Update number of guess vectors and current number of bvectors
            self._nguess = 1 if civ.ndim == 1 else civ.shape[1]
            self.nbvector = 1 if civ.ndim == 1 else civ.shape[1]
            # Occupy guess vectors with old solution
            bvector = []
            for i in range(self.nbvector):
                b_v = self.lf.create_one_index(civ.shape[0])
                civ_ = civ if civ.ndim == 1 else civ[:, i]
                b_v.assign(civ_)
                bvector.append(b_v)
            return bvector
        bvector, nvec = obj.build_guess_vectors(
            self.nguess, self.todisk, *args
        )
        self.nbvector = nvec
        return bvector

    def compute_h_diag(self, obj: Any, *args: Any) -> OneIndex:
        """Calculate the diagonal elements of the matrix to be diagonalized.
        Function is defined in obj class and can take function arguments args.

        Args:
            obj (Any): an instance of some obj class (some QM method)

        Returns:
            OneIndex: the diagonal part of the matrix to be diagonalized
        """
        return obj.compute_h_diag(*args)

    def build_subspace_hamiltonian(
        self,
        obj: Any,
        bvector: list[OneIndex],
        hdiag: OneIndex,
        sigma: list[OneIndex] | None,
        hamsub: TwoIndex,
        *args: Any,
    ) -> tuple[TwoIndex, list[OneIndex] | None]:
        """Build subspace Hamiltonian of search space defined in obj class.
        Can take function arguments args.

        Args:
            obj (Any): an instance of some obj class (some QM method)
            bvector (list[OneIndex]): b vector for each targeted root
            hdiag (OneIndex): the diagonal of the matrix to be diagonalized
            sigma (list[OneIndex] | None): the previous sigma solutions
            hamsub (TwoIndex): the already determined part of H_sub

        Returns:
            tuple[TwoIndex, list[OneIndex] | None]: The subspace Hamiltonian of
                                                    the current iteration and the
                                                    updated list of sigma vectors
        """
        bind = 0
        if sigma is False:
            # first iteration
            # sigma = []
            self.nsigmav = 0
            if self.todisk:
                sigma = None
            else:
                sigma = []
        else:
            # Append
            bind = self.nsigmav
        # Loop over all bvectors to calculate sigma vectors
        for b in range(bind, self.nbvector):
            bv = self.read_from_disk(bvector, "bvector", b)
            sigma_ = obj.build_subspace_hamiltonian(bv, hdiag, *args)
            sigma = self.push_vector(sigma, sigma_, "sigmav", self.nsigmav)
            self.nsigmav += 1
        ham = self.calculate_subspace_hamiltonian(bvector, sigma, hamsub, bind)
        return ham, sigma

    def calculate_subspace_hamiltonian(
        self,
        bvector: list[OneIndex] | None,
        sigmav: list[OneIndex] | None,
        hamsub: TwoIndex,
        bind: int,
    ) -> TwoIndex:
        """Calculate subspace Hamiltonian (bvector.sigma)_ij

        Args:
            bvector (list[OneIndex] | None): list containing all b vectors
            sigmav (list[OneIndex] | None): list containing all sigma vectors
            hamsub (TwoIndex): the subspace Hamiltonian from a previous iteration
            bind (int): index indicating the position of the new sigma vectors

        Returns:
            TwoIndex: The subspace Hamiltonian of the current iteration step
        """
        subham = self.lf.create_two_index(self.nbvector, self.nbvector)
        if hamsub is not False:
            subham.assign(hamsub, end0=hamsub.nbasis, end1=hamsub.nbasis1)
            del hamsub
            for b in range(0, self.nbvector):
                for s in range(bind, self.nbvector):
                    bv = self.read_from_disk(bvector, "bvector", b)
                    sv = self.read_from_disk(sigmav, "sigmav", s)
                    prod1 = bv.dot(sv)
                    subham.set_element(b, s, prod1, symmetry=1)
                    if b < s:
                        bv = self.read_from_disk(bvector, "bvector", s)
                        sv = self.read_from_disk(sigmav, "sigmav", b)
                        prod2 = bv.dot(sv)
                        subham.set_element(s, b, prod2, symmetry=1)
        else:
            row = 0
            for b in range(0, self.nbvector):
                bv = self.read_from_disk(bvector, "bvector", b)
                col = 0
                for s in range(0, self.nbvector):
                    sv = self.read_from_disk(sigmav, "sigmav", s)
                    prod = bv.dot(sv)
                    subham.set_element(row, col, prod, symmetry=1)
                    col += 1
                row += 1
        return subham

    def gramschmidt(
        self,
        old: list[OneIndex] | None,
        new: OneIndex,
        nvector: int,
        select: int,
        norm: bool = True,
        threshold: float = 1e-4,
    ) -> OneIndex | None:
        """Orthonormalize a vector (new) on a set of others (already orthonormal)
        using the Gram-Schmidt orthonormalization procedure.

        Args:
            old (list[OneIndex] | None): list of old (orthonormal) vectors
            new (OneIndex): new vector to be orthonormalized
            nvector (int): number of old vectors
            select (int): the name of vectors to be loaded from disk
            norm (bool, optional): if True, do a normalizatoin. Defaults to True.
            threshold (float, optional): If norm of new vector is small, do not
                                         normalize. Defaults to 1e-4.

        Returns:
            OneIndex | None: _description_
        """
        for i in range(0, nvector):
            oldi = self.read_from_disk(old, select, i)
            proj = oldi.copy()
            norm2 = oldi.dot(oldi)
            newdotold = new.dot(oldi, 1.0)
            proj.iscale(newdotold / norm2)
            new.iadd(proj, -1.0)
            oldi = None
            proj = None
        if norm:
            newnormo = new.norm()
            if log.do_high:
                log(f"Norm {newnormo}")
            if newnormo <= threshold:
                return None
            else:
                new.iscale(1 / newnormo)
                return new
        return new

    @timer.with_section("Davidson")
    def __call__(
        self, obj: Any, *args: Any
    ) -> tuple[
        NDArray[np.float64],
        None | NDArray[np.float64] | list[NDArray[np.float64]],
    ]:
        """Perform a Davidson diagonalization.

        Args:
            obj (Any): a class instance containing method-specific functions

        Returns:
            tuple[NDArray[np.float64], NDArray[np.float64]]: The eigenvalues and eigenvectors
        """
        #
        # compute diagonal of Hamiltonian
        #
        hdiag = self.compute_h_diag(obj, *args)
        #
        # compute guess vectors
        #
        bvector = self.build_guess_vectors(obj, hdiag, *args)

        if log.do_medium:
            log.hline("=")
            log("Davidson diagonalization")
            log.hline("~")
            log(f"{'maxiter':>20s}: {self.maxiter}")
            log(f"{'nroots':>20s}: {self.nroots}")
            log(f"{'nguess':>20s}: {self.nguess}")
            log(f"{'to disk':>20s}: {self.todisk}")
            log(f"{'Energy tolerance':>20s}: {self.tol}")
            log(f"{'Vector tolerance':>20s}: {self.tolv}")
            log(f"{'restart':>20s}: {self.restart_fn}")
            log.hline("~")

        theta_old = np.zeros(self.nroots)
        iter_ = 0
        restart = False
        dim = obj.dimension
        rknorm = np.zeros(self.nroots)
        if self.todisk:
            evec = None
            rk = None
        else:
            evec = np.zeros((dim, self.nroots))
            rk = np.zeros((dim, self.nroots))
        converged = []
        while True:
            #
            # First iteration or after subspace collapse: construct full Hamiltonian
            #
            if iter_ == 0 or restart:
                hamsub, sigma = self.build_subspace_hamiltonian(
                    obj, bvector, hdiag, False, False, *args
                )
                restart = False
            #
            # subsequent iterations: construct new subspace Hamiltonian elements
            #
            else:
                hamsub, sigma = self.build_subspace_hamiltonian(
                    obj, bvector, hdiag, sigma, hamsub, *args
                )
            #
            # diagonalization of submatrix (eigenvalues not sorted)
            #
            theta, s = scipy.linalg.eig(
                hamsub._array,
                b=None,
                left=False,
                right=True,
                overwrite_a=False,
                overwrite_b=False,
                check_finite=True,
            )
            #
            # sort eigenvalues and eigenvectors
            #
            theta, s = self.sort_eig(theta, s)
            #
            # loop over all roots
            #
            evec = self.reset_vector(evec)
            rk = self.reset_vector(rk)
            for j in range(0, self.nroots):
                tmpevj = np.zeros(dim)
                tmprkj = np.zeros(dim)
                for i in range(self.nsigmav):
                    bv = self.read_from_disk(bvector, "bvector", i)
                    sv = self.read_from_disk(sigma, "sigmav", i)
                    tmpevj[:] += bv._array * s[i, j].real
                    tmprkj[:] = (
                        tmprkj[:]
                        + sv._array * s[i, j]
                        - theta[j] * bv._array * s[i, j]
                    )
                #
                # Calculate norm for convergence
                #
                rknorm[j] = np.linalg.norm(tmprkj[:], ord=2)
                #
                # Append to list or store to disk
                #
                evec = self.push_vector(evec, tmpevj.real, "evecs", j)
                #
                # get rid of nans or division by almost small numbers:
                #
                ind = np.where(abs(theta[j] - hdiag._array) < 1e-4)
                # Preconditioning
                # Do not divide by zero
                if rknorm[j] >= 1e-4:
                    tmprkj = (
                        np.divide(
                            tmprkj[:],
                            (theta[j] - hdiag._array),
                            where=(abs(theta[j] - hdiag._array) != 0.0),
                        )
                    ).real
                # If denominator small, set to zero
                tmprkj[ind] = 0.0
                # Push back residual
                rk = self.push_vector(rk, tmprkj, "residual", j)
                tmpevj = None
                tmprkj = None
            # free memory
            s = None
            #
            # normalize correction vectors
            #
            deltak = self.normalize_correction_vector(rk, dim)
            #
            # perform subspace collapse if required
            #
            if self.nbvector > self.maxvectors:
                if log.do_medium:
                    log(
                        "Maximum number of Davidson vectors reached. "
                        "Performing subspace collapse."
                    )
                self.nbvector = 0
                bvector = self.reset_vector(bvector)
                restart = True
                for j in range(self.nroots):
                    bj = self.lf.create_one_index(dim)
                    evecj = self.read_from_disk(evec, "evecs", j)
                    bj.assign(evecj)
                    if j != 0:
                        bjortho = self.gramschmidt(
                            bvector, bj, self.nbvector, "bvector"
                        )
                        if bjortho is not None:
                            bvector = self.push_vector(
                                bvector, bjortho, "bvector", self.nbvector
                            )
                            self.nbvector += 1
                    else:
                        bvector = self.push_vector(
                            bvector, bj, "bvector", self.nbvector
                        )
                        self.nbvector += 1
                    bj = None
                    evecj = None
            #
            # expand search space with correction vectors
            #
            for j in range(0, self.nroots):
                newv = self.lf.create_one_index(dim)
                drk = self.read_from_disk(deltak, "residualortho", j)
                newv.assign(drk)
                #
                # orthogonalize correction vectors against bvectors
                #
                deltakortho = self.gramschmidt(
                    bvector, newv, self.nbvector, "bvector"
                )
                if log.do_high:
                    try:
                        log(
                            f"New b vector for root {j} with norm: {deltakortho.norm()}"
                        )
                    except Exception:
                        log(f"b vector neglected for root {j}.")
                if deltakortho is not None:
                    # append new vector
                    bvector = self.push_vector(
                        bvector, deltakortho, "bvector", self.nbvector
                    )
                    self.nbvector += 1
                deltakortho = None
                drk = None
            # free memory
            newv = None
            #
            # calculate convergence thresholds
            #
            de = abs(theta[: self.nroots].real - theta_old.real)
            if log.do_medium:
                log(
                    f"{'iter':>6s} {'vector':>7s} {'|HR-ER|':>10s} "
                    f"{'E(new)-E(old)':>19s} {'E_excitation':>14s}"
                )
                for i in range(self.nroots):
                    if i == 0 and self.skipgs:
                        continue
                    if i in converged:
                        if abs(de[i]) > self.tol or rknorm[i] > self.tolv:
                            log(
                                f"{iter_:>5d} {i:>6d}   {rknorm[i]:> .6e}    "
                                f"{theta[i] - theta_old[i]:> .6e}  {theta[i]:> .6e}  "
                            )
                            converged.remove(i)
                        continue
                    if abs(de[i]) < self.tol and rknorm[i] < self.tolv:
                        log(
                            f"{iter_:>5d} {i:>6d}   {rknorm[i]:> .6e}    "
                            f"{theta[i] - theta_old[i]:> .6e}  {theta[i]:> .6e}  "
                            f"converged"
                        )
                        if i not in converged:
                            converged.append(i)
                    elif i not in converged:
                        log(
                            f"{iter_:>5d} {i:>6d}   {rknorm[i]:> .6e}    "
                            f"{theta[i] - theta_old[i]:> .6e}  {theta[i]:> .6e}  "
                        )
                log(" ")
            theta_old = theta[: self.nroots].real
            #
            # Do checkpointing (only most recent vectors stored in evec)
            #
            if not self.todisk:
                try:
                    acronym = obj.acronym
                except AttributeError:
                    acronym = self.acronym
                self.checkpoint.update(f"civ_{acronym}", evec)
                self.checkpoint.to_file(f"checkpoint_Davidson_{acronym}.h5")
            #
            # check for convergence
            #
            if (de < self.tol).all() and (rknorm < self.tolv).all():
                if log.do_medium:
                    log.hline("~")
                    log("   Davidson converged")
                    log.hline("=")
                return theta.real, evec
            iter_ += 1
            if iter_ >= self.maxiter:
                if log.do_medium:
                    log.hline("~")
                    log("   Davidson NOT converged")
                    log.hline("=")
                return theta.real, evec
