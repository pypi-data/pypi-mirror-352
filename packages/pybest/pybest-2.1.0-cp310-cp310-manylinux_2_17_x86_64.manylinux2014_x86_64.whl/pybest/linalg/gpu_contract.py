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
# 2023: GPU cupy support written by Maximilian Kriebel

"""Contract arrays via NVIDIA GPU using cupy."""

from __future__ import annotations

import copy
from typing import Any

import numpy as np

from pybest.exceptions import ArgumentError
from pybest.log import log, timer

# a list of hand-optimized CuPy routines, should outperform the generic implementation
# if a contraction is not contained here, a generic algorithm is also supplied
cupy_optimized = [
    "xac,xbd,ecfd->eafb",
    "xac,xbd,ecfd->efab",
    "xac,xbd,edfc->eafb",
    "xac,xbd,efcd->efab",
    "xac,xbd,efcd->efba",
    "xac,xbd,efcd->eafb",
    "xac,xbd,efcd->abef",
    "xac,xbd,cefd->faeb",
    "xac,xbd,cedf->aebf",
    "xac,xbd,cedf->aefb",
    "xac,xbd,cedf->abfe",
    "xac,xbd,ecdf->efab",
    "xac,xbd,efdc->efab",
    "xac,xbd,cfed->afeb",
    "xac,xbd,defc->aefb",
    "xac,xbd,cde->abe",
    "xac,xbd,dce->abe",
    "xac,xbd,ecfd->efba",
]


def cupy_availability_check():
    """Checks if Cupy CUDA is properly installed.

    Returns True or False.

    """
    try:
        import cupy as cp  # type: ignore
    except ImportError:
        log.warn("Warning")
        log.warn("Cupy CUDA not available.")
        log.warn("Defaulting to numpy.tensordot if select=None.")
        return False
    try:
        test_dummy_cupy = cp.zeros(0)
    except Exception:
        log.warn("Warning")
        log.warn("Can not allocate on VRAM.")
        log.warn("Cupy CUDA not properly installed.")
        log.warn("Defaulting to numpy.tensordot if select=None.")
        return False
    test_dummy_cupy += 1.0  # needed to make ruff happy
    del test_dummy_cupy
    cp.get_default_memory_pool().free_all_blocks()
    return True


#
# Utility function to assess sizes of arrays (used in batching)
#


# NOTE: Cannot use CholeskyFourIndex as type due to circular import error
def get_cholesky_size(
    chol_1: Any,
    chol_2: Any,
    axis_1: int | None = None,
    axis_2: int | None = None,
) -> float:
    """Return size in bytes for a given view of the Cholesky vectors

    Args:
        chol_1 (Any): Cholesky array1 (stored as array attribute)
        chol_2 (Any): Cholesky array2
        axis_1 (int, optional): number of batches used for array1. Defaults to None.
        axis_2 (int, optional): number of batches used for array2. Defaults to None.

    Returns:
        float: size of Cholesky arrays in bytes to be transferred to the GPU
    """
    # The recipe is as follows:
    # axis_1 = axis_2 = None: No batching of Cholesky vectors
    # axis_1 ! axis_2 = None: We only batch the first Cholesky vector (array1)
    # axis_1 and axis_2 != None: We batch both Cholesky vectors
    axis_1 = 1 if axis_1 is None else axis_1
    axis_2 = 1 if axis_2 is None else axis_2
    # Return updated size of batched Cholesky vectors
    return (
        chol_1.size * chol_1.itemsize / axis_1
        + chol_2.size * chol_2.itemsize / axis_2
    )


# NOTE: Cannot use CholeskyFourIndex as type due to circular import error
def get_abcd_size(
    chol_1: Any,
    chol_2: Any,
    axis_1: int | None = None,
    axis_2: int | None = None,
) -> float:
    """Return size in bytes for the dense intermediate abcd

    Args:
        chol_1 (Any): Cholesky array1 (stored as array attribute)
        chol_2 (Any): Cholesky array2
        axis_1 (int, optional): number of batches used for array1. Defaults to None.
        axis_2 (int, optional): number of batches used for array2. Defaults to None.

    Returns:
        float: size of the dense abcd array in bytes stored on the GPU
    """
    # The recipe is as follows:
    # axis_1 = axis_2 = None: No batching of Cholesky vectors
    # axis_1 ! axis_2 = None: We only batch the first Cholesky vector (array1)
    # axis_1 and axis_2 != None: We batch both Cholesky vectors
    axis_1 = 1 if axis_1 is None else axis_1
    axis_2 = 1 if axis_2 is None else axis_2
    return (
        chol_1.shape[1]
        * chol_1.shape[2]
        * chol_2.shape[1]
        * chol_2.shape[2]
        * chol_1.itemsize
        / axis_1
        / axis_2
    )


