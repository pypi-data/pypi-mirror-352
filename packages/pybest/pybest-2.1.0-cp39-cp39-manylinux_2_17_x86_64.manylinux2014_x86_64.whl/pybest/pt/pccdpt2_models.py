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
"""Perturbation theory module

Variables used in this module:
 :ncore:      number of frozne core orbitals
 :nocc:       number of occupied orbitals in the principle configuration
 :nacto:      number of active occupied orbitals in the principle configuration
 :nvirt:      number of virtual orbitals in the principle configuration
 :nactv:      number of active virtual orbitals in the principle configuration
 :nbasis:     total number of basis functions
 :nact:       total number of active orbitals (nacto+nactv)
 :energy:     the energy correction, list that can contain different
              contributions
 :amplitudes: the optimized amplitudes, list that can contain different
              contributions
 :singles:    the singles amplitudes, bool used to determine whether singles
              are to be included or not

 Indexing convention:
  :i,j,k,..: occupied orbitals of principle configuration
  :a,b,c,..: virtual orbitals of principle configuration
  :p,q,r,..: general indices (occupied, virtual)
"""

import numpy as np
from scipy import linalg
from scipy import optimize as opt

from pybest.exceptions import (
    ConsistencyError,
    EmptyData,
    NoConvergence,
    UnknownOption,
)
from pybest.linalg import Orbital
from pybest.log import log, timer
from pybest.pt.pccdpt2_base import pCCDPT2
from pybest.pt.perturbation_utils import get_pt2_amplitudes
from pybest.utility import check_options, check_type


class pCCDPT2D(pCCDPT2):
    """Base class for a diagonal one-body zero-order Hamiltonian"""

    long_name = "2nd-order Pertrubation Theory with diagonal H0"
    acronym = "pCCD-PT2"
    reference = "pCCD"
    overlap = ""

    @timer.with_section("PT2D: T")
    def calculate_amplitudes(self, *args, **kwargs):
        """Calculate amplitudes (singles and doubles)

        **Returns:**
             List of double and single amplitudes sorted as [D,S]
        """
        #
        # By default, calculate singles
        #
        self.singles = True
        #
        # Get "excitation" matrices w.r.t. |pCCD> (psi0): <jbkc|VN|pCCD>
        #
        matrix = self.vfunction_psi0(*args, **kwargs)

        fock = self.get_aux_matrix("fock")
        #
        # Get diagonal part of Fock matrix
        #
        fdiago = fock.copy_diagonal(end=self.nacto)
        fdiagv = fock.copy_diagonal(begin=self.nacto)

        ts, td = get_pt2_amplitudes(
            self.denself,
            [matrix[1], matrix[0]],
            [fdiago, fdiagv],
            singles=True,
        )
        return [td, ts]

    def calculate_singles(self, amplitudes, *args, **kwargs):
        """Calculate energy contribution of singles"""
        raise NotImplementedError

    def calculate_ex_matrix(self, *args, **kwargs):
        """Calculate "excitation" matrices w.r.t. |HF> (0)"""
        raise NotImplementedError

    def calculate_energy(self, amplitudes, *args, **kwargs):
        """Calculate PT energy and energy contribution of seniority sectors.
        Depends on PT model used.

        **Arguments:**

        amplitudes
             PT amplitudes. A FourIndex instance

        args
             List containing the geminal coefficients, 1- and 2-el
             integrals, and auxiliary matrices
        """
        #
        # Get "excitation" matrices w.r.t. |HF> (0)
        #
        exjbkc0 = self.calculate_ex_matrix(*args, **kwargs)
        #
        # Single excitations:
        #
        e_singles = self.calculate_singles(amplitudes, *exjbkc0, **kwargs)
        #
        # Seniority-0 sector
        #
        e_seniority_0 = amplitudes[0].contract("abab,abab", exjbkc0[0])
        #
        # Seniority-2 sector
        #
        e_seniority_2 = amplitudes[0].contract("abad,abad", exjbkc0[0])
        e_seniority_2 += amplitudes[0].contract("abdb,abdb", exjbkc0[0])
        energy = amplitudes[0].contract("abcd,abcd", exjbkc0[0]) * 2.0
        energy -= amplitudes[0].contract("abcd,adcb", exjbkc0[0])
        #
        # Seniority-4 sector
        #
        e_seniority_4 = energy - e_seniority_2 - e_seniority_0
        #
        # Update for checkpointing
        #
        energy_dict = {}
        energy_dict.update({"e_corr_d": energy})
        energy_dict.update({"e_corr_s": e_singles})
        energy_dict.update({"e_corr_s0": e_seniority_0})
        energy_dict.update({"e_corr_s2": e_seniority_2})
        energy_dict.update({"e_corr_s4": e_seniority_4})
        e_corr = energy + e_singles
        e_tot = e_corr + self.e_ref
        energy_dict.update({"e_ref": self.e_ref})
        energy_dict.update({"e_tot": e_tot})
        energy_dict.update({"e_corr": e_corr})
        #
        # Force update singles
        #
        return energy_dict


