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
#
# 2021-12: updated prepare_cp_hf to work with new structure of the OccupationModel
#          class. Instead of passing list of occupations numbers (ints), a list
#          of dictionaries containing molecule specific options is passed
#          (charge, nocc_a, etc.)

"""
SAPT Utils Module
Provides some useful functions for dimer center basis sets (DBCS) computations:
    * preparing ghost basis sets,
    * updating molecule geometries,
    * preparing computational primitives (AO integrals).
    * monomers dimer optimization (HF)

Purpose of this module is to simplify 'interaction energy calculations' scripts.
"""

from __future__ import annotations

import os
import pathlib
from typing import Any

import numpy as np

import pybest.gbasis.cholesky_eri as cholesky_module

# pybest imports
import pybest.gbasis.dense_ints as ints_module
import pybest.gbasis.gobasis as basis_module
from pybest.exceptions import ArgumentError, MissingFileError, UnknownOption
from pybest.iodata import IOData
from pybest.linalg import (
    CholeskyLinalgFactory,
    DenseLinalgFactory,
    DenseOrbital,
    FourIndex,
)
from pybest.log import log, timer
from pybest.occ_model import AufbauOccModel
from pybest.units import ekelvin, invcm, kcalmol
from pybest.utility import check_type
from pybest.wrappers import RHF

__all__ = [
    "prepare_cp_hf",
    "prepare_cp_molecules",
    "prepare_cp_monomers",
]

SAPT_HATREE_2_KCAL = 1 / kcalmol
SAPT_HATREE_2_CM = 1 / invcm
SAPT_HATREE_2_KELVIN = 1 / ekelvin


@timer.with_section("SAPT_AO-MO")
def transform_integrals_SAPT(
    two: FourIndex,
    orb_monA: DenseOrbital,
    orb_monB: DenseOrbital,
    indextrans: str = "tensordot",
    simple: bool | None = None,
    out: list[FourIndex] | None = None,
) -> list[FourIndex] | FourIndex:
    """Update MO integrals for SAPT theories. Returns list of 2-electron
    integrals according to a list of expansion coefficients which are taken from A and B monomer
     calculations.

    **Arguments:**

    two
        Two-electron integrals in the AO basis. (FourIndex)

    orb_monA orb_monB
        The monomers A and B AO/MO orbitals coefficients. (DenseOrbital)

    **Optional arguments:**

    indextrans
        Choice of 4-index transformation. Default 'cupy', if not available use
        'tensordot' instead.
    simple
        Setting this flag to any value will transform only ABAB type
        of the integrals. Mainly for debugging purposes (quick)
    out
        Two-electron integral (FourIndex), which the result should be
        written to. It should always be used with simple flag.
    :rtype: List of ABAB, BBAB, AAAB two-electron integrals in MO basis. (FourIndex)

    """
    check_type("two", two, FourIndex)
    check_type("orb_monA", orb_monA, DenseOrbital)
    check_type("orb_monB", orb_monB, DenseOrbital)
    result = []

    # just ABAB integrals
    if simple is not None:
        if out is None:
            out4ind = two.new()
            out4ind.assign_four_index_transform(
                two, orb_monA, orb_monB, orb_monA, orb_monB, indextrans
            )
            result.append(out4ind)
            return result

        check_type("out", out, FourIndex)
        out.assign_four_index_transform(
            two, orb_monA, orb_monB, orb_monA, orb_monB, indextrans
        )
        return out

    # ABAB
    out4ind = two.new()
    out4ind.assign_four_index_transform(
        two, orb_monA, orb_monB, orb_monA, orb_monB, indextrans
    )
    result.append(out4ind)

    # BBAB
    out4ind = two.new()
    out4ind.assign_four_index_transform(
        two, orb_monB, orb_monB, orb_monA, orb_monB, indextrans
    )
    result.append(out4ind)

    # AAAB
    out4ind = two.new()
    out4ind.assign_four_index_transform(
        two, orb_monA, orb_monA, orb_monA, orb_monB, indextrans
    )
    result.append(out4ind)
    return result


def get_monomers_geos(dimer_geo: str) -> tuple[pathlib.Path, pathlib.Path]:
    """
    Returns monomers file names in following convention:
    fn_dim = 'ArHF.xyz'
    will produce:
    fn_monA =  'ArHFa.xyz'
    fn_monB = 'ArHFb.xyz'
    """
    dimer_geo_file = pathlib.Path(dimer_geo)
    geo_file_name = dimer_geo_file.stem
    mon_a_geo_file = dimer_geo_file.with_name(geo_file_name + "a.xyz")
    mon_b_geo_file = dimer_geo_file.with_name(geo_file_name + "b.xyz")
    return mon_a_geo_file, mon_b_geo_file


