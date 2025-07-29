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

# 2025: Originally written by Katharina Boguslawski
#
# Detailed changes (see also CHANGELOG):

"""Functions used in NIndex.expand function"""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

#
# Tested cases for expand method. If a new flavor is added, a test has to be
# added to test_expand.py
#

expand_valid_cases = [
    # One2Two
    "a->ab",
    "b->ab",
    # One2Three
    "a->abc",
    "b->abc",
    "c->abc",
    "a->aab",
    # One2Four
    "a->abcd",
    "b->abcd",
    "c->abcd",
    "d->abcd",
    "a->abac",
    "b->abcb",
    "b->abbc",
    # Two2Three
    "ab->abc",
    "ac->abc",
    "bc->abc",
    "ab->aab",
    "aa->abc",
    "bb->abc",
    "cc->abc",
    "cb->abc",
    "ca->abc",
    # Two2Four
    "ab->abcd",
    "bc->abcd",
    "cd->abcd",
    "cb->abcd",
    "ac->abcd",
    "ad->abcd",
    "ca->abcd",
    "bd->abcd",
    "db->abcd",
    "ac->abbc",
    "ac->abcb",
    "bc->abac",
    "bc->abca",
    "ab->abab",
    "ab->abba",
    "ab->baab",
    "ab->baba",
    "ab->aabb",
    "ab->bbaa",
    # Three2Four
    "abc->abac",
    "abc->acbc",
    "abc->abca",
    "abc->abcb",
    "abc->aabc",
    "abc->abbc",
    "bcd->abcd",
    "acd->abcd",
    "abd->abcd",
    "abc->abcd",
    "acb->abcd",
    # Four2Three
    "abab->abc",
    "acac->abc",
    "bcbc->abc",
]

expand_diagonal_cases = [
    "ab->abab",
    "ab->abba",
    "ab->baab",
    "ab->baba",
    "ab->aabb",
    "ab->bbaa",
]

#
# Routines
#


def contract_operands(
    subscripts: str,
    operands: Any,
    operands_: list[NDArray[np.float64]],
    kwargs: dict[str, Any],
) -> NDArray[np.float64]:
    """Contract repeated indices of operands of input array.

    Args:
        subscripts (str): contraction recipe using np.einsum notation. Example: aa->a
        operands (NIndexObject): list of NIndex objects without output operand.
                                 The first operand that is to be reduced
        operands_ (list[NDArray[np.float64]]): if nothing is to be done, operands_[0] is returned
        kwargs (dict[str, Any]): contains ranges to generate proper views for contraction

    Returns:
        NDArray[np.float64]: final array used in expansion procedure
    """
    inscript, _ = subscripts.split("->")
    # Check for unique/distinct characters in input scripts
    inscript_unique_char = np.unique(list(inscript))
    # If we have repeating characters in input string, we contract first
    # Example: aa..->.. is translated to a..->..
    if len(inscript_unique_char) < len(list(inscript)):
        inscript_contraction = inscript + "->" + "".join(inscript_unique_char)
        inp = operands[0].contract(inscript_contraction, **kwargs)
        return inp.array
    return operands_[0]


#
# Parser
#


def parse_expand_case(subscripts: str) -> None | tuple[int, str]:
    """

    Args:
        subscripts (str): Recipe in np.einsum notation. Example a->aab or a->ab

    Returns:
        None | list[int, str]: If expansion method is supported, a list is returned.
                               First element of the list labels the expanions flavor
                               (internal labeling), the second updated the input
                               scripts if we have repeating indices in the input
                               array.
                               If recipe is unsupported, None is returned.
    """
    inscript, outscript = subscripts.split("->")
    # Check for unique/distinct characters in input scripts
    inscript_unique_char = np.unique(list(inscript))
    # If we have repeating characters in input string, we contract first
    # Example: aa..->.. is translated to a..->..
    if len(inscript_unique_char) < len(list(inscript)):
        inscript = "".join(inscript_unique_char)

    # Check for repeated characters
    count_repeating_out = False
    count_repeating_inp = False
    repeating_char_inp = []
    repeating_char_out = []
    for letter in inscript:
        # Search for doubly-occuring letters
        if inscript.count(letter) > 1:
            count_repeating_inp = True
            repeating_char_inp.append(letter)
            break
    for letter in outscript:
        # Search for doubly-occuring letters
        if outscript.count(letter) > 1:
            count_repeating_out = True
            repeating_char_out.append(letter)
            break

    if (not count_repeating_inp) and (not count_repeating_out):
        return 1, inscript
    elif count_repeating_inp or count_repeating_out:
        return 2, inscript
    return None


def parse_repeated_expand_axes(
    inscript: str, outscript: str
) -> tuple[list[int], list[int]]:
    """Resolve input and output axes along which expansion is performed.
    We collect those that contain repeated indices. If not present, -1 is added.
    We assume the following:
        - inscript/outscript pair has repeating axes
        - only one axis can be repeated, the last repeated one is selected. Example:
            * ..->abbc is supported
            * ..->abba is not supported

    Examples:
        - a->aab: index_inp = [0], index_out = [0,1]
        - abc->abca: index_inp = [0], index_out = [0, 3]
        - bc->abca: index_inp = [-1], index_out =  [0, 3]

    Args:
        inscript (str): a np.einsum-type subscript string for the input array
        outscript (str): a np.einsum-type subscript string for the output array

    Returns:
        tuple[list[int], list[int]]: a list containing the repeated axes for
                                     input and output array. If repeated axis is
                                     not present, -1 is stored
    """
    # Search for repeating index/letter
    # Check if inscript and outscript share repeating letters/indices
    common_letters = [i for i in inscript if i in outscript]
    common_letters_repeated_inp = None
    common_letters_repeated_out = None
    for letter in common_letters:
        if inscript.count(letter) > 1:
            common_letters_repeated_inp = letter
        if outscript.count(letter) > 1:
            common_letters_repeated_out = letter
    # Take the scrips that feature repeating indices (should always be outscript)
    scripts_ = (
        inscript if common_letters_repeated_inp is not None else outscript
    )
    # Double check (this line should not do anything due to the contraction of
    # the input arrays, like aa->a, before their expansion, like aa(->a)->ab)
    scripts_ = (
        outscript if common_letters_repeated_out is not None else scripts_
    )
    # Looping over the proper scripts allows us to decide where indices
    # are repeated (inscripts [aa->abc] or outscripts [a->aab]) to
    # select the proper ranges
    for letter in scripts_:
        # Case ab->aab etc.
        if outscript.count(letter) == 2:
            # Get position of repeating indices contained in inscript
            # and outscript
            index_out = [
                i for i, letter_ in enumerate(outscript) if letter_ == letter
            ]
            index_inp = [
                inscript.find(letter),
            ]
            break
        # Case aa->abc etc.
        # We never enter this case, but keep it for reasons of completeness
        elif inscript.count(letter) == 2:
            index_inp = [
                i for i, letter_ in enumerate(inscript) if letter_ == letter
            ]
            index_out = [
                outscript.find(letter),
            ]
            break
    return index_inp, index_out
