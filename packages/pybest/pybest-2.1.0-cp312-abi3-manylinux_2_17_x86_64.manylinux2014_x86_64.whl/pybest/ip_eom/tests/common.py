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
# 2025-02: unification of variables and type hints (Julian Świerczyński)
# 2025-05: incorporation of new molecue testing framework and optimization (Julia Szczuczko)

from pybest.cc import (
    RCCD,
    RCCSD,
    RLCCD,
    RLCCSD,
    RfpCCD,
    RfpCCSD,
    RpCCDLCCD,
    RpCCDLCCSD,
)
from pybest.context import context
from pybest.geminals import ROOpCCD, RpCCD
from pybest.io.molden import load_molden
from pybest.ip_eom import (
    RDIPCCD,
    RDIPCCSD,
    RDIPLCCD,
    RDIPLCCSD,
    RIPCCD,
    RIPCCSD,
    RIPLCCD,
    RIPLCCSD,
    RDIPfpCCD,
    RDIPfpCCSD,
    RDIPfpLCCD,
    RDIPfpLCCSD,
    RDIPpCCD,
    RIPfpCCD,
    RIPfpCCSD,
    RIPfpLCCD,
    RIPfpLCCSD,
    RIPpCCD,
)
from pybest.linalg import DenseFourIndex, DenseTwoIndex
from pybest.tests.molecule import BaseMolecule


