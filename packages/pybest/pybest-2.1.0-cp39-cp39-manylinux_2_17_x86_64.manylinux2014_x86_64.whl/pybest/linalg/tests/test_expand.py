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

from __future__ import annotations

from typing import Any, SupportsIndex

import numpy as np
import pytest

from pybest.linalg import DenseFourIndex, DenseLinalgFactory, DenseTwoIndex
from pybest.linalg.expand import (
    contract_operands,
    parse_expand_case,
    parse_repeated_expand_axes,
)

#
# General expand tests
#


@pytest.mark.parametrize(
    "subscripts,subscripts_contract,create_n_index",
    [
        ("aa->ab", "aa->a", DenseTwoIndex),
        ("aa->abc", "aa->a", DenseTwoIndex),
        ("bb->abc", "bb->b", DenseTwoIndex),
        ("cc->abc", "cc->c", DenseTwoIndex),
        ("bcbc->abc", "bcbc->bc", DenseFourIndex),
        ("acac->abc", "acac->ac", DenseFourIndex),
        ("abab->abc", "abab->ab", DenseFourIndex),
    ],
)
@pytest.mark.parametrize(
    "kwargs",
    [
        # NOTE: contract assigns for each repeated index the same range
        # Example: for aa->.. only begin0/end0 are used, for abab->.. begin0/end0
        # are used for a, begin1/end1 for b
        ({"begin0": 0, "end0": None, "begin1": 0}),
        ({"begin0": 3, "end0": 7, "begin1": 4}),
    ],
)
def test_contract_operands(
    subscripts: str,
    subscripts_contract: str,
    create_n_index: DenseTwoIndex | DenseFourIndex,
    kwargs: dict[str, Any],
):
    """Test pre-contraction of operands containing operations like aa->... or abab->..."""
    inscript, _ = subscripts.split("->")
    # Create the required DenseNIndex object
    dim = tuple([10 for _ in inscript])
    dense_n_index = create_n_index(*dim)
    # Assign random values
    dense_n_index.randomize()
    # Generte reference
    ref = dense_n_index.contract(subscripts_contract, **kwargs)
    # Prepare for function call
    operands = [dense_n_index, None]
    operands_ = [operands[0].array, None]
    output = contract_operands(subscripts, operands, operands_, kwargs)
    assert output.shape == ref.shape
    assert np.allclose(ref.array, output)


@pytest.mark.parametrize(
    "subscripts, expected",
    [
        ("a->aab", (2, "a")),
        ("abc->abca", (2, "abc")),
        ("bc->abca", (2, "bc")),
        ("db->abad", (2, "db")),
        ("ab->abad", (2, "ab")),
        ("ab->abcd", (1, "ab")),
        ("a->abcd", (1, "a")),
        ("aa->abc", (1, "a")),
        ("bb->abbc", (2, "b")),
        ("bc->abc", (1, "bc")),
    ],
)
def test_parse_expand_case(subscripts: str, expected: tuple[int, str]):
    """Distinguish between different expansion flavors, check modified inscripts."""
    output = parse_expand_case(subscripts)
    assert output == expected


@pytest.mark.parametrize(
    "inscript,outscript, expected",
    [
        ("a", "aab", ([0], [0, 1])),
        ("abc", "abca", ([0], [0, 3])),
        ("bc", "abca", ([-1], [0, 3])),
        ("db", "abad", ([-1], [0, 2])),
        ("ab", "abad", ([0], [0, 2])),
    ],
)
def test_parse_repeated_expand_axes(
    inscript: str, outscript: str, expected: tuple[list[int], list[int]]
):
    """Check axes of repeated indices."""
    output = parse_repeated_expand_axes(inscript, outscript)
    assert output == expected


#
# Test expansion cases (one example per case) using explicit loops
# to test validity of implementations for case 1 and 2.
# This should be a bulletproof test case as we consider general ranges
# for both input and output arguments.
#


