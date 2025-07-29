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


import pytest

from pybest.iodata import IOData
from pybest.linalg import DenseOrbital, DenseTwoIndex
from pybest.utility.unmask_data import unmask, unmask_orb


def test_unmask():
    iodata = IOData(kwarg1="hello", kwarg2=[0, 1], kwarg3=1410)
    not_iodata = DenseTwoIndex(nbasis=1, label="kwarg3")
    assert unmask("kwarg3", iodata) == 1410
    assert isinstance(unmask("kwarg3", iodata, not_iodata), DenseTwoIndex)


orb_a1 = DenseOrbital(nbasis=20, nfn=20)
orb_b1 = DenseOrbital(nbasis=30, nfn=30)
orb_a2 = DenseOrbital(nbasis=23, nfn=23)
orb_b2 = DenseOrbital(nbasis=33, nfn=33)
iodata = IOData(orb_a=orb_a2, orb_b=orb_b2)

test_unmask_cases = [
    ((orb_a1,), {}, {"orb1": orb_a1, "len": 1}),
    ((orb_a1, orb_b1), {}, {"orb1": orb_a1, "orb2": orb_b1, "len": 2}),
    ((orb_b1, orb_a1), {}, {"orb1": orb_b1, "orb2": orb_a1, "len": 2}),
    (
        (),
        {"orb_a": orb_a1, "orb_b": orb_b1},
        {"orb1": orb_a1, "orb2": orb_b1, "len": 2},
    ),
    ((orb_a1,), {"orb_a": orb_a2}, {"orb1": orb_a2, "len": 1}),
    ((orb_a1, orb_b1), {"orb_a": orb_a2}, {"orb1": orb_a2, "len": 1}),
    (
        (orb_a1,),
        {"orb_a": orb_a2, "orb_b": orb_b2},
        {"orb1": orb_a2, "orb_b": orb_b2, "len": 2},
    ),
    ((iodata,), {}, {"orb1": orb_a2, "orb2": orb_b2, "len": 2}),
    ((iodata, orb_a1), {}, {"orb1": orb_a1, "len": 1}),
    ((iodata,), {"orb_a": orb_a1}, {"orb1": orb_a1, "len": 1}),
]


@pytest.mark.parametrize("args, kwargs, result", test_unmask_cases)
def test_unmask_orb(args, kwargs, result):
    assert unmask_orb(*args, **kwargs)[0] == result["orb1"]
    assert len(unmask_orb(*args, **kwargs)) == result["len"]
    if hasattr(result, "orb2"):
        assert unmask_orb(*args, **kwargs)[1] == result["orb2"]


test_cases = [
    ("chplus", [0.0, 0.0, 0.0]),
    ("nh3", [0.0, 0.0, -0.3089891187736095]),
]
