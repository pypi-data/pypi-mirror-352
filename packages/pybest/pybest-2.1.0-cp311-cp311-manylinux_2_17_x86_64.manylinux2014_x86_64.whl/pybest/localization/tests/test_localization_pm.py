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
#


import numpy as np
import pytest

from pybest.localization import PipekMezey
from pybest.localization.tests.common import prepare_olp, prepare_ref_orbitals
from pybest.occ_model import AufbauOccModel
from pybest.part.mulliken import get_mulliken_operators

testdata_pm = [
    (
        "water.xyz",
        "cc-pvdz",
        0,
        {"hf": "water_hf.molden", "loc": "water_loc_fc0.molden"},
    ),
    (
        "water.xyz",
        "cc-pvdz",
        1,
        {"hf": "water_hf.molden", "loc": "water_loc_fc1.molden"},
    ),
]


def do_pm_localization(iodata, linalg_set, ncore):
    # Read in reference HF orbitals from molden file
    hf = prepare_ref_orbitals(iodata["hf"])
    basis = hf.basis
    occ_model = AufbauOccModel(basis, ncore=ncore)

    lf = linalg_set(basis.nbasis)
    hf.olp = prepare_olp(lf, basis)

    # check HF orbitals
    hf.orb_a.check_orthonormality(hf.olp, 1e-8)

    # localization:
    mulliken = get_mulliken_operators(basis)
    loc = PipekMezey(lf, occ_model, mulliken)
    # occupied block
    loc(hf, "occ")
    # virtual block
    loc(hf, "virt")

    return hf


@pytest.mark.parametrize("mol,basis,ncore,expected", testdata_pm)
def test_localization_pm_orthogonality(mol, basis, ncore, expected, linalg):
    # PM localization
    hf = do_pm_localization(expected, linalg, ncore)

    # check orthogonality
    hf.orb_a.check_orthonormality(hf.olp, 1e-8)


@pytest.mark.parametrize("mol,basis,ncore,expected", testdata_pm)
def test_localization_pm(mol, basis, ncore, expected, linalg):
    # PM localization
    hf = do_pm_localization(expected, linalg, ncore)

    with pytest.raises(AssertionError):
        hf.orb_a.check_orthonormality(hf.olp, 1e-20)
    # check with reference data
    loc_orb_ref = prepare_ref_orbitals(expected["loc"]).orb_a
    assert np.allclose(hf.orb_a.coeffs, loc_orb_ref.coeffs)
