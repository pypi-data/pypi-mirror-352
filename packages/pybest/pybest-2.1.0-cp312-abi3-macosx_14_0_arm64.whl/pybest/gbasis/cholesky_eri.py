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
"""Cholesky-decomposed ERI interface."""

from __future__ import annotations

import numpy as np

from pybest.core import ints
from pybest.log import log, timer

# nanobind classes
from . import Basis

__all__ = [
    "compute_cholesky_eri",
]


PYBEST_CHOLESKY_ENABLED = hasattr(ints, "compute_cholesky_eri_cpp")


@timer.with_section("Ints: CD-ERI")
def compute_cholesky_eri(
    basis0: Basis,
    basis1: Basis | None = None,
    symmetry: bool = True,
    threshold: float = 1e-4,
    prealloc: int = 15,
):
    """Compute the cholesky decomposed ERI in a Gaussian orbital basis

     **Arguments:**

     basis0, basis1
         A Basis instance

     threshold float
         accuracy threshold for cd-eri algorithm

     prealloc int
         controlls pre-allocation size of output tensor.

         total size is Naux x Nbf x Nbf,
         prealloc controlls size of Naux as:
         Naux = prealloc * Nbf.

         For thresholds below 1e-6 prealloc=10 is reasonable.
         If pre-allocation size won't be sufficient,
         additional memory allocations and data movement might
         occur, degrading the performance.


    **Returns:** ``CholeskyFourIndex`` object
    """
    if not PYBEST_CHOLESKY_ENABLED:
        log.warn(
            "Cholesky-decomposition ERI are not available. Build libchol and "
            "re-run build PYBEST_ENABLE_CHOLESKY=1"
        )
        raise RuntimeError(
            "Cholesky decomposition of ERI was not enabled during compilation!"
        )
    # To prevent circular imports, import locally.
    # This can be fixed by passing an lf instance, which requires a rewrite
    from pybest.linalg import CholeskyFourIndex

    log.warn(f"basis1:{basis1} option is not active in cd-eri module")
    log.warn(f"symmetry:{symmetry} option is not active in cd-eri module")
    nbasis0 = basis0.nbasis

    if log.do_medium:
        log.hline("~")
        log("Computing cholesky decomposed ERI:")
        log(f"NBASIS:        {nbasis0}")
        log(f"CD_THRESH:     {threshold}")
        log(f"CD_BETA:       {prealloc}")
        log("computing ...")

    # call the low-level routine
    cd_eri = ints.compute_cholesky_eri_cpp(basis0, threshold, prealloc)
    nvec = int(cd_eri.size / (nbasis0 * nbasis0))

    # fold to 3-idx tensor
    cd_eri_npy = cd_eri.reshape(nvec, nbasis0, nbasis0)

    # compute some statistics
    cd_eri_nbytes = cd_eri_npy.nbytes
    cd_eri_mib = cd_eri_nbytes / (float(1024) ** 2)
    cd_eri_sparsity = 1.0 - np.count_nonzero(cd_eri_npy) / float(
        cd_eri_npy.size
    )

    if log.do_medium:
        log("\t finished!")
        log(f"CD_ERI_SHAPE:    {(nvec, nbasis0, nbasis0)}")
        log(f"CD_ERI_SIZE:     {cd_eri_npy.size}")
        log(f"CD_ERI_BYTES:    {cd_eri_nbytes} ({cd_eri_mib:.2f} MiB)")
        log(f"CD_ERI_SPARSITY: {100 * cd_eri_sparsity:.2f} %")
        log.hline("~")

    out = CholeskyFourIndex(
        nbasis=nbasis0,
        nvec=nvec,
        array=cd_eri_npy,
        array2=cd_eri_npy,
        copy=False,
        label="cd-eri",
    )
    return out
