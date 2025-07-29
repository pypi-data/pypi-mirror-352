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
# 11/2024: This file has been written by Seyedehdelaram Jahani (original version)
# 09/2024: Rewrite of PropertyBase (Kasia Boguslawski)
#
#
# Detailed changes:
# See CHANGELOG

"""Base property class containing various property implementations

For more information see doc-strings.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from pybest.cache import Cache
from pybest.constants import CACHE_DUMP_ACTIVE_ORBITAL_THRESHOLD as CACHE_THR
from pybest.exceptions import (
    ArgumentError,
    NonEmptyData,
)
from pybest.featuredlists import OneBodyHamiltonian, TwoBodyHamiltonian
from pybest.iodata import CheckPoint, IOData
from pybest.linalg import (
    DenseLinalgFactory,
    FourIndex,
    LinalgFactory,
    OneIndex,
    ThreeIndex,
    TwoIndex,
)
from pybest.log import log
from pybest.occ_model.occ_base import OccupationModel
from pybest.utility import (
    check_options,
    unmask,
    unmask_orb,
)


class PropertyBase(ABC):
    """Base class for determining various properties obtained by different methods
    Property                   -->  Method:

    Orbital Energy             -->  Koopmans' theorem
    Orbital Energy             -->  Modified Koopmans' theorem
    Orbital Energy             -->  Extended Koopmans' theorem

    Transition Dipole Moment   -->  Linear response method
    Transition Polarizability  -->  Linear response method

    Dipole Moment              -->  Expectation value DMs
    Dipole Moment              -->  Response DMs

    Quadrupole Moment          -->  Expectation value DMs
    Quadrupole Moment          -->  Response DMs

    """

    def __init__(self, lf: LinalgFactory, occ_model: OccupationModel) -> None:
        """Initialize class attributes common to all property child classes.

        Args:
            lf (LinalgFactory): A LinalgFactory instance
            occ_model (OccupationModel): The chosen occupation model
        """
        log.cite("Entering the property module")

        self._lf = lf
        self._dense_lf = DenseLinalgFactory(lf.default_nbasis)
        self._occ_model = occ_model

        # Intermediate Hamiltonian as an instance of Cache
        self._cache = Cache()
        self._dump_cache = self._occ_model.nact[0] > CACHE_THR
        self._e_core = 0.0

        self._checkpoint = CheckPoint({})
        self._checkpoint_fn = f"checkpoint_{self.acronym}.h5"
        # Include occupation model into checkpoint file (IOData container)
        self.checkpoint.update("occ_model", self.occ_model)

    @property
    def lf(self) -> LinalgFactory:
        """The linalg factory"""
        return self._lf

    @property
    def dense_lf(self) -> DenseLinalgFactory:
        """The dense linalg factory"""
        return self._dense_lf

    @property
    def cache(self) -> Cache:
        """The Cache instance used to store property data in memory"""
        return self._cache

    @property
    def occ_model(self) -> OccupationModel:
        """The occupation model"""
        return self._occ_model

    @property
    def checkpoint(self) -> CheckPoint:
        """The IOdata container that contains all data dump to disk"""
        return self._checkpoint

    @property
    def checkpoint_fn(self) -> str:
        """The filename that will be dumped to disk"""
        return self._checkpoint_fn

    @property
    def e_core(self) -> float:
        """The core energy"""
        return self._e_core

    @abstractmethod
    def print_results(self) -> None:
        """Print all information about the investigated property"""

    @abstractmethod
    def read_input(self, *args: Any, **kwargs: Any) -> Any:
        """Read input parameters and keyword options for transforming electron integrals and
        return the transformed integrals.
        """

    @abstractmethod
    def prepare_intermediates(self, *args: Any, **kwargs: Any) -> None:
        """Derive all effective Hamiltonian elements.
        gppqq:   <pp|qq>,
        gpqpq:   <pq|pq>,
        fock:    h_pp + sum_i(2<pi|pi>-<pi|ip>)
        """

    @abstractmethod
    def get_property(self) -> None:
        """Get the peroperty from related submodule"""

    def unmask_args(self, *args: Any, **kwargs: Any) -> Any:
        """Resolve arguments passed to function call"""
        #
        # olp
        #
        olp = unmask("olp", *args, **kwargs)
        if olp is None:
            raise ArgumentError(
                "Cannot find overlap integrals in function call."
            )
        self.checkpoint.update("olp", olp)

        #
        # orb
        #
        orbs = unmask_orb(*args, **kwargs)
        if orbs:
            orbs = orbs[0]
            self.checkpoint.update("orb_a", orbs.copy())
        else:
            raise ArgumentError("Cannot find orbitals.")
        #
        # 1-e ints and 2-e ints
        #
        one = self.lf.create_two_index(label="one")
        for arg in args:
            if isinstance(arg, TwoIndex):
                if arg.label in OneBodyHamiltonian:
                    one.iadd(arg)
            elif isinstance(arg, FourIndex):
                if arg.label in TwoBodyHamiltonian:
                    two = arg
        return one, two, orbs

    def get_size(self, string: str | Sequence[int]) -> tuple[int, ...]:
        """Return list of arguments containing sizes of tensors

        **Arguments:**

        string : string or int
            any sequence of "o" (occupied) and "v" (virtual) OR a tuple of
            integers indicating the sizes of an array
        """
        args = []
        for char in string:
            if char == "o":
                args.append(self.nacto)
            elif char == "v":
                args.append(self.nactv)
            elif isinstance(char, int):
                args.append(char)
            else:
                raise ArgumentError(f"Do not know how to handle size {char}.")
        return tuple(args)

    def print_info(self, **kwargs: dict[str, Any]) -> None:
        """Print information related to property submodule"""
        do_print = kwargs.get("print", True)
        # Print only if wanted
        if log.do_medium and do_print:
            log.hline()
            log(" ")
            log(f"Entering {self.long_name} module:")
            log(" ")
            log.hline()
            log("OPTIMIZATION PARAMETERS:")
            log(f"Number of frozen cores:        {self.occ_model.ncore[0]}")
            log(f"Number of active occupied:     {self.occ_model.nacto[0]}")
            log(f"Number of active virtuals:     {self.occ_model.nactv[0]}")
            log.hline("~")

    def clear_cache(self, **kwargs: dict[str, Any]) -> None:
        """Clear the Cache instance

        Kwargs:
            tags (str): the tag of the cache item to be cleared
        """
        for name in kwargs:
            check_options(name, name, "tags")
            # Tag 'p' relates to the property module
        tags = kwargs.get("tags", "p")

        self.cache.clear(tags=tags, dealloc=True)

    def __call__(self, *args: Any, **kwargs: dict[str, Any]) -> IOData:
        """Execute a base command sequence similar to all property submodules

        Returns:
            IOData: An IOData container instance
        """
        #
        # Unmask all property-specific args and kwargs
        # and store them in self.checkpoint
        #
        self.unmask_args(*args, **kwargs)
        #
        # Print property-specific information
        #
        self.print_info(**kwargs)
        #
        # Read input:
        #
        self.read_input(*args, **kwargs)
        #
        # Prepare intermediates required for property
        # calculation. This contains, amongst others,
        # integrals, integral transformations, effective
        # Hamiltonians, etc.
        #
        self.prepare_intermediates(*args, **kwargs)
        #
        # Do the actual property calculation
        #
        self.get_property()
        #
        # Print property-specific options
        #
        self.print_results()

        return self.checkpoint()

    def from_cache(
        self, select: str
    ) -> OneIndex | TwoIndex | ThreeIndex | FourIndex:
        """Get a matrix/tensor from the cache.

        Args:
            select (str): some object stored in the Cache

        Raises:
            NotImplementedError: if not found in Cache

        Returns:
            NIndex: Either OneIndex or TwoIndex or ThreeIndex or FourIndex
        """
        if select in self.cache:
            return self.cache.load(select)
        raise NotImplementedError

    def init_cache(
        self, select: str, *args: Any, **kwargs: dict[str, Any]
    ) -> OneIndex | TwoIndex | ThreeIndex | FourIndex:
        """Initialize some cache instance

        Args:
            select (str): label of the auxiliary tensor
            args (list[int]): The size of the auxiliary matrix in each dimension.
                              The number of given arguments determines the order
                              and sizes of the tensor. Either a tuple or a string
                              (oo, vv, ovov, etc.) indicating the sizes.
                              Not required if ``alloc`` is specified.

        Kwargs:
            tags (str): The tag used for storing some matrix/tensor in the Cache
                        (default `p`).
            alloc (callable): Specify alloc function explicitly. If not defined
                              some flavor of `self.lf.create_N_index` is taken
                              depending on the length of args.
            nvec (int): Number of Cholesky vectors. Only required if Cholesky-
                        decomposed ERI are used. In this case, only ``args[0]``
                        is required as the Choleskyn class does not support
                        different sizes of the arrays.

        Raises:
            ArgumentError: Raised if no allocation can be performed
            NonEmptyData: Raised if array already exists in the cache

        Returns:
            OneIndex | TwoIndex | ThreeIndex | FourIndex: Some NIndex object
        """
        for name, _ in kwargs.items():
            check_options(name, name, "tags", "nvec", "alloc")
        tags = kwargs.get("tags", "p")
        nvec = kwargs.get("nvec", None)
        alloc = kwargs.get("alloc", None)
        # Resolve args: either pass dimensions or string indicating dimensions
        args = self.get_size(args)

        if len(args) == 0 and not alloc:
            raise ArgumentError(
                "At least one dimension or a user-defined allocation function "
                "have to be specified"
            )
        if alloc:
            pass
        elif nvec is not None:
            alloc = (self.lf.create_four_index, args[0], nvec)
        elif len(args) == 1:
            alloc = (self.lf.create_one_index, *args)
        elif len(args) == 2:
            alloc = (self.lf.create_two_index, *args)
        elif len(args) == 3:
            alloc = (self.lf.create_three_index, *args)
        else:
            alloc = (self.dense_lf.create_four_index, *args)
        # Load into the cache
        matrix, new = self.cache.load(select, alloc=alloc, tags=tags)
        if not new:
            raise NonEmptyData(
                f"The Cache instance {select} already exists. "
                "Call clear prior to updating the Cache instance."
            )

        return matrix

    def get_range(self, string: str, offset: int = 0) -> dict[str, int]:
        """Return dictionary with keys beginX, endX, begin(X+1), etc.
        *  string - any sequence of 'o' (occupied), 'v' (virtual)
                    'V' (virtual starting with index 0),
                    'n' (all active basis functions)
        Args:
            string (str): any sequence of 'o' (occupied), 'v' (virtual)
                          'V' (virtual starting with index 0,
                          'n' (all active basis functions)
            offset (int, optional): Move begin/end index to offset. Defaults to 0.

        Raises:
            ValueError: Unknown character for string

        Returns:
            dict[str, int]: Dictionary containing the range of a view of an array
        """
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        nact = self.occ_model.nact[0]

        range_ = {}
        ind = offset
        for char in string:
            if char == "o":
                range_[f"begin{ind}"] = 0
                range_[f"end{ind}"] = nacto
            elif char == "v":
                range_[f"begin{ind}"] = nacto
                range_[f"end{ind}"] = nact
            elif char == "V":
                range_[f"begin{ind}"] = 0
                range_[f"end{ind}"] = nactv
            elif char == "n":
                range_[f"begin{ind}"] = 0
                range_[f"end{ind}"] = nact
            else:
                raise ValueError(f"Do not know how to handle choice {char}")
            ind += 1
        return range_