def prepare_cp_monomers(
    fn_geo: str,
) -> tuple[IOData, IOData, IOData, list, list]:
    """
    Prepares CP-corrected (dimer centered) molecules vIOData.prepare_ghosts
    **Arguments**
    fn_geo
        Path to input dimer geometry .xyz (str): /path/to/geometry.xyz.
        Monomers geometries are assumed to be in following path:
        /path/to/geometrya.xyz, /path/to/geometryb.xyz
    """
    if fn_geo is None:
        raise ArgumentError(
            'You must specify input geometry file! Set fn_geo="path/to/geometry.xyz"'
        )

    if isinstance(fn_geo, str):
        fn_dim = fn_geo
        fn_mon_A, fn_mon_B = get_monomers_geos(fn_geo)
        if not os.path.isfile(fn_dim):
            raise MissingFileError(
                f"No such a file: {fn_dim}!\nDid you set up your dimer geometry input file?"
            )
        if not os.path.isfile(fn_mon_A):
            raise MissingFileError(
                f"No such a file: {fn_mon_A}!\nDid you set up your monomer A geometry input file?"
            )
        if not os.path.isfile(fn_mon_B):
            raise MissingFileError(
                f"No such a file: {fn_mon_B}'\nDid you set up your monomer B geometry input file?"
            )
    else:
        raise TypeError("Geometry File Path must be a string!")

    mol_dim = IOData.from_file(fn_dim)
    mol_mon_A = IOData.from_file(fn_mon_A)
    mol_mon_B = IOData.from_file(fn_mon_B)

    ix_map_A, ix_map_B = IOData.prepare_ghosts(fn_mon_A, fn_mon_B, fn_dim)
    return mol_dim, mol_mon_A, mol_mon_B, ix_map_A, ix_map_B


def prepare_cp_molecules(
    basis: str = "cc-pvdz",
    fn_geo: str | None = None,
    fourindex_type: str = "dense",
    er_threshold: float = 1e-10,
    updated_geometry: np.ndarray = None,
) -> tuple[IOData, IOData, IOData]:
    """
    Prepares computational primitives for dimer centered basis function.
    **Arguments:**
    basis
        Basis type (str) (default 'cc-pvdz')
    fn_geo
        Path to input dimer geometry .xyz (str): /path/to/geometry.xyz.
        Monomers geometries are assumed to be in following path:
        /path/to/geometrya.xyz, /path/to/geometryb.xyz
    fourindex_type
        FourIndex instance type (str) (default 'Dense')
        Available implementations:'Dense' or 'Cholesky'.
    er_threshold
        Threshold used with 'Cholesky' FourIndex approximation algorithm.
        (float) (default 1e-10)
        Causes values of matrix elements lower than that to be neglected.
    updated_geometry
        Matrix (numpy.ndarray)(default None) representing new geometry
        matrix for dimer centered molecule.
    """
    if fn_geo is None:
        raise ArgumentError(
            'You must specify input geometry file! Set fn_geo="path/to/geometry.xyz"'
        )
    ret = prepare_cp_monomers(fn_geo=fn_geo)
    (
        mol_dim,
        mol_mon_a,
        mol_mon_b,
        dummy_mon_a,
        dummy_mon_b,
    ) = ret

    if updated_geometry is not None:
        if isinstance(updated_geometry, np.ndarray):
            mol_dim.coordinates = updated_geometry.copy()
        else:
            raise TypeError("updated_geometry should be numpy.ndarray")

    # grab DBCS gbasis objects for each fragment
    gbasis_dim = basis_module.get_gobasis(basisname=basis, coords=mol_dim)
    gbasis_mon_a = basis_module.get_gobasis(
        basisname=basis, coords=mol_dim, dummy=dummy_mon_a
    )
    gbasis_mon_b = basis_module.get_gobasis(
        basisname=basis, coords=mol_dim, dummy=dummy_mon_b
    )

    if fourindex_type.lower() == "cholesky":
        lf = CholeskyLinalgFactory(gbasis_dim.nbasis)
        lf_a = CholeskyLinalgFactory(gbasis_mon_a.nbasis)
        lf_b = CholeskyLinalgFactory(gbasis_mon_b.nbasis)
    elif fourindex_type.lower() == "dense":
        lf = DenseLinalgFactory(gbasis_dim.nbasis)
        lf_a = DenseLinalgFactory(gbasis_mon_a.nbasis)
        lf_b = DenseLinalgFactory(gbasis_mon_b.nbasis)
    else:
        log.warn(
            f"Unrecognized fourindex_type: '{fourindex_type}'. Defaulting to 'Dense'"
        )
        lf = DenseLinalgFactory(gbasis_dim.nbasis)
        lf_a = DenseLinalgFactory(gbasis_mon_a.nbasis)
        lf_b = DenseLinalgFactory(gbasis_mon_b.nbasis)
        fourindex_type = "dense"

    # dimer
    olp = ints_module.compute_overlap(gbasis_dim)
    kin = ints_module.compute_kinetic(gbasis_dim)
    na = ints_module.compute_nuclear(gbasis_dim)

    # ERI AO in DCBS are the same for monA, monB & dimer
    if fourindex_type.lower() == "dense":
        er = ints_module.compute_eri(gbasis_dim)

    # otherwise do cholesky eri
    elif fourindex_type.lower() == "cholesky":
        er = cholesky_module.compute_cholesky_eri(
            gbasis_dim, threshold=er_threshold
        )
    else:
        raise UnknownOption(
            f"'{fourindex_type.lower()}' is not valid value of fourindex_type"
        )

    # mon a
    olp_a = ints_module.compute_overlap(gbasis_mon_a)
    kin_a = ints_module.compute_kinetic(gbasis_mon_a)
    na_a = ints_module.compute_nuclear(gbasis_mon_a)

    # mon b
    olp_b = ints_module.compute_overlap(gbasis_mon_b)
    kin_b = ints_module.compute_kinetic(gbasis_mon_b)
    na_b = ints_module.compute_nuclear(gbasis_mon_b)

    dimer = IOData(
        title="dimer",
        coords=mol_dim,
        lf=lf,
        olp=olp,
        kin=kin,
        na=na,
        eri=er,
        basis=gbasis_dim,
    )
    mon_a = IOData(
        title="mon A",
        coords=mol_mon_a,
        lf=lf_a,
        olp=olp_a,
        kin=kin_a,
        na=na_a,
        eri=er,
        basis=gbasis_mon_a,
    )
    mon_b = IOData(
        title="mon B",
        coords=mol_mon_b,
        lf=lf_b,
        olp=olp_b,
        kin=kin_b,
        na=na_b,
        eri=er,
        basis=gbasis_mon_b,
    )
    return dimer, mon_a, mon_b


