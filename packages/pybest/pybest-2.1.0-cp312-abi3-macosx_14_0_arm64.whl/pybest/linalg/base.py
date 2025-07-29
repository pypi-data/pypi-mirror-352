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
# 2020-07-01: Introduce general tensor contraction engine used for all NIndex objects
# 2022-09/10: dense.py split into files for each class in subfolder dense (Maximilian Kriebel)
# 2022-09/10: [slice] and [tco] replaced with [contract] (Maximilian Kriebel)
# 2023      : contraction defaults set to CuPy if available and specifically implemented (Maximilian Kriebel)
# 2024      : added support of DenseFiveIndex and DenseSixIndex (Michał Kopczyński)
# 2025      : added general expand function (Katharina Boguslawski)
# 2024-11   : added DenseEightIndex support (Lena Szczuczko)

"""Base classes"""

from __future__ import annotations

import abc
import os
import uuid
from typing import Any, SupportsIndex

import numpy as np

from pybest import filemanager
from pybest.exceptions import ArgumentError, MatrixShapeError, UnknownOption
from pybest.io import dump_h5, load_h5
from pybest.log import log

from ._opt_einsum import oe_contract
from .contract import (
    cholesky_td_routine,
    get_outshape,
    parse_contract_input,
    parse_subscripts,
    slice_output,
    td_helper,
)
from .expand import (
    contract_operands,
    expand_diagonal_cases,
    expand_valid_cases,
    parse_expand_case,
    parse_repeated_expand_axes,
)
from .gpu_contract import (
    cupy_availability_check,
    cupy_helper,
    cupy_optimized,
    td_cupy_helper,
)

# from decouple import config
# Get environment variable for cupy cuda.
PYBEST_CUPY_AVAIL = bool(os.environ.get("PYBEST_CUPY_AVAIL", ""))
# PYBEST_CUPY_AVAIL = config("PYBEST_CUPY_AVAIL", default=False, cast=bool)
# Check if cupy cuda is available.
# If yes, set PYBEST_CUPY_AVAIL to True, if no, set PYBEST_CUPY_AVAIL to False.
if PYBEST_CUPY_AVAIL:
    PYBEST_CUPY_AVAIL = cupy_availability_check()


class LinalgFactory(abc.ABC):
    """A collection of compatible matrix and linear algebra routines.

    This is just an abstract base class that serves as a template for
    specific implementations.
    """

    linalg_identifier = True

    def __init__(self, default_nbasis=None):
        """
        **Optional arguments:**

        default_nbasis
             The default basis size when constructing new
             operators/expansions.
        """
        self.default_nbasis = default_nbasis

    @classmethod
    def from_hdf5(cls, grp):
        """Construct an instance from data previously stored in an h5py.Group.

        **Arguments:**

        grp
             An h5py.Group object.
        """
        default_nbasis = grp.attrs.get("default_nbasis")
        return cls(default_nbasis)

    def to_hdf5(self, grp):
        """Write a LinalgFactory to an HDF5 group

        **Argument:**

        grp
             A h5py.Group instance to write to.
        """
        grp.attrs["class"] = self.__class__.__name__
        if self.default_nbasis is not None:
            grp.attrs["default_nbasis"] = self.default_nbasis

    @property
    def default_nbasis(self):
        """The default number of basis functions"""
        return self._default_nbasis

    @default_nbasis.setter
    def default_nbasis(self, nbasis):
        """Set default number of basis functions"""
        self._default_nbasis = nbasis

    @abc.abstractmethod
    def create_one_index(self, nbasis=None, label=""):
        """Create a new instance of OneIndex"""

    @abc.abstractmethod
    def create_orbital(self, nbasis=None, nfn=None):
        """Create a new instance of Orbital

        **Arguments:**

        nbasis
            (int) The number of basis functions.

        nfn
            (int) The number of (molecular) orbitals.
        """

    @abc.abstractmethod
    def create_two_index(self, nbasis=None, nbasis1=None, label=""):
        """Create a new instance of TwoIndex"""

    @abc.abstractmethod
    def create_three_index(
        self, nbasis=None, nbasis1=None, nbasis2=None, label=""
    ):
        """Create a new instance of ThreeIndex"""

    @abc.abstractmethod
    def create_four_index(
        self, nbasis=None, nbasis1=None, nbasis2=None, nbasis3=None, label=""
    ):
        """Create a new instance of FourIndex"""

    @abc.abstractmethod
    def create_five_index(
        self,
        nbasis=None,
        nbasis1=None,
        nbasis2=None,
        nbasis3=None,
        nbasis4=None,
        label="",
    ):
        """Create a new instance of FiveIndex"""

    @abc.abstractmethod
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
        """Create a new instance of SixIndex"""

    @abc.abstractmethod
    def create_eight_index(
        self,
        nbasis: int | None = None,
        nbasis1: int | None = None,
        nbasis2: int | None = None,
        nbasis3: int | None = None,
        nbasis4: int | None = None,
        nbasis5: int | None = None,
        nbasis6: int | None = None,
        nbasis7: int | None = None,
        label="",
    ):
        """Create a new instance of EightIndex

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

        Raises:
            TypeError: If the argument is not of the correct type.
        """

    # NOTE: We need to define a class-internal check_option method to prevent circular imports
    @staticmethod
    def check_type(name: Any, instance: Any, *Classes: Any) -> None:
        """Check type of argument with given name against list of types

        **Arguments:**

        name
            The name of the argument being checked.

        instance
            The object being checked.

        Classes
            A list of allowed types.
        """
        if len(Classes) == 0:
            raise TypeError(
                "Type checking with an empty list of classes. This is a simple bug!"
            )
        match = False
        for Class in Classes:
            if isinstance(instance, Class):
                match = True
                break
        if not match:
            classes_parts = ["'", Classes[0].__name__, "'"]
            for Class in Classes[1:-1]:
                classes_parts.extend([", ``", Class.__name__, "'"])
            if len(Classes) > 1:
                classes_parts.extend([" or '", Classes[-1].__name__, "'"])
            raise TypeError(
                f"The argument '{name}' must be an instance of {''.join(classes_parts)}. "
                f"Got a '{instance.__class__.__name__}' instance instead."
            )


