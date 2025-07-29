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

from pybest.context import context
from pybest.exceptions import ArgumentError, BasisError
from pybest.gbasis import get_gobasis
from pybest.linalg import DenseLinalgFactory
from pybest.linalg.cholesky import CholeskyLinalgFactory
from pybest.utility.check_data import check_lf


def test_check_gobasis():
    fn = context.get_fn("test/h2o_ccdz.xyz")
    # Dry runs (basis set consistencies are checked in basis tests):
    get_gobasis("cc-pVDZ", fn, print_basis=False)

    with pytest.raises(BasisError):
        get_gobasis("cc-pVDZ", fn, dummy=0, print_basis=False)
    with pytest.raises(BasisError):
        get_gobasis("cc-pVDZ", fn, active_fragment=0, print_basis=False)
    with pytest.raises(BasisError):
        get_gobasis(
            "cc-pVDZ", fn, active_fragment=[0], dummy=[1], print_basis=False
        )

    # basis set does not contain information about atom and has to fail:
    # this error is only captured in check_gobasis function
    fn = context.get_fn("test/u2.xyz")
    with pytest.raises(BasisError):
        get_gobasis("cc-pVDZ", fn, print_basis=False)


lf_dense = DenseLinalgFactory(5)
lf_chol = CholeskyLinalgFactory(5)
ind_dense = lf_dense.create_four_index()
ind_chol = lf_chol.create_four_index(nvec=10)

test_cases_lf_pass = [
    (lf_dense, ind_dense),
    (lf_chol, ind_chol),
]

test_cases_lf_raise = [
    (lf_chol, ind_dense),
    (lf_dense, ind_chol),
]


@pytest.mark.parametrize("lf, operand", test_cases_lf_pass)
def test_check_lf_pass(lf, operand):
    """Check correct linalg-fourindex pair (should pass).

    Args:
        lf (LinalgFactory): Either Cholesky or Dense
        operand (FourIndex): Either Cholesky or Dense
    """
    check_lf(lf, operand)


@pytest.mark.parametrize("lf, operand", test_cases_lf_raise)
def test_check_lf_raise(lf, operand):
    """Check incorrect linalg-fourindex pair (should fail).

    Args:
        lf (LinalgFactory): Either Cholesky or Dense
        operand (FourIndex): Either Cholesky or Dense
    """
    with pytest.raises(ArgumentError):
        check_lf(lf, operand)
