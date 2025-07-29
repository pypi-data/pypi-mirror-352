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

from pybest.exceptions import EmptyData
from pybest.iodata import IOData
from pybest.pt import PT2b, PT2MDd, PT2MDo, PT2SDd, PT2SDo
from pybest.pt.tests.common import Molecule

test_cases = [
    (
        "nh3",
        "cc-pvdz",
        PT2SDd,
        "(sd)",
        0,
        {
            "orb_file": "nh3_ap1rog.txt",
            "e_ref": -56.288865946757,
            "e_tot": -56.39067080,
            "e_corr_s": -0.00023982,
            "e_corr_d": -0.101565033243,
            "kwargs": {},
        },
    ),
    (
        "nh3",
        "cc-pvdz",
        PT2MDd,
        "(sd)",
        0,
        {
            "orb_file": "nh3_ap1rog.txt",
            "e_ref": -56.288865946757,
            "e_tot": -56.38820919,
            "e_corr_s": -0.000349570000,
            "e_corr_d": -0.098993673243,
            "kwargs": {},
        },
    ),
    (
        "nh3",
        "cc-pvdz",
        PT2SDo,
        "(d)",
        0,
        {
            "orb_file": "nh3_ap1rog.txt",
            "e_ref": -56.288865946757,
            "e_tot": -56.40050443,
            "e_corr_d": -0.111638483243,
            "kwargs": {"singles": False},
        },
    ),
    (
        "nh3",
        "cc-pvdz",
        PT2SDo,
        "(sd)",
        0,
        {
            "orb_file": "nh3_ap1rog.txt",
            "e_ref": -56.288865946757,
            "e_tot": -56.40050594662758672,
            "e_corr_s": 0.00000000000000000,
            "e_corr_d": -0.11163999987058672,
            "kwargs": {"singles": True},
        },
    ),
    (
        "nh3",
        "cc-pvdz",
        PT2MDo,
        "(d)",
        0,
        {
            "orb_file": "nh3_ap1rog.txt",
            "e_ref": -56.288865946757,
            "e_tot": -56.395285377381,
            "e_corr_s": -0.000000000000,
            "e_corr_d": -0.106419469618,
            "kwargs": {"singles": False},
        },
    ),
    (
        "nh3",
        "cc-pvdz",
        PT2MDo,
        "(d)",
        0,
        {
            "orb_file": "nh3_ap1rog.txt",
            "e_ref": -56.288865946757,
            "e_tot": -56.395549517241,
            "e_corr_s": -0.000264322783,
            "e_corr_d": -0.106419286696,
            "kwargs": {"singles": True},
        },
    ),
    (
        "nh3",
        "cc-pvdz",
        PT2b,
        "(d)",
        0,
        {
            "orb_file": "nh3_ap1rog.txt",
            "e_ref": -56.288865946757,
            "e_tot": -56.392294846446,
            "e_corr_s": -0.00000000000,
            "e_corr_d": -0.10342893868,
            "kwargs": {"singles": False},
        },
    ),
    (
        "nh3",
        "cc-pvdz",
        PT2b,
        "(d)",
        0,
        {
            "orb_file": "nh3_ap1rog.txt",
            "e_ref": -56.288865946757,
            "e_tot": -56.392694604520,
            "e_corr_s": -0.000394757465,
            "e_corr_d": -0.103433939292,
            "kwargs": {"singles": True},
        },
    ),
    (
        "nh3",
        "cc-pvdz",
        PT2b,
        "(d)",
        0,
        {
            "orb_file": "nh3_ap1rog.txt",
            "e_ref": -56.288865946757,
            "e_tot": -56.392117900844,
            "e_corr_s": -0.00000000000,
            "e_corr_d": -0.103251993081,
            "kwargs": {"singles": False, "excludepairs": True},
        },
    ),
    (
        "nh3",
        "cc-pvdz",
        PT2b,
        "(d)",
        0,
        {
            "orb_file": "nh3_ap1rog.txt",
            "e_ref": -56.288865946757,
            "e_tot": -56.392517698981,
            "e_corr_s": -0.000394778161,
            "e_corr_d": -0.103257013058,
            "kwargs": {"singles": True, "excludepairs": True},
        },
    ),
    (
        "nh3",
        "cc-pvdz",
        PT2b,
        "(sd)",
        1,
        {
            "orb_file": "nh3_ap1rog.txt",
            "e_ref": -56.28858326584,
            "e_tot": -56.389998293967,
            "e_corr_s": -0.000355689228,
            "e_corr_d": -0.101059338891,
            "kwargs": {"singles": True, "excludepairs": True},
        },
    ),
]


@pytest.mark.parametrize("mol,basis,cls,t_,ncore,dict_", test_cases)
def test_pccd_pt2_iodata(mol, basis, cls, t_, ncore, dict_, linalg_slow):
    """Check PT2X implementation passing iodata container"""
    mol_ = Molecule(
        linalg_slow,
        basis,
        f"test/{mol}.xyz",
        f"test/{dict_['orb_file']}",
        ncore=ncore,
    )

    # Prepare IOData container
    iodata = IOData(orb_a=mol_.orb_a, olp=mol_.olp, e_core=mol_.external)
    # Do pCCD optimization:
    mol_.do_pccd(iodata)
    assert abs(mol_.pccd.e_tot - dict_["e_ref"]) < 1e-6
    # Do PTX correction on top of pCCD
    mol_.do_pccd_ptx(cls, **dict_["kwargs"])
    # Get energies from result dict
    energies = [key for key in dict_ if "e_" in key.lower()]
    for e in energies:
        assert (
            abs(getattr(mol_.pccd_ptx, e) - dict_[e]) < 1e-6
        ), f"wrong energy contribution for {e}"


@pytest.mark.parametrize("mol,basis,cls,t_,ncore,dict_", test_cases)
def test_pccd_pt2_args(mol, basis, cls, t_, ncore, dict_, linalg_slow):
    """Check PT2X implementation passing arguments"""
    mol_ = Molecule(
        linalg_slow,
        basis,
        f"test/{mol}.xyz",
        f"test/{dict_['orb_file']}",
        ncore=ncore,
    )

    # Prepare IOData container
    iodata = IOData(orb_a=mol_.orb_a, olp=mol_.olp, e_core=mol_.external)
    # Do pCCD optimization:
    mol_.do_pccd(iodata)
    assert abs(mol_.pccd.e_tot - dict_["e_ref"]) < 1e-6
    # Do PTX correction on top of pCCD using args not IOData
    args = (mol_.pccd.orb_a, mol_.pccd.olp, mol_.pccd.t_p)
    try:
        mol_.do_pccd_ptx(cls, *args, e_ref=mol_.pccd.e_tot, **dict_["kwargs"])
    except EmptyData:
        mol_.do_pccd_ptx(
            cls,
            *args,
            e_ref=mol_.pccd.e_tot,
            overlap=mol_.pccd.overlap,
            **dict_["kwargs"],
        )
    # Get energies from result dict
    energies = [key for key in dict_ if "e_" in key.lower()]
    for e in energies:
        assert (
            abs(getattr(mol_.pccd_ptx, e) - dict_[e]) < 1e-6
        ), f"wrong energy contribution for {e}"