class LinalgObject(abc.ABC):
    """A base class for NIndex objects."""

    @property
    @abc.abstractmethod
    def array(self):
        """Linalg objects store all data in array"""

    @property
    @abc.abstractmethod
    def array2(self):
        """Cholesky Linalg objects store all data in array and array2"""

    @property
    @abc.abstractmethod
    def arrays(self):
        """List of all linalg array objects"""

    @property
    @abc.abstractmethod
    def label(self):
        """The label of a linalg object"""

    @abc.abstractmethod
    def __eq__(self, other):
        """Check if two objects are equal"""

    @abc.abstractmethod
    def __del__(self):
        """Explicitly delete all arrays"""

    @classmethod
    @abc.abstractmethod
    def from_hdf5(cls, grp):
        """Read from h5 file."""

    @abc.abstractmethod
    def to_hdf5(self, grp):
        """Write to h5 file."""

    @abc.abstractmethod
    def new(self):
        """Return a new NIndex object with the same nbasis"""

    def __clear__(self):
        """Part of the API specified in pybest.cache"""
        self.clear()

    @abc.abstractmethod
    def clear(self):
        """Reset all elements to zero."""

    @abc.abstractmethod
    def replace_array(self, value):
        """Replace array elements. No copy is generated, only a new reference."""

    # NOTE: We need to define a class-internal check_option method to prevent
    # circular imports
    @staticmethod
    def check_options(name: str, select: Any, *options: Any) -> None:
        """Check if a select is in the list of options. If not raise ValueError

        **Arguments:**

        name
            The name of the argument.

        select
            The value of the argument.

        options
            A list of allowed options.
        """
        if select not in options:
            formatted = ", ".join([f"'{option}'" for option in options])
            raise ValueError(
                f"The argument '{name}' must be one of: {formatted}"
            )

    # NOTE: We need to define a class-internal check_option method to prevent
    # circular imports
    @staticmethod
    def check_type(name: Any, instance: Any, *Classes: Any) -> None:
        """Check type of argument with given name against list of types

        **Arguments:**

        name
            The name of the argument being checked.

        instance
            The object being checked.

        Classes
            A list of allowed types.
        """
        if len(Classes) == 0:
            raise TypeError(
                "Type checking with an empty list of classes. This is a simple bug!"
            )
        match = False
        for Class in Classes:
            if isinstance(instance, Class):
                match = True
                break
        if not match:
            classes_parts = ["'", Classes[0].__name__, "'"]
            for Class in Classes[1:-1]:
                classes_parts.extend([", ``", Class.__name__, "'"])
            if len(Classes) > 1:
                classes_parts.extend([" or '", Classes[-1].__name__, "'"])
            raise TypeError(
                f"The argument '{name}' must be an instance of {''.join(classes_parts)}. "
                f"Got a '{instance.__class__.__name__}' instance instead."
            )


