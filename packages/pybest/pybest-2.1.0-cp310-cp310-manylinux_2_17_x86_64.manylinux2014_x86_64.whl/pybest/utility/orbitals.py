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
# This file has been originally written and updated by Katharina Boguslawski (see CHANGELOG)
# Its current version contains updates from the PyBEST developer team.
#
# Part of this implementation can also be found in `Horton 2.0.0`.
# However, this file has been updated and debugged. Compatibility with Horton is NOT
# guaranteed.
#
# Detailed changes (see also CHANGELOG):
# 2020-07-01: update to new python features, including f-strings
# 2020-07-01: use PyBEST standards, including naming convention, exception class, unmask
#             functions, Hamiltonian labels
# 2020-07-01: new functions: print_ao_mo_coeffs

"""Utility functions for orbital modifications"""

import numpy as np

from pybest.exceptions import ArgumentError
from pybest.featuredlists import OneBodyHamiltonian
from pybest.gbasis import Basis, compute_overlap
from pybest.iodata import IOData
from pybest.linalg import FourIndex, Orbital, TwoIndex
from pybest.log import log, timer

from .check_data import check_options, check_type
from .unmask_data import unmask, unmask_orb

__all__ = [
    "compute_unitary_matrix",
    "print_ao_mo_coeffs",
    "project_orbitals",
    "project_orbitals_frozen_core",
    "rotate_orbitals",
    "split_core_active",
    "transform_integrals",
]


def rotate_orbitals(*args):
    """Rotate AO/MO (or MO/MO) coefficient matrix such that C` = C*U

    **Arguments:**

    args
         Rotation matrices (TwoIndex instance) and AO/MO coefficients
         (Orbital instance). rots and exps are ordered such that rot1
         corresponds to exp1, etc., i.e., rot1, rot2,..., exp1, exp2,...
    """
    orbs = []
    rotmat = []
    for arg in args:
        if isinstance(arg, TwoIndex):
            rotmat.append(arg)
        elif isinstance(arg, Orbital):
            orbs.append(arg)
        else:
            raise ArgumentError(f"Argument of unsupported type: {arg}")
    for i, orb in enumerate(orbs):
        orb.assign_dot(orb, rotmat[i])


def compute_unitary_matrix(kappa):
    """Determine a unitary matrix from a skew-symmetric matrix K as
    U = exp(-K) by approximating U = 1 - K + 1/2 K^2 + O(3)

    **Arguments:**

    kappa
         A skew-symmetric matrix (TwoIndex instance)
    """
    out = kappa.new()
    out.assign_diagonal(1.0)

    #
    # Approximate unitary matrix
    # U = exp(-K) by U = 1 - K + 1/2 K^2 + O(3)
    #
    out.iadd(kappa, -1.0)
    out.iadd_dot(kappa, kappa, 0.5)
    #
    # orthogonalization because approximate U matrix might not be unitary/orthogonal:
    #
    out.iortho()
    return out


@timer.with_section("Index Trans")
def transform_integrals(*args, **kwargs):
    """Update MO integrals. Returns list of transformed 1- and 2-electron
    integrals according to a list of expansion coefficients.

    **Arguments:**

    args
        All one-electron integrals in the AO basis. A TwoIndex instance.
        The two-electron integrals in the AO basis.
        The orbitals used in the transformation.

    **Keyword arguments:**

    indextrans
        4-index Transformation (str). Choice between ``tensordot`` (default),
        ``cupy``, ``einsum``, ``cpp``, ``opt_einsum``, or ``einsum_naive``
        If ``cupy`` is not available, we switch to ``tensordot``.

    """
    # When we call the function, we allow indextrans=None if not specified
    # otherwise
    indextrans = kwargs.get("indextrans", None)
    indextrans = "tensordot" if indextrans is None else indextrans
    check_options(
        "indextrans",
        indextrans,
        "tensordot",
        "einsum",
        "opt_einsum",
        "einsum_naive",
        "cupy",
    )
    for arg in args:
        check_type("args", arg, IOData, TwoIndex, FourIndex, Orbital)
    #
    # Unmask arguments
    #
    # orb
    orb = unmask_orb(*args)
    if not orb:
        raise ArgumentError("Orbitals are required for the transformation!")
    # 1-e ints and 2-e ints
    one = None
    for arg in args:
        if isinstance(arg, TwoIndex):
            if arg.label in OneBodyHamiltonian:
                if one is not None:
                    one.iadd(arg)
                else:
                    one = arg.copy()
                    one.label = "one"
        elif isinstance(arg, FourIndex):
            two = arg

    two_mo = []
    one_mo = []
    if not all(isinstance(orb_, Orbital) for orb_ in orb):
        raise ArgumentError("Orbital argument of unsupported type")

    #
    # Loop over all possible AO/MO coefficients. We distinguish between
    #   * restricted orbitals: only one expansion instance (alpha=beta), returns
    #                          one set of 1- and 2-body integrals
    #   * unrestricted orbitals: two expansion instances (alpha, beta), returns
    #                            two sets of 1-body, and three sets of 2-body
    #                            integrals (one_alpha,alpha and one_beta,beta)
    #                            and (<alpha alpha|alpha alpha>, )
    #                            (<alpha beta|alpha beta>, <beta beta|beta beta>)
    #                            Note that order of alpha and beta is determined
    #                            by the order of the expansion instances
    #
    for i, orb_1 in enumerate(orb):
        for j, orb_2 in enumerate(orb):
            if j < i:
                continue
            #
            # Transform 2-electron part
            # Note that integrals are stored using physics' convention <12|12>
            #
            out4ind = two.new()
            out4ind.label = two.label
            out4ind.assign_four_index_transform(
                two, orb_1, orb_2, orb_1, orb_2, indextrans, **kwargs
            )
            two_mo.append(out4ind)

        #
        # Transform 1-electron part
        #
        out2ind = one.copy()
        out2ind.assign_two_index_transform(one, orb_1)
        one_mo.append(out2ind)
    #
    # Assign to IOData container
    #
    output = IOData(one=one_mo, two=two_mo)
    #
    # Done
    #
    return output


