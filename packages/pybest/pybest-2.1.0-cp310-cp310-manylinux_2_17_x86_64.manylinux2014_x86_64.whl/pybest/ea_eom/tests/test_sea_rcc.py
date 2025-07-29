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
# 2024: This file has been originally written by Saman Behjou.
#

"""Unit tests for EA-EOM-CC methods from rcc module."""

import numpy as np
import pytest

from pybest.cc import (
    RCCD,
    RCCSD,
    RLCCD,
    RLCCSD,
    RfpCCD,
    RfpCCSD,
    RpCCDLCCD,
    RpCCDLCCSD,
)
from pybest.context import context
from pybest.ea_eom.sea_rccd1 import (
    SEACCD1,
    SEALCCD1,
    SEAfpCCD1,
    SEAfpLCCD1,
)
from pybest.ea_eom.sea_rccsd1 import (
    SEACCSD1,
    SEALCCSD1,
    SEAfpCCSD1,
    SEAfpLCCSD1,
)
from pybest.ea_eom.tests.common import EA_EOMMolecule
from pybest.ea_eom.xea_base import RXEACC
from pybest.ea_eom.xea_rcc import (
    REACCD,
    REACCSD,
    REALCCD,
    REALCCSD,
    REAfpCCD,
    REAfpCCSD,
    REAfpLCCD,
    REAfpLCCSD,
)
from pybest.exceptions import ArgumentError
from pybest.geminals import ROOpCCD
from pybest.linalg import (
    DenseFourIndex,
    DenseLinalgFactory,
    DenseTwoIndex,
)
from pybest.occ_model import AufbauOccModel
from pybest.tests.common import load_reference_data

test_ip_cls_resolve_t = [
    (REACCD, {"alpha": 1}, {"t_2": DenseFourIndex(2, 4, 2, 4)}),
    (REACCSD, {"alpha": 1}, {"t_1": 1, "t_2": DenseFourIndex(2, 4, 2, 4)}),
    (REALCCD, {"alpha": 1}, {"t_2": DenseFourIndex(2, 4, 2, 4)}),
    (REALCCSD, {"alpha": 1}, {"t_1": 1, "t_2": DenseFourIndex(2, 4, 2, 4)}),
    (REAfpCCD, {"alpha": 1}, {"t_2": DenseFourIndex(2, 4, 2, 4)}),
    (REAfpCCSD, {"alpha": 1}, {"t_1": 1, "t_2": DenseFourIndex(2, 4, 2, 4)}),
    (REAfpLCCD, {"alpha": 1}, {"t_p": 1, "t_2": DenseFourIndex(2, 4, 2, 4)}),
    (
        REAfpLCCSD,
        {"alpha": 1},
        {"t_1": 1, "t_p": 1, "t_2": DenseFourIndex(2, 4, 2, 4)},
    ),
]


@pytest.mark.parametrize("cls,kwargs,t_args", test_ip_cls_resolve_t)
def test_resolve_t(cls, kwargs, t_args):
    """Test if T amplitudes are properly resolved from arguments"""
    # Some preliminaries
    lf = DenseLinalgFactory(10)
    occ_model = AufbauOccModel(lf, nel=4 * 2, ncore=0)
    # Initialize empty class (we cannot use abc class)
    rcc = cls(lf, occ_model, **kwargs)
    # Dry run, if it fails a KeyError will be raised
    rcc.resolve_t(t_args)
    # Check items
    for key, item in t_args.items():
        assert rcc.checkpoint[key] == item, "wrong item stored in container"


test_data_alpha = [
    (REACCD, {"alpha": 1}, 1),
    (REACCSD, {"alpha": 1}, 1),
    (REALCCD, {"alpha": 1}, 1),
    (REALCCSD, {"alpha": 1}, 1),
    (REAfpCCD, {"alpha": 1}, 1),
    (REAfpCCSD, {"alpha": 1}, 1),
    (REAfpLCCD, {"alpha": 1}, 1),
    (REAfpLCCSD, {"alpha": 1}, 1),
]


@pytest.mark.parametrize("cls,kwargs,expected", test_data_alpha)
def test_alpha(cls, kwargs, expected):
    """Check if alpha agrees after REApCCD/RDEApCCD inits."""
    # Some preliminaries
    lf = DenseLinalgFactory(10)
    occ_model = AufbauOccModel(lf, nel=8, ncore=0)
    # Initialize empty class
    earcc = cls(lf, occ_model, **kwargs)

    assert earcc.alpha == expected


