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

from pybest.ee_eom import (
    REOMCCD,
    REOMCCSD,
    REOMLCCD,
    REOMLCCSD,
    REOMpCCD,
    REOMpCCDCCS,
    REOMpCCDLCCD,
    REOMpCCDLCCSD,
    REOMpCCDS,
)
from pybest.exceptions import ArgumentError

test_dump_cache_item = [
    "loovv",
    "x1_iakc",
    "x_ajkc",
    "x_iakc",
    "x_ajkc",
    "lovvv",
    "goovv",
    "x_adkc",
    "x_abcd",
]

test_dump_cache_cls = [
    REOMCCD,
    REOMCCSD,
    REOMLCCD,
    REOMLCCSD,
    REOMpCCD,
    REOMpCCDS,
    REOMpCCDCCS,
    REOMpCCDLCCD,
    REOMpCCDLCCSD,
]


@pytest.mark.parametrize("cls", test_dump_cache_cls)
@pytest.mark.parametrize("cache_item", test_dump_cache_item)
def test_ee_eom_dump_cache(cls, cache_item, c_atom):
    """Test if effective Hamiltonian is dumped to disk.

    We check three different functions here:
    1) set_hamiltonian
    2) build_hamiltonian
    3) compute_h_diag

    If Cache instance contains an item ``cache_item``, we check for the ``_array``
    attribute, which should NOT be present in any test case.
    We circumvent missing ``cache_item`` elements by
    * passing with KeyError (``cache_item`` is not stored at all in an EOM model)
    * raising ArgumentError (if present, ``cache_item`` should not be valid)
    """
    # Create an EE-EOM-pCCD-based instance
    ee_eom = cls(c_atom.lf, c_atom.occ_model)
    # set some class attributes explicitly as they are set during function call
    ee_eom.unmask_args(
        c_atom.olp, *c_atom.orb_a, *c_atom.hamiltonian, **c_atom.amplitudes
    )
    ee_eom._dump_cache = True

    # we need to copy the arrays as they get deleted
    one, two = c_atom.one.copy(), c_atom.two.copy()
    ee_eom.set_hamiltonian(one, two)

    # Check if cache has been dumped properly
    # We need to access _store directly, otherwise the load function of the
    # Cache class is called and test will fail by construction
    #
    # 1) Check set_hamiltonian
    try:
        assert not hasattr(ee_eom.cache._store[cache_item], "_array"), (
            f"Cache element {cache_item} not properly dumped to disk in "
            "set_hamiltonian"
        )
    except KeyError:
        pass
    # 2) Check build_hamiltonian
    vector = c_atom.lf.create_one_index(ee_eom.dimension)
    # all elements should be loaded from the disk and dumped to the disk again
    ee_eom.build_subspace_hamiltonian(vector, None)
    try:
        with pytest.raises(ArgumentError):
            assert not hasattr(
                ee_eom.cache._store[cache_item].value, "_array"
            ), (
                f"Cache element {cache_item} not properly dumped to disk in "
                "build_subspace_hamiltonian"
            )
    except KeyError:
        pass
    # 3) Check compute_h_diag
    # all elements should be loaded from disk and dump to disk again
    ee_eom.compute_h_diag()
    try:
        with pytest.raises(ArgumentError):
            assert not hasattr(
                ee_eom.cache._store[cache_item].value, "_array"
            ), (
                f"Cache element {cache_item} not properly dumped to disk in "
                "compute_h_diag"
            )
    except KeyError:
        pass


@pytest.mark.parametrize("cls", test_dump_cache_cls)
@pytest.mark.parametrize("cache_item", test_dump_cache_item)
def test_ee_eom_load_dump_cache(cls, cache_item, c_atom):
    """Test if effective Hamiltonian is dumped to disk."""
    # Create an EE-EOM-pCCD-based instance
    ee_eom = cls(c_atom.lf, c_atom.occ_model)
    # set some class attributes explicitly as they are set during function call
    ee_eom.unmask_args(
        c_atom.olp, *c_atom.orb_a, *c_atom.hamiltonian, **c_atom.amplitudes
    )
    ee_eom._dump_cache = True

    # we need to copy the arrays as they get deleted
    one, two = c_atom.one.copy(), c_atom.two.copy()
    ee_eom.set_hamiltonian(one, two)

    # First load arrays again and check if present
    try:
        assert hasattr(
            ee_eom.cache[cache_item], "_array"
        ), f"Cache element {cache_item} not properly loaded from disk"
        ee_eom.cache.dump(cache_item)
    except KeyError:
        pass

    # Dump again, so cache item should not be present
    try:
        assert not hasattr(
            ee_eom.cache._store[cache_item], "_array"
        ), f"Cache element {cache_item} not properly dumped to disk"
    except KeyError:
        pass
