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
# This module has been originaly written and updated by Katharina Boguslawski (see CHANGELOG)
# Its current version contains updates from the PyBEST developer team.
#
# An original version of this implementation can also be found in 'Horton 2.0.0'.
# However, this file has been updated and debugged. Compatibility with Horton is NOT
# guaranteed.
#
# 10.2022:
# This module has been rewritten by Emil Sujkowski
#
# Moved out from here
# To rpccd base:
# - get_ndm
# - generate_gues
# - get_guess
#
# Moved here from rpccd_base.py:
# - clear_aux_matrix
# - get_aux_matrix
# - init_aux_matrix
# - clear
#
# New methods:
# - defined compute_1dm and compute_2dm as abstract methods
# - defined geminals and Lagrange setter as abstract method
# - created abstract method _get_alloc_size
# - created abstract method update_ndm
#
# All aux_matrix methods has been replaced by cache methods
# - clear_aux_matrix -> clear_cache
# - get_aux_matrix -> from_cache
# - init_aux_matrix -> init_cache
#
# - added cashe property
# - ncore, npairs, nocc, nvirt, nbasis variables has been removed and replaced by
#   the use of occ_model
# - geminal and Lagrange setter are defined in rpccd_base
#
# 2024: Seyedehdelaram Jahani: orbital energies
# 2024: Seyedehdelaram Jahani: moved orbital energies to a separate module
#
#
# Detailed changes:
# See CHANGELOG


"""Correlated wavefunction implementations

This is a general geminals class.

Variables used in this module:
 :nacto:     number of electron pairs
             (abbreviated as no)
 :nactv:     number of (active) virtual orbitals in principal configuration
             (abbreviated as nv)
 :ncore:     number of core orbitals
             (abbreviated as nc)
 :nact:      total number of basis functions
             (abbreviated as na)

 Indexing convention:
  :i,j,k,..: occupied orbitals of principal configuration
  :a,b,c,..: virtual orbitals of principal configuration
  :p,q,r,..: general indices (occupied, virtual)

 Abbreviations used (if not mentioned in doc-strings):
  :L_pqrs: 2<pq|rs>-<pq|sr>
  :g_pqrs: <pq|rs>

 For more information see doc-strings.
"""

from abc import ABC, abstractmethod
from functools import reduce
from itertools import permutations
from math import fsum  # NOTE: fsum really needed for accuracy?
from operator import mul

import numpy as np

from pybest.cache import Cache
from pybest.exceptions import (
    ArgumentError,
    ConsistencyError,
    NonEmptyData,
    RestartError,
    UnknownOption,
)
from pybest.featuredlists import OneBodyHamiltonian
from pybest.gbasis import Basis
from pybest.iodata import CheckPoint
from pybest.linalg import FourIndex, Orbital, TwoIndex
from pybest.linalg.dense.dense_linalg_factory import DenseLinalgFactory
from pybest.log import log
from pybest.utility import (
    check_lf,
    check_options,
    check_type,
    project_orbitals_frozen_core,
    split_core_active,
    transform_integrals,
    unmask,
    unmask_orb,
)