class PT2SDd(pCCDPT2D):
    """Diagonal one-body zero-order Hamiltonian with single determinant as dual"""

    reference = "pCCD"
    acronym = "PT2SDd"
    overlap = False
    include_fock = True

    def calculate_singles(self, amplitudes, *args, **kwargs):
        """Calculate energy contribution of singles

        **Arguments:**

        amplitudes
             PT amplitudes. Containing a list of [doubles, singles] amplitudes.

        args
            Not required for this PT flavour.
        """
        fock = self.get_aux_matrix("fock")
        ov = self.get_range("ov", 2)
        #
        # Single excitations:
        #
        e_singles = 2.0 * amplitudes[1].contract("ab,ab", fock, **ov)
        return e_singles

    def calculate_ex_matrix(self, *args, **kwargs):
        """Calculate "excitation" matrices w.r.t. |HF> (0)

        **Arguments:**

        args
             List containing the geminal coefficients, 1- and 2-el
             integrals, and auxiliary matrices. Not required for this PT
             flavour.
        """
        return [self.vfunction_0()]

    def compute_modified_fock(self, oldfock, **kwargs):
        """Modify Fock operator due to splitting the Hamiltonian in H0 and
        perturbation part. Set diagonal of Fock matrix to 0.
        """
        newfock = oldfock.copy()
        newfock.assign_diagonal(0.0)
        return newfock


class PT2MDd(pCCDPT2D):
    """Diagonal one-body zero-order Hamiltonian with pCCD determinant as dual"""

    reference = "pCCD"
    acronym = "PT2MDd"
    overlap = True
    include_fock = True

    def calculate_singles(self, amplitudes, *args, **kwargs):
        """Calculate energy contribution of singles

        **Arguments:**

        amplitudes
             PT amplitudes. Containing a list of [doubles, singles] amplitudes.

        args
             List containing some excitation matrices used to calculate the singles
             energy correction. The order is [doubles, singles].
        """
        #
        # Single excitations:
        #
        e_singles = 2.0 * amplitudes[1].contract("ab,ab", args[1])
        return e_singles

    def calculate_ex_matrix(self, *args, **kwargs):
        """Calculate "excitation" matrices w.r.t. |pCCD> (0)

        **Arguments:**

        args
             List containing the geminal coefficients, 1- and 2-el
             integrals, and auxiliary matrices
        """
        #
        # Get "excitation" matrices w.r.t. |psi_0> (0)
        #
        return self.vfunction_psi0(*args, **kwargs)

    def compute_modified_fock(self, oldfock, **kwargs):
        """Modify Fock operator due to splitting the Hamiltonian in H0 and
        perturbation part. Scale diagonal of Fock matrix using wfn overlap
        """
        newfock = oldfock.copy()
        olp = self.checkpoint["overlap"]
        # copy diagonal of old fock and scale
        diagfock = oldfock.copy_diagonal()
        scale = 1 - 1 / olp
        diagfock.iscale(scale)
        # assign new diagonal
        newfock.assign_diagonal(diagfock)
        return newfock

    def check_input(self, **kwargs):
        """Check input parameters."""
        for name in kwargs:
            check_options(
                name, name, "e_ref", "threshold", "indextrans", "overlap"
            )


