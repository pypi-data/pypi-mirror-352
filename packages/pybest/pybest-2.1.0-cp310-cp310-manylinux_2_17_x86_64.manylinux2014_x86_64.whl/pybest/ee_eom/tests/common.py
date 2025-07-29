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

from __future__ import annotations

from typing import Any

import numpy as np

from pybest.cc import (
    RCCD,
    RCCS,
    RCCSD,
    RLCCD,
    RLCCSD,
    RfpCCD,
    RfpCCSD,
    RpCCDCCS,
    RpCCDLCCD,
    RpCCDLCCSD,
)
from pybest.context import context
from pybest.ee_eom import (
    REOMCCD,
    REOMCCS,
    REOMCCSD,
    REOMLCCD,
    REOMLCCSD,
    REOMpCCD,
    REOMpCCDCCS,
    REOMpCCDLCCD,
    REOMpCCDLCCSD,
    REOMpCCDS,
)
from pybest.gbasis import (
    compute_cholesky_eri,
    compute_eri,
    compute_kinetic,
    compute_nuclear,
    compute_nuclear_repulsion,
    compute_overlap,
    get_gobasis,
)
from pybest.geminals import ROOpCCD, RpCCD
from pybest.io import load_fcidump, load_molden
from pybest.iodata import IOData
from pybest.linalg import (
    CholeskyLinalgFactory,
    DenseFourIndex,
    DenseLinalgFactory,
    DenseTwoIndex,
)
from pybest.occ_model import AufbauOccModel
from pybest.wrappers import RHF