@pytest.mark.parametrize(
    "nbasis,kwargs",
    [
        (
            4,
            {
                "begin0": 0,
                "end0": None,
                "begin1": 0,
                "end1": None,
                "begin2": 0,
                "end2": None,
            },
        ),
        (
            8,
            {
                "begin0": 1,
                "end0": 5,
                "begin1": 3,
                "end1": 7,
                "begin2": 2,
                "end2": 6,
            },
        ),
    ],
)
def test_expand_case_1_a_abc(nbasis: int, kwargs: dict[str, Any]):
    """Test one expansion case of type One2Three with and without ranges with loops."""
    lf = DenseLinalgFactory(nbasis)
    inp = lf.create_three_index(nbasis)
    one = lf.create_one_index(nbasis)

    inp.randomize()
    out = inp.copy()
    one.randomize()

    one.expand("a->abc", out=inp, factor=1.3, **kwargs)

    begin0 = kwargs.get("begin0", 0)
    begin1 = kwargs.get("begin1", 0)
    begin2 = kwargs.get("begin2", 0)
    for a in range(4):
        for b in range(4):
            for c in range(nbasis):
                out.array[a + begin1, b + begin2, c] += (
                    one.array[a + begin0] * 1.3
                )
    assert np.allclose(out.array, inp.array)


@pytest.mark.parametrize(
    "nbasis,kwargs",
    [
        (
            4,
            {
                "begin0": 0,
                "end0": None,
                "begin1": 0,
                "end1": None,
                "begin2": 0,
                "end2": None,
            },
        ),
        (
            8,
            {
                "begin0": 1,
                "end0": 5,
                "begin1": 3,
                "end1": 7,
                "begin2": 2,
                "end2": 6,
            },
        ),
    ],
)
def test_expand_case_2_a_aab(nbasis: int, kwargs: dict[str, Any]):
    """Test one expansion case of type One2Three with and without ranges with loops."""
    lf = DenseLinalgFactory(nbasis)
    inp = lf.create_three_index(nbasis)
    one = lf.create_one_index(nbasis)

    inp.randomize()
    out = inp.copy()
    one.randomize()

    one.expand("a->aab", out=inp, factor=1.3, **kwargs)

    begin0 = kwargs.get("begin0", 0)
    begin1 = kwargs.get("begin1", 0)
    begin2 = kwargs.get("begin2", 0)
    for a in range(4):
        for b in range(nbasis):
            out.array[a + begin1, a + begin2, b] += one.array[a + begin0] * 1.3
    assert np.allclose(out.array, inp.array)


#
# Expand for DenseTwoIndex tests
#


@pytest.mark.parametrize(
    "subscripts",
    ["a->ab", "b->ab"],
)
@pytest.mark.parametrize(
    "nbasis,kwargs",
    [
        (4, {"begin0": 0, "end0": None, "end1": None}),
        (8, {"begin0": 3, "end0": 7}),
    ],
)
def test_expand_output_args(
    subscripts: str, nbasis: int, kwargs: dict[str, Any]
):
    """Test output argument with and without ranges."""
    lf = DenseLinalgFactory(4)
    inp = lf.create_two_index()
    one = lf.create_one_index(nbasis)

    inp.randomize()
    inp_2 = inp.copy()
    one.randomize()

    # expand function call without out
    one.expand(subscripts, inp, factor=1.3, **kwargs)
    # expand function call with out
    one.expand(subscripts, out=inp_2, factor=1.3, **kwargs)

    assert np.allclose(inp.array, inp_2.array)


@pytest.mark.parametrize(
    "subscripts",
    ["a->ab", "b->ab"],
)
@pytest.mark.parametrize(
    "nbasis,kwargs,shift",
    [
        (4, {"begin0": 0, "end0": None, "end1": None}, 0),
        (8, {"begin0": 3, "end0": 7}, 3),
    ],
)
def test_expand_one_to_two(
    subscripts: str, nbasis: int, kwargs: dict[str, Any], shift: int
):
    """Test expansion of type One2Two with and without ranges."""
    lf = DenseLinalgFactory(4)
    inp = lf.create_two_index()
    one = lf.create_one_index(nbasis)

    inp.randomize()
    out = inp.copy()
    one.randomize()

    # expand function call
    one.expand(subscripts, out=inp, factor=1.3, **kwargs)

    # Explicit loop
    char, outscript = subscripts.split("->")
    index = outscript.find(char)
    begin0 = kwargs.get("begin0", 0)
    end0 = kwargs.get("end0", nbasis - shift)
    for i in range(4):
        ranges: SupportsIndex | slice = [i]
        ranges.insert(index, slice(None))
        out.array[tuple(ranges)] += one.array[begin0:end0] * 1.3
    assert np.allclose(out.array, inp.array)


