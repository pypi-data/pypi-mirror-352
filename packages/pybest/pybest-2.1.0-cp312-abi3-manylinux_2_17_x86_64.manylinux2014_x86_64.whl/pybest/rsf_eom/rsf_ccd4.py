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
# The RSF-CC sub-package has been originally written and updated by Aleksandra Leszczyk (see CHANGELOG)
# Its current version contains updates from the PyBEST developer team.
#
# 2023/24:
# This file has been written by Emil Sujkowski (original version)

from __future__ import annotations

from typing import Any

from pybest.cache import Cache
from pybest.linalg import (
    CholeskyFourIndex,
    DenseFourIndex,
    DenseOneIndex,
    DenseOrbital,
    DenseTwoIndex,
)
from pybest.linalg.cholesky import CholeskyLinalgFactory
from pybest.log import timer
from pybest.rsf_eom.eff_ham_ccd import EffectiveHamiltonianRCCD
from pybest.rsf_eom.ms2_base import RSFMS2Base


class RSFCCD4(RSFMS2Base):
    """
    Reversed spin flip coupled cluster doubles
    class restricted to reversed spin flip for a CCD reference function and 4 unpaired
    electrons (S_z=2 components)

    This class defines only the functions that are unique for the RSFCCD model
    with 4 unpaired electrons:

        * set_hamiltonian (calculates effective Hamiltonian)
        * compute_h_diag (pre-conditioner used by Davidson)
        * build_subspace_hamiltonian (subspace to be diagonalized)
    """

    long_name = "Reversed Spin Flip Coupled Cluster Doubles"
    acronym = "RSF-EOM-CCD"
    reference = "RCCD"

    alpha = 4  # Number of unpaired electrons

    def set_hamiltonian(
        self,
        ham_1_ao: DenseTwoIndex,
        ham_2_ao: DenseFourIndex | CholeskyFourIndex,
        mos: DenseOrbital,
    ) -> Cache:
        """Saves Hamiltonian terms in cache.

        Arguments:
        ham_1_ao : DenseTwoIndex
            Sum of one-body elements of the electronic Hamiltonian in AO
            basis, e.g., kinetic energy, nuclei--electron attraction energy

        ham_2_ao : DenseFourIndex
            Sum of two-body elements of the electronic Hamiltonian in AO
            basis, e.g., electron repulsion integrals.

        mos : DenseOrbital
            Molecular orbitals, e.g., RHF orbitals or pCCD orbitals.
        """
        cache = EffectiveHamiltonianRCCD(
            ham_1_ao, ham_2_ao, mos, self.rcc_iodata
        ).cache

        return cache

    @timer.with_section("Hdiag RSF-RCCD")
    def compute_h_diag(self, *args: Any) -> DenseOneIndex:
        """Used by Davidson module for pre-conditioning.

        **Arguments:**

        args:
            required for Davidson module (not used here)
        """
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]

        # Output objects
        h_diag_d = DenseFourIndex(nacto, nactv, nacto, nactv)

        # Get auxiliary matrices
        I_oo = self.cache.load("I_oo")
        I_VV = self.cache.load("I_VV")
        I_oooo = self.cache.load("I_oooo")
        I_VoVo = self.cache.load("I_VoVo")

        # I_oo
        H_ii = I_oo.copy_diagonal()
        H_ii.expand("a->abcd", h_diag_d)  # i -> iajb
        H_ii.expand("c->abcd", h_diag_d)
        # I_vv
        H_aa = I_VV.copy_diagonal()
        H_aa.expand("b->abcd", h_diag_d)
        H_aa.expand("d->abcd", h_diag_d)

        # I_oooo
        H_ij = I_oooo.contract("abab->ab")
        H_ij.expand("ac->abcd", h_diag_d)  # ij->iajb
        # I_VVVV
        self.compute_h_diag_term_abcd(h_diag_d)
        # I_VoVo
        H_ia = I_VoVo.contract("abab->ba")
        H_ia.expand("ab->abcd", h_diag_d)  # ia->iaxx
        H_ia.expand("ad->abcd", h_diag_d)  # ia->ixxa P_ab
        H_ia.expand("cb->abcd", h_diag_d)  # ia->xaix P_ij
        H_ia.expand("cd->abcd", h_diag_d)  # ia->xxia

        # Ravel
        out = self.ravel(h_diag_d)
        return out

    def compute_h_diag_term_abcd(self, h_diag_d: DenseFourIndex) -> None:
        """Compute h_diag term involving an vvvv block

        **Arguments:**

        :h_diag_d: (DenseFourIndex)
            the current value of the diagonal
        """
        if isinstance(self.lf, CholeskyLinalgFactory):
            e_vvvv = self.cache.load("e_vvvv")
            e_oovv = self.cache.load("e_oovv")
            t_2 = self.rcc_iodata.t_2

            # Additional factor of 0.5 is compensated by add_t operation
            # 1/2 * <ab||ab>
            tmp_ab = e_vvvv.contract("abab->ab", factor=0.25)

            e_vvvv.contract("abba->ab", out=tmp_ab, factor=-0.25)

            # 1/2 <km||ab> * t_km^ab
            e_oovv.contract("abcd,acbd->cd", t_2, out=tmp_ab, factor=0.25)
            e_oovv.contract("abcd,adbc->dc", t_2, out=tmp_ab, factor=-0.25)

            tmp_ab.iadd_t(tmp_ab, factor=1.0)
            tmp_ab.expand("bd->abcd", h_diag_d)

        else:
            I_VVVV = self.cache.load("I_VVVV")
            H_ab = I_VVVV.contract("abab->ab", factor=0.5)
            H_ab.iadd_t(H_ab, factor=1.0)
            H_ab.expand("bd->abcd", h_diag_d)  # ab->iajb

    def build_subspace_hamiltonian(
        self, bvector: DenseOneIndex, hdiag: DenseOneIndex, *args: Any
    ) -> DenseOneIndex:
        """Used by Davidson module to construct subspace Hamiltonian. Includes all
        terms that are similar for all RSF-EOM flavors.

        **Arguments:**

        bvector: OneIndex
            Contains current approximation to CI coefficients

        hdiag:
            Diagonal Hamiltonian elements required in Davidson module (not used
            here)

        args:
            Set of arguments passed by the Davidson module (not used here)

        **Returns**

        sigma: DenseOneIndex
        """
        # Get auxiliary matrices
        I_oo = self.cache.load("I_oo")
        I_VV = self.cache.load("I_VV")
        I_oooo = self.cache.load("I_oooo")
        I_VoVo = self.cache.load("I_VoVo")

        # Calculate sigma vector (H.bvector)_kc
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        sigma_d = DenseFourIndex(nacto, nactv, nacto, nactv)
        bvec_d = self.unravel(bvector)

        # Compute sigma vector
        # P(i,j) P(a,b) I_jbkc r_iakc
        tmp = I_VoVo.contract("bkcj,iakc->iajb", bvec_d)
        sigma_d.iadd(tmp)
        sigma_d.iadd_transpose((2, 3, 0, 1), other=tmp)
        sigma_d.iadd_transpose((0, 3, 2, 1), other=tmp, factor=-1)
        sigma_d.iadd_transpose((2, 1, 0, 3), other=tmp, factor=-1)

        # - P(i,j) r_iamb I_mj
        bvec_d.contract("iamb,mj->iajb", I_oo, out=sigma_d)
        bvec_d.contract("jamb,mi->iajb", I_oo, out=sigma_d, factor=-1)

        # P(a,b) r_iajc I_bc
        bvec_d.contract("iajc,bc->iajb", I_VV, out=sigma_d)
        bvec_d.contract("ibjc,ac->iajb", I_VV, out=sigma_d, factor=-1)
        # I_ijkm r_kamb
        I_oooo.contract("kmij,kamb->iajb", bvec_d, out=sigma_d)
        # I_abcd r_icjd
        self.get_effective_hamiltonian_term_abcd(bvec_d, sigma_d)

        # Flatten
        sigma = self.ravel(sigma_d)
        return sigma

    def get_effective_hamiltonian_term_abcd(
        self, bvec: DenseFourIndex, sigma: DenseFourIndex
    ) -> None:
        """Compute effective Hamiltonian term involving a vvvv block

        **Arguments:**

        :bvec: (DenseFourIndex)
                the current approximation to the CI doubles coefficient

        :sigma: (DenseFourIndex)
                the output sigma vector
        """
        if isinstance(self.lf, CholeskyLinalgFactory):
            e_vvvv = self.cache.load("e_vvvv")
            e_oovv = self.cache.load("e_oovv")
            t_2 = self.rcc_iodata.t_2

            # sigma is v^2 o^2 object
            new_sigma = sigma.new()

            # 1/2 * <ab||cd> * r_icjd
            e_vvvv.contract(
                "abcd,ecfd->eafb", bvec, out=new_sigma, factor=0.25
            )
            e_vvvv.contract(
                "abcd,edfc->eafb", bvec, out=new_sigma, factor=-0.25
            )

            # 1/2 <km||cd> * r_icjd * t_kamb
            tmp = e_oovv.contract("abcd,ecfd->eafb", bvec, factor=0.25)
            e_oovv.contract("abcd,edfc->eafb", bvec, out=tmp, factor=-0.25)
            tmp.contract("abcd,bedf->aecf", t_2, out=new_sigma)

            new_sigma.iadd_transpose((0, 3, 2, 1), factor=-1)
            sigma.iadd(new_sigma)
        else:
            I_VVVV = self.cache.load("I_VVVV")
            I_VVVV.contract("abcd,icjd->iajb", bvec, out=sigma, factor=0.5)
            I_VVVV.contract("abcd,icjd->ibja", bvec, out=sigma, factor=-0.5)