class Orbital(LinalgObject):
    """Base class for Orbital objects."""

    @property
    def array(self):
        """Linalg objects store all data in array. Will be overwritten by
        DenseNIndex objects.
        Those are not needed for Orbital class. The current class structure
        requires them to be defined.
        """

    @property
    def array2(self):
        """Cholesky Linalg objects store all data in array and array2. Will be
        overwritten by CholeskyFourIndex.
        Those are not needed for Orbital class. The current class structure
        requires them to be defined.
        """

    @property
    def arrays(self):
        """List of all linalg array objects. Will be overwritten by Dense and
        CholeskyIndex objects.
        Those are not needed for Orbital class. The current class structure
        requires them to be defined.
        """

    @property
    def label(self):
        """The label of a linalg/orbital object. It is not needed for the
        Orbital class. However, the current class structure requires it to be
        defined.
        """

    @abc.abstractmethod
    def check_normalization(self, overlap, eps=1e-4):
        """Check normalization of orbitals."""

    @abc.abstractmethod
    def error_eigen(self, fock, overlap):
        """Compute the error of the orbitals with respect to the eigenproblem"""


class NIndexObject(LinalgObject):
    """A base class for NIndex objects."""

    n_identifier = True

    @property
    def array(self):
        """Linalg objects store all data in array. Will be overwritten by
        DenseNIndex objects.
        """

    @property
    def array2(self):
        """Cholesky Linalg objects store all data in array and array2. Will be
        overwritten by CholeskyFourIndex.
        """

    @property
    def arrays(self):
        """List of all linalg array objects. Will be overwritten by Dense and
        CholeskyIndex objects.
        """

    @property
    def label(self):
        """The label of a linalg object"""

    @abc.abstractmethod
    def iscale(self, factor):
        """In-place multiplication with a scalar."""

    @property
    @abc.abstractmethod
    def shape(self):
        """Return shape of array."""

    @property
    def ndim(self):
        """The number of axes in the N-index object."""
        return len(self.shape)

    def fix_ends(self, *ends):
        """Return the last index of each dimension of array.
        Each end defined as None will be replaced by the corresponding axis
        dimension. Otherwise, each end remains unchanged.

        Arguments:
            list: containing end0, end1, end2,... (all `ends` must be provided)

        Returns:
            tuple: containing the last index of array (or its view) indices
        """
        shape = self.shape
        if len(shape) != len(ends):
            raise MatrixShapeError(
                "The argument 'ends' must have the same length as 'self.shape'."
            )
        return tuple(
            shape[i] if ends[i] is None else ends[i] for i in range(len(shape))
        )

    def dump_array(self, label, filename=None):
        """Dump some NIndexObject to disk and delete all array instances.
        NIndexObject will be dump to ``temp_dir`` specified in ``filemanager``
        (globally defined)

        **Arguments:**

        label
            (str) The label used to store the attribute in the IOData container

        **Optional Arguments:**

        filename
            (str) The filename of the checkpoint file. Has to end with ``.h5``
        """
        # Generate some unique internal label if not present or empty
        if not self.label:
            self.label = str(uuid.uuid4())
        # Use the pybest.io interface to write the checkpoint file
        filename = filename or f"checkpoint_{self.label}.h5"
        # Use the pybest.io interface to write the checkpoint file
        if not label:
            raise ArgumentError(f"Improper label chosen: {label}.")
        data = {f"{label}": self}
        # Some tmp dir
        filename = filemanager.temp_path(f"{filename}")
        dump_h5(filename, data)
        # Delete array explicitly
        self.__del__()

    def load_array(self, label, filename=None):
        """Read some NIndexObject from disk and replace all array instances.
        NIndexObject will be read from ``temp_dir`` specified in ``filemanager``
        (globally defined)

        **Arguments:**

        label
            (str) The label used to store the attribute in the IOData container

        **Optional Arguments:**

        filename
            (str) The filename of the checkpoint file. Has to end with ``.h5``
        """
        # Use the pybest.io interface to read the checkpoint file
        filename = filename or f"checkpoint_{self.label}.h5"
        # Some tmp dir
        filename = filemanager.temp_path(filename)
        # check if file exists
        if not filename.exists():
            raise FileNotFoundError(
                f"Cannot find checkpoint file while loading array from {filename}"
            )
        # get data stored as dictionary with key `label`
        data = load_h5(filename)
        if label not in data:
            raise ArgumentError(f"Cannot find label {label}")
        data = data[label]
        self.replace_array(data)

    def contract(self, *args, **kwargs):
        """General NIndex contraction function

            NIndex = CholeskyFourIndex or DenseNIndex
            where N = One, Two, Three, Four

        *** Arguments ***

        * self : NIndex
              This is the first operand.

        * subscript : string
              Specifies the subscripts for summation as comma separated list
              of subscript labels, for example: 'abcd,efcd->abfe'.

        * operands : DenseNIndex
              These are the other arrays for the operation. If out keyword is
              not specified and the result of operation is not scalar value,
              the last operand is treated as out.

        *** Keyword arguments ***

        * out : DenseNIndex
              The product of operation is added to out.

        * factor : float
              The product of operation is multiplied by factor before it is
              added to out.

        * clear : boolean
               The out is cleared before the product of operation is added to
               out if clear is set to True.

        * select : string
               Specifies the contraction algorithm: One of:
               - 'opt_einsum' - opt_einsum.contract
               - 'einsum' - numpy.einsum function,
               - 'td' - operations with utilization of numpy.tensordot function,
               - 'cupy' - operations using the cupy library,
               - None - first tries 'cupy' (very fast but
                 only supported for a set of contractions), then 'td' routine.
                 In case of failure, it performs the 'einsum' operation.
               'td' is usually much faster, but it can result in increased
               memory usage and it is available only for specific cases.

        * optimize : {False, True, 'optimal'}
               Specifies contraction path for operation if select is set to
               'einsum'. For details, see numpy.einsum_path.

        * begin0, end0, begin1, ... :
               The lower and upper bounds for summation.
        """
        subscripts = args[0]
        factor = kwargs.get("factor", 1.0)
        select = kwargs.get("select", None)
        clear = kwargs.get("clear", False)
        opt = kwargs.get("optimize", "optimal")
        out = kwargs.get("out", None)
        save_memory = kwargs.get("save_memory", False)

        # Check if out is scalar
        scripts, outscript = parse_subscripts(subscripts)
        is_out_scalar = outscript in ("", "...")

        # If keyword out is None, use last argument as out. Determine operands.
        if (len(args) == len(scripts) + 1) and (out is None):
            operands = [self, *list(args[1:-1])]
            out = args[-1]
            arr = out.array
        else:
            operands = [self, *list(args[1:])]

        # Slice arrays of operands and create a list with operands (ndarrays)
        subs_, operands_ = parse_contract_input(subscripts, operands, kwargs)
        args_ = [subs_, *operands_]

        # Create output array if not given
        if (not is_out_scalar) and (out is None):
            from pybest.linalg import DenseLinalgFactory

            shape = get_outshape(subs_, operands_)
            out = DenseLinalgFactory.allocate_check_output(None, shape)

        # Clear out is required and reference to its _array attribute.
        if out is not None:
            if clear:
                out.clear()
            arr = out.array

        # 1. The product of operation is a scalar.
        if is_out_scalar:
            if out is not None:
                raise ArgumentError(
                    "Output operand should not be specified if the contraction"
                    " result is scalar."
                )
            if select == "td":
                return factor * td_helper(*args_)
            if select == "opt_einsum":
                return factor * oe_contract(*args_, optimize=opt)
            if select == "einsum":
                return factor * np.einsum(*args_, optimize=opt)
            if select == "cupy":
                if PYBEST_CUPY_AVAIL:
                    try:
                        return factor * cupy_helper(*args_, **kwargs)
                    except MemoryError:
                        return factor * td_helper(*args_)
                else:
                    select = None
            if select is None:
                try:
                    x = factor * td_helper(*args_)
                except ArgumentError:
                    x = factor * np.einsum(*args_, optimize=opt)
                return x
            raise UnknownOption(
                f"Unrecognized keyword: select = {select}.\n"
                "Do you mean one of: 'cupy', 'td', 'opt_einsum' or 'einsum'?\n"
            )

        # 2. The product of operation is DenseNIndexObject.
        slice_ = slice_output(subscripts, kwargs)

        if select == "td" and len(self.arrays) == 2:
            try:
                args_td = [subscripts, operands_, arr, factor, save_memory]
                cholesky_td_routine(*args_td)
            except (NotImplementedError, ValueError):
                try:
                    arr[:] += factor * td_helper(*args_)
                except ArgumentError:
                    raise ArgumentError(
                        f"{subscripts} cannot be done with select='td'."
                    ) from None

        elif select == "td":
            arr[slice_] += factor * td_helper(*args_)

        elif select == "opt_einsum":
            arr[slice_] += factor * oe_contract(*args_, optimize=opt)

        elif select == "einsum":
            arr[slice_] += factor * np.einsum(*args_, optimize=opt)

        elif select == "cupy":
            if PYBEST_CUPY_AVAIL:
                if args_[0] in cupy_optimized:
                    args_ = [*args_, arr]
                    arr[slice_] += factor * cupy_helper(*args_, **kwargs)
                else:
                    try:
                        arr[slice_] += factor * td_cupy_helper(
                            *args_, shape=arr[slice_].shape
                        )
                    except ArgumentError:
                        try:
                            args_cupy = [*args_, arr]
                            arr[slice_] += factor * cupy_helper(
                                *args_cupy, **kwargs
                            )
                        except (MemoryError, ArgumentError):
                            if log.do_high:
                                log.warn("Not enough VRAM.")
                                log.warn("Defaulting to numpy.tensordot.")
                            try:
                                if len(self.arrays) == 2:
                                    try:
                                        args_td = [
                                            subscripts,
                                            operands_,
                                            arr,
                                            factor,
                                            save_memory,
                                        ]
                                        cholesky_td_routine(*args_td)
                                    except NotImplementedError:
                                        arr[slice_] += factor * td_helper(
                                            *args_
                                        )
                                else:
                                    arr[slice_] += factor * td_helper(*args_)
                            except ArgumentError:
                                arr[slice_] += factor * oe_contract(
                                    *args_, optimize=opt
                                )
            else:
                arr[slice_] += factor * td_helper(*args_)

        elif select is None:
            if args_[0] in cupy_optimized and PYBEST_CUPY_AVAIL:
                args_ = [*args_, arr]
                arr[slice_] += factor * cupy_helper(*args_, **kwargs)
            else:
                try:
                    if len(self.arrays) == 2:
                        if PYBEST_CUPY_AVAIL:
                            try:
                                arr[slice_] += factor * td_cupy_helper(
                                    *args_, shape=arr[slice_].shape
                                )
                            except (ArgumentError, MemoryError):
                                try:
                                    args_td = [
                                        subscripts,
                                        operands_,
                                        arr,
                                        factor,
                                        save_memory,
                                    ]
                                    cholesky_td_routine(*args_td)
                                except NotImplementedError:
                                    arr[slice_] += factor * td_helper(*args_)
                        else:
                            try:
                                args_td = [
                                    subscripts,
                                    operands_,
                                    arr,
                                    factor,
                                    save_memory,
                                ]
                                cholesky_td_routine(*args_td)
                            except NotImplementedError:
                                arr[slice_] += factor * td_helper(*args_)
                    else:
                        # CuPy is not faster for dense matrices containing at most
                        # TwoIndex objects (yet). Thus, we skip those for the moment
                        # It is important that the largest NIndex object is the first
                        # operand (according to PyBEST convention)
                        if PYBEST_CUPY_AVAIL and args_[1].ndim > 2:
                            try:
                                arr[slice_] += factor * td_cupy_helper(
                                    *args_, shape=arr[slice_].shape
                                )
                            except (ArgumentError, MemoryError):
                                arr[slice_] += factor * td_helper(*args_)
                        else:
                            arr[slice_] += factor * td_helper(*args_)
                except ArgumentError:
                    arr[slice_] += factor * oe_contract(*args_, optimize=opt)

        else:
            raise UnknownOption(
                f"Unrecognized keyword: select = {select}.\n"
                "Do you mean one of: 'cupy', 'td', 'opt_einsum' or 'einsum'?\n"
            )

        return out

    def expand(self, *args: Any, **kwargs: dict[str, Any]) -> Any:
        """General NIndex expand function.
        It expands some NIndex objects along one or two axes and adds the
        corresponding result to some output NIndex object.

            NIndex = DenseNIndex, where N = One, Two, Three, Four

        *** Arguments ***

        * self : NIndex
              This is the first operand, accessed as operands[0].

        * subscript : string
              Specifies the subscripts for expansion as comma separated list
              of subscript labels, for example: 'abc->abcd'.

        *** Keyword arguments ***

        * out : DenseNIndex
              The product of operation is added to out.

        * factor : float
              The product of operation is multiplied by factor before it is
              added to out.

        * clear : boolean
               The out is cleared before the product of operation is added to
               out if clear is set to True.

        * begin0, end0, begin1, ... :
               The lower and upper bounds for summation.
        """
        # Get expansion recipe using np.einsum notation
        subscripts = args[0]
        # Generate copy of kwargs
        # Due to a possible contract operation, we need to remove all
        # unnecessary keys. To prevent data loss, we pop from a copy.
        kwargs_contract = {}
        for key, val in kwargs.items():
            kwargs_contract[key] = val
        # kwargs and kwargs_contract have the same key-value pair
        factor = kwargs_contract.pop("factor", 1.0)
        clear = kwargs_contract.pop("clear", False)
        out = kwargs_contract.pop("out", None)

        # Do sanity check (we guarantee a functional implementation for tested
        # cases only)
        if subscripts not in expand_valid_cases:
            raise ArgumentError(
                f"Found untested flavor {subscripts} in expand method."
            )

        # Parse subscripts into input and output scripts
        # Defined in contract.py
        inscript, outscript = parse_subscripts(subscripts)

        # If keyword out is None, use last argument as out. Determine operands.
        if (len(args) == len(inscript) + 1) and (out is None):
            operands = [self, *list(args[1:-1])]
            out = args[-1]
            arr = out.array
        else:
            operands = [self, *list(args[1:])]

        # Slice arrays of operands and create a list with operands (ndarrays)
        # Defined in contract.py
        subs_, operands_ = parse_contract_input(subscripts, operands, kwargs)

        # Create output array if not given
        if out is None:
            from pybest.linalg import DenseLinalgFactory

            shape = get_outshape(subs_, operands_)
            out = DenseLinalgFactory.allocate_check_output(None, shape)

        # Clear out if required and reference to its _array attribute.
        if out is not None:
            if clear:
                out.clear()
            arr = out.array

        # Choose expansion flavor and overwrite inscript
        # We distinguish three cases:
        # 0) special expansion case of the form ab->abab, where the output
        #    scripts contain any order of `a` and `b` as long as `a` and `b`
        #    show up twice. Input scripts are always of the from `ab`
        # 1) expansions of the form a->ab, where we have non-repeating indices
        #    in inscripts and outscripts
        # 2) expansions of the form a->aab or aa->ab, where we have repeating
        #    indices in either inscript or outscript. In the later case (aa->),
        #    we first perform a contraction (here aa->a) before expanding.
        #    Formally, we have a two-step process: aa->ab => aa->a => a->ab
        # For case 2, we have to update the inscripts in some cases.
        case, inscript = parse_expand_case(subscripts)

        # For case 2 (aa..->.. or abab->..), we first contract, then expand
        # Perform partial contraction of input operand and overwirte operands_[0]
        # If nothing is to be done, operands_[0] is returned
        operands_[0] = contract_operands(
            subscripts, operands, operands_, kwargs_contract
        )

        # Get the slice of the final output array
        # We need to do it before updating the subscripts due to partial contraction
        slice_ = slice_output(subscripts, kwargs)

        if subscripts in expand_diagonal_cases:
            # Expand operations of the form (special case):
            # ab->abab, ab->abba, ab->baab, etc. (starting with ab, expanding
            # two axes with a and two axes with b)
            # Get index of (first) axis a and b
            index_a, index_b = outscript.find("a"), outscript.find("b")
            # Get the corresponding array indices
            ind_a, ind_b = np.indices(
                (arr[slice_].shape[index_a], arr[slice_].shape[index_b])
            )
            # Distinguish between different order of a..b.. in the FourIndex
            # object (abab, abba, aabb, etc.)
            slice_abab = tuple(
                [ind_a if index == "a" else ind_b for index in outscript]
            )
            arr[slice_][slice_abab] += operands_[0] * factor
        elif case == 1:
            # Expand operations of the form:
            # a->ab, abc->abcd, etc. (non-repeating indices)
            # Get transposition of input (ab-> or ba->)
            trans = tuple(
                [inscript.find(i) for i in outscript if inscript.find(i) != -1]
            )
            # Get axis along which the array is to be expanded
            expand_axis = tuple(
                i
                for i, letter in enumerate(outscript)
                if letter not in inscript
            )
            # No need to assert shapes as numpy will raise an error for us
            arr[slice_] += (
                np.expand_dims(operands_[0].transpose(trans), axis=expand_axis)
                * factor
            )
        elif case == 2:
            # Expansion of the form a->aab, ab->aabc
            # Get axes for input and output arrays used for expansion loop
            index_inp, index_out = parse_repeated_expand_axes(
                inscript, outscript
            )
            # Get general ranges (we already work with sliced arrays of proper views)
            ranges_out: SupportsIndex | slice = [
                slice(None) for _ in outscript
            ]
            ranges_inp: SupportsIndex | slice = [slice(None) for _ in inscript]
            # Get range over summation index, which is the repeated index
            # stored in index_out or index_inp
            for i in range(arr[slice_].shape[index_out[0]]):
                # Allow for ...->aab
                for ind in index_out:
                    if ind != -1:
                        ranges_out[ind] = i
                # Allow for aa->ab..
                for ind in index_inp:
                    if ind != -1:
                        ranges_inp[ind] = i
                arr[slice_][tuple(ranges_out)] += (
                    operands_[0][tuple(ranges_inp)] * factor
                )
        else:
            raise UnknownOption(f"Unsupported expansion of type {subscripts}")

        return out

    def get_max_values(self, limit=None, absolute=True, threshold=1e-3):
        """Return list of tuples with maximal values and their indices."""
        # overwrite limit to avoid None value
        limit = 20 if limit is None else limit
        if absolute:
            indices = np.where(abs(self.array) > threshold)
        else:
            indices = np.where(self.array > threshold)
        # consider only sub-array
        array_ = self.array[indices]
        # sort indices in ascending order
        if absolute:
            sorted_ind = np.argsort(abs(array_))
        else:
            sorted_ind = np.argsort(array_)
        # reorder in descending order (largest first)
        sorted_ind = sorted_ind[::-1]
        # store final data as list ((indices), value)
        values = list()
        for i in sorted_ind:
            if len(values) >= limit:
                break
            index = list()
            # loop over all array dimensions
            for dim_a in range(len(indices)):
                index.append(indices[dim_a][i])
            values.append((tuple(index), array_[i]))

        return values


