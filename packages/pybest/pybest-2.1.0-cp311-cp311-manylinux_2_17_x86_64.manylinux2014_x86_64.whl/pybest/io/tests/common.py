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
from pybest.iodata import IOData
from pybest.linalg import CholeskyLinalgFactory, DenseLinalgFactory
from pybest.occ_model import AufbauOccModel
from pybest.part.mulliken import get_mulliken_operators
from pybest.scf.hamiltonian import RScfHam, UScfHam
from pybest.scf.observable import (
    RDirectTerm,
    RExchangeTerm,
    RTwoIndexTerm,
    UDirectTerm,
    UExchangeTerm,
    UTwoIndexTerm,
)
from pybest.scf.utils import compute_1dm_hf
from pybest.utility import check_type


def compute_mulliken_charges(basis, lf, numbers, dm):
    """Compute Mulliken charges for some molecule with basis instance called basis."""
    operators = get_mulliken_operators(basis)
    populations = np.array(
        [operator.contract("ab,ab", dm) for operator in operators]
    )
    return numbers - np.array(populations)


def compute_hf_energy(mol):
    """Compute HF energy for some molecule."""
    kin = compute_kinetic(mol.basis)
    na = compute_nuclear(mol.basis)
    er = compute_eri(mol.basis)
    external = {"nn": compute_nuclear_repulsion(mol.basis)}
    if hasattr(mol, "orb_b"):
        # assuming unrestricted
        terms = [
            UTwoIndexTerm(kin, "kin"),
            UDirectTerm(er, "hartree"),
            UExchangeTerm(er, "x_hf"),
            UTwoIndexTerm(na, "ne"),
        ]
        ham = UScfHam(terms, external)
        dm_a = compute_1dm_hf(mol.orb_a)
        dm_b = compute_1dm_hf(mol.orb_b)
        ham.reset(dm_a, dm_b)
    else:
        # assuming restricted
        terms = [
            RTwoIndexTerm(kin, "kin"),
            RDirectTerm(er, "hartree"),
            RExchangeTerm(er, "x_hf"),
            RTwoIndexTerm(na, "ne"),
        ]
        ham = RScfHam(terms, external)
        dm_a = compute_1dm_hf(mol.orb_a)
        ham.reset(dm_a)
    return ham.compute_energy()


class Molecule:
    """Set up some molecule and its Hamiltonian."""

    def __init__(self, molfile, basis, lf_cls, **kwargs):
        fn = context.get_fn(f"test/{molfile}.xyz")
        self.basis = get_gobasis(basis, fn, print_basis=False)
        #
        # Define Occupation model, expansion coefficients and overlap
        #
        self.lf = lf_cls(self.basis.nbasis)
        self.occ_model = AufbauOccModel(self.basis, **kwargs)
        orb = [
            self.lf.create_orbital() for i in range(len(self.occ_model.nbasis))
        ]
        self.orb_a = orb[0]
        self.orb_b = orb[-1]
        self.olp = compute_overlap(self.basis)
        #
        # Construct Hamiltonian
        #
        kin = compute_kinetic(self.basis)
        na = compute_nuclear(self.basis)
        if isinstance(self.lf, CholeskyLinalgFactory):
            er = compute_cholesky_eri(self.basis, threshold=1e-8)
        elif isinstance(self.lf, DenseLinalgFactory):
            er = compute_eri(self.basis)
        external = compute_nuclear_repulsion(self.basis)

        self.hamiltonian = [kin, na, er, external]
        self.one = kin.copy()
        self.one.iadd(na)
        self.two = er
        self._iodata = IOData()

    @property
    def iodata(self):
        """Some IOData instance"""
        return self._iodata

    @iodata.setter
    def iodata(self, new):
        """Return IOData container containing a list of attributes specified
        in new.

        **Arguments:**
        new:
            Either a tuple containing strings (*args) or a dict (**kwargs)
            containing a string-value pair. For some arg (str) in the tuple new,
            the key `arg` is added to self.iodata with the value of self.arg
            self has to have `arg` as an attribute.
            For some kwarg (str for key, some value), the attribute `key` is
            added to self.iodata with the value of `key`. Thus, self.iodata.key
            is either generated or overwritten.
            In all tests, self.iodata is assumed to be empty.
        """
        check_type("new", new, tuple, dict)
        if isinstance(new, tuple):
            for arg in new:
                setattr(self.iodata, arg, getattr(self, arg))
        if isinstance(new, dict):
            for key in new:
                setattr(self.iodata, key, getattr(self, key))


def get_orbital_data(mol_file, orb_file, basis_file):
    """Load orbitals from file assuming same number of AOs and MOs. An instance
    of IOData is returned with the orb_a attribute.
    """
    fn_mol = context.get_fn(f"test/{mol_file}.xyz")
    fn_orb = context.get_fn(f"test/{orb_file}.txt")
    fn_bas = context.get_fn(f"test/{basis_file}")
    basis = get_gobasis(fn_bas, fn_mol, print_basis=False)
    lf = DenseLinalgFactory(basis.nbasis)
    orb_a = lf.create_orbital()
    orb_a.coeffs[:] = np.fromfile(fn_orb, sep=",").reshape(
        orb_a.nbasis, orb_a.nbasis
    )
    return IOData(**{"orb_a": orb_a, "basis": basis})
