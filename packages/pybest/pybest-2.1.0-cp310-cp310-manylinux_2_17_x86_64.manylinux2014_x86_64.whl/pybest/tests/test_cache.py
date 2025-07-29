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


import uuid

import numpy as np
import pytest

from pybest import filemanager
from pybest.cache import Cache, JustOnceClass, just_once
from pybest.exceptions import ArgumentError
from pybest.linalg import (
    DenseFourIndex,
    DenseLinalgFactory,
    DenseOneIndex,
    DenseOrbital,
    DenseThreeIndex,
    DenseTwoIndex,
)


class Example(JustOnceClass):
    def __init__(self):
        JustOnceClass.__init__(self)
        self.counter = 0

    @just_once
    def inc(self):
        self.counter += 1

    def inc_bis(self):
        self.counter += 1


def test_just_once():
    e = Example()
    assert e.counter == 0
    e.inc()
    assert e.counter == 1
    e.inc()
    assert e.counter == 1
    e.clear()
    assert e.counter == 1
    e.inc()
    assert e.counter == 2
    e.inc()
    assert e.counter == 2
    e.inc_bis()
    assert e.counter == 3


@pytest.fixture
def cache_item():
    return Cache()


# Creates original Cache item
data_basic_1 = [
    (("foo", 5), "foo", 5),
    (("foo", 5), ("foo",), 5),
    ((("foo", 5)), "foo", 5),
    ((("foo", 5)), ("foo",), 5),
]

# Overwrites original Cache item
data_basic_2 = [
    (("foo", 4, 6), "foo", 5),
    (("foo", 4, 6), ("foo",), 5),
    (("foo", 4, 6), ("foo", 4), 6),
    (("foo", 4, 6), (("foo", 4)), 6),
]


@pytest.mark.parametrize("args2,load2,expected2", data_basic_2)
@pytest.mark.parametrize("args1,load1,expected1", data_basic_1)
def test_basics1(args1, load1, expected1, args2, load2, expected2, cache_item):
    cache_item.save(*args1)
    assert cache_item[load1] == expected1
    assert cache_item.load(load1) == expected1
    cache_item.save(*args2)
    assert cache_item[load2] == expected2
    assert cache_item.load(load2) == expected2
    assert len(cache_item) == 2
    cache_item.clear()
    assert len(cache_item._store) == 0
    assert len(cache_item) == 0


@pytest.mark.parametrize("args2,load2,expected2", data_basic_2)
@pytest.mark.parametrize("args1,load1,expected1", data_basic_1)
def test_basics2(args1, load1, expected1, args2, load2, expected2, cache_item):
    # resolve proper arguments from strings or tuples
    args1_ = load1 if isinstance(load1, str) else load1[0]
    args2_ = args2[:2]
    # write data from string
    cache_item[args1_] = expected1
    assert cache_item[load1] == expected1
    # overwrite data using tuple
    cache_item[args2_] = expected2
    assert cache_item[load2] == expected2
    assert len(cache_item) == 2
    cache_item.clear()
    assert len(cache_item._store) == 0
    assert len(cache_item) == 0


data_alloc = [
    ("bar", {"alloc": 5}, (5,), float),
    ("egg", {"alloc": (5, 10)}, (5, 10), float),
    ("foo", {"alloc": (5, 10, 2)}, (5, 10, 2), float),
]


@pytest.mark.parametrize("args,kwargs,shape,data_type", data_alloc)
def test_alloc1(args, kwargs, shape, data_type, cache_item):
    assert args not in cache_item
    # allocate new object
    tmp, new = cache_item.load(args, **kwargs)
    assert new
    assert (tmp == 0).all()
    assert tmp.shape == shape
    assert issubclass(tmp.dtype.type, data_type)
    assert args in cache_item
    assert "missingitem" not in cache_item
    # overwrite parts of the data
    tmp[3] = 1
    bis = cache_item.load(args)
    assert bis is tmp
    # check if Cache item values are properly overwritten
    assert (bis[3] == 1).all()
    # load already existing data (alloc should NOT mark object as new)
    tris, new = cache_item.load(args, **kwargs)
    assert not new
    assert tris is tmp