#
# DenseThreeIndex tests
#


@pytest.mark.parametrize(
    "subscripts",
    ["a->abc", "b->abc", "c->abc"],
)
@pytest.mark.parametrize(
    "nbasis,kwargs,shift",
    [
        (4, {"begin0": 0, "end0": None, "end1": None}, 0),
        (8, {"begin0": 3, "end0": 7}, 3),
    ],
)
def test_expand_one_to_three(
    subscripts: str, nbasis: int, kwargs: dict[str, Any], shift: int
):
    """Test expansion of type One2Three with and without ranges."""
    lf = DenseLinalgFactory(4)
    inp = lf.create_three_index()
    one = lf.create_one_index(nbasis)

    inp.randomize()
    out = inp.copy()
    one.randomize()

    one.expand(subscripts, out=inp, factor=1.3, **kwargs)

    begin0 = kwargs.get("begin0", 0)
    end0 = kwargs.get("end0", nbasis - shift)
    char, outscript = subscripts.split("->")
    index = outscript.find(char)
    for i in range(4):
        for j in range(4):
            ranges: SupportsIndex | slice = [i, j]
            ranges.insert(index, slice(None))
            out.array[tuple(ranges)] += one.array[begin0:end0] * 1.3
    assert np.allclose(out.array, inp.array)


@pytest.mark.parametrize(
    "subscripts",
    ["a->aab"],
)
@pytest.mark.parametrize(
    "nbasis,kwargs,shift",
    [
        (4, {"begin0": 0, "end0": None, "end1": None}, 0),
        (8, {"begin0": 3, "end0": 7}, 3),
    ],
)
def test_expand_one_to_three_v2(
    subscripts: str, nbasis: int, kwargs: dict[str, Any], shift: int
):
    """Test expansion of type One2Three with and without ranges."""
    lf = DenseLinalgFactory(4)
    inp = lf.create_three_index()
    one = lf.create_one_index(nbasis)

    inp.randomize()
    out = inp.copy()
    one.randomize()

    char, outscript = subscripts.split("->")
    for letter in char:
        # Search for doubly-occuring letters
        if outscript.count(letter) == 2:
            break
    index_out = [i for i, letter_ in enumerate(outscript) if letter_ == letter]
    index_inp = char.find(letter)

    one.expand(subscripts, out=inp, factor=1.3, **kwargs)

    for i in range(4):
        ranges_out: SupportsIndex | slice = [
            slice(None),
            slice(None),
            slice(None),
        ]
        ranges_out[index_out[0]] = i
        ranges_out[index_out[1]] = i
        ranges_inp: SupportsIndex | slice = [slice(None)]
        ranges_inp[index_inp] = i + shift
        out.array[tuple(ranges_out)] += one.array[tuple(ranges_inp)] * 1.3
    assert np.allclose(out.array, inp.array)


@pytest.mark.parametrize(
    "subscripts",
    ["bcbc->abc", "acac->abc", "abab->abc"],
)
@pytest.mark.parametrize(
    "nbasis,kwargs",
    [
        (4, {"begin0": 0, "end0": None, "end1": None}),
        (
            8,
            {
                "begin0": 3,
                "end0": 7,
                "begin1": 3,
                "end1": 7,
                "begin2": 3,
                "end2": 7,
                "begin3": 3,
                "end3": 7,
            },
        ),
    ],
)
def test_expand_four_to_three(
    subscripts: str, nbasis: int, kwargs: dict[str, Any]
):
    """Test expansion of type Four2Three with and without ranges."""
    lf = DenseLinalgFactory(4)
    inp = lf.create_three_index()
    four = lf.create_four_index(nbasis)

    inp.randomize()
    out = inp.copy()
    four.randomize()

    char, outscript = subscripts.split("->")
    # Get contracted scripts bcbc -> bc
    char_2n = "".join(dict.fromkeys(char))

    index = [i for i, letter in enumerate(outscript) if letter in char_2n]
    index = index if char_2n[0] < char_2n[1] else index[::-1]

    four.expand(subscripts, out=inp, factor=1.3, **kwargs)

    # First, contract with einsum, example "bcbc" + "->" + "bc"
    four_contracted = four.contract(char + "->" + char_2n, **kwargs)
    # Second, expand
    for i in range(4):
        for j in range(4):
            ranges: SupportsIndex | slice = [
                slice(None),
                slice(None),
                slice(None),
            ]
            ranges[index[0]] = i
            ranges[index[1]] = j
            out.array[tuple(ranges)] += four_contracted.array[i, j] * 1.3
    assert np.allclose(out.array, inp.array)