# NOTE: Cannot use CholeskyFourIndex as type due to circular import error
def get_batch_sizes(
    chol_1: Any, chol_2: Any, mem_gpu: float
) -> tuple[int, int]:
    """Get batch sizes for Cholesky axis.
    We first batch only the first Cholesky vector. If the data does not fit on
    the VRAM, we start batching the second Cholesky vector. The recipe is as
    follows:
    - increase batch number for second Cholesky vector by one
    - batch first Cholesky vector until everything fits on the VRAM
    - if VRAM is not sufficient go to the first step above until converged

    Args:
        chol_1 (Any): Cholesky array1 (stored as array attribute)
        chol_2 (Any): Cholesky array2
        mem_gpu (float): the available GPU VRAM

    Returns:
        tuple[int, int]: number of batches for both Cholesky arrays
    """
    # Get memory size for operands (input and output)
    # First, we need to assess the most expensive step without batching
    mem_chol = get_cholesky_size(chol_1, chol_2)
    mem_abcd = get_abcd_size(chol_1, chol_2)
    # This should be the memory peak
    # We assume that td creates an intermediate array that
    # is equal to the final array
    mem_need = mem_chol + 2 * mem_abcd
    n_batch_chol_1 = 1
    n_batch_chol_2 = 1

    # Use at most 90% of GPU VRAM
    # NOTE: use environment variable instead of hard-coded value of 0.9
    while mem_need > (mem_gpu * 0.9):
        # NOTE: Raising a MemoryError is not needed here as in the worst case
        # we end up with 2-D arrays. Even for very large dimensions, all
        # intermediates should still fit on less than 1 GB of VRAM.
        n_batch_chol_1 += 1
        if n_batch_chol_1 > chol_1.shape[1]:
            # Reset n_batch_chol_1 and start batching chol_2
            n_batch_chol_1 = 1
            n_batch_chol_2 += 1
        mem_chol = get_cholesky_size(
            chol_1, chol_2, axis_1=n_batch_chol_1, axis_2=n_batch_chol_2
        )
        mem_abcd = get_abcd_size(
            chol_1, chol_2, axis_1=n_batch_chol_1, axis_2=n_batch_chol_2
        )
        # Update mem_need for batched arrays
        mem_need = mem_chol + 2 * mem_abcd
    return n_batch_chol_1, n_batch_chol_2


#
# GPU helper classes to perform specific tensor contractions
#


