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
"""Functions used in NIndex.contract function"""

import gc
from collections.abc import Sequence
from itertools import groupby, islice

from numpy.typing import NDArray

from ._opt_einsum import oe_contract

try:
    from itertools import batched
except ImportError:
    # TODO: remove after minimal Python version is 3.12
    def batched(iterable, n):
        # batched('ABCDEFG', 3) --> ABC DEF G
        if n < 1:
            raise ValueError("n must be at least one")
        it = iter(iterable)
        while batch := tuple(islice(it, n)):
            yield batch


import numpy as np
from numpy import tensordot as td

from pybest.exceptions import ArgumentError

#
# Routines
#


def td_helper(subscripts, *operands):
    """Performes numpy.tensordot operations with numpy.einsum input format.

    **Arguments**

    subscripts : str
        e.g. 'xac,xbd,defc->abfe'

    operands : numpy.ndarray
        first and second are arrays of CholeskyFourIndex or DenseNIndex,
        the third is an array of DenseNIndex object
    """
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

    for step in path[1:]:
        # Take 1st and 2nd operands and corresponding subscripts
        op0 = operands.pop(step[0])
        op1 = operands.pop(step[1] - 1)
        script0 = scripts.pop(step[0])
        script1 = scripts.pop(step[1] - 1)
        # Find summation axes
        sum_ind = [i for i in script0 if i in script1]
        axis0 = [script0.index(i) for i in sum_ind]
        axis1 = [script1.index(i) for i in sum_ind]
        axis = (axis0, axis1)
        # Find default outscript
        outscript_ = [i for i in script0 if i not in script1]
        outscript_ += [i for i in script1 if i not in script0]
        outscript_ = "".join(outscript_)
        # Do contraction
        outmat = np.tensordot(op0, op1, axes=axis)
        # Update the list of operands and subscripts
        operands.append(outmat)
        scripts.append(outscript_)
    # Do transposition if required.
    if (outscript != outscript_) and (outscript is not None):
        trans = tuple(outscript_.index(i) for i in outscript)
        outmat = outmat.transpose(trans)
    return outmat


