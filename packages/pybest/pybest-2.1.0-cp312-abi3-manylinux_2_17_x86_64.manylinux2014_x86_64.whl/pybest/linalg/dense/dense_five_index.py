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
# This file has been added by Michał Kopczyński.


import numpy as np

from pybest.exceptions import ArgumentError
from pybest.linalg.base import FiveIndex
from pybest.log import log

from .dense_four_index import DenseFourIndex
from .dense_one_index import DenseOneIndex
from .dense_three_index import DenseThreeIndex
from .dense_two_index import DenseTwoIndex


class DenseFiveIndex(FiveIndex):
    """Dense five-dimensional matrix.

    This is the most inefficient implementation in terms of memory usage and
    computer time. Due to its simplicity, it is trivial to implement. This
    implementation mainly serves as a reference for testing purposes.
    """

    # identification attribute
    dense_five_identifier = True

    #
    # Constructor and destructor
    #

    def __init__(
        self,
        nbasis,
        nbasis1=None,
        nbasis2=None,
        nbasis3=None,
        nbasis4=None,
        label="",
    ):
        """
        **Arguments:**

        nbasis
             The number of basis functions.

        **Optional arguments:**

        nbasis1, nbasis2, nbasis3, nbasis4
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
        if nbasis4 is None:
            nbasis4 = nbasis
        self._array = np.zeros(
            (nbasis, nbasis1, nbasis2, nbasis3, nbasis4), float
        )
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
        self,
        nbasis,
        nbasis1=None,
        nbasis2=None,
        nbasis3=None,
        nbasis4=None,
    ):
        """Is self compatible with the given constructor arguments?

        nbasis
             The number of basis functions. (Number of rows).

        **Optional arguments:**

        nbasis1, nbasis2, nbasis3, nbasis4
             When not given, nbasis is the default value for other nbasisX
             arguments if not specified.
        """
        if nbasis1 is None:
            nbasis1 = nbasis
        if nbasis2 is None:
            nbasis2 = nbasis
        if nbasis3 is None:
            nbasis3 = nbasis
        if nbasis4 is None:
            nbasis4 = nbasis
        assert nbasis == self.nbasis
        assert nbasis1 == self.nbasis1
        assert nbasis2 == self.nbasis2
        assert nbasis3 == self.nbasis3
        assert nbasis4 == self.nbasis4

    def __eq__(self, other):
        """Compare self with other"""
        return (
            isinstance(other, DenseFiveIndex)
            and other.nbasis == self.nbasis
            and other.nbasis1 == self.nbasis1
            and other.nbasis2 == self.nbasis2
            and other.nbasis3 == self.nbasis3
            and other.nbasis4 == self.nbasis4
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
        nbasis4 = grp["array"].shape[4]
        label = grp.attrs["label"]
        result = cls(nbasis, nbasis1, nbasis2, nbasis3, nbasis4, label)
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
        """Return a new five-index object with the same nbasis"""
        return DenseFiveIndex(
            self.nbasis,
            self.nbasis1,
            self.nbasis2,
            self.nbasis3,
            self.nbasis4,
        )

    @staticmethod
    def einsum_index(script):
        """Returns indices to numpy.einsum summation."""
        if not len(script) == 5 and isinstance(script, str):
            raise ValueError
        return script

    #
    # Properties
    #
    @property
    def nbasis(self):
        """The number of basis functions in basis"""
        return self.array.shape[0]

    @property
    def nbasis1(self):
        """The number of basis functions in nbasis1"""
        return self.array.shape[1]

    @property
    def nbasis2(self):
        """The number of basis functions in nbasis2"""
        return self.array.shape[2]

    @property
    def nbasis3(self):
        """The number of basis functions in nbasis3"""
        return self.array.shape[3]

    @property
    def nbasis4(self):
        """The number of basis functions in nbasis4"""
        return self.array.shape[4]

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
        if not ndarray.ndim == 5:
            raise ArgumentError("Only 5D array can be set.")
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
            self.nbasis,
            self.nbasis1,
            self.nbasis2,
            self.nbasis3,
            self.nbasis4,
        )

    new.__check_init_args__ = _check_new_init_args

    def clear(self):
        """Reset all elements to zero."""
        self.array[:] = 0.0

    def replace_array(self, value):
        """Replaces an array with another array, if not present, it will be
        generated.
        """
        if isinstance(value, DenseFiveIndex):
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
        begin4=0,
        end4=None,
    ):
        """Return a copy of (a part of) the object

        **Optional arguments:**

        begin0, end0, begin1, end1, begin2, end2, begin3, end3, begin4, end4
             Can be used to select a subblock of the object. When not given,
             the full range is used.
        """
        end0, end1, end2, end3, end4 = self.fix_ends(
            end0, end1, end2, end3, end4
        )
        result = DenseFiveIndex(
            end0 - begin0,
            end1 - begin1,
            end2 - begin2,
            end3 - begin3,
            end4 - begin4,
        )
        result.array[:] = self.array[
            begin0:end0,
            begin1:end1,
            begin2:end2,
            begin3:end3,
            begin4:end4,
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
        elif len(shape) == 5:
            out = DenseFiveIndex(
                shape[0], shape[1], shape[2], shape[3], shape[4]
            )
        out.array[:] = np.reshape(self.array, shape, order="C")
        return out

    def assign(self, other, ind=None, begin5=0, end5=None):
        """Assign with the contents of another object

        **Arguments:**

        other
             Another DenseXIndex object or a np ndarrray or float.

        ind
            If given, take only indices ``ind`` of other array.

        begin5, end5
             Can be used to select a subblock of the object. When not given,
             the full range is used.
        """
        self.check_type(
            "other",
            other,
            DenseFiveIndex,
            DenseFourIndex,
            DenseThreeIndex,
            DenseTwoIndex,
            DenseOneIndex,
            np.ndarray,
            float,
        )
        if isinstance(other, DenseFiveIndex):
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
                    (
                        self.nbasis,
                        self.nbasis1,
                        self.nbasis2,
                        self.nbasis3,
                        self.nbasis4,
                    )
                )
        elif isinstance(other, DenseFourIndex):
            if ind is not None:
                raise NotImplementedError(
                    "This functionality is not yet implemented"
                )

            else:
                self.array[:] = other.array.reshape(
                    (
                        self.nbasis,
                        self.nbasis1,
                        self.nbasis2,
                        self.nbasis3,
                        self.nbasis4,
                    )
                )
        elif isinstance(other, DenseThreeIndex):
            if ind is not None:
                raise NotImplementedError(
                    "This functionality is not yet implemented"
                )
            else:
                self.array[:] = other.array.reshape(
                    (
                        self.nbasis,
                        self.nbasis1,
                        self.nbasis2,
                        self.nbasis3,
                        self.nbasis4,
                    )
                )
        elif isinstance(other, DenseTwoIndex):
            if ind is not None:
                raise NotImplementedError(
                    "This functionality is not yet implemented"
                )
            else:
                self.array[:] = other.array.reshape(
                    (
                        self.nbasis,
                        self.nbasis1,
                        self.nbasis2,
                        self.nbasis3,
                        self.nbasis4,
                    )
                )
        elif isinstance(other, DenseOneIndex):
            if ind is not None:
                end5 = other.fix_ends(end5)[0]
                self.array[ind] = other.array[begin5:end5]
            else:
                end5 = other.fix_ends(end5)[0]
                self.array[:] = other.array[begin5:end5].reshape(
                    (
                        self.nbasis,
                        self.nbasis1,
                        self.nbasis2,
                        self.nbasis3,
                        self.nbasis4,
                    )
                )
        else:
            raise ArgumentError(
                f"Do not know how to assign object of type {type(other)}."
            )

    def randomize(self):
        """Fill with random normal data"""
        self.array[:] = np.random.normal(0, 1, self.shape)

    # NOTE to be implemented if needed in the future
    def change_basis_signs(self, signs):
        """Correct for different sign conventions of the basis functions.

        **Arguments:**

        signs
             A numpy array with sign changes indicated by +1 and -1.
        """
        raise NotImplementedError

    def iscale(self, factor):
        """In-place multiplication with a scalar

        **Arguments:**

        factor
             A scalar factor.
        """
        self.check_type("factor", factor, float, int)
        self.array *= factor

    def get_element(self, i, j, k, l, m):
        """Return the element at indices i, j, k, l, m of the array."""
        return self.array[i, j, k, l, m]

    def set_element(self, i, j, k, l, m, value):
        """Set a matrix element

        **Arguments:**

        i, j, k, l, m
             The matrix indices to be set

        value
             The value to be assigned to the matrix element.
        """
        self.array[i, j, k, l, m] = value

    def itranspose(self, transpose=None):
        """In-place transpose: ``0,1,2,3,4 -> 1,0,3,2,4``"""
        if transpose is None:
            raise NotImplementedError(
                "This functionality is not yet implemented"
            )
        else:
            self.array = self.array.transpose(transpose)

    def sum(self):
        """Return the sum of all elements"""
        return np.sum(self.array)

    def iadd_transpose(self, transpose, other=None, factor=1.0):
        """In-place addition of transpose. If `other` is given (FiveIndex),
        its transpose is added, otherwise (None) its own transpose is added.
        """
        self.check_type("factor", factor, float, int)
        self.check_type("other", other, type(None), DenseFiveIndex)
        if other is None:
            self.array[:] = (
                self.array + self.array.transpose(transpose) * factor
            )
        else:
            self.array[:] = (
                self.array + other.array.transpose(transpose) * factor
            )
