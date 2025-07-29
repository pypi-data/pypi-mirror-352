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
"""Perturbation theory module

Variables used in this module:
 :ncore:      number of frozne core orbitals
 :nocc:       number of occupied orbitals in the principle configuration
 :nacto:      number of active occupied orbitals in the principle configuration
 :nvirt:      number of virtual orbitals in the principle configuration
 :nactv:      number of active virtual orbitals in the principle configuration
 :nbasis:     total number of basis functions
 :nact:       total number of active orbitals (nacto+nactv)
 :energy:     the energy correction, list that can contain different
              contributions
 :amplitudes: the optimized amplitudes, list that can contain different
              contributions
 :singles:    the singles amplitudes, bool used to determine whether singles
              are to be included or not

 Indexing convention:
  :i,j,k,..: occupied orbitals of principle configuration
  :a,b,c,..: virtual orbitals of principle configuration
  :p,q,r,..: general indices (occupied, virtual)
"""

import numpy as np

from pybest.auxmat import get_fock_matrix
from pybest.exceptions import (
    ArgumentError,
    ConsistencyError,
    EmptyData,
    NonEmptyData,
    SymmetryError,
)
from pybest.linalg import Orbital
from pybest.log import log, timer
from pybest.pt.perturbation_base import Perturbation
from pybest.utility import check_options, check_type, unmask