@pytest.mark.parametrize("args,kwargs,shape,data_type", data_alloc)
def test_alloc2(args, kwargs, shape, data_type, cache_item):
    ar1, new = cache_item.load(args, **kwargs)
    with pytest.raises(ArgumentError):
        # wrong alloc size
        cache_item.load(args, alloc=(10, 5))
    ar1[:] = 1.0
    cache_item.clear()
    assert args not in cache_item
    assert (ar1[:] == 0.0).all()
    # try to load it, while it is no longer valid
    with pytest.raises(KeyError):
        ar2 = cache_item.load(args)
    # properly load it anew
    ar2, new = cache_item.load(args, **kwargs)
    assert new
    assert ar2 is ar1  # still the same array, just cleared.
    assert args in cache_item
    # simple load should now work
    ar3 = cache_item.load(args)
    assert ar3 is ar1
    # clear again and use different alloc
    cache_item.clear()
    ar4, new = cache_item.load(args, alloc=(5, 1, 2))
    assert new
    assert ar4.shape == (5, 1, 2)
    assert ar4 is not ar1


data_keys = [
    (("a", 1), ("a", 1, 2), 2),
    (("foo", 1), ("foo", 1, 3), 3),
    (("foo", 1), ("foo", 1, "a"), "a"),
    (("foo", 1), ("foo", 1, "name"), "name"),
]


@pytest.mark.parametrize("keys,args,expected", data_keys)
def test_multiple_keys(keys, args, expected, cache_item):
    assert keys not in cache_item
    cache_item.save(*args)
    assert keys in cache_item
    assert cache_item.load(keys) == expected


def test_default(cache_item):
    # with scalars
    assert cache_item.load("egg", default=5)
    cache_item.save("egg", 5)
    assert cache_item.load("egg") == 5
    assert cache_item.load("egg", default=6) == 5
    cache_item.clear()
    assert cache_item.load("egg", default=6) == 6
    with pytest.raises(KeyError):
        cache_item.load("egg")
    cache_item.clear()
    assert cache_item.load("egg", default=None) is None
    with pytest.raises(KeyError):
        cache_item.load("egg")
    # with arrays
    cache_item.save("floep", np.array([3.1, 5.1]))
    assert (cache_item.load("floep", default=3) == np.array([3.1, 5.1])).all()
    cache_item.clear()
    assert cache_item.load("floep", default=3) == 3
    with pytest.raises(KeyError):
        cache_item.load("floep")


def test_dense_orbital(cache_item):
    lf = DenseLinalgFactory()
    exp1, new = cache_item.load("egg", alloc=(lf.create_orbital, 10, 9))
    assert new
    assert isinstance(exp1, DenseOrbital)
    assert exp1.nbasis == 10
    assert exp1.nfn == 9
    exp2 = cache_item.load("egg")
    assert exp1 is exp2
    exp3, new = cache_item.load("egg", alloc=(lf.create_orbital, 10, 9))
    assert not new
    assert exp1 is exp3
    # things that should not work
    with pytest.raises(ArgumentError):
        exp4, new = cache_item.load("egg", alloc=(lf.create_orbital, 5))
    with pytest.raises(ArgumentError):
        exp4, new = cache_item.load("egg", alloc=(lf.create_orbital, 10, 5))
    with pytest.raises(ArgumentError):
        exp4, new = cache_item.load("egg", alloc=5)
    # after clearing
    exp1.coeffs[1, 2] = 5.2
    cache_item.clear()
    assert exp1.coeffs[1, 2] == 0.0
    with pytest.raises(KeyError):
        exp4 = cache_item.load("egg")
    exp4, new = cache_item.load("egg", alloc=(lf.create_orbital, 10, 9))
    assert new
    assert exp1 is exp4
    exp5 = cache_item.load("egg")
    assert exp1 is exp5
    # default_nbasis
    lf.default_nbasis = 5
    with pytest.raises(ArgumentError):
        cache_item.load("egg", alloc=lf.create_orbital)
    cache_item.clear()
    exp6, new = cache_item.load("egg", alloc=lf.create_orbital)
    assert new
    assert exp5 is not exp6
    assert exp6.nbasis == 5
    assert exp6.nfn == 5


test_case_lf = [
    (
        DenseLinalgFactory(5),
        DenseOneIndex,
        DenseLinalgFactory(5).create_one_index,
        (2,),
        5.2,
    ),
    (
        DenseLinalgFactory(5),
        DenseTwoIndex,
        DenseLinalgFactory(5).create_two_index,
        (1, 2),
        5.2,
    ),
    (
        DenseLinalgFactory(5),
        DenseThreeIndex,
        DenseLinalgFactory(5).create_three_index,
        (1, 2, 3),
        5.2,
    ),
    (
        DenseLinalgFactory(5),
        DenseFourIndex,
        DenseLinalgFactory(5).create_four_index,
        (1, 2, 1, 2),
        5.2,
    ),
]