class Molecule:
    def __init__(
        self,
        molfile: str,
        basis: str,
        lf_cls: DenseLinalgFactory | CholeskyLinalgFactory,
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize Molecule information to do some calculation.
        This class generates/defines all required input (geometries, basis sets,
        integrals, etc.) and contains the main logic in calculations.

        Args:
            molfile (tr): the file name containing the coordinates
            basis (str): the basis set name
            lf_cls (LinalgFactory): the linalg flavor to be tested
        """
        self.mol_name = molfile
        fn = context.get_fn(f"test/{molfile}.xyz")
        self.obasis = get_gobasis(basis, fn, print_basis=False)
        #
        # Define Occupation model, expansion coefficients and overlap
        #
        self.lf = lf_cls(self.obasis.nbasis)
        self.occ_model = AufbauOccModel(self.obasis, **kwargs)
        self.orb_a = [self.lf.create_orbital(self.obasis.nbasis)]
        self.olp = compute_overlap(self.obasis)
        #
        # Construct Hamiltonian
        #
        kin = compute_kinetic(self.obasis)
        na = compute_nuclear(self.obasis)
        if isinstance(self.lf, CholeskyLinalgFactory):
            er = compute_cholesky_eri(self.obasis, threshold=1e-8)
        elif isinstance(self.lf, DenseLinalgFactory):
            er = compute_eri(self.obasis)
        external = compute_nuclear_repulsion(self.obasis)

        self.hamiltonian = [kin, na, er, external]
        self.one = kin.copy()
        self.one.iadd(na)
        self.two = er

        self.hf = None
        self.pccd = None
        self.oopccd = None
        self.pccdccs = None
        self.ccs = None
        self.ccd = None
        self.lccd = None
        self.fpccd = None
        self.fplccd = None
        self.ccsd = None
        self.lccsd = None
        self.fpccsd = None
        self.fplccsd = None
        self.eom_pccd = None
        self.eom_pccds = None
        self.eom_pccdccs = None
        self.eom_fplccd = None
        self.eom_fplccsd = None
        self.eom_ccs = None
        self.eom_ccd = None
        self.eom_ccsd = None
        self.eom_lccd = None
        self.eom_lccsd = None
        # Common tuples and dictionaries
        self.args = (self.olp, *self.orb_a, *self.hamiltonian, self.t_p)
        self.amplitudes = {"t_1": self.t_1, "t_2": self.t_2, "t_p": self.t_p}

    @property
    def t_p(self) -> DenseTwoIndex:
        if self.pccd is None:
            no, nv = self.occ_model.nacto[0], self.occ_model.nactv[0]
            return DenseTwoIndex(no, nv, label="t_p")
        return self.pccd.t_p

    @property
    def t_1(self) -> DenseTwoIndex:
        mask = (self.ccsd, self.lccsd, self.fpccsd, self.fplccsd)
        for instance in mask:
            # only one instance at a time is not None
            if instance is not None:
                return instance.t_1
        no, nv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        return DenseTwoIndex(no, nv, label="t_1")

    @property
    def t_2(self) -> DenseFourIndex:
        mask = (
            self.ccd,
            self.lccd,
            self.fpccd,
            self.fplccd,
            self.ccsd,
            self.lccsd,
            self.fpccsd,
            self.fplccsd,
        )
        for instance in mask:
            # only one instance at a time is not None
            if instance is not None:
                return instance.t_2
        no, nv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        return DenseFourIndex(no, nv, no, nv, label="t_2")

    def do_series_calculations(
        self, *args: str, **kwargs: dict[str, dict[str, Any]] | None
    ) -> None:
        """Perform a series of calculations. Calculations should always be
        carried out in the order RHF->(pCCD->)CC->EOM-CC, where the pCCD step
        can be skipped for CC on RHF.
        The translation is as follows:

        * hf -> RHF
        * pccd -> RpCCD
        * oopccd -> ROOpCCD
        * ccd -> RCCD
        * fpccd -> RfpCCD
        * fplccd -> RpCCDLCCD
        * eom_ccd -> REOMCCD
        * eom_ccsd -> REOMCCSD
        etc.
        """
        mask = {
            "hf": self.do_rhf,
            "pccd": self.do_pccd,
            "oopccd": self.do_pccd,
            "pccdccs": self.do_pccdccs,
            "ccs": self.do_ccs,
            "ccd": self.do_ccd,
            "lccd": self.do_lccd,
            "ccsd": self.do_ccsd,
            "lccsd": self.do_lccsd,
            "fpccd": self.do_fpccd,
            "fpccsd": self.do_fpccsd,
            "fplccd": self.do_fplccd,
            "fplccsd": self.do_fplccsd,
            "eom_ccs": self.do_eom_ccs,
            "eom_pccd": self.do_eom_pccd,
            "eom_pccds": self.do_eom_pccds,
            "eom_pccdccs": self.do_eom_pccdccs,
            "eom_fplccd": self.do_eom_fplccd,
            "eom_fplccsd": self.do_eom_fplccsd,
            "eom_ccd": self.do_eom_ccd,
            "eom_ccsd": self.do_eom_ccsd,
            "eom_lccd": self.do_eom_lccd,
            "eom_lccsd": self.do_eom_lccsd,
        }
        for arg in args:
            kwargs_ = kwargs.get(arg, {})
            if arg == "pccd":
                mask[arg](RpCCD, **kwargs_)
            elif arg == "oopccd":
                mask[arg](ROOpCCD, **kwargs_)
            else:
                mask[arg](**kwargs_)

    def do_rhf(self) -> None:
        """Do RHF calculation"""
        hf = RHF(self.lf, self.occ_model)
        self.hf = hf(*self.hamiltonian, self.olp, *self.orb_a)

    def do_pccd(
        self, pccd_cls: ROOpCCD | RpCCD, **kwargs: dict[str, Any]
    ) -> None:
        """Do pCCD calculation based on input class pccd_cls using this class'
        RHF solution.

        In case other orbitals are to be used, they can be passed using the
        `molden` kwarg where we assume that the orbitals are stored as
        `self.mol_name`.molden.
        """
        if self.hf is None:
            self.do_rhf()
        # read orbitals if passed
        molden_file = kwargs.pop("molden", False)
        args = ()
        if molden_file:
            molden_fn = context.get_fn(f"test/{self.mol_name}.molden")
            orb_a = load_molden(molden_fn)["orb_a"]
            args = (orb_a,)
        pccd = pccd_cls(self.lf, self.occ_model)
        self.pccd = pccd(*self.hamiltonian, self.hf, *args, **kwargs)
        self.oopccd = self.pccd

    def do_eom_pccd(self, **kwargs: dict[str, Any]) -> None:
        """Do EOM-pCCD calculation using this class' pCCD solution"""
        if self.pccd is None:
            raise ValueError("No pCCD solution found.")
        nroot = kwargs.get("nroot")
        nguessv = kwargs.get("nguessv", nroot * 10)
        davidson = kwargs.get("davidson", False)
        eompccd = REOMpCCD(self.lf, self.occ_model)
        self.eom_pccd = eompccd(
            *self.hamiltonian,
            self.pccd,
            nroot=nroot,
            tolerancev=1e-7,
            nguessv=nguessv,
            davidson=davidson,
        )

    def do_eom_pccds(self, **kwargs: dict[str, Any]) -> None:
        """Do EOM-pCCD calculation using this class' pCCD solution"""
        if self.pccd is None:
            raise ValueError("No pCCD solution found.")
        nroot = kwargs.get("nroot")
        nguessv = kwargs.get("nguessv", nroot * 10)
        davidson = kwargs.get("davidson", False)
        eompccds = REOMpCCDS(self.lf, self.occ_model)
        self.eom_pccds = eompccds(
            *self.hamiltonian,
            self.pccd,
            nroot=nroot,
            tolerancev=1e-7,
            nguessv=nguessv,
            davidson=davidson,
        )

    def do_ccs(self, **kwargs: dict[str, Any]) -> None:
        """Do CCS calculation based on this class' RHF solution"""
        if self.hf is None:
            self.do_rhf()
        ccs = RCCS(self.lf, self.occ_model)
        self.ccs = ccs(*self.hamiltonian, self.hf, threshold_r=1e-6)

    def do_pccdccs(self, **kwargs: dict[str, Any]) -> None:
        """Do pCCDCCS calculation based on this class' pCCD solution"""
        if self.pccd is None:
            raise ValueError("No pCCD solution found.")
        ccs = RpCCDCCS(self.lf, self.occ_model)
        self.pccdccs = ccs(*self.hamiltonian, self.pccd, threshold_r=1e-6)

    def do_eom_ccs(self, **kwargs: dict[str, Any]) -> None:
        """Do EOM-CCS calculation using this class' CCD solution"""
        if self.ccs is None:
            raise ValueError("No CCS solution found.")
        nroot = kwargs.get("nroot")
        nguessv = kwargs.get("nguessv", nroot * 10)
        eomccd = REOMCCS(self.lf, self.occ_model)
        self.eom_ccs = eomccd(
            *self.hamiltonian,
            self.ccs,
            nroot=nroot,
            tolerancev=1e-7,
            nguessv=nguessv,
        )

    def do_eom_pccdccs(self, **kwargs: dict[str, Any]) -> None:
        """Do EOM-pCCDCCS calculation using this class' pCCDCCS solution"""
        if self.pccdccs is None:
            raise ValueError("No pCCDCCS solution found.")
        nroot = kwargs.get("nroot")
        nguessv = kwargs.get("nguessv", nroot * 10)
        eompccdccs = REOMpCCDCCS(self.lf, self.occ_model)
        self.eom_pccdccs = eompccdccs(
            *self.hamiltonian,
            self.pccdccs,
            nroot=nroot,
            tolerancev=1e-7,
            nguessv=nguessv,
        )

    def do_ccd(self, **kwargs: dict[str, Any]) -> None:
        """Do CCD calculation based on this class' RHF solution"""
        if self.hf is None:
            self.do_rhf()
        ccd = RCCD(self.lf, self.occ_model)
        self.ccd = ccd(*self.hamiltonian, self.hf, threshold_r=1e-6)

    def do_lccd(self, **kwargs: dict[str, Any]) -> None:
        """Do LCCD calculation based on this class' RHF solution"""
        if self.hf is None:
            self.do_rhf()
        ccd = RLCCD(self.lf, self.occ_model)
        self.lccd = ccd(*self.hamiltonian, self.hf, threshold_r=1e-6)

    def do_fpccd(self, **kwargs: dict[str, Any]) -> None:
        """Do fpCCD calculation based on this class' pCCD solution"""
        if self.pccd is None:
            raise ValueError("No pCCD solution found.")
        ccd = RfpCCD(self.lf, self.occ_model)
        self.fpccd = ccd(*self.hamiltonian, self.pccd, threshold_r=1e-6)

    def do_fplccd(self, **kwargs: dict[str, Any]) -> None:
        """Do fpLCCD calculation based on this class' pCCD solution"""
        if self.pccd is None:
            raise ValueError("No pCCD solution found.")
        ccd = RpCCDLCCD(self.lf, self.occ_model)
        self.fplccd = ccd(*self.hamiltonian, self.pccd, threshold_r=1e-6)

    def do_eom_ccd(self, **kwargs: dict[str, Any]) -> None:
        """Do EOM-CCD calculation using this class' CCD solution"""
        if self.ccd is None:
            raise ValueError("No CCD solution found.")
        nroot = kwargs.get("nroot")
        nguessv = kwargs.get("nguessv", nroot * 10)
        eomccd = REOMCCD(self.lf, self.occ_model)
        self.eom_ccd = eomccd(
            *self.hamiltonian,
            self.ccd,
            nroot=nroot,
            tolerancev=1e-7,
            nguessv=nguessv,
        )

    def do_eom_lccd(self, **kwargs: dict[str, Any]) -> None:
        """Do EOM-LCCD calculation using this class' LCCD solution"""
        if self.lccd is None:
            raise ValueError("No LCCD solution found.")
        nroot = kwargs.get("nroot")
        nguessv = kwargs.get("nguessv", nroot * 10)
        eomlccd = REOMLCCD(self.lf, self.occ_model)
        self.eom_lccd = eomlccd(
            *self.hamiltonian,
            self.lccd,
            nroot=nroot,
            tolerancev=1e-6,
            nguessv=nguessv,
        )

    def do_eom_fplccd(self, **kwargs: dict[str, Any]) -> None:
        """Do EOM-fpLCCD calculation using this class' fpLCCD solution"""
        if self.fplccd is None:
            raise ValueError("No fpLCCD solution found.")
        nroot = kwargs.get("nroot")
        nguessv = kwargs.get("nguessv", nroot * 10)
        eomfplccd = REOMpCCDLCCD(self.lf, self.occ_model)
        self.eom_fplccd = eomfplccd(
            *self.hamiltonian,
            self.fplccd,
            nroot=nroot,
            tolerancev=1e-6,
            nguessv=nguessv,
        )

    def do_ccsd(self, **kwargs: dict[str, Any]) -> None:
        """Do CCSD calculation using this class' RHF solution"""
        if self.hf is None:
            self.do_rhf()
        ccsd = RCCSD(self.lf, self.occ_model)
        self.ccsd = ccsd(*self.hamiltonian, self.hf, threshold_r=1e-6)

    def do_lccsd(self, **kwargs: dict[str, Any]) -> None:
        """Do LCCSD calculation using this class' RHF solution"""
        if self.hf is None:
            self.do_rhf()
        ccsd = RLCCSD(self.lf, self.occ_model)
        options = {"solver": "krylov", "threshold_r": 1e-6}
        self.lccsd = ccsd(*self.hamiltonian, self.hf, **options)

    def do_fpccsd(self, **kwargs: dict[str, Any]) -> None:
        """Do fpCCSD calculation using this class' pCCD solution"""
        if self.pccd is None:
            raise ValueError("No pCCD solution found.")
        ccsd = RfpCCSD(self.lf, self.occ_model)
        self.fpccsd = ccsd(*self.hamiltonian, self.pccd, threshold_r=1e-6)

    def do_fplccsd(self, **kwargs: dict[str, Any]) -> None:
        """Do fpLCCSD calculation using this class' pCCD solution"""
        if self.pccd is None:
            raise ValueError("No pCCD solution found.")
        ccsd = RpCCDLCCSD(self.lf, self.occ_model)
        self.fplccsd = ccsd(*self.hamiltonian, self.pccd, threshold_r=1e-6)

    def do_eom_fplccsd(self, **kwargs: dict[str, Any]) -> None:
        """Do EOM-fpLCCSD calculation using this class' fpLCCSD solution"""
        if self.fplccsd is None:
            raise ValueError("No fpLCCSD solution found.")
        nroot = kwargs.get("nroot")
        nguessv = kwargs.get("nguessv", nroot * 10)
        eomfplccsd = REOMpCCDLCCSD(self.lf, self.occ_model)
        self.eom_fplccsd = eomfplccsd(
            *self.hamiltonian,
            self.fplccsd,
            nroot=nroot,
            tolerancev=1e-6,
            nguessv=nguessv,
        )

    def do_eom_lccsd(self, **kwargs: dict[str, Any]) -> None:
        """Do EOM-LCCSD calculation using this class' LCCSD solution"""
        if self.lccsd is None:
            raise ValueError("No LCCSD solution found.")
        nroot = kwargs.get("nroot")
        nguessv = kwargs.get("nguessv", nroot * 10)
        eomlccsd = REOMLCCSD(self.lf, self.occ_model)
        self.eom_lccsd = eomlccsd(
            *self.hamiltonian,
            self.lccsd,
            nroot=nroot,
            tolerancev=1e-6,
            nguessv=nguessv,
        )

    def do_eom_ccsd(self, **kwargs: dict[str, Any]) -> None:
        """Do EOM-CCSD calculation using this class' CCSD solution"""
        if self.ccsd is None:
            raise ValueError("No CCSD solution found.")
        nroot = kwargs.get("nroot")
        nguessv = kwargs.get("nguessv", nroot * 10)
        eomccsd = REOMCCSD(self.lf, self.occ_model)
        self.eom_ccsd = eomccsd(
            *self.hamiltonian,
            self.ccsd,
            nroot=nroot,
            tolerancev=1e-7,
            nguessv=nguessv,
        )


class FromFile(Molecule):
    """Read molecular information from file.

    Args:
        Molecule (class): Molecule class containing all the logic
    """

    def __init__(
        self,
        molfile: str,
        basis: int,
        lf_cls: DenseLinalgFactory = DenseLinalgFactory,
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize Molecule information to do some calculation.
        This class reads the Hamiltonian in the FCIDUMP format and contains
        the main logic in calculations.

        Args:
            molfile (tr): the name of the FCIDUMP file
            basis (int): the number of basis functions
            lf_cls (LinalgFactory): the linalg flavor to be tested
        """
        self.mol_name = molfile
        fn = context.get_fn(f"test/{molfile}.fcidump")
        #
        # Define Occupation model, expansion coefficients and overlap
        #
        self.lf = lf_cls(basis)
        nocc = kwargs.get("nocc", 0)
        ncore = kwargs.get("ncore", 0)
        self.occ_model = AufbauOccModel(self.lf, nel=nocc * 2, ncore=ncore)
        # olp as identity matrix
        self.olp = self.lf.create_two_index(basis, label="olp")
        self.olp.assign_diagonal(1.0)
        # orb_a as identity matrix
        orb_a = self.lf.create_orbital(basis)
        orb_a.assign(self.olp)
        orb = kwargs.get("orb", None)
        if orb is not None:
            fn_orb = context.get_fn(orb)
            orb_a.coeffs[:] = np.fromfile(fn_orb, sep=",").reshape(
                basis, basis
            )
        self.orb_a = [orb_a]
        #
        # Read Hamiltonian from data dir
        #
        integrals = load_fcidump(fn)
        self.one = integrals["one"]
        self.two = integrals["two"]
        core = integrals["e_core"]
        self.hamiltonian = [self.one, self.two, core]

        # overwrite HF solution with IOData data as FCIDUMP is generated from RHF
        self.hf = IOData(
            **{"orb_a": orb_a, "olp": self.olp, "e_core": core, "e_ref": 0.0}
        )
        self.pccd = None
        self.oopccd = None
        self.pccdccs = None
        self.ccs = None
        self.ccd = None
        self.lccd = None
        self.fpccd = None
        self.fplccd = None
        self.ccsd = None
        self.lccsd = None
        self.fpccsd = None
        self.fplccsd = None
        self.eom_pccd = None
        self.eom_pccds = None
        self.eom_pccdccs = None
        self.eom_fplccd = None
        self.eom_fplccsd = None
        self.eom_ccs = None
        self.eom_ccd = None
        self.eom_ccsd = None
        self.eom_lccd = None
        self.eom_lccsd = None
        # Common tuples and dictionaries
        self.args = (self.olp, *self.orb_a, *self.hamiltonian, self.t_p)
        self.amplitudes = {"t_1": self.t_1, "t_2": self.t_2, "t_p": self.t_p}
