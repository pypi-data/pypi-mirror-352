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


from pybest.context import context
from pybest.gbasis import compute_overlap
from pybest.iodata import IOData


def prepare_olp(lf, basis):
    olp = compute_overlap(basis)

    return olp


def prepare_ref_orbitals(filen):
    fn_molden = context.get_fn(f"test/{filen}")
    data = IOData.from_file(fn_molden)

    return data
