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


import pybest.gbasis as pybest_basis
from pybest.context import context
from pybest.linalg import CholeskyLinalgFactory, DenseLinalgFactory
from pybest.occ_model import AufbauOccModel


class Molecule:
    def __init__(self, filen, nbasis, linalg_set, ncore=0, nactc=0):
        fn = context.get_fn(f"test/{filen}")
        self.obasis = pybest_basis.get_gobasis(nbasis, fn, print_basis=False)
        self.lf = linalg_set(self.obasis.nbasis)
        self.olp = pybest_basis.compute_overlap(self.obasis)
        self.kin = pybest_basis.compute_kinetic(self.obasis)
        self.na = pybest_basis.compute_nuclear(self.obasis)
        self.external = pybest_basis.compute_nuclear_repulsion(self.obasis)

        if isinstance(self.lf, CholeskyLinalgFactory):
            self.er = pybest_basis.compute_cholesky_eri(
                self.obasis, threshold=1e-8
            )
        elif isinstance(self.lf, DenseLinalgFactory):
            self.er = pybest_basis.compute_eri(self.obasis)

        self.orb_a = self.lf.create_orbital()

        self.occ_model = AufbauOccModel(self.obasis, ncore=ncore, nactc=nactc)
