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
# This module has been originally written and updated by Katharina Boguslawski (see CHANGELOG)
# Its current version contains updates from the PyBEST developer team.
#
# Part of this implementation can also be found in `Horton 2.0.0`.
# However, this file has been updated and debugged. Compatibility with Horton is NOT
# guaranteed.
#
# Detailed changes (see also CHANGELOG):
# 2020-07-01: update class structure and init procedure
# 2020-07-01: make function call more user friendly and black box by passing IOData instance
# 2020-07-01: update to new python features, including f-strings
# 2020-07-01: use PyBEST standards, including naming convention and filemanager
# 2020-07-01: new features: spin-component scaled MP2, relaxed response 1-RDM

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

 Indexing convention:
  :i,j,k,..: occupied orbitals of principle configuration
  :a,b,c,..: virtual orbitals of principle configuration
  :p,q,r,..: general indices (occupied, virtual)
"""

import numpy as np
from scipy import linalg

from pybest.auxmat import get_fock_matrix
from pybest.exceptions import NonEmptyData, SymmetryError
from pybest.linalg import FourIndex, OneIndex, Orbital, TwoIndex
from pybest.log import log, timer
from pybest.pt.perturbation_base import Perturbation
from pybest.pt.perturbation_utils import get_pt2_amplitudes
from pybest.utility import check_options, check_type


class RMP2(Perturbation):
    """Moller-Plesset Perturbation Theory of second order

    Purpose:
    Optimize amplitudes and determine energy correction to Hartree-Fock
    reference wavefunction.
    """

    acronym = "MP2"

    def __init__(self, lf, occ_model):
        # default scaling factors used in MP2 module
        self.fss = 1.0
        self.fos = 1.0
        Perturbation.__init__(self, lf, occ_model)

    @property
    def fss(self):
        """The same spin scaling factor"""
        return self._fss

    @fss.setter
    def fss(self, new):
        self._fss = new

    @property
    def fos(self):
        """The opposite spin scaling factor"""
        return self._fos

    @fos.setter
    def fos(self, new):
        self._fos = new

    @timer.with_section("RMP2: Solver")
    def solve(self, *args, **kwargs):
        """Solve for energy and amplitudes using a biorthogonal basis.

        **Arguments:**

        args
             Contains one- and two-electron integrals in the MO basis
                 * [0]:  wfn expansion coefficients
                 * [1]:  1-el MO integrals
                 * [2]:  2-el MO integrals

        **Keywords**
             :threshold: threshold for symmetry check of MP2 amplitudes
        """
        self.fss = kwargs.get("fss", 1.0)
        self.fos = kwargs.get("fos", 1.0)
        self.checkpoint.update("fss", self.fss)
        self.checkpoint.update("fos", self.fos)

        self.singles = kwargs.get("singles", False)
        self.checkpoint.update("singles", self.singles)

        if self.singles:
            if self.relaxation or self.natorb:
                log.warn(
                    "Orbital relaxation contributions from singles not implemented "
                    "in MP2 module"
                )

        check_type("args[0]", args[0], Orbital)
        fock = self.get_aux_matrix("fock")
        ov2 = self.get_range("ov", start=2)
        #
        # Calculate excitation matrix <jb|kc>
        #
        giajb = self.calculate_ex_matrix()
        #
        # Calculate MP2 amplitudes t_jbkc
        #
        amplitudes = self.calculate_amplitudes(giajb)
        freeze = kwargs.get("freeze", [])
        if freeze:
            amplitudes[0].assign(freeze[1], freeze[0])
            amplitudes[-1].assign(freeze[1], freeze[0])
        self.checkpoint.update("t_2", amplitudes[0])
        self.checkpoint.update("l_2", amplitudes[-1])
        #
        # Calculate MP2 energy correction
        #
        e_tot = self.e_ref
        e_corr = 0.0
        # doubles
        energy_dict = {}
        l_abij = self.get_aux_matrix("l_abij")
        energy = amplitudes[0].contract("abcd,abcd", l_abij)
        energy_dict.update({"e_corr_d": energy})
        # SOS component determined from Lambda
        osenergy = amplitudes[0].contract("abcd,abcd", giajb) * self.fos
        # FIXME: fss energy can be implemented more efficiently
        ssenergy = amplitudes[0].contract("abcd,abcd", l_abij)
        ssenergy -= amplitudes[0].contract("abcd,abcd", giajb)
        ssenergy *= self.fss
        energy = ssenergy + osenergy
        # update e_tot and e_corr
        e_tot += energy
        e_corr += energy
        pairenergy = amplitudes[0].contract("abab,abab", giajb)
        energy_dict.update({"e_corr_p": pairenergy})
        energy_dict.update({"e_corr_ss": ssenergy})
        energy_dict.update({"e_corr_os": osenergy})
        # singles
        if self.singles:
            senergy = 2.0 * amplitudes[1].contract("ab,ab", fock, **ov2)
            energy_dict.update({"e_corr_s": senergy})
            self.checkpoint.update("t_1", amplitudes[1])
            e_tot += senergy
            e_corr += senergy

        energy_dict.update({"e_tot": e_tot})
        energy_dict.update({"e_corr": e_corr})
        return energy_dict, amplitudes

    @timer.with_section("RMP2: ExMatrix")
    def calculate_ex_matrix(self):
        """Calculates excitation matrix with elements (jbkc)

        **Arguments:**

        mo2
            2-el MO integrals
        """
        #
        # B_jb|kc
        #
        govvo = self.get_aux_matrix("govvo")
        out = govvo.contract("abcd->acdb", factor=1.0, clear=True)
        return out

    @timer.with_section("RMP2: T Solver")
    def calculate_amplitudes(self, exmatrix):
        """Calculates MP2 amplitudes

        **Arguments:**

        exmatrix
            Sliced 2-el MO integrals
        """
        #
        # Get auxmatrices
        #
        l_abij = self.get_aux_matrix("l_abij")
        fock = self.get_aux_matrix("fock")
        #
        # Get diagonal part of Fock matrix
        #
        fdiago = fock.copy_diagonal(end=self.nacto)
        fdiagv = fock.copy_diagonal(begin=self.nacto)

        if self.singles:
            ts, td, lag = get_pt2_amplitudes(
                self.denself,
                [fock, exmatrix, l_abij],
                [fdiago, fdiagv],
                singles=self.singles,
                lagrange=True,
            )
        else:
            td, lag = get_pt2_amplitudes(
                self.denself,
                [exmatrix, l_abij],
                [fdiago, fdiagv],
                singles=self.singles,
                lagrange=True,
            )
        #
        # Update for SOS and SSS
        # This is a work around and does not account for the efficiency of SOS
        # calculations
        if self.fss != 1.0 or self.fos != 1.0:
            # SSS component
            lag.iadd(td, -1.0)
            lag.iscale(self.fss)
            # SOS component
            lag.iadd(td, self.fos)
        if self.singles:
            return [td, ts, lag]
        return [td, lag]

    def calculate_aux_matrix(self, mo1, mo2):
        """Compute auxiliary matrices

        **Arguments:**

        args
             One- and two-electron integrals (some Hamiltonian matrix
             elements) in the MO basis.
        """
        check_type("args[1]", mo1, TwoIndex)
        check_type("args[2]", mo2, FourIndex)
        self.clear_aux_matrix()
        self.update_aux_matrix(mo1, mo2)

    def init_aux_matrix(self, select):
        """Initialize auxiliary matrices

        **Arguments:**

        select
             One of 'fock', 'l_iajk', 'l_akij', 'l_abic', 'l_aijb', 'l_abij',
             'l_ajbc', 'govvo'
        """
        alloc_size = {
            "fock": (self.lf.create_two_index, self.nact),
            "l_iajk": (
                self.denself.create_four_index,
                self.nacto,
                self.nactv,
                self.nacto,
                self.nacto,
            ),
            "l_abic": (
                self.denself.create_four_index,
                self.nactv,
                self.nactv,
                self.nacto,
                self.nactv,
            ),
            "l_aijb": (
                self.denself.create_four_index,
                self.nactv,
                self.nacto,
                self.nacto,
                self.nactv,
            ),
            "l_abij": (
                self.denself.create_four_index,
                self.nacto,
                self.nactv,
                self.nacto,
                self.nactv,
            ),
            "l_akij": (
                self.denself.create_four_index,
                self.nactv,
                self.nacto,
                self.nacto,
                self.nacto,
            ),
            "l_ajbc": (
                self.denself.create_four_index,
                self.nactv,
                self.nacto,
                self.nactv,
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

    @timer.with_section("RMP2: Hamiltonian")
    def update_aux_matrix(self, mo1, mo2):
        """Derive all auxiliary matrices.
        fock_pp:     one_pp + sum_m(2<pm|pm> - <pm|mp>),

        **Arguments:**

        mo1, mo2
             one- and two-electron integrals.
        """
        auxmat1 = self.init_aux_matrix("fock")
        get_fock_matrix(auxmat1, mo1, mo2, self.nacto)

        #
        # Get views of arrays and tensors
        #
        vvoo = self.get_range("vvoo")
        ovvo = self.get_range("ovvo")
        voov = self.get_range("voov")
        vovo = self.get_range("vovo")
        ovoo = self.get_range("ovoo")
        vooo = self.get_range("vooo")
        vvov = self.get_range("vvov")
        vvvo = self.get_range("vvvo")
        vovv = self.get_range("vovv")
        #
        # exchange integrals l_abij <ab||ij>; stored as iajb
        #
        auxmat4 = self.init_aux_matrix("l_abij")
        mo2.contract("abcd->cadb", out=auxmat4, factor=2.0, clear=True, **vvoo)
        mo2.contract("abcd->dacb", out=auxmat4, factor=-1.0, **vvoo)

        #
        # g_ovvo
        #
        auxmat7 = self.init_aux_matrix("govvo")
        mo2.contract("abcd->abcd", out=auxmat7, factor=1.0, clear=True, **ovvo)

        if self.natorb:
            #
            # exchange integrals l_iajk <ia||jk>
            #
            auxmat2 = self.init_aux_matrix("l_iajk")
            mo2.contract(
                "abcd->abcd", out=auxmat2, factor=1.0, clear=True, **ovoo
            )

            #
            # exchange integrals l_akij <ak||ij>
            #
            auxmat2 = self.init_aux_matrix("l_akij")
            mo2.contract(
                "abcd->abcd", out=auxmat2, factor=2.0, clear=True, **vooo
            )
            mo2.contract("abcd->abdc", out=auxmat2, factor=-1.0, **vooo)

            #
            # exchange integrals l_abic <ab||ic>
            #
            auxmat3 = self.init_aux_matrix("l_abic")
            mo2.contract(
                "abcd->abcd", out=auxmat3, factor=2.0, clear=True, **vvov
            )
            mo2.contract("abcd->abdc", out=auxmat3, factor=-1.0, **vvvo)

            #
            # exchange integrals l_aijb <ai||jb>
            #
            auxmat5 = self.init_aux_matrix("l_aijb")
            mo2.contract(
                "abcd->abcd", out=auxmat5, factor=2.0, clear=True, **voov
            )
            mo2.contract("abcd->abdc", out=auxmat5, factor=-1.0, **vovo)

            #
            # exchange integrals l_ajbc <aj||bc>
            #
            auxmat6 = self.init_aux_matrix("l_ajbc")
            mo2.contract(
                "abcd->abcd", out=auxmat6, factor=1.0, clear=True, **vovv
            )

    def print_results(self, **kwargs):
        natorb = kwargs.get("natorb", False)
        if log.do_medium:
            log(f"E_ref: {self.e_ref:>25.8f} a.u.")
            log(" ")
            if self.singles:
                log(f"E_MP2(singles): {self.energy['e_corr_s']:>16.8f} a.u.")
            log(f"E_MP2(doubles): {self.energy['e_corr_d']:>16.8f} a.u.")
            log(f"E_MP2(SS): {self.energy['e_corr_ss']:>21.8f} a.u.")
            log(f"E_MP2(OS): {self.energy['e_corr_os']:>21.8f} a.u.")
            log(f"E_MP2(pairs): {self.energy['e_corr_p']:>18.8f} a.u.")
            log(" ")
            log(f"E_MP2: {self.energy['e_corr']:>25.8f} a.u.")
            log(
                f"E_MP2/pairs: {(self.energy['e_corr'] - self.energy['e_corr_p']):>19.8f} a.u."
            )
            log.hline("-")
            log(f"E_tot: {(self.energy['e_tot']):>25.8f} a.u.")
            log(
                f"E_tot/pairs: "
                f"{(self.energy['e_tot'] - self.energy['e_corr_p']):>19.8f} a.u."
            )
            log(" ")
            if natorb:
                log("MP2 natural occupation numbers:")
            else:
                log("MP2 occupation numbers:")
            s = ""
            for occn in self.checkpoint["orb_a"].occupations:
                s += str(f"{occn:< 14.8f}")
            log(s)

    def print_info(self, **kwargs):
        singles = kwargs.get("singles", False)
        fos = kwargs.get("fos", 1.0)
        fss = kwargs.get("fss", 1.0)
        if log.do_medium:
            log("MP2 perturbation module")
            log(" ")
            log("OPTIMIZATION PARAMETERS:")
            log(f"Reference Function {'RHF':>20}")
            log(f"Number of frozen core orbitals: {self.ncore:>5}")
            log(f"Number of occupied orbitals: {self.nacto:>8}")
            log(f"Number of virtual orbitals: {self.nactv:>10}")
            log(f"Same spin scaling factor (fss): {fss:>7}")
            log(f"Opposite spin scaling factor (fos): {fos}")
            log(f"Include singles excitations: {'':>6s} {singles!s}")
            log(f"Calculate natural orbitals: {'':>7s} {self.natorb!s}")
            log.hline()

    def check_input(self, **kwargs):
        """Check input parameters"""
        for name in kwargs:
            check_options(
                "name",
                name,
                "threshold",
                "indextrans",
                "natorb",
                "freeze",
                "relaxation",
                "fss",
                "fos",
                "singles",
                "e_ref",
            )

    def check_result(self, **kwargs):
        """Check if amplitudes are symmetric (within a given threshold)."""
        thresh = kwargs.get("threshold", 1e-6)

        if not self.amplitudes[0].is_symmetric("cdab", atol=thresh):
            raise SymmetryError("Warning: Cluster amplitudes not symmetric!")

    #
    # Density matrices:
    #
    def update_ndm(self, ndm=None):
        """Update 1-RDM

        **Arguments:**

        **Optional arguments:**

        one_dm
             When provided, this 1-RDM is stored. A OneIndex instance.
        """
        cached_one_dm = self.init_ndm("one_dm")
        if ndm is None:
            self.compute_1dm(
                cached_one_dm, self.amplitudes[0], self.amplitudes[-1]
            )
        else:
            ind = None
            if isinstance(ndm, OneIndex):
                ind = np.diag_indices(ndm.nbasis)
            cached_one_dm.assign(ndm, ind)

    def compute_1dm(self, dmout, amplitudes, lagrangem):
        """Compute 1-RDM for MP2

        **Arguments:**

        amplitudes
             A DenseTwoIndex instance used to calculated 1-RDM.

        """
        occblock = self.lf.create_two_index(self.nacto, self.nacto)
        virtblock = self.lf.create_two_index(self.nactv, self.nactv)
        #
        # Assign frozen block
        #
        if self.ncore > 0:
            dmout.assign_diagonal(2.0, end=self.ncore)
        #
        # Calculate occupied block
        #
        amplitudes.contract("abcd,ebcd->ae", lagrangem, occblock, factor=-2.0)
        dmout.assign(
            occblock,
            begin0=self.ncore,
            end0=(self.nacto + self.ncore),
            begin1=self.ncore,
            end1=(self.nacto + self.ncore),
        )

        #
        # Calculate virtual block
        #
        amplitudes.contract("abcd,aecd->be", lagrangem, virtblock, factor=2.0)
        dmout.assign(
            virtblock,
            begin0=(self.nacto + self.ncore),
            end0=(self.nact + self.ncore),
            begin1=(self.nacto + self.ncore),
            end1=(self.nact + self.ncore),
        )

        if self.relaxation:
            self.compute_1dm_relaxation(dmout, lagrangem)
        #
        # RHF contribution
        #
        dmout.iadd_diagonal(
            2.0, begin0=self.ncore, end0=(self.ncore + self.nacto)
        )
        #
        # Store only alpha component
        #
        dmout.iscale(0.5)

    @timer.with_section("RMP2: 1DM Relaxation")
    def compute_1dm_relaxation(self, dmout, amplitudes):
        """Compute relaxation part 1-RDM for MP2

        **Arguments:**

        amplitudes
             A DenseTwoIndex instance used to calculated 1-RDM.

        """
        fock = self.get_aux_matrix("fock")
        l_iajk = self.get_aux_matrix("l_iajk")
        l_akij = self.get_aux_matrix("l_akij")
        l_abic = self.get_aux_matrix("l_abic")
        l_abij = self.get_aux_matrix("l_abij")
        l_aijb = self.get_aux_matrix("l_aijb")
        l_ajbc = self.get_aux_matrix("l_ajbc")

        oo4 = self.get_range("cc", start=4)
        vv4 = self.get_range("CC", start=4)
        #
        # Construct Iai intermediate
        #
        iai = self.lf.create_two_index(self.nactv, self.nacto)
        # (ai) = t_ka,jb.<ib||kj>
        amplitudes.contract(
            "abcd,edac->be", l_iajk, out=iai, factor=-2.0, clear=True
        )
        amplitudes.contract("abcd,ebca->de", l_iajk, out=iai, factor=-2.0)
        #
        # Construct Xai intermediate
        #
        # (ai) = D_kj.<ak||ij>
        l_akij.contract("abcd,bd->ac", dmout, iai, **oo4)
        # (ai) = D_kj.<aj||ik>
        l_akij.contract("abcd,db->ac", dmout, iai, **oo4)
        # (ai) = D_cb.<ac||ib>
        l_abic.contract("abcd,bd->ac", dmout, iai, **vv4)
        # (ai) = D_cb.<ab||ic>
        l_abic.contract("abcd,db->ac", dmout, iai, **vv4)
        # (ai) = t_ic,jb.<aj||bc>
        l_ajbc.contract("abcd,ecbd->ae", amplitudes, iai, factor=2.0)
        l_ajbc.contract("abcd,bdec->ae", amplitudes, iai, factor=2.0)

        #
        # Construct Aaibj intermediate
        #
        Aaibj = self.denself.create_four_index(
            self.nactv, self.nacto, self.nactv, self.nacto
        )
        # Get diagonal part of Fock matrix
        fdiago = fock.copy_diagonal(end=self.nacto)
        fdiagv = fock.copy_diagonal(begin=self.nacto)
        fai = self.lf.create_two_index(self.nactv, self.nacto)
        fai.iadd(fdiagv, -1.0)
        fai.iadd(fdiago, 1.0, transpose=True)
        l_abij.contract("abcd->badc", out=Aaibj, factor=-2.0, clear=True)
        l_aijb.contract("abcd->acdb", out=Aaibj, factor=-2.0)
        # assign Fock matrix to aiai block
        ind1, ind2 = np.indices((self.nactv, self.nacto))
        indices = [ind1, ind2, ind1, ind2]
        Aaibj.iadd(fai, ind=indices, factor=2.0)

        #
        # Solve CPHF equations to get perturbed DMs as Aaijb.solai=iai
        #
        sol = linalg.solve(
            np.reshape(
                Aaibj._array,
                (self.nacto * self.nactv, self.nacto * self.nactv),
            ),
            iai._array.ravel(),
        )
        sol = sol.reshape(self.nactv, self.nacto)
        for a in range(self.nactv):
            aa = a + self.nacto
            for i in range(self.ncore, self.nacto):
                dmout.set_element(aa, i, sol[a, i], symmetry=2)
