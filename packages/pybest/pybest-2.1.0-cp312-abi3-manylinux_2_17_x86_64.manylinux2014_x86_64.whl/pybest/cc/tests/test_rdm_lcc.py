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
# 03/2025:
# This file has been modified by Somayeh Ahmadkhani and Lena Szczuczko


import numpy as np
import pytest

from pybest.cc.rdm_lcc import (
    compute_1dm_pccdlccd,
    compute_1dm_pccdlccsd,
    compute_2dm_pccdlccd,
    compute_2dm_pccdlccsd,
    compute_3dm_pccdlccd,
    compute_3dm_pccdlccsd,
    compute_4dm_pccdlccd,
    compute_4dm_pccdlccsd,
    set_seniority_0,
)
from pybest.context import context
from pybest.linalg import DenseFourIndex, DenseOneIndex, DenseTwoIndex

methods = {
    "dm_1": "compute_1dm",
    "dm_2": "compute_2dm",
    "dm_3": "compute_3dm",
    "dm_4": "compute_4dm",
}

method_call_map = {
    "compute_1dm_pccdlccd": compute_1dm_pccdlccd,
    "compute_1dm_pccdlccsd": compute_1dm_pccdlccsd,
    "compute_2dm_pccdlccd": compute_2dm_pccdlccd,
    "compute_2dm_pccdlccsd": compute_2dm_pccdlccsd,
    "compute_3dm_pccdlccd": compute_3dm_pccdlccd,
    "compute_3dm_pccdlccsd": compute_3dm_pccdlccsd,
    "compute_4dm_pccdlccd": compute_4dm_pccdlccd,
    "compute_4dm_pccdlccsd": compute_4dm_pccdlccsd,
}

occ_nbasis = [(5, 24)]

lccd = "pCCDLCCD"
lccsd = "pCCDLCCSD"

rdm_set = [
    # LCCD
    (lccd, "dm_1", "pq", ("t_2",), ("l_2",), ("t_p",)),
    (lccd, "dm_2", "pPPp", ("t_2",), ("l_2",), ("t_p",)),
    (lccd, "dm_2", "pqqp_a", ("t_2",), ("l_2",), ("t_p",)),
    (lccd, "dm_2", "pQQp_b", ("t_2",), ("l_2",), ("t_p",)),
    (lccd, "dm_2", "qQQp", ("t_2",), ("l_2",), ("t_p",)),
    (lccd, "dm_2", "pQPp", ("t_2",), ("l_2",), ("t_p",)),
    (lccd, "dm_2", "qQPq", ("t_2",), ("l_2",), ("t_p",)),
    (lccd, "dm_2", "qQPp", ("t_2",), ("l_2",), ("t_p",)),
    (lccd, "dm_2", "pQPq", ("t_2",), ("l_2",), ("t_p",)),
    (lccd, "dm_2", "qPPp", ("t_2",), ("l_2",), ("t_p",)),
    (lccd, "dm_3", "qPQQPp", ("t_2",), ("l_2",), ("t_p",)),
    (lccd, "dm_3", "qpPPpq", ("t_2",), ("l_2",), ("t_p",)),
    (lccd, "dm_4", "pPqQQqPp", ("t_2",), ("l_2",), ("t_p",)),
    # LCCSD
    (lccsd, "dm_1", "pq", ("t_2", "t_1"), ("l_2", "l_1"), ("t_p",)),
    (lccsd, "dm_2", "pPPp", ("t_2", "t_1"), ("l_2", "l_1"), ("t_p",)),
    (lccsd, "dm_2", "pqqp_a", ("t_2", "t_1"), ("l_2", "l_1"), ("t_p",)),
    (lccsd, "dm_2", "pQQp_b", ("t_2", "t_1"), ("l_2", "l_1"), ("t_p",)),
    (lccsd, "dm_2", "qQQp", ("t_2", "t_1"), ("l_2", "l_1"), ("t_p",)),
    (lccsd, "dm_2", "pQPp", ("t_2", "t_1"), ("l_2", "l_1"), ("t_p",)),
    (lccsd, "dm_2", "qQPq", ("t_2", "t_1"), ("l_2", "l_1"), ("t_p",)),
    (lccsd, "dm_2", "qQPp", ("t_2", "t_1"), ("l_2", "l_1"), ("t_p",)),
    (lccsd, "dm_2", "pQPq", ("t_2", "t_1"), ("l_2", "l_1"), ("t_p",)),
    (lccsd, "dm_2", "qPPp", ("t_2", "t_1"), ("l_2", "l_1"), ("t_p",)),
    (lccsd, "dm_3", "qPQQPp", ("t_2", "t_1"), ("l_2", "l_1"), ("t_p",)),
    (lccsd, "dm_3", "qpPPpq", ("t_2", "t_1"), ("l_2", "l_1"), ("t_p",)),
    (lccsd, "dm_4", "pPqQQqPp", ("t_2", "t_1"), ("l_2", "l_1"), ("t_p",)),
]


