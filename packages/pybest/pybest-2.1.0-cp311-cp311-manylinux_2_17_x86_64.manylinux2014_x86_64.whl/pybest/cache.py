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
# This implementation has been taken from `Horton 2.0.0`.
# However, this file has been updated and debugged. Compatibility with Horton is NOT
# guaranteed.
# Its current version contains updates from the PyBEST developer team.
#
# Detailed changes (see also CHANGELOG):
# 2020-07-01: update to new python features, including f-strings
# 2020-07-01: use PyBEST standards, including naming convention, exception clas
# 2022-11-16: include dump method to dump _array attributes to disk

"""Avoid recomputation of earlier results and reallocation of existing arrays

In principle, the ``JustOnceClass`` and the ``Cache`` can be used
independently, but in some cases it makes a lot of sense to combine them.

The ``Cache`` class is supposed to store temporary objects in memory so that
they occupy the same memory location throughout an optimization. It is not
meant to store output data or any return values from method classes.
For this purpose, we use the ``IOData`` container.
"""

import types
import uuid
from functools import wraps

import numpy as np

from pybest.exceptions import ArgumentError
from pybest.linalg.base import NIndexObject
from pybest.log import log


class JustOnceClass:
    """Base class for classes with methods that should never be executed twice.

    In typical applications, these methods get called many times, but
    only during the first call, an actual computation is carried out. This
    way, the caller can safely call a method, just to make sure that a
    required result is computed.

    All methods in the subclasses that should have this feature must be
    given the ``just_once`` decorator, e.g. ::

        class Example(JustOnceClass):
            @just_once
            def do_something():
                self.foo = self.bar

    When all results are outdated, one can call the ``clear`` method
    to forget which methods were called already.
    """

    def __init__(self):
        self._done_just_once = set()

    def __clear__(self):
        """Clear the internal state of the JustOnceClass instance"""
        self.clear()

    def clear(self):
        """Reset to forget that a method has been already called."""
        self._done_just_once = set()

    @property
    def done_just_once(self):
        """A set to keep track of things that should be executed only once"""
        return self._done_just_once

    @done_just_once.setter
    def done_just_once(self, new):
        self._done_just_once.add(new)


def just_once(fn):
    """Decorator used to call and execute a function only once."""

    @wraps(fn)
    def wrapper(instance):
        if not hasattr(instance, "_done_just_once"):
            raise TypeError(
                "Missing hidden _done_just_once. Forgot to call JustOnceClass.__init__()?"
            )
        if fn.__name__ in instance.done_just_once:
            return
        fn(instance)
        instance.done_just_once = fn.__name__

    return wrapper


def _normalize_alloc(alloc):
    """Normalize the alloc argument of the from_alloc and check_alloc methods"""
    if not hasattr(alloc, "__len__"):
        alloc = (alloc,)
    if len(alloc) == 0:
        raise ArgumentError("Alloc can not be an empty list")
    return alloc


def _normalize_tags(tags):
    """Normalize the tags argument of the CacheItem constructor"""
    if tags is None:
        return set()
    return set(tags)