class OneIndex(NIndexObject):
    """Base class for OneIndex objects."""

    one_identifier = True

    @abc.abstractmethod
    def copy(self):
        """Create a copy of TwoIndex object."""

    @abc.abstractmethod
    def get_element(self, i):
        """Return element i of array"""

    @abc.abstractmethod
    def set_element(self, i, value):
        """Set element i of array"""


class TwoIndex(NIndexObject):
    """Base class for TwoIndex objects."""

    two_identifier = True

    @abc.abstractmethod
    def copy(self):
        """Create a copy of TwoIndex object."""

    @abc.abstractmethod
    def get_element(self, i, j):
        """Return element i,j of array."""

    @abc.abstractmethod
    def set_element(self, i, j, value, symmetry=2):
        """Set element i,j of array."""


class ThreeIndex(NIndexObject):
    """Base class for ThreeIndex objects."""

    three_identifier = True

    @abc.abstractmethod
    def copy(self):
        """Create a copy of TwoIndex object."""

    @abc.abstractmethod
    def get_element(self, i, j, k):
        """Return element i,j,k of array."""

    @abc.abstractmethod
    def set_element(self, i, j, k, value):
        """Set element i,j,k of array."""


class FourIndex(NIndexObject):
    """Base class for FourIndex objects."""

    four_identifier = True

    @abc.abstractmethod
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
        """Create a copy of FourIndex object."""

    @abc.abstractmethod
    def get_element(self, i, j, k, l):
        """Return element i,j,k,l of array."""

    @abc.abstractmethod
    def set_element(self, i, j, k, l, value, symmetry=8):
        """Set element i,j,k,l of array."""