@timer.with_section("GPU")
def cupy_helper(subs, *args, **kwargs):
    """Contraction using GPU via cupy

    *** Arguments ***

    * subscript : string
          Specifies the subscripts for summation as comma separated-list
          of subscript labels, for example: 'abcd,efcd->abfe'.

    * operands : DenseNIndex
          These are the other arrays for the operation.
          The last operand is treated as output.

    *** Keyword argument ***

    * parts : positive integer > 0
          If given, an array is split "parts" times and looped over.
          Mostly Cholesky array is split at index "x".
          Option for the user for limited GPU memory.

    """
    import cupy as cp

    mempool = cp.get_default_memory_pool()
    pinned_mempool = cp.get_default_pinned_memory_pool()

    if subs in (
        "xac,xbd,ecfd->eafb",  # much faster
        "xac,xbd,ecfd->efab",  # much faster
        "xac,xbd,edfc->eafb",  # much faster (~x19)
        "xac,xbd,efcd->efab",
        "xac,xbd,efcd->efba",
        "xac,xbd,efcd->eafb",
        "xac,xbd,efcd->abef",
        "xac,xbd,cefd->faeb",
        "xac,xbd,cedf->aebf",
        "xac,xbd,cedf->aefb",
        "xac,xbd,cedf->abfe",
        "xac,xbd,ecdf->efab",  # much faster (~x17)
        "xac,xbd,efdc->efab",  # much faster (~x10)
        "xac,xbd,cfed->afeb",  # much faster (~x10)
        "xac,xbd,defc->aefb",  # much faster (~x10)
        "xac,xbd,ecfd->efba",  # faster (~x2 numpy.td very efficient)
    ):
        axis_e = str(subs.split("->")[0].split(",")[-1]).rfind("e")
        axis_c = str(subs.split("->")[0].split(",")[-1]).rfind("c")
        axis_f = str(subs.split("->")[0].split(",")[-1]).rfind("f")
        axis_d = str(subs.split("->")[0].split(",")[-1]).rfind("d")

        memhave = cp.cuda.runtime.memGetInfo()[0]

        parts_chol = 1  # how often the cholesky arrays are split
        parts_dense = 1  # how often the dense and result arrays are split.

        # the size of necessery video memory is determined by:
        # number of elements of first dense array (or result of chol*chol)* 16
        # + number of elements of second dense array *16
        # + number of result array *16
        # each one is counted if split
        # in fact this does not really makes sense, because the video memory
        # should be deallocated in between
        # but it works and it crashes if choosen tighter.

        # increase the number how often dense and result array is splitted by 1
        # an upper limit to prevent an endless loop
        # for splitting reasoning, see above
        for parts_dense in range(1, 100):
            memneed = (
                16
                * args[0].shape[1]
                / int(parts_chol)
                * args[0].shape[2]
                * args[1].shape[1]
                / int(parts_chol)
                * args[1].shape[2]
                + 16
                * args[2].shape[axis_e]
                / int(parts_dense)
                * args[2].shape[axis_f]
                * args[0].shape[2]
                * args[1].shape[2]
                + 16
                * args[2].shape[axis_e]
                / int(parts_dense)
                * args[2].shape[axis_f]
                * args[0].shape[1]
                / int(parts_chol)
                * args[1].shape[1]
                / int(parts_chol)
            )

            # if necessary vram < available vram then leave loop and start
            if memhave > memneed:
                break

            # increase the number how often the cholesky are splitted by 1
            parts_chol += 1

            memneed = (
                16
                * args[0].shape[1]
                / int(parts_chol)
                * args[0].shape[2]
                * args[1].shape[1]
                / int(parts_chol)
                * args[1].shape[2]
                + 16
                * args[2].shape[axis_e]
                / int(parts_dense)
                * args[2].shape[axis_f]
                * args[0].shape[2]
                * args[1].shape[2]
                + 16
                * args[2].shape[axis_e]
                / int(parts_dense)
                * args[2].shape[axis_f]
                * args[0].shape[1]
                / int(parts_chol)
                * args[1].shape[1]
                / int(parts_chol)
            )

            if memhave > memneed:
                break

        parts_chol = kwargs.get("parts", parts_chol)
        parts_dense = kwargs.get("parts", parts_dense)

        # get lengths of chunks
        chol_chunk_lengths_1 = []
        for x in range(0, parts_chol):
            chol_chunk_lengths_1.append(
                np.array_split(args[0], parts_chol, axis=1)[x].shape[1]
            )
        chol_chunk_lengths_2 = []
        for x in range(0, parts_chol):
            chol_chunk_lengths_2.append(
                np.array_split(args[1], parts_chol, axis=1)[x].shape[1]
            )
        dense_e_chunk_lengths = []
        for x in range(0, parts_dense):
            dense_e_chunk_lengths.append(
                np.array_split(args[2], parts_dense, axis=axis_e)[x].shape[
                    axis_e
                ]
            )

        if parts_chol == 1 and parts_dense == 1:
            chol1 = cp.array(args[0])
            chol2 = cp.array(args[1])
            # x summation
            result_temp = cp.tensordot(chol1, chol2, axes=(0, 0))
            del chol1, chol2
            cp.get_default_memory_pool().free_all_blocks()
            operand = cp.array(args[2])
            result_part = cp.tensordot(
                result_temp, operand, axes=([1, 3], [axis_c, axis_d])
            )
            del result_temp, operand
            cp.get_default_memory_pool().free_all_blocks()
            if subs in (
                "xac,xbd,ecfd->efab",
                "xac,xbd,efcd->efab",
                "xac,xbd,ecdf->efab",
                "xac,xbd,efdc->efab",
            ):
                result_cp = cp.transpose(result_part, axes=(2, 3, 0, 1))
            elif subs in (
                "xac,xbd,ecfd->eafb",
                "xac,xbd,edfc->eafb",
                "xac,xbd,efcd->eafb",
            ):
                result_cp = cp.transpose(result_part, axes=(2, 0, 3, 1))
            elif subs in (
                "xac,xbd,efcd->efba",
                "xac,xbd,ecfd->efba",
            ):
                result_cp = cp.transpose(result_part, axes=(2, 3, 1, 0))
            elif subs == "xac,xbd,efcd->abef":
                result_cp = result_part
            elif subs == "xac,xbd,cefd->faeb":
                result_cp = cp.transpose(result_part, axes=(3, 0, 2, 1))
            elif subs == "xac,xbd,cedf->aebf":
                result_cp = cp.transpose(result_part, axes=(0, 2, 1, 3))
            elif subs == "xac,xbd,cedf->aefb":
                result_cp = cp.transpose(result_part, axes=(0, 2, 3, 1))
            elif subs == "xac,xbd,cedf->abfe":
                result_cp = cp.transpose(result_part, axes=(0, 1, 3, 2))
            elif subs == "xac,xbd,cfed->afeb":
                result_cp = cp.transpose(result_part, axes=(0, 2, 3, 1))
            elif subs == "xac,xbd,defc->aefb":
                result_cp = cp.transpose(result_part, axes=(0, 2, 3, 1))
            result = result_cp.get()
            del result_part, result_cp
            cp.get_default_memory_pool().free_all_blocks()
        else:
            result = np.zeros(args[3].shape)
            if parts_dense > 1:
                start_e = 0
                end_e = 0
                for e in range(0, parts_dense):
                    end_e += dense_e_chunk_lengths[e]
                    start_a = 0
                    end_a = 0
                    for a in range(0, parts_chol):
                        end_a += chol_chunk_lengths_1[a]
                        start_b = 0
                        end_b = 0
                        for b in range(0, parts_chol):
                            end_b += chol_chunk_lengths_2[b]
                            chol_1 = cp.array(
                                np.array_split(args[0], parts_chol, axis=1)[a]
                            )
                            chol_2 = cp.array(
                                np.array_split(args[1], parts_chol, axis=1)[b]
                            )
                            result_temp = cp.tensordot(
                                chol_1, chol_2, axes=(0, 0)
                            )
                            del chol_1, chol_2
                            cp.get_default_memory_pool().free_all_blocks()
                            operand = cp.array(
                                np.array_split(
                                    args[2],
                                    parts_dense,
                                    axis=axis_e,
                                )[e]
                            )
                            result_temp_2 = cp.tensordot(
                                result_temp,
                                operand,
                                axes=([1, 3], [axis_c, axis_d]),
                            )
                            del operand, result_temp
                            cp.get_default_memory_pool().free_all_blocks()
                            if subs in (
                                "xac,xbd,ecfd->efab",
                                "xac,xbd,efcd->efab",
                                "xac,xbd,ecdf->efab",
                                "xac,xbd,efdc->efab",
                            ):
                                result_part = cp.transpose(
                                    result_temp_2, axes=(2, 3, 0, 1)
                                )
                                del result_temp_2
                                cp.get_default_memory_pool().free_all_blocks()
                                result[
                                    start_e:end_e,
                                    :,
                                    start_a:end_a,
                                    start_b:end_b,
                                ] = result_part.get()
                                del result_part
                            elif subs in (
                                "xac,xbd,ecfd->eafb",
                                "xac,xbd,edfc->eafb",
                                "xac,xbd,efcd->eafb",
                            ):
                                result_part = cp.transpose(
                                    result_temp_2, axes=(2, 0, 3, 1)
                                )
                                del result_temp_2
                                cp.get_default_memory_pool().free_all_blocks()
                                result[
                                    start_e:end_e,
                                    start_a:end_a,
                                    :,
                                    start_b:end_b,
                                ] = result_part.get()
                                del result_part
                            elif subs in (
                                "xac,xbd,efcd->efba",
                                "xac,xbd,ecfd->efba",
                            ):
                                result_part = cp.transpose(
                                    result_temp_2, axes=(2, 3, 1, 0)
                                )
                                del result_temp_2
                                cp.get_default_memory_pool().free_all_blocks()
                                result[
                                    start_e:end_e,
                                    :,
                                    start_b:end_b,
                                    start_a:end_a,
                                ] = result_part.get()
                                del result_part
                            elif subs == "xac,xbd,cedf->abfe":
                                result_part = cp.transpose(
                                    result_temp_2, axes=(0, 1, 3, 2)
                                )
                                del result_temp_2
                                cp.get_default_memory_pool().free_all_blocks()
                                result[
                                    start_a:end_a,
                                    start_b:end_b,
                                    :,
                                    start_e:end_e,
                                ] = result_part.get()
                                del result_part
                            elif subs == "xac,xbd,cefd->faeb":
                                result_part = cp.transpose(
                                    result_temp_2, axes=(3, 0, 2, 1)
                                )
                                del result_temp_2
                                cp.get_default_memory_pool().free_all_blocks()
                                result[
                                    :,
                                    start_a:end_a,
                                    start_e:end_e,
                                    start_b:end_b,
                                ] = result_part.get()
                                del result_part
                            elif subs == "xac,xbd,cedf->aebf":
                                result_part = cp.transpose(
                                    result_temp_2, axes=(0, 2, 1, 3)
                                )
                                del result_temp_2
                                cp.get_default_memory_pool().free_all_blocks()
                                result[
                                    start_a:end_a,
                                    start_e:end_e,
                                    start_b:end_b,
                                    :,
                                ] = result_part.get()
                                del result_part
                            elif subs == "xac,xbd,cedf->aefb":
                                result_part = cp.transpose(
                                    result_temp_2, axes=(0, 2, 3, 1)
                                )
                                del result_temp_2
                                cp.get_default_memory_pool().free_all_blocks()
                                result[
                                    start_a:end_a,
                                    start_e:end_e,
                                    :,
                                    start_b:end_b,
                                ] = result_part.get()
                                del result_part
                            elif subs == "xac,xbd,efcd->abef":
                                result_part = result_temp_2
                                del result_temp_2
                                cp.get_default_memory_pool().free_all_blocks()
                                result[
                                    start_a:end_a,
                                    start_b:end_b,
                                    start_e:end_e,
                                    :,
                                ] = result_part.get()
                                del result_part
                            elif subs == "xac,xbd,cfed->afeb":
                                result_part = cp.transpose(
                                    result_temp_2, axes=(0, 2, 3, 1)
                                )
                                del result_temp_2
                                cp.get_default_memory_pool().free_all_blocks()
                                result[
                                    start_a:end_a,
                                    :,
                                    start_e:end_e,
                                    start_b:end_b,
                                ] = result_part.get()
                                del result_part
                            elif subs == "xac,xbd,defc->aefb":
                                result_part = cp.transpose(
                                    result_temp_2, axes=(0, 2, 3, 1)
                                )
                                del result_temp_2
                                cp.get_default_memory_pool().free_all_blocks()
                                result[
                                    start_a:end_a,
                                    start_e:end_e,
                                    :,
                                    start_b:end_b,
                                ] = result_part.get()
                                del result_part
                            cp.get_default_memory_pool().free_all_blocks()
                            start_b = end_b
                        start_a = end_a
                    start_e = end_e
            else:
                start_a = 0
                end_a = 0
                for a in range(0, parts_chol):
                    end_a += chol_chunk_lengths_1[a]
                    start_b = 0
                    end_b = 0
                    for b in range(0, parts_chol):
                        end_b += chol_chunk_lengths_2[b]
                        chol_1 = cp.array(
                            np.array_split(args[0], parts_chol, axis=1)[a]
                        )
                        chol_2 = cp.array(
                            np.array_split(args[1], parts_chol, axis=1)[b]
                        )
                        result_temp = cp.tensordot(chol_1, chol_2, axes=(0, 0))
                        del chol_1, chol_2
                        cp.get_default_memory_pool().free_all_blocks()
                        operand = cp.array(args[2])
                        result_temp_2 = cp.tensordot(
                            result_temp,
                            operand,
                            axes=([1, 3], [axis_c, axis_d]),
                        )
                        del operand, result_temp
                        cp.get_default_memory_pool().free_all_blocks()
                        if subs in (
                            "xac,xbd,ecfd->efab",
                            "xac,xbd,efcd->efab",
                            "xac,xbd,ecdf->efab",
                            "xac,xbd,efdc->efab",
                        ):
                            result_part = cp.transpose(
                                result_temp_2, axes=(2, 3, 0, 1)
                            )
                            del result_temp_2
                            cp.get_default_memory_pool().free_all_blocks()
                            result[:, :, start_a:end_a, start_b:end_b] = (
                                result_part.get()
                            )
                            del result_part
                        elif subs in (
                            "xac,xbd,ecfd->eafb",
                            "xac,xbd,edfc->eafb",
                            "xac,xbd,efcd->eafb",
                        ):
                            result_part = cp.transpose(
                                result_temp_2, axes=(2, 0, 3, 1)
                            )
                            del result_temp_2
                            cp.get_default_memory_pool().free_all_blocks()
                            result[:, start_a:end_a, :, start_b:end_b] = (
                                result_part.get()
                            )
                            del result_part

                        elif subs in (
                            "xac,xbd,efcd->efba",
                            "xac,xbd,ecfd->efba",
                        ):
                            result_part = cp.transpose(
                                result_temp_2, axes=(2, 3, 1, 0)
                            )
                            del result_temp_2
                            cp.get_default_memory_pool().free_all_blocks()
                            result[:, :, start_b:end_b, start_a:end_a] = (
                                result_part.get()
                            )
                            del result_part
                        elif subs == "xac,xbd,cedf->abfe":
                            result_part = cp.transpose(
                                result_temp_2, axes=(0, 1, 3, 2)
                            )
                            del result_temp_2
                            cp.get_default_memory_pool().free_all_blocks()
                            result[start_a:end_a, start_b:end_b, :, :] = (
                                result_part.get()
                            )
                            del result_part
                        elif subs == "xac,xbd,cefd->faeb":
                            result_part = cp.transpose(
                                result_temp_2, axes=(3, 0, 2, 1)
                            )
                            del result_temp_2
                            cp.get_default_memory_pool().free_all_blocks()
                            result[:, start_a:end_a, :, start_b:end_b] = (
                                result_part.get()
                            )
                            del result_part
                        elif subs == "xac,xbd,cedf->aebf":
                            result_part = cp.transpose(
                                result_temp_2, axes=(0, 2, 1, 3)
                            )
                            del result_temp_2
                            cp.get_default_memory_pool().free_all_blocks()
                            result[start_a:end_a, :, start_b:end_b, :] = (
                                result_part.get()
                            )
                            del result_part
                        elif subs == "xac,xbd,cedf->aefb":
                            result_part = cp.transpose(
                                result_temp_2, axes=(0, 2, 3, 1)
                            )
                            del result_temp_2
                            cp.get_default_memory_pool().free_all_blocks()
                            result[start_a:end_a, :, :, start_b:end_b] = (
                                result_part.get()
                            )
                            del result_part
                        elif subs == "xac,xbd,efcd->abef":
                            result_part = result_temp_2
                            del result_temp_2
                            cp.get_default_memory_pool().free_all_blocks()
                            result[start_a:end_a, start_b:end_b, :, :] = (
                                result_part.get()
                            )
                            del result_part
                        elif subs == "xac,xbd,cfed->afeb":
                            result_part = cp.transpose(
                                result_temp_2, axes=(0, 2, 3, 1)
                            )
                            del result_temp_2
                            cp.get_default_memory_pool().free_all_blocks()
                            result[start_a:end_a, :, :, start_b:end_b] = (
                                result_part.get()
                            )
                            del result_part
                        elif subs == "xac,xbd,defc->aefb":
                            result_part = cp.transpose(
                                result_temp_2, axes=(0, 2, 3, 1)
                            )
                            del result_temp_2
                            cp.get_default_memory_pool().free_all_blocks()
                            result[start_a:end_a, :, :, start_b:end_b] = (
                                result_part.get()
                            )
                            del result_part
                        cp.get_default_memory_pool().free_all_blocks()
                        start_b = end_b
                    start_a = end_a

    elif subs in (
        "xac,xbd,cde->abe",
        "xac,xbd,dce->abe",
    ):
        axis_e = str(subs.split("->")[0].split(",")[-1]).rfind("e")
        axis_c = str(subs.split("->")[0].split(",")[-1]).rfind("c")
        axis_d = str(subs.split("->")[0].split(",")[-1]).rfind("d")

        mem_gpu = cp.cuda.runtime.memGetInfo()[0]

        # We do not slice the dense arrays here as they are small
        n_batch_chol_1, n_batch_chol_2 = get_batch_sizes(
            args[0], args[1], mem_gpu
        )

        # Split all arrays
        chol_1_batched = np.array_split(args[0], n_batch_chol_1, axis=1)
        chol_2_batched = np.array_split(args[1], n_batch_chol_2, axis=1)

        result = np.zeros(args[3].shape)
        start_a = 0
        end_a = 0
        for xac in chol_1_batched:
            end_a = start_a + xac.shape[1]
            start_b = 0
            for xbd in chol_2_batched:
                end_b = start_b + xbd.shape[1]
                # Contract xac,xbd -> acbd
                chol_1 = cp.array(xac)
                chol_2 = cp.array(xbd)
                chol2dense = cp.tensordot(chol_1, chol_2, axes=(0, 0))
                # Free memory
                del chol_1, chol_2
                mempool.free_all_blocks()
                pinned_mempool.free_all_blocks()
                # Move dense to GPU
                operand = cp.array(args[2])
                # acbd,cde -> abe
                result_batch = cp.tensordot(
                    chol2dense,
                    operand,
                    axes=([1, 3], [axis_c, axis_d]),
                )
                # Free memory
                del operand, chol2dense
                mempool.free_all_blocks()
                pinned_mempool.free_all_blocks()
                # Assign to final array
                result[start_a:end_a, start_b:end_b, :] = result_batch.get()
                # Cleanup
                del result_batch
                mempool.free_all_blocks()
                pinned_mempool.free_all_blocks()
                start_b = end_b
            start_a = end_a

    # generic
    else:
        # the index x is reserved for Cholesky vectors
        # if an x is contained in a contraction subscript, we assume Cholesky vectors
        operands_cp = []
        # first operand cholesky decomposed
        if "x" == subs[0]:
            chol1 = cp.array(args[0])
            chol2 = cp.array(args[1])
            # xac,xbd -> acbd
            result_temp_cp = cp.tensordot(chol1, chol2, axes=(0, 0))
            del chol1, chol2
            mempool.free_all_blocks()
            pinned_mempool.free_all_blocks()
            # adds the other operands to operands_cp array
            # while leaving out the 2 cholesky arrays
            # Input operands are copied to GPU Memory (VRAM).
            for num in range(2, len(subs.split("->")[0].split(","))):
                operands_cp.append(cp.asarray(args[num]))
            # changes subscripts from e.g.: xac,xbd,...->... to: acbd,...->...
            subs = subs[1:3] + subs[5:]
            # acbd , ... -> ....
            # calculation on GPU
            result_cp = cp.einsum(
                subs, result_temp_cp, *operands_cp, optimize="optimal"
            )
            del result_temp_cp
        # first operand dense representation
        else:
            for num in range(0, len(subs.split("->")[0].split(","))):
                # Input operands are copied to GPU Memory (VRAM).
                operands_cp.append(cp.asarray(args[num]))
            # calculation on GPU
            result_cp = cp.einsum(subs, *operands_cp, optimize="optimal")
        # Result is copied back to RAM
        result = result_cp.get()
        # VRAM deallocation
        del result_cp, operands_cp

    mempool.free_all_blocks()
    pinned_mempool.free_all_blocks()
    # Result is returned
    return result


