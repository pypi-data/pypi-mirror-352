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


from pybest.context import context
from pybest.gbasis import (
    compute_eri,
    compute_kinetic,
    compute_nuclear,
    compute_nuclear_repulsion,
    compute_overlap,
    get_gobasis,
)
from pybest.geminals import ROOpCCD
from pybest.geminals.rpccd import RpCCD
from pybest.iodata import IOData
from pybest.linalg.dense.dense_linalg_factory import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel
from pybest.wrappers import RHF


class Molecule:
    """Set some molecule."""

    def __init__(self, basis, filen="test/h2.xyz", **kwargs):
        fn_xyz = context.get_fn(filen)
        self.obasis = get_gobasis(basis, fn_xyz, print_basis=False)
        self.lf = DenseLinalgFactory(self.obasis.nbasis)

        self.olp = compute_overlap(self.obasis)
        self.kin = compute_kinetic(self.obasis)
        self.ne = compute_nuclear(self.obasis)
        self.eri = compute_eri(self.obasis)
        self.external = compute_nuclear_repulsion(self.obasis)
        self.hamiltonian = [self.kin, self.ne, self.eri]

        self.orb_a = self.lf.create_orbital()
        # access ncore explicitly so that old and new tests work
        ncore = kwargs.pop("ncore", 0)
        self.occ_model = AufbauOccModel(self.obasis, ncore=ncore, **kwargs)

        self.one = self.kin.copy()
        self.one.iadd(self.ne)

        self.rhf = None

        self.data = IOData(
            **{"orb_a": self.orb_a, "olp": self.olp, "e_core": self.external}
        )

    def do_hf(self):
        """Do a RHF calculation and store result in self.rhf"""
        hf = RHF(self.lf, self.occ_model)
        self.rhf = hf(*self.hamiltonian, self.external, self.olp, self.orb_a)

    def do_pccd(self, *args, **kwargs):
        """Do pCCD optimization"""
        pccd = RpCCD(self.lf, self.occ_model)
        self.pccd = pccd(
            self.kin, self.ne, self.eri, self.rhf, *args, **kwargs
        )

    def do_oopccd(self, *args, **kwargs):
        """Do oo-pCCD optimization"""
        pccd = ROOpCCD(self.lf, self.occ_model)
        self.oopccd = pccd(
            self.kin, self.ne, self.eri, self.rhf, *args, **kwargs
        )

    def do_oopccd_restart(self, *args, **kwargs):
        """Do pCCD optimization after restart"""
        pccd = ROOpCCD(self.lf, self.occ_model)
        self.oopccd = pccd(self.kin, self.ne, self.eri, *args, **kwargs)

    def read_oopccd(self, filename):
        data = IOData.from_file(context.get_fn(f"test/{filename}"))
        pccd = ROOpCCD(self.lf, self.occ_model)
        self.oopccd = pccd(
            self.kin,
            self.ne,
            self.eri,
            self.olp,
            data.orb_a,
            e_core=0.0,
            maxiter={"orbiter": 0},
        )