test_data_instance = [
    (REACCD, {"alpha": 1}, SEACCD1),
    (REACCSD, {"alpha": 1}, SEACCSD1),
    (REALCCD, {"alpha": 1}, SEALCCD1),
    (REALCCSD, {"alpha": 1}, SEALCCSD1),
    (REAfpCCD, {"alpha": 1}, SEAfpCCD1),
    (REAfpCCSD, {"alpha": 1}, SEAfpCCSD1),
    (REAfpLCCD, {"alpha": 1}, SEAfpLCCD1),
    (REAfpLCCSD, {"alpha": 1}, SEAfpLCCSD1),
]


@pytest.mark.parametrize("cls,kwargs,expected", test_data_instance)
def test_instance(cls, kwargs, expected):
    """Check if __new__ overwrite works properly."""
    # Some preliminaries
    lf = DenseLinalgFactory(10)
    occ_model = AufbauOccModel(lf, nel=8, ncore=0)
    # Initialize empty class
    earcc = cls(lf, occ_model, **kwargs)

    assert isinstance(earcc, expected)


test_ea_flavor = [
    REACCD,
    REACCSD,
    REALCCD,
    REALCCSD,
    REAfpCCD,
    REAfpCCSD,
    REAfpLCCD,
    REAfpLCCSD,
]

test_unmask = [
    # Everything should be fine
    {"alpha": 1},
    {"alpha": 1},
]


@pytest.mark.parametrize("cls", test_ea_flavor)
@pytest.mark.parametrize("kwargs", test_unmask)
def test_ea_cc_unmask(cls, kwargs, boron):
    """Test unmask_arg function by passing proper arguments"""
    # Create IPCC instance
    ea_cc = cls(boron.lf, boron.occ_model, **kwargs)

    # We do not need to check the arrays, just the objects
    assert ea_cc.unmask_args(*boron.args, **boron.amplitudes) == (
        boron.one,
        boron.two,
        boron.orb[0],
    )


#
# Test effective Hamiltonian (only initialization)
#


test_ea_rccd_flavor = [
    REACCD,
    REALCCD,
    REAfpCCD,
    REAfpLCCD,
]

h_rccd_dens = {
    "fock",
    "I_abjd",
    "I_aBJd",
    "I_ck",
    "I_bd",
    "I_jm",
    "I_abcd",
    "I_aBcD",
    "I_jbKC",
    "I_JaKc",
    "goovv",
    "gvovv",
    "gnnnv",
    "gnnvn",
    "gnvnn",
    "gvvvv",
    "gnnvv",
}

test_set_rccd_hamiltonian = [
    ({"alpha": 1}, h_rccd_dens),
]


@pytest.mark.parametrize("cls", test_ea_rccd_flavor)
@pytest.mark.parametrize("kwargs,expected", test_set_rccd_hamiltonian)
def test_ea_rccd_set_hamiltonian(cls, kwargs, expected, carbon):
    """Test if effective Hamiltonian has been constructed at all. We do not
    test the actual elements.
    """
    # Create EAPCC instance
    earccd = cls(carbon.lf, carbon.occ_model, **kwargs)

    # Set some class attributes
    earccd.unmask_args(
        carbon.t_p,
        carbon.olp,
        *carbon.orb,
        *carbon.hamiltonian,
        **carbon.amplitudes,
    )

    # We do not need to check the arrays, just the objects
    # We need to copy the arrays as they get deleted
    one, two = carbon.one.copy(), carbon.two.copy()
    earccd.set_hamiltonian(carbon.one, carbon.two)
    carbon.one, carbon.two = one, two

    factory_type = carbon.lf.__class__.__name__

    if factory_type == "DenseLinalgFactory":
        # Check if cache instance contains all relevant terms
        assert (
            earccd.cache._store.keys() == expected
        ), f"Cache element not found {earccd.cache._store.keys()}"

        # Check loading from cache
        for h_eff in expected:
            assert earccd.from_cache(h_eff), "Loading from cache unsuccessful"

    elif factory_type == "CholeskyLinalgFactory":
        h_rccd_chol = {
            "fock",
            "I_ck",
            "I_bd",
            "I_jm",
            "I_jbKC",
            "I_JaKc",
            "goovv",
            "gvovv",
            "gnnnv",
            "gnnvn",
            "gnvnn",
            "gvvvv",
            "gnnvv",
        }

        # Check if cache instance contains all relevant terms for CholeskyLinalgFactory
        assert (
            earccd.cache._store.keys() == h_rccd_chol
        ), f"Cache element not found for CholeskyLinalgFactory: {earccd.cache._store.keys()}"

        # Check loading from cache for CholeskyLinalgFactory
        for h_eff in h_rccd_chol:
            assert earccd.from_cache(
                h_eff
            ), "Loading from cache unsuccessful for CholeskyLinalgFactory"