class pCCDPT2O(pCCDPT2):
    """Base class for an off-diagonal one-body zero-order Hamiltonian"""

    long_name = "2nd-order Pertrubation Theory with off-diagonal H0"
    acronym = "pCCD-PT2"
    reference = "pCCD"
    overlap = ""

    def calculate_singles(self, amplitudes, *args, **kwargs):
        """Calculate energy contribution of singles"""
        raise NotImplementedError

    def calculate_ex_matrix(self, *args, **kwargs):
        """Calculate "excitation" matrices w.r.t. |HF> (0)"""
        raise NotImplementedError

    def callback(self, x, f):
        """Prints progress of convergence and dumps current solution"""
        #
        # Convergence progress
        #
        norm2 = linalg.norm(f)
        normmax = linalg.norm(f, ord=np.inf)
        if log.do_medium:
            log(f"{norm2:< 18.12f} {normmax:< 18.12f}")
        #
        # Dump current solution
        #
        begin = 0
        if self.singles:
            begin = self.nacto * self.nactv
            self.checkpoint.update("t_1", x[:begin])
            self.checkpoint.update("t_2", x[begin:])
        else:
            self.checkpoint.update("t_2", x[begin:])
        checkpoint_fn = self.get_checkpoint_fn()
        self.checkpoint.to_file(checkpoint_fn)

    @timer.with_section("PT2O: T Solver")
    def calculate_amplitudes(self, *args, **kwargs):
        """Solve for amplitudes

        **Arguments:**

        args
             Contains geminal coefficients, 1- and 2-el integrals, and
             auxiliary matrices

        **Keywords:**
             :threshold: threshold when checking symmetry of amplitudes
             :guess: initial guess
             :maxiter: maximum number of iterations
             :singles: include single excitations in projection manifold
             :excludepairs: exclude pair excitations from ampitude equations
                            (only supported for PT2b)

        For more details, see :py:meth:`Pertubation.__call__`
        """
        if log.do_medium:
            log(f"{'residual 2-norm':<18s} {'residual max norm':<18s}")

        #
        # Check argument type prior optimization:
        #
        check_type("args[0]", args[0], Orbital)
        #
        # Keyword arguments
        #
        thresh = kwargs.get("threshold", 1e-7)
        maxiter = kwargs.get("maxiter", 200)
        initguess = kwargs.get("guess", None)
        singles = kwargs.get("singles", False)
        excludepairs = self.exclude_pairs(**kwargs)

        #
        # Update PT parameters
        #
        self.singles = singles
        #
        #
        # Append overlap to function arguments:
        #
        args += ((self.checkpoint["t_p"]),)
        # FIXME: improve handling of overlap args
        olp = 0.0 if not self.overlap else self.checkpoint["overlap"]
        args += ((olp),)
        args += ((excludepairs),)
        check_type("args[2]", args[2], float)
        check_type("args[4]", args[3], bool)

        #
        # Get initial guess:
        #
        if initguess is not None:
            guess = initguess
            guess = self.fix_guess(initguess, singles, excludepairs)
        else:
            guess = self.get_guess(excludepairs)

        #
        # Solve matrix equation using scipy.optimize.root routine:
        #
        amplitudes = opt.root(
            self.vfunction,
            guess,
            args=(args),
            method="krylov",
            callback=self.callback,
            options={"fatol": thresh, "maxiter": maxiter},
        )
        if not amplitudes.success:
            raise NoConvergence(
                f"ERROR: program terminated. Error in solving \
                              amplitude equations: {amplitudes.message}"
            )
        if log.do_medium:
            log(
                f"Optimization of cluster amplitudes converged in {amplitudes.nit} "
                f"iterations."
            )
            log.hline("~")
            log("Calculating energy correction:")

        #
        # Store amplitudes
        #
        t = self.amplitudes2index(amplitudes.x)

        return t

    def amplitudes2index(self, t):
        """Transforms the np.array into dense objects"""
        end = self.nacto * self.nactv * (self.nacto * self.nactv + 1) // 2
        td = self.denself.create_four_index(
            self.nacto, self.nactv, self.nacto, self.nactv
        )
        # assign triu block
        td.assign_triu(t[:end])
        # add missing block
        tp_ = td.contract("abab->ab", clear=True)
        td.iadd_transpose((2, 3, 0, 1))
        ind1, ind2 = np.indices((self.nacto, self.nactv))
        indp = [ind1, ind2, ind1, ind2]
        # assign diagonal
        td.assign(tp_, indp)
        if self.singles:
            ts = self.denself.create_two_index(self.nacto, self.nactv)
            ts.assign(t[end:])
            return [td, ts]
        return [td]

    @timer.with_section("PT2O: VecFct")
    def vfunction(self, amplitudes, *args):
        """Vector function used to solve the amplitude equations of a given
        PT model.

        **Arguments:**

        amplitudes
             PT amplitudes. Need to be determined.

        args
             All function arguments needed to calculated the vector
             function:

             * [0]:  wfn expansion coefficients
             * [1]:  geminal coefficients
             * [2]:  overlap (float)
             * [3]:  singles (bool)
             * [4]:  pairs (bool)
        """
        ov = self.get_range("ov")
        vv2 = self.get_range("vv", 2)
        oo2 = self.get_range("oo", 2)
        oo4 = self.get_range("oo", 4)
        ov4 = self.get_range("ov", 4)
        vv4 = self.get_range("vv", 4)
        excludepairs = args[3]
        fock = self.get_aux_matrix("fock")
        #
        # output
        #
        matrix = self.vfunction_psi0(
            *args, **{"overlap": args[2], "excludepairs": excludepairs}
        )
        out = matrix[0]
        outs = matrix[1]
        #
        # Scale due to P_ijab operation
        #
        out.iscale(0.5)
        #
        # PT amplitudes
        #
        end = self.nacto * self.nactv * (self.nacto * self.nactv + 1) // 2
        ptamplitudes = self.denself.create_four_index(
            self.nacto, self.nactv, self.nacto, self.nactv
        )
        #
        # Expand triangular blocks
        #
        ptamplitudes.assign_triu(amplitudes[:end])
        tp_ = ptamplitudes.contract("abab->ab", clear=True)
        ptamplitudes.iadd_transpose((2, 3, 0, 1))
        ind1, ind2 = np.indices((self.nacto, self.nactv))
        indp = [ind1, ind2, ind1, ind2]
        # assign diagonal
        ptamplitudes.assign(tp_, indp)
        if self.singles:
            samplitudes = self.lf.create_two_index(self.nacto, self.nactv)
            samplitudes.assign(amplitudes[end:])

        # Singles only
        if self.singles:
            #
            #
            #
            samplitudes.contract("ab,bc->ac", fock, outs, **vv2)
            #
            #
            #
            samplitudes.contract("ab,ac->cb", fock, outs, factor=-1.0, **oo2)

        # coupling singles-doubles
        if self.singles:
            #
            #
            #
            ptamplitudes.contract("abcd,ab->cd", fock, outs, **ov4)
            # P_jb,kc
            ptamplitudes.contract("abcd,cd->ab", fock, outs, **ov4)
            #
            #
            #
            ptamplitudes.contract(
                "abcd,cb->ad", fock, outs, factor=-0.5, **ov4
            )
            # P_jb,kc
            ptamplitudes.contract(
                "abcd,ad->cb", fock, outs, factor=-0.5, **ov4
            )

        # coupling doubles-singles
        if self.singles:
            #
            #
            #
            fock.contract("ab,cd->abcd", samplitudes, out, **ov)

        # Doubles only
        # sum_aifo A^jbkc_iaof
        #
        # sum_c F_ac t_icjb
        #
        ptamplitudes.contract("abcd,eb->aecd", fock, out, factor=0.5, **vv4)
        #
        # sum_c F_ac t_jbic
        #
        ptamplitudes.contract("abcd,ed->ceab", fock, out, factor=0.5, **vv4)
        #
        # sum_l F_lj t_lbia
        #
        ptamplitudes.contract("abcd,ae->cdeb", fock, out, factor=-0.5, **oo4)
        #
        # sum_l F_lj t_ialb
        #
        ptamplitudes.contract("abcd,ce->edab", fock, out, factor=-0.5, **oo4)

        #
        # P_ijab
        #
        out.iadd_transpose((2, 3, 0, 1))
        # Get rid of pair amplitudes:
        if excludepairs:
            ind1, ind2 = np.indices((self.nacto, self.nactv))
            indices = [ind1, ind2, ind1, ind2]
            out.assign(0.0, indices)

        if self.singles:
            return np.hstack(
                (out.get_triu().ravel(order="C"), outs._array.ravel(order="C"))
            )
        return out.get_triu().ravel(order="C")

    def get_guess(self, excludepairs):
        """Generate initial guess for amplitudes. By default, an MP2 guess
        is calculated.
        """
        #
        # Get auxmatrices
        #
        iajb = self.get_aux_matrix("govov")
        liajb = iajb.copy()
        liajb.iadd_transpose((0, 3, 2, 1), factor=-1.0)
        liajb.iadd(iajb)
        fock = self.get_aux_matrix("fock")
        #
        # Get diagonal part of Fock matrix
        #
        fdiago = fock.copy_diagonal(end=self.nacto)
        fdiagv = fock.copy_diagonal(begin=self.nacto)

        ts, td = get_pt2_amplitudes(
            self.denself,
            [fock, liajb],
            [fdiago, fdiagv],
            singles=True,
            lagrange=False,
        )
        if excludepairs:
            ind1, ind2 = np.indices((self.nacto, self.nactv))
            indp = [ind1, ind2, ind1, ind2]
            td.assign(0.0, indp)
        # get only upper triangular block
        if self.singles:
            return np.hstack(
                (td.get_triu().ravel(order="C"), ts.ravel()._array)
            )
        return td.get_triu().ravel(order="C")

    def fix_guess(self, guess, singles, excludepairs):
        """Generate initial guess for amplitudes"""
        if singles:
            endd = self.nacto * self.nactv * (self.nacto * self.nactv + 1) // 2
            ends = self.nacto * self.nactv
            end = endd + ends
            if guess.ndim != 1:
                raise UnknownOption(
                    "Guess has to be a 1-dimensional vector containing first doubles "
                    "amplitudes, then singles"
                )
        else:
            end = self.nacto * self.nactv * (self.nacto * self.nactv + 1) // 2
            if guess.ndim != 1:
                raise UnknownOption(
                    "Guess has to be a 1-dimensional vector containing doubles amplitudes"
                )
        if guess.shape[0] == end:
            return guess
        # assuming that guess is a dense four index object
        endd = self.nacto * self.nactv * self.nacto * self.nactv
        guessd = self.denself.create_four_index(
            self.nacto, self.nactv, self.nacto, self.nactv
        )
        #
        # Expand triangular blocks
        #
        guessd.assign(guess[:endd])
        guessd.iadd_transpose((2, 3, 0, 1))
        guessd.iscale(0.5)
        if excludepairs:
            ind1, ind2 = np.indices((self.nacto, self.nactv))
            indp = [ind1, ind2, ind1, ind2]
            guessd.assign(0.0, indp)
        # get only upper triangular block
        if self.singles:
            return np.hstack((guessd.get_triu(), guess[endd:]))
        return guessd.get_triu()

    def print_info(self, **kwargs):
        """Print information on keyword arguments and other properties of a
        given PT flavour.
        """
        thresh = kwargs.get("threshold", 1e-7)
        maxiter = kwargs.get("maxiter", 200)
        guess = kwargs.get("guess", None)
        singles = kwargs.get("singles", False)
        exclude = self.exclude_pairs(**kwargs)
        if log.do_medium:
            log(f"{self.acronym} perturbation module")
            log(" ")
            log("OPTIMIZATION PARAMETERS:")
            log("Reference Function              pCCD")
            log(f"Number of frozen core orbitals: {self.ncore}")
            log(f"Number of occupied orbitals:    {self.nacto}")
            log(f"Number of virtual orbitals:     {self.nactv}")
            if self.overlap:
                log(
                    f"Approximate overlap:            {self.checkpoint['overlap']}"
                )
            if singles:
                log("Projection manifold             T1 + T2")
            else:
                log("Projection manifold             T2")
            if exclude:
                log("  Electron pairs                excluded")
            else:
                log("  Electron pairs                included")
            if guess is None:
                log("Initial guess:                  MP2")
            else:
                log("Initial guess:                  user-defined")
            log("Solvers:")
            log(f"  {self.acronym + 'amplitudes:':<26s}    krylov")
            log("Optimization thresholds:")
            log(f"  {self.acronym + 'amplitudes:':<26s}    {thresh:.2e}")
            log(f"  maxiter:                      {maxiter}")
            log.hline()

    def check_input(self, **kwargs):
        """Check input parameters."""
        for name in kwargs:
            check_options(
                name,
                name,
                "e_ref",
                "threshold",
                "maxiter",
                "singles",
                "guess",
                "indextrans",
                "excludepairs",
                "overlap",
            )
        guess = kwargs.get("guess", None)
        if guess is not None:
            check_type("guess", guess, np.ndarray)
            if (
                not len(guess)
                == self.nacto * self.nacto * self.nactv * self.nactv
            ):
                raise ConsistencyError(
                    "Length of guess array does not agree with number of unknowns"
                )

    def calculate_energy(self, amplitudes, *args, **kwargs):
        """Calculate PT energy and energy contribution of seniority sectors

        **Arguments:**

        amplitudes
             PT amplitudes. A FourIndex instance

        args
             List containing the geminal coefficients, 1- and 2-el
             integrals, and auxiliary matrices
        """
        #
        # Get "excitation" matrices w.r.t. |HF> (0)
        #
        exjbkc0 = self.calculate_ex_matrix(*args, **kwargs)
        #
        # Single excitations:
        #
        e_singles = self.calculate_singles(amplitudes, *exjbkc0, **kwargs)
        #
        # Seniority-0 sector
        #
        e_seniority_0 = amplitudes[0].contract("abab,abab", exjbkc0[0])
        #
        # Seniority-2 sector
        #
        e_seniority_2 = amplitudes[0].contract("abad,abad", exjbkc0[0])
        e_seniority_2 += amplitudes[0].contract("abdb,abdb", exjbkc0[0])
        energy = amplitudes[0].contract("abcd,abcd", exjbkc0[0]) * 2.0
        energy -= amplitudes[0].contract("abcd,adcb", exjbkc0[0])
        #
        # Seniority-4 sector
        #
        e_seniority_4 = energy - e_seniority_2 - e_seniority_0
        #
        # Update for checkpointing
        #
        energy_dict = {}
        energy_dict.update({"e_corr_d": energy})
        energy_dict.update({"e_corr_s": e_singles})
        energy_dict.update({"e_corr_s0": e_seniority_0})
        energy_dict.update({"e_corr_s2": e_seniority_2})
        energy_dict.update({"e_corr_s4": e_seniority_4})
        e_corr = energy + e_singles
        e_tot = e_corr + self.e_ref
        energy_dict.update({"e_ref": self.e_ref})
        energy_dict.update({"e_tot": e_tot})
        energy_dict.update({"e_corr": e_corr})

        return energy_dict

    def exclude_pairs(self, **kwargs):
        """Exclude electron pairs from projection manifold"""
        return True