@pytest.mark.parametrize("LF_,NI,create,indices,value", test_case_lf)
def test_dense_index(LF_, NI, create, indices, value, cache_item):
    op1, new = cache_item.load("egg", alloc=(create, 10))
    assert new
    assert isinstance(op1, NI)
    assert op1.nbasis == 10
    op2 = cache_item.load("egg")
    assert op1 is op2
    op3, new = cache_item.load("egg", alloc=(create, 10))
    assert not new
    assert op1 is op3
    # things that should not work
    with pytest.raises(ArgumentError):
        op4, new = cache_item.load("egg", alloc=(create, 5))
    with pytest.raises(ArgumentError):
        op4, new = cache_item.load("egg", alloc=5)
    # after clearing
    op1.set_element(*indices, value)
    cache_item.clear()
    assert op1._array[indices] == 0.0
    with pytest.raises(KeyError):
        op4 = cache_item.load("egg")
    op4, new = cache_item.load("egg", alloc=(create, 10))
    assert new
    assert op1 is op4
    op5 = cache_item.load("egg")
    assert op1 is op5
    # default_nbasis
    with pytest.raises(ArgumentError):
        cache_item.load("egg", alloc=create)
    cache_item.clear()
    op6, new = cache_item.load("egg", alloc=create)
    assert new
    assert op5 is not op6
    assert op6.nbasis == 5
    # the new method of the two-index object
    op7, new = cache_item.load("bork", alloc=op6.new)
    assert new
    assert op5 is not op7
    assert op7.nbasis == 5


data_basic_exceptions_load = [
    (("boo",), {}, KeyError),
    (("bar",), {"alloc": 5}, ArgumentError),
    ((), {}, ArgumentError),
    (("foo",), {"sadfj": 4}, ArgumentError),
    (("foo",), {"alloc": 3, "default": 0}, ArgumentError),
    (("foo",), {"alloc": 3, "default": 0}, ArgumentError),
    (("foo",), {"jgfjg": 3, "default": 0}, ArgumentError),
]


@pytest.mark.parametrize("data,kwargs,error", data_basic_exceptions_load)
def test_basic_exceptions_load_clear(data, kwargs, error, cache_item):
    cache_item.save("bar", np.zeros(4, float))
    with pytest.raises(error):
        cache_item.load(*data, **kwargs)
    with pytest.raises(ArgumentError):
        # at least one arg is required
        cache_item.clear_item()


data_basic_exceptions_save = [
    ((), ArgumentError),
    (("one",), ArgumentError),
]


@pytest.mark.parametrize("data,error", data_basic_exceptions_save)
def test_basic_exceptions_save(data, error, cache_item):
    with pytest.raises(error):
        cache_item.save(*data)


def test_dealloc(cache_item):
    cache_item.save("foo", 5)
    cache_item.save("bar", 6)
    cache_item.clear_item("foo", dealloc=True)
    assert "foo" not in cache_item
    assert "bar" in cache_item
    assert len(cache_item._store) == 1
    cache_item.save("foo", 5)
    cache_item.clear(dealloc=True)
    assert "foo" not in cache_item
    assert "bar" not in cache_item
    assert len(cache_item._store) == 0


def test_save_unpack(cache_item):
    cache_item.save(("foo",), 5)
    assert "foo" in cache_item


data_iter = [
    (
        [("foo", 5), ("bar", 6)],
        {
            "keys": ["bar", "foo"],
            "values": [5, 6],
            "items": [("bar", 6), ("foo", 5)],
            "len": 2,
        },
    ),
    (
        [("foo", 5), ("bar", 6), ("bla", -1)],
        {
            "keys": ["bar", "bla", "foo"],
            "values": [-1, 5, 6],
            "items": [("bar", 6), ("bla", -1), ("foo", 5)],
            "len": 3,
        },
    ),
]


@pytest.mark.parametrize("data,expected", data_iter)
def test_iter(data, expected, cache_item):
    for data_ in data:
        cache_item.save(*data_)
    assert sorted(cache_item.iterkeys()) == expected["keys"]
    assert sorted(cache_item.values()) == expected["values"]
    assert sorted(cache_item.items()) == expected["items"]
    assert len(cache_item) == expected["len"]
    assert sorted(cache_item) == expected["keys"]