def split_core_active(*args, **kwargs):
    """Reduce a Hamiltonian to an active space

    Works only for restricted wavefunctions.

    **Arguments:**

    args
         One and two-electron integrals.
         The core energy of the given Hamiltonian. In the case of a standard
         molecular system, this is the nuclear nuclear repulsion.
         The MO expansion coefficients. An Orbital instance. If None,
         integrals are assued to be already transformed into the mo basis
         and no transformation is carried out in this function.
         The core energy is passed either as a dictionary or
         IOData instance.

    **Keyword Arguments:**

    ncore
         The number of frozen core orbitals (int)

    nactive
         The number of active orbitals (int)

    indextrans
        4-index Transformation (str). Choice between ``tensordot`` (default),
        ``cupy``, ``einsum``, ``cpp``, ``opt_einsum``, or ``einsum_naive``

    **Returns** an instance of IOData with three values:

    one
         The one-body operator in the small space

    two
         The two-body operator in the small space

    e_core
         The core energy, i.e. the sum of the given core energy and HF
         contributions from the core orbitals.
    """
    #
    # Unmask arguments
    #
    # orb
    orb = unmask_orb(*args)
    if orb:
        orb = orb[0]
    # 1-e ints and 2-e ints
    one = None
    for arg in args:
        if isinstance(arg, TwoIndex):
            if arg.label in OneBodyHamiltonian:
                if one is not None:
                    one.iadd(arg)
                else:
                    one = arg.copy()
        elif isinstance(arg, FourIndex):
            two = arg
    #
    # external terms
    # search for core energy in the following order:
    # kwargs > iodata
    # only one core energy term is added
    e_core = unmask("e_core", *args, **kwargs)
    if e_core is None:
        raise ArgumentError("Cannot find core energy in arguments.")

    #
    # Set default keyword arguments:
    #
    ncore = kwargs.get("ncore", 0)
    nactive = kwargs.get("nactive", (one.nbasis - ncore))
    # When we call the function, we allow indextrans=None if not specified
    # otherwise
    indextrans = kwargs.get("indextrans", None)
    indextrans = "tensordot" if indextrans is None else indextrans
    #
    # Check type/option of arguments
    #
    check_type("ncore", ncore, int)
    check_type("nactive", nactive, int)
    check_options(
        "indextrans",
        indextrans,
        "tensordot",
        "einsum",
        "opt_einsum",
        "einsum_naive",
        "cupy",
    )
    if ncore < 0:
        raise ValueError(f"ncore must be >= 0. Got ncore = {ncore}")
    if nactive <= 0:
        raise ValueError(f"nactive must be > 0. Got nactive = {nactive}")
    if nactive + ncore > one.nbasis:
        raise ValueError("More active orbitals than basis functions.")

    #
    # Optional transformation to mo basis
    #
    if not orb:
        one_mo = one
        two_mo = two
    else:
        # No need to check orb. This is done in transform_integrals function
        ti = transform_integrals(one, two, orb, **kwargs)
        one_mo = ti.one[0]
        two_mo = ti.two[0]

    # Core energy
    norb = one.nbasis
    #   One body term
    e_core += 2 * one_mo.trace(0, ncore, 0, ncore)
    #   Direct part
    ranges = {"end0": ncore, "end1": ncore, "end2": ncore, "end3": ncore}
    e_core += two_mo.contract("abab->ab", out=None, factor=2.0, **ranges).sum()
    #   Exchange part
    e_core += two_mo.contract(
        "abba->ab", out=None, factor=-1.0, **ranges
    ).sum()

    # Get ranges
    ncn = {
        "begin0": 0,
        "end0": norb,
        "begin1": 0,
        "end1": ncore,
        "begin2": 0,
        "end2": norb,
    }
    nnc = {
        "begin0": 0,
        "end0": norb,
        "begin1": 0,
        "end1": norb,
        "begin2": 0,
        "end2": ncore,
    }

    # Active space one-body integrals
    one_mo_corr = one_mo.new()
    # Can be done directly with contract functions using td for speed up (for Cholesky)
    # Will default to tensordot operations if implemented
    # Direct part
    two_mo.contract("abcb->ac", one_mo_corr, factor=2.0, **ncn)
    # Exchange part
    two_mo.contract("abcc->ab", one_mo_corr, factor=-1.0, **nnc)
    one_mo.iadd(one_mo_corr, 1.0)

    #
    # Store in smaller n-index objects
    #
    one_mo_small = one_mo.copy(ncore, ncore + nactive, ncore, ncore + nactive)
    two_mo_small = two_mo.copy(
        ncore,
        ncore + nactive,
        ncore,
        ncore + nactive,
        ncore,
        ncore + nactive,
        ncore,
        ncore + nactive,
    )

    #
    # Assign to IOData container
    #
    output = IOData(one=one_mo_small, two=two_mo_small, e_core=e_core)
    #
    # Done
    #
    return output