def read_amplitudes(mol, method, t_x, occ, nbasis):
    """Read some amplitudes from file `mol_method_t_x.txt`"""
    filename = f"test/{mol.lower()}_{method.lower()}_{t_x}.txt"
    amplitudes_fn = context.get_fn(filename)
    amplitudes = np.fromfile(amplitudes_fn, sep=",")
    vir = nbasis - occ
    if t_x in ["t_1", "l_1", "t_p"]:
        amplitudes = amplitudes.reshape(occ, vir)
        amplitudes_ = DenseTwoIndex(occ, vir)
        amplitudes_.assign(amplitudes)
    elif t_x in ["t_2", "l_2"]:
        amplitudes = amplitudes.reshape(occ, vir, occ, vir)
        amplitudes_ = DenseFourIndex(occ, vir, occ, vir)
        amplitudes_.assign(amplitudes)
    return amplitudes_


@pytest.mark.parametrize("mol", ["h2o"])
@pytest.mark.parametrize("occ,nbasis", occ_nbasis)
@pytest.mark.parametrize("method,rdm,block,t_cc,l_cc,t_p", rdm_set)
def test_rdm_lcc(mol, occ, nbasis, method, rdm, block, t_cc, l_cc, t_p):
    """Test all compute_*dm_* methods. Test only pCCD-LCC part as it exploits
    also the LCC implementation of RDMs.
    A set of amplitudes (CC and Lambda) is read from disk. The corresponding
    blocks of some RDMs are constructed and compared to reference RDMs.
    The reference data is stored as `mol_method_rdm_block.txt` and
    `mol_method_t_cc.txt` or `mol_method_l_cc.txt`.

    :mol: (str) the name of the molecule
    :method: (str) acronym of the CC flavour
    :occ: (int) number of occupied orbitals
    :nbasis: (int) number of basis function
    :rdm: (str) either 1-, 2-, 3-, or 4-RDM
    :block: (str) the block of the N-RDM being calculated
    :t_cc: (tuple of str) containing the types of CC amplitdudes as keys
    :l_cc: (tuple of str) containing the types of Lambda amplitdudes as keys
    :t_p: (str) indicating whether CC electron pair amplitdudes are passed
    """
    # Reference RDMs
    filename = f"test/{mol.lower()}_{method.lower()}_{rdm}_{block}.txt"
    dm_file = context.get_fn(filename)
    dm_ref = np.fromfile(dm_file, sep=",")
    dm_test = DenseOneIndex(nbasis)
    if dm_ref.size == nbasis * nbasis:
        dm_ref = dm_ref.reshape(nbasis, nbasis)
        dm_test = DenseTwoIndex(nbasis)
    # CC amplitudes
    t_cc_ = {}
    for key in t_cc:
        value = read_amplitudes(mol, method, key, occ, nbasis)
        t_cc_.update({key: value})
    # Lambda amplitudes
    l_cc_ = {}
    for key in l_cc:
        value = read_amplitudes(mol, method, key, occ, nbasis)
        l_cc_.update({key: value})
    # Electron pair amplitudes
    t_p_ = {}
    for key in t_p:
        value = read_amplitudes(mol, method, key, occ, nbasis)
        t_p_.update({key: value})
    # Take into account case insensitive file systems
    block = block.split("_")[0]
    # choose correct method to test
    method_name = f"{methods[rdm]}_{method.lower()}"
    method_call_map[method_name](block, dm_test, l_cc_, t_cc_, 1.0, **t_p_)
    assert np.allclose(dm_test.array, dm_ref)


s0_set = [("H2O", "pCCDLCCD", 5, 24)]


@pytest.mark.parametrize("mol,method,occ,nbasis", s0_set)
def test_set_seniority_0_array(mol, method, occ, nbasis):
    """Assign array of t_p to t_2"""
    t_2 = {"t_2": read_amplitudes(mol, method, "t_2", occ, nbasis)}
    t_p = read_amplitudes(mol, method, "t_p", occ, nbasis)
    # Get seniority 0 indices
    vir = t_p.nbasis1
    ind1, ind2 = np.indices((occ, vir))
    indices = tuple([ind1, ind2, ind1, ind2])
    assert not np.allclose(t_2["t_2"].array[indices], t_p.array)
    # Assign t_p
    set_seniority_0(t_2, t_p)
    assert np.allclose(t_2["t_2"].array[indices], t_p.array)


@pytest.mark.parametrize("mol,method,occ,nbasis", s0_set)
def test_set_seniority_0_value(mol, method, occ, nbasis):
    """Assign a value of 1.0 to the senority 0 block of t_2"""
    # t_2 amplitudes with a seniority 0 block of 0.0
    t_2 = {"t_2": read_amplitudes(mol, method, "t_2", occ, nbasis)}
    # Get seniority 0 indices
    vir = nbasis - occ
    ind1, ind2 = np.indices((occ, vir))
    indices = tuple([ind1, ind2, ind1, ind2])
    assert np.allclose(t_2["t_2"].array[indices], 0.0)
    # Assign 1.0
    set_seniority_0(t_2, 1.0)
    assert np.allclose(t_2["t_2"].array[indices], 1.0)
