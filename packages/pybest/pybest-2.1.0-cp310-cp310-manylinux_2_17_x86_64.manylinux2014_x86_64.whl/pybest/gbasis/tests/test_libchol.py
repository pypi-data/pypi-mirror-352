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

import pybest
import pybest.gbasis.cholesky_eri as cholesky_module
import pybest.gbasis.dense_ints as dense_module
import pybest.gbasis.gobasis as basis_module
import pybest.iodata as io_module

H2O_GEOMETRY = """
3
# H2O molecule
O 	0.0000 	 0.0000  0.1197
H 	0.0000 	 0.7616 -0.4786
H 	0.0000 	-0.7616 -0.4786
""".strip()

H2_GEOMETRY = """
2
# H2 molecule
H 	0.0000 	 0.0000   0.3710
H 	0.0000 	 0.0000  -0.3710
""".strip()

BSETS_H2 = ["cc-pvdz"]
BSETS_H2O = BSETS_H2
CD_THRESH = [1e-3, 1e-4, 1e-5, 1e-6]


def get_4idx_eri(geometry_str, basis_str):
    """[summary]

    Arguments:
        geometry_str {[type]} -- [description]
        basis_str {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    mol = io_module.IOData.from_str(geometry_str)
    basis = basis_module.get_gobasis(basis_str, mol)
    eri = dense_module.compute_eri(basis)
    return basis, eri._array


def assert_cd_eri(cd_eri, ref_eri, precision):
    # FML PyBEST is using 1212
    tested_eri = np.einsum("Qpq,Qrs->prqs", cd_eri, cd_eri, optimize=True)
    residual_eri = tested_eri - ref_eri
    frobenius_norm = np.linalg.norm(residual_eri)
    max_diff = abs(residual_eri).max()
    print("")
    print(f"FROB. NORM: {frobenius_norm:.3e}")
    print(f"MAX   DIFF: {max_diff:.3e}")
    assert np.allclose(ref_eri, tested_eri, atol=precision, rtol=precision)
    return frobenius_norm, max_diff


def compute_cholesky(*args, **kwargs):
    return cholesky_module.compute_cholesky_eri(*args, **kwargs)


@pytest.mark.skipif(
    not cholesky_module.PYBEST_CHOLESKY_ENABLED,
    reason="Cholesky-decomposition ERI are not available. Build libchol and re-run build --enable-cholesky",
)
def test_static_file():
    fn = pybest.context.get_fn("test/h2o_ccdz.xyz")
    obs = basis_module.get_gobasis("cc-pVDZ", fn, print_basis=False)

    CD_THRESH = 1e-3
    cd_eri = compute_cholesky(obs, threshold=CD_THRESH)

    # load reference data
    fnints = pybest.context.get_fn("test/ints_h2o_eri.txt")
    ref = np.fromfile(fnints, sep=",").reshape(24, 24, 24, 24)

    assert_cd_eri(cd_eri._array, ref, CD_THRESH)


@pytest.mark.skipif(
    not cholesky_module.PYBEST_CHOLESKY_ENABLED,
    reason="Cholesky-decomposition ERI are not available. Build libchol and re-run build --enable-cholesky",
)
@pytest.mark.parametrize(
    "basis,precision",
    [(basis, precision) for basis in BSETS_H2 for precision in CD_THRESH],
)
def test_cd_eri_h2(basis, precision):
    basis, ref_dense_eri = get_4idx_eri(H2_GEOMETRY, basis)
    cd_eri = compute_cholesky(basis, threshold=precision)
    _frob_norm, _max_diff = assert_cd_eri(
        cd_eri._array, ref_dense_eri, precision=precision
    )


@pytest.mark.skipif(
    not cholesky_module.PYBEST_CHOLESKY_ENABLED,
    reason="Cholesky-decomposition ERI are not available. Build libchol and re-run build --enable-cholesky",
)
@pytest.mark.parametrize(
    "basis,precision",
    [(basis, precision) for basis in BSETS_H2O for precision in CD_THRESH],
)
def test_cd_eri_h2o(basis, precision):
    basis, ref_dense_eri = get_4idx_eri(H2O_GEOMETRY, basis)
    cd_eri = compute_cholesky(basis, threshold=precision)
    _frob_norm, _max_diff = assert_cd_eri(
        cd_eri._array, ref_dense_eri, precision=precision
    )


# single atom tests

cc_pvdz_atoms = [
    "H",
    "He",
    # second row
    "Li",
    "Be",
    "B",
    "C",
    "N",
    "O",
    "F",
    "Ne",
    # third row
    "Na",
    "Mg",
    "Al",
    "Si",
    "P",
    "S",
    "Cl",
    "Ar",
]
aug_cc_pvtz_atoms = ["H", "He", "B", "C", "N", "O", "F", "Ne"]
precisions = [1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8, 1e-9]


@pytest.mark.skipif(
    not cholesky_module.PYBEST_CHOLESKY_ENABLED,
    reason="Cholesky-decomposition ERI are not available. Build libchol and re-run build --enable-cholesky",
)
@pytest.mark.parametrize(
    "atom,precision",
    [(atom, precision) for atom in cc_pvdz_atoms for precision in precisions],
)
def test_cd_eri_cc_pvdz(atom, precision, basis="cc-pvdz"):
    geometry = """
1
# test atom
{} 0.000 0.000 0.000
""".strip()
    basis, ref_dense_eri = get_4idx_eri(geometry.format(atom), basis)
    cd_eri = compute_cholesky(basis, threshold=precision)
    _frob_norm, _max_diff = assert_cd_eri(
        cd_eri._array, ref_dense_eri, precision=precision
    )


@pytest.mark.skipif(
    not cholesky_module.PYBEST_CHOLESKY_ENABLED,
    reason="Cholesky-decomposition ERI are not available. Build libchol and re-run build --enable-cholesky",
)
@pytest.mark.parametrize(
    "atom,precision",
    [
        (atom, precision)
        for atom in aug_cc_pvtz_atoms
        for precision in precisions
    ],
)
def test_cd_eri_avtz(atom, precision, basis="augcc-pvtz"):
    geometry = """
1
# test atom
{} 0.000 0.000 0.000
""".strip()
    basis, ref_dense_eri = get_4idx_eri(geometry.format(atom), basis)
    cd_eri = compute_cholesky(basis, threshold=precision)
    _frob_norm, _max_diff = assert_cd_eri(
        cd_eri._array, ref_dense_eri, precision=precision
    )
