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
"""Perturbation utility functions module

Variables used in this module:
 :nocc:       number of occupied orbitals in the principle configuration
 :nvirt:      number of virtual orbitals in the principle configuration
 :nbasis:     total number of basis functions
              contributions

 Indexing convention:
  :i,j,k,..: occupied orbitals of principle configuration
  :a,b,c,..: virtual orbitals of principle configuration
  :p,q,r,..: general indices (occupied, virtual)
"""

from pybest.exceptions import ConsistencyError, EmptyData
from pybest.linalg import FourIndex, OneIndex, TwoIndex
from pybest.log import timer
from pybest.utility import check_type


@timer.with_section("PT2: Amplitudes")
def get_pt2_amplitudes(lf, v, f, singles=False, lagrange=False, shift=None):
    """Calculates PT2 amplitudes according to the equation
        t_pq^rs = V_prqs/(F_p+F_q-F_r-F_s)
    or, if asked for, singles amplitudes according to
        t_p^r = v_pr/(F_p-F_r)

    **Arguments:**

    lf
        A LinalgFactory instance.

    v
        The perturbation matrix (a list). For T2 only, it is a four-index
        quantity. Indices have to be sorted as <(pr)(qs)> as in the amplitudes.
        If singles is True, v is a list that contains the perturbation matrix
        for the singles (v[0], a two-index object) and the perturbation
        matrix for the doubles (v[1], a four-index object). If lagrange is
        True, the last element of v is the matrix used to calculated the
        lagrange amplitudes.
        Currently, all v except for T1 have to have the proper dimensions.

    f
        Contains a list of one-index objects (e.g., orbital energies,
        diagonal Fock matrices, etc.). The order has to be [p,r,q,s] and they
        have to have the proper dimensions.

    **Optional Arguments:**

    singles
        If True, singles amplitudes are also calculated. They are only
        calculated for f[0] and f[1]. (default: False)

    lagrange
        If True, Lagrange amplitudes are also calculated. They are used to
        obtain the relaxed DM in, for instance, MP2. (default: False)

    shift
        A list of (orbital-dependent) shifts applied to the denominator.
        Either a float or a one-index object. Note that the shift overwrites
        the elements of f. (default: None)

    **Returns:**
        A list of PT2 (T2) amplitudes. T2 amplitudes are a four-index object
        and stored as T_{pq}^{rs}. If singles is True, it also returns the
        singles amplitudes. The order is [T_1, T_2, Lagrange_d]
    """
    #
    # Check types
    #
    if singles:
        check_type("v[0]", v[0], TwoIndex)
        check_type("v[1]", v[1], FourIndex)
        if lagrange:
            check_type("v[2]", v[2], FourIndex)
    elif lagrange:
        check_type("v[0]", v[0], FourIndex)
        check_type("v[1]", v[1], FourIndex)
    else:
        check_type("v[0]", v[0], FourIndex)
    if shift is not None:
        for el in shift:
            check_type("shift", el, float, OneIndex)
        if not len(f) == len(shift):
            raise EmptyData(
                "You have to provide for each explicitly given Fock matrix a shift."
            )
    for arg in f:
        check_type("arg", arg, OneIndex)
    #
    # Assign orbital energies/Fock matrix:
    #
    if len(f) == 4:
        fi = f[0]
        fa = f[1]
        fj = f[2]
        fb = f[3]
        #
        # Apply orbital-dependent shift:
        #
        if shift is not None:
            fi.iadd(shift[0])
            fa.iadd(shift[1])
            fj.iadd(shift[2])
            fb.iadd(shift[3])
    elif len(f) == 2:
        fi = f[0]
        fa = f[1]
        #
        # Apply orbital-dependent shift:
        #
        if shift is not None:
            fi.iadd(shift[0])
            fa.iadd(shift[1])
    else:
        raise ConsistencyError(
            "Do not know how to assign arguments to Fock matrix"
        )
    #
    # Get dimensions
    #
    if singles:
        nocc = v[1].nbasis
        nvirt = v[1].nbasis1
    else:
        nocc = v[0].nbasis
        nvirt = v[0].nbasis1
    #
    # Create PT amplitudes
    # By default singles are calculated because they are used to determine
    # doubles
    #
    ts_1 = lf.create_two_index(nocc, nvirt)
    if len(f) == 4:
        ts_2 = lf.create_two_index(nocc, nvirt)
    td = lf.create_four_index(nocc, nvirt, nocc, nvirt)
    td_ = lf.create_two_index(nocc * nvirt, nocc * nvirt)
    #
    # Step 1:
    # Calculate singles (Fi-Fa) and, if required, (Fj-Fb)
    #
    ts_1.iadd(fi, 1.0)
    ts_1.iadd(fa, -1.0, transpose=True)
    if len(f) == 4:
        ts_2.iadd(fj, 1.0)
        ts_2.iadd(fb, -1.0, transpose=True)
    #
    # Step 1:
    # Calculate Doubles from singles (Fi+Fj-Fa-Fb)
    #
    tsravel1 = ts_1.ravel()
    td_.iadd(tsravel1)
    if len(f) == 4:
        tsravel2 = ts_2.ravel()
        td_.iadd(tsravel2, transpose=True)
        del tsravel2
    else:
        td_.iadd(tsravel1, transpose=True)
        del tsravel1
    if singles:
        s1 = ts_1.new()
        s1.assign(1.0)
        # singles 1/ts
        ts = s1.divide(ts_1)
        del ts_1, s1
    d1 = td_.new()
    d1.assign(1.0)
    # doubles 1/td
    td_ = d1.divide(td_)
    td.assign(td_)
    del td_
    #
    # Lagrange part (used for relaxation of DM)
    #
    if lagrange:
        lag = td.copy()
    #
    # Calculate amplitudes
    #
    # Get ranges
    ov2 = {
        "begin2": 0,
        "end2": nocc,
        "begin3": nocc,
        "end3": (nocc + nvirt),
    }
    if singles:
        # Adjust v[0] if it does not have the proper shape of v[0]ia
        if v[0].shape == (nocc, nvirt):
            ts.imul(v[0], 1.0)
        else:
            ts.imul(v[0], 1.0, **ov2)
        td.imul(v[1])
        if lagrange:
            lag.imul(v[2])
            return [ts, td, lag]
        return [ts, td]
    td.imul(v[0])
    if lagrange:
        lag.imul(v[1])
        return [td, lag]
    return [td]