def print_ao_mo_coeffs(basis, orb, begin=1, end=None):
    """Print AO/MO coefficients for a given orbital basis

    Works only for pure basis functions.

    **Arguments:**

    basis
         A Basis instance.

    orb
         The MO expansion coefficients. An Orbital instance.

    **Optional arguments:**

    begin, end
         First and last orbital index to be printed (using normal indexing).
         If end is None, the last orbital is taken to be the last element of
         orb.
    """

    def convert_to_fullao(basis):
        atom = np.array([], dtype=int)
        shell = np.array([])
        for a, s in zip(basis.shell2atom, basis.shell_types):
            ls = int(abs(s) * 2.0 + 1)
            for s_ in range(ls):
                atom = np.append(atom, int(a))
                key = shells[abs(s)]
                als = str(key) + str(lm[key][s_])
                shell = np.append(shell, als)
        return atom, shell

    log()
    log.hline("~")
    log("AO/MO coefficients:")
    log.hline("~")
    shells = ["s", "p", "d", "f", "g", "h", "i"]
    lm = {
        "s": [""],
        "p": ["+1", "-1", "0"],
        "d": ["-2", "-1", "0", "+1", "+2"],
        "f": ["-3", "-2", "-1", "0", "+1", "+2", "+3"],
        "g": ["-4", "-3", "-2", "-1", "0", "+1", "+2", "+3", "+4"],
        "h": ["-5", "-4", "-3", "-2", "-1", "0", "+1", "+2", "+3", "+4", "+5"],
        "i": [
            "-6",
            "-5",
            "-4",
            "-3",
            "-2",
            "-1",
            "0",
            "+1",
            "+2",
            "+3",
            "+4",
            "+5",
            "+6",
        ],
    }
    if end is None:
        end = orb.nfn

    # Check input:
    if begin < 1:
        raise ValueError(
            "First orbital index has to be equal or larger than 1."
        )
    if begin > orb.nfn:
        raise ValueError(
            "First orbital index exceeds number of basis functions."
        )
    if begin > end:
        raise ValueError("First and last orbital index have to differ.")
    if end > orb.nfn:
        raise ValueError(
            "Last orbital index exceeds number of basis functions."
        )

    # print orbitals in batches of 10
    totcol = int(end - begin) // 10 + 1
    beginc = begin - 1
    if (end - begin - 1) <= 10:
        endc = end
    else:
        endc = begin + 9

    # get atom indices and full basis information
    atoms, aos = convert_to_fullao(basis)
    # loop over all mos, print at most 10 columns at once
    for _ in range(totcol):
        log(f"\t {'Molecular orbital number':>26}")
        s = "      "
        for i in range(beginc, endc):
            s += f"  {(i + 1):>7}"
        log(s)
        for aoi in range(orb.nbasis):
            s2 = f"{(atoms[aoi] + 1):>3} {aos[aoi]:>3}"
            for moi in range(beginc, endc):
                s2 += f"  {orb.coeffs[aoi, moi]:> 7.3f}"
            log(s2)
        beginc = endc
        endc = endc + 10
        endc = min(endc, end)
        if beginc > end:
            break
        log.hline("-")
    log.hline("~")