@pytest.mark.parametrize(
    "subscripts",
    ["ac->abc", "bc->abc", "ab->abc", "cb->abc", "ca->abc"],
)
@pytest.mark.parametrize(
    "nbasis,kwargs,shift",
    [
        (4, {"begin0": 0, "end0": None, "end1": None}, 0),
        (8, {"begin0": 3, "end0": 7, "end1": 4}, 4),
    ],
)
def test_expand_two_to_three(
    subscripts: str, nbasis: int, kwargs: dict[str, Any], shift: int
):
    """Test expansion of type Two2Three with and without ranges."""
    lf = DenseLinalgFactory(4)
    inp = lf.create_three_index()
    two = lf.create_two_index(nbasis)

    inp.randomize()
    out = inp.copy()
    two.randomize()

    char, outscript = subscripts.split("->")
    trans = tuple([char.find(i) for i in outscript if char.find(i) != -1])
    (index_in,) = (
        i for i, letter_ in enumerate(outscript) if letter_ not in char
    )

    two.expand(subscripts, out=inp, factor=1.3, **kwargs)

    begin0 = kwargs.get("begin0", 0)
    end0 = kwargs.get("end0", nbasis - shift)
    begin1 = kwargs.get("begin1", 0)
    end1 = kwargs.get("end1", nbasis - shift)
    for i in range(4):
        ranges_out: SupportsIndex | slice = [
            slice(None),
            slice(None),
            slice(None),
        ]
        ranges_out[index_in] = i
        out.array[tuple(ranges_out)] += (
            two.array[begin0:end0, begin1:end1].transpose(trans) * 1.3
        )
    assert np.allclose(out.array, inp.array)


@pytest.mark.parametrize(
    "subscripts", ["ab->aab", "aa->abc", "cc->abc", "bb->abc"]
)
@pytest.mark.parametrize(
    "nbasis,kwargs,shift",
    [
        (4, {"begin0": 0, "end0": None, "end1": None}, 0),
        (8, {"begin0": 3, "end0": 7, "begin1": 3, "end1": 7}, 4),
    ],
)
def test_expand_two_to_three_v2(
    subscripts: str, nbasis: int, kwargs: dict[str, Any], shift: int
):
    """Test expansion of type Two2Three with and without ranges."""
    lf = DenseLinalgFactory(4)
    inp = lf.create_three_index()
    two = lf.create_two_index(nbasis)

    inp.randomize()
    out = inp.copy()
    two.randomize()

    char, outscript = subscripts.split("->")
    for letter in char:
        # Search for doubly-occuring letters
        # Case ab->aab etc.
        if outscript.count(letter) == 2:
            index_out = [
                i for i, letter_ in enumerate(outscript) if letter_ == letter
            ]
            index_inp = [
                char.find(letter),
            ]
            break
        # Case aa->abc etc.
        elif char.count(letter) == 2:
            index_inp = [
                i for i, letter_ in enumerate(char) if letter_ == letter
            ]
            index_out = [
                outscript.find(letter),
            ]
            break

    two.expand(subscripts, out=inp, factor=1.3, **kwargs)

    begin0 = kwargs.get("begin0", 0)
    end0 = kwargs.get("end0", nbasis - shift)
    begin1 = kwargs.get("begin1", 0)
    end1 = kwargs.get("end1", nbasis - shift)
    for i in range(4):
        ranges_out: SupportsIndex | slice = [
            slice(None),
            slice(None),
            slice(None),
        ]
        # Allow for ...->aab
        for ind in index_out:
            ranges_out[ind] = i
        ranges_inp: SupportsIndex | slice = [
            slice(begin0, end0),
            slice(begin1, end1),
        ]
        ranges_inp_slice: SupportsIndex | slice = [
            slice(None),
            slice(None),
        ]
        # Allow for aa->ab..
        for ind in index_inp:
            ranges_inp_slice[ind] = i
        out.array[tuple(ranges_out)] += (
            (two.array[tuple(ranges_inp)])[tuple(ranges_inp_slice)] * 1.3
        )
    assert np.allclose(out.array, inp.array)