def cholesky_td_routine(
    subscripts,
    operands_: Sequence[NDArray[np.float64]],
    arr,
    factor,
    save_memory=False,
):
    """All existing tensordot contractions from CholeskyFourIndex class
    are collected here.
        It is a temporary solution for the lack of td_helper method in
    CholeskyLinalgFactory class.

    *** Arguments ***
    * subscripts : str
    * operands : list of numpy.ndarray
    * arr : numpy.ndarray
        the result of contraction is added to arr
    * factor : float or int
    * save_memory : boolean. If True, a partial for-loop implementation is
                    chosen. This option is only supported for specific
                    contractions starting with `abcd->`:
                    abcd->abcd, ... (and all remaining 23 permutations of abcd)
                    OR
                    the routine with the smallest intermediates is chosen
    """
    op0 = operands_[0]
    op1 = operands_[1]
    input_scripts, output_scripts = parse_subscripts(subscripts)
    # First check for all possible transpositions of a contraction of type
    # 'abcd->abcd'
    if len(input_scripts) == 1:
        input_abcd = all((c in input_scripts[0]) for c in "abcd")
        output_abcd = all((c in output_scripts) for c in "abcd")
        if input_abcd and output_abcd:
            cholesky_td_routine_abcd(
                subscripts, operands_, arr, factor, save_memory
            )
            return
    # Do remaining special cases:
    if subscripts == "abab->ab":
        L_xa = np.diagonal(op0, axis1=1, axis2=2)
        L_xb = np.diagonal(op1, axis1=1, axis2=2)
        arr[:] += factor * td(L_xa, L_xb, axes=(0, 0))
    elif subscripts == "abcb->abc":
        L_r = np.diagonal(op1, axis1=1, axis2=2)
        arr[:] += factor * td(op0, L_r, axes=(0, 0)).swapaxes(1, 2)
    elif subscripts == "abcb->ac":
        L_xb = np.diagonal(op1, axis1=1, axis2=2)
        L_x = np.einsum("ab->a", L_xb, optimize=True)
        del L_xb
        arr[:] += factor * td(op0, L_x, axes=(0, 0))
    elif subscripts == "abcc->abc":
        for i in range(op0.shape[2]):
            arr[:, :, i] += factor * td(
                op0[:, :, i], op1[:, :, i], axes=(0, 0)
            )
    elif subscripts == "abcc->acb":
        for i in range(op0.shape[2]):
            arr[:, i, :] += factor * td(
                op0[:, :, i], op1[:, :, i], axes=(0, 0)
            )
    elif subscripts == "abcd,c->abd":
        # first do xac,c->xa
        tmp = td(op0, operands_[2], axes=(2, 0))
        # xa,xbd->abd
        arr[:, :, :] += factor * td(tmp, op1, axes=(0, 0))
    elif subscripts == "abcd,c->adb":
        # first do xac,c->xa
        tmp = td(op0, operands_[2], axes=(2, 0))
        # xa,xbd->adb
        arr[:, :, :] += factor * td(tmp, op1, axes=(0, 0)).transpose((0, 2, 1))
    elif subscripts == "abcd,d->abc":
        # first do xbd,d->xb
        tmp = td(op1, operands_[2], axes=(2, 0))
        # xac,xb->abc
        arr[:, :, :] += factor * td(op0, tmp, axes=(0, 0)).transpose((0, 2, 1))
    elif subscripts == "abcd,d->acb":
        # first do xbd,d->xb
        tmp = td(op1, operands_[2], axes=(2, 0))
        # xac,xb->acb
        arr[:, :, :] += factor * td(op0, tmp, axes=(0, 0))
    elif subscripts == "abac,bc->ac":
        # xaa -> xa
        L_xa = np.diagonal(op0, axis1=1, axis2=2)
        # sum over b to get xc
        L_xc = oe_contract("xbc,bc->xc", op1, operands_[2])
        # xa,xc -> ac
        arr[:] += factor * td(L_xa, L_xc, axes=(0, 0))
    elif subscripts == "abcc,b->ac":
        # xbc,b->xc
        tmp = td(op1, operands_[2], axes=(1, 0))
        for i in range(op0.shape[2]):
            # xa[c],x[c]->a[c]
            arr[:, i] += factor * td(op0[:, :, i], tmp[:, i], axes=(0, 0))
    elif subscripts == "abcc,ac->ab":
        tmp = np.multiply(
            op0[:,],
            operands_[2],
        )
        arr[:] += factor * td(tmp, op1, axes=([0, 2], [0, 2]))
    elif subscripts == "abcc,ab->ab":
        tmp = np.tensordot(op0, op1, axes=([0, 2], [0, 2]))
        arr[:] += factor * np.multiply(tmp, operands_[2])
    elif subscripts == "abcc,ca->ab":
        tmp = np.multiply(
            op0[:,],
            operands_[2].T,
        )
        arr[:] += factor * td(tmp, op1, axes=([0, 2], [0, 2]))
    elif subscripts == "abcc,ab->c":
        tmp = td(op0, operands_[2], axes=([1], [0]))
        arr[:] += factor * td(tmp, op1, axes=([0, 2], [0, 1])).diagonal()
    elif subscripts == "abcd,ac->acbd":
        # use np.einsum with optimize=True to construct smaller intermediate
        tmp = np.einsum("xac,ac->xac", op0, operands_[2], optimize=True)
        # if this is to expensive, use the memory saving routine
        if save_memory:
            cholesky_td_routine_abcd(
                "abcd->acbd", (tmp, op1), arr, factor, True
            )
        else:
            arr[:] += factor * td(tmp, op1, axes=(0, 0))
    elif subscripts == "abcd,ad->adbc":
        # loop here to not construct expensive 4-index intermediate
        for i in range(op1.shape[2]):
            tmp = td(op0, op1[:, :, i], axes=(0, 0)).transpose(0, 2, 1)
            # use np.einsum with optimize=True to perform operation that is not
            # possible with tensordot. Not ideal, but still much better than
            # the alternative without for loops.
            arr[:, i, :, :] += factor * np.einsum(
                "abc,a->abc", tmp, operands_[2][:, i], optimize=True
            )
    elif subscripts == "abcc,abd->cd":
        # loop here to not construct expensive 4-index intermediate
        for i in range(op0.shape[2]):
            # xac,xbc->ab[c]
            tmp = td(op0[:, :, i], op1[:, :, i], axes=(0, 0))
            # [c]d += ab[c] abd
            arr[i, :] += factor * td(tmp, operands_[2], axes=([0, 1], [0, 1]))
    elif subscripts == "abcd,abc->d":
        # first do xac,abc->xb
        tmp = td(op0, operands_[2], axes=([1, 2], [0, 2]))
        # xbd,xb->d
        arr[:] += factor * td(op1, tmp, axes=([0, 1], [0, 1]))
    elif subscripts == "abcd,abd->c":
        # first do xbd,abd->xa
        tmp = td(op1, operands_[2], axes=([1, 2], [1, 2]))
        # xac,xa->c
        arr[:] += factor * td(op0, tmp, axes=([0, 1], [0, 1]))
    elif subscripts == "abcd,cdb->a":
        # first do xbd,cdb->xc
        tmp = td(op1, operands_[2], axes=([1, 2], [2, 1]))
        # xc,xac->a
        arr[:] += factor * td(tmp, op0, axes=([0, 1], [0, 2]))
    elif subscripts == "abcd,dcb->a":
        # first do xbd,dcb->xc
        tmp = td(op1, operands_[2], axes=([1, 2], [2, 0]))
        # xc,xac->a
        arr[:] += factor * td(tmp, op0, axes=([0, 1], [0, 2]))
    elif subscripts == "abcd,cde->abe":
        # dim is typically equal to nacto
        dim = operands_[2].shape[2]
        # check if we have an intermediate of size at most o2v2
        check_size_of_intermediate = (op0.shape[0] // dim + 1) < dim
        # either sum over [e] axis or partition [x] into smaller junks
        # the second option requires larger intermediates, but is faster
        # we default to the second option [x]
        if not save_memory and check_size_of_intermediate:
            for x in batched(range(op0.shape[0]), dim):
                tmp = td(op0[x, :, :], operands_[2], axes=(2, 0))
                arr[:] += factor * td(
                    tmp, op1[x, :, :], axes=([0, 2], [0, 2])
                ).transpose(0, 2, 1)
            return
        for i in range(operands_[2].shape[2]):
            tmp = td(op0, operands_[2][:, :, i], axes=(2, 0))
            arr[:, :, i] += factor * td(tmp, op1, axes=([0, 2], [0, 2]))
    elif subscripts == "abcd,dce->abe":
        # dim is typically equal to nacto
        dim = operands_[2].shape[2]
        # check if we have an intermediate of size at most o2v2
        check_size_of_intermediate = (op0.shape[0] // dim + 1) < dim
        # either sum over [e] axis or partition [x] into smaller junks
        # the second option requires larger intermediates, but is faster
        # we default to the second option [x]
        if not save_memory and check_size_of_intermediate:
            for x in batched(range(op0.shape[0]), dim):
                tmp = td(op0[x, :, :], operands_[2], axes=(2, 1))
                arr[:] += factor * td(
                    tmp, op1[x, :, :], axes=([0, 2], [0, 2])
                ).transpose(0, 2, 1)
            return
        for i in range(operands_[2].shape[2]):
            tmp = td(op0, operands_[2][:, :, i], axes=(2, 1))
            arr[:, :, i] += factor * td(tmp, op1, axes=([0, 2], [0, 2]))
    elif subscripts == "abcd,efbd->efac":
        # xbd,efbd->xef
        tmp = td(op1, operands_[2], axes=([1, 2], [2, 3]))
        arr[:] += factor * td(tmp, op0, axes=([0], [0]))
    elif subscripts == "abcd,edbf->efac":
        # xbd,edbf->xef
        tmp = td(op1, operands_[2], axes=([1, 2], [2, 1]))
        arr[:] += factor * td(tmp, op0, axes=([0], [0]))
    elif subscripts == "abcd,befd->acfe":
        # xbd,befd->xfe
        tmp = td(op1, operands_[2], axes=([1, 2], [0, 3])).transpose((0, 2, 1))
        arr[:] += factor * td(op0, tmp, axes=([0], [0]))
    elif subscripts == "abcd,ecfd->eafb":
        # default to batches of 10 elements
        slices = 1 if save_memory else 10
        for a in batched(range(op0.shape[1]), slices):
            # xac,xbd->[a]cbd
            tmp = td(op0[:, a, :], op1, axes=(0, 0))
            # ecfd,[a]cbd->ef[a]b
            arr[:, a, :, :] += factor * td(
                operands_[2], tmp, axes=([1, 3], [1, 3])
            ).transpose((0, 2, 1, 3))
    elif subscripts == "abcd,edfc->eafb":
        # default to batches of 10 elements
        slices = 1 if save_memory else 10
        for a in batched(range(op0.shape[1]), slices):
            # xbd,xac->bd[a]c
            tmp = td(op1, op0[:, a, :], axes=(0, 0))
            # edfc,bd[a]c->efb[a]
            arr[:, a, :, :] += factor * td(
                operands_[2], tmp, axes=([1, 3], [1, 3])
            ).transpose((0, 3, 1, 2))
    elif subscripts == "abcd,ecdf->eabf":
        # default to batches of 10 elements
        slices = 1 if save_memory else 10
        for a in batched(range(op0.shape[1]), slices):
            # xac,xbd->[a]cbd
            tmp = td(op0[:, a, :], op1, axes=(0, 0))
            # ecdf,[a]cbd->ef[a]b
            arr[:, a, :, :] += factor * td(
                operands_[2], tmp, axes=([1, 2], [1, 3])
            ).transpose((0, 2, 3, 1))
    elif subscripts == "abcd,efcd->efab":
        # default to batches of 10 elements
        slices = 1 if save_memory else 10
        for a in batched(range(op0.shape[1]), slices):
            # xac,xbd->[a]cbd
            tmp = td(op0[:, a, :], op1, axes=(0, 0))
            # efcd,[a]cbd->efb[a]
            arr[:, :, a, :] += factor * td(
                operands_[2], tmp, axes=([2, 3], [1, 3])
            )
    elif subscripts == "abcd,efcd->efba":
        # default to batches of 10 elements
        slices = 1 if save_memory else 10
        for a in batched(range(op0.shape[1]), slices):
            # xbd,xac->bd[a]c
            tmp = td(op1, op0[:, a, :], axes=(0, 0))
            # efcd,bd[a]c->efb[a]
            arr[:, :, :, a] += factor * td(
                operands_[2], tmp, axes=([2, 3], [3, 1])
            )
    elif subscripts == "abcd,efcd->eafb":
        # default to batches of 10 elements
        slices = 1 if save_memory else 10
        for a in batched(range(op0.shape[1]), slices):
            # xac,xbd->[a]cbd
            tmp = td(op0[:, a, :], op1, axes=(0, 0))
            # efcd,[a]cbd->ef[a]b
            arr[:, a, :, :] += factor * td(
                operands_[2], tmp, axes=([2, 3], [1, 3])
            ).transpose((0, 2, 1, 3))
    elif subscripts == "abcd,ecfd->efab":
        # default to batches of 10 elements
        slices = 1 if save_memory else 10
        for a in batched(range(op0.shape[1]), slices):
            # xac,xbd->[a]cbd
            tmp = td(op0[:, a, :], op1, axes=(0, 0))
            # ecfd,[a]cbd->ef[a]b
            arr[:, :, a, :] += factor * td(
                operands_[2], tmp, axes=([1, 3], [1, 3])
            )
    elif subscripts == "abcd,cefd->faeb":
        # default to batches of 10 elements
        slices = 1 if save_memory else 10
        for a in batched(range(op0.shape[1]), slices):
            # xac,xbd->[a]cbd
            tmp = td(op1, op0[:, a, :], axes=(0, 0))
            # cefd,bd[a]c->efb[a]
            arr[:, a, :, :] += factor * td(
                operands_[2], tmp, axes=([0, 3], [3, 1])
            ).transpose((1, 3, 0, 2))
    elif subscripts == "abcd,efcd->abef":
        # default to batches of 10 elements
        slices = 1 if save_memory else 10
        for a in batched(range(op0.shape[1]), slices):
            # xac,xbd->[a]cbd
            tmp = td(op0[:, a, :], op1, axes=(0, 0))
            # [a]cbd,efcd->[a]bef
            arr[a, :, :, :] += factor * td(
                tmp, operands_[2], axes=([1, 3], [2, 3])
            )
    elif subscripts == "abcd,cedf->aebf":
        # default to batches of 10 elements
        slices = 1 if save_memory else 10
        for a in batched(range(op0.shape[1]), slices):
            # xac,xbd->[a]cbd
            tmp = td(op0[:, a, :], op1, axes=(0, 0))
            # [a]cbd,cedf->[a]bef
            arr[a, :, :, :] += factor * td(
                tmp, operands_[2], axes=([1, 3], [0, 2])
            ).transpose((0, 2, 1, 3))
    elif subscripts == "abcd,cedf->beaf":
        # default to batches of 10 elements
        slices = 1 if save_memory else 10
        for a in batched(range(op0.shape[1]), slices):
            # xbd,xac->bd[a]c
            tmp = td(op1, op0[:, a, :], axes=(0, 0))
            # cedf,bd[a]c->efb[a]
            arr[:, :, a, :] += factor * td(
                operands_[2], tmp, axes=([0, 2], [3, 1])
            ).transpose((2, 0, 3, 1))
    elif subscripts == "abcd,edaf->efbc":
        # default to batches of 10 elements
        slices = 1 if save_memory else 10
        for b in batched(range(op1.shape[1]), slices):
            # xbd,xac->[b]dac
            tmp = td(op1[:, b, :], op0, axes=(0, 0))
            # edaf,[b]dac->ef[b]c
            arr[:, :, b, :] += factor * td(
                operands_[2], tmp, axes=([1, 2], [1, 2])
            )
    elif subscripts in (
        "abcd,cedf->aefb",
        "abcd,cedf->abfe",
    ):
        # Should work for any contraction of type 'abcd,cedf->a...'.
        _, outscript = subscripts.split("->")
        trans = ["efb".index(char) for char in outscript[1:]]
        # Do bcd,cedf->efb, the transpose efb and add it to output.
        for i in range(op0.shape[1]):
            tmp = td(op0[:, i, :], op1, axes=(0, 0))
            arr[i, :, :, :] += factor * td(
                operands_[2], tmp, axes=([0, 2], [0, 2])
            ).transpose(trans)
    #   elif subscripts in ("abcd,cefd->afeb",):
    #       # Should work for any contraction of type 'abcd,cefd->a...'.
    #       _, outscript = subscripts.split("->")
    #       trans = tuple("efb".index(char) for char in outscript[1:])
    #       # Do bcd,cedf->efb, the transpose efb and add it to output.
    #       for i in range(op0.shape[1]):
    #           tmp = td(op0[:, i, :], op1, axes=([0, 0]))
    #           arr[i, :, :, :] += factor * td(
    #               operands_[2], tmp, axes=([0, 3], [0, 2])
    #           ).transpose(trans)
    else:
        raise NotImplementedError(f"{subscripts}")
    try:
        del tmp
    except UnboundLocalError:
        pass
    gc.collect()


def cholesky_td_routine_abcd(
    subscripts,
    operands: Sequence[NDArray[np.float64]],
    arr,
    factor,
    save_memory,
):
    """Create a dense and transpose array from a Cholesky array using td.

    **Arguments:**
    * subscripts : str
    * operands : list of numpy.ndarray
    * arr : numpy.ndarray. The result of contraction is added to arr
    * factor : float or int
    * save_memory : boolean. If True a partial for loop implementation is
                    chosen. This option is only supported for specific
                    contractions: abcd->[any four index permutation],
    """
    op0: NDArray[np.float64] = operands[0]
    op1: NDArray[np.float64] = operands[1]
    input_scripts, _ = parse_subscripts(subscripts)
    # Should work for any contraction of type 'abcd->abcd'
    # That is, any permutation of input and output indices is allowed
    _, outscript = subscripts.split("->")
    i_s = input_scripts[0]
    if save_memory:
        # This subroutine should be used in cases numpy generates a copy of the
        # temporaray array. Note that transpositions do not generate copies
        # unless it is required. It seems to be required after a specific
        # array size is reached.
        if i_s not in ["abcd"]:
            raise ArgumentError(
                f"If save_memory=True, we only allow for abcd slices, got {i_s}"
            )
        outscript_ = outscript.replace("a", "")
        for i in range(op0.shape[1]):
            # slice_abcd generates indices of the form ":,i,:,:" for any valid
            # transposition
            slice_ = slice_abcd(outscript, i, "a")
            tmp = np.ascontiguousarray(td(op0[:, i, :], op1, axes=(0, 0)))
            # will return a view of the array if possible
            trans = ["cbd".index(char) for char in outscript_]
            tmp_t = np.transpose(tmp, axes=trans)
            arr[slice_] += factor * tmp_t
            del tmp, tmp_t
            gc.collect()
        return
    # resolve tensordot order: abcd translates to acbd (indices 1 and
    # 2 need to be swapped)
    td_result = f"{i_s[0]}{i_s[2]}{i_s[1]}{i_s[3]}"
    trans = [td_result.index(char) for char in outscript]
    # first create a dense array. This is expensive as it doubles the
    # memory. But it is much faster and cheaper than einsum...
    tmp = td(op0, op1, axes=(0, 0))
    # will return a view of the array if possible
    tmp_t = np.transpose(tmp, axes=trans)
    arr[:] += factor * tmp_t
    del tmp, tmp_t
    gc.collect()


#
# Parser
#


def parse_contract_input(subscripts, operands, kwargs):
    """Returns subscripts corresponding to operand._array
    and list of sliced arrays

    Arguments:
    subscripts - 'abcd,cd->ab'
    operands - list of NIndex objects without output operand
    """
    scripts, outscript = parse_subscripts(subscripts)
    assert len(scripts) == len(operands)  # Sanity check

    subscripts_ = ""
    operands_ = []
    i = 0

    for operand, script in zip(operands, scripts):
        scripts_ = operand.einsum_index(script)
        subscripts_ += scripts_ + ","
        for script_, array in zip(scripts_.split(","), operand.arrays):
            slice_ = [
                slice(
                    kwargs.get("begin" + str(i + script.find(char)), 0),
                    kwargs.get("end" + str(i + script.find(char)), None),
                    None,
                )
                for char in script_
            ]
            operands_.append(array[tuple(slice_)])
        i += len(script)

    subscripts_ = subscripts_[: len(subscripts_) - 1]
    if "->" in subscripts:
        subscripts_ += "->" + outscript

    return subscripts_, operands_


def reduce_subscript(subscript):
    """."""
    new = "".join(c for c, _ in groupby(subscript))
    return new


def slice_output(subscripts, kwargs):
    """Returns indices of the block of the output array based on the begin0,
    end0, begin1... keywords
    """
    inscripts, outscript = parse_subscripts(subscripts)
    outlen = len(outscript)
    start = len("".join(inscripts))
    slice_ = []
    for i in range(start, start + outlen):
        slice_.append(
            slice(
                kwargs.get("begin" + str(i), 0),
                kwargs.get("end" + str(i), None),
                None,
            )
        )
    return tuple(slice_)


def slice_abcd(subscript, index_, char):
    """Returns a tuple of indices of a four-index output array, where the axis
    corresponding to `char` is replaced by element `index_`.
    That is, we yield on of the following possibilities:
    `index_,:,:,:` (char=a), `:,index_,:,:` (char=b), `:,:,index_,:` (char=c),
    or `:,:,:,index_` (char=d)
    """
    char_index = subscript.find(char)
    slice_ = [slice(None), slice(None), slice(None)]
    slice_.insert(char_index, index_)
    return tuple(slice_)


def parse_subscripts(subscripts):
    """Returns list of subscripts and outscript.

    Examples:
        'abcd,cd->ba' -> ['abcd', 'cd'], 'ba'
        'abcd,cd' -> ['abcd', 'cd'], 'ab'
        'ab,ac,cd' -> ['ab', 'ac', 'cd'], 'bd'
    """
    if "->" in subscripts:
        inscripts, outscript = subscripts.split("->")
    else:
        outscript = ""
        inscripts = subscripts
    if "," in inscripts:
        scripts = inscripts.split(",")
    else:
        scripts = [inscripts]

    if outscript == "":
        inscripts = inscripts.replace(",", "")
        for char in inscripts:
            if inscripts.count(char) == 1:
                outscript += char
    return scripts, outscript


def get_outshape(subscripts, operands):
    """Returns shape matching the output of the operation or None if
    output is scalar.

    Arguments
    subscripts : str
        Specifies the subscripts for summation as comma separated subscript
        labels.

    operands : list of numpy.ndarray
    """
    scripts, outscript = parse_subscripts(subscripts)

    # Determine the default shape of the output
    shape = []
    for char in outscript:
        for script, operand in zip(scripts, operands):
            xdim = script.find(char)
            if xdim != -1:
                shape.append(operand.shape[xdim])
                break

    return tuple(shape)
