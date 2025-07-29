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

from pybest.ea_eom import RDEApCCD, REApCCD
from pybest.ea_eom.dea_pccd0 import RDEApCCD0
from pybest.ea_eom.dea_pccd2 import RDEApCCD2
from pybest.ea_eom.dea_pccd4 import RDEApCCD4
from pybest.ea_eom.sea_pccd1 import REApCCD1
from pybest.ea_eom.sea_pccd3 import REApCCD3
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel

test_data_alpha = [
    (REApCCD, {"alpha": 1}, 1),
    (REApCCD, {"alpha": 3}, 3),
    (RDEApCCD, {"alpha": 0}, 0),
    (RDEApCCD, {"alpha": 2}, 2),
    (RDEApCCD, {"alpha": 4}, 4),
]


@pytest.mark.parametrize("cls,kwargs,expected", test_data_alpha)
def test_alpha(cls, kwargs, expected):
    """Check if alpha agrees after REApCCD/RDEApCCD inits."""
    # some preliminaries
    lf = DenseLinalgFactory(10)
    occ_model = AufbauOccModel(lf, nel=8, ncore=0)
    # Initialize empty class
    eacc = cls(lf, occ_model, **kwargs)

    assert eacc.alpha == expected


test_data_instance = [
    (REApCCD, {"alpha": 1}, REApCCD1),
    (REApCCD, {"alpha": 3}, REApCCD3),
    (RDEApCCD, {"alpha": 0}, RDEApCCD0),
    (RDEApCCD, {"alpha": 2}, RDEApCCD2),
    (RDEApCCD, {"alpha": 4}, RDEApCCD4),
]


@pytest.mark.parametrize("cls,kwargs,expected", test_data_instance)
def test_instance(cls, kwargs, expected):
    """Check if __new__ overwrite works properly."""
    # some preliminaries
    lf = DenseLinalgFactory(10)
    occ_model = AufbauOccModel(lf, nel=8, ncore=0)
    # Initialize empty class
    eacc = cls(lf, occ_model, **kwargs)

    assert isinstance(eacc, expected)
