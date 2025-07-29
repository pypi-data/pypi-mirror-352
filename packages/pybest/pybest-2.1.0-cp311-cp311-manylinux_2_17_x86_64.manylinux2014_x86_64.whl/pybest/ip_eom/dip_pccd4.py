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

"""Double Ionization Potential Equation of Motion Coupled Cluster implementations
for a pCCD reference function and 4 unpaired electrons (S_z=2.0 components)

   Variables used in this module:
    :ncore:     number of frozen core orbitals
    :nocc:      number of occupied orbitals in the principal configuration
    :nacto:     number of active occupied orbitals in the principal configuration
    :nvirt:     number of virtual orbitals in the principal configuration
    :nactv:     number of active virtual orbitals in the principal configuration
    :nbasis:    total number of basis functions
    :nact:      total number of active orbitals (nacto+nactv)
    :e_dip:     the energy correction for IP
    :civ_dip:   the CI amplitudes from a given EOM model
    :rij:       2 holes operator
    :rijkc:     3 holes 1 particle operator (same spin)
    :rijKC:     3 holes 1 particle operator (opposite spin)
    :cia:       the pCCD pair amplitudes (T_p)
    :alpha:     number of unpaired electrons; for alpha=0, the spin-integrated
                equations target all possible m_s=0 states (singlet, triplet,
                quintet), for alpha=1, m_s=1/2 states are accessible (doublet,
                quartet), for alpha=2, m_s=1 states (triplet, quintet), for
                alpha=3, m_s=3/2 states (quartet), and for alpha=4, m_s=2 states
                (quintet)

   Indexing convention:
    :i,j,k,..: occupied orbitals of principal configuration
    :a,b,c,..: virtual orbitals of principal configuration
    :p,q,r,..: general indices (occupied, virtual)

Abbreviations used (if not mentioned in doc-strings; all ERI are in
physicists' notation):
 :<pq||rs>: <pq|rs>-<pq|sr>
 :2h:    2 holes
 :3h:    3 holes
 :aa:    same-spin component
 :ab:    opposite-spin component
"""

from typing import Any

from pybest.auxmat import get_fock_matrix
from pybest.ip_eom.dip_base import RDIPCC4
from pybest.linalg import (
    CholeskyFourIndex,
    DenseFourIndex,
    DenseOneIndex,
    DenseTwoIndex,
)
from pybest.log import timer


