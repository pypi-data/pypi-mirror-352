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

from pybest.linalg import DenseLinalgFactory
from pybest.modelhamiltonians import Hubbard
from pybest.occ_model import AufbauOccModel
from pybest.wrappers import RHF


def do_rhf(lf, occ_model, one, two, orb, olp):
    rhf = RHF(lf, occ_model)
    rhf_ = rhf(one, two, orb, olp, 0.0)
    return rhf_


test_cases = [
    # (t, u, pbc, sites, filling)
    (-1, 2, True, 10, 10, {"e_tot": -7.94427}),
    (-1, 2, True, 20, 10, {"e_tot": -15.580588085361}),
    (-1, 2, False, 10, 10, {"e_tot": -7.0533}),
    (-1, 2, False, 20, 10, {"e_tot": -15.033906656272}),
]


@pytest.mark.parametrize("t, U, pbc, sites, filling, expected", test_cases)
def test_1d_hubbard_hamiltonian(t, U, pbc, sites, filling, expected):
    lf = DenseLinalgFactory(sites)
    occ_model = AufbauOccModel(lf, nel=filling)

    modelham = Hubbard(lf, occ_model=occ_model, pbc=pbc)
    modelham.parameters = {"on_site": 0.0, "hopping": t, "u": U}

    orb_a = lf.create_orbital(sites)
    olp = modelham.compute_overlap()

    kin = modelham.compute_one_body()
    eri = modelham.compute_two_body()

    # Test the half-filled 1-D Hubbard model Hamiltonian

    result = do_rhf(lf, occ_model, kin, eri, orb_a, olp)

    assert abs(result.e_ref - expected["e_tot"]) < 1e-4
    assert abs(result.e_tot - expected["e_tot"]) < 1e-4
