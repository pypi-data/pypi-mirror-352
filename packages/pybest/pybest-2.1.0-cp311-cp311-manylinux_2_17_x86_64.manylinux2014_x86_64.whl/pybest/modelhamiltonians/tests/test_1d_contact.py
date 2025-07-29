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
from numpy.testing import assert_almost_equal

from pybest.geminals import ROOpCCD
from pybest.linalg import DenseLinalgFactory
from pybest.modelhamiltonians import ContactInteraction1D
from pybest.occ_model import AufbauOccModel
from pybest.wrappers import RHF


def do_rhf(lf, occ_model, one, two, orb, olp):
    """Performs RHF calculations for given integrals"""
    rhf = RHF(lf, occ_model)
    rhf_ = rhf(one, two, orb, olp, 0.0)
    return rhf_


def potential(r):
    """Defines a function used for a potential inside Contact Interaction
    Hamiltonian"""
    return 0.5 * r**2


test_cases = [
    # (nbasis, fermions, g, grid, mass, potential, reference)
    (10, 2, 2.0, (-6.0, 6.0, 1e-2), 1, potential, 1.5366053492863712),
    (10, 2, 0.0, (-6.0, 6.0, 1e-2), 1, potential, 0.99999141685880055),
    (10, 2, -4.0, (-6.0, 6.0, 1e-2), 1, potential, -1.8165171976234478),
    (10, 4, -4.0, (-6.0, 6.0, 1e-2), 1, potential, -2.210034013408),
    (10, 4, 0.0, (-6.0, 6.0, 1e-2), 1, potential, 4.000000000005047),
    (10, 4, 4.0, (-6.0, 6.0, 1e-2), 1, potential, 7.175816796793814),
]


@pytest.mark.parametrize(
    "no_orbs, no_fermions, g_coupling, grid, mass, potential, reference",
    test_cases,
)
def test_1d_contact(
    no_orbs, no_fermions, g_coupling, grid, mass, potential, reference
):
    lf = DenseLinalgFactory(no_orbs)
    occ_model = AufbauOccModel(lf, nel=no_fermions)
    modelham = ContactInteraction1D(
        lf=lf,
        occ_model=occ_model,
        domain=grid,
        mass=mass,
        potential=potential,
    )
    olp = modelham.compute_overlap()
    one = modelham.compute_one_body()
    two = modelham.compute_two_body()
    orb_a = lf.create_orbital()

    # scale by coupling strength
    two.iscale(g_coupling)

    # do RHF
    result = do_rhf(lf, occ_model, one, two, orb_a, olp)
    # do oo-pCCD
    oopccd = ROOpCCD(lf, occ_model)
    results = oopccd(one, two, result)

    # reasonable accuracy, results grid dependent
    assert_almost_equal(results.e_tot, reference, decimal=3)