data_tags = [
    (
        [
            (("foo", 5), {"tags": "c"}),
            (("bar", 6), {}),
            (("egg", 7), {"tags": "op"}),
            (("spam", 8), {"tags": "co"}),
        ],
        {
            "keys": ["bar", "egg", "foo", "spam"],
            "values": [5, 6, 7, 8],
            "items": [("bar", 6), ("egg", 7), ("foo", 5), ("spam", 8)],
            "len": 4,
            "tags": {
                "c": {
                    "keys": ["foo", "spam"],
                    "values": [5, 8],
                    "items": [("foo", 5), ("spam", 8)],
                },
                "o": {
                    "keys": ["egg", "spam"],
                    "values": [7, 8],
                    "items": [("egg", 7), ("spam", 8)],
                },
                "a": {"keys": [], "values": [], "items": []},
            },
        },
    ),
]


@pytest.mark.parametrize("data,expected", data_tags)
def test_iter_tags(data, expected, cache_item):
    for data_ in data:
        cache_item.save(*data_[0], **data_[1])
    assert sorted(cache_item.iterkeys()) == expected["keys"]
    assert sorted(cache_item.values()) == expected["values"]
    assert sorted(cache_item.items()) == expected["items"]
    for tag, value in expected["tags"].items():
        assert sorted(cache_item.iterkeys(tags=tag)) == value["keys"]
        assert sorted(cache_item.values(tags=tag)) == value["values"]
        assert sorted(cache_item.items(tags=tag)) == value["items"]
    assert len(cache_item) == expected["len"]
    assert sorted(cache_item) == expected["keys"]


#
# Fixtures for testing tags
#
@pytest.fixture(
    params=[
        (("a", 5), {"tags": "ma"}),
        (("a", 5), {"tags": "a"}),
        (("a", 5), {"tags": "foo"}),
    ]
)
def tags(request):
    """Create collection of tags and assess"""
    cache_item = Cache()
    cache_item.save(*request.param[0], **request.param[1])
    return cache_item, request.param[1]["tags"]


# data_tags_load and data_tags_clear are to be combined with tags fixture
data_tags_load = [
    (("a",), {"tags": "a"}, 5, ArgumentError),
    (("a",), {"tags": "ab"}, 5, ArgumentError),
    (("a",), {"tags": "abc"}, 5, ArgumentError),
    (("a",), {"tags": "abc", "default": 5}, 5, ArgumentError),
]

data_tags_clear = [
    ("cd"),
    ("a"),
    ("m"),
    ("b"),
    ("fo"),
    ("foo"),
]


@pytest.mark.parametrize("tags_to_clear", data_tags_clear)
@pytest.mark.parametrize("data,kwargs,expected,error", data_tags_load)
def test_tags_load_clear(tags_to_clear, data, kwargs, expected, error, tags):
    cache_item, tag = tags
    # In a normal load call, the tags should not be allowed
    with pytest.raises(error):
        assert (
            cache_item.load(*data, **kwargs) == expected
        ), "tags kwarg should not be allowed"
    # clear with some tags taken from tags_to_clear
    # assume that tag is not to be cleared
    length = 1
    for char in tag:
        # if we want to clear, length will be 0, otherwise it remains unchanged
        length = 0 if char in tags_to_clear else length
    cache_item.clear(tags=tags_to_clear)
    assert len(cache_item) == length


data_tags_load_alloc = [
    (("tmp",), {"tags": "w", "alloc": 5}, ArgumentError),
    (("tmp",), {"tags": "aw", "alloc": 5}, ArgumentError),
    (("tmp",), {"tags": "ab", "alloc": 5}, ArgumentError),
]


@pytest.mark.parametrize("data,kwargs,error", data_tags_load_alloc)
def test_tags_load_alloc(data, kwargs, error, cache_item):
    cache_item.save("a", 5, tags="ab")
    # use in combination with alloc
    tmp1, new = cache_item.load("tmp", alloc=5, tags="qw")
    assert new
    # load again but no new object is created, alloc overwrites existing object
    tmp2, new = cache_item.load("tmp", alloc=5, tags="qw")
    assert not new, "Object should have been already present in the Cache"
    assert tmp1 is tmp2, "tmp1 and tmp2 should be the same object"
    with pytest.raises(error):
        cache_item.load(*data, **kwargs)
    # clear and write again, now tmp3 is new again but clear does not deallocate
    # only elements are set to zero
    cache_item.clear()
    tmp3, new = cache_item.load("tmp", alloc=5, tags="qw")
    assert new
    assert tmp1 is tmp3
    with pytest.raises(error):
        cache_item.load(*data, **kwargs)


