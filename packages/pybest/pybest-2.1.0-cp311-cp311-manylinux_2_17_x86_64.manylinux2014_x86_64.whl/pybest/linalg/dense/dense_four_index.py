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
# Its current version contains updates from the PyBEST developer team.
#
# This file has been rewritten by Maximilian Kriebel.
#
# Detailed changes (see also CHANGELOG):
# 2020-07-01: Update to PyBEST standard, including naming convention
# 2020-07-01: Update to new python features, including f-strings
# 2020-07-01: Changed to general [slice] function and removed deprecated [slice_to] functions
# 2020-07-01: Removed deprecated [contract_] functions
# 2020-07-01: Introduce labels for all NIndex objects for book keeping
# 2021-TBD-v1.1.0: Introduce array setters
# 2022-09/10: dense.py split into files for each class in subfolder dense
# 2022-09/10: [slice] and [tco] replaced with [contract]

#
# FIXME:
# - rename ``new()`` into ``clean_copy``
# - add (orbital-related) methods specific for HF to HF module or orbital_utils


r"""Dense matrix implementations

The naming scheme for the expand methods
-------------------------------------------------------

The name of ``expand`` methods is as follows::

     [iadd_]{expand}[_X][_Y][_to_Z]

where each part between square brackets is optional. ``X``, ``Y`` and ``Z``
can be any of ``one``, ``two``, ``three`` or ``four``. The name ``expand``
have the following meaning:

``expand``
     Products of elements are computed but these products are not added.
     Similar to an outer product but more general.

When ``iadd_`` is used as a prefix, the result of the contraction is added
in-place to the self object. In this case, the ``_to_Z`` part is never
present. A contraction of all input arguments is made. The dimensionality
of the input arguments is indicated by ``_X`` and ``_Y``.

When ``_to_Z`` is present, the contraction involves self and possibly other
arguments whose dimensionality is indicated by ``_X`` and ``_Y``. In this
case, ``iadd_`` can not be present. The result is written to an output
argument. If the output argument is not provided, fresh memory is allocated
to compute the contraction and the result is returned. (This allocation is
provided for convenience but should not be used in critical situations.)

Some remarks:

* Similar conventions apply to an ``expand`` method.
* All ``expand`` methods are implemented with the driver
  method ``DenseLinalgFactory.tco``. However, other implementations than
  `Dense` are free to implement things differently.
* All ``expand`` methods never touch the internals of
  higher-index objects.

For more specific information, read the documentation of the individual
classes and methods below.


.. _dense_matrix_symmetry:

Handling of index symmetry
--------------------------

The dense matrix classes do not exploit matrix symmetry to reduce memory
needs. Instead they will happily store non-symmetric data if need be. There
are however a few methods in the :py:class:`DenseTwoIndex` and
:py:class:`DenseFourIndex` classes below that take a ``symmetry`` argument to
check or enforce a certain index symmetry.

The symmetry argument is always an integer that corresponds to the redundancy
of the off-diagonal matrix elements in the dense storage. In practice this
means the following:

* :py:class:`DenseFourIndex`

  * ``symmetry=1``: Nothing is checked/enforced

  * ``symmetry=2``: Dummy index symmetry is
    checked/enforced, i.e.
    :math:`\langle ij \vert B \vert kl \rangle =`
    :math:`\langle ji \vert B \vert lk \rangle`

  * ``symmetry=4``: Hermitian and real index symmetry are checked/enforced,
    i.e.
    :math:`\langle ij \vert B \vert kl \rangle =`
    :math:`\langle kl \vert B \vert ij \rangle =`
    :math:`\langle kj \vert B \vert il \rangle =`
    :math:`\langle il \vert B \vert kj \rangle`.
    (This only makes sense because the basis functions are assumed to be
    real.)

  * ``symmetry=8``: All possible symmetries are checked/enforced, i.e.
    :math:`\langle ij \vert B \vert kl \rangle =`
    :math:`\langle kl \vert B \vert ij \rangle =`
    :math:`\langle kj \vert B \vert il \rangle =`
    :math:`\langle il \vert B \vert kj \rangle =`
    :math:`\langle ji \vert B \vert lk \rangle =`
    :math:`\langle lk \vert B \vert ji \rangle =`
    :math:`\langle jk \vert B \vert li \rangle =`
    :math:`\langle li \vert B \vert jk \rangle`.
    (This only makes sense because the basis functions are assumed to be
    real.)

Dense matrix classes
--------------------
"""