#
# DenseFourIndex tests
#


@pytest.mark.parametrize(
    "subscripts",
    [
        "ab->abab",
        "ab->abba",
        "ab->baab",
        "ab->baba",
        "ab->aabb",
        "ab->bbaa",
    ],
)
@pytest.mark.parametrize(
    "nbasis,kwargs,shift",
    [
        (4, {}, 0),
        (
            8,
            {
                "begin0": 3,
                "end0": 7,
                "begin1": 3,
                "end1": 7,
                "begin2": 3,
                "end2": 7,
                "begin3": 3,
                "end3": 7,
                "begin4": 3,
                "end4": 7,
                "begin5": 3,
                "end5": 7,
            },
            4,
        ),
    ],
)
def test_expand_diagonal(
    subscripts: str, nbasis: int, kwargs: dict[str, Any], shift: int
):
    """Test expansion of diagonal type with and without ranges."""
    lf = DenseLinalgFactory(4)
    inp = lf.create_four_index(nbasis)
    two = lf.create_two_index(nbasis)

    inp.randomize()
    out = inp.copy()
    two.randomize()

    two.expand(subscripts, out=inp, factor=1.3, **kwargs)

    begin0 = kwargs.get("begin0", 0)
    end0 = kwargs.get("end0", nbasis - shift)
    begin1 = kwargs.get("begin1", 0)
    end1 = kwargs.get("end1", nbasis - shift)
    for i in range(begin0, end0):
        for a in range(begin1, end1):
            if subscripts == "ab->abab":
                out.array[i, a, i, a] += two.array[i, a] * 1.3
            if subscripts == "ab->abba":
                out.array[i, a, a, i] += two.array[i, a] * 1.3
            if subscripts == "ab->baab":
                out.array[a, i, i, a] += two.array[i, a] * 1.3
            if subscripts == "ab->baba":
                out.array[a, i, a, i] += two.array[i, a] * 1.3
            if subscripts == "ab->aabb":
                out.array[i, i, a, a] += two.array[i, a] * 1.3
            if subscripts == "ab->bbaa":
                out.array[a, a, i, i] += two.array[i, a] * 1.3
    assert np.allclose(out.array, inp.array)


@pytest.mark.parametrize(
    "subscripts", ["a->abcd", "b->abcd", "c->abcd", "d->abcd"]
)
@pytest.mark.parametrize(
    "nbasis,kwargs,shift",
    [
        (4, {"begin0": 0, "end0": None, "end1": None}, 0),
        (8, {"begin0": 3, "end0": 7}, 4),
    ],
)
def test_expand_one_to_four(
    subscripts: str, nbasis: int, kwargs: dict[str, Any], shift: int
):
    """Test expansion of type One2Four with and without ranges."""
    # test in detail for 0-2
    lf = DenseLinalgFactory(4)
    inp = lf.create_four_index()
    one = lf.create_one_index(nbasis)

    inp.randomize()
    out = inp.copy()
    one.randomize()

    one.expand(subscripts, out=inp, factor=1.3, **kwargs)
    char, outscript = subscripts.split("->")
    index = outscript.find(char)

    begin0 = kwargs.get("begin0", 0)
    end0 = kwargs.get("end0", nbasis - shift)
    for i in range(4):
        for j in range(4):
            for k in range(4):
                ranges: SupportsIndex | slice = [i, j, k]
                ranges.insert(index, slice(None))
                out.array[tuple(ranges)] += one.array[begin0:end0] * 1.3
    assert np.allclose(out.array, inp.array)