def parse_four_index_transform_exps(exp0, exp1, exp2, exp3, Class):
    """Parse the optional arguments exp1, exp2 and exp3.

    **Arguments:**

    exp0, exp1, exp2, exp3
         Four sets of orbitals for the mo transformation. Some may be None
         but only the following not None combinations are allowed:

         * ``(exp0,)``: maintain eight-fold symmetry (if any)
         * ``(exp0, exp1)``: maintain four-fold symmetry (if any)
         * ``(exp0, exp2)``: maintain two-fold symmetry (if any)
         * ``(exp0, exp1, exp2, exp3)``: break all symmetry

    Class
         The expected class of the exps objects.


    **Returns:** exp0, exp1, exp2, exp3. (All not None)
    """
    # Four supported situations
    if exp1 is None and exp2 is None and exp3 is None:
        # maintains eight-fold symmetry
        exp1 = exp0
        exp2 = exp0
        exp3 = exp0
    elif exp2 is None and exp3 is None:
        # maintains four-fold symmetry
        exp2 = exp0
        exp3 = exp1
    elif exp1 is None and exp3 is None:
        # maintains two-fold symmetry
        exp1 = exp0
        exp3 = exp2
    elif exp1 is None or exp2 is None or exp3 is None:
        # the only other allowed case is no symmetry.
        raise ArgumentError(
            "It is not clear how to interpret the optional arguments exp1, exp2 and exp3."
        )
    if not isinstance(exp0, Class):
        raise TypeError(
            f"Wrong instance for exp0. Got {exp0.__class__.__name__}."
        )
    if not isinstance(exp1, Class):
        raise TypeError(
            f"Wrong instance for exp0. Got {exp0.__class__.__name__}."
        )
    if not isinstance(exp2, Class):
        raise TypeError(
            f"Wrong instance for exp0. Got {exp0.__class__.__name__}."
        )
    if not isinstance(exp3, Class):
        raise TypeError(
            f"Wrong instance for exp0. Got {exp0.__class__.__name__}."
        )
    return exp0, exp1, exp2, exp3