test_ea_rccsd_flavor = [
    REACCSD,
    REALCCSD,
    REAfpCCSD,
    REAfpLCCSD,
]

h_rccsd_dens = {
    "fock",
    "I_abjd",
    "I_aBJd",
    "I_ck",
    "I_bd",
    "I_jm",
    "I_abcd",
    "I_aBcD",
    "I_jbKC",
    "I_JaKc",
    "goovv",
    "gvovv",
    "gnnnv",
    "gnnvn",
    "gnvnn",
    "gvvvv",
    "govvv",
    "goovo",
    "govvo",
    "gvovo",
    "gnnvv",
}


test_set_rccsd_hamiltonian = [
    # Molecule instance, n_particle_operator, alpha, expected
    ({"alpha": 1}, h_rccsd_dens),
]


@pytest.mark.parametrize("cls", test_ea_rccsd_flavor)
@pytest.mark.parametrize("kwargs,expected", test_set_rccsd_hamiltonian)
def test_ea_rccsd_set_hamiltonian(cls, kwargs, expected, carbon):
    """Test if effective Hamiltonian has been constructed at all. We do not
    test the actual elements.
    """
    # Create EAPCC instance
    earccsd = cls(carbon.lf, carbon.occ_model, **kwargs)

    # Set some class attributes
    earccsd.unmask_args(
        carbon.t_p,
        carbon.olp,
        *carbon.orb,
        *carbon.hamiltonian,
        **carbon.amplitudes,
    )

    # We do not need to check the arrays, just the objects
    # We need to copy the arrays as they get deleted
    one, two = carbon.one.copy(), carbon.two.copy()
    earccsd.set_hamiltonian(carbon.one, carbon.two)
    carbon.one, carbon.two = one, two

    factory_type = carbon.lf.__class__.__name__

    if factory_type == "DenseLinalgFactory":
        # Check if cache instance contains all relevant terms
        assert (
            earccsd.cache._store.keys() == expected
        ), f"Cache element not found {earccsd.cache._store.keys()}"

        # Check loading from cache
        for h_eff in expected:
            assert earccsd.from_cache(h_eff), "Loading from cache unsuccessful"

    elif factory_type == "CholeskyLinalgFactory":
        h_rccsd_chol = {
            "fock",
            "I_ck",
            "I_bd",
            "I_jm",
            "I_jbKC",
            "I_JaKc",
            "goovv",
            "gvovv",
            "gnnnv",
            "gnnvn",
            "gnvnn",
            "gvvvv",
            "govvv",
            "goovo",
            "govvo",
            "gvovo",
            "gnnvv",
        }

        # Check if cache instance contains all relevant terms for CholeskyLinalgFactory
        assert (
            earccsd.cache._store.keys() == h_rccsd_chol
        ), f"Cache element not found for CholeskyLinalgFactory: {earccsd.cache._store.keys()}"

        # Check loading from cache for CholeskyLinalgFactory
        for h_eff in h_rccsd_chol:
            assert earccsd.from_cache(
                h_eff
            ), "Loading from cache unsuccessful for CholeskyLinalgFactory"


test_dump_cache = [
    # Molecule instance, nparticle, alpha, expected
    ({"alpha": 1}, "I_abcd"),
    ({"alpha": 1}, "I_aBcD"),
    ({"alpha": 1}, "I_jbKC"),
    ({"alpha": 1}, "I_JaKc"),
    ({"alpha": 1}, "I_abjd"),
    ({"alpha": 1}, "I_aBJd"),
]

test_cls = [
    REACCD,
    REACCSD,
    REALCCD,
    REALCCSD,
    REAfpCCD,
    REAfpCCSD,
    REAfpLCCD,
    REAfpLCCSD,
]


