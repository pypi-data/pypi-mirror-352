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
"""Double Electron Affinity Equation of Motion Coupled Cluster implementations
   for a pCCD reference function

   Variables used in this module:
    :ncore:     number of frozen core orbitals
    :nocc:      number of occupied orbitals in the principle configuration
    :nacto:     number of active occupied orbitals in the principle configuration
    :nvirt:     number of virtual orbitals in the principle configuration
    :nactv:     number of active virtual orbitals in the principle configuration
    :nbasis:    total number of basis functions
    :nact:      total number of active orbitals (nacto+nactv)
    :e_ea:      the energy correction for DEA
    :civ_ea:    the CI amplitudes from a given EOM model
    :rab:       2 particle operator
    :rabck:     1 hole 3 particle operator (same spin)
    :rabCK:     1 hole 3 particle operator (opposite spin)

    Indexing convention:
     :i,j,k,..: occupied orbitals of principal configuration (alpha spin)
     :a,b,c,..: virtual orbitals of principal configuration (alpha spin)
     :p,q,r,..: general indices (occupied, virtual; alpha spin)
     :I,J,K,..: occupied orbitals of principal configuration (beta spin)
     :A,B,C,..: virtual orbitals of principal configuration (beta spin)
     :P,Q,R,..: general indices (occupied, virtual; beta spin)

    Abbreviations used (if not mentioned in doc-strings):
     :2p:    2 particles
     :3p:    3 particles
     :aa:    same-spin component (Alpha-Alpha)
     :ab:    opposite-spin component (Alpha-Beta)

This module has been written by:
2023: Katharina Boguslawski
"""

from functools import partial
from typing import Any

from pybest.auxmat import get_fock_matrix
from pybest.ea_eom.dea_base import RDEACC4
from pybest.linalg import (
    CholeskyFourIndex,
    DenseOneIndex,
    DenseTwoIndex,
    FourIndex,
)
from pybest.log import timer