@pytest.mark.parametrize(
    "subscripts",
    ["a->abac", "b->abcb", "b->abbc"],
)
@pytest.mark.parametrize(
    "nbasis,kwargs,shift",
    [
        (4, {"begin0": 0, "end0": None, "end1": None}, 0),
        (8, {"begin0": 3, "end0": 7}, 3),
    ],
)
def test_expand_one_to_four_v2(
    subscripts: str, nbasis: int, kwargs: dict[str, Any], shift: int
):
    """Test expansion of type One2Four with and without ranges."""
    lf = DenseLinalgFactory(4)
    inp = lf.create_four_index()
    one = lf.create_one_index(nbasis)

    inp.randomize()
    out = inp.copy()
    one.randomize()

    one.expand(subscripts, out=inp, factor=1.3, **kwargs)

    char, outscript = subscripts.split("->")
    index = [i for i, letter in enumerate(outscript) if letter == char]
    for i in range(4):
        ranges: SupportsIndex | slice = [
            slice(None),
            slice(None),
            slice(None),
            slice(None),
        ]
        for index_ in index:
            ranges[index_] = i
        out.array[tuple(ranges)] += one.array[i + shift] * 1.3
    assert np.allclose(out.array, inp.array)


@pytest.mark.parametrize(
    "subscripts",
    [
        "bc->abac",
        "ac->abbc",
        "bc->abca",
        "ac->abcb",
    ],
)
@pytest.mark.parametrize(
    "nbasis,kwargs,shift",
    [
        (4, {"begin0": 0, "end0": None, "end1": None}, 0),
        (8, {"begin0": 3, "end0": 7, "end1": 4}, 4),
    ],
)
def test_expand_two_to_four(
    subscripts: str, nbasis: int, kwargs: dict[str, Any], shift: int
):
    """Test expansion of type Two2Four with and without ranges."""
    lf = DenseLinalgFactory(4)
    inp = lf.create_four_index()
    two = lf.create_two_index(nbasis)

    inp.randomize()
    out = inp.copy()
    two.randomize()

    two.expand(subscripts, out=inp, factor=1.3, **kwargs)

    begin0 = kwargs.get("begin0", 0)
    end0 = kwargs.get("end0", nbasis - shift)
    begin1 = kwargs.get("begin1", 0)
    end1 = kwargs.get("end1", nbasis - shift)
    char, outscript = subscripts.split("->")
    index = [i for i, letter in enumerate(outscript) if letter not in char]
    for i in range(4):
        ranges: SupportsIndex | slice = [
            slice(None),
            slice(None),
            slice(None),
            slice(None),
        ]
        for index_ in index:
            ranges[index_] = i
        ranges_inp: SupportsIndex | slice = [
            slice(begin0, end0),
            slice(begin1, end1),
        ]
        out.array[tuple(ranges)] += two.array[tuple(ranges_inp)] * 1.3
    assert np.allclose(out.array, inp.array)


@pytest.mark.parametrize(
    "subscripts",
    [
        "ab->abcd",
        "bc->abcd",
        "cd->abcd",
        "cb->abcd",
        "ad->abcd",
        "ac->abcd",
        "ca->abcd",
        "bd->abcd",
        "db->abcd",
    ],
)
@pytest.mark.parametrize(
    "nbasis,kwargs,shift",
    [
        (4, {"begin0": 0, "end0": None, "end1": None}, 0),
        (8, {"begin0": 3, "end0": 7, "end1": 4}, 3),
    ],
)
def test_expand_two_to_four_v2(
    subscripts: str, nbasis: int, kwargs: dict[str, Any], shift: int
):
    """Test expansion of type Two2Four with and without ranges."""
    lf = DenseLinalgFactory(4)
    inp = lf.create_four_index()
    two = lf.create_two_index(nbasis)

    inp.randomize()
    out = inp.copy()
    two.randomize()

    char, outscript = subscripts.split("->")
    index = [i for i, letter in enumerate(outscript) if letter in char]
    index = index if char[0] < char[1] else index[::-1]

    two.expand(subscripts, out=inp, factor=1.3, **kwargs)
    for i in range(4):
        for j in range(4):
            ranges: SupportsIndex | slice = [
                slice(None),
                slice(None),
                slice(None),
                slice(None),
            ]
            ranges[index[0]] = i
            ranges[index[1]] = j
            out.array[tuple(ranges)] += two.array[i + shift, j] * 1.3
    assert np.allclose(out.array, inp.array)