@timer.with_section("PT2: Epsilon")
def get_epsilon(lf, f, singles=False, shift=None, doubles=True):
    """Calculates Epsilon according to the equation
        epsilon_pq^rs = (F_p+F_q-F_r-F_s)
    or, if asked for, singles according to
        epsilon_p^r = (F_p-F_r)

    **Arguments:**

    lf
        A LinalgFactory instance.

    f
        Contains a list of one-index objects (e.g., orbital energies,
        diagonal Fock matrices, etc.). The order has to be [p,r,q,s] and they
        have to have the proper dimensions.

    **Optional Arguments:**

    singles
        If True, singles amplitudes are also calculated. They are only
        calculated for f[0] and f[1]. (default: False)

    shift
        A list of (orbital-dependent) shifts applied to the denominator.
        Either a float or a one-index object. Note that the shift overwrites
        the elements of f. (default: None)

    **Returns:**
        A list of epsilons. The order is [F_1, F_2]
    """
    #
    # Check types
    #
    if shift is not None:
        for el in shift:
            check_type("shift", el, float, OneIndex)
        if not len(f) == len(shift):
            raise EmptyData(
                "You have to provide for each explicitly given Fock matrix a shift."
            )
    for arg in f:
        check_type("arg", arg, OneIndex)
    #
    # Assign orbital energies/Fock matrix:
    #
    if len(f) == 4:
        fi = f[0]
        fa = f[1]
        fj = f[2]
        fb = f[3]
        #
        # Apply orbital-dependent shift:
        #
        if shift is not None:
            fi.iadd(shift[0])
            fa.iadd(shift[1])
            fj.iadd(shift[2])
            fb.iadd(shift[3])
    elif len(f) == 2:
        fi = f[0]
        fa = f[1]
        #
        # Apply orbital-dependent shift:
        #
        if shift is not None:
            fi.iadd(shift[0])
            fa.iadd(shift[1])
    else:
        raise ConsistencyError(
            "Do not know how to assign arguments to Fock matrix"
        )
    #
    # Get dimensions
    #
    nocc = f[0].nbasis
    nvirt = f[1].nbasis
    #
    # Create PT amplitudes
    # By default singles are calculated because they are used to determine
    # doubles
    #
    ts_1 = lf.create_two_index(nocc, nvirt)
    if len(f) == 4:
        ts_2 = lf.create_two_index(nocc, nvirt)
    if doubles:
        t_d = lf.create_two_index(nocc * nvirt, nocc * nvirt)
    #
    # Step 1:
    # Calculate singles (Fi-Fa) and, if required, (Fj-Fb)
    #
    ts_1.iadd(fi, 1.0)
    ts_1.iadd(fa, -1.0, transpose=True)
    if len(f) == 4:
        ts_2.iadd(fj, 1.0)
        ts_2.iadd(fb, -1.0, transpose=True)
    #
    # Step 2:
    # Calculate Doubles from singles (Fi+Fj-Fa-Fb)
    #
    if doubles:
        tsravel1 = ts_1.ravel()
        t_d.iadd(tsravel1)
        if len(f) == 4:
            tsravel2 = ts_2.ravel()
            t_d.iadd(tsravel2, transpose=True)
            del tsravel2
        else:
            t_d.iadd(tsravel1, transpose=True)
            del tsravel1
    if singles:
        if doubles:
            return ts_1, t_d
        return ts_1
    return t_d