def get_view(
    subscript: str,
    start: int,
    end: int,
    char: str,
    input_view: list[slice] | None = None,
) -> list[slice] | slice:
    """Return a list of indices of a N-index output array.
    The axis corresponding to `char` is replaced by a view `start:end`.

    Args:
        subscript (str): the subscript of interest
        start (int): the first element of the view `start:end`
        end (int): the final element of the view `start:end`
        char (str): the character labeling the axis to be sliced, contained in subscript
        input_view (slice | None, optional): Update already existing slice if
                                             present. Defaults to None.

    Returns:
        slice: a slice instance or a list thereof encoding a view of an array used in batching
    """
    char_index = subscript.find(char)
    # Generate slice of axis that is batched/split
    view = slice(start, end, 1)
    # Update exisiting view if present
    if input_view is not None:
        if char_index == -1:
            return input_view
        # Insert view for label/char if batched
        input_view.pop(char_index)
        input_view.insert(char_index, view)
        return input_view
    # Generate list of slices from scratch
    slice_ = []
    for _ in range(len(subscript) - 1):
        slice_.append(slice(None))
    # Skip slicing if batched char/index not found
    if char_index == -1:
        slice_.append(slice(None))
        return slice_
    # Update view for batched char/index
    slice_.insert(char_index, view)
    return slice_