class PT2SDo(pCCDPT2O):
    """Off-diagonal one-body zero-order Hamiltonian with single determinant as dual."""

    reference = "pCCD"
    acronym = "PT2SDo"
    overlap = False
    include_fock = False

    def calculate_singles(self, amplitudes, *args, **kwargs):
        """Calculate energy contribution of singles"""
        return 0.0

    def calculate_ex_matrix(self, *args, **kwargs):
        """Calculate "excitation" matrices w.r.t. |HF> (0)

        **Arguments:**

        args
             List containing the geminal coefficients, 1- and 2-el
             integrals, and auxiliary matrices
        """
        return [self.vfunction_0()]


class PT2MDo(pCCDPT2O):
    """Off-diagonal one-body zero-order Hamiltonian with pCCD determinant as
    dual.
    """

    reference = "pCCD"
    acronym = "PT2MDo"
    overlap = True
    include_fock = True

    def calculate_singles(self, amplitudes, *args, **kwargs):
        """Calculate energy contribution of singles

        **Arguments:**

        amplitudes
             PT amplitudes. A FourIndex instance

        args
             List containing the geminal coefficients, 1- and 2-el
             integrals, and auxiliary matrices
        """
        #
        # Single excitations:
        #
        if self.singles:
            e_singles = 2.0 * amplitudes[1].contract("ab,ab", args[1])
            return e_singles
        return 0.0

    def calculate_ex_matrix(self, *args, **kwargs):
        """Calculate "excitation" matrices w.r.t. |pCCD> (0)

        **Arguments:**

        args
             List containing the geminal coefficients, 1- and 2-el
             integrals, and auxiliary matrices
        """
        #
        # Get "excitation" matrices w.r.t. |psi_0> (0)
        #
        return self.vfunction_psi0(*args, **kwargs)

    def compute_modified_fock(self, oldfock, **kwargs):
        """Modify Fock operator due to splitting the Hamiltonian in H0 and
        perturbation part. Scale full Fock matrix using wfn overlap
        """
        newfock = oldfock.copy()
        olp = self.checkpoint["overlap"]
        scale = 1 - 1 / olp
        newfock.iscale(scale)
        return newfock

    def check_input(self, **kwargs):
        """Check input parameters."""
        # check for overlap; only required for PT2MDo class
        try:
            self.checkpoint["overlap"]
        except KeyError:
            raise EmptyData(
                "Warning: Cannot find wavefunction overlap!"
            ) from None
        # call partent class:
        pCCDPT2O.check_input(self, **kwargs)


