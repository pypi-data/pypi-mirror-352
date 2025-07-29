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

# FIXME:
# - rename ``new()`` into ``clean_copy``
# - add (orbital-related) methods specific for HF to HF module or orbital_utils


r"""Dense matrix implementations

Naming scheme for the expand methods
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

* :py:class:`DenseTwoIndex`

  * ``symmetry=1``: Nothing is checked/enforced

  * ``symmetry=2``: Hermitian index symmetry is
    checked/enforced (default), i.e. :math:`\langle i \vert A \vert j
    \rangle = ` :math:`\langle j \vert A \vert i \rangle`


Dense matrix classes
--------------------
"""

from functools import reduce

import numpy as np
from scipy.linalg import (
    eig,
    eigh,
    eigvals,
    eigvalsh,
    inv,
    sqrtm,
)

from pybest.exceptions import ArgumentError, MatrixShapeError, SymmetryError
from pybest.linalg.base import TwoIndex
from pybest.log import log

from .dense_one_index import DenseOneIndex
from .dense_orbital import DenseOrbital


class DenseTwoIndex(TwoIndex):
    """Dense two-dimensional matrix."""

    # identification attribute
    dense_two_identifier = True

    #
    # Constructor and destructor
    #

    def __init__(self, nbasis, nbasis1=None, label=""):
        """
        **Arguments:**

        nbasis
             The number of basis functions. (Number of rows. Also number of
             columns, unless nbasis1 is given.)

        **Optional arguments:**

        nbasis1
             When given, this is the number of columns (second index).

        Note that by default the two-index object is assumed to be Hermitian.
        Only when nbasis1 is given, this assumption is dropped.

        label
             The name (label) of the instance to be created.
        """
        if nbasis1 is None:
            nbasis1 = nbasis
        self._array = np.zeros((nbasis, nbasis1), float)
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

    def __check_init_args__(self, nbasis, nbasis1=None):
        """Is self compatible with the given constructor arguments?

        nbasis, nbasis1
             The number of basis functions. Nbasis is a default value for other
             nbasisX arguments if not specified.
        """
        if nbasis1 is None:
            nbasis1 = nbasis
        assert nbasis == self.nbasis
        assert nbasis1 == self.nbasis1

    def __eq__(self, other):
        """Compare self with other"""
        return (
            isinstance(other, DenseTwoIndex)
            and other.nbasis == self.nbasis
            and other.nbasis1 == self.nbasis1
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
        label = grp.attrs["label"]
        result = cls(nbasis, nbasis1, label)
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
        grp.attrs["label"] = self.label

    def new(self):
        """Return a new two-index object with the same nbasis (and nbasis1)"""
        return DenseTwoIndex(self.nbasis, self.nbasis1)

    @staticmethod
    def einsum_index(script):
        """Returns indices to numpy.einsum summation."""
        if not len(script) == 2 and isinstance(script, str):
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
        """The other size of the two-index object"""
        return self.shape[1]

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
        if not ndarray.ndim == 2:
            raise ArgumentError("Only 2D array can be set.")
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
        other.__check_init_args__(self.nbasis, self.nbasis1)

    new.__check_init_args__ = _check_new_init_args

    def replace_array(self, value):
        """Replaces an array with another array, if not present, it will be
        generated.
        """
        if isinstance(value, DenseTwoIndex):
            self.array = value.array
        elif isinstance(value, np.ndarray):
            self.array = value
        else:
            raise ArgumentError(
                f"Do not know how to assign object of type {type(value)}."
            )

    def clear(self):
        """Reset all elements to zero."""
        self.array[:] = 0.0

    def copy(
        self, begin0=0, end0=None, begin1=0, end1=None, transpose: bool = False
    ):
        """Return a copy of (a part of) the object

        **Optional arguments:**

        begin0, end0, begin1, end1
             Can be used to select a subblock of the object. When not given,
             the full range is used. Only when the ranges are equal for both
             axes, an Hermitian two-index may be returned.
        transpose (bool):
            If True, the returned instance will be transposed.
        """
        end0, end1 = self.fix_ends(end0, end1)
        nbasis = end0 - begin0
        nbasis1 = end1 - begin1
        result = DenseTwoIndex(nbasis, nbasis1)
        if transpose is True:
            result.array[:] = (self.array[begin0:end0, begin1:end1]).T
        else:
            result.array[:] = self.array[begin0:end0, begin1:end1]

        result.label = self._label
        return result

    def ravel(self, begin0=0, end0=None, begin1=0, end1=None, ind=None):
        """Return a copy of (a part of) the object as a one-index object

        **Optional arguments:**

        begin0, end0, begin1, end1
             Can be used to select a subblock of the object. When not given,
             the full range is used. Only when the ranges are equal for both
             axes, an Hermitian two-index may be returned.

        ind
             2-Tuple of 1-dim arrays with row and column indices of TwoIndex
             object to be copied.
        """
        end0, end1 = self.fix_ends(end0, end1)
        nbasis = end0 - begin0
        nbasis1 = end1 - begin1
        if ind is None:
            result = DenseOneIndex(nbasis * nbasis1)
            result.array[:] = self.array[begin0:end0, begin1:end1].ravel(
                order="C"
            )
        else:
            if not ind[0].shape == ind[1].shape:
                raise ArgumentError("Number of array indices not identical.")
            result = DenseOneIndex(len(ind[0]))
            result.array[:] = (self.array[begin0:end0, begin1:end1])[
                ind
            ].ravel(order="C")
        return result

    def get_triu(self):
        """Convert a two-index object into one-index and return corresponding
        upper triangular matrix.
        """
        if self.nbasis != self.nbasis1:
            raise MatrixShapeError(
                "Do not know how to reshape two-index object."
            )
        indtriu = np.triu_indices(self.nbasis)
        return self.array[indtriu]

    def assign(
        self,
        other,
        ind=None,
        begin0=0,
        end0=None,
        begin1=0,
        end1=None,
        begin2=0,
        end2=None,
        begin3=0,
        end3=None,
    ):
        """Assign a new contents to the two-index object

        **Arguments:**

        other
             The new data, may be DenseTwoIndex, DenseOneIndex, a scalar
             value, or an ndarray.

        ind
             If provided, only these elements (of DenseOneIndex) are
             assigned

        begin0, end0, begin1, end1
             When given, specify the ranges where the contribution will be
             added. When not given, the full range is used.
        """
        end0, end1 = self.fix_ends(end0, end1)
        dim0 = end0 - begin0
        dim1 = end1 - begin1
        if isinstance(other, DenseTwoIndex):
            end2, end3 = other.fix_ends(end2, end3)
            self.array[begin0:end0, begin1:end1] = other.array[
                begin2:end2, begin3:end3
            ]
        elif isinstance(other, (float, int)):
            self.array[begin0:end0, begin1:end1] = other
        elif isinstance(other, np.ndarray):
            if ind is None:
                if other.shape == self.shape:
                    self.array[:] = other
                else:
                    if end2 is None:
                        end2 = other.size
                    self.array[begin0:end0, begin1:end1] = other[
                        begin2:end2
                    ].reshape((dim0, dim1))
            else:
                self.array[begin0:end0, begin1:end1][ind] = other
        elif isinstance(other, DenseOneIndex):
            end2 = other.fix_ends(end2)[0]
            if ind is None:
                self.array[begin0:end0, begin1:end1] = (
                    other.array[begin2:end2]
                ).reshape((dim0, dim1))
            else:
                self.array[begin0:end0, begin1:end1][ind] = other.array[
                    begin2:end2
                ]
        else:
            raise ArgumentError(
                f"Do not know how to assign object of type {type(other)}"
            )

    def assign_dot(self, other, tf2):
        """Dot product of orbitals in a DenseOrbital and TwoIndex object

        **Arguments:**

        other
             An expansion object with input orbitals

        tf2
             A two-index object

        The transformed array is stored in self.
        """
        self.check_type("other", other, DenseOrbital)
        self.check_type("tf2", tf2, DenseTwoIndex)
        if not self.nbasis == other.nbasis:
            raise MatrixShapeError(
                "Both expansions must have the same number of basis functions."
            )
        if not (tf2.shape[0] == other.nfn and tf2.shape[1] == self.shape[1]):
            raise MatrixShapeError(
                "The shape of the two-index object is incompatible with that of the expansions."
            )
        self.array[:] = np.dot(other.coeffs, tf2.array)

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
        transpose=False,
    ):
        """Add another DenseTwoIndex object in-place, multiplied by factor. If
        begin0, end0, begin1, end1 are specified, other is added to the
        selected range.

        **Arguments:**

        other
             A DenseTwoIndex, DenseOneIndex instance or float to be added

        **Optional arguments:**

        factor
             When given, a factor scaling the result of the computation.

        begin0, end0, begin1, end1
             When given, specify the ranges where the contribution will be
             added. When not given, the full range is used.
        """
        self.check_type("factor", factor, float, int)
        end0, end1 = self.fix_ends(end0, end1)
        if isinstance(other, DenseTwoIndex):
            end2, end3 = other.fix_ends(end2, end3)
            if transpose:
                self.array[begin0:end0, begin1:end1] += (
                    (other.array[begin2:end2, begin3:end3]).T * factor
                )
            else:
                self.array[begin0:end0, begin1:end1] += (
                    other.array[begin2:end2, begin3:end3] * factor
                )
        elif isinstance(other, float):
            self.array[begin0:end0, begin1:end1] += other * factor
        elif isinstance(other, DenseOneIndex):
            end2 = other.fix_ends(end2)[0]
            if transpose:
                self.array[begin0:end0, begin1:end1] += (
                    other.array[begin2:end2] * factor
                )
            else:
                self.array[begin0:end0, begin1:end1] += (
                    (other.array[begin2:end2])[np.newaxis].T * factor
                )
        else:
            raise ArgumentError(
                "Do not know how to add in-place an object of type"
                f" {type(other)}."
            )

    def iadd_t(
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
    ):
        """See :py:meth:`DenseTwoIndex.iadd`, transpose=True"""
        self.iadd(
            other,
            factor,
            begin0,
            end0,
            begin1,
            end1,
            begin2,
            end2,
            begin3,
            end3,
            True,
        )

    def iadd_diagonal(self, other, factor=1.0, begin0=0, end0=None):
        """Add to diagonal of DenseTwoIndex object in-place, multiplied by
        factor.

        **Arguments:**

        other
             Another DenseOneIndex object or an scalar.

        **Optional arguments:**

        factor
             When given, a factor scaling the result of the computation.

        begin0, end0, begin1, end1
             When given, specify the ranges of contribution to be
             added. When not given, the full range is used.
        """
        self.check_type("factor", factor, float, int)
        self.check_type("other", other, DenseOneIndex, float)
        end1 = None
        end0, end1 = self.fix_ends(end0, end1)
        if isinstance(other, DenseOneIndex):
            for i, j in zip(range(begin0, end0), range(end0 - begin0)):
                self.array[i, i] += other.array[j] * factor
        elif isinstance(other, float):
            for i in range(begin0, end0):
                self.array[i, i] += other * factor

    def iscale(self, factor):
        """In-place multiplication with a scalar

        **Arguments:**

        factor
             A scalar factor.
        """
        self.check_type("factor", factor, float, int)
        self.array *= factor

    def iortho(self):
        """In-place orthogonalization"""
        matrix, _ = np.linalg.qr(self.array, mode="complete")
        self.array[:] = matrix

    def randomize(self):
        """Fill with random normal data"""
        self.array[:] = np.random.normal(0, 1, self.shape)

    def permute_basis(self, permutation):
        """Reorder the coefficients for a given permutation of basis functions.

        The same permutation is applied to all indexes.

        **Arguments:**

        permutation
             An integer numpy array that defines the new order of the basis
             functions.
        """
        self.array[:] = self.array.take(permutation, axis=0)
        self.array[:] = self.array.take(permutation, axis=1)

    def permute(self, permutation):
        """Reorder the coefficients for a given permutation of columns.

        **Arguments:**

        permutation
             An integer numpy array that defines the new order of the
             orbitals.
        """
        self.array[:] = self.array[:, permutation]

    def change_basis_signs(self, signs):
        """Correct for different sign conventions of the basis functions.

        **Arguments:**

        signs
             A numpy array with sign changes indicated by +1 and -1.
        """
        self.array *= signs
        self.array *= signs.reshape(-1, 1)

    def get_element(self, i, j):
        """Return a matrix element"""
        return self.array[i, j]

    def set_element(self, i, j, value, symmetry=2):
        """Set a matrix element

        **Arguments:**

        i, j
             The matrix indexes to be set

        value
             The value to be assigned to the matrix element.

        **Optional arguments:**

        symmetry
             When 2 (the default), the element (j,i) is set to the same
             value. When set to 1 the opposite off-diagonal is not set. See
             :ref:`dense_matrix_symmetry` for more details.
        """
        self.check_options("symmetry", symmetry, 1, 2)
        if not self.is_shape_symmetric(symmetry):
            raise SymmetryError(
                "TwoIndex object does not have the right shape to impose the selected symmetry."
            )
        self.array[i, j] = value
        if symmetry == 2:
            self.array[j, i] = value

    def sum(self, begin0=0, end0=None, begin1=0, end1=None):
        """Return the sum of all elements (in the selected range)

        **Optional arguments:**

        begin0, end0, begin1, end1
             Can be used to select a subblock of the object to be contracted.
        """
        end0, end1 = self.fix_ends(end0, end1)
        return self.array[begin0:end0, begin1:end1].sum()

    def trace(self, begin0=0, end0=None, begin1=0, end1=None):
        """Return the trace of the two-index object.

        **Optional arguments:**

        begin0, end0, begin1, end1
             Can be used to select a subblock of the object to be contracted.
        """
        end0, end1 = self.fix_ends(end0, end1)
        if end0 - begin0 != end1 - begin1:
            raise ArgumentError(
                "Only the trace of a square (part of a) two-index object can be computed."
            )
        return np.trace(self.array[begin0:end0, begin1:end1])

    def itranspose(self):
        """In-place transpose"""
        self.array[:] = self.array.T

    def inner(self, vec0, vec1):
        """Compute an inner product of two vectors using the two-index as a metric

        **Arguments:**

        vec0, vec1
             The vectors, either DenseOneIndex or numpy arrays.
        """
        if vec0.shape != (self.shape[0],):
            raise MatrixShapeError(
                "The length of vec0 does not match the shape of the two-index object."
            )
        if vec1.shape != (self.shape[1],):
            raise MatrixShapeError(
                "The length of vec1 does not match the shape of the two-index object."
            )
        if isinstance(vec0, DenseOneIndex) and isinstance(vec1, DenseOneIndex):
            return np.dot(vec0.array, np.dot(self.array, vec1.array))
        if isinstance(vec0, np.ndarray) and isinstance(vec1, np.ndarray):
            return np.dot(vec0, np.dot(self.array, vec1))
        raise ArgumentError(
            "Do not know how to compute inner product with objects of "
            f"type {type(vec0)} and {type(vec1)}"
        )

    def sqrt(self):
        """Return the real part of the square root of two-index object"""
        out = DenseTwoIndex(self.nbasis, self.nbasis1)
        out.array[:] = sqrtm(self.array).real
        return out

    def inverse(self):
        """Return the inverse of two-index object"""
        out = DenseTwoIndex(self.nbasis, self.nbasis1)
        out.array[:] = inv(self.array)
        return out

    def diagonalize(self, eigvec=False, use_eigh=False):
        """Return eigenvalues (DenseOneIndex) and eigenvectors (DenseTwoIndex,
        default False) of two-index object using different scipy.linalg methods:
        eig, eigh, eigvals, or eigvalsh. Thus, the array needs to be square.
        """

        def choose_method():
            if eigvec and use_eigh:
                return list(eigh(self.array))
            if eigvec and not use_eigh:
                return list(eig(self.array))
            if use_eigh:
                return [eigvalsh(self.array)]
            return [eigvals(self.array)]

        result = choose_method()
        out_e = DenseOneIndex(self.nbasis)
        out_e.array[:] = result[0]
        if eigvec:
            out_v = DenseTwoIndex(self.nbasis, self.nbasis1)
            out_v.array[:] = result[1]
            return out_e, out_v
        return out_e

    def det(self):
        """Return determinant of two-index object"""
        if self.nbasis != self.nbasis1:
            raise MatrixShapeError(
                f"Array has the wrong shape {self.nbasis} x {self.nbasis1}"
            )
        (sign, logdet) = np.linalg.slogdet(self.array)
        out = sign * np.exp(logdet)
        return out

    def idivide(self, other, factor=1.0):
        """Divide self by other DenseTwoIndex object element-wise, multiplied
        by factor

        **Arguments:**

        other
             A DenseTwoIndex instance used as denominator

        **Optional arguments:**

        factor
             When given, a factor scaling the result of the computation.

        """
        self.check_type("other", other, DenseTwoIndex)
        self.check_type("factor", factor, float, int)
        if self.shape != other.shape:
            raise MatrixShapeError(
                "The output argument has the incorrect shape."
            )
        self.array[:] = np.divide(self.array, other.array) * factor

    def divide(
        self,
        other,
        factor=1.0,
        out=None,
        begin0=0,
        end0=None,
        begin1=0,
        end1=None,
    ):
        """Divide two DenseTwoIndex object, multiplied by factor, and return
        output

        **Arguments:**

        other
             A DenseTwoIndex instance to be divided. If DenseOneIndex,
             the object will be reshaped assuming C-order.

        **Optional arguments:**

        factor
             When given, a factor scaling the result of the computation.

        out
             The output DenseTwoIndex
        """
        end0, end1 = self.fix_ends(end0, end1)
        self.check_type("other", other, DenseTwoIndex, DenseOneIndex)
        self.check_type("factor", factor, float, int)
        if out is None:
            out = DenseTwoIndex((end0 - begin0), (end1 - begin1))
        else:
            self.check_type("out", out, DenseTwoIndex)
            if out.shape != self.array[begin0:end0, begin1:end1].shape:
                raise MatrixShapeError(
                    "The output argument has the incorrect shape."
                )
            if isinstance(other, DenseTwoIndex):
                if out.shape != other.shape:
                    raise MatrixShapeError(
                        "The output argument has the incorrect shape."
                    )
        if isinstance(other, DenseOneIndex):
            out.array[:] = (
                np.divide(
                    self.array[begin0:end0, begin1:end1],
                    other.array.reshape(self.nbasis, self.nbasis1),
                )
                * factor
            )
        else:
            out.array[:] = (
                np.divide(self.array[begin0:end0, begin1:end1], other.array)
                * factor
            )
        return out

    def assign_diagonal(self, value, factor=1.0, begin=0, end=None):
        """Set diagonal elements to value

        **Arguments:**

        value
             Either a scalar or a DenseOneIndex object
        """
        end, end1 = self.fix_ends(end, end)
        assert end == end1
        if isinstance(value, DenseOneIndex):
            np.fill_diagonal(
                self.array[begin:end, begin:end], value.array * factor
            )
        elif isinstance(value, np.ndarray):
            np.fill_diagonal(self.array[begin:end, begin:end], value * factor)
        elif isinstance(value, float):
            np.fill_diagonal(self.array[begin:end, begin:end], value * factor)
        elif isinstance(value, DenseTwoIndex):
            np.fill_diagonal(
                self.array[begin:end, begin:end],
                value.array.ravel(order="C") * factor,
            )
        else:
            raise ArgumentError(
                "Do not know how to set diagonal with object of type "
                f"{type(value)}"
            )

    def copy_diagonal(self, out=None, begin=0, end=None):
        """Copy (part of) the diagonal of the two-index object

        **Optional arguments:**

        out
             The output argument (DenseOneIndex with proper size).

        begin, end
             Can be used to select a range of the diagonal. If not given,
             then the entire diagonal is copied.
        """
        if not self.shape[0] == self.shape[1]:
            raise MatrixShapeError(
                "The diagonal can only be copied when the two-index object is squared."
            )
        end, end1 = self.fix_ends(end, end)
        assert end == end1
        if out is None:
            out = DenseOneIndex(end - begin)
        else:
            self.check_type("out", out, DenseOneIndex)
            if out.shape != (end - begin,):
                raise MatrixShapeError(
                    "The output argument has the incorrect shape."
                )
        out.array[:] = np.diagonal(self.array[begin:end, begin:end])
        return out

    def is_symmetric(self, symmetry=2, rtol=1e-5, atol=1e-8):
        """Check the symmetry of the array.

        **Optional arguments:**

        symmetry
             The symmetry to check. See :ref:`dense_matrix_symmetry`
             for more details.

        rtol and atol
             relative and absolute tolerance. See to ``np.allclose``.
        """
        self.check_options("symmetry", symmetry, 1, 2)
        if not self.is_shape_symmetric(symmetry):
            return False
        if symmetry == 2:
            return np.allclose(self.array, self.array.T, rtol, atol)
        return True

    def is_shape_symmetric(self, symmetry):
        """Check whether the symmetry argument matches the shape"""
        return symmetry == 1 or self.nbasis == self.nbasis1

    def check_symmetric(self, rtol=1e-5, atol=1e-8):
        """Check the symmetry of the array.

        **Optional arguments:**

        rtol and atol
             relative and absolute tolerance. See to ``np.allclose``.
        """
        return np.allclose(self.array, self.array.T, rtol, atol)

    def symmetrize(self, symmetry=2):
        """Symmetrize in-place

        **Optional arguments:**

        symmetry
             The symmetry to impose. See :ref:`dense_matrix_symmetry` for
             more details.
        """
        self.check_options("symmetry", symmetry, 1, 2)
        if not self.is_shape_symmetric(symmetry):
            raise SymmetryError(
                "TwoIndex object does not have the right shape for symmetrization."
            )
        if symmetry == 2:
            self.array[:] = self.array + self.array.T
            self.iscale(0.5)

    def iadd_outer(self, other0, other1, factor=1.0):
        """In-place addition of outer product of two other DenseTwoIndex

        **Arguments:**

        other0, other1
             Two-index objects that go into the outer product. They are
             raveled before taking the outer product.

        **Optional arguments:**

        factor
             When given, a factor scaling the result of the computation.
        """
        self.check_type("other0", other0, DenseTwoIndex)
        self.check_type("other1", other1, DenseTwoIndex)
        self.check_type("factor", factor, float, int)
        self.array += (
            np.outer(other0.array.ravel(), other1.array.ravel()) * factor
        )

    def iadd_kron(self, other0, other1, factor=1.0):
        """In-place addition of kronecker product of two other DenseTwoIndex

        **Arguments:**

        other0, other1
             Two-index objects that go into the kronecker product.

        **Optional arguments:**

        factor
             The term added is scaled by this factor.
        """
        self.check_type("other0", other0, DenseTwoIndex)
        self.check_type("other1", other1, DenseTwoIndex)
        self.check_type("factor", factor, float, int)
        self.array += np.kron(other0.array, other1.array) * factor

    def iadd_dot(
        self,
        other0,
        other1,
        factor=1.0,
        begin0=0,
        end0=None,
        begin1=0,
        end1=None,
        begin2=0,
        end2=None,
        begin3=0,
        end3=None,
    ):
        """In-place addition of dot product: ``other0 * other1``

        **Arguments:**

        other0, other1
             Two-index objects that go into the kronecker product.

        **Optional arguments:**

        factor
             The term added is scaled by this factor.

        begin0, end0, begin1, end1
             Can be used to select a subblock of the other0 object. When
             not given, the full range is used.

        begin2, end2, begin3, end3
             Can be used to select a subblock of the other1 object. When
             not given, the full range is used.
        """
        self.check_type("other0", other0, DenseTwoIndex)
        self.check_type("other1", other1, DenseTwoIndex)
        self.check_type("factor", factor, float, int)
        end0, end1 = other0.fix_ends(end0, end1)
        end2, end3 = other1.fix_ends(end2, end3)
        self.array[:] += (
            np.dot(
                other0.array[begin0:end0, begin1:end1],
                other1.array[begin2:end2, begin3:end3],
            )
            * factor
        )

    def iadd_tdot(self, other0, other1, factor=1.0):
        """In-place addition of dot product: ``other0.T * other1``

        **Arguments:**

        other0, other1
             Two-index objects that go into the kronecker product.

        **Optional arguments:**

        factor
             When given, a factor scaling the result of the computation.
        """
        self.check_type("other0", other0, DenseTwoIndex)
        self.check_type("other1", other1, DenseTwoIndex)
        self.check_type("factor", factor, float, int)
        self.array[:] += np.dot(other0.array.T, other1.array) * factor

    def iadd_dott(self, other0, other1, factor=1.0):
        """In-place addition of dot product: ``other0 * other1.T``

        **Arguments:**

        other0, other1
             Two-index objects that go into the kronecker product.

        **Optional arguments:**

        factor
             When given, a factor scaling the result of the computation.
        """
        self.check_type("other0", other0, DenseTwoIndex)
        self.check_type("other1", other1, DenseTwoIndex)
        self.check_type("factor", factor, float, int)
        self.array[:] += np.dot(other0.array, other1.array.T) * factor

    def iadd_transform(self, other, omega, factor=1.0, transpose=False):
        """Perform transformation: ``self += omega.T * other * omega``

        **Arguments:**

        other
             Something computed in some basis

        omega
             The transformation matrix.

        **Optional arguments:**

        transpose
             When given, the following is computed: ``omega * other * omega.T``
        """
        if transpose:
            self.array[:] += (
                reduce(np.dot, [omega.array, other.array, omega.array.T])
                * factor
            )
        else:
            self.array[:] += (
                reduce(np.dot, [omega.array.T, other.array, omega.array])
                * factor
            )

    def iadd_mult(
        self,
        other0,
        other1,
        factor=1.0,
        begin0=0,
        end0=None,
        begin1=0,
        end1=None,
        begin2=0,
        end2=None,
        begin3=0,
        end3=None,
        transpose0=False,
        transpose1=False,
    ):
        """In-place addition of multiplication: ``other0 * other1``

        **Arguments:**

        other0, other1
             Two-index objects that go into the product.

        **Optional arguments:**

        factor
             The term added is scaled by this factor.

        begin0, end0, begin1, end1
             Can be used to select a subblock of the other0 object. When
             not given, the full range is used.

        begin2, end2, begin3, end3
             Can be used to select a subblock of the other1 object. When
             not given, the full range is used.

        transpose0, transpose1
             Can be used to select transpose of other0, other1 objects
        """
        self.check_type("other0", other0, DenseTwoIndex)
        self.check_type("other1", other1, DenseTwoIndex)
        self.check_type("factor", factor, float, int)
        self.check_type("transpose0", transpose0, bool)
        self.check_type("transpose1", transpose1, bool)
        end0, end1 = other0.fix_ends(end0, end1)
        end2, end3 = other1.fix_ends(end2, end3)
        if transpose0 and transpose1:
            self.array[:] += (
                other0.array[begin0:end0, begin1:end1].T
                * other1.array[begin2:end2, begin3:end3].T
            ) * factor
        elif transpose0:
            self.array[:] += (
                other0.array[begin0:end0, begin1:end1].T
                * other1.array[begin2:end2, begin3:end3]
            ) * factor
        elif transpose1:
            self.array[:] += (
                other0.array[begin0:end0, begin1:end1]
                * other1.array[begin2:end2, begin3:end3].T
            ) * factor
        else:
            self.array[:] += (
                other0.array[begin0:end0, begin1:end1]
                * other1.array[begin2:end2, begin3:end3]
            ) * factor

    def iadd_one_mult(
        self, other0, other1, factor=1.0, transpose0=False, transpose1=False
    ):
        """In-place addition of multiplication: ``other0 * other1``

        **Arguments:**

        other0, other1
             One-index objects that go into the product.

        **Optional arguments:**

        factor
             When given, a factor scaling the result of the computation.

        transpose0, transpose1
             Can be used to select transpose of one-index objects.
        """
        self.check_type("other0", other0, DenseOneIndex)
        self.check_type("other1", other1, DenseOneIndex)
        self.check_type("factor", factor, float, int)
        self.check_type("transpose0", transpose0, bool)
        self.check_type("transpose1", transpose1, bool)
        if transpose0 and transpose1:
            self.array[:] += (
                other0.array[np.newaxis].T * other1.array[np.newaxis].T
            ) * factor
        elif transpose0:
            self.array[:] += (
                other0.array[np.newaxis].T * other1.array
            ) * factor
        elif transpose1:
            self.array[:] += (
                other0.array * other1.array[np.newaxis].T
            ) * factor
        else:
            self.array[:] += (other0.array * other1.array) * factor

    def iadd_shift(self, lshift):
        """Add positive shift to elements. If negative subtract shift

        **Arguments:**

        lshift
             A scalar used to augment the matrix elements.
        """
        self.check_type("lshift", lshift, float, int)
        self.array[self.array >= 0] += lshift
        self.array[self.array < 0] -= lshift

    def idot(self, other, transpose=False):
        """In-place dot product: self = self * other

        **Arguments:**

        other
             The other array.
        """
        self.check_type("other", other, DenseTwoIndex, DenseOrbital)
        if isinstance(other, DenseTwoIndex):
            if transpose:
                self.array = np.dot(self.array, other.array.T)
            else:
                self.array = np.dot(self.array, other.array)
        else:
            if transpose:
                self.array = np.dot(self.array, other.coeffs.T)
            else:
                self.array = np.dot(self.array, other.coeffs)

    def idot_t(self, other):
        """In-place dot product: self = self * other

        **Arguments:**

        other
             The other array.
        """
        self.idot(other, transpose=True)

    def imul(
        self, other, factor=1.0, begin2=0, end2=None, begin3=0, end3=None
    ):
        """In-place element-wise multiplication: ``self *= other * factor``

        **Arguments:**

        other
             A DenseOneIndex or DenseTwoIndex instance.

        **Optional arguments:**

        factor
             The two-index object is scaled by this factor.

        begin0, end0, begin1, end1
             Can be used to select a subblock of the (other) object. When
             not given, the full range is used.
        """
        self.check_type("other", other, DenseOneIndex, DenseTwoIndex)
        self.check_type("factor", factor, float, int)
        if isinstance(other, DenseTwoIndex):
            end2, end3 = other.fix_ends(end2, end3)
            self.array *= other.array[begin2:end2, begin3:end3]
        else:
            end2 = other.fix_ends(end2)[0]
            self.array *= other.array[begin2:end2]
        self.iscale(factor)

    def imul_t(
        self, other, factor=1.0, begin2=0, end2=None, begin3=0, end3=None
    ):
        """In-place element-wise multiplication: ``self *= other.T * factor``

        **Arguments:**

        other
             A DenseTwoIndex instance.

        **Optional arguments:**

        factor
             The two-index object is scaled by this factor.

        begin0, end0, begin1, end1
             Can be used to select a subblock of the (other) object. When
             not given, the full range is used.
        """
        self.check_type("other", other, DenseTwoIndex)
        self.check_type("factor", factor, float, int)
        end2, end3 = other.fix_ends(end2, end3)
        self.array *= other.array[begin2:end2, begin3:end3].T
        self.iscale(factor)

    def itransform(self, omega, factor=1.0, transpose=False):
        """Perform transformation: ``self = omega.T * self * omega``

        **Arguments:**

        omega
             The transformation matrix.

        **Optional arguments:**

        factor
             When given, a factor scaling the result of the computation.

        transpose
             When given, the following is computed: ``omega * other * omega.T``
        """
        if transpose:
            self.array[:] = (
                reduce(np.dot, [omega.array, self.array, omega.array.T])
                * factor
            )
        else:
            self.array[:] = (
                reduce(np.dot, [omega.array.T, self.array, omega.array])
                * factor
            )

    def distance_inf(self, other):
        """The infinity norm distance between self and other

        **Arguments:**

        other
             A DenseTwoIndex instance.
        """
        self.check_type("other", other, DenseTwoIndex)
        return abs(self.array.ravel() - other.array.ravel()).max()

    def iabs(self):
        """In-place absolute values"""
        self.array[:] = abs(self.array)

    def assign_two_index_transform(self, ao_integrals, exp0, exp1=None):
        """Perform two index transformation: ``exp0.T * ao_integrals * exp0``

        **Arguments:**

        ao_integrals
             Something computed in the atomic orbital basis

        exp0
             The molecular orbitals.

        **Optional arguments:**

        exp1
             When given, the following is computed: ``exp0.T * ao_integrals *
             exp1``
        """
        if exp1 is None:
            exp1 = exp0
        self.array[:] = reduce(
            np.dot, [exp0.coeffs.T, ao_integrals.array, exp1.coeffs]
        )

    def sort(self, vector: DenseOneIndex) -> None:
        """Sort a DenseTwoIndex object based on sorting of DenseOneIndex object

        Args:
            vector (DenseOneIndex): A DenseOneIndex instance that will be sorted and provide
            indices that will sort the DenseTwoIndex object
        """
        sorted_indices = vector.sort_indices(reverse=False)
        self.array = self.array[:, sorted_indices]