class CacheItem:
    """A container for an object stored in a Cache instance"""

    def __init__(self, value, own=False, tags=None):
        """
        **Arguments:**

        value
             The object stored in this container

        **Optional arguments:**

        own
             If True, this container will denounce the memory allocated for
             the contained object. This can only be True for a numpy array.

        tags
             Tag used to store several instances of CacheItem to keep track of
             a group of objects. Objects belonging to the same `tags` can be
             deallocated all at once.
        """
        self._value = value
        self.valid = True
        self._dumped = False
        self._own = own
        self._tags = _normalize_tags(tags)

    @property
    def value(self):
        """The value of the item stored as an instance of CacheItem. It can be
        anything (int, str, np.array, NIndexObject, etc.). It is only returned
        if it is valid
        """
        if not self.valid:
            raise ArgumentError("This cached item is not valid.")
        return self._value

    @property
    def valid(self):
        """Indicates if a cached item is accessible (True) or not (False).
        Accessible means that it has not been deallocated and is tored in the
        memory. For an item is stored in memory (`dumped=False`), `valid=True`.
        For an item stored on disk (`dumped=True`), `valid=False`.
        """
        return self._valid

    @valid.setter
    def valid(self, new):
        if isinstance(new, bool):
            self._valid = new
        else:
            raise ArgumentError(f"Cannot assign valid of type {type(new)}")

    @property
    def dumped(self):
        """Keep track whether _array data has been dumped to disk"""
        return self._dumped

    @dumped.setter
    def dumped(self, new):
        if not isinstance(new, bool):
            raise ArgumentError(f"Cannot assign valid of type {type(new)}")
        self._dumped = new

    @property
    def tags(self):
        """Tag used to store several instances of CacheItem to keep track of a
        group of objects
        """
        return self._tags

    @classmethod
    def from_alloc(cls, alloc, tags):
        """Allocate some nd-array using some cls (here some NIndexObject)"""
        alloc = _normalize_alloc(alloc)
        if all(isinstance(i, int) for i in alloc):
            # initialize a floating point array
            array = np.zeros(alloc, float)
            log.mem.announce(array.nbytes)
            return cls(array, own=True, tags=tags)
        # initialize a new object
        return cls(alloc[0](*alloc[1:]), tags=tags)

    def __del__(self):
        """Overwrite __del__ method"""
        if self._own and log is not None:
            assert isinstance(self._value, np.ndarray)
            log.mem.denounce(self._value.nbytes)

    def check_alloc(self, alloc):
        """Check a given allocation method if it has been appropriately called
        and passed to the `load` method
        """
        alloc = _normalize_alloc(alloc)
        if all(isinstance(i, int) for i in alloc):
            # check if the array has the correct shape and dtype
            if not (
                isinstance(self._value, np.ndarray)
                and self._value.shape == tuple(alloc)
                and issubclass(self._value.dtype.type, float)
            ):
                raise ArgumentError(
                    "The stored item does not match the given alloc."
                )
        else:
            # check if the object was initialized with compatible arguments
            try:
                if isinstance(alloc[0], type):
                    # first argument is a class
                    alloc[0].__check_init_args__(self._value, *alloc[1:])
                elif isinstance(alloc[0], types.MethodType):
                    # first argument is something else, assuming a method of a factory class
                    factory = alloc[0].__self__
                    alloc[0].__check_init_args__(
                        factory, self._value, *alloc[1:]
                    )
                else:
                    raise NotImplementedError
            except AssertionError as e:
                raise ArgumentError(
                    "The stored item does not match the given alloc."
                ) from e

    def check_tags(self, tags):
        """Check for consistency of tags. If not found in tag list, raise
        error
        """
        tags = _normalize_tags(tags)
        if tags != self.tags:
            raise ArgumentError("Tags do not match.")

    def clear(self):
        """Mark the item as invalid and clear the contents of the object.

        **Returns:** A boolean indicating that clearing was successful
        """
        if isinstance(self.value, np.ndarray):
            self._value[:] = 0.0
            self.valid = False
        elif hasattr(self.value, "__clear__") and callable(
            self.value.__clear__
        ):
            self.value.__clear__()
            self.valid = False
        else:
            self.valid = False
            return False
        return True


class NoDefault:
    """Simply continue if no default value is provided"""


no_default = NoDefault()


def _normalize_key(key):
    """Normalize the key argument(s) of the load and dump methods"""
    if hasattr(key, "__len__") and len(key) == 0:
        raise ArgumentError("At least one argument needed to specify a key.")
    # unpack the key if needed
    while len(key) == 1 and isinstance(key, tuple):
        key = key[0]
    return key