class PT2b(pCCDPT2O):
    """PT2b perturbation theory model with a pCCD reference function"""

    reference = "pCCD"
    acronym = "PT2b"
    overlap = False
    include_fock = True

    def calculate_singles(self, amplitudes, *args, **kwargs):
        """Calculate energy contribution of singles

        **Arguments:**

        amplitudes
             PT amplitudes. A FourIndex instance

        args
             List containing some excitation matrices in the order
             [doubles, singles]
        """
        #
        # Single excitations:
        #
        if self.singles:
            e_singles = 2.0 * amplitudes[1].contract("ab,ab", args[1])
            return e_singles
        return 0.0

    def calculate_ex_matrix(self, *args, **kwargs):
        """Calculate "excitation" matrices w.r.t. |pCCD> (0)

        **Arguments:**

        args
             List containing the geminal coefficients, 1- and 2-el
             integrals, and auxiliary matrices
        """
        #
        # Get "excitation" matrices w.r.t. |psi_0> (0)
        #
        return self.vfunction_psi0(*args, **kwargs)

    def compute_modified_fock(self, oldfock, **kwargs):
        """Modify Fock operator due to splitting the Hamiltonian in H0 and
        perturbation part. Here, it remains unchanged.
        """
        return oldfock

    def exclude_pairs(self, **kwargs):
        """Exclude electron pairs from projection manifold (default: False)"""
        exclude = kwargs.get("excludepairs", False)
        return exclude
