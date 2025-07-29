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

# Detailed changelog:
# 12/2024: This file has been written by Somayeh Ahmadkhani (original version)
# 05/2025: This file has been updated by Somayeh Ahmadkhani (original version)


import numpy as np
import pytest

from pybest.ee_jacobian import JacobianpCCD, JacobianpCCDS
from pybest.properties import LRpCCD, LRpCCDS
from pybest.tests.common import load_reference_data

from .common import PropertyMolecule

# Testing transition dipole moments and excitation energies using the linear response module,
# For pCCD and pCCDS references, for a water molecule in the cc-pVDZ basis set.

test_set = [
    (
        "water",
        "cc-pvdz",
        {"charge": 0, "ncore": -1, "nroot": 0},
    ),
]


@pytest.mark.parametrize(
    "cls,cls_jac,ref",
    [(LRpCCD, JacobianpCCD, "pccd"), (LRpCCDS, JacobianpCCDS, "pccds")],
)
@pytest.mark.parametrize("mol_f,basis,kwargs", test_set)
def test_tranision_dipole_moment(
    cls, cls_jac, ref, mol_f, basis, kwargs, linalg
):
    """Test transition dipole moments and excitation energies using the linear response module,
    as well as pCCD and pCCDS references, for a water molecule in the cc-pVDZ basis set.

    Args:
        cls (type): Class representing the orbital energy method (LRpCCD and LRpCCDS).
        ref (str): Reference method label used in property calculations ( "pccd" and "pccds").
        mol_f (str): Molecule identifier (e.g., "water").
        basis (str): Basis set to be used (e.g., "cc-pvdz").
        kwargs (dict): Dictionary containing:
            - ncore (int): Number of frozen core orbitals (-1 to autodetect).
            - nroot (int): Number of excited states/roots.
            - charge (int): Total molecular charge.
        linalg (Any): Linear algebra backend or solver instance.
    """

    ncore = kwargs.get("ncore")
    nroot = kwargs.get("nroot")
    charge = kwargs.get("charge")

    # Use auto_ncore feature by setting ncore=-1
    mol = PropertyMolecule(mol_f, basis, linalg, charge=charge, ncore=ncore)
    mol.do_rhf()
    mol.read_molden(f"{mol_f}_pccd")
    mol.do_pccd()
    mol.do_lr_dipole_moment(cls, cls_jac, ref)

    expected = load_reference_data(
        method="series",
        molecule_name=mol_f,
        basis=basis,
        ncore=ncore,
        charge=charge,
        nroot=nroot,
    )

    params = ["e_ee", "mu_t"]

    for param in params:
        # Dynamically access the results using getattr
        tdm = getattr(mol.out_tdm, param)
        data = expected[f"{param}_{ref}"]
        for val_ref, val_calc in zip(data, tdm):
            assert np.allclose(
                val_ref,
                val_calc,
                atol=1e-5,
            ), f"Wrong pCCD {param} for {cls}."