class FiveIndex(NIndexObject):
    """Base class for FiveIndex objects."""

    five_identifier = True

    @abc.abstractmethod
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
        """Create a copy of FiveIndex object."""

    # set an get should be deleted eventually
    @abc.abstractmethod
    def get_element(self, i, j, k, l, m):
        """Return the element at indices i, j, k, l, m of the array."""

    @abc.abstractmethod
    def set_element(self, i, j, k, l, m, value):
        """Set a matrix element

        **Arguments:**

        i, j, k, l, m
             The matrix indices to be set

        value
             The value to be assigned to the matrix element.
        """


class SixIndex(NIndexObject):
    """Base class for SixIndex objects."""

    six_identifier = True

    @abc.abstractmethod
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
        begin5=0,
        end5=None,
    ):
        """Create a copy of SixIndex object."""

    @abc.abstractmethod
    def get_element(self, i, j, k, l, m, n):
        """Return the element at indices i, j, k, l, m, n of the array."""

    @abc.abstractmethod
    def set_element(self, i, j, k, l, m, n, value):
        """Set a matrix element

        **Arguments:**

        i, j, k, l, m, n
             The matrix indices to be set

        value
             The value to be assigned to the matrix element.
        """


class EightIndex(NIndexObject):
    """Base class for EightIndex objects.

    Args:
        NIndexObject (NIndexObject): The base class for objects with N indices, providing core functionality and interface for subclasses.
    """

    eight_identifier = True

    @abc.abstractmethod
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
        begin5=0,
        end5=None,
        begin6=0,
        end6=None,
        begin7=0,
        end7=None,
    ):
        """Create a copy of EightIndex object.

        Args:
            begin0 (int, optional): The starting index for the slice along the zeroth axis. Defaults to 0.
            end0 (int | None, optional): The ending index for the slice along the zeroth axis. Defaults to None.
            begin1 (int, optional): The starting index for the slice along the first axis. Defaults to 0.
            end1 (int | None, optional): The ending index for the slice along the first axis. Defaults to None.
            begin2 (int, optional): The starting index for the slice along the second axis. Defaults to 0.
            end2 (int | None, optional): The ending index for the slice along the second axis. Defaults to None.
            begin3 (int, optional): The starting index for the slice along the third axis. Defaults to 0.
            end3 (int | None, optional): The ending index for the slice along the third axis. Defaults to None.
            begin4 (int, optional): The starting index for the slice along the fourth axis. Defaults to 0.
            end4 (int | None, optional): The ending index for the slice along the fourth axis. Defaults to None.
            begin5 (int, optional): The starting index for the slice along the fifth axis. Defaults to 0.
            end5 (int | None, optional): The ending index for the slice along the fifth axis. Defaults to None.
            begin6 (int, optional): The starting index for the slice along the sixth axis. Defaults to 0.
            end6 (int | None, optional): The ending index for the slice along the sixth axis. Defaults to None.
            begin7 (int, optional): The starting index for the slice along the seventh axis. Defaults to 0.
            end7 (int | None, optional): The ending index for the slice along the seventh axis. Defaults to None.
        """

    @abc.abstractmethod
    def get_element(self, i, j, k, l, m, n, o, p):
        """Return the element at indices i, j, k, l, m, n, o, p of the array.

        Args:
            i (int): The index along the zeroth axis.
            j (int): The index along the first axis.
            k (int): The index along the second axis.
            l (int): The index along the third axis.
            m (int): The index along the fourth axis.
            n (int): The index along the fifth axis.
            o (int): The index along the sixth axis.
            p (int): The index along the seventh axis.
        """

    @abc.abstractmethod
    def set_element(self, i, j, k, l, m, n, o, p, value):
        """Set the element at indices i, j, k, l, m, n, o, p of the array to the given value.

        Args:
            i (int): The index along the zeroth axis.
            j (int): The index along the first axis.
            k (int): The index along the second axis.
            l (int): The index along the third axis.
            m (int): The index along the fourth axis.
            n (int): The index along the fifth axis.
            o (int): The index along the sixth axis.
            p (int): The index along the seventh axis.
            value (float): The value to be assigned to the matrix element.
        """
