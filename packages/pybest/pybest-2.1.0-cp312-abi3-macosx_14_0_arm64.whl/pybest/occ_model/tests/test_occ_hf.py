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
import pytest

from pybest.context import context
from pybest.gbasis import (
    compute_eri,
    compute_kinetic,
    compute_nuclear,
    compute_nuclear_repulsion,
    compute_overlap,
    get_gobasis,
)
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import (
    AufbauOccModel,
    FermiOccModel,
    FixedOccModel,
    FractionalOccModel,
)
from pybest.wrappers import UHF


class Molecule:
    def __init__(self, molfile, basis_name, occ_cls, **kwargs):
        fn = context.get_fn(f"test/{molfile}.xyz")
        basis = get_gobasis(basis_name, fn, print_basis=False)
        #
        # Define Occupation model, expansion coefficients and overlap
        #
        self.lf = DenseLinalgFactory(basis.nbasis)
        self.occ_model = occ_cls(basis, **kwargs)
        self.orb = [
            self.lf.create_orbital(basis.nbasis)
            for i in range(len(self.occ_model.nbasis))
        ]
        self.olp = compute_overlap(basis)
        #
        # Construct Hamiltonian
        #
        kin = compute_kinetic(basis)
        na = compute_nuclear(basis)
        er = compute_eri(basis)
        external = compute_nuclear_repulsion(basis)

        self.hamiltonian = [kin, na, er, external]


ref_e_o2_dz = {
    "e_kin": 149.575744206055,
    "e_hartree": 100.421461361941,
    "e_x_hf": -16.348044840042,
    "e_ne": -411.500937624523,
    "e_tot": -149.628992314170,
}


test_occ_model = [
    (AufbauOccModel, {"alpha": 2}),
    # We have to use integer occ numbers otherwise test will fail
    (FractionalOccModel, {"nocc_a": 9, "nocc_b": 7}),
    # Equivalent to the Aufbau occupation model otherwise test will fail
    (
        FixedOccModel,
        {
            "occ_a": np.array([1, 1, 1, 1, 1, 1, 1, 1, 1]),
            "occ_b": np.array([1, 1, 1, 1, 1, 1, 1]),
        },
    ),
    (FermiOccModel, {"alpha": 2}),
    (FermiOccModel, {"alpha": 2, "temperature": 300}),
    (FermiOccModel, {"alpha": 2, "temperature": 300, "delta_t": 40}),
    (FermiOccModel, {"alpha": 2, "temperature": 300, "method": "fon"}),
]

test_molecules = [
    ("o2_ccdz", "cc-pvdz", ref_e_o2_dz),
]

test_diis = [("plain"), ("cdiis"), ("ediis2")]


@pytest.mark.parametrize("mol,basis,expected", test_molecules)
@pytest.mark.parametrize("occ_cls,kwargs", test_occ_model)
@pytest.mark.parametrize("diis", test_diis)
def test_occ_model_uhf(mol, basis, expected, occ_cls, kwargs, diis):
    """Check if various occuption models result in the proper energy
    contributions. We test for several features:
        * UHF
        * DIIS
        * OccModel

    Note: the AufbauSpinOccModel is not tested as it does not converge to
    the proper ground state.
    """
    molecule = Molecule(mol, basis, occ_cls, **kwargs)

    scf_ = UHF(molecule.lf, molecule.occ_model)

    scf = scf_(*molecule.hamiltonian, molecule.olp, *molecule.orb, diis=diis)

    for key, value in expected.items():
        assert abs(value - getattr(scf, key)) < 1e-7