class GeminalsBase(ABC):
    """A collection of geminal models and optimization routines.

    This is just a base class that serves as a template for
    specific implementations.
    """

    acronym = ""
    long_name = ""
    reference = ""
    cluster_operator = ""
    comment = ""

    def __init__(
        self,
        lf,
        occ_model,
        freezerot=None,
    ):
        """
        **Arguments:**

        lf
             A LinalgFactory instance.

        occ_model
             Occupation model

        **Optional arguments:**

        freezerot
             freezes selected blocks of the orbital rotations
             Possible choices are "vv", "oo", and "ov" or any combination of it

        npairs
             Number of electron pairs, if not specified,
             npairs = number of occupied orbitals

        nvirt
             Number of virtual orbitals, if not specified,
             nvirt = (nbasis-npairs)

        """
        log.cite("the pCCD method", "boguslawski2014a", "boguslawski2014b")

        self._lf = lf
        self._denself = DenseLinalgFactory(lf.default_nbasis)
        self._occ_model = occ_model

        nc = self.occ_model.ncore[0]
        no = self.occ_model.nacto[0]
        nv = self.occ_model.nactv[0]

        self._cache = Cache()
        self._e_core = 0
        self._geminal_matrix = None
        self._lagrange_matrix = None
        # TODO: This is a quick hack and should be cleaned up in the future
        self._freezerot = freezerot
        self._norbiter = 0
        if freezerot is not None:
            for el in freezerot:
                check_options("freezerot", el, "vv", "ov", "oo")
        self._energy = {}
        self._checkpoint = CheckPoint({})
        # dump mos only once
        self._mo2_dumped = False
        #
        # Update IOData container with default parameters for molecule
        #

        self.checkpoint.update("ncore", nc)
        self.checkpoint.update("nocc", no)
        self.checkpoint.update("nvirt", nv)
        self.checkpoint.update("occ_model", self.occ_model)

    def __call__(self, *args, **kwargs):
        """Optimize geminal coefficients and---if required---find
        optimal set of orbitals.

        **Arguments:**

        one, two
             One- and two-body integrals (some Hamiltonian matrix elements).

        core
             The core energy (not included in 'one' and 'two').

        orb
             DenseOrbital instance. It contains the MO coefficients
             (orbitals).

        olp
             The AO overlap matrix. A TwoIndex instance.

        **Keywords:**
             See :py:meth:`Geminals.solve`
             and :py:meth:`OOGeminals.solve`
        """
        one = self.lf.create_two_index(label="one")
        # olp
        olp = unmask("olp", *args, **kwargs)
        # orb; we have to use unmask_orb here
        orbs = unmask_orb(*args, **kwargs)
        # If orbs are passed in **kwargs, pop them as solve function does not
        # accept it
        kwargs.pop("orb_a", None)
        if not orbs and kwargs.get("restart", False):
            orbs = [None]
        elif not orbs:
            raise ArgumentError("Cannot find orbitals in function call.")
        else:
            # create a copy of the orbitals to avoid overwrite of all input
            # containers; copy ONLY container orbitals
            orbs = [orb.copy() for orb in orbs]
        # 1-e ints and 2-e ints
        one = self.lf.create_two_index(label="one")
        for arg in args:
            if isinstance(arg, TwoIndex):
                if arg.label in OneBodyHamiltonian:
                    one.iadd(arg)
            elif isinstance(arg, FourIndex):
                check_lf(self.lf, arg)
                two = arg

        # Consistency check: look for occ_model in passed IOData container
        # and compare to instance property
        occ_model = unmask("occ_model", *args, **kwargs)
        if occ_model is not None:
            self.check_coordinates(occ_model)
        # Solve function only works for restricted orbitals
        # FIXME: passing some args twice. Clean-up later (too invasive for now).
        return self.solve(one, two, olp, *orbs, *args, **kwargs)

    @property
    def occ_model(self):
        """The occupation model"""
        return self._occ_model

    @property
    def cache(self):
        """A cache instance"""
        return self._cache

    # TODO: This is a quick hack and should be cleaned up in the future
    @property
    def freezerot(self):
        """Freeze orbital rotations"""
        return self._freezerot

    @property
    def denself(self):
        """The LinalgFactory instance"""
        return self._denself

    @property
    def lf(self):
        """The LinalgFactory instance"""
        return self._lf

    @property
    def e_core(self):
        """The core energy"""
        return self._e_core

    @e_core.setter
    def e_core(self, new):
        """Update core energy"""
        self._e_core = new

    @property
    def dimension(self):
        """The number of unknowns (i.e. the number of geminal coefficients)"""
        return self.occ_model.nacto[0] * self.occ_model.nactv[0]

    @property
    def geminal_matrix(self):
        """The geminal coefficients"""
        return self._geminal_matrix

    @property
    def lagrange_matrix(self):
        """The Lagrange multipliers"""
        return self._lagrange_matrix

    @property
    def norbiter(self):
        """The number of orbital optimization steps"""
        return self._norbiter

    @norbiter.setter
    def norbiter(self, new):
        """Update number of orbital rotation steps"""
        self._norbiter = new

    @property
    def checkpoint(self):
        """The iodata container that contains all data dump to disk"""
        return self._checkpoint

    @property
    def energy(self):
        """The energy dictionary (e_tot, e_corr, e_ref)"""
        return self._energy

    @energy.setter
    def energy(self, energy_dict):
        """Update energies in dictionary"""
        self._energy.update(energy_dict)

    @energy.deleter
    def energy(self):
        """Clear energy information"""
        self._energy = {}

    @property
    def mo2_dumped(self):
        """Boolean to check whether 2-el mos have been dumped."""
        return self._mo2_dumped

    @mo2_dumped.setter
    def mo2_dumped(self, new):
        """Update mo2_dumped"""
        if not isinstance(new, bool):
            raise ArgumentError(
                f"Unknown type for {new}. Excepted bool, got {type(new)} instead."
            )
        self._mo2_dumped = new

    def __clear__(self):
        """Clear all wavefunction information"""
        self.clear()

    def clear(self):
        """Clear all wavefunction information"""
        self.cache.clear()

    def clear_dm(self):
        """Clear RDM information"""
        self.cache.clear(tags="d", dealloc=True)

    def get_size(self, string):
        """Returns list of arguments containing sizes of tensors

        **Arguments:**

        string : string or int
            any sequence of "o" (occupied) and "v" (virtual) OR a tuple of
            integers indicating the sizes of an array
        """
        no = self.occ_model.nacto[0]
        nv = self.occ_model.nactv[0]

        args = []
        for char in string:
            if char == "o":
                args.append(no)
            elif char == "v":
                args.append(nv)
            elif isinstance(char, int):
                args.append(char)
            else:
                raise ArgumentError(f"Do not know how to handle size {char}.")
        return tuple(args)

    def clear_cache(self, **kwargs):
        """Clear the Cache instance

        **Keyword arguments:**

        tags
             The tag used for storing some matrix/tensor in the Cache (default
             `h`).
        """
        for name in kwargs:
            check_options(name, name, "tags")
        tags = kwargs.get("tags", "h")

        self.cache.clear(tags=tags, dealloc=True)

    @abstractmethod
    def update_hamiltonian(self, select, two_mo, one_mo=None):
        """Derive all effective Hamiltonian elements.
        gppqq:   <pp|qq>,
        gpqpq:   <pq|pq>,
        lpqpq:   2<pq|pq>-<pq|qp>,
        fock:    h_pp + sum_i(2<pi|pi>-<pi|ip>)

        **Arguments:**

        select
             ``scf``.

        two_mo
             two-electron integrals in the MO basis. A FourIndex instance.

        one_mo
             one-electron integrals in the MO basis. A TwoIndex instance.
        """

    def from_cache(self, select):
        """Get a matrix/tensor from the cache.

        **Arguments:**

        select
            (str) some object stored in the Cache.
        """
        if select in self.cache:
            return self.cache.load(select)
        raise NotImplementedError

    def init_cache(self, select, *args, **kwargs):
        """Initialize some cache instance

        **Arguments:**

        select

            (str) label of the auxiliary tensor

        args
            The size of the auxiliary matrix in each dimension. The number of given
            arguments determine the order and sizes of the tensor.
            Either a tuple or a string (oo, vv, ovov, etc.) indicating the sizes.
            Not required if ``alloc`` is specified.

        **Keyword Arguments:**

        tags
            The tag used for storing some matrix/tensor in the Cache (default
            `h`).

        alloc
            Specify alloc function explicitly. If not defined, some flavor of
            `self.lf.create_N_index` is taken depending on the length of args.

        nvec
            A number of Cholesky vectors. Only required if Cholesky-decomposed ERI
            are used. In this case, only ``args[0]`` is required as the Cholesky
            class does not support different sizes of arrays.
        """
        for name, _ in kwargs.items():
            check_options(name, name, "tags", "nvec", "alloc")
        tags = kwargs.get("tags", "h")
        nvec = kwargs.get("nvec", None)
        alloc = kwargs.get("alloc", None)
        # resolve args: either pass dimensions or string indicating dimensions
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
            alloc = (self.denself.create_four_index, *args)
        # load into the cache
        matrix, new = self.cache.load(select, alloc=alloc, tags=tags)
        if not new:
            raise NonEmptyData(
                f"The Cache instance {select} already exists. "
                "Call clear prior to updating the Cache instance."
            )

        return matrix

    @abstractmethod
    def compute_1dm(self, dmout, mat1, mat2, select, factor):
        """Compute 1-RDM

        **Arguments:**

        dmout
             The output DM

        mat1, mat2
             A DenseTwoIndex instance used to calculated 1-RDM. For response
             RDM, mat1 is the geminal matrix, mat2 the Lagrange multipliers

        select
             Switch between response and PS2 1-RDM

        **Optional arguments:**

        factor
             A scalar factor
        """

    @abstractmethod
    def compute_2dm(self, dmout, mat1, mat2, select, factor):
        """Compute 2-RDM

        ** Arguments **


            A 1DM. A OneIndex instance.

        mat1, mat2
            TwoIndex instances used to calculate the 2-RDM. To get the
            response DM, mat1 is the geminal coefficient matrix, mat2 are the
            Lagrange multipliers

        select
            Either 'two_dm_(r)ppqq' or 'two_dm_(r)pqpq'. Note that the elements
            (iiii), i.e., the 1DM, are stored in pqpq, while the elements (aaaa) are
            stored in ppqq.

        **Optional arguments:**

        factor
             A scalar factor
        """

    @abstractmethod
    def _get_alloc_size(self, select):
        """Returns dictionary for init_ndm."""

    def init_ndm(self, select):
        """Initialize an n-RDM object

        **Arguments**

        select
             'ps2' or 'response'.
        """
        alloc_method = {
            "one_dm": self.compute_1dm,
            "two_dm": self.compute_2dm,
        }
        for key, value in alloc_method.items():
            if key in select:
                method = value
        dm, new = self.cache.load(
            select,
            alloc=self._get_alloc_size(select),
            tags="d",
        )
        if not new:
            raise NonEmptyData(
                f"The matrix {select} already exists. Call clear prior updating DMs."
            )

        return dm, method

    @abstractmethod
    def update_ndm(self, select, ndm=None):
        """Update n-RDM

        **Arguments:**

        select
             One of ``ps2``, ``response``

        **Optional arguments:**

        ndm
             When provided, this n-RDM is stored.
        """

    # Initial guess generators:
    @abstractmethod
    def generate_guess(self, guess, dim=None, mo1=None, mo2=None):
        """Generate a guess of type 'guess'.

        **Arguments:**

        guess
            A dictionary, containing the type of guess.

        **Optional arguments:**

        dim
            Length of guess.
        """

    @abstractmethod
    def get_guess(self, one, two, olp, orb, **kwargs):
        """**Arguments:**

        one, two
             One- (TwoIndex instance) and two-body integrals (FourIndex or
             Cholesky instance) (some Hamiltonian matrix elements)

        orb
             An expansion instance. It contains the MO coefficients.

        olp
             The AO overlap matrix. A TwoIndex instance.

        For keyword arguments see child classess
        """

    # solve is defined in geminals and oogeminals
    def solve(self, one, two, olp, orb, *args, **kwargs):
        raise NotImplementedError

    def compute_rotation_matrix(self, coeff):
        """Compute orbital rotation matrix"""
        raise NotImplementedError

    # Check convergence:
    @staticmethod
    def check_convergence(e0, e1, gradient, thresh):
        """Check convergence.

        **Arguments:**

        e0, e1
             Used to calculate energy difference e0-e1

        gradient
             The gradient, a OneIndex instance

        thresh
             Dictionary containing threshold parameters ('energy', 'gradientmax',
             'gradientnorm')

        **Returns:**
             True if energy difference, norm of orbital gradient, largest
             element of orbital gradient are smaller than some threshold
             values.
        """
        return (
            abs(e0 - e1) < thresh["energy"]
            and gradient.get_max() < thresh["gradientmax"]
            and gradient.norm() < thresh["gradientnorm"]
        )

    @staticmethod
    def check_stepsearch(linesearch):
        """Check trustradius. Abort calculation if trustradius is smaller than
        1e-8
        """
        return (
            linesearch.method == "trust-region"
            and linesearch.trustradius < 1e-8
        )

    @staticmethod
    def prod(lst):
        return reduce(mul, lst)

    def perm(self, a):
        """Calculate the permament of a matrix

        **Arguments**

        a
             A np array
        """
        check_type("matrix", a, np.ndarray)
        n = len(a)
        r = range(n)
        s = permutations(r)
        return fsum(self.prod(a[i][sigma[i]] for i in r) for sigma in s)

    def get_range(self, string, start=0):
        """Returns dictionary with keys beginX, endX, begin(X+1), etc.
        *  string - any sequence of 'o' (occupied) and 'v' (virtual)
        """
        no = self.occ_model.nacto[0]
        nv = self.occ_model.nactv[0]
        na = self.occ_model.nact[0]

        range_ = {}
        ind = start
        for char in string:
            if char == "o":
                range_[f"begin{ind}"] = 0
                range_[f"end{ind}"] = no
            elif char == "v":
                range_[f"begin{ind}"] = no
                range_[f"end{ind}"] = na
            elif char == "V":
                range_[f"begin{ind}"] = 0
                range_[f"end{ind}"] = nv
            elif char == "n":
                range_[f"begin{ind}"] = 0
                range_[f"end{ind}"] = na
            else:
                raise UnknownOption(
                    f"Do not know how to handle choice {char}."
                )
            ind += 1
        return range_

    def dump_eri(self, eri):
        """Dump eri (here in AO basis)

        **Arguments:**

        eri
             The electron repulsion integrals

        """
        if not self.mo2_dumped:
            # Dump and delete
            eri.dump_array("eri")
            # update mo2_dumped flag
            self.mo2_dumped = True
        else:
            # ERI are already dumped, just delete array
            eri.__del__()

    def transform_integrals(self, one, two, orb, indextrans):
        """Tranform the AO integrals into the MO basis using the
        :py:meth:`orbital_utils.split_core_active` or
        :py:meth:`orbital_utils.transform_integrals`` functions.

        **Arguments:**

        one
            (DenseOneIndex) the sum of all one electron integrals

        two
            (DenseTwoIndex, CholeskyIndex) the ERI

        orb
            (DenseOrbital) the orbitals used in the transformation

        indextrans
            (str) the flavor of the 4-index transformation
        """
        nc = self.occ_model.ncore[0]
        na = self.occ_model.nact[0]

        if nc > 0:
            cas = split_core_active(
                one,
                two,
                orb,
                e_core=self.e_core,
                ncore=nc,
                nactive=na,
                indextrans=indextrans,
            )
            self.e_core = cas.e_core
            return cas.one, cas.two
        ti = transform_integrals(one, two, orb, indextrans=indextrans)
        return ti.one[0], ti.two[0]

    def fix_core_energy(self, one, two, orb, indextrans):
        """Re-calculate core energy for a frozen core.
        See :py:meth:`orbital_utils.split_core_active` function.

        **Arguments:**

        one
            (DenseOneIndex) the sum of all one electron integrals

        two
            (DenseTwoIndex, CholeskyIndex) the ERI

        orb
            (DenseOrbital) the orbitals used in the transformation

        indextrans
            (str) the flavor of the 4-index transformation
        """
        nc = self.occ_model.ncore[0]
        na = self.occ_model.nact[0]

        if nc > 0:
            cas = split_core_active(
                one,
                two,
                orb,
                e_core=self.e_core,
                ncore=nc,
                nactive=na,
                indextrans=indextrans,
            )
            self.e_core = cas.e_core
            return

        raise NotImplementedError

    def load_orbitals(self, one, two, olp, orb, data, **kwargs):
        """Overwrite orbitals `orb` with those stored in the data container.
        Fix everything else (core energy, frozen core).

        **Arguments:**

        one
            (DenseOneIndex) the sum of all one electron integrals

        two
            (DenseTwoIndex, CholeskyIndex) the ERI

        orb
            (DenseOrbital) the current orbitals to be updated

        olp
            (DenseTwoIndex) the current overlap integrals (not updated)

        data
            (IOData) container containing the new orbitals

        indextrans
            (str) the flavor of the 4-index transformation
        """
        n_c = self.occ_model.ncore[0]
        indextrans = kwargs.get("indextrans", None)
        # First check if orbitals and overlap integrals are provided.
        if isinstance(olp, TwoIndex) and isinstance(orb, Orbital):
            # Print some information
            log("\nReading orbitals and overlap integrals from file.")
            if olp == data.olp:
                # if orbitals are the same, also load core energy
                if hasattr(data, "e_core"):
                    log("\nOverwriting core energy from restart file.\n")
                    self.e_core = unmask("e_core", data, **kwargs)
                # No need for projection
                return data.orb_a, olp
            log("\nProjecting new orbitals on current solution.\n")
            # We need to keep the current frozen core orbitals.
            # Thus, neglect all new frozen core orbitals when doing the projection
            # (the function below works with and without a frozen core)
            project_orbitals_frozen_core(data.olp, olp, data.orb_a, orb, n_c)
            # If olp differ (different geometries!), we have to fix the core energy.
            # This involves an AO/MO transformation step.
            # This is expensive but currently the quickest fix
            log("Recalculating core energy.\n")
            self.fix_core_energy(one, two, orb, indextrans)
        else:
            # Check if current geometry and restart geometry agree
            if hasattr(data, "occ_model"):
                self.check_coordinates(data.occ_model)
            else:
                # Print some warning and continue. Let's hope that everything
                # will be fine!
                log.warn(
                    "No initial orbitals and/or overlap integrals found!",
                    " We will take the ones found in the restart file.",
                    " If you restart from a different geometry, this is",
                    " not correct. Please, provide initial orbitals and",
                    " overlap integrals for the current geometry!",
                )
            olp = data.olp
            orb = data.orb_a
            self.e_core = unmask("e_core", data, **kwargs)
        return orb, olp

    def check_coordinates(self, occ_model):
        """Check if coordinates taken from occ_model agree with current ones.
        If occ_model.factory is a Basis instance and contains coordinates,
        we compare them to self.occ_model.factory.coordinates. They have to be
        the same.

        Args:
            occ_model (OccModel): Should contain factory.coordinates
        """
        # Check if we are dealing with molecules otherwise we do not care
        if isinstance(self.occ_model.factory, Basis):
            # This should never fail as coordinates in basis cannot be deleted
            if not hasattr(self.occ_model.factory, "coordinates"):
                raise ConsistencyError(
                    "Expected coordinates in Basis instance are missing!"
                )
            current_coordinates = np.array(self.occ_model.factory.coordinates)
            restart_coordinates = np.array(occ_model.factory.coordinates)
            if not (
                abs(current_coordinates - restart_coordinates) < 1e-12
            ).all():
                raise RestartError(
                    "Coordinates do not agree! Most likely, your IOData container "
                    "or your restart file are corrupted. For different geometries, "
                    "we need to perform a projection. Please provide current "
                    "overlap integrals and initial orbitals!"
                )