class RDEApCCD4(RDEACC4):
    """
    Restricted Double Electron Affinity Equation of Motion Coupled Cluster
    class restricted to Double EA for a pCCD reference function and 4 unpaired
    electron (m_s = 2.0)

    This class defines only the function that are unique for the DEA-pCCD model
    with 4 unpaired electron:

        * dimension (number of degrees of freedom)
        * unmask_args (resolve T_p amplitudes)
        * set_hamiltonian (calculates effective Hamiltonian -- at most O(o2v2))
        * compute_h_diag (pre-conditioner used by Davidson)
        * build_subspace_hamiltonian (subspace to be diagonalized)
        * print functions (ci vector and weights)
    """

    long_name = "Double Electron Affinity Equation of Motion pair Coupled Cluster Doubles"
    acronym = "DEA-EOM-pCCD"
    reference = "pCCD"
    cluster_operator = "Tp"
    particle_hole_operator = "3p1h"
    order = "DEA"
    alpha = 4

    @timer.with_section("DEApCCD4: H_diag")
    def compute_h_diag(self, *args: Any) -> DenseOneIndex:
        """Used by davidson module for pre-conditioning"""
        h_diag = self.lf.create_one_index(self.dimension, "h_diag")
        #
        # Get auxiliary matrices
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        xkm = self.from_cache("xkm")
        xcd = self.from_cache("xcd")
        xckdm = self.from_cache("xckdm")
        gvvvv = self.from_cache("gvvvv")
        #
        # intermediates
        #
        xkk = xkm.copy_diagonal()
        xcc = xcd.copy_diagonal()
        l_ab = xcd.new()
        gvvvv.contract("abab->ab", l_ab)
        gvvvv.contract("abba->ab", l_ab, factor=-1.0)
        xckck = xckdm.contract("abab->ab", out=None)
        #
        # H_abcK,abcK
        #
        h_abcK = self.denself.create_four_index(nactv, nactv, nactv, nacto)
        #
        # 1/3 xkm(k,k)
        #
        xkk.expand("d->abcd", h_abcK, factor=1 / 3)
        #
        # xcd(c,c)
        #
        xcc.expand("c->abcd", h_abcK)
        #
        # 0.5 l_ab
        #
        l_ab.expand("ab->abcd", h_abcK, factor=0.5)
        #
        # xckck
        #
        xckck.expand("cd->abcd", h_abcK)
        #
        # Permutations
        #
        # create copy first
        tmp = h_abcK.copy()
        # Pca (abck)
        h_abcK.iadd_transpose((2, 1, 0, 3), other=tmp)
        # Pcb (abck)
        h_abcK.iadd_transpose((0, 2, 1, 3), other=tmp)
        del tmp
        #
        # assign using mask
        #
        h_diag.assign(h_abcK.array[self.get_mask(True)])
        return h_diag

    @timer.with_section("DEApCCD4: H_sub")
    def build_subspace_hamiltonian(
        self, b_vector: DenseOneIndex, h_diag: DenseOneIndex, *args: Any
    ) -> DenseOneIndex:
        """
        Used by Davidson module to construct subspace Hamiltonian

        **Arguments:**

        b_vector:
            (OneIndex object) contains current approximation to CI coefficients

        h_diag:
            Diagonal Hamiltonian elements required in Davidson module (not used
            here)

        args:
            Set of arguments passed by the Davidson module (not used here)
        """
        #
        # Get auxiliary matrices
        #
        nacto, nactv = self.occ_model.nacto[0], self.occ_model.nactv[0]
        xkm = self.from_cache("xkm")
        xcd = self.from_cache("xcd")
        xckdm = self.from_cache("xckdm")
        gvvvv = self.from_cache("gvvvv")
        #
        # Calculate sigma vector = (H.bvector)
        #
        # output
        sigma = self.denself.create_four_index(nactv, nactv, nactv, nacto)
        to_s = {"out": sigma, "clear": False}
        # input
        b_v = self.denself.create_four_index(nactv, nactv, nactv, nacto)
        # assign bvector
        b_v.assign(b_vector, ind=self.get_index_of_mask(True))
        # create tmp object to account for symmetry
        tmp = b_v.copy()
        b_v.iadd_transpose((1, 0, 2, 3), other=tmp, factor=-1.0)
        b_v.iadd_transpose((0, 2, 1, 3), other=tmp, factor=-1.0)
        b_v.iadd_transpose((2, 1, 0, 3), other=tmp, factor=-1.0)
        b_v.iadd_transpose((1, 2, 0, 3), other=tmp, factor=1.0)
        b_v.iadd_transpose((2, 0, 1, 3), other=tmp, factor=1.0)
        del tmp
        #
        # R_abcK
        #
        # (1) 1/3 rabcM x1km
        #
        b_v.contract("abcd,ed->abce", xkm, **to_s, factor=1 / 3)
        #
        # (2) rabdK xcd
        #
        b_v.contract("abcd,ec->abed", xcd, **to_s)
        #
        # (3) 0.5 <ab||de> rdecK
        #
        gvvvv.contract("abcd,cdef->abef", b_v, **to_s, factor=0.5)
        gvvvv.contract("abcd,dcef->abef", b_v, **to_s, factor=-0.5)
        #
        # (4) rabdM xckdm
        #
        b_v.contract("abcd,efcd->abef", xckdm, **to_s)
        #
        # Permutations
        #
        # - Pca (abcK)
        # create copy first
        tmp = sigma.copy()
        sigma.iadd_transpose((2, 1, 0, 3), other=tmp, factor=-1.0)
        # - Pcb (abcK)
        sigma.iadd_transpose((0, 2, 1, 3), other=tmp, factor=-1.0)
        del tmp
        #
        # Assign to sigma vector
        # overwrite bv vector (not needed anymore) to give as return value
        #
        del b_v
        b_v = self.lf.create_one_index(self.dimension)
        #
        # assign using mask
        #
        b_v.assign(sigma.array[self.get_mask(True)])

        return b_v

    @timer.with_section("DEApCCD4: H_eff")
    def set_hamiltonian(
        self,
        mo1: DenseTwoIndex,
        mo2: FourIndex,
    ) -> None:
        """Derive selected effective Hamiltonian elements. Like
        fock_pq:     one_pq + sum_m(2<pm|qm> - <pm|mq>),

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
        # get ranges
        #
        oovv = self.get_range("oovv")
        voov = self.get_range("voov")
        vovo = self.get_range("vovo")
        vvoo = self.get_range("vvoo")
        #
        # optimize contractions
        #
        opt = "td" if isinstance(mo2, CholeskyFourIndex) else "einsum"
        #
        # Inactive Fock matrix
        #
        fock = self.lf.create_two_index(nact, nact)
        get_fock_matrix(fock, mo1, mo2, nacto)
        #
        # xkm
        #
        xkm = self.init_cache("xkm", nacto, nacto)
        # -fkm
        xkm.iadd(fock, -1.0, end2=nacto, end3=nacto)
        # -<km|ee> cke
        mo2.contract("abcc,ac->ab", cia, xkm, factor=-1.0, **oovv, select=opt)
        #
        # xcd
        #
        xcd = self.init_cache("xcd", nactv, nactv)
        # fcd
        xcd.iadd(fock, 1.0, begin2=nacto, begin3=nacto)
        # -<cd|kk> ckc
        mo2.contract("abcc,ca->ab", cia, xcd, factor=-1.0, **vvoo, select=opt)
        #
        # xckdm
        #
        xckdm = self.init_cache("xckdm", nactv, nacto, nactv, nacto)
        # - <cm|dk> = - <ck|dm>
        mo2.contract("abcd->abcd", xckdm, factor=-1.0, **vovo)
        # <cd|mk> ckc = <ck|md> ckc
        mo2.contract("abcd,ba->abdc", cia, xckdm, **voov)

        #
        # 4-Index slices of ERI
        #
        def alloc(arr: FourIndex, block: str) -> tuple[partial[FourIndex]]:
            """Determines alloc keyword argument for init_cache method.
            arr: an instance of CholeskyFourIndex or DenseFourIndex
            block: (str) encoding which slices to consider using the get_range
                    method.
            """
            # Taken from CC module.
            # Non-redundant blocks are accessed as views.
            if isinstance(arr, CholeskyFourIndex):
                return (partial(arr.view, **self.get_range(block)),)
            # But we store only non-redundant blocks of DenseFourIndex
            return (partial(arr.copy, **self.get_range(block)),)

        #
        # Get blocks
        #
        slices = ["vvvv"]
        for slice_ in slices:
            self.init_cache(f"g{slice_}", alloc=alloc(mo2, slice_))
        #
        # Clean up
        #
        mo1.__del__()
        mo2.__del__()