def project_orbitals(olp0, olp1, orb0, orb1):
    r"""Take reference set of orbitals orb0 and project solution on new set of
    orbitals orb1. Final orbitals will be orthonormal wrt to the basis set of
    orb0.

    Parameters
    ----------
    olp0 : TwoIndex or Basis
           The overlap matrix (or alternatively the orbital basis) for the
           original orbitals
    olp1 : TwoIndex or Basis
           The overlap matrix (or alternatively the orbital basis) for the
           projected new set of orbitals
    orb0 : DenseOrbital
           The AO/MO coefficients of the original orbitals.
    orb1 : DenseOrbital
           An output argument in which the projected orbitals will be stored.

    Notes
    -----
    This projection just transforms the old orbitals to an orthogonal basis
    by a multiplication with the square root of the old overlap matrix. The
    orbitals in this basis are then again multiplied with the inverse square
    root of the new overlap matrix:

    .. math ::

        C_\text{new} = S_\text{new}^{-1/2} S_\text{old}^{1/2} C_\text{old}

    This guarantees that :math:`C_\text{new}^T S_\text{new} C_\text{new} = I`
    if :math:`C_\text{old}^T S_\text{old} C_\text{old} = I`. This approach is
    simple and robust but the current implementation has some limitations: it
    only works for projections between basis sets of the same size and it
    assumes that there is some similarity between the new and old
    orthogonalized atomic basis sets. The latter is only the case when the
    old and new atomic basis sets are very similar, e.g. for small geometric
    changes.
    """
    if olp0.nbasis != olp1.nbasis:
        raise ValueError("The two basis sets must have the same size")

    def helper_olp(olp):
        if isinstance(olp, Basis):
            basis = olp
            olp = compute_overlap(olp)
        elif isinstance(olp, TwoIndex):
            basis = None
        else:
            raise ArgumentError(
                "The olp arguments must be an instance of TwoIndex or Basis."
            )
        return olp, basis

    olp0, _ = helper_olp(olp0)
    olp1, _ = helper_olp(olp1)

    tmp = olp1.inverse()
    tmp.idot(olp0)
    tf = tmp.sqrt()

    # Transform the coefficients
    orb1.assign_dot(tf, orb0)

    # Clear the energies in exp1 as they can not be defined in a meaningful way
    orb1.energies[:] = 0.0
    # Just copy the occupation numbers and hope for the best
    orb1.occupations[:] = orb0.occupations


def project_orbitals_frozen_core(olp0, olp1, orb0, orb1, ncore=0):
    r"""Take reference set of orbitals orb0 and project solution on a new set of
    orbitals orb1. Final orbitals will be orthonormal wrt to the basis set of
    orb0. This function works with a set of frozen core orbitals, that is,
    the first `ncore` orbitals are NOT altered.

    Parameters
    ----------
    olp0 : TwoIndex or Basis
           The overlap matrix (or alternatively the orbital basis) for the
           original orbitals
    olp1 : TwoIndex or Basis
           The overlap matrix (or alternatively the orbital basis) for the
           projected new set of orbitals
    orb0 : DenseOrbital
           The AO/MO coefficients of the original orbitals.
    orb1 : DenseOrbital
           An output argument in which the projected orbitals will be stored.
    ncore: float
           An output argument in which the projected orbitals will be stored.

    Notes
    -----
    Compared to the `project_orbitals` function, the algorithm is slightly
    altered: After full projection, we move to orthonormal orbitals and over-
    write the frozen core with the original set (orb1) prior projection.
    Then, a Gram-Schmidt orthogonalization is performed to ensure that the
    partly projected orbitals are orthogonal to the unprojected ones.
    """
    orb1_ = orb1.copy()
    project_orbitals(olp0, olp1, orb0, orb1)

    if ncore == 0:
        return

    # Orthogonalize current orbitals (the ones with the correct frozen core)
    # as we will use the Gram-Schmidt procedure to fix the frozen core.
    olp1_12 = olp1.sqrt()
    orb1_.assign_dot(olp1_12, orb1_)
    orb1.assign_dot(olp1_12, orb1)
    # reset frozen core of already projected orbitals (overwrite those that
    # should not be overwritten)
    orb1.assign_coeffs(orb1_.coeffs[:, :ncore], end0=ncore)
    # GS orthogonalization (to make sure that the old (frozen) and new ones are
    # orthonormal)
    orb1.gram_schmidt()
    # Get rid of orthogonality
    olp1_12_inv = olp1_12.inverse()
    orb1.assign_dot(olp1_12_inv, orb1)

    # Check if everything is fine.
    orb1.check_normalization(olp1)
