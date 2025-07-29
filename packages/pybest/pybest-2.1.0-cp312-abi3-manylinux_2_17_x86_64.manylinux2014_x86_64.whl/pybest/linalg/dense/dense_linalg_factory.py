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
# 2024-01/20: Added support for DenseSixIndex (Michał Kopczyński)
# 2024-02: Added support for DenseFiveIndex (Michał Kopczyński)
# 2024-12: Added Support for DenseEightIndex (Lena Szczuczko)

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

from typing import Optional

from pybest.exceptions import ArgumentError, MatrixShapeError

from ..base import LinalgFactory
from .dense_eight_index import DenseEightIndex
from .dense_five_index import DenseFiveIndex
from .dense_four_index import DenseFourIndex
from .dense_one_index import DenseOneIndex
from .dense_orbital import DenseOrbital
from .dense_six_index import DenseSixIndex
from .dense_three_index import DenseThreeIndex
from .dense_two_index import DenseTwoIndex


class DenseLinalgFactory(LinalgFactory):
    """Base class for dense implementation of LinalgFactory."""

    # identification attribute
    dense_linalg_identifier = True

    #
    # DenseOneIndex constructor with default arguments
    #

    def create_one_index(self, nbasis=None, label=""):
        """Create a DenseOneIndex with defaults from the LinalgFactory

        **Optional arguments:**

        nbasis
             The number of basis functions. When not given, the
             default_nbasis value of the DenseLinalgFactory instance will be
             used.

        label
             The name (label) of the instance to be created.
        """
        nbasis = nbasis or self.default_nbasis
        return DenseOneIndex(nbasis, label)

    def _check_one_index_init_args(self, other, nbasis=None):
        """Is an object compatible with the constructor arguments?

        **Optional arguments:**

        other
             Another OneIndex object.

        nbasis
             The number of basis functions. When not given, the
             default_nbasis value of the DenseLinalgFactory instance will be
             used. Nbasis is a default value for other
             nbasisX arguments if not specified.
        """
        nbasis = nbasis or self.default_nbasis
        other.__check_init_args__(nbasis)

    create_one_index.__check_init_args__ = _check_one_index_init_args

    #
    # DenseOrbital constructor with default arguments
    #

    def create_orbital(self, nbasis=None, nfn=None):
        """Create a DenseOrbital with defaults from the LinalgFactory

        **Optional arguments:**

        nbasis
             The number of basis functions. When not given, the
             default_nbasis value of the DenseLinalgFactory instance will be
             used.

        nfn
             The number of orbitals. When not given, the default_nbasis
             value of the DenseLinalgFactory instance will be used.
        """
        nbasis = nbasis or self.default_nbasis
        nfn = nfn or nbasis
        return DenseOrbital(nbasis, nfn)

    def _check_orbital_init_args(self, orbitals, nbasis=None, nfn=None):
        """Is an object compatible with the constructor arguments?

        **Optional arguments:**

        orbitals
             Orbital coefficient matrix.

        nbasis
             The number of basis functions. When not given, the
             default_nbasis value of the DenseLinalgFactory instance will be
             used. Nbasis is a default value for other
             nbasisX arguments if not specified.

        nfn
             The number of orbitals. When not given, the default_nbasis
             value of the DenseLinalgFactory instance will be used.
        """
        nbasis = nbasis or self.default_nbasis
        nfn = nfn or nbasis
        orbitals.__check_init_args__(nbasis, nfn)

    create_orbital.__check_init_args__ = _check_orbital_init_args

    #
    # DenseTwoIndex constructor with default arguments
    #

    def create_two_index(self, nbasis=None, nbasis1=None, label=""):
        """Create a DenseTwoIndex with defaults from the LinalgFactory

        **Optional arguments:**

        nbasis
             The number of basis functions. When not given, the
             default_nbasis value of the DenseLinalgFactory instance will be
             used.

        nbasis1
             The number of basis functions for the second axis if it differes
             from ``nbasis``.

        label
             The name (label) of the instance to be created.
        """
        nbasis = nbasis or self.default_nbasis
        # Don't replace nbasis1 by self.default_nbasis when it is None! It is
        # a genuine optional argument.
        return DenseTwoIndex(nbasis, nbasis1, label)

    def _check_two_index_init_args(self, other, nbasis=None, nbasis1=None):
        """Is an object compatible the constructor arguments?

        **Optional arguments:**

        other
             Another TwoIndex object.

        nbasis, nbasis1
             The number of basis functions. When not given, the
             default_nbasis value of the DenseLinalgFactory instance will be
             used. Nbasis is a default value for other
             nbasisX arguments if not specified.
        """
        nbasis = nbasis or self.default_nbasis
        # Don't replace nbasis1 by self.default_nbasis when it is None! It is
        # a genuine optional argument.
        other.__check_init_args__(nbasis, nbasis1)

    create_two_index.__check_init_args__ = _check_two_index_init_args

    #
    # DenseThreeIndex constructor with default arguments
    #

    def create_three_index(
        self, nbasis=None, nbasis1=None, nbasis2=None, label=""
    ):
        """Create a DenseThreeIndex with defaults from the LinalgFactory

        **Optional arguments:**

        nbasis, nbasis1, nbasis2
             The number of basis functions. When not given, the
             default_nbasis value of the DenseLinalgFactory instance will be
             used. Nbasis is a default value for other
             nbasisX arguments if not specified.

        label
             The name (label) of the instance to be created.
        """
        nbasis = nbasis or self.default_nbasis
        # Don't replace nbasis1, nbasis2 by self.default_nbasis when None! They
        # are genuine optional arguments.
        return DenseThreeIndex(nbasis, nbasis1, nbasis2, label)

    def _check_three_index_init_args(
        self, other, nbasis=None, nbasis1=None, nbasis2=None
    ):
        """Is an object is compatible the constructor arguments?

        **Optional arguments:**

        other
             Another ThreeIndex object.

        nbasis, nbasis1, nbasis2
             The number of basis functions. When not given, the
             default_nbasis value of the DenseLinalgFactory instance will be
             used. Nbasis is a default value for other
             nbasisX arguments if not specified.
        """
        nbasis = nbasis or self.default_nbasis
        # Don't replace nbasis1, nbasis2 by self.default_nbasis when None! They
        # are genuine optional arguments.
        other.__check_init_args__(nbasis, nbasis1, nbasis2)

    create_three_index.__check_init_args__ = _check_three_index_init_args

    #
    # DenseFourIndex constructor with default arguments
    #

    def create_four_index(
        self, nbasis=None, nbasis1=None, nbasis2=None, nbasis3=None, label=""
    ):
        """Create a DenseFourIndex with defaults from the LinalgFactory

        **Optional arguments:**

        nbasis (obligatory), nbasis1, nbasis2, nbasis3
             The number of basis functions. When not given, the
             default_nbasis value of the DenseLinalgFactory instance will be
             used. Nbasis is a default value for other
             nbasisX arguments if not specified.

        label
             The name (label) of the instance to be created.
        """
        nbasis = nbasis or self.default_nbasis
        # Don't replace nbasis1, nbasis2, nbasis3 by self.default_nbasis when None! They
        # are genuine optional arguments.
        return DenseFourIndex(nbasis, nbasis1, nbasis2, nbasis3, label)

    def _check_four_index_init_args(
        self, other, nbasis=None, nbasis1=None, nbasis2=None, nbasis3=None
    ):
        """Is an object is compatible the constructor arguments?

        **Optional arguments:**

        other
             Another FourIndex object.

        nbasis, nbasis1, nbasis2, nbasis3
             The number of basis functions. When not given, the
             default_nbasis value of the DenseLinalgFactory instance will be
             used. Nbasis is a default value for other
             nbasisX arguments if not specified.
        """
        nbasis = nbasis or self.default_nbasis
        other.__check_init_args__(nbasis, nbasis1, nbasis2, nbasis3)

    create_four_index.__check_init_args__ = _check_four_index_init_args

    #
    # DenseFiveIndex constructor with default arguments
    #

    def create_five_index(
        self,
        nbasis=None,
        nbasis1=None,
        nbasis2=None,
        nbasis3=None,
        nbasis4=None,
        label="",
    ):
        """Create a DenseFiveIndex with defaults from the LinalgFactory

        **Optional arguments:**

        nbasis (obligatory), nbasis1, nbasis2, nbasis3, nbasis4
             The number of basis functions. When not given, the
             default_nbasis value of the DenseLinalgFactory instance will be
             used. Nbasis is a default value for other
             nbasisX arguments if not specified.

        label
             The name (label) of the instance to be created.
        """
        nbasis = nbasis or self.default_nbasis
        # Don't replace nbasis1, nbasis2, nbasis3, nbasis4 by self.default_nbasis when None! They
        # are genuine optional arguments.
        return DenseFiveIndex(
            nbasis, nbasis1, nbasis2, nbasis3, nbasis4, label
        )

    def _check_five_index_init_args(
        self,
        other,
        nbasis=None,
        nbasis1=None,
        nbasis2=None,
        nbasis3=None,
        nbasis4=None,
    ):
        """Is an object is compatible the constructor arguments?

        **Optional arguments:**

        other
             Another FiveIndex object.

        nbasis, nbasis1, nbasis2, nbasis3, nbasis4
             The number of basis functions. When not given, the
             default_nbasis value of the DenseLinalgFactory instance will be
             used. Nbasis is a default value for other
             nbasisX arguments if not specified.
        """
        nbasis = nbasis or self.default_nbasis
        other.__check_init_args__(nbasis, nbasis1, nbasis2, nbasis3, nbasis4)

    create_five_index.__check_init_args__ = _check_five_index_init_args

    #
    # DenseSixIndex constructor with default arguments
    #

    def create_six_index(
        self,
        nbasis=None,
        nbasis1=None,
        nbasis2=None,
        nbasis3=None,
        nbasis4=None,
        nbasis5=None,
        label="",
    ):
        """Create a DenseSixIndex object with defaults from the LinalgFactory

        **Optional arguments:**

        nbasis (obligatory), nbasis1, nbasis2, nbasis3, nbasis4, nbasis5
             The number of basis functions. When not given, the
             default_nbasis value of the DenseLinalgFactory instance will be
             used. Nbasis is a default value for other
             nbasisX arguments if not specified.

        label
             The name (label) of the instance to be created.
        """
        nbasis = nbasis or self.default_nbasis
        # Don't replace nbasis1, nbasis2, nbasis3 by self.default_nbasis when None! They
        # are genuine optional arguments.
        return DenseSixIndex(
            nbasis, nbasis1, nbasis2, nbasis3, nbasis4, nbasis5, label
        )

    def _check_six_index_init_args(
        self,
        other,
        nbasis=None,
        nbasis1=None,
        nbasis2=None,
        nbasis3=None,
        nbasis4=None,
        nbasis5=None,
    ):
        """Is an object is compatible the constructor arguments?

        **Optional arguments:**

        other
             Another SixIndex object.

        nbasis, nbasis1, nbasis2, nbasis3, nbasis4, nbasis5
             The number of basis functions. When not given, the
             default_nbasis value of the DenseLinalgFactory instance will be
             used. Nbasis is a default value for other
             nbasisX arguments if not specified.
        """
        nbasis = nbasis or self.default_nbasis
        other.__check_init_args__(
            nbasis, nbasis1, nbasis2, nbasis3, nbasis4, nbasis5
        )

    create_six_index.__check_init_args__ = _check_six_index_init_args

    #
    # DenseEightIndex constructor with default arguments
    #:
    def create_eight_index(
        self,
        nbasis: Optional[int] = None,
        nbasis1: Optional[int] = None,
        nbasis2: Optional[int] = None,
        nbasis3: Optional[int] = None,
        nbasis4: Optional[int] = None,
        nbasis5: Optional[int] = None,
        nbasis6: Optional[int] = None,
        nbasis7: Optional[int] = None,
        label: str = "",
    ) -> DenseEightIndex:
        """Create a DenseEightIndex object with default arguments.

        Args:
            nbasis (Optional[int], optional): The number of basis functions for the first dimension. Defaults to None.
            nbasis1 (Optional[int], optional): The number of basis functions for the second dimension. Defaults to None.
            nbasis2 (Optional[int], optional): The number of basis functions for the third dimension. Defaults to None.
            nbasis3 (Optional[int], optional): The number of basis functions for the fourth dimension. Defaults to None.
            nbasis4 (Optional[int], optional): The number of basis functions for the fifth dimension. Defaults to None.
            nbasis5 (Optional[int], optional): The number of basis functions for the sixth dimension. Defaults to None.
            nbasis6 (Optional[int], optional): The number of basis functions for the seventh dimension. Defaults to None.
            nbasis7 (Optional[int], optional): The number of basis functions for the eighth dimension. Defaults to None.
            label (str, optional): The name (label) of the created object. Defaults to "".

        Returns:
            DenseEightIndex: Creates a DenseEightIndex object with default arguments.
        """
        nbasis = nbasis or self.default_nbasis
        # Don't replace nbasis1, nbasis2, nbasis3, nbasis4, nbasis5, nbasis6, nbasis7 by self.default_nbasis when None!
        # They are genuine optional arguments.
        return DenseEightIndex(
            nbasis,
            nbasis1,
            nbasis2,
            nbasis3,
            nbasis4,
            nbasis5,
            nbasis6,
            nbasis7,
            label,
        )

    def _check_eight_index_init_args(
        self,
        other: DenseEightIndex,
        nbasis: Optional[int] = None,
        nbasis1: Optional[int] = None,
        nbasis2: Optional[int] = None,
        nbasis3: Optional[int] = None,
        nbasis4: Optional[int] = None,
        nbasis5: Optional[int] = None,
        nbasis6: Optional[int] = None,
        nbasis7: Optional[int] = None,
    ) -> None:
        """Check initialization arguments for a DenseEightIndex object.

        Args:
            other (DenseEightIndex): The DenseEightIndex object to compare against.
            nbasis (Optional[int], optional): The number of basis functions for the first dimension. Defaults to None.
            nbasis1 (Optional[int], optional): The number of basis functions for the second dimension. Defaults to None.
            nbasis2 (Optional[int], optional): The number of basis functions for the third dimension. Defaults to None.
            nbasis3 (Optional[int], optional): The number of basis functions for the fourth dimension. Defaults to None.
            nbasis4 (Optional[int], optional): The number of basis functions for the fifth dimension. Defaults to None.
            nbasis5 (Optional[int], optional): The number of basis functions for the sixth dimension. Defaults to None.
            nbasis6 (Optional[int], optional): The number of basis functions for the seventh dimension. Defaults to None.
            nbasis7 (Optional[int], optional): The number of basis functions for the eighth dimension. Defaults to None.
        """
        nbasis = nbasis or self.default_nbasis
        # Ensure that the other object has compatible arguments
        other.__check_init_args__(
            nbasis,
            nbasis1,
            nbasis2,
            nbasis3,
            nbasis4,
            nbasis5,
            nbasis6,
            nbasis7,
        )

    create_eight_index.__check_init_args__ = _check_eight_index_init_args

    #
    # Other code
    #

    #
    # NOTE: staticmethod can be removed, but code base needs to be fixed.
    # For now, we call LinalgFactory.check_type instead.
    @staticmethod
    def allocate_check_output(out, outshape):
        """Allocate/check the output for the wrappers below

        **Arguments:**

        out
             The output argument.

        outshape
             The expected shape of the output argument.

        **Returns:** the output argument.
        """
        #       if len(outshape) == 3 and not (outshape[0] == outshape[1] and
        #                                      outshape[0] == outshape[2]):
        #           raise TypeError('A 3-index object must have the same size in all indexes.')
        #       if len(outshape) == 4 and not (outshape[0] == outshape[1] and
        #                                      outshape[0] == outshape[2] and
        #                                      outshape[0] == outshape[3]):
        #           raise TypeError('A 4-index object must have the same size in all indexes.')

        # Handle the output argument
        if out is None:
            if len(outshape) == 0:
                pass
            elif len(outshape) == 1:
                out = DenseOneIndex(outshape[0])
            elif len(outshape) == 2:
                out = DenseTwoIndex(*outshape)
            elif len(outshape) == 3:
                out = DenseThreeIndex(*outshape)
            #               out = DenseThreeIndex(outshape[0])
            elif len(outshape) == 4:
                out = DenseFourIndex(*outshape)
            #               out = DenseFourIndex(outshape[0])
            elif len(outshape) == 5:
                out = DenseFiveIndex(*outshape)
            elif len(outshape) == 6:
                out = DenseSixIndex(*outshape)
            elif len(outshape) == 8:
                out = DenseEightIndex(*outshape)
            else:
                raise ArgumentError(
                    "The outshape must have length 0, 1, 2, 3, 4, 5, 6 or 8"
                )
        else:
            if len(outshape) == 0:
                raise ArgumentError(
                    "No output argument can be given when contracting to a scalar."
                )
            if len(outshape) == 1:
                LinalgFactory.check_type("out", out, DenseOneIndex)
            elif len(outshape) == 2:
                LinalgFactory.check_type("out", out, DenseTwoIndex)
            elif len(outshape) == 3:
                LinalgFactory.check_type("out", out, DenseThreeIndex)
            elif len(outshape) == 4:
                LinalgFactory.check_type("out", out, DenseFourIndex)
            elif len(outshape) == 5:
                LinalgFactory.check_type("out", out, DenseFiveIndex)
            elif len(outshape) == 6:
                LinalgFactory.check_type("out", out, DenseSixIndex)
            elif len(outshape) == 8:
                LinalgFactory.check_type("out", out, DenseEightIndex)
            else:
                raise ArgumentError(
                    "The outshape must have length 0, 1, 2, 3, 4, 5, 6 or 8"
                )
            if out.shape != outshape:
                raise MatrixShapeError(
                    "The output argument does not have the right shape."
                )
        return out