@pytest.mark.parametrize(
    "subscripts",
    [
        "abc->abac",
        "abc->acbc",
        "abc->abca",
        "abc->abcb",
        "abc->aabc",
        "abc->abbc",
    ],
)
@pytest.mark.parametrize(
    "nbasis,kwargs,shift",
    [
        (4, {"begin0": 0, "end0": None, "end1": None}, 0),
        (8, {"begin0": 3, "end0": 7, "end1": 4, "end2": 4}, 4),
    ],
)
def test_expand_three_to_four(
    subscripts: str, nbasis: int, kwargs: dict[str, Any], shift: int
):
    """Test expansion of type Three2Four with and without ranges."""
    lf = DenseLinalgFactory(4)
    inp = lf.create_four_index()
    three = lf.create_three_index(nbasis)

    inp.randomize()
    out = inp.copy()
    three.randomize()

    char, outscript = subscripts.split("->")
    for letter in char:
        # Search for doubly-occuring letters
        if outscript.count(letter) == 2:
            break
    index_out = [i for i, letter_ in enumerate(outscript) if letter_ == letter]
    index_inp = char.find(letter)

    three.expand(subscripts, out=inp, factor=1.3, **kwargs)

    begin0 = kwargs.get("begin0", 0)
    end0 = kwargs.get("end0", nbasis - shift)
    begin1 = kwargs.get("begin1", 0)
    end1 = kwargs.get("end1", nbasis - shift)
    begin2 = kwargs.get("begin2", 0)
    end2 = kwargs.get("end2", nbasis - shift)
    for i in range(4):
        ranges_out: SupportsIndex | slice = [
            slice(None),
            slice(None),
            slice(None),
            slice(None),
        ]
        ranges_out[index_out[0]] = i
        ranges_out[index_out[1]] = i
        ranges_inp: SupportsIndex | slice = [
            slice(begin0, end0),
            slice(begin1, end1),
            slice(begin2, end2),
        ]
        ranges_slice: SupportsIndex | slice = [
            slice(None),
            slice(None),
            slice(None),
        ]
        ranges_slice[index_inp] = i
        out.array[tuple(ranges_out)] += (
            (three.array[tuple(ranges_inp)])[tuple(ranges_slice)] * 1.3
        )
    assert np.allclose(out.array, inp.array)


@pytest.mark.parametrize(
    "subscripts",
    [
        "bcd->abcd",
        "acd->abcd",
        "abd->abcd",
        "abc->abcd",
        "acb->abcd",
    ],
)
@pytest.mark.parametrize(
    "nbasis,kwargs,shift",
    [
        (4, {"begin0": 0, "end0": None, "end1": None}, 0),
        (8, {"begin0": 3, "end0": 7, "end1": 4, "end2": 4}, 4),
    ],
)
def test_expand_three_to_four_v2(
    subscripts: str, nbasis: int, kwargs: dict[str, Any], shift: int
):
    """Test expansion of type Three2Four with and without ranges."""
    lf = DenseLinalgFactory(4)
    inp = lf.create_four_index()
    three = lf.create_three_index(nbasis)

    inp.randomize()
    out = inp.copy()
    three.randomize()

    char, outscript = subscripts.split("->")
    trans = tuple([char.find(i) for i in outscript if char.find(i) != -1])
    (index_in,) = (
        i for i, letter_ in enumerate(outscript) if letter_ not in char
    )

    three.expand(subscripts, out=inp, factor=1.3, **kwargs)

    begin0 = kwargs.get("begin0", 0)
    end0 = kwargs.get("end0", nbasis - shift)
    begin1 = kwargs.get("begin1", 0)
    end1 = kwargs.get("end1", nbasis - shift)
    begin2 = kwargs.get("begin2", 0)
    end2 = kwargs.get("end2", nbasis - shift)
    for i in range(4):
        ranges_out: SupportsIndex | slice = [
            slice(None),
            slice(None),
            slice(None),
            slice(None),
        ]
        ranges_inp: SupportsIndex | slice = [
            slice(begin0, end0),
            slice(begin1, end1),
            slice(begin2, end2),
        ]
        ranges_out[index_in] = i
        out.array[tuple(ranges_out)] += (
            three.array[tuple(ranges_inp)].transpose(trans) * 1.3
        )
    assert np.allclose(out.array, inp.array)