def get_batch_sizes_generic(
    step0: tuple[int, int],
    scripts: str,
    outscript: str,
    *operands: tuple[np.ndarray, ...],
) -> tuple[int, int, str, int, int, str]:
    """Get batch sizes for op0 and op1 to fit arrays on VRAM.
    We split the arrays based on the knowledge of the first contraction step
    step0.

    Args:
        step0 (tuple[int, int]): first contraction of the optimal einsum path
        scripts (str): the subscript containing the contraction recipe
        outscript (str): the final output in terms of subscripts abcd...

    Raises:
        MemoryError: if arrays do not fit on VRAM despite batching

    Returns:
        tuple[int, int, str, int, int, str]: batch sizes, axis, and label of axis
                                             to be split for operands op0 and op1
    """
    import cupy as cp

    # Get maximum VRAM available
    mem_gpu = cp.cuda.runtime.memGetInfo()[0]

    # Get memory size for op0 and op1
    mem_op0 = operands[step0[0]].nbytes
    mem_op1 = operands[step0[1]].nbytes
    # Get subscripts for op0 (script0) and op1 (script1)
    script0 = scripts[step0[0]]
    script1 = scripts[step0[1]]
    # Get output subscripts resulting from contracting op0 and op1
    # according to the recipe contained in script0 and script1
    # (Nonrepeating indices are considered output indices)
    outscript0_ = [i for i in script0 if i not in script1]
    outscript0_ += [i for i in script1 if i not in script0]
    outscript0_ = "".join(outscript0_)
    # Get memory size of output array
    mem_res0 = operands[step0[0]].itemsize
    # Assume no batches for result array along axis0 and axis1
    n_batch_res_0 = -1
    n_batch_res_1 = -1
    # Determine memory size of output array
    for char in outscript0_:
        if char in script0:
            i = script0.find(char)
            mem_res0 *= operands[step0[0]].shape[i]
            # Check if op0 and output share subscripts
            n_batch_res_0 += 1
            continue
        if char in script1:
            i = script1.find(char)
            mem_res0 *= operands[step0[1]].shape[i]
            # Check if op1 and output share subscripts
            n_batch_res_1 += 1
            continue
    # Determine memory peak of tensordot operation
    # (all arrays will be moved to the GPU)
    mem_need = mem_op0 + mem_op1 + mem_res0 * 2.0
    axis0, axis1 = -1, -1
    # Check if final outscripts appear in current contraction
    # result (outscript0_)
    batch_axis = [char for char in outscript0_ if outscript.find(char) != -1]
    for ind in batch_axis:
        axis0 = script0.find(ind)
        # Take first occurence
        if axis0 != -1:
            ind0 = ind
            break
    for ind in batch_axis:
        axis1 = script1.find(ind)
        # Take first occurence
        if axis1 != -1:
            ind1 = ind
            break
    # Default batch sizes
    n_batch_0 = 1  # if axis0 is None else 1
    n_batch_1 = 1  # if axis1 is None else 1
    while mem_need > 0.9 * mem_gpu:
        # Determine batch size for axis0
        if axis0 != -1:
            n_batch_0 += 1
            mem_op0 = operands[step0[0]].nbytes / n_batch_0
            scale = 1 if n_batch_res_0 == -1 else n_batch_0
            mem_need = mem_op0 + mem_op1 + mem_res0 * 2.0 / scale
            if n_batch_0 > operands[step0[0]].shape[axis0]:
                raise MemoryError
        # Determine batch size for axis1
        if axis1 != -1:
            n_batch_1 += 1
            mem_op1 = operands[step0[1]].nbytes / n_batch_1
            scale = 1 if n_batch_res_1 == -1 else n_batch_1
            mem_need = mem_op0 + mem_op1 + mem_res0 * 2.0 / scale
            if n_batch_1 > operands[step0[1]].shape[axis1]:
                raise MemoryError

    # Default batch axis if we couldn't find anything
    default_ind0 = 1 if "x" in script0 else 0
    default_ind1 = 1 if "x" in script1 else 0
    # Finally, set axis and batched subscripts (ind0, ind1)
    ind0 = script0[default_ind0] if axis0 == -1 else ind0
    ind1 = script1[default_ind1] if axis1 == -1 else ind1
    axis0 = default_ind0 if axis0 == -1 else axis0
    axis1 = default_ind1 if axis1 == -1 else axis1

    return n_batch_0, axis0, ind0, n_batch_1, axis1, ind1