@pytest.mark.parametrize("cls", test_cls)
@pytest.mark.parametrize("kwargs,cache_item", test_dump_cache)
def test_ea_rcc_dump_cache(cls, kwargs, cache_item, boron):
    """Test if effective Hamiltonian is dumped to disk."""
    # Create REACCSD instance
    earcc = cls(boron.lf, boron.occ_model, **kwargs)
    # Set some class attributes explicitly as they are set during function call
    earcc.unmask_args(
        boron.t_p,
        boron.olp,
        *boron.orb,
        *boron.hamiltonian,
        **boron.amplitudes,
    )

    earcc._n_particle_operator = 2
    earcc._dump_cache = True

    # We need to copy the arrays as they get deleted
    one, two = boron.one.copy(), boron.two.copy()
    earcc.set_hamiltonian(one, two)

    # Check if cache has been dumped properly
    # We need to access _store directly, otherwise the load function of the
    # Cache class is called and test will fail by construction
    #
    # 1) Check set_hamiltonian
    try:
        assert not hasattr(earcc.cache._store[cache_item]._value, "_array"), (
            f"Cache element {cache_item} not properly dumped to disk in "
            "set_hamiltonian"
        )
    except KeyError:
        pass
    # 2) Check build_hamiltonian
    vector = boron.lf.create_one_index(earcc.dimension)
    # All elements should be loaded from the disk and dumped to the disk again
    earcc.build_subspace_hamiltonian(vector, None)
    try:
        with pytest.raises(ArgumentError):
            assert not hasattr(
                earcc.cache._store[cache_item].value, "_array"
            ), (
                f"Cache element {cache_item} not properly dumped to disk in "
                "build_subspace_hamiltonian"
            )
    except KeyError:
        pass
    # 3) Check compute_h_diag
    # All elements should be loaded from disk and dump to disk again
    earcc.compute_h_diag()
    try:
        with pytest.raises(ArgumentError):
            assert not hasattr(
                earcc.cache._store[cache_item].value, "_array"
            ), (
                f"Cache element {cache_item} not properly dumped to disk in "
                "compute_h_diag"
            )
    except KeyError:
        pass


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


s0_set = [("h2o", "pCCDLCCD", 5, 24), ("h2o", "pCCDLCCSD", 5, 24)]


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
    RXEACC.set_seniority_0(t_2, t_p)
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
    RXEACC.set_seniority_0(t_2, 1.0)
    assert np.allclose(t_2["t_2"].array[indices], 1.0)


#
# Test for electron attachments energies
#

# Mapping from EA classes to their correct RCC counterparts
test_data_ea_rcc = [
    ([RCCD], REACCD),
    ([RCCSD], REACCSD),
    ([RLCCD], REALCCD),
    ([RLCCSD], REALCCSD),
    ([ROOpCCD, RfpCCD], REAfpCCD),
    ([ROOpCCD, RfpCCSD], REAfpCCSD),
    ([ROOpCCD, RpCCDLCCD], REAfpLCCD),
    (
        [ROOpCCD, RpCCDLCCSD],
        REAfpLCCSD,
    ),
]
test_data_rcc = [
    (
        "no",
        "cc-pvdz",
        {"ncore": 0, "charge": 1, "alpha": 1, "nroot": 7},
    ),
]


@pytest.mark.parametrize(
    "cls,ea_cls",
    test_data_ea_rcc,
    ids=[
        "RCCD",
        "RCCSD",
        "RLCCD",
        "RLCCSD",
        "RfpCCD",
        "RfpCCSD",
        "RpCCDLCCD",
        "RpCCDLCCSD",
    ],
)
@pytest.mark.parametrize("mol_f,basis,kwargs", test_data_rcc)
def test_ea_rcc(cls, ea_cls, mol_f, basis, kwargs, linalg_slow):
    """Test electron attachment energies for EA-CC models."""

    ncore = kwargs.get("ncore")
    alpha = kwargs.get("alpha")
    nroot = kwargs.get("nroot")
    charge = kwargs.get("charge")
    spinfree = kwargs.get("spinfree", False)

    # Load and validate reference data
    required_keys = ["e_cc", f"e_ea_{alpha}"]
    if ROOpCCD in cls:
        required_keys += ["e_pccd"]

    method = ea_cls.__name__

    expected = load_reference_data(
        method,
        mol_f,
        basis,
        charge,
        ncore=ncore,
        nroot=nroot,
        spinfree=spinfree,
        required_keys=required_keys,
    )

    # Prepare molecule
    mol_ = EA_EOMMolecule(
        mol_f, basis, linalg_slow, ncore=ncore, charge=charge
    )
    # Do RHF solotion:
    mol_.do_rhf()

    # Do CC optimization (load pCCD orbitals if required):
    mol_.do_rcc(cls, orbital_file=mol_f + "_" + basis)
    assert abs(mol_.cc.e_tot - expected["e_cc"]) < 1e-6
    if ROOpCCD in cls:
        assert abs(mol_.pccd.e_tot - expected["e_pccd"]) < 1e-5

    # Do EA_CC optimization:
    mol_.do_ea_rcc(ea_cls, alpha, nroot)

    for ind in range(nroot):
        assert (
            abs(mol_.ea_rcc.e_ea_1[ind] - expected["e_ea_1"][ind]) < 5e-6
        ), f"Attachment energy mismatch for root {ind}: expected {expected['e_ea_1'][ind]}, got {mol_.ea_rcc.e_ea_1[ind]}"
