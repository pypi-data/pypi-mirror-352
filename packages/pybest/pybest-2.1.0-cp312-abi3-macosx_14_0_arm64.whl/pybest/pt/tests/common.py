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


import numpy as np

from pybest.context import context
from pybest.gbasis import (
    compute_cholesky_eri,
    compute_eri,
    compute_kinetic,
    compute_nuclear,
    compute_nuclear_repulsion,
    compute_overlap,
    get_gobasis,
)
from pybest.geminals import ROOpCCD
from pybest.linalg import CholeskyLinalgFactory, DenseLinalgFactory
from pybest.occ_model import AufbauOccModel
from pybest.pt.mp2 import RMP2
from pybest.wrappers import RHF


class Molecule:
    """Set up molecule instance that contains all quantities to perform some
    QC calculation
    """

    def __init__(self, linalg_set, basis, mol_fn, orb_fn, ncore=0):
        fn_xyz = context.get_fn(mol_fn)
        self.obasis = get_gobasis(basis, fn_xyz, print_basis=False)
        self.lf = linalg_set(self.obasis.nbasis)
        self.olp = compute_overlap(self.obasis)
        self.kin = compute_kinetic(self.obasis)
        self.na = compute_nuclear(self.obasis)
        if isinstance(self.lf, CholeskyLinalgFactory):
            self.er = compute_cholesky_eri(self.obasis, threshold=1e-8)
        elif isinstance(self.lf, DenseLinalgFactory):
            self.er = compute_eri(self.obasis)
        self.external = compute_nuclear_repulsion(self.obasis)
        self.ham = (self.kin, self.na, self.er)

        self.occ_model = AufbauOccModel(self.obasis, ncore=ncore)

        fn_orb = context.get_fn(orb_fn)
        orb_ = np.fromfile(fn_orb, sep=",").reshape(
            self.obasis.nbasis, self.obasis.nbasis
        )
        self.orb_a = self.lf.create_orbital()
        self.orb_a.coeffs[:] = orb_
        # add anything; will be overwritten by RHF solver; otherwise restart
        # does not work
        self.orb_a.energies[:] = 1.0
        self.orb_a.occupations[: self.occ_model.nocc[0]] = 1.0

        # store RHF results as IOData container
        self.rhf = None
        self.pccd = None
        self.pccd_ptx = None

    def do_rhf(self):
        """Store RHF as IOData container"""
        hf = RHF(self.lf, self.occ_model)
        self.rhf = hf(*self.ham, self.external, self.orb_a.copy(), self.olp)

    def do_mp2(self, **kwargs):
        """Do MP2 calculation"""
        fos = kwargs.get("fos", 1.0)
        fss = kwargs.get("fss", 1.0)
        natorb = kwargs.get("natorb", False)
        relaxation = kwargs.get("relaxation", False)
        orb_a = kwargs.get("orb_a", None)
        pt2 = RMP2(self.lf, self.occ_model)
        self.mp2 = pt2(
            *self.ham,
            self.rhf,
            orb_a,
            fos=fos,
            fss=fss,
            natorb=natorb,
            relaxation=relaxation,
        )

    def do_pccd(self, iodata=None):
        """Perform pCCD calculation"""
        pccd = ROOpCCD(self.lf, self.occ_model)
        if iodata is None:
            iodata = self.rhf
        self.pccd = pccd(*self.ham, iodata)

    def do_pccd_ptx(self, cls, *args, **kwargs):
        """Perform pCCD-PTX calculation. We always test for one, so we can
        overwrite this instance.
        """
        ptx = cls(self.lf, self.occ_model)
        if len(args):
            self.pccd_ptx = ptx(*self.ham, *args, **kwargs)
        else:
            self.pccd_ptx = ptx(*self.ham, self.pccd, **kwargs)
