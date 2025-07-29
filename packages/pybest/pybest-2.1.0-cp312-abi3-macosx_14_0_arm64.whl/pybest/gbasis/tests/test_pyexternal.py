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

from numpy.testing import assert_almost_equal

from pybest import context
from pybest.gbasis import compute_nuclear_repulsion, get_gobasis


def test_nucnuc(ref_value: float = 9.138880475737013):
    fn = context.get_fn("test/h2o_ccdz.xyz")
    obs = get_gobasis("cc-pvdz", fn, print_basis=False)

    nucnuc = compute_nuclear_repulsion(obs)

    assert_almost_equal(
        nucnuc,
        ref_value,
        decimal=9,
        err_msg="Nuclear repulsion energy is not as expected. Double check Libint2 version! PyBEST expects libint v2.9.0",
    )