import numpy as np

from pybest.exceptions import (
    ArgumentError,
    MatrixShapeError,
    SymmetryError,
    UnknownOption,
)
from pybest.linalg.base import (
    PYBEST_CUPY_AVAIL,
    FourIndex,
    parse_four_index_transform_exps,
)
from pybest.linalg.gpu_contract import cupy_helper
from pybest.log import log

from .._opt_einsum import oe_contract
from .dense_one_index import DenseOneIndex
from .dense_orbital import DenseOrbital
from .dense_three_index import DenseThreeIndex
from .dense_two_index import DenseTwoIndex


class DenseFourIndex(FourIndex):
    """Dense symmetric four-dimensional matrix.

    This is the most inefficient implementation in terms of memory usage and
    computer time. Due to its simplicity, it is trivial to implement. This
    implementation mainly serves as a reference for testing purposes.
    """

    # identification attribute
    dense_four_identifier = True

    #
    # Constructor and destructor
    #

    def __init__(
        self, nbasis, nbasis1=None, nbasis2=None, nbasis3=None, label=""
    ):
        """
        **Arguments:**

        nbasis
             The number of basis functions.

        **Optional arguments:**

        nbasis1, nbasis2, nbasis3
             When not given, nbasis is the default value for other nbasisX
             arguments if not specified.

        label
             The name (label) of the instance to be created.
        """
        if nbasis1 is None:
            nbasis1 = nbasis
        if nbasis2 is None:
            nbasis2 = nbasis
        if nbasis3 is None:
            nbasis3 = nbasis
        self._array = np.zeros((nbasis, nbasis1, nbasis2, nbasis3), float)
        self._label = label
        log.mem.announce(self.array.nbytes)

    def __del__(self):
        """Destructor."""
        if log is not None:
            if hasattr(self, "_array"):
                log.mem.denounce(self.array.nbytes)
        if hasattr(self, "_array"):
            del self._array

    #
    # Methods from base class
    #

    def __check_init_args__(
        self, nbasis, nbasis1=None, nbasis2=None, nbasis3=None
    ):
        """Is self compatible with the given constructor arguments?

        nbasis
             The number of basis functions. (Number of rows).

        **Optional arguments:**

        nbasis1, nbasis2, nbasis3
             When not given, nbasis is the default value for other nbasisX
             arguments if not specified.
        """
        if nbasis1 is None:
            nbasis1 = nbasis
        if nbasis2 is None:
            nbasis2 = nbasis
        if nbasis3 is None:
            nbasis3 = nbasis
        assert nbasis == self.nbasis
        assert nbasis1 == self.nbasis1
        assert nbasis2 == self.nbasis2
        assert nbasis3 == self.nbasis3

    def __eq__(self, other):
        """Compare self with other"""
        return (
            isinstance(other, DenseFourIndex)
            and other.nbasis == self.nbasis
            and other.nbasis1 == self.nbasis1
            and other.nbasis2 == self.nbasis2
            and other.nbasis3 == self.nbasis3
            and (other.array == self.array).all()
        )

    @classmethod
    def from_hdf5(cls, grp):
        """Construct an instance from data previously stored in an h5py.Group.

        **Arguments:**

        grp
             An h5py.Group object.
        """
        nbasis = grp["array"].shape[0]
        nbasis1 = grp["array"].shape[1]
        nbasis2 = grp["array"].shape[2]
        nbasis3 = grp["array"].shape[3]
        label = grp.attrs["label"]
        result = cls(nbasis, nbasis1, nbasis2, nbasis3, label)
        grp["array"].read_direct(result.array)
        return result

    def to_hdf5(self, grp):
        """Dump this object in an h5py.Group

        **Arguments:**

        grp
             An h5py.Group object.
        """
        grp.attrs["class"] = self.__class__.__name__
        grp["array"] = self.array
        grp.attrs["label"] = self._label

    def new(self):
        """Return a new four-index object with the same nbasis"""
        return DenseFourIndex(
            self.nbasis, self.nbasis1, self.nbasis2, self.nbasis3
        )

    @staticmethod
    def einsum_index(script):
        """Returns indices to numpy.einsum summation."""
        if not len(script) == 4 and isinstance(script, str):
            raise ValueError
        return script

    #
    # Properties
    #
    @property
    def nbasis(self):
        """The number of basis functions"""
        return self.array.shape[0]

    @property
    def nbasis1(self):
        """The number of basis functions"""
        return self.array.shape[1]

    @property
    def nbasis2(self):
        """The number of basis functions"""
        return self.array.shape[2]

    @property
    def nbasis3(self):
        """The number of basis functions"""
        return self.array.shape[3]

    @property
    def shape(self):
        """The shape of the object"""
        return self.array.shape

    @property
    def array(self):
        """Returns the actual array of class"""
        return self._array

    @array.setter
    def array(self, ndarray):
        """Sets numpy.ndarray as an array attribute."""
        if not ndarray.ndim == 4:
            raise ArgumentError("Only 4D array can be set.")
        self._array = ndarray

    @property
    def arrays(self):
        """Returns list containing self.array"""
        return [self.array]

    @property
    def label(self):
        """Returns label of instance"""
        return self._label

    @label.setter
    def label(self, label):
        """Sets label of instance"""
        self._label = label

    def _check_new_init_args(self, other):
        """Check whether an already initialized object is compatible"""
        other.__check_init_args__(
            self.nbasis, self.nbasis1, self.nbasis2, self.nbasis3
        )

    new.__check_init_args__ = _check_new_init_args

    def clear(self):
        """Reset all elements to zero."""
        self.array[:] = 0.0

    def replace_array(self, value):
        """Replaces an array with another array, if not present, it will be
        generated.
        """
        if isinstance(value, DenseFourIndex):
            self.array = value.array
        elif isinstance(value, np.ndarray):
            self.array = value
        else:
            raise ArgumentError(
                f"Do not know how to assign object of type {type(value)}."
            )

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
        """Return a copy of (a part of) the object

        **Optional arguments:**

        begin0, end0, begin1, end1, begin2, end2, begin3, end3
             Can be used to select a subblock of the object. When not given,
             the full range is used.
        """
        end0, end1, end2, end3 = self.fix_ends(end0, end1, end2, end3)
        result = DenseFourIndex(
            end0 - begin0, end1 - begin1, end2 - begin2, end3 - begin3
        )
        result.array[:] = self.array[
            begin0:end0, begin1:end1, begin2:end2, begin3:end3
        ]
        result.label = self._label
        return result

    def reshape(self, shape):
        """Reshape array

        **Optional arguments:**

        shape
             List containing the new dimension of each axis.
        """
        if len(shape) == 0:
            raise ArgumentError("No array shape given.")
        if len(shape) == 1:
            out = DenseOneIndex(shape[0])
        elif len(shape) == 2:
            out = DenseTwoIndex(shape[0], shape[1])
        elif len(shape) == 3:
            out = DenseThreeIndex(shape[0], shape[1], shape[2])
        elif len(shape) == 4:
            out = DenseFourIndex(shape[0], shape[1], shape[2], shape[3])
        out.array[:] = np.reshape(self.array, shape, order="C")
        return out

    def assign(self, other, ind=None, begin4=0, end4=None):
        """Assign with the contents of another object

        **Arguments:**

        other
             Another DenseXIndex object or a np ndarrray or float.

        ind
            If given, take only indices ``ind`` of other array.

        begin4, end4
             Can be used to select a subblock of the object. When not given,
             the full range is used.
        """
        self.check_type(
            "other",
            other,
            DenseFourIndex,
            np.ndarray,
            float,
            DenseTwoIndex,
            DenseOneIndex,
        )
        if isinstance(other, DenseFourIndex):
            if ind is not None:
                self.array[tuple(ind)] = other.array
            else:
                self.array[:] = other.array
        elif isinstance(other, float):
            if ind is not None:
                self.array[tuple(ind)] = other
            else:
                self.array[:] = other
        elif isinstance(other, np.ndarray):
            if other.shape == self.shape:
                self.array[:] = other
            elif ind is not None:
                self.array[ind] = other
            else:
                self.array[:] = other.reshape(
                    (self.nbasis, self.nbasis1, self.nbasis2, self.nbasis3)
                )
        elif isinstance(other, DenseTwoIndex):
            if ind is not None:
                self.array[tuple(ind)] = other.array
            else:
                self.array[:] = other.array.reshape(
                    (self.nbasis, self.nbasis1, self.nbasis2, self.nbasis3)
                )
        elif isinstance(other, DenseOneIndex):
            if ind is not None:
                end4 = other.fix_ends(end4)[0]
                self.array[ind] = other.array[begin4:end4]
            else:
                end4 = other.fix_ends(end4)[0]
                self.array[:] = other.array[begin4:end4].reshape(
                    (self.nbasis, self.nbasis1, self.nbasis2, self.nbasis3)
                )
        else:
            raise ArgumentError(
                f"Do not know how to assign object of type {type(other)}."
            )

    def assign_triu(self, other, begin4=0, end4=None, shape=None, k=0):
        """Assign upper triangular with the contents of another object
        Four-index object will be reshaped as (self.nbasis*self.nbasis1,self.nbasis2*self.nbasis3)
        during that operation.

        **Arguments:**

        other
             Another DenseFourIndex object or a np ndarrray or float.

        begin4, end4
             Can be used to select a subblock of the object. When not given,
             the full range is used.

        k
             (int) offset of matrix; k=0 corresponds to upper triangular matrix
             including the diagonal, k=1 excludes diagonal, etc.
        """
        self.check_type("other", other, DenseOneIndex, np.ndarray)
        if isinstance(other, DenseOneIndex):
            end4 = other.fix_ends(end4)[0]
            if shape is None:
                indtriu = np.triu_indices(self.nbasis * self.nbasis1, k)
                self.array.reshape(
                    self.nbasis * self.nbasis1, self.nbasis2 * self.nbasis3
                )[indtriu] = other.array[begin4:end4]
            else:
                raise NotImplementedError
        elif isinstance(other, np.ndarray):
            if other.ndim != 1:
                raise ArgumentError(
                    f"Do not know how to assign object of type {type(other)}."
                )
            if shape is None:
                indtriu = np.triu_indices(self.nbasis * self.nbasis1)
                self.array.reshape(
                    self.nbasis * self.nbasis1, self.nbasis2 * self.nbasis3
                )[indtriu] = other[begin4:end4]
            else:
                raise NotImplementedError
        else:
            raise ArgumentError(
                f"Do not know how to assign object of type {type(other)}."
            )

    def randomize(self):
        """Fill with random normal data"""
        self.array[:] = np.random.normal(0, 1, self.shape)

    def permute_basis(self, permutation):
        """Reorder the coefficients for a given permutation of basis functions.

        **Arguments:**

        permutation
             An integer numpy array that defines the new order of the basis
             functions.
        """
        self.array[:] = self.array.take(permutation, axis=0)
        self.array[:] = self.array.take(permutation, axis=1)
        self.array[:] = self.array.take(permutation, axis=2)
        self.array[:] = self.array.take(permutation, axis=3)

    def change_basis_signs(self, signs):
        """Correct for different sign conventions of the basis functions.

        **Arguments:**

        signs
             A numpy array with sign changes indicated by +1 and -1.
        """
        self.array *= signs
        self.array *= signs.reshape(-1, 1)
        self.array *= signs.reshape(-1, 1, 1)
        self.array *= signs.reshape(-1, 1, 1, 1)

    def get_triu(self, k=0):
        """Convert a four-index object into two-index with shape (nbasis*nbasis1,
        nbasis2*nbasis3) and return corresponding upper triangular matrix.

        **Arguments:**

        k
             (int) offset of matrix; k=0 corresponds to upper triangular matrix
             including the diagonal, k=1 excludes diagonal, etc.
        """
        if self.nbasis * self.nbasis1 != self.nbasis2 * self.nbasis3:
            msg = (
                f"Dimensions do not match ({self.nbasis * self.nbasis1} != "
                f"{self.nbasis2 * self.nbasis3}). "
                "Do not know how to reshape four-index object with dimensions "
                f"({self.nbasis},{self.nbasis1},{self.nbasis2},{self.nbasis3})"
                f" into an array of shape ({self.nbasis * self.nbasis1},"
                f"{self.nbasis2 * self.nbasis3})"
            )
            raise MatrixShapeError(msg)
        indtriu = np.triu_indices(self.nbasis * self.nbasis1, k)
        return self.array.reshape(
            self.nbasis * self.nbasis1, self.nbasis2 * self.nbasis3
        )[indtriu]

    def iadd(
        self,
        other,
        factor=1.0,
        begin0=0,
        end0=None,
        begin1=0,
        end1=None,
        begin2=0,
        end2=None,
        begin3=0,
        end3=None,
        begin4=0,
        end4=None,
        begin5=0,
        end5=None,
        begin6=0,
        end6=None,
        begin7=0,
        end7=None,
        ind=None,
    ):
        """Add another DenseFourIndex object in-place, multiplied by factor

        **Arguments:**

        other
             A DenseFourIndex instance to be added

        **Optional arguments:**

        factor
             The added term is scaled by this factor.

        begin0, end0, begin1, end1, begin2, end2, begin3, end3, ...
             Can be used to select a subblock of the object. When not given,
             the full range is used.

        ind
             FIXME
             If ind is provided, other will be added to view of array as
             indicated by ind. This only works for 2 index objects.
        """
        self.check_type("other", other, DenseFourIndex, DenseTwoIndex)
        self.check_type("factor", factor, float, int)
        end0, end1, end2, end3 = self.fix_ends(end0, end1, end2, end3)
        if ind is None:
            # only works with 4-index
            self.check_type("other", other, DenseFourIndex)
            end4, end5, end6, end7 = other.fix_ends(end4, end5, end6, end7)
            self.array[begin0:end0, begin1:end1, begin2:end2, begin3:end3] += (
                other.array[begin4:end4, begin5:end5, begin6:end6, begin7:end7]
                * factor
            )
        else:
            # only works with 2-index
            self.check_type("other", other, DenseTwoIndex)
            end4, end5 = other.fix_ends(end4, end5)
            self.array[tuple(ind)] += (
                other.array[begin4:end4, begin5:end5] * factor
            )

    def imul(self, other, factor=1.0):
        """In-place element-wise multiplication: ``self *= other * factor``

        **Arguments:**

        other
             A DenseFourIndex instance.

        **Optional arguments:**

        factor
             The four-index object is scaled by this factor.
        """
        self.check_type("other", other, DenseFourIndex)
        self.check_type("factor", factor, float, int)

        # def from_mask(mask):
        #    return {0: 1, 1: 2, 2: 4, 3: 8}[mask]

        # def to_mask(sym):
        #    return {1: 0, 2: 1, 4: 2, 8: 3}[sym]

        self.array *= other.array
        self.iscale(factor)

    def iscale(self, factor):
        """In-place multiplication with a scalar

        **Arguments:**

        factor
             A scalar factor.
        """
        self.check_type("factor", factor, float, int)
        self.array *= factor

    def get_element(self, i, j, k, l):  # redundant?
        """Return a matrix element"""
        return self.array[i, j, k, l]

    def set_element(self, i, j, k, l, value, symmetry=8):  # redundant?
        """Set a matrix element

        **Arguments:**

        i, j, k, l
             The matrix indexes to be set

        value
             The value to be assigned to the matrix element.

        **Optional arguments:**

        symmetry
             The level of symmetry to be enforced when setting the matrix
             element. See :ref:`dense_matrix_symmetry` for more details.
        """
        self.check_options("symmetry", symmetry, 1, 2, 4, 8)
        if not self.is_shape_symmetric(symmetry):
            raise SymmetryError(
                "FourIndex object does not have the right shape to impose the selected symmetry."
            )
        self.array[i, j, k, l] = value
        if symmetry in (2, 8):
            self.array[j, i, l, k] = value
        if symmetry in (4, 8):
            self.array[k, j, i, l] = value
            self.array[i, l, k, j] = value
            self.array[k, l, i, j] = value
        if symmetry == 8:
            self.array[l, k, j, i] = value
            self.array[j, k, l, i] = value
            self.array[l, i, j, k] = value

    def is_symmetric(self, symmetry=8, rtol=1e-5, atol=1e-8):
        """Check the symmetry of the array.

        **Optional arguments:**

        symmetry
             The symmetry to check. See :ref:`dense_matrix_symmetry`
             for more details. In addition to 1, 2, 4, 8, also 'cdab' is
             supported.

        rtol and atol
             relative and absolute tolerance. See to ``np.allclose``.
        """
        if not self.is_shape_symmetric(symmetry):
            return False
        result = True
        if symmetry in (2, 8):
            result &= np.allclose(
                self.array, self.array.transpose(1, 0, 3, 2), rtol, atol
            )
        if symmetry in (4, 8):
            result &= np.allclose(
                self.array, self.array.transpose(2, 3, 0, 1), rtol, atol
            )
            result &= np.allclose(
                self.array, self.array.transpose(2, 1, 0, 3), rtol, atol
            )
            result &= np.allclose(
                self.array, self.array.transpose(0, 3, 2, 1), rtol, atol
            )
        if symmetry == 8:
            result &= np.allclose(
                self.array, self.array.transpose(3, 2, 1, 0), rtol, atol
            )
            result &= np.allclose(
                self.array, self.array.transpose(3, 0, 1, 2), rtol, atol
            )
            result &= np.allclose(
                self.array, self.array.transpose(1, 2, 3, 0), rtol, atol
            )
        if symmetry == "cdab":
            result &= np.allclose(
                self.array, self.array.transpose(2, 3, 0, 1), rtol, atol
            )
        return result

    def is_shape_symmetric(self, symmetry):
        """Check whether the symmetry argument matches the shape"""
        result = True
        if symmetry in (2, 8):
            result &= self.nbasis == self.nbasis1
            result &= self.nbasis2 == self.nbasis3
        if symmetry in (4, 8):
            result &= self.nbasis == self.nbasis2
            result &= self.nbasis1 == self.nbasis3
            result &= self.nbasis == self.nbasis3
            result &= self.nbasis1 == self.nbasis2
        return result

    def symmetrize(self, symmetry=8):
        """Symmetrize in-place

        **Optional arguments:**

        symmetry
             The symmetry to impose. See :ref:`dense_matrix_symmetry` for
             more details.
        """
        self.check_options("symmetry", symmetry, 1, 2, 4, 8)
        # The implementation is relatively expensive (in terms of memory) but
        # results in exactly symmetrized four-index objects.
        if not self.is_shape_symmetric(symmetry):
            raise SymmetryError(
                "FourIndex object does not have the right shape for symmetrization."
            )
        if symmetry in (2, 8):
            self.array[:] = self.array + self.array.transpose(1, 0, 3, 2)
            self.iscale(0.5)
        if symmetry in (4, 8):
            self.array[:] = self.array + self.array.transpose(2, 3, 0, 1)
            self.array[:] = self.array + self.array.transpose(0, 3, 2, 1)
            self.iscale(0.25)

    def itranspose(self, transpose=None):
        """In-place transpose: ``0,1,2,3 -> 1,0,3,2``"""
        if transpose is None:
            self.array = self.array.transpose(1, 0, 3, 2)
        else:
            self.array = self.array.transpose(transpose)

    def sum(self):
        """Return the sum of all elements"""
        return np.sum(self.array)

    def iadd_exchange(self):
        """In-place addition of its own exchange contribution"""
        # Broken code, don't use
        # self.array -= np.einsum('abcd->abdc', self.array)
        # We cannot do inplace einsum. Instead use (and don't change):
        self.array = self.array - np.einsum("abcd->abdc", self.array)

    def iadd_transpose(self, transpose, other=None, factor=1.0):
        """In-place addition of transpose. If `other` is given (FourIndex),
        its transpose is added, otherwise (None) its own transpose is added.
        """
        self.check_type("factor", factor, float, int)
        self.check_type("other", other, type(None), DenseFourIndex)
        if other is None:
            self.array[:] = (
                self.array + self.array.transpose(transpose) * factor
            )
        else:
            self.array[:] = (
                self.array + other.array.transpose(transpose) * factor
            )

    def assign_four_index_transform(
        self,
        ao_integrals,
        exp0,
        exp1=None,
        exp2=None,
        exp3=None,
        method="tensordot",
        **kwargs,
    ):
        """Perform four index transformation.

        **Arguments:**

        oa_integrals
             A DenseFourIndex with integrals in atomic orbitals.

        exp0
             A DenseOrbital object with molecular orbitals

        **Optional arguments:**

        exp1, exp2, exp3
             Can be provided to transform each index differently.

        method
             (str) either ``einsum`` or ``tensordot`` (default) or
             ``opt_einsum`` or ``einsum_naive``.
             ``einsum_naive`` uses the conventional einsum operation using the
             naive and brute-force implementation "pqrs,pa,qb,rc,sd" and the
             ``opt`` argument switched to ``optimal``. It may result in the
             same performance as ``opt_einsum``. If ``False`` is chosen, the
             contraction will be extremly slow for large tensors.

        **Keyword arguments:**

        optimize
            Controls if intermediate optimization should occur according to the
            np.einsum documentation. This kwargs is only supported for the
            flavors ``einsum`` and ``einsum_naive``.

        """
        # parse arguments
        self.check_type("ao_integrals", ao_integrals, DenseFourIndex)
        exp0, exp1, exp2, exp3 = parse_four_index_transform_exps(
            exp0, exp1, exp2, exp3, DenseOrbital
        )
        # actual transform
        if method == "einsum":
            # The order of the dot products is according to literature
            # conventions.
            opt = kwargs.get("optimize", "optimal")
            self.array[:] = np.einsum(
                "sd,pqrs->pqrd",
                exp3.coeffs,
                ao_integrals.array,
                casting="no",
                order="C",
                optimize=opt,
            )
            self.array[:] = np.einsum(
                "rc,pqrd->pqcd",
                exp2.coeffs,
                self.array,
                casting="no",
                order="C",
                optimize=opt,
            )
            self.array[:] = np.einsum(
                "qb,pqcd->pbcd",
                exp1.coeffs,
                self.array,
                casting="no",
                order="C",
                optimize=opt,
            )
            self.array[:] = np.einsum(
                "pa,pbcd->abcd",
                exp0.coeffs,
                self.array,
                casting="no",
                order="C",
                optimize=opt,
            )
        elif method == "cupy" and PYBEST_CUPY_AVAIL:
            try:
                self.array[:] = cupy_helper(
                    "sd,pqrs->pqrd",
                    exp3.coeffs,
                    ao_integrals.array,
                    **kwargs,
                )
                self.array[:] = cupy_helper(
                    "rc,pqrd->pqcd",
                    exp2.coeffs,
                    self.array,
                    **kwargs,
                )
                self.array[:] = cupy_helper(
                    "qb,pqcd->pbcd",
                    exp1.coeffs,
                    self.array,
                    **kwargs,
                )
                self.array[:] = cupy_helper(
                    "pa,pbcd->abcd",
                    exp0.coeffs,
                    self.array,
                    **kwargs,
                )
            except MemoryError:
                if log.do_high:
                    log.warn("Not enough Video memory.")
                    log.warn("Defaulting to numpy.tensordot.")
                self.array[:] = np.tensordot(
                    ao_integrals.array, exp0.coeffs, axes=([0], [0])
                )
                self.array[:] = np.tensordot(
                    self.array, exp1.coeffs, axes=([0], [0])
                )
                self.array[:] = np.tensordot(
                    self.array, exp2.coeffs, axes=([0], [0])
                )
                self.array[:] = np.tensordot(
                    self.array, exp3.coeffs, axes=([0], [0])
                )
        elif method == "tensordot" or (
            method == "cupy" and not PYBEST_CUPY_AVAIL
        ):
            # because the way tensordot works, the order of the dot products is
            # not according to literature conventions.
            self.array[:] = np.tensordot(
                ao_integrals.array, exp0.coeffs, axes=([0], [0])
            )
            self.array[:] = np.tensordot(
                self.array, exp1.coeffs, axes=([0], [0])
            )
            self.array[:] = np.tensordot(
                self.array, exp2.coeffs, axes=([0], [0])
            )
            self.array[:] = np.tensordot(
                self.array, exp3.coeffs, axes=([0], [0])
            )
        elif method == "opt_einsum":
            self.array[:] = oe_contract(
                "pqrs,pa,qb,rc,sd",
                ao_integrals.array,
                exp0.coeffs,
                exp1.coeffs,
                exp2.coeffs,
                exp3.coeffs,
            )
        elif method == "einsum_naive":
            opt = kwargs.get("optimize", "optimal")
            self.array[:] = np.einsum(
                "pqrs,pa,qb,rc,sd",
                ao_integrals.array,
                exp0.coeffs,
                exp1.coeffs,
                exp2.coeffs,
                exp3.coeffs,
                casting="no",
                order="C",
                optimize=opt,
            )
        else:
            raise UnknownOption(
                "The method must either be 'einsum' or 'tensordot'."
            )