class IP_EOMMolecule(BaseMolecule):
    """
    Represents an ionization potential (IP) Equation-of-Motion (EOM) molecule for testing.

    This class extends BaseMolecule to support pCCD-based and CC-based methods for
    computing ionization potentials (IP) and double ionization potentials (DIP).
    It enables flexible test construction through dynamic series execution and
    structured result storage.

    Attributes:
    mol_name (str): File stem for molecule files (used for Molden loading).
    pccd (object): pCCD reference state object (RpCCD or ROOpCCD).
    rcc (object): Most recently computed RCC-like object (e.g., CCD, CCSD, etc.).
    results (dict): Dictionary storing named results from each computation step.
    t_p (DenseTwoIndex): Pair amplitude tensor.
    t_1, t_2 (DenseTwoIndex, DenseFourIndex): Singles and doubles amplitude tensors.
    amplitudes (dict): Dictionary of amplitude tensors.
    t (tuple): Tuple of all amplitude tensors (t_1, t_2, t_p).
    """

    def __init__(self, molfile, basis, lf_cls, **kwargs):
        super().__init__(molfile, basis, lf_cls, **kwargs)
        self.mol_name = molfile

        self.results = {}
        self.pccd = None
        self.rcc = None
        self.ip_pccd = None
        self.dip_pccd = None
        self.ip_rcc = None
        self.dip_rcc = None

        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        self.t_p = DenseTwoIndex(nacto, nactv, label="t_p")
        self.args = (self.olp, *self.orb, *self.hamiltonian, self.t_p)
        self.t_1 = DenseTwoIndex(nacto, nactv, label="t_1")
        self.t_2 = DenseFourIndex(nacto, nactv, nacto, nactv, label="t_2")
        self.amplitudes = {"t_1": self.t_1, "t_2": self.t_2, "t_p": self.t_p}
        self.t = (self.t_1, self.t_2, self.t_p)

    def __getattr__(self, name):
        """Fallback for .ccd, .fpccsd, .ip_fpccd, etc., using stored results or .rcc."""
        rcc_aliases = {
            "ccd",
            "ccsd",
            "lccd",
            "lccsd",
            "fpccd",
            "fpccsd",
            "fplccd",
            "fplccsd",
        }
        if name in rcc_aliases and self.rcc is not None:
            return self.rcc
        if name in self.results:
            return self.results[name]
        raise AttributeError(
            f"{self.__class__.__name__} has no attribute '{name}'"
        )

    def _store(self, name, result):
        self.results[name] = result
        return result

    def do_series_calculations(self, *tasks, **kwargs):
        """Perform a list of sequential tasks based on method names."""
        dispatch = {
            "hf": lambda **kw: self.do_rhf(),
            "pccd": lambda **kw: self.do_pccd(RpCCD, **kw),
            "oopccd": lambda **kw: self._store(
                "oopccd", self.do_pccd(ROOpCCD, **kw)
            ),
            "ccd": lambda **kw: self.do_ccd(**kw),
            "lccd": lambda **kw: self.do_lccd(**kw),
            "ccsd": lambda **kw: self.do_ccsd(**kw),
            "lccsd": lambda **kw: self.do_lccsd(**kw),
            "fpccd": lambda **kw: self.do_fpccd(**kw),
            "fpccsd": lambda **kw: self.do_fpccsd(**kw),
            "fplccd": lambda **kw: self.do_fplccd(**kw),
            "fplccsd": lambda **kw: self.do_fplccsd(**kw),
            "ip_ccd": lambda **kw: self.do_ip_rcc(RIPCCD, **kw),
            "ip_lccd": lambda **kw: self.do_ip_rcc(RIPLCCD, **kw),
            "ip_ccsd": lambda **kw: self.do_ip_rcc(RIPCCSD, **kw),
            "ip_lccsd": lambda **kw: self.do_ip_rcc(RIPLCCSD, **kw),
            "ip_fpccd": lambda **kw: self.do_ip_rcc(RIPfpCCD, **kw),
            "ip_fpccsd": lambda **kw: self.do_ip_rcc(RIPfpCCSD, **kw),
            "ip_fplccd": lambda **kw: self.do_ip_rcc(RIPfpLCCD, **kw),
            "ip_fplccsd": lambda **kw: self.do_ip_rcc(RIPfpLCCSD, **kw),
            "dip_ccd": lambda **kw: self.do_dip_rcc(RDIPCCD, **kw),
            "dip_lccd": lambda **kw: self.do_dip_rcc(RDIPLCCD, **kw),
            "dip_ccsd": lambda **kw: self.do_dip_rcc(RDIPCCSD, **kw),
            "dip_lccsd": lambda **kw: self.do_dip_rcc(RDIPLCCSD, **kw),
            "dip_fpccd": lambda **kw: self.do_dip_rcc(RDIPfpCCD, **kw),
            "dip_fpccsd": lambda **kw: self.do_dip_rcc(RDIPfpCCSD, **kw),
            "dip_fplccd": lambda **kw: self.do_dip_rcc(RDIPfpLCCD, **kw),
            "dip_fplccsd": lambda **kw: self.do_dip_rcc(RDIPfpLCCSD, **kw),
        }
        for task in tasks:
            task_fn = dispatch[task]
            task_kwargs = kwargs.get(task, {})
            result = task_fn(**task_kwargs)
            if result is not None:
                self.results[task] = result

    def do_pccd(self, pccd_cls, **kwargs):
        if self.hf is None:
            self.do_rhf()
        molden = kwargs.pop("molden", False)
        args = ()
        if molden:
            fn = context.get_fn(f"test/{self.mol_name}.molden")
            args = (load_molden(fn)["orb_a"],)
        solver = pccd_cls(self.lf, self.occ_model)
        self.pccd = solver(*self.hamiltonian, self.hf, *args, **kwargs)
        self.results["pccd"] = self.pccd

    def do_ip_pccd(self, alpha, nroot, nhole):
        if self.pccd is None:
            raise ValueError("Missing pCCD result")
        solver = RIPpCCD(self.lf, self.occ_model, alpha=alpha)
        self.ip_pccd = solver(
            *self.hamiltonian, self.pccd, nroot=nroot, nhole=nhole
        )
        self.results["ip_pccd"] = self.ip_pccd

    def do_dip_pccd(self, alpha, nroot, nhole):
        if self.pccd is None:
            raise ValueError("Missing pCCD result")
        solver = RDIPpCCD(self.lf, self.occ_model, alpha=alpha)
        self.dip_pccd = solver(
            *self.hamiltonian,
            self.pccd,
            nroot=nroot,
            nhole=nhole,
            nguessv=nroot * 10,
        )
        self.results["dip_pccd"] = self.dip_pccd

    def do_rcc(self, solver_cls, **kwargs):
        if self.hf is None:
            self.do_rhf()
        solver = solver_cls(self.lf, self.occ_model)

        # Explicitly pass t_p if needed
        if hasattr(solver, "t_p"):
            solver.t_p = self.t_p

        # Remove unsupported keys like t_p if accidentally included
        kwargs.pop("t_p", None)

        self.rcc = solver(*self.hamiltonian, self.hf, **kwargs)
        self.results["rcc"] = self.rcc

    def do_ccd(self, **kwargs):
        self.do_rcc(RCCD, **kwargs)

    def do_lccd(self, **kwargs):
        self.do_rcc(RLCCD, **kwargs)

    def do_ccsd(self, **kwargs):
        self.do_rcc(RCCSD, **kwargs)

    def do_fpccd(self, **kwargs):
        if self.pccd is None:
            raise ValueError("Missing pCCD result (call do_pccd() first)")
        solver = RfpCCD(self.lf, self.occ_model)
        solver.t_p = self.t_p
        self.fpccd = solver(*self.hamiltonian, self.pccd, **kwargs)
        self.rcc = self.fpccd
        self.results["fpccd"] = self.fpccd

    def do_fpccsd(self, **kwargs):
        if self.pccd is None:
            raise ValueError("Missing pCCD result (call do_pccd() first)")
        solver = RfpCCSD(self.lf, self.occ_model)
        solver.t_p = self.t_p
        self.fpccsd = solver(*self.hamiltonian, self.pccd, **kwargs)
        self.rcc = self.fpccsd
        self.results["fpccsd"] = self.fpccsd

    def do_fplccd(self, **kwargs):
        if self.pccd is None:
            raise ValueError("Missing pCCD result (call do_pccd() first)")
        solver = RpCCDLCCD(self.lf, self.occ_model)
        solver.t_p = self.t_p
        self.fplccd = solver(*self.hamiltonian, self.pccd, **kwargs)
        self.rcc = self.fplccd
        self.results["fplccd"] = self.fplccd

    def do_fplccsd(self, **kwargs):
        if self.pccd is None:
            raise ValueError("Missing pCCD result (call do_pccd() first)")
        solver = RpCCDLCCSD(self.lf, self.occ_model)
        solver.t_p = self.t_p
        self.fplccsd = solver(
            *self.hamiltonian,
            self.pccd,
            solver="krylov",
            threshold_r=1e-6,
            **kwargs,
        )
        self.rcc = self.fplccsd
        self.results["fplccsd"] = self.fplccsd

    def do_lccsd(self, **kwargs):
        if self.hf is None:
            self.do_rhf()
        solver = RLCCSD(self.lf, self.occ_model)
        self.rcc = solver(
            *self.hamiltonian, self.hf, solver="krylov", threshold_r=1e-6
        )
        self.results["lccsd"] = self.rcc

    def do_ip_rcc(self, ip_cls, **kwargs):
        if self.rcc is None:
            raise ValueError("Missing RCC result")
        solver = ip_cls(
            self.lf,
            self.occ_model,
            alpha=kwargs["alpha"],
            spinfree=kwargs.get("spinfree"),
        )
        result = solver(
            *self.hamiltonian,
            self.rcc,
            nroot=kwargs["nroot"],
            nhole=kwargs.get("nhole", 2),
            nguessv=kwargs.get("nguessv", kwargs["nroot"] * 10),
            tolerancev=1e-8,
        )
        self.ip_rcc = result
        return result

    def do_dip_rcc(self, dip_cls, **kwargs):
        if self.rcc is None:
            raise ValueError("Missing RCC result")
        solver = dip_cls(self.lf, self.occ_model, alpha=kwargs["alpha"])
        result = solver(
            *self.hamiltonian,
            self.rcc,
            nroot=kwargs["nroot"],
            nhole=kwargs.get("nhole", 3),
            nguessv=kwargs.get("nguessv", kwargs["nroot"] * 10),
            tolerancev=1e-8,
        )
        self.dip_rcc = result
        return result