class RSFLCCD4(RSFCCD4):
    """
    Reversed spin flip linearized coupled cluster doubles
    class restricted to reversed spin flip for a LCCD reference function and 4 unpaired
    electrons (S_z=2 components)
    """

    long_name = "Reversed Spin Flip Linearized Coupled Cluster Doubles"
    acronym = "RSF-EOM-LCCD"
    reference = "RLCCD"

    alpha = 4  # Number of unpaired electrons


class RSFfpCCD4(RSFCCD4):
    """
    Reversed spin flip frozen pair coupled cluster doubles
    class restricted to reversed spin flip for a fpCCD reference function and 4 unpaired
    electrons (S_z=2 components)
    """

    long_name = "Reversed Spin Flip frozen pair Coupled Cluster Doubles"
    acronym = "RSF-EOM-fpCCD"
    reference = "RfpCCD"

    alpha = 4  # Number of unpaired electrons


class RSFfpLCCD4(RSFLCCD4):
    """
    Reversed Spin Flip frozen pair Linearized Coupled Cluster Doubles
    class restricted to reversed spin flip for a fpLCCD reference function and 4 unpaired
    electrons (S_z=2 components)
    """

    long_name = (
        "Reversed Spin Flip frozen pair Linearized Coupled Cluster Doubles"
    )
    acronym = "RSF-EOM-fpLCCD"
    reference = "RfpLCCD"

    alpha = 4  # Number of unpaired electrons
