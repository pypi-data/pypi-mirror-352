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


"""

import numpy as np

from pybest.exceptions import ArgumentError, MatrixShapeError
from pybest.linalg.base import OneIndex
from pybest.log import log


class DenseOneIndex(OneIndex):
    """Dense one-dimensional matrix (vector)

    This is also used for (diagonal) density matrices.
    """

    # identification attribute
    dense_one_identifier = True

    #
    # Constructor and destructor
    #

    def __init__(self, nbasis, label=""):
        """
        **Arguments:**

        nbasis
             The number of basis functions.

        label
             The name (label) of the instance to be created.
        """
        self._array = np.zeros((nbasis,), float)
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

    def __check_init_args__(self, nbasis):
        """Is self compatible with the given constructor arguments?

        nbasis
             The number of basis functions.
        """
        assert nbasis == self.nbasis

    def __eq__(self, other):
        """Compare self with other

        other
             Another DenseOneIndex object or an array.
        """
        return (
            isinstance(other, DenseOneIndex)
            and other.nbasis == self.nbasis
            and (other.array == self.array).all()
        )

    def __lt__(self, other):
        """Compare self with other

        other
             Another DenseOneIndex object or a scalar.
        """
        if isinstance(other, DenseOneIndex):
            assert other.nbasis == self.nbasis
            return (abs(self.array <= other.array)).all()
        if isinstance(other, float):
            return (abs(self.array <= other)).all()
        raise ArgumentError(f"{type(other)} is of an unsupported type.")

    @classmethod
    def from_hdf5(cls, grp):
        """Construct an instance from data previously stored in an h5py.Group.

        **Arguments:**

        grp
             An h5py.Group object.
        """
        nbasis = grp["array"].shape[0]
        label = grp.attrs["label"]
        result = cls(nbasis, label)
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
        """Return a new one-index object with the same nbasis"""
        return DenseOneIndex(self.nbasis)

    @staticmethod
    def einsum_index(script):
        """Returns indices to numpy.einsum summation."""
        if not len(script) == 1 and isinstance(script, str):
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
        if not ndarray.ndim == 1:
            raise ArgumentError("Only 1D array can be set.")
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
        other.__check_init_args__(self.nbasis)

    new.__check_init_args__ = _check_new_init_args

    def replace_array(self, value):
        """Replaces an array with another array, if not present, it will be
        generated.
        """
        if isinstance(value, DenseOneIndex):
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

    def copy(self, begin=0, end=None):
        """Return a copy of (a part of) the object

        **Optional arguments:**

        begin, end
             Can be used to select a subblock of the object. When not given,
             the full range of other object is used.
        """
        if end is None:
            end = self.nbasis
        result = DenseOneIndex(end - begin)
        result.array[:] = self.array[begin:end]
        result.label = self._label
        return result

    def assign(
        self, other, begin0=0, end0=None, begin1=0, end1=None, ind1=None
    ):
        """Assign with the contents of another object

        **Arguments:**

        other
             Another DenseOneIndex object or a scalar.

        **Optional arguments:**

        begin0, end0, begin1, end1
             Can be used to select a subblock of the object. When not given,
             the full range of other object is used.

        ind1
            Take only indices ``ind1`` of other array. Only supported for
            TwoIndex, ThreeIndex, or FourIndex
        """
        end0 = self.fix_ends(end0)[0]
        if isinstance(other, DenseOneIndex):
            end1 = other.fix_ends(end1)[0]
            self.array[begin0:end0] = other.array[begin1:end1]
        elif isinstance(other, (float, int)):
            self.array[begin0:end0] = other
        elif isinstance(other, np.ndarray):
            if end1 is None:
                end1 = other.size
            self.array[begin0:end0] = other[begin1:end1]
        elif ind1 is not None:
            self.array[begin0:end0] = other.array[ind1]
        #        elif isinstance(other, DenseThreeIndex):
        elif hasattr(other, "dense_three_identifier"):
            if end1 is None:
                end1 = other.array.size
            self.array[begin0:end0] = (other.array.ravel(order="C"))[
                begin1:end1
            ]
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
        self.array[:] = self.array[permutation]

    def change_basis_signs(self, signs):
        """Correct for different sign conventions of the basis functions.

        **Arguments:**

        signs
             A numpy array with sign changes indicated by +1 and -1.
        """
        self.array *= signs

    def iadd(
        self, other, factor=1.0, begin0=0, end0=None, begin1=0, end1=None
    ):
        """Add another DenseOneIndex object in-place, multiplied by factor

        **Arguments:**

        other
             A DenseOneIndex instance to be added

        **Optional arguments:**

        factor
             A scalar factor

        begin0, end0, begin1, end1
             Can be used to select a subblock of the object. When not given,
             the full range is used.
        """
        self.check_type("other", other, DenseOneIndex, np.ndarray, float)
        self.check_type("factor", factor, float, int)
        end0 = self.fix_ends(end0)[0]
        if isinstance(other, DenseOneIndex):
            end1 = other.fix_ends(end1)[0]
            self.array[begin0:end0] += other.array[begin1:end1] * factor
        elif isinstance(other, float):
            self.array[begin0:end0] += other * factor
        elif isinstance(other, np.ndarray):
            if other.ndim != 1:
                raise TypeError(
                    f"Wrong dimension of the {type(other)}: expected 1, got {other.ndim}."
                )
            if end1 is None:
                end1 = other.size
            self.array[begin0:end0] += other[begin1:end1] * factor

    def iscale(self, factor):
        """In-place multiplication with a scalar

        **Arguments:**

        factor
             A scalar factor.
        """
        self.check_type("factor", factor, float, int)
        self.array *= factor

    def norm(self):
        """Calculate L2 norm"""
        return np.linalg.norm(self.array, ord=2)

    def trace(self, begin0=0, end0=None):
        """Calculate trace

        **Optional arguments:**

        begin0, end0
             Can be used to select a subblock of the object. When not given,
             the full range is used.
        """
        end0 = self.fix_ends(end0)[0]
        return np.sum(self.array[begin0:end0])

    def get_element(self, i):
        """Return a matrix element"""
        return self.array[i]

    def get_max(self, absolute=True):
        """Return maximum (absolute) element"""
        if absolute:
            return np.max(np.abs(self.array))
        return np.max(self.array)

    def set_element(self, i, value):
        """Set a matrix element

        i
            Element number i+1 of array.

        value
            Value array element will be set to.
        """
        self.array[i] = value

    def get_nonzero(self):
        """Get indices of all non-zero elements"""
        return np.nonzero(self.array)[0]

    def sort_indices(self, reverse=False, begin0=0, end0=None):
        """Return indices of sorted arguments in decreasing order

        **Optional arguements**

        reverse
             If True search order is reversed to increasing arguements

        begin0, end0
             Can be used to select a subblock of the object. When not given,
             the full range is used.
        """
        end0 = self.nbasis
        if reverse:
            return np.argsort(
                self.array[begin0:end0], axis=-1, kind="mergesort", order=None
            )
        return np.argsort(
            self.array[begin0:end0], axis=-1, kind="mergesort", order=None
        )[::-1]

    def mult(self, other, out=None, factor=1.0):
        """Muliply with other DenseOneIndex object, multiplied by factor

        **Arguments:**

        other
             A DenseOneIndex instance to be added

        **Optional arguments:**

        out
             The output argument (DenseOneIndex with proper size).

        factor
             A scalar factor
        """
        self.check_type("other", other, DenseOneIndex)
        self.check_type("factor", factor, float, int)
        if out is None:
            out = DenseOneIndex(self.shape[0])
        else:
            self.check_type("out", out, DenseOneIndex)
            if out.shape != self.shape:
                raise MatrixShapeError(
                    "The output argument has the incorrect shape."
                )
        out.array[:] = self.array * other.array * factor
        return out

    def dot(self, other, factor=1.0):
        """Dot product with other DenseOneIndex object, multiplied by factor

        **Arguments:**

        other
             A DenseOneIndex instance to be added

        **Optional arguments:**

        factor
             A scalar factor
        """
        self.check_type("other", other, DenseOneIndex)
        self.check_type("factor", factor, float, int)
        return np.dot(self.array, other.array) * factor

    def idivide(self, other, factor=1.0):
        """Divide self by two DenseOneIndex object, multiplied by factor

        **Arguments:**

        other
             A DenseOneIndex instance to be divided

        **Optional arguments:**

        factor
             When given, a factor scaling the result of the operation.

        """
        self.check_type("other", other, DenseOneIndex)
        self.check_type("factor", factor, float, int)
        if self.shape != other.shape:
            raise MatrixShapeError(
                "The output argument has the incorrect shape."
            )
        self.array[:] = np.divide(self.array, other.array) * factor

    def divide(self, other, factor=1.0, out=None):
        """Divide two DenseOneIndex object, multiplied by factor, and return
        output

        **Arguments:**

        other
             A DenseOneIndex instance to be divided

        **Optional arguments:**

        factor
             A scalar factor

        out
             The output DenseOneIndex
        """
        self.check_type("other", other, DenseOneIndex)
        self.check_type("factor", factor, float, int)
        if out is None:
            out = DenseOneIndex(other.shape[0])
        else:
            self.check_type("out", out, DenseOneIndex)
            if out.shape != self.shape or out.shape != other.shape:
                raise MatrixShapeError(
                    "The output argument has the incorrect shape."
                )
        out.array[:] = np.divide(self.array, other.array) * factor
        return out

    def sqrt(self):
        """Return the real part of the square root of one-index object"""
        out = DenseOneIndex(self.nbasis)
        out.array[:] = np.sqrt(self.array).real
        return out

    def isqrt(self):
        """Real part of the square root of one-index object"""
        self.array[:] = np.sqrt(self.array).real

    def inverse(self):
        """Return the inverse of one-index object"""
        out = DenseOneIndex(self.nbasis)
        out.array[:] = 1.0 / (self.array)
        return out
