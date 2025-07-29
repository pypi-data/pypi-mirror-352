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

from pybest.exceptions import ArgumentError
from pybest.linalg.base import ThreeIndex
from pybest.log import log

from .dense_one_index import DenseOneIndex


class DenseThreeIndex(ThreeIndex):
    """Dense three-dimensional object.

    This is the most inefficient implementation in terms of memory usage and
    computer time. Due to its simplicity, it is trivial to implement. This
    implementation mainly serves as a reference for testing purposes.
    """

    # identification attribute
    dense_three_identifier = True

    #
    # Constructor and destructor
    #

    def __init__(self, nbasis, nbasis1=None, nbasis2=None, label=""):
        """
        **Arguments:**

        nbasis, nbasis1, nbasis2
             The number of basis functions. Nbasis is a default value for other
             nbasisX arguments if not specified.

        label
             The name (label) of the instance to be created.
        """
        if nbasis1 is None:
            nbasis1 = nbasis
        if nbasis2 is None:
            nbasis2 = nbasis
        self._array = np.zeros((nbasis, nbasis1, nbasis2), float)
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

    def __check_init_args__(self, nbasis, nbasis1=None, nbasis2=None):
        """Is self compatible with the given constructor arguments?

        nbasis, nbasis1, nbasis2
             The number of basis functions. Nbasis is a default value for other
             nbasisX arguments if not specified.
        """
        if nbasis1 is None:
            nbasis1 = nbasis
        if nbasis2 is None:
            nbasis2 = nbasis
        assert nbasis == self.nbasis
        assert nbasis1 == self.nbasis1
        assert nbasis2 == self.nbasis2

    def __eq__(self, other):
        """Compare self with other"""
        return (
            isinstance(other, DenseThreeIndex)
            and other.nbasis == self.nbasis
            and other.nbasis1 == self.nbasis1
            and other.nbasis2 == self.nbasis2
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
        label = grp.attrs["label"]
        result = cls(nbasis, nbasis1, nbasis2, label)
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
        """Return a new three-index object with the same nbasis"""
        return DenseThreeIndex(self.nbasis, self.nbasis1, self.nbasis2)

    @staticmethod
    def einsum_index(script):
        """Returns indices to numpy.einsum summation."""
        if not len(script) == 3 and isinstance(script, str):
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
        if not ndarray.ndim == 3:
            raise ArgumentError("Only 3D array can be set.")
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
        other.__check_init_args__(self.nbasis, self.nbasis1, self.nbasis2)

    new.__check_init_args__ = _check_new_init_args

    def replace_array(self, value):
        """Replaces an array with another array, if not present, it will be
        generated.
        """
        if isinstance(value, DenseThreeIndex):
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
        self, begin0=0, end0=None, begin1=0, end1=None, begin2=0, end2=None
    ):
        """Return a copy of (a part of) the object

        **Optional arguments:**

        begin0, end0, begin1, end1, begin2, end2
             Can be used to select a subblock of the object. When not given,
             the full range is used.
        """
        end0, end1, end2 = self.fix_ends(end0, end1, end2)
        result = DenseThreeIndex(end0 - begin0, end1 - begin1, end2 - begin2)
        result.array[:] = self.array[begin0:end0, begin1:end1, begin2:end2]
        result.label = self.label
        return result

    def assign(
        self,
        other,
        begin3=0,
        end3=None,
        begin4=0,
        end4=None,
        begin5=0,
        end5=None,
        ind0=None,
    ):
        """Assign with the contents of another object

        **Arguments:**

        other
             Another DenseThreeIndex object or an array.

        **Optional arguments:**

        begin3, end3
             If specified, only a subblock of other is assigned.

        ind0
             If specified, only a subblock of self is assigned. Only
             implemented for DenseOneIndex
        """
        self.check_type(
            "other", other, DenseThreeIndex, np.ndarray, DenseOneIndex
        )
        if isinstance(other, DenseThreeIndex):
            end3, end4, end5 = other.fix_ends(end3, end4, end5)
            self.array[:] = other.array[begin3:end3, begin4:end4, begin5:end5]
        elif isinstance(other, np.ndarray):
            self.array[:] = other
        elif isinstance(other, DenseOneIndex):
            shape = other.shape
            ends = [end3]
            end3 = ends[0] or shape[0]
            if ind0 is not None:
                self.array[ind0] = other.array[begin3:end3]
            else:
                self.array[:] = other.array[begin3:end3].reshape(
                    self.nbasis, self.nbasis1, self.nbasis2
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

    def change_basis_signs(self, signs):
        """Correct for different sign conventions of the basis functions.

        **Arguments:**

        signs
             A numpy array with sign changes indicated by +1 and -1.
        """
        self.array *= signs
        self.array *= signs.reshape(-1, 1)
        self.array *= signs.reshape(-1, 1, 1)

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
    ):
        """Add another DenseThreeIndex object in-place, multiplied by factor

        **Arguments:**

        other
             A DenseThreeIndex instance to be added

        **Optional arguments:**

        factor
             When given, the added term is scaled by this factor.

        begin0, end0, begin1, end1, begin2, end2, ...
             Can be used to add only a part of the three-index object
        """
        self.check_type("other", other, DenseThreeIndex)
        self.check_type("factor", factor, float, int)
        end0, end1, end2 = self.fix_ends(end0, end1, end2)
        end3, end4, end5 = other.fix_ends(end3, end4, end5)
        self.array[begin0:end0, begin1:end1, begin2:end2] += (
            other.array[begin3:end3, begin4:end4, begin5:end5] * factor
        )

    def iadd_transpose(self, transpose, other=None, factor=1.0):
        """In-place addition of its own (other=None) or other DenseThreeIndex
        transpose
        """
        self.check_type("factor", factor, float, int)
        if other is None:
            self.array[:] = (
                self.array + self.array.transpose(transpose) * factor
            )
        else:
            self.check_type("other", other, DenseThreeIndex)
            self.array[:] = (
                self.array + other.array.transpose(transpose) * factor
            )

    def iscale(self, factor):
        """In-place multiplication with a scalar

        **Arguments:**

        factor
             A scalar factor.
        """
        self.check_type("factor", factor, float, int)
        self.array *= factor

    def itranspose(self, *shape):
        """In-place transpose according to shape"""
        self.array = self.array.transpose(shape)

    def get_element(self, i, j, k):
        """Return a matrix element"""
        return self.array[i, j, k]

    def set_element(self, i, j, k, value):
        """Set a matrix element"""
        self.array[i, j, k] = value
