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
# This implementation has been taken from `Horton 2.0.0`.
# However, this file has been updated and debugged. Compatibility with Horton is NOT
# guaranteed.
#
# Detailed changes (see also CHANGELOG):
# 2020-07-01: Update to PyBEST standard, including naming convention
# 2020-07-01: Introduce general tensor contraction engine
# 2020-07-01: Update to new python features, including f-strings
# 2020-07-01: Changed to general [slice] function and removed deprecated [slice_to] functions
# 2020-07-01: Included additional tensor contractions
# 2020-07-01: Removed deprecated [contract_] functions

"""Cholesky decomposition of four-index objects"""

from __future__ import annotations

import numpy as np

from pybest.exceptions import ArgumentError, MatrixShapeError, UnknownOption
from pybest.linalg import DenseFourIndex, DenseLinalgFactory, DenseOrbital
from pybest.linalg.base import (
    PYBEST_CUPY_AVAIL,
    FourIndex,
    parse_four_index_transform_exps,
)
from pybest.linalg.gpu_contract import cupy_helper
from pybest.log import log, timer
from pybest.utility import doc_inherit


class CholeskyLinalgFactory(DenseLinalgFactory):
    """Cholesky Linalg Factory containing the Cholesky decomposed four-index
    electron repulsion integrals.
    """

    cholesky_linalg_identifier = True

    @doc_inherit(DenseLinalgFactory)
    def create_four_index(
        self,
        nbasis=None,
        nvec=None,
        array=None,
        array2=None,
        copy=False,
        label="",
        nbasis1=None,
        nbasis2=None,
        nbasis3=None,
    ):
        nbasis = nbasis or self.default_nbasis
        return CholeskyFourIndex(
            nbasis,
            nvec=nvec,
            array=array,
            array2=array2,
            copy=copy,
            label=label,
            nbasis1=nbasis1,
            nbasis2=nbasis2,
            nbasis3=nbasis3,
        )

    @doc_inherit(DenseLinalgFactory)
    def _check_four_index_init_args(self, four_index, nbasis=None, nvec=None):
        nbasis = nbasis or self.default_nbasis
        four_index.__check_init_args__(nbasis, nvec)

    create_four_index.__check_init_args__ = _check_four_index_init_args