class RDIPpCCD4(RDIPCC4):
    """
    Restricted Double Ionization Potential Equation of Motion Coupled Cluster
    class restricted to Double IP for a pCCD reference function and 4 unpaired
    electrons (S_z=2.0 components)

    This class defines only the function that are unique for the DIP-pCCD model
    with 4 unpaired electron:

        * set_hamiltonian (calculates effective Hamiltonian -- at most O(o2v2))
        * compute_h_diag (pre-conditioner used by Davidson)
        * build_subspace_hamiltonian (subspace to be diagonalized)
    """

    long_name = "Double Ionization Potential Equation of Motion pair Coupled Cluster Doubles"
    acronym = "DIP-EOM-pCCD"
    reference = "pCCD"
    order = "DIP"
    alpha = 4

    @timer.with_section("DIPpCCD4: H_diag")
    def compute_h_diag(self, *args: Any) -> DenseOneIndex:
        """Diagonal approximation to Hamiltonian for S_z=2.0 states"""
        h_diag = self.lf.create_one_index(self.dimension, label="h_diag")
        #
        # Get effective Hamiltonian terms
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        goooo = self.from_cache("goooo")
        x1im = self.from_cache("x1im")
        x1cd = self.from_cache("x1cd")
        #
        # Intermediates
        #
        x1ii = x1im.copy_diagonal()
        x1cc = x1cd.copy_diagonal()
        lij = x1im.new()
        goooo.contract("abab->ab", out=lij)
        goooo.contract("abba->ab", out=lij, factor=-1.0)
        x2kcmd = self.from_cache("x2kcmd")
        x2kckc = x2kcmd.contract("abab->ab", out=None)
        if self.dump_cache:
            self.cache.dump("x2kcmd")
        #
        # rijkC
        #
        h_ijkc = self.denself.create_four_index(nacto, nacto, nacto, nactv)
        #
        # x1im(k,k)
        #
        x1ii.expand("c->abcd", h_ijkc)
        #
        # 1/3 x1cd(c,c)
        #
        x1cc.expand("d->abcd", h_ijkc, factor=1 / 3)
        #
        # 0.5 lij
        #
        lij.expand("ab->abcd", h_ijkc, factor=0.5)
        #
        # x2kckc
        #
        x2kckc.expand("cd->abcd", h_ijkc)
        #
        # Permutations
        #
        # create copy first
        tmp = h_ijkc.copy()
        # Pki (ijkc)
        h_ijkc.iadd_transpose((2, 1, 0, 3), other=tmp)
        # Pkj (ijkc)
        h_ijkc.iadd_transpose((0, 2, 1, 3), other=tmp)
        del tmp
        #
        # Assign using mask
        #
        h_diag.assign(h_ijkc, ind1=self.get_mask(True))
        return h_diag

    @timer.with_section("DIPpCCD4: H_sub")
    def build_subspace_hamiltonian(
        self, b_vector: DenseOneIndex, h_diag: DenseOneIndex, *args: Any
    ) -> DenseOneIndex:
        """
        Used by the Davidson module to construct subspace Hamiltonian for S_z=2.0

        **Arguments:**

        b_vector:
            (OneIndex object) contains current approximation to CI coefficients

        h_diag:
            Diagonal Hamiltonian elements required in davidson module (not used
            here)

        args:
            Set of arguments passed by the davidson module (not used here)
        """
        #
        # Get effective Hamiltonian terms
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        x1im = self.from_cache("x1im")
        x1cd = self.from_cache("x1cd")
        goooo = self.from_cache("goooo")
        #
        # Calculate sigma vector = (H.b_vector)_ijkc
        #
        # output
        sigma = self.denself.create_four_index(nacto, nacto, nacto, nactv)
        to_s = {"out": sigma, "clear": False}
        # Input
        b_v = self.denself.create_four_index(nacto, nacto, nacto, nactv)
        #
        # reshape b_vector
        #
        b_v.clear()
        b_v.assign(b_vector, ind=self.get_index_of_mask(True))
        # create tmp object to account for symmetry
        tmp = b_v.copy()
        b_v.iadd_transpose((1, 0, 2, 3), other=tmp, factor=-1.0)
        b_v.iadd_transpose((0, 2, 1, 3), other=tmp, factor=-1.0)
        b_v.iadd_transpose((2, 1, 0, 3), other=tmp, factor=-1.0)
        b_v.iadd_transpose((1, 2, 0, 3), other=tmp, factor=1.0)
        b_v.iadd_transpose((2, 0, 1, 3), other=tmp, factor=1.0)
        del tmp
        # All terms with P(k/ij)
        # R_ijkC
        #
        # (1) 1/3 rijkD x1cd
        #
        b_v.contract("abcd,ed->abce", x1cd, **to_s, factor=1 / 3)
        #
        # (2) rmjkC x1im(i,m) = x1im(k,m) rijmC
        #
        b_v.contract("abcd,ec->abed", x1im, **to_s)
        #
        # (3) 0.5 <ij||mn> rmnkC
        #
        goooo.contract("abcd,cdef->abef", b_v, **to_s, factor=0.5)
        goooo.contract("abcd,dcef->abef", b_v, **to_s, factor=-0.5)
        #
        # (4) x2kcmd rijmD
        #
        x2kcmd = self.from_cache("x2kcmd")
        b_v.contract("abcd,efcd->abef", x2kcmd, **to_s)
        if self.dump_cache:
            self.cache.dump("x2kcmd")
        #
        # Permutations P(k/ij)
        #
        # - Pki (ijkc)
        # create copy first
        tmp = sigma.copy()
        sigma.iadd_transpose((2, 1, 0, 3), other=tmp, factor=-1.0)
        # - Pkj (ijkc)
        sigma.iadd_transpose((0, 2, 1, 3), other=tmp, factor=-1.0)
        del tmp
        #
        # Assign to sigma vector
        #
        # Overwrite bv vector (not needed anymore) to give as return value
        #
        del b_v
        b_v = self.lf.create_one_index(self.dimension)
        #
        # Assign using mask
        #
        b_v.assign(sigma, ind1=self.get_mask(True))

        return b_v

    @timer.with_section("DIPpCCD4: H_eff")
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
        ovov = self.get_range("ovov")
        ovvo = self.get_range("ovvo")
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
        # x1cd
        #
        x1cd = self.init_cache("x1cd", nactv, nactv)
        # fcd
        x1cd.iadd(fock, 1.0, begin2=nacto, begin3=nacto)
        # -<cd|kk> ckc
        mo2.contract("abcc,ca->ab", cia, x1cd, factor=-1.0, **vvoo, select=opt)
        #
        # goooo
        #
        goooo = self.init_cache("goooo", nacto, nacto, nacto, nacto)
        mo2.contract("abcd->abcd", goooo, **oooo)
        #
        # x2kcmd
        #
        x2kcmd = self.init_cache("x2kcmd", nacto, nactv, nacto, nactv)
        # <kc|dm> ckc
        mo2.contract("abcd,ab->abdc", cia, x2kcmd, **ovvo)
        # -<kd|mc>
        mo2.contract("abcd->abcd", x2kcmd, factor=-1.0, **ovov)
        if self.dump_cache:
            self.cache.dump("x2kcmd")
        #
        # Clean up
        #
        mo1.__del__()
        mo2.__del__()
