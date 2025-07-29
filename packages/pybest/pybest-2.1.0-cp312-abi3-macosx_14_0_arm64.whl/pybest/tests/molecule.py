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
# The testing framework has been originally written by Julia Szczuczko (see CHANGELOG).


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
from pybest.linalg import CholeskyLinalgFactory
from pybest.occ_model import AufbauOccModel
from pybest.wrappers import RHF


class BaseMolecule:
    def __init__(self, molfile, basis, lf_cls, **kwargs):
        self._initialize_obasis(molfile, basis)
        self.lf = lf_cls(self.basis.nbasis)
        self.occ_model = AufbauOccModel(self.basis, **kwargs)
        self.orb = [self.lf.create_orbital(self.basis.nbasis)]
        # Save orb_a explicitly
        self.orb_a = self.orb[0]

        self.olp = compute_overlap(self.basis)

        # Construct Hamiltonian
        self._initialize_hamiltonian()

        # Flexible property storage
        self.properties = {}  # To store submodule-specific properties
        self.results = {}  # To store calculation results

        self.hf = None

    def _initialize_obasis(self, molfile, basis):
        """Initialize the orbital basis set."""
        fn = context.get_fn(f"test/{molfile}.xyz")
        self.basis = get_gobasis(basis, fn, print_basis=False)

    def _initialize_hamiltonian(self):
        """Construct the Hamiltonian components."""
        self.kin = compute_kinetic(self.basis)
        self.ne = compute_nuclear(self.basis)
        eri = (
            compute_cholesky_eri(self.basis, threshold=1e-8)
            if isinstance(self.lf, CholeskyLinalgFactory)
            else compute_eri(self.basis)
        )
        self.external = compute_nuclear_repulsion(self.basis)

        self.hamiltonian = [self.kin, self.ne, eri, self.external]
        self.one = self.kin.copy()
        self.one.iadd(self.ne)
        self.two = eri

    def set_property(self, name, value):
        """Set a submodule-specific property."""
        self.properties[name] = value

    def get_property(self, name):
        """Get a submodule-specific property."""
        return self.properties.get(name)

    def add_result(self, name, result):
        """Store a result for later retrieval."""
        self.results[name] = result

    def get_result(self, name):
        """Retrieve a stored result."""
        return self.results.get(name)

    def run_task(self, task_name, *args, **kwargs):
        """Run a submodule-specific task."""
        if not hasattr(self, task_name):
            raise ValueError(f"Task {task_name} is not defined.")
        return getattr(self, task_name)(*args, **kwargs)

    # Common utilities
    def do_rhf(self):
        """Do RHF optimization"""
        hf = RHF(self.lf, self.occ_model)
        self.hf = hf(*self.hamiltonian, self.olp, *self.orb)
