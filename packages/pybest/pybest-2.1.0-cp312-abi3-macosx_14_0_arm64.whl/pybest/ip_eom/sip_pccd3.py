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

"""Ionization Potential Equation of Motion Coupled Cluster implementations for
a pCCD reference function for 3 unpaired electrons (S_z = 1.5)

   Variables used in this module:
    :ncore:     number of frozen core orbitals
    :nocc:      number of occupied orbitals in the principal configuration
    :nacto:     number of active occupied orbitals in the principal configuration
    :nvirt:     number of virtual orbitals in the principal configuration
    :nactv:     number of active virtual orbitals in the principal configuration
    :nbasis:    total number of basis functions
    :nact:      total number of active orbitals (nacto+nactv)
    :e_ip:      the energy correction for IP
    :civ_ip:    the CI amplitudes from a given EOM model
    :alpha:     number of unpaired electrons; for alpha=0, the spin-integrated
                equations target all possible m_s=0 states (singlet, triplet,
                quintet), for alpha=1, m_s=1/2 states are accessible (doublet,
                quartet), for alpha=2, m_s=1 states (triplet, quintet), for
                alpha=3, m_s=3/2 states (quartet), and for alpha=4, m_s=2 states
                (quintet)
    :cia:       the pCCD pair amplitudes (T_p)

   Indexing convention:
    :i,j,k,..: occupied orbitals of principal configuration
    :a,b,c,..: virtual orbitals of principal configuration
    :p,q,r,..: general indices (occupied, virtual)

Abbreviations used (if not mentioned in doc-strings; all ERI are in
physicists' notation):
 :<pq||rs>: <pq|rs>-<pq|sr>
"""

from functools import partial
from typing import Any

from pybest.auxmat import get_fock_matrix
from pybest.ip_eom.sip_base import RSIPCC3
from pybest.linalg import (
    CholeskyFourIndex,
    DenseFourIndex,
    DenseOneIndex,
    DenseTwoIndex,
)
from pybest.log import timer