class pCCDPT2(Perturbation):
    """Perturbation base class for pCCD"""

    long_name = "2nd-order Pertrubation Theory"
    acronym = "pCCD-PT2"
    reference = "pCCD"
    overlap = ""
    include_fock = ""

    def unmask_args(self, *args, **kwargs):
        """Resolve arguments and keyword arguments passed to function call."""
        # t_p
        t_p = unmask("t_p", *args, **kwargs)
        if t_p is not None:
            self.checkpoint.update("t_p", t_p)
        else:
            raise ArgumentError("Cannot find Tp amplitudes.")
        # overlap of pCCD wave function, required by some pCCD-PT2 models
        overlap = unmask("overlap", *args, **kwargs)
        if self.overlap and overlap is None:
            raise EmptyData("overlap missing in pCCD container.")
        if overlap is not None:
            self.checkpoint.update("overlap", overlap)
        return Perturbation.unmask_args(self, *args, **kwargs)

    def calculate_amplitudes(self, *args, **kwargs):
        """Solve for amplitudes. Equations depend on the chosen flavor of the
        PT model.
        """
        raise NotImplementedError

    def calculate_energy(self, amplitudes, *args, **kwargs):
        """Calcuate total energy and energy contributions of a given PT model"""
        raise NotImplementedError

    @timer.with_section("PT2: Solver")
    def solve(self, *args, **kwargs):
        """Solve for energy and amplitudes

        **Arguments:**

        args
             Contains AO/MO and geminal coefficients

        **Keywords**
             :e_ref:      reference energy
             :threshold: threshold when checking symmetry of amplitudes
             :overlap:   approximate overlap used in PT2b-type PT
             :singles:   add single excitations (bool, default False)
        """
        log.cite("the PTX methods", "boguslawski2017a")

        #
        # Calculate amplitudes
        #
        amplitudes = self.calculate_amplitudes(*args, **kwargs)
        if self.singles:
            self.checkpoint.update("t_1", amplitudes[1])
        self.checkpoint.update("t_2", amplitudes[0])
        #
        # Calculate energy contributions of different seniority sectors
        # and total energy
        #
        energy = self.calculate_energy(amplitudes, *args, **kwargs)

        return energy, amplitudes

    def vfunction_0(self):
        """Elements of <bcjk|H|0>. Used in all PT2SD based methods.

        **Arguments:**

        args
             All function arguments needed to calculate the vector
             function:
        """
        #
        # B_jb|kc
        #
        govvo = self.get_aux_matrix("govvo")
        out = govvo.contract("abcd->acdb", factor=1.0, clear=True)
        return out

    def calculate_aux_matrix(self, mo1, mo2):
        """Compute auxiliary matrices

        **Arguments:**

        args
             List of arguments. Only geminal coefficients [1], one- [mo1]
             and two-body [mo2] integrals are used.
        """
        t_p = self.checkpoint["t_p"]
        self.clear_aux_matrix()
        self.update_aux_matrix(mo1, mo2, t_p)

    def init_aux_matrix(self, select):
        """Initialize auxiliary matrices

        **Arguments:**

        select
             One of ``fock``, ``ocjbc``, ``vcjkb``, ``ocjkb``,
             ``vcjbc``, ``dcjb``, ``'ocjb``, ``vcjb``

        """
        alloc_size = {
            "fock": (self.lf.create_two_index, self.nact),
            "ocjbc": (
                self.lf.create_three_index,
                self.nacto,
                self.nactv,
                self.nactv,
            ),
            "vcjbc": (
                self.lf.create_three_index,
                self.nacto,
                self.nactv,
                self.nactv,
            ),
            "vcjkb": (
                self.lf.create_three_index,
                self.nacto,
                self.nacto,
                self.nactv,
            ),
            "ocjkb": (
                self.lf.create_three_index,
                self.nacto,
                self.nacto,
                self.nactv,
            ),
            "dcjb": (self.lf.create_two_index, self.nacto, self.nactv),
            "ocjb": (self.lf.create_two_index, self.nacto, self.nactv),
            "vcjb": (self.lf.create_two_index, self.nacto, self.nactv),
            "govov": (
                self.denself.create_four_index,
                self.nacto,
                self.nactv,
                self.nacto,
                self.nactv,
            ),
            "govvo": (
                self.denself.create_four_index,
                self.nacto,
                self.nactv,
                self.nactv,
                self.nacto,
            ),
        }
        matrix, new = self._cache.load(
            select,
            alloc=alloc_size[select],
            tags="m",
        )
        if not new:
            raise NonEmptyData(
                f"The matrix {select} already exists. "
                "Call clear prior to updating the wfn."
            )
        return matrix

    @timer.with_section("PT2: Hamiltonian")
    def update_aux_matrix(self, mo1, mo2, cia):
        """Derive all matrices.
        fock_pq:     one_pq + sum_m(2<pm|qm> - <pm|mq>),
        oc_jbc:      sum_m(<mm|bc> c_jm^bc),
        vc_jkb:      sum_d(<dd|jk> c_jk^bd),
        vc_jbc:      sum_d(<dd|bc> c_j^d),
        oc_jkb:      sum_m(<mm|jk> c_m^b),
        dc_jb:       sum_md(<mm|dd> c_j^d*c_k^b),
        oc_jb:       sum_i(<jb|ii> c_i^b),
        vc_jb:       sum_a(<jb|aa> c_j^a),
        g_ovov:      <ov|ov>,
        g_ovvo:      <ov|vo>,

        **Arguments:**

        mo1, mo2
             one- and two-electron integrals to be sorted.

        cia
             The geminal coefficients. A TwoIndex instance
        """
        vvo = self.get_range("vvo")
        ovv = self.get_range("ovv")
        oov = self.get_range("oov")
        ovo = self.get_range("ovo")
        vvv = self.get_range("vvv")
        ooo = self.get_range("ooo")
        ov2 = self.get_range("ov", 2)
        ovov = self.get_range("ovov")
        ovvo = self.get_range("ovvo")
        #
        # Inactive Fock matrix
        #
        auxmat1 = self.init_aux_matrix("fock")
        get_fock_matrix(auxmat1, mo1, mo2, self.nacto)
        #
        # tmp storage
        #
        tmp = self.denself.create_two_index(self.nactv, self.nactv)
        # use 3-index intermediate (will be used several times)
        # This also works with Cholesky
        # tmpabc
        tmpabc = self.denself.create_three_index(self.nact)
        mo2.contract("abcc->abc", out=tmpabc, factor=1.0)
        #
        # oc_jbc = sum_m <mm|bc> c_jm^bc
        #
        auxmat2 = self.init_aux_matrix("ocjbc")
        tmpabc.contract("abc,cb->ab", cia, tmp, clear=True, **vvo)
        cia.contract("ab,bc->abc", tmp, auxmat2)
        # P_jm
        tmpabc.contract("abc,ca->ab", cia, tmp, clear=True, **vvo)
        cia.contract("ac,bc->abc", tmp, auxmat2)
        #
        # vc_jkb = sum_d <dd|jk> c_jk^bd
        #
        auxmat3 = self.init_aux_matrix("vcjkb")
        # tmp storage
        tmp = self.denself.create_two_index(self.nacto, self.nacto)
        tmpabc.contract("abc,bc->ab", cia, tmp, clear=True, **oov)
        tmp.contract("ab,ac->abc", cia, auxmat3)
        # P_jm
        tmpabc.contract("abc,ac->ab", cia, tmp, clear=True, **oov)
        tmp.contract("ab,bc->abc", cia, auxmat3)
        #
        # vc_jbc = sum_d <bc|dd> c_j^d
        #
        auxmat4 = self.init_aux_matrix("vcjbc")
        tmpabc.contract("abc,dc->dab", cia, auxmat4, clear=True, **vvv)
        #
        # oc_jkb = sum_m <mm|jk> c_m^b
        #
        auxmat5 = self.init_aux_matrix("ocjkb")
        tmpabc.contract("abc,cd->abd", cia, auxmat5, clear=True, **ooo)
        #
        # OLD:
        # dc_jb = sum_md <mm|dd> c_jm^bd
        # NEW:
        # dc_jb = sum_md <mm|dd> c_m^b c_j^d
        #
        auxmat6 = self.init_aux_matrix("dcjb")
        tmp = self.lf.create_two_index(self.nact, self.nact)
        tmp2 = self.lf.create_two_index(self.nacto, self.nacto)
        # There is a bug in np.einsum that forces us to slice first
        # Slice nevertheless to make it work with cholesky
        mo2.contract("aabb->ab", out=tmp, factor=1.0, clear=True)
        cia.contract("ab,cb->ac", tmp, tmp2, clear=True, **ov2)
        cia.contract("ab,ca->cb", tmp2, auxmat6)
        #
        # oc_jb = sum_i <jb|ii> c_j^b
        #
        auxmat7 = self.init_aux_matrix("ocjb")
        tmpabc.contract("abc,ab->ab", cia, auxmat7, clear=True, **ovo)
        #
        # vc_jb = sum_i <jb|aa> c_j^b
        #
        auxmat8 = self.init_aux_matrix("vcjb")
        tmpabc.contract("abc,ab->ab", cia, auxmat8, clear=True, **ovv)
        #
        # g_ovov
        #
        auxmat9 = self.init_aux_matrix("govov")
        mo2.contract("abcd->abcd", out=auxmat9, factor=1.0, clear=True, **ovov)
        #
        # g_ovvo
        #
        auxmat10 = self.init_aux_matrix("govvo")
        mo2.contract(
            "abcd->abcd", out=auxmat10, factor=1.0, clear=True, **ovvo
        )
        del tmp, tmpabc, tmp2

    def update_ndm(self, ndm=None):
        """Update 1-RDM

        **Optional arguments:**

        one_dm
             When provided, this 1-RDM is stored.
        """

    def print_results(self, **kwargs):
        """Print final results to standard output."""
        if log.do_medium:
            log(
                f"E_{self.acronym + '(Seniority 0):':<22} "
                f"{self.energy['e_corr_s0']:> 16.12f} a.u."
            )
            log(
                f"E_{self.acronym + '(Seniority 2):':<22} "
                f"{self.energy['e_corr_s2']:> 16.12f} a.u."
            )
            log(
                f"E_{self.acronym + '(Seniority 4):':<22} "
                f"{self.energy['e_corr_s4']:> 16.12f} a.u."
            )
            log.hline("-")
            log(
                f"E_{self.acronym + '(singles):':<22} {self.energy['e_corr_s']:> 16.12f} a.u."
            )
            log(
                f"E_{self.acronym + '(doubles):':<22} {self.energy['e_corr_d']:> 16.12f} a.u."
            )
            log.hline("-")
            log(f"E_{'ref:':<22} {self.e_ref:> 16.12f} a.u.")
            log(
                f"E_{self.acronym + ':':<22} "
                f"{self.energy['e_tot']:> 16.12f} a.u."
            )
            log.hline("-")
            log(
                f"E_{'tot(d):':<22} {self.energy['e_corr_d'] + self.e_ref:> 16.12f} a.u."
            )
            if self.singles:
                log(
                    f"E_{'tot(s+d):':<22} "
                    f"{self.energy['e_tot']:> 16.12f} a.u."
                )

    def print_info(self, **kwargs):
        """Print information on keyword arguments and other properties of a
        given PT flavour.
        """
        if log.do_medium:
            log(f"{self.acronym} perturbation module")
            log(" ")
            log("OPTIMIZATION PARAMETERS:")
            log("Reference Function              pCCD")
            log(f"Number of frozen core orbitals: {self.ncore}")
            log(f"Number of occupied orbitals:    {self.nacto}")
            log(f"Number of virtual orbitals:     {self.nactv}")
            if self.overlap:
                olp = self.checkpoint["overlap"]
                log(f"Approximate overlap:            {olp:f}")
            log.hline()

    def check_input(self, **kwargs):
        """Check input parameters."""
        for name in kwargs:
            check_options(name, name, "e_ref", "threshold", "indextrans")

    def check_result(self, **kwargs):
        """Check if amplitudes are reasonable."""
        thresh = kwargs.get("threshold", 1e-6)

        # check symmetry of amplitudes:
        if not self.amplitudes[0].is_symmetric("cdab", atol=thresh):
            raise SymmetryError("Warning: Cluster amplitudes not symmetric.")

        excludepairs = kwargs.get("excludepairs", True)
        if excludepairs:
            # check if diagonal amplitudes are zero:
            tmp = self.amplitudes[0].contract("abab->ab", clear=True)
            if tmp.sum() > thresh:
                raise ConsistencyError(
                    "Warning: Diagonal cluster amplitudes not negligible."
                )

    @timer.with_section("PT2: VecFct")
    def vfunction_psi0(self, *args, **kwargs):
        """Elements of <bcjk|H|pCCD>. Used in all PT models.

        **Arguments:**

        args
             All function arguments needed to calculate the vector
             function:

             * [0]:  wfn expansion coefficients
             * [1]:  geminal coefficients
        """
        check_type("args[0]", args[0], Orbital)
        t_p = self.checkpoint["t_p"]
        excludepairs = kwargs.get("excludepairs", True)
        #
        # Get ranges
        #
        vv2 = self.get_range("vv", 2)
        oo2 = self.get_range("oo", 2)
        ov2 = self.get_range("ov", 2)
        #
        # Get aux matrices
        #
        fockmod = self.get_aux_matrix("fock")
        vcjkb = self.get_aux_matrix("vcjkb")
        ocjbc = self.get_aux_matrix("ocjbc")
        vcjbc = self.get_aux_matrix("vcjbc")
        ocjkb = self.get_aux_matrix("ocjkb")
        dcjb = self.get_aux_matrix("dcjb")
        ocjb = self.get_aux_matrix("ocjb")
        vcjb = self.get_aux_matrix("vcjb")
        govov = self.get_aux_matrix("govov")
        govvo = self.get_aux_matrix("govvo")
        #
        # Get proper Fock matrix (depends on PT model used)
        #
        if self.include_fock:
            fockmod = self.compute_modified_fock(fockmod, **kwargs)

        #
        # output
        #
        out = self.denself.create_four_index(
            self.nacto, self.nactv, self.nacto, self.nactv
        )
        outs = self.denself.create_two_index(self.nacto, self.nactv)
        #
        # temporary storage
        #
        tmp4ind = self.denself.create_four_index(
            self.nacto, self.nactv, self.nacto, self.nactv
        )
        tmp3ind0 = self.denself.create_three_index(
            self.nacto, self.nactv, self.nactv
        )
        tmp3ind1 = self.denself.create_three_index(
            self.nacto, self.nacto, self.nactv
        )

        #
        # <jk|bc>
        #
        govvo.contract("abcd->acdb", out=out, factor=1.0, clear=True)
        #
        # c_kc <jc||bk>
        #
        govvo.contract("abcd,db->acdb", t_p, out)
        govov.contract("abcd,cb->adcb", t_p, out, factor=-1.0)
        #
        # c_jb <jc||bk>
        #
        govvo.contract("abcd,ac->acdb", t_p, out)
        govov.contract("abcd,ad->adcb", t_p, out, factor=-1.0)
        #
        # c_jc <bk|cj>
        #
        govov.contract("abcd,ab->adcb", t_p, out, factor=-1.0)
        #
        # c_kb <bk|cj>
        #
        govov.contract("abcd,cd->adcb", t_p, out, factor=-1.0)
        #
        # c_jkbc <bk|jc>
        #
        govvo.contract("abcd,ac->acdb", t_p, tmp4ind, clear=True)
        tmp4ind.contract("abcd,cd->abcd", t_p, out)
        govvo.contract("abcd,ab->acdb", t_p, tmp4ind, clear=True)
        tmp4ind.contract("abcd,cb->abcd", t_p, out)
        #
        # delta_jk [ c_jc F_bc ]
        #
        if self.include_fock:
            t_p.contract("ac,bc->abc", fockmod, tmp3ind0, **vv2)
        #
        # delta_jk [ c_jb F_bc ]
        #
        if self.include_fock:
            t_p.contract("ab,bc->abc", fockmod, tmp3ind0, **vv2)
        #
        # delta_jk [ oc_jbc ]
        #
        tmp3ind0.iadd(ocjbc, -1.0)
        #
        # delta_jk [ vc_jbc ]
        #
        tmp3ind0.iadd(vcjbc, 1.0)
        #
        # Add delta_jk-contribution
        #
        tmp3ind0.expand("abc->abac", out)
        #
        # delta_bc [ c_jb F_jk ]
        #
        if self.include_fock:
            t_p.contract("ab,ac->acb", fockmod, tmp3ind1, factor=-1.0, **oo2)
        #
        # delta_bc [ c_kb F_jk ]
        #
        if self.include_fock:
            t_p.contract("cb,ac->acb", fockmod, tmp3ind1, factor=-1.0, **oo2)
        #
        # delta_bc [ vc_jkb ]
        #
        tmp3ind1.iadd(vcjkb, -1.0)
        #
        # delta_bc [ oc_jkb ]
        #
        tmp3ind1.iadd(ocjkb, 1.0)
        #
        # Add delta_bc-contribution
        #
        tmp3ind1.expand("abc->acbc", out)
        #
        #
        # delta_bc,jk [ (sum_md <mm|dd> c_jm c_mb) ]
        #
        dcjb.expand("ab->abab", out)
        #
        # Single excitations
        #
        #
        # F_jb*c_jb
        #
        if self.include_fock:
            outs.assign(t_p)
            outs.imul(fockmod, 1.0, **ov2)
        #
        # F_jb
        #
        if self.include_fock:
            outs.iadd(fockmod, 1.0, **ov2)
        #
        # (sum_a <jb|aa> c_ja)
        #
        outs.iadd(vcjb)
        #
        # (sum_i <jb|ii> c_ib)
        #
        outs.iadd(ocjb, -1.0)

        # Get rid of pair amplitudes:
        if excludepairs:
            ind1, ind2 = np.indices((self.nacto, self.nactv))
            indices = [ind1, ind2, ind1, ind2]
            out.assign(0.0, indices)

        return [out, outs]

    def compute_modified_fock(self, oldfock, **kwargs):
        """Scale diagonal of Fock matrix using wfn overlap. Only effective for
        some PT flavours.
        """
        raise NotImplementedError
