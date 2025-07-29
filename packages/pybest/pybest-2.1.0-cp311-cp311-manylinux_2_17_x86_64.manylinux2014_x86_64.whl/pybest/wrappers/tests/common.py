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


from pybest.cc import RpCCDLCCSD
from pybest.context import context
from pybest.gbasis import (
    compute_cholesky_eri,
    compute_dipole,
    compute_eri,
    compute_kinetic,
    compute_nuclear,
    compute_nuclear_pc,
    compute_nuclear_repulsion,
    compute_overlap,
    compute_point_charges,
    compute_quadrupole,
    compute_static_embedding,
    get_charges,
    get_embedding,
    get_gobasis,
)
from pybest.linalg import CholeskyLinalgFactory, DenseLinalgFactory
from pybest.occ_model import AufbauOccModel
from pybest.utility import get_com


class Molecule:
    """Set up molecule instance that contains all quantities to perform some
    QC calculation
    """

    def __init__(self, linalg_set, basis, mol_fn, **kwargs):
        fn_xyz = context.get_fn(mol_fn)
        self.obasis = get_gobasis(basis, fn_xyz, print_basis=False)
        self.lf = linalg_set(self.obasis.nbasis)
        self.olp = compute_overlap(self.obasis)
        self.kin = compute_kinetic(self.obasis)
        self.na = compute_nuclear(self.obasis)
        if isinstance(self.lf, CholeskyLinalgFactory):
            self.eri = compute_cholesky_eri(self.obasis, threshold=1e-8)
        elif isinstance(self.lf, DenseLinalgFactory):
            self.eri = compute_eri(self.obasis)
        self.external = compute_nuclear_repulsion(self.obasis)
        self.ham = [self.kin, self.na, self.eri]
        # Read embedding if given in kwargs and remove it
        emb_fn = kwargs.pop("emb_fn", None)
        if emb_fn is not None:
            emb_xyz = context.get_fn(emb_fn)
            self.embedding_pot = get_embedding(emb_xyz)
            self.emb = compute_static_embedding(
                self.obasis, self.embedding_pot
            )
            self.ham.append(self.emb)

        # Read point charges if given in kwargs and remove it
        pc_fn = kwargs.pop("pc_fn", None)
        if pc_fn is not None:
            pc_xyz = context.get_fn(pc_fn)
            self.charges = get_charges(pc_xyz)
            self.pc = compute_point_charges(self.obasis, self.charges)
            self.ham.append(self.pc)
            # Add interaction with point charges to external
            self.external_pc = compute_nuclear_pc(self.obasis, self.charges)
            self.external += self.external_pc
        self.occ_model = AufbauOccModel(self.obasis, **kwargs)
        self.orb = [self.lf.create_orbital() for i in self.occ_model.nbasis]
        self.scf = None
        self.uhf = None
        self.dipole = None
        self.quadrupole = None
        self.pccd = None
        self.pccd_lccsd = None

    def compute_dipole(self):
        """Compute dipole integrals"""
        com = get_com(self.obasis)
        self.dipole = compute_dipole(self.obasis, x=com[0], y=com[1], z=com[2])

    def compute_quadrupole(self):
        """Compute quadrupole integrals"""
        self.quadrupole = compute_quadrupole(self.obasis, x=0.0, y=0.0, z=0.0)

    def do_scf(self, cls, *args, **kwargs):
        """Perform RHF/UHF calculation. args and kwargs required for testing
        purposes.
        """
        hf = cls(self.lf, self.occ_model)
        self.scf = hf(
            *self.ham, self.external, *self.orb, self.olp, *args, **kwargs
        )

    def do_pccd(self, pccd_cls, **kwargs):
        """Do pCCD optimization based on input class pccd_cls using this class's
        RHF solution
        """
        if self.scf is None:
            raise ValueError("No RHF solution found.")
        pccd = pccd_cls(self.lf, self.occ_model)
        self.pccd = pccd(*self.ham, self.scf, **kwargs)

    def do_pccd_lccsd(self):
        """Perform LCCSD calculation and solve the lambda equations based on
        input class pccd_cls using this class's
        pCCD solution
        """
        if self.pccd is None:
            raise ValueError("No pCCD solution found.")
        pccd_lccsd = RpCCDLCCSD(self.lf, self.occ_model)
        self.pccd_lccsd = pccd_lccsd(
            *self.ham, self.pccd, lambda_equations=True
        )