class RIPpCCD3(RSIPCC3):
    """
    Restricted Single Ionization Potential Equation of Motion Coupled Cluster
    class restricted to Single IP for a pCCD reference function for 3 unpaired
    electrons.

    This class defines only the function that are unique for the IP-pCCD model
    with 3 unpaired electrons:

        * dimension (number of degrees of freedom)
        * unmask_args (resolve T_p amplitudes)
        * set_hamiltonian (calculates effective Hamiltonian -- at most O(o2v2))
        * compute_h_diag (pre-conditioner used by Davidson)
        * build_subspace_hamiltonian (subspace to be diagonalized)
        * print functions (ci vector and weights)
    """

    long_name = (
        "Ionization Potential Equation of Motion pair Coupled Cluster Doubles"
    )
    acronym = "IP-EOM-pCCD"
    reference = "pCCD"
    order = "IP"
    alpha = 3

    @timer.with_section("IPpCCD3: H_diag")
    def compute_h_diag(self, *args: Any) -> DenseOneIndex:
        """Used by the Davidson module for pre-conditioning

        **Arguments:**

        args:
            required for the Davidson module (not used here)
        """
        cia = self.checkpoint["t_p"]
        h_diag = self.lf.create_one_index(self.dimension, label="h_diag")
        #
        # Get effective Hamiltonian terms
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        goooo = self.from_cache("goooo")
        x1im = self.from_cache("x1im")
        x4bd = self.from_cache("x4bd")
        goovv = self.from_cache("goovv")
        govov = self.from_cache("govov")
        #
        # Intermediates
        #
        lij = x1im.new()
        goooo.contract("abab->ab", out=lij)
        goooo.contract("abab->ab", out=lij, factor=-1.0)
        gjjbb = goovv.contract("aabb->ab", out=None)
        gjbjb = govov.contract("abab->ab", out=None)
        #
        # H_ijB,ijB
        #
        h_ijb = self.lf.create_three_index(nacto, nacto, nactv)
        #
        # x1im(j,j)
        #
        x1im.expand("bb->abc", h_ijb)
        #
        # 0.5 x4bd(b,b)
        #
        x4bd.expand("cc->abc", h_ijb, factor=0.5)
        #
        # 0.25 lij
        #
        lij.expand("aa->abc", h_ijb, factor=0.25)
        #
        # gjbjb
        #
        gjbjb.expand("bc->abc", h_ijb)
        #
        # gjjbb cjb
        #
        cia_ = cia.copy()
        cia_.imul(gjjbb)
        cia_.expand("bc->abc", h_ijb)
        #
        h_ijb.iadd_transpose((1, 0, 2), factor=1.0)
        #
        # Assign using mask
        #
        h_diag.assign(h_ijb.array[self.get_mask(0)])
        return h_diag

    @timer.with_section("IPpCCD3: H_sub")
    def build_subspace_hamiltonian(
        self, b_vector: DenseOneIndex, h_diag: DenseOneIndex, *args: Any
    ) -> None:
        """
        Used by the Davidson module to construct subspace Hamiltonian

        **Arguments:**

        b_vector:
            (OneIndex object) contains current approximation to CI coefficients

        h_diag:
            Diagonal Hamiltonian elements required in the Davidson module (not used
            here)

        args:
            Set of arguments passed by the Davidson module (not used here)
        """
        cia = self.checkpoint["t_p"]
        #
        # Get effective Hamiltonian terms
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        x1im = self.from_cache("x1im")
        x4bd = self.from_cache("x4bd")
        goooo = self.from_cache("goooo")
        govov = self.from_cache("govov")
        govvo = self.from_cache("govvo")
        #
        # Calculate sigma vector s = (H.b)_ijB
        #
        # output
        s_3 = self.lf.create_three_index(nacto, nacto, nactv)
        to_s_3 = {"out": s_3, "clear": False}
        sigma = self.lf.create_one_index(self.dimension)
        # Inpute
        b_3 = self.lf.create_three_index(nacto, nacto, nactv)
        #
        # reshape b_vector
        #
        b_3.clear()
        b_3.assign(b_vector, ind0=self.get_index_of_mask(0))
        b_3.iadd_transpose((1, 0, 2), factor=-1.0)
        #
        # R_ijB
        #
        # (1) P(ij) rimB x1jm
        #
        b_3.contract("abc,db->adc", x1im, **to_s_3)
        #
        # (8) P(ij) x4bd rijD
        #
        b_3.contract("abc,dc->abd", x4bd, factor=0.5, **to_s_3)
        #
        # (9) P(ij) 0.25 <ij||kl> rklB
        #
        goooo.contract("abcd,cde->abe", b_3, factor=0.25, **to_s_3)
        goooo.contract("abcd,cde->bae", b_3, factor=-0.25, **to_s_3)
        #
        # (10) P(ij) (jdbl) rilD
        # -<jb|ld> rild
        govov.contract("abcd,ecd->eab", b_3, **to_s_3, factor=-1.0)
        # <jb|dl> rild cjb
        tmp = govvo.contract("abcd,edc->eab", b_3)
        tmp.contract("abc,bc->abc", cia, s_3)
        #
        # P(ij)
        #
        s_3.iadd_transpose((1, 0, 2), factor=-1.0)
        #
        # Assign to sigma vector using mask
        #
        sigma.assign(s_3.array[self.get_mask(0)])
        return sigma

    @timer.with_section("IPpCCD3: H_eff")
    def set_hamiltonian(self, mo1: DenseTwoIndex, mo2: DenseFourIndex) -> None:
        """Derive all auxiliary matrices. Like
        fock_pq/f:     mo1_pq + sum_m(2<pm|qm> - <pm|mq>),

        **Arguments:**

        mo1, mo2
             one- and two-electron integrals.
        """
        cia = self.checkpoint["t_p"]
        nacto, nactv, nact = (
            self.occ_model.nacto[0],
            self.occ_model.nactv[0],
            self.occ_model.nact[0],
        )
        #
        # Get ranges
        #
        oooo = self.get_range("oooo")
        oovv = self.get_range("oovv")
        vvoo = self.get_range("vvoo")
        #
        # optimize contractions
        #
        opt = "td" if isinstance(mo2, CholeskyFourIndex) else None
        #
        # Inactive Fock matrix
        #
        fock = self.init_cache("fock", nact, nact)
        get_fock_matrix(fock, mo1, mo2, nacto)
        #
        # x1im
        #
        x1im = self.init_cache("x1im", nacto, nacto)
        # -fim
        x1im.iadd(fock, -1.0, end2=nacto, end3=nacto)
        # -<im|ee> cie
        mo2.contract("abcc,ac->ab", cia, x1im, factor=-1.0, **oovv, select=opt)
        #
        # x4bd
        #
        x4bd = self.init_cache("x4bd", nactv, nactv)
        # fbd
        x4bd.iadd(fock, 1.0, begin2=nacto, begin3=nacto)
        # -<bd|kk> ckb
        mo2.contract("abcc,ca->ab", cia, x4bd, factor=-1.0, **vvoo, select=opt)
        #
        # goooo
        #
        goooo = self.init_cache("goooo", nacto, nacto, nacto, nacto)
        mo2.contract("abcd->abcd", out=goooo, **oooo)

        #
        # 4-Index slices of ERI
        #
        def alloc(arr, block):
            """Determines alloc keyword argument for init_cache method."""
            # We keep one whole CholeskyFourIndex to rule them all.
            # Non-redundant blocks are accessed as views.
            if isinstance(arr, CholeskyFourIndex):
                return (partial(arr.view, **self.get_range(block)),)
            # But we store only non-redundant blocks of DenseFourIndex
            return (partial(arr.copy, **self.get_range(block)),)

        #
        # Get blocks (for the systems we can treat with Dense, it does not
        # matter that we store both the vvoo and oovv blocks)
        #
        slices = ["ovvo", "ovov", "oovv"]
        for slice_ in slices:
            self.init_cache(f"g{slice_}", alloc=alloc(mo2, slice_))
        #
        # Clean up
        #
        mo1.__del__()
        mo2.__del__()