@timer.with_section("GPU")
def td_cupy_helper(
    subscripts: str,
    *operands: tuple[np.ndarray, ...],
    **kwargs: Any,
) -> np.ndarray:
    """Performes cp.tensordot operations with numpy.einsum input format.

    Args:
        subscripts (str): einstein summation label, e.g. 'xac,xbd,defc->abfe'
        operands (np.ndarray): first and second are arrays of CholeskyFourIndex
                               or DenseNIndex, the third is an array of DenseNIndex object

    Raises:
        ArgumentError: if tensordot operation is not possible

    Returns:
        np.ndarray: the final output of a tensor contraction
    """
    import cupy as cp

    shape = kwargs.get("shape")

    if "->" in subscripts:
        inscripts, outscript = subscripts.split("->")
    else:
        inscripts = subscripts
        outscript = None
    scripts = inscripts.split(",")

    # Sanity check.
    error_message = f"'td' not available for operation {subscripts}."
    if len(scripts) < 2:
        raise ArgumentError(error_message)
    for char in subscripts:
        if (subscripts.count(char) > 2) and char.isalpha():
            raise ArgumentError(error_message)
    for script in scripts:
        for char in script:
            if script.count(char) > 1:
                raise ArgumentError(error_message)

    operands = list(operands)

    # Do contractions.
    path, _ = np.einsum_path(subscripts, *operands)

    # Sometimes einsum_path does not return a list of two-element tuples.
    # Since there is no optimized path, we provide some not-optimized path.
    if len(path) < len(operands):
        path = [(0, 1) for i in range(len(operands))]

    mempool = cp.get_default_memory_pool()
    pinned_mempool = cp.get_default_pinned_memory_pool()

    # Get number of batches for op0 and op1, the corresponding axes (the ones
    # that are split/batched), and the label (ind) of the splitted subscripts
    # (abcd...)
    n_batch_0, axis0, ind0, n_batch_1, axis1, ind1 = get_batch_sizes_generic(
        path[1], scripts, outscript, *operands
    )

    # We will batch the first arrays that appear in einsum_path and in the output
    # They correspond to operands[step0[0]] and operands[step0[1]]
    # First assess memory needed for first contraction in path
    step = path[1]

    # Split first two operands contained in first step of path into
    # batches under the condition that input and output share axis indices
    op0_batched = np.array_split(operands.pop(step[0]), n_batch_0, axis=axis0)
    op1_batched = np.array_split(
        operands.pop(step[1] - 1), n_batch_1, axis=axis1
    )

    # Create final output
    result = np.zeros(shape)

    # Loop over batched operators
    # start_X and end_X indicate the view of the batched array
    start_0 = 0
    end_0 = 0
    for op0_ in op0_batched:
        # Update views of batched arrays (needed for assigning results)
        end_0 = start_0 + op0_.shape[axis0]
        start_1 = 0
        # Update view of results array for axis0
        # The batched scipts need to show up in the results, otherwise
        # they are simply ignored and the whole array is taken as view
        view = get_view(outscript, start_0, end_0, ind0)
        for op1_ in op1_batched:
            # Update views of batched arrays (needed for assigning results)
            end_1 = start_1 + op1_.shape[axis1]
            # Update view of results array for axis1
            view = get_view(outscript, start_1, end_1, ind1, view)
            # Copy subscripts as they get deleted during the batching
            # process. Use a deep copy to work with
            scripts_ = copy.deepcopy(scripts)
            # Create a deep copy of the path. Due to batching, we will
            # execute the same path several times
            # Each path gets deleted AFTER it has been executed
            path_ = copy.deepcopy(path)
            # Create a shallow copy (not copying data) of operand list
            # We loop through the list for each batched view
            # In each iteration, the operands are popped (deleted) from
            # the list. A copy is needed to restart the loop in each
            # batched step
            operands_ = copy.copy(operands)
            for counter, step in enumerate(path_[1:]):
                # For the 0-th iteration, we need to take the batched arrays
                # For each subsequent path step, we need to pop the next operand
                # contained in the list of operands.
                # The (copied) list of operands contains only unused arrays, that
                # is arrays that have NOT been contracted yet
                op0 = op0_ if counter == 0 else operands_.pop(step[0])
                op1 = op1_ if counter == 0 else operands_.pop(step[1] - 1)
                # Get first subscripts used for op0 (the first in the list of
                # operands)
                script0 = scripts_.pop(step[0])
                # Get view of new op0 for first batched index (ind0)
                # We need to check if ind0 or ind1 are contained in script0
                # If yes, we need to adjust the view, otherwise the take the
                # whole axis
                view_0 = get_view(script0, start_0, end_0, ind0)
                if ind1 in script0:
                    # Update view_0 for second batched index (ind1)
                    view_0 = get_view(script0, start_1, end_1, ind1, view_0)
                # Update view of op0 so that dimensions matched
                # We distinguish the following cases
                # - counter == 0: very first iteration containing only the
                #                 batched arrays. No view updates required
                # - counter > 0: op0 corresponds to the next, yet uncontracted
                #                operand. Its view must be matched with the
                #                operand generated in the previous contraction
                #                step
                op0 = op0 if counter == 0 else op0[tuple(view_0)]
                # Subscripts for second operand
                script1 = scripts_.pop(step[1] - 1)
                # Find summation axes used in tensordot notation
                sum_ind = [i for i in script0 if i in script1]
                axis0_ = [script0.index(i) for i in sum_ind]
                axis1_ = [script1.index(i) for i in sum_ind]
                axis_ = (axis0_, axis1_)
                # Find default outscript of tensordot operation
                # It may differ from the outscript of the overal tensor
                # contraction due to the way tensordot works
                # Required for transposition step below
                outscript_ = [i for i in script0 if i not in script1]
                outscript_ += [i for i in script1 if i not in script0]
                outscript_ = "".join(outscript_)
                # Move arrays to GPU
                op0_gpu = cp.array(op0)
                op1_gpu = cp.array(op1)
                # Do contraction on GPU (finally)
                outmat = cp.tensordot(op0_gpu, op1_gpu, axes=axis_)
                # Cleanup
                del op0_gpu, op1_gpu
                mempool.free_all_blocks()
                pinned_mempool.free_all_blocks()
                # Update the list of operands and subscripts
                # The partially contracted array and its subscripts
                # (here outscript_) are appended to the working copies
                # of the operands and scripts. They will be used in the
                # next contraction step
                operands_.append(outmat)
                scripts_.append(outscript_)
            # Do transposition if required
            if (outscript != outscript_) and (outscript is not None):
                trans = tuple(outscript_.index(i) for i in outscript)
                outmat = outmat.transpose(trans)
            # Add batched contraction result to view of result array
            result[tuple(view)] += outmat.get()
            # Cleanup
            del outmat
            mempool.free_all_blocks()
            pinned_mempool.free_all_blocks()
            # Move to next batch for axis1
            start_1 = end_1
        # Move to next batch for axis0
        start_0 = end_0
    return result