#
# Fixtures for testing Cache class
#
@pytest.fixture(
    params=[
        ((10,), "ma"),
        ((10,), "ma"),
        ((10, 10), "mab"),
        ((10, 10, 10), "mabc"),
        ((10, 10, 10, 10), "mabcd"),
    ]
)
def dense_object(request):
    """Create some DenseIndex object of shape `dim` and with label `label`"""
    dim = request.param[0]
    label = request.param[1]
    if len(dim) == 1:
        dense_array = DenseOneIndex(*dim)
    elif len(dim) == 2:
        dense_array = DenseTwoIndex(*dim)
    elif len(dim) == 3:
        dense_array = DenseThreeIndex(*dim)
    elif len(dim) == 4:
        dense_array = DenseFourIndex(*dim)
    dense_array.randomize()
    dense_array.label = label
    return dense_array


def test_cache_dump(dense_object, cache_item):
    """Test dumping of _array attribute of stored values in a Cache instance."""
    key = dense_object.label
    # store data in Cache; note that a copy of data is stored
    cache_item.save(key, dense_object.copy(), tags="h")
    # access cached item
    data = cache_item.load(key)
    cache_item.dump(key)
    # filename is generated using data.label attribute where label is replaced
    # by a unique identifier in case of case-insesitive file system.
    filename = f"checkpoint_{data.label}.h5"
    filename = filemanager.temp_path(filename)
    # check if file exists
    assert filename.exists()
    # check if data is deleted
    assert not hasattr(data, "_array")
    assert not hasattr(data, "_array2")
    # other attributes have to be there
    assert hasattr(data, "label")


def test_cache_second_dump(dense_object, cache_item):
    """Test dumping of _array attribute of stored values in a Cache instance."""
    key = dense_object.label
    # store data in Cache; note that a copy of data is stored
    cache_item.save(key, dense_object.copy(), tags="h")
    # access cached item
    data = cache_item.load(key)
    cache_item.dump(key)
    label0 = data.label
    # second dump should not do anything and label will be the same
    cache_item.dump(key)
    label1 = data.label
    assert label0 == label1


def test_cache_dump_load(dense_object, cache_item):
    """Test dumping and loading of _array attribute of stored values in a Cache
    instance."""
    key = dense_object.label
    # store data in Cache; note that a copy of data is stored
    cache_item.save(key, dense_object.copy(), tags="h")
    # dump _array first
    cache_item.dump(key)
    # read data again
    data_ = cache_item.load(key)
    assert data_ == dense_object, "Dumped and loaded data differ"
    assert id(dense_object) != id(data_), "Different references expected"


dump_exceptions = [  # value, key0, key1, kwargs, exception raised
    (np.array([1]), "array", "array", {}, ValueError),
    ([1, 2, 3], "list", "list", {}, ValueError),
    (1, "int", "int", {}, ValueError),
    (None, "none", "none", {}, ValueError),
    (DenseOneIndex(10), "ma", "ma", {"foo": 1}, ArgumentError),
    (DenseOneIndex(10), "ma", "mb", {}, KeyError),
]


@pytest.mark.parametrize("data,key0,key1,kwargs,exception", dump_exceptions)
def test_cache_dump_exceptions(
    data, key0, key1, kwargs, exception, cache_item
):
    """Test all exceptions that should be raised."""
    # store data in Cache; we do not need to copy as tests will raise exceptions
    cache_item.save(key0, data, tags="h")
    with pytest.raises(exception):
        cache_item.dump(key1, **kwargs)


def test_cache_dump_force(dense_object, cache_item):
    """Test whether kwargs force works properly."""
    key = dense_object.label
    # store data in Cache; note that a copy of data is stored
    cache_item.save(key, dense_object.copy(), tags="h")
    # first get label (should be equal to the original one)
    label0 = cache_item.load(key).label
    assert label0 == dense_object.label, "Labels should not have changed"
    # dump first time: label needs to be set
    cache_item.dump(key, force=True)
    label1 = cache_item.load(key).label
    assert label1 != dense_object.label, "Labels have to differ"
    assert uuid.UUID(str(label1)), "Label has to have a unique ID"
    # dump second time: label should be the same
    cache_item.dump(key, force=True)
    # get label again
    label2 = cache_item.load(key).label
    assert label2 != dense_object.label, "Labels have to differ"
    assert label1 == label2, "Labels have to be identical"