class Cache:
    """Object that stores previously computed results.

    The cache behaves like a dictionary with some extra features that can be
    used to avoid recomputation or reallocation.
    """

    def __init__(self):
        self._store = {}

    @property
    def store(self):
        """Dictionary that stores all items of a Cache instance"""
        return self._store

    @store.setter
    def store(self, dict_el):
        self._store.update(dict_el)

    @staticmethod
    def is_valid_label(label: str) -> bool:
        """Check if a `label` is valid and corresponds to a uuid.UUID instance.
        The `dump_array` method of NIndexObject in base.py generates a unique
        ID if the label is `""`. In the `Cache` class, dumped items should
        use a uuid.UUID instance to prevent case-insensitive file systems
        from dumping/loading the wrong item value.
        """
        try:
            # base ndarray is using uuid4
            # make sure that we use the same uuid
            uuid_obj = uuid.UUID(label, version=4)
        except ValueError:
            # otherwise we need to generate a unique ID
            # this is done in the `dump_array` method of NIndexObject if
            # the label is set to an empty string `""`
            return False
        return str(uuid_obj) == label

    def clear(self, **kwargs):
        """Clear all items in the cache

        **Optional arguments:**

        dealloc
             When set to True, the items are really removed from memory.

        tags
             Limit the items cleared to those who have at least one tag
             that matches one of the given tags. When this argument is used
             and it contains at least one tag, items with no tags are not
             cleared.
        """
        # Parse kwargs. This forces the caller to use keywords in order to avoid
        # confusion.
        dealloc = kwargs.pop("dealloc", False)
        tags = kwargs.pop("tags", None)
        if len(kwargs) > 0:
            raise ArgumentError(f"Unexpected arguments: {kwargs.keys()}")
        # actual work
        tags = _normalize_tags(tags)
        for key, item in list(self.store.items()):
            if len(tags) == 0 or len(item.tags & tags) > 0:
                self.clear_item(key, dealloc=dealloc)

    def clear_item(self, *key, **kwargs):
        """Clear a selected item from the cache

        **Optional arguments:**

        dealloc
             When set to True, the item is really removed from memory.
        """
        key = _normalize_key(key)
        dealloc = kwargs.pop("dealloc", False)
        if len(kwargs) > 0:
            raise ArgumentError(f"Unexpected arguments: {kwargs.keys()}")
        item = self.store.get(key)
        if item is None:
            return
        cleared = False
        if not dealloc:
            cleared = item.clear()
        if not cleared:
            del self.store[key]

    def load(self, *key, **kwargs):
        """Get a value from the cache

        **Arguments:**

        key0 [key1 ...]
             All positional arguments are used as keys to identify the cached
             value.

        **Optional arguments:**

        alloc
             Parameters used to allocate a cached value if it is not present
             yet. This argument can take two forms. When an integer or a
             tuple of integers is given, an array is allocated.
             Alternatively, a tuple may be given whose first element is a
             constructor, and further elements are arguments for that
             constructor.

        default
             A default value that is returned when the key does not exist in
             the cache. This default value is not stored in the cache.

        tags
             When alloc is used and a new object is thereby created or
             reused, it will get these tags. This argument is only allowed if
             the alloc argument is present. In case no new object is
             allocated, the given tags must match those already present.

        The optional argument alloc and default are both meant to handle
        situations when the key has not associated value. Hence they can not
        be both present.

        The loading process of a Cache item depends on two attributes:
        - `valid`: item is accessible, that is, it has to be loaded in the Cache
        - `dumped`: item is stored on disk (not in memory)
        `valid` and `dumped` are decoupled from each other and indicate
        different states of the cached item (stored in the attribute `value`).
        """
        key = _normalize_key(key)

        # parse kwargs
        alloc = kwargs.pop("alloc", None)
        default = kwargs.pop("default", no_default)
        tags = kwargs.pop("tags", None)
        if not (alloc is None or default is no_default):
            raise ArgumentError(
                "The optional arguments alloc and default can not be used at the same time."
            )
        if tags is not None and alloc is None:
            raise ArgumentError(
                "The tags argument is only allowed when the alloc argument is present."
            )
        if len(kwargs) > 0:
            raise ArgumentError(f"Unknown optional arguments: {kwargs.keys()}")

        # get the item from the store and decide what to do
        item = self.store.get(key)
        # there are three behaviors, depending on the keyword argumentsL
        if alloc is not None:
            # alloc is given. hence two return values: value, new
            if item is None:
                # allocate a new item and store it
                item = CacheItem.from_alloc(alloc, tags)
                self.store = {key: item}
                return item.value, True
            if not item.valid:
                try:
                    # try to reuse the same memory
                    item.check_alloc(alloc)
                    item.valid = True  # as if it is newly allocated
                    item.check_tags(tags)
                except ArgumentError:
                    # if reuse fails, reallocate
                    item = CacheItem.from_alloc(alloc, tags)
                    self.store = {key: item}
                return item.value, True
            item.check_alloc(alloc)
            item.check_tags(tags)
            return item.value, False
        if default is not no_default:
            # a default value is given, it is not stored
            if item is None or not item.valid:
                return default
        elif item is not None and item.dumped:
            # assume that value has been dumped to disk; data will be read from
            # disk using the load_array method of NIndexObject where label
            # is the key
            if not item.valid:
                # check if item values are valid, if not, we need to load them
                # from file first, otherwise, they are still in memory
                item.valid = True
                item.dumped = True
                # first load
                item.value.load_array(key)
            # then return (otherwise it breaks) (outside if clause)
        # no optional arguments are given
        elif item is None or not item.valid:
            raise KeyError(key)
        return item.value

    def __contains__(self, key):
        """Check if a key is in the cache"""
        key = _normalize_key(key)
        item = self.store.get(key)
        if item is None:
            return False
        return item.valid

    def save(self, *args, **kwargs):
        """Store an object in the cache.

        **Arguments:**

        key1 [, key2, ...]
             The positional arguments (except for the last) are used as a key
             for the object.

        value
             The object to be stored.

        **Optional argument:**

        own
             When set to True, the cache will take care of denouncing the
             memory usage due to this array.

        tags
             Tags to be associated with the object
        """
        own = kwargs.pop("own", False)
        tags = kwargs.pop("tags", None)
        if len(kwargs) > 0:
            raise ArgumentError(f"Unknown optional arguments: {kwargs.keys()}")
        if len(args) < 2:
            raise ArgumentError(
                "At least two arguments are required: key1 and value."
            )
        key = _normalize_key(args[:-1])
        value = args[-1]
        item = CacheItem(value, own, tags)
        self.store[key] = item

    def dump(self, *key, **kwargs):
        """Dump a value from the Cache. The method only works if Cache value is
        an instance of NIndexObject. In this case, the dump_array method is
        used where the _array attribute is first dumped to disk and then
        deleted. The actual Cache instance is not affected.

        Procedure:
        - select item with key `key` from the current Cache instance
        - check if the selected item has already been dumped
            - if already dumped, skip the dumping process
            - if already dumped but rewrite required, dump again
            - check for unique ID to guarantee that files are overwritten
        - if dumped, _array attribute gets deleted
            - set attribute `valid` to False (not accessible in memory)
            - set attribute `dumped` to True (accessible on disk)
          (see also `load` method)
        - in order to update a dumped _array, the `force` keyword argument has
          to be set to True. Otherwise, the dump function does NOTHING as the
          _array is assumed to be dumped already (we dump only once per item)

        **Arguments:**

        key0 [key1 ...]
             All positional arguments are used as keys to identify the cached
             value.

        **Optional arguments:**

        force
             force dumping `_array` attribute to disk. This will overwrite
             the original file if present
        """
        key = _normalize_key(key)
        # parse kwargs
        force = kwargs.pop("force", False)
        if len(kwargs) > 0:
            raise ArgumentError(f"Unknown optional arguments: {kwargs.keys()}")
        # get the item from the store and decide what to do
        item = self.store.get(key)
        # if there is an item in the cache but it contains no data to be dumped,
        # we will do nothing
        if item is not None and not item.valid:
            if not item.dumped:
                raise ValueError("Expected item has not been dumped, yet.")
            if not force:
                # item has been already dumped and we do not force overwrite
                return
        # if there isn't any item nor data, raise error
        if item is None or not item.valid:
            raise KeyError(key)
        # check if item is an instance of NIndexObject (we can only access
        # `item.value` if item is `valid`)
        if not isinstance(item.value, NIndexObject):
            raise ValueError(
                "We can only dump instances of NIndexObject to disk"
            )
        # (1) we want the dump_array method to generate a unique label so that
        # labels that differ in case sensitive letters do not get overwritten
        # (2) if force == True, do not reset label, but use the unique label
        # assigned
        if not force or item.value.label != "":
            item.value.label = (
                ""
                if not self.is_valid_label(str(item.value.label))
                else item.value.label
            )
        # dump the array
        item.value.dump_array(key)
        # declare item as invalid
        item.valid = False
        item.dumped = True

    def __len__(self):
        """Returns length of valid items in cache"""
        return sum(item.valid for item in self.store.values())

    def __getitem__(self, key):
        """Get a value from the cache"""
        return self.load(key)

    def __setitem__(self, key, value):
        """Set a value in the cache"""
        return self.save(key, value)

    def __iter__(self):
        """Iterate over the keys of all valid items in the cache."""
        return self.iterkeys()

    def iterkeys(self, tags=None):
        """Iterate over the keys of all valid items in the cache."""
        tags = _normalize_tags(tags)
        for key, item in self.store.items():
            if item.valid and (len(tags) == 0 or len(item.tags & tags) > 0):
                yield key

    def values(self, tags=None):
        """Iterate over the values of all valid items in the cache."""
        tags = _normalize_tags(tags)
        for item in self.store.values():
            if item.valid and (len(tags) == 0 or len(item.tags & tags) > 0):
                yield item.value

    def items(self, tags=None):
        """Iterate over all valid items in the cache."""
        tags = _normalize_tags(tags)
        for key, item in self.store.items():
            if item.valid and (len(tags) == 0 or len(item.tags & tags) > 0):
                yield key, item.value