class CholeskyFourIndex(FourIndex):
    """Cholesky four-dimensional matrix."""

    cholesky_four_identifier = True

    #
    # Constructor and destructor
    #

    def __init__(
        self,
        nbasis: int | None = None,
        nvec: int | None = None,
        array: np.ndarray | None = None,
        array2: np.ndarray | None = None,
        copy: bool = False,
        label: str = "",
        nbasis1: int | None = None,
        nbasis2: int | None = None,
        nbasis3: int | None = None,
    ):
        """Initializes a four-index matrix class stored in decomposed form of
        three-dimensional arrays. The indices correspond to physical notation
        with <pr|qs> = (pq|Q)(Q|rs) where p corresponds to nbasis, r - nbasis1,
        q - nbasis2, and s - nbasis3.

        **Arguments:**

        nbasis (obligatory), nbasis1, nbasis2, nbasis3
            The number of basis functions. nbasis is a default value for other
            nbasisX arguments if not specified.

        nvec
            The number of (2-index) Cholesky vectors.

        array
            The array with Cholesky vectors, shape = (nvec, nbasis, nbasis2).

        array2
            The second set of Cholesky vectors, if different from the first.

        Either nvec or array must be given (or both).
        """
        if nvec is None and array is None:
            raise ArgumentError(
                "Either nvec or array must be given (or both)."
            )

        if array is not None:
            self.from_array(array, array2=array2, copy=copy)
        else:
            self._self_alloc = True
            if array2 is not None:
                raise ArgumentError(
                    "Argument array2 only allowed when array is given."
                )
            self.from_nbasis(nvec, nbasis, nbasis1, nbasis2, nbasis3)

        self._label = label

    def from_array(self, array, array2=None, copy=False):
        """Initializes instance from numpy.ndarrays."""
        self._self_alloc = False
        # Ensure that nvec (number of Cholesky vectors) agree.
        if array2 is not None and array2.shape[0] != array.shape[0]:
            raise ArgumentError("Inconsistent number of Cholesky vectors.")
        # Set array and array2 attributes
        if copy:
            self._array = array.copy()
        else:
            self._array = array
        if array2 is None:
            self._array2 = self._array
        else:
            if copy:
                self._array2 = array2.copy()
            else:
                self._array2 = array2

    def from_nbasis(
        self,
        nvec: int | None = None,
        nbasis: int | None = None,
        nbasis1: int | None = None,
        nbasis2: int | None = None,
        nbasis3: int | None = None,
    ):
        """Initializes instance filled with zeros."""
        self._self_alloc = True

        if nvec is None:
            raise RuntimeError("nvec cannot be None!")

        if nbasis is None:
            raise RuntimeError("nbasis cannot be None!")

        if nbasis2 is None:
            nbasis2 = nbasis

        self._array = np.zeros((nvec, nbasis, nbasis2))
        log.mem.announce(self._array.nbytes)
        if nbasis1 is None and nbasis3 is None:
            self._array2 = self._array
        else:
            nbasis1 = nbasis1 or nbasis
            nbasis3 = nbasis3 or nbasis
            self._array2 = np.zeros((nvec, nbasis1, nbasis3))
            log.mem.announce(self._array2.nbytes)

    def __del__(self):
        """Destructor."""
        if log is not None:
            if hasattr(self, "_array") and hasattr(self, "_self_alloc"):
                if self._self_alloc:
                    log.mem.denounce(self._array.nbytes)
                    if (
                        hasattr(self, "_array2")
                        and self._array2 is not self._array
                    ):
                        log.mem.denounce(self._array2.nbytes)
        if hasattr(self, "_array"):
            del self._array
        # delete second pointer or second element
        if hasattr(self, "_array2"):
            del self._array2

    @staticmethod
    def einsum_index(script):
        """Returns indices to numpy.einsum summation
        string - str of length equal to four

        Example:
        self.einsum_index('abcd') returns 'xac,xbd'
        """
        if len(script) != 4 and isinstance(script, str):
            raise ValueError
        char = next(char for char in "xijkl" if char not in script)
        return f"{char}{script[0]}{script[2]},{char}{script[1]}{script[3]}"

    #
    # Properties
    #

    @property
    def shape(self):
        """The shape of the object"""
        return (
            self._array.shape[1],
            self._array2.shape[1],
            self._array.shape[2],
            self._array2.shape[2],
        )

    @property
    def array(self):
        """Returns the actual array of class"""
        return self._array

    @array.setter
    def array(self, new_array):
        """Sets the array and array2 of class"""
        if not new_array.ndim == 3:
            raise ArgumentError("Only 3D array can be set.")
        if not new_array.shape[0] == self.nvec:
            raise ArgumentError("Number of Cholesky vectors must be the same.")
        self._array = new_array
        self._array2 = self._array

    @property
    def array2(self):
        """Sets the actual array2 of class"""
        return self._array2

    @array2.setter
    def array2(self, new_array):
        """Sets the actual array2 of class"""
        if not new_array.ndim == 3:
            raise ArgumentError("Only 3D array can be set.")
        if not new_array.shape[0] == self.nvec:
            raise ArgumentError("Number of Cholesky vectors must be the same.")
        self._array2 = new_array

    @property
    def arrays(self):
        """Returns list containing self._array and self._array2"""
        return [self._array, self._array2]

    @property
    def label(self):
        """Returns label of Cholesky object"""
        return self._label

    @label.setter
    def label(self, label):
        """Sets label of instance"""
        self._label = label

    #
    # Methods from base class

    def __check_init_args__(self, nbasis, nvec):
        """Is self compatible with the given constructor arguments?"""
        assert self.array is not None
        assert nbasis == self.nbasis
        assert nvec == self.nvec

    def __eq__(self, other):
        """Compare self with other"""
        return (
            isinstance(other, CholeskyFourIndex)
            and other.nbasis == self.nbasis
            and other.nvec == self.nvec
            and other.is_decoupled == self.is_decoupled
            and (other.array == self.array).all()
            and (other.array2 == self.array2).all()
        )
        # Shall we also compare the label here?

    @classmethod
    def from_hdf5(cls, grp):
        """Construct an instance from data previously stored in an h5py.Group.

        **Arguments:**

        grp
             An h5py.Group object.
        """
        nvec = grp["array"].shape[0]
        nbasis = grp["array"].shape[1]
        label = grp.attrs["label"]
        result = cls(nbasis, nvec, label=label)
        grp["array"].read_direct(result.array)
        if "array2" in grp:
            result.decouple_array2()
            grp["array2"].read_direct(result.array2)
        return result

    def to_hdf5(self, grp):
        """Dump this object in an h5py.Group

        **Arguments:**

        grp
             An h5py.Group object.
        """
        grp.attrs["class"] = self.__class__.__name__
        grp["array"] = self.array
        if self.array is not self.array2:
            grp["array2"] = self.array2
        grp.attrs["label"] = self.label

    def replace_array(self, value):
        """Replaces an array with another array, if not present, it will be
        generated.
        """
        if value.array2 is not value.array:
            self._array2 = value.array2
        else:
            self._array2 = value.array
        self._array = value.array

    def new(self):
        """Return a new four-index object with the same nbasis"""
        nbas = {"nbasis2": self.shape[2]}
        if self.is_decoupled:
            nbas.update(
                {
                    "nbasis1": self.shape[1],
                    "nbasis3": self.shape[2],
                }
            )
        return CholeskyFourIndex(self.nbasis, nvec=self.nvec, **nbas)

    def _check_new_init_args(self, other):
        """Check whether an already initialized object is compatible"""
        other.__check_init_args__(self.nbasis, self.nvec)

    new.__check_init_args__ = _check_new_init_args

    def clear(self):
        """Reset all elements to zero."""
        self.array[:] = 0.0
        if self.array is not self._array2:
            self.array2[:] = 0.0

    def copy(
        self,
        begin0=0,
        end0=None,
        begin1=0,
        end1=None,
        begin2=0,
        end2=None,
        begin3=0,
        end3=None,
    ):
        """Return a copy of the current four-index operator"""
        end0, end1, end2, end3 = self.fix_ends(end0, end1, end2, end3)
        nbasis = end0 - begin0
        nbas = {
            "nbasis1": end1 - begin1,
            "nbasis2": end2 - begin2,
            "nbasis3": end3 - begin3,
        }
        result = CholeskyFourIndex(nbasis, self.nvec, label=self.label, **nbas)
        result.assign(
            self, begin0, end0, begin1, end1, begin2, end2, begin3, end3
        )
        return result

    def view(
        self,
        begin0=0,
        end0=None,
        begin1=0,
        end1=None,
        begin2=0,
        end2=None,
        begin3=0,
        end3=None,
    ):
        """Returns a CholeskyFourIndex instance with arrays being a view of
        self.array and self.array2. The instance stops being a true view (stops
        sharing the same memory with its parent instance) if any of its arrays
        is set manually.

        ** Arguments **

        begin0, end0
            start and stop index for dimension corresponding to p/nbasis

        begin1, end1
            start and stop index for dimension corresponding to r/nbasis1

        begin2, end2
            start and stop index for dimension corresponding to q/nbasis2

        begin3, end3
            start and stop index for dimension corresponding to s/nbasis3

        """
        end0, end1, end2, end3 = self.fix_ends(end0, end1, end2, end3)
        nbasis = end0 - begin0
        array = self.array[:, begin0:end0, begin2:end2]
        array2 = self.array2[:, begin1:end1, begin3:end3]
        result = CholeskyFourIndex(
            nbasis,
            array=array,
            array2=array2,
            label=self.label,
        )
        return result

    def assign(
        self,
        other,
        begin4=0,
        end4=None,
        begin5=0,
        end5=None,
        begin6=0,
        end6=None,
        begin7=0,
        end7=None,
    ):
        """Assign with the contents of other object

        chol_0.assign(chol_1, begin5=2)
        is equivalent to
        chol_0.array[:, :, :] = chol_1[:, 2:, :]
        chol_0.array2[:, :, :] = chol_1[:, :, :]

        **Arguments:**

        other: CholeskyFourIndex
            its arrays (or slices) are copied to assigned object

        begin4, end4: int
            start and stop index of other's axis corresponding to p/nbasis

        begin5, end5: int
            start and stop index of other's axis corresponding to r/nbasis1

        begin6, end6: int
            start and stop index of other's axis corresponding to q/nbasis2

        begin7, end7: int
            start and stop index of other's axis corresponding to s/nbasis3

        """
        end4, end5, end6, end7 = other.fix_ends(end4, end5, end6, end7)
        self.check_type("other", other, CholeskyFourIndex)
        shape = (end4 - begin4, end5 - begin5, end6 - begin6, end7 - begin7)
        if self.shape != shape:
            raise MatrixShapeError(f"Shape mismatch: {self.shape} != {shape}")
        self.array[:] = other.array[:, begin4:end4, begin6:end6]
        is_begin_same = begin4 == begin5 and begin6 == begin7
        is_end_same = end4 == end5 and end6 == end7
        if (other.array is other.array2) and is_begin_same and is_end_same:
            self.reset_array2()
        else:
            self.decouple_array2()
            self.array2[:] = other.array2[:, begin5:end5, begin7:end7]

    def randomize(self):
        """Fill with random normal data"""
        self.array[:] = np.random.normal(0, 1, self.array.shape)
        if self.is_decoupled:
            self.array2[:] = np.random.normal(0, 1, self.array2.shape)

    def permute_basis(self, permutation):
        """Reorder the coefficients for a given permutation of basis functions."""
        # Easy enough but irrelevant
        raise NotImplementedError

    def change_basis_signs(self, signs):
        """Correct for different sign conventions of the basis functions."""
        # Easy enough but irrelevant
        raise NotImplementedError

    def iadd(self, other, factor):
        """This method is not supported due to the Cholesky decomposition."""
        raise NotImplementedError

    def iscale(self, factor):
        """In-place multiplication with a scalar

        **Arguments:**

        factor
             A scalar factor.
        """
        self._array *= np.sqrt(factor)

        if self.array is not self.array2:
            # arrays have been transformed
            self._array2 *= np.sqrt(factor)

    def get_element(self, i, j, k, l):
        """Return a matrix element"""
        return np.dot(self.array[:, i, k], self.array2[:, j, l])

    def set_element(self, i, j, k, l, value):
        """This method is not supported due to the Cholesky decomposition."""
        raise NotImplementedError

    #
    # Properties
    #

    @property
    def nbasis(self):
        """The number of basis functions"""
        return self.array.shape[1]

    @property
    def nvec(self):
        """The number of Cholesky vectors"""
        return self.array.shape[0]

    @property
    def is_decoupled(self):
        """Returns True if array and array2 are the same object."""
        return self.array is not self.array2

    def decouple_array2(self):
        """Allocates a second Cholesky vector if not done yet"""
        if self.array2 is self.array:
            self._array2 = self.array.copy()
            log.mem.announce(self.array2.nbytes)

    def reset_array2(self):
        """Deallocates the second cholesky vector and sets it to match the first."""
        if self.array2 is not self.array:
            log.mem.denounce(self.array2.nbytes)
            self._array2 = self.array

    @timer.with_section("CholToDense")
    def get_dense(self, select="td"):
        """Return the DenseFourIndex equivalent. ONLY FOR TESTING. SUPER SLOW."""
        result = DenseFourIndex(self.nbasis)
        if select == "td":
            result.array[:] = np.tensordot(
                self.array, self.array2, axes=([0], [0])
            )
            result.array[:] = result.array.transpose(0, 2, 1, 3)
        elif select == "einsum":
            result = self.contract("abcd->abcd", select="einsum")
        else:
            raise UnknownOption(f"Unknown switch: {select}")
        return result

    def is_symmetric(self, symmetry=2, rtol=1e-5, atol=1e-8):
        """Check the symmetry of the array.

        **Optional arguments:**

        symmetry
             The symmetry to check. See :ref:`dense_matrix_symmetry`
             for more details.

        rtol and atol
             relative and absolute tolerance. See to ``np.allclose``.
        """
        if self.is_decoupled and symmetry in (2, 8):
            return False
        if symmetry in (4, 8):
            if not np.allclose(
                self.array, self.array.swapaxes(1, 2), rtol, atol
            ):
                return False
            if self.is_decoupled and not np.allclose(
                self.array2, self.array2.swapaxes(1, 2), rtol, atol
            ):
                return False
        return True

    def symmetrize(self, symmetry=8):
        """Adds transposition to ensure symmetry."""
        self.check_options("symmetry", symmetry, 1, 2, 4, 8)
        if symmetry in (2, 8) and self.is_decoupled:
            # This is a different type of symmetrization than in the dense case!
            self._array[:] += self.array2
            self._array *= 0.5
            self.reset_array2()
        if symmetry in (4, 8):
            self._array[:] = self.array + self.array.transpose(0, 2, 1)
            if self.is_decoupled:
                self._array2[:] = self.array2 + self.array2.transpose(0, 2, 1)

    def itranspose(self):
        """In-place transpose: ``0,1,2,3 -> 1,0,3,2``"""
        if self.is_decoupled:
            self._array, self._array2 = self.array2, self.array

    def sum(self):
        """Return the sum of all elements. EXPENSIVE!"""
        return np.tensordot(self.array, self.array2, (0, 0)).sum()

    def iadd_exchange(self):
        """In-place addition of its own exchange contribution"""
        raise NotImplementedError

    def assign_four_index_transform(
        self,
        ao_integrals,
        exp0,
        exp1=None,
        exp2=None,
        exp3=None,
        method="cupy",
        **kwargs,
    ):
        """Perform four index transformation.

        **Arguments:**

        oa_integrals
             A CholeskyFourIndex with integrals in atomic orbitals.

        exp0
             A DenseOrbital object with molecular orbitals

        **Optional arguments:**

        exp1, exp2, exp3
             Can be provided to transform each index differently. See
             ``parse_four_index_transform_exps`` for details.

        method
             Either ``einsum``, ``cupy`` (default) or ``tensordot``.
        """
        self.check_type("ao_integrals", ao_integrals, CholeskyFourIndex)
        exp0, exp1, exp2, exp3 = parse_four_index_transform_exps(
            exp0, exp1, exp2, exp3, DenseOrbital
        )
        if method == "einsum":
            opt = kwargs.get("optimize", "optimal")
            # All 4 indices of the integral array in atomic orbital basis
            # have to be coordinate transformed seperately.
            if ao_integrals.is_decoupled or not (
                exp0 is exp1 and exp2 is exp3
            ):
                self.decouple_array2()
                self._array2[:] = np.einsum(
                    "bi,kbd->kid",
                    exp1.coeffs,
                    ao_integrals.array2,
                    optimize=opt,
                )
                self._array2[:] = np.einsum(
                    "dj,kid->kij", exp3.coeffs, self._array2, optimize=opt
                )
            self._array[:] = np.einsum(
                "ai,kac->kic", exp0.coeffs, ao_integrals.array
            )
            self._array[:] = np.einsum(
                "cj,kic->kij", exp2.coeffs, self._array, optimize=opt
            )
        elif method == "cupy" and PYBEST_CUPY_AVAIL:
            # All 4 indices of the integral array in atomic orbital basis
            # have to be coordinate transformed seperately.
            if ao_integrals.is_decoupled or not (
                exp0 is exp1 and exp2 is exp3
            ):
                self.decouple_array2()
                try:
                    self._array2[:] = cupy_helper(
                        "bi,kbd->kid",
                        exp1.coeffs,
                        ao_integrals.array2,
                        **kwargs,
                    )
                    self._array2[:] = cupy_helper(
                        "dj,kid->kij", exp3.coeffs, self._array2, **kwargs
                    )
                except MemoryError:
                    if log.do_high:
                        log.warn("Not enough Video memory.")
                        log.warn("Defaulting to numpy.tensordot.")
                    self._array2[:] = np.tensordot(
                        ao_integrals.array2, exp1.coeffs, axes=([1], [0])
                    )
                    self._array2[:] = np.tensordot(
                        self._array2, exp3.coeffs, axes=([1], [0])
                    )
            try:
                self._array[:] = cupy_helper(
                    "bi,kbd->kid", exp0.coeffs, ao_integrals.array, **kwargs
                )
                self._array[:] = cupy_helper(
                    "dj,kid->kij", exp2.coeffs, self._array, **kwargs
                )
            except MemoryError:
                if log.do_high:
                    log.warn("Not enough Video memory.")
                    log.warn("Defaulting to numpy.tensordot.")
                self._array[:] = np.tensordot(
                    ao_integrals.array, exp0.coeffs, axes=([1], [0])
                )
                self._array[:] = np.tensordot(
                    self._array, exp2.coeffs, axes=([1], [0])
                )
        elif method == "tensordot" or (
            method == "cupy" and not PYBEST_CUPY_AVAIL
        ):
            # All 4 indices of the integral array in atomic orbital basis
            # have to be coordinate transformed seperately.
            if ao_integrals.is_decoupled or not (
                exp0 is exp1 and exp2 is exp3
            ):
                self.decouple_array2()
                self._array2[:] = np.tensordot(
                    ao_integrals.array2, exp1.coeffs, axes=([1], [0])
                )
                self._array2[:] = np.tensordot(
                    self._array2, exp3.coeffs, axes=([1], [0])
                )
            self._array[:] = np.tensordot(
                ao_integrals.array, exp0.coeffs, axes=([1], [0])
            )
            self._array[:] = np.tensordot(
                self._array, exp2.coeffs, axes=([1], [0])
            )
        else:
            raise UnknownOption(
                "The method must either be 'einsum' or 'tensordot'."
            )
