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
    compute_eri,
    compute_kinetic,
    compute_nuclear,
    compute_nuclear_repulsion,
    compute_overlap,
    get_gobasis,
)
from pybest.linalg import DenseLinalgFactory
from pybest.occ_model import AufbauOccModel
from pybest.scf.guess import guess_core_hamiltonian
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


def prepare_hf(basis_name, molfile, *nocc, skip_guess=False, **kwargs_o_m):
    fn = context.get_fn(molfile)
    basis = get_gobasis(basis_name, fn, print_basis=False)
    #
    # Define Occupation model, expansion coefficients and overlap
    #
    lf = DenseLinalgFactory(basis.nbasis)
    occ_model = AufbauOccModel(basis, **kwargs_o_m)
    orb = [
        lf.create_orbital(basis.nbasis) for i in range(len(occ_model.nbasis))
    ]
    olp = compute_overlap(basis)
    #
    # Construct Hamiltonian
    #
    kin = compute_kinetic(basis)
    na = compute_nuclear(basis)
    er = compute_eri(basis)
    external = {"nn": compute_nuclear_repulsion(basis)}
    if len(occ_model.nbasis) == 1:
        terms = [
            RTwoIndexTerm(kin, "kin"),
            RDirectTerm(er, "hartree"),
            RExchangeTerm(er, "x_hf"),
            RTwoIndexTerm(na, "ne"),
        ]
        ham = RScfHam(terms, external)
    else:
        terms = [
            UTwoIndexTerm(kin, "kin"),
            UDirectTerm(er, "hartree"),
            UExchangeTerm(er, "x_hf"),
            UTwoIndexTerm(na, "ne"),
        ]
        ham = UScfHam(terms, external)
    #
    # Perform initial guess
    #
    if not skip_guess:
        guess_core_hamiltonian(olp, kin, na, *orb)
    #
    # Return output for HF calculations
    #

    return lf, olp, ham, occ_model, orb


def get_ref_coeffs(filename, lf):
    orb = lf.create_orbital()
    fn_orb = context.get_fn(filename)
    orb.coeffs[:] = np.fromfile(fn_orb, sep=",").reshape(
        orb.nbasis, orb.nbasis
    )
    return orb


def solve_scf_hf(scf_solver, lf, ham, occ_model, olp, *orb):
    # Plain SCF solver
    if scf_solver.kind == "orb":
        occ_model.assign_occ_reference(*orb)
        assert scf_solver.error(ham, lf, olp, *orb) > scf_solver.threshold
        out = scf_solver(ham, lf, olp, occ_model, *orb)
        assert scf_solver.error(ham, lf, olp, *orb) < scf_solver.threshold
        return out
    # Some DIIS solver
    else:
        occ_model.assign_occ_reference(*orb)
        dms = [compute_1dm_hf(exp) for exp in orb]
        assert scf_solver.error(ham, lf, olp, *dms) > scf_solver.threshold
        out = scf_solver(ham, lf, olp, occ_model, *dms)
        assert scf_solver.error(ham, lf, olp, *dms) < scf_solver.threshold
        focks = [lf.create_two_index() for i in range(ham.ndm)]
        ham.compute_fock(*focks)
        for i in range(ham.ndm):
            orb[i].from_fock(focks[i], olp)
        occ_model.assign_occ_reference(*orb)
        return out
