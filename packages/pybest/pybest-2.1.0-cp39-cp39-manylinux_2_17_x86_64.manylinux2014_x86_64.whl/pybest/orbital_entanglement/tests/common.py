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


import numpy as np

from pybest.cc import RpCCDLCCSD
from pybest.context import context
from pybest.gbasis import (
    compute_eri,
    compute_kinetic,
    compute_nuclear,
    compute_nuclear_repulsion,
    compute_overlap,
    get_gobasis,
)
from pybest.geminals.roopccd import ROOpCCD
from pybest.iodata import IOData
from pybest.linalg import DenseLinalgFactory
from pybest.modelhamiltonians import Hubbard
from pybest.occ_model import AufbauOccModel
from pybest.wrappers.hf import RHF


class Molecule:
    """Set up molecule instance that contains all quantities to perform some
    QC calculation
    """

    def __init__(self, basis, mol_fn, orb_fn, ncore=0):
        fn_xyz = context.get_fn(mol_fn)
        self.obasis = get_gobasis(basis, fn_xyz, print_basis=False)
        self.lf = DenseLinalgFactory(self.obasis.nbasis)
        self.olp = compute_overlap(self.obasis)
        self.kin = compute_kinetic(self.obasis)
        self.ne = compute_nuclear(self.obasis)
        self.eri = compute_eri(self.obasis)
        self.external = compute_nuclear_repulsion(self.obasis)
        self.ham = (self.kin, self.ne, self.eri)

        fn_orb = context.get_fn(orb_fn)
        orb_ = np.fromfile(fn_orb, sep=",").reshape(
            self.obasis.nbasis, self.obasis.nbasis
        )
        self.orb_a = self.lf.create_orbital()
        self.orb_a._coeffs = orb_

        self.occ_model = AufbauOccModel(self.obasis, ncore=ncore)

        self.data = IOData(
            **{
                "orb_a": self.orb_a,
                "olp": self.olp,
                "e_core": self.external,
            }
        )

        self.pccd = None

    def do_pccd(self):
        """Perform pCCD calculation"""
        pccd = ROOpCCD(self.lf, self.occ_model)
        self.pccd = pccd(*self.ham, self.data)


class Model:
    """Set up Model hamiltonian instance that contains all quantities to
    perform some QC calculation
    """

    def __init__(self, nbasis, nel, t, v, ncore=0):
        self.lf = DenseLinalgFactory(nbasis)
        self.occ_model = AufbauOccModel(self.lf, nel=nel, ncore=ncore)

        self.modelham = Hubbard(self.lf, occ_model=self.occ_model, pbc=True)
        self.modelham.parameters = {"u": v, "hopping": t, "on_site": 0.0}

        self.one = self.modelham.compute_one_body()
        self.two = self.modelham.compute_two_body()

        self.olp = self.modelham.compute_overlap()
        self.external = 0.0

        self.ham = (self.one, self.two)

        self.orb_a = self.lf.create_orbital()

        self.data = IOData(
            **{
                "orb_a": self.orb_a,
                "olp": self.olp,
                "e_core": self.external,
            }
        )

        self.rhf = None
        self.pccd = None
        self.pccdlccsd = None

    def do_rhf(self):
        """Perform RHF calculation"""
        hf = RHF(self.lf, self.occ_model)
        self.rhf = hf(*self.ham, self.external, self.orb_a, self.olp)

    def do_pccd(self):
        """Perform pCCD calculation"""
        pccd = ROOpCCD(self.lf, self.occ_model)
        self.pccd = pccd(*self.ham, self.data)

    def do_pccdlccsd(self):
        """Perform pCCD-LCCSD calculation with lambda=True"""
        lccsd = RpCCDLCCSD(self.lf, self.occ_model)
        self.pccdlccsd = lccsd(*self.ham, self.pccd, lambda_equations=True)