def prepare_cp_hf(
    basis: str = "cc-pvdz",
    fn_geo: str | None = None,
    occupations: tuple[dict, dict, dict] | None = None,
    fourindex_type: str = "Dense",
    er_threshold: float = 1e-10,
    updated_geometry: np.ndarray = None,
    solver: str = "ediis2",
    solver_opts: dict[str, Any] | None = None,
):
    """
    Computes cp-corrected interaction of dimer supersystem at the SCF Hartree-Fock level.
    Intended to be used as a pre-processing step in post-SCF theories, i.e., SAPT solvers
    """
    if occupations is None:
        occupations = ({}, {}, {})

    if solver_opts is None:
        solver_opts = {"wfn_thresh": 1e-12, "en_thresh": 1e-9}

    if fn_geo is None:
        raise ArgumentError(
            'You must specify input geometry file! Set fn_geo="path/to/geometry.xyz"'
        )

    avail_scf_hf_solvers = [
        "cdiis",
        "ediis",
        "ediis2",
        "plain",
        None,  # skips DBCS SCF
    ]
    if "wfn_thresh" not in solver_opts.keys():
        raise ArgumentError("Keyword 'wfn_thresh' is required in solver_opts!")

    if "en_thresh" not in solver_opts.keys():
        raise ArgumentError("Keyword 'opt_name' is required in solver_opts!")

    if solver not in avail_scf_hf_solvers:
        raise UnknownOption(f"solver must be one of: {avail_scf_hf_solvers}")

    wfn_thresh = solver_opts.get("wfn_thresh")

    kwargs_monA, kwargs_monB, kwargs_dim = occupations
    dimer, monA, monB = prepare_cp_molecules(
        basis, fn_geo, fourindex_type, er_threshold, updated_geometry
    )

    orb_dim = dimer.lf.create_orbital()
    orb_monA = monA.lf.create_orbital()
    orb_monB = monB.lf.create_orbital()

    external_dim = ints_module.compute_nuclear_repulsion(dimer.basis)
    external_monA = ints_module.compute_nuclear_repulsion(monA.basis)
    external_monB = ints_module.compute_nuclear_repulsion(monB.basis)

    if solver:
        # compute dimer rhf
        occ_model_dim = AufbauOccModel(dimer.basis, **kwargs_dim)
        occ_model_dim.assign_occ_reference(orb_dim)
        dimer_rhf = RHF(dimer.lf, occ_model_dim)
        dimer_rhf.threshold = wfn_thresh
        dimer_rhf(
            dimer.kin,
            dimer.na,
            dimer.eri,
            external_dim,
            dimer.olp,
            orb_dim,
            diis=solver,
        )
        en_dim = dimer_rhf.hamiltonian.compute_energy()

        # compute monomer A rhf
        occ_model_monA = AufbauOccModel(monA.basis, **kwargs_monA)
        occ_model_monA.assign_occ_reference(orb_monA)
        monA_rhf = RHF(monA.lf, occ_model_monA)
        monA_rhf.threshold = wfn_thresh
        monA_rhf(
            monA.kin,
            monA.na,
            monA.eri,
            external_monA,
            monA.olp,
            orb_monA,
            diis=solver,
        )
        en_monA = monA_rhf.hamiltonian.compute_energy()

        # compute monomer B rhf
        occ_model_monB = AufbauOccModel(monB.basis, **kwargs_monB)
        occ_model_monB.assign_occ_reference(orb_monB)
        monB_rhf = RHF(monB.lf, occ_model_monB)
        monB_rhf.threshold = wfn_thresh
        monB_rhf(
            monB.kin,
            monB.na,
            monB.eri,
            external_monB,
            monB.olp,
            orb_monB,
            diis=solver,
        )
        en_monB = monB_rhf.hamiltonian.compute_energy()
    else:
        # no scf
        en_dim, en_monA, en_monB = (0, 0, 0)
        log.hline("~")
        log("SKIPPING HARTREE FOCK CALCULATIONS")

    en_int = en_dim - (en_monA + en_monB)
    raw_fn_geo = fn_geo.split("/")[-1]
    nbasis = occ_model_dim.nbasis[0]
    nvirt_dim = occ_model_dim.nactv[0]
    nvirt_monA = occ_model_monA.nactv[0]
    nvirt_monB = occ_model_monB.nactv[0]
    occ_dim = occ_model_dim.nacto[0]
    occ_monA = occ_model_monA.nacto[0]
    occ_monB = occ_model_monB.nacto[0]
    log("DCBS HF INTERACTION SUMMARY (SUPERMOLECULAR + CP CORRECTION) ")
    log(" ")
    log.hline("~")
    log(f"{'GEO_FNAME':9s} {'BASIS':14s} {'NBFS':14s}")
    log(f"{raw_fn_geo:9s} {basis:14s} {nbasis!s:14s}")
    log(" ")
    log(f"{'':9s} {'NO OCC':14s} {'NO VIRT':14s}")
    log(f"{'DIMER':9s} {occ_dim!s:14s} {nvirt_dim!s:14s}")
    log(f"{'MONOMER A':9s} {occ_monA!s:14s} {nvirt_monA!s:14s}")
    log(f"{'MONOMER B':9s} {occ_monB!s:14s} {nvirt_monB!s:14s}")
    log(" ")
    e_int_str = "E^{{int}}_{{HF}}"
    hatree_str = "mHatree"
    kcalmol_str = "kCal/mol"
    invcm_str = "cm^{-1}"
    kelvins_str = "Kelvins"
    log(
        f"{e_int_str:12s} {hatree_str:14s} {kcalmol_str:14s} {invcm_str:14s} {kelvins_str:14s}"
    )
    en_int_mhatree = en_int * 1000
    en_int_kcal = en_int * SAPT_HATREE_2_KCAL
    en_int_invcm = en_int * SAPT_HATREE_2_CM
    en_int_kelivn = en_int * SAPT_HATREE_2_KELVIN
    log(
        f"{en_int:12.10f} {en_int_mhatree:13.7f} {en_int_kcal:14.7f}"
        f"{en_int_invcm:16.5f} {en_int_kelivn:14.5f}"
    )

    log(" ")
    log.hline("~")

    dimer_hf = IOData(
        title="dimer",
        e_hf=en_dim,
        orb=orb_dim,
        lf=dimer.lf,
        occ_model=occ_model_dim,
        nuc=external_dim,
        eri=dimer.eri,
        na=dimer.na,
        olp=dimer.olp,
    )
    monA_hf = IOData(
        title="mon A",
        e_hf=en_monA,
        orb=orb_monA,
        lf=monA.lf,
        occ_model=occ_model_monA,
        nuc=external_monA,
        eri=monA.eri,
        na=monA.na,
        olp=monA.olp,
    )
    monB_hf = IOData(
        title="mon B",
        e_hf=en_monB,
        orb=orb_monB,
        lf=monB.lf,
        occ_model=occ_model_monB,
        nuc=external_monB,
        eri=monB.eri,
        na=monB.na,
        olp=monB.olp,
    )

    return dimer_hf, monA_hf, monB_hf
