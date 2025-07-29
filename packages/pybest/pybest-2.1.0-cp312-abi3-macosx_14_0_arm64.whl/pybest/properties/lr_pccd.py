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
# 03/2025: This file has been written by Somayeh Ahmadkhani (original version)
#
# Detailed changes:
# See CHANGELOG

"""Correlated wavefunction implementations

This module contains linear response pCCD

Indexing convention:
:i,j,k,..: occupied orbitals of principal configuration
:a,b,c,..: virtual orbitals of principal configuration
:p,q,r,..: general indices (occupied, virtual)

Abbreviations used (if not mentioned in doc-strings):
:g_pqrs: <pq|rs>

"""

from typing import Any

import numpy as np
from numpy.typing import NDArray

from pybest.exceptions import ArgumentError
from pybest.linalg import DenseTwoIndex, FourIndex, TwoIndex
from pybest.properties.lr_base import LRCC
from pybest.utility import unmask


class LRpCCD(LRCC):
    """Linear Response Transition Matrix for pair Coupled Cluster Doubles class"""

    acronym = "TM-LRpCCD"
    long_name = (
        "Transition Matrix for Linear Response pair Coupled Cluster Doubles"
    )
    reference = "pCCD"
    cluster_operator = "Tp"
    comment = ""

    @property
    def dimension(self) -> int:
        """The number of unknowns (total number of excited states incl. ground
        state) for pCCD. Variable used by the Davidson module.

        1 :        Ground state
        nacto * nactv :  Single excitation states
        nacto * nactv :  Pair excitation states
        """
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        return nacto * nactv + 1

    def unmask_args(self, *args: Any, **kwargs: Any) -> Any:
        """Extract all tensors/quantities from function arguments and keyword
        arguments. Arguments/kwargs may contain:

        - t_p (DenseTwoIndex): Pair CC doubles amplitudes.
        - l_p (DenseTwoIndex): Lagrange multipliers


        Returns:
        Any: The result from the `unmask_args` method of the base `PropertyBase` class.

        """
        l_p = unmask("l_p", *args, **kwargs)
        if l_p is None:
            raise ArgumentError("Cannot find lagrange multipliers (l_p).")
        self.checkpoint.update("l_p", l_p)

        t_p = unmask("t_p", *args, **kwargs)
        if t_p is None:
            raise ArgumentError("Cannot find amplitudes (t_p).")
        self.checkpoint.update("t_p", t_p)

        return LRCC.unmask_args(self, *args, **kwargs)

    def update_hamiltonian(self, mo1: TwoIndex, mo2: FourIndex) -> None:
        """Prepare effective Hamiltonian elements required for electronic structure calculations,
        including two-electron integral intermediates in the molecular orbital (MO) basis.

        Args:
        - `mo1`: A `TwoIndex` instance holding one-electron integrals in the MO basis.
        - `mo2`: A `FourIndex` instance holding two-electron integrals in the MO basis.

        This method calculates or retrieves key intermediates used in constructing the Hamiltonian:
        - `gppqq`: Two-electron integral <pp|qq>, involving pair-pair interactions.
        - `gpqpq`: Two-electron integral <pq|pq>, involving cross-term interactions.

        If these intermediates are already available in the checkpoint, they are loaded from the
        checkpoint cache and reused. Otherwise, they are calculated using the provided two-electron
        integrals in the MO basis.


        **Cache and Checkpoint Operations:**
        - The checkpoint is first cleared of any previously stored `fock`, `gppqq`, or `gpqpq` data.
        - After calculation, results are stored in the cache to avoid redundant calculations in subsequent calls.

        Returns:
            None

        """
        # Get ranges
        nact = self.occ_model.nact[0]

        #
        # <pp|qq>
        #
        gppqq = self.init_cache("gppqq", nact, nact)
        mo2.contract("aabb->ab", gppqq)
        #
        # <pq|pq>
        #
        gpqpq = self.init_cache("gpqpq", nact, nact)
        mo2.contract("abab->ab", gpqpq)

    def eta_matrix(
        self, operator: tuple[DenseTwoIndex, DenseTwoIndex, DenseTwoIndex]
    ) -> TwoIndex:
        """Eta vector defined for linear response equation

        Args:
            operator (tuple): property dependent operator for calculating transition matrix

        Returns:
            TwoIndex: eta_ia
        """
        # get ranges
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]

        oo = self.get_range("oo")
        vv = self.get_range("vv")
        eta = self.lf.create_two_index(nacto, nactv)

        l_p = self.checkpoint["l_p"]

        #
        #      Coupling Pairs <P|P>
        #
        tmp = operator.contract("ab,ac->ac", l_p, factor=-2.0, **oo)
        operator.contract("ab,cb->cb", l_p, out=tmp, factor=2.0, **vv)
        eta.iadd(tmp)
        del tmp

        return eta

    #
    #   xi_{ia}(D,w) Matrix elements
    #
    def xi_matrix(
        self, operator: tuple[DenseTwoIndex, DenseTwoIndex, DenseTwoIndex]
    ) -> TwoIndex:
        """Xi_jb vector defined for linear response equation

        Args:
            operator (tuple): property dependent operator for calculating transition matrix

        Returns:
            TwoIndex: xi_n
        """
        # get ranges
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]

        oo = self.get_range("oo")
        vv = self.get_range("vv")

        t_p = self.checkpoint["t_p"]
        xi = self.lf.create_two_index(nacto, nactv)

        # tmp_ia = -2 A_ij t_ia +
        tmp = operator.contract("ab,ac->ac", t_p, factor=-2.0, **oo)
        # tmp_ib = 2 A_ba t_ia
        operator.contract("ab,cb->cb", t_p, out=tmp, factor=2.0, **vv)
        xi.iadd(tmp)

        return xi

    #
    #  F_{iajb} Matrix elements
    #
    def fmn_matrix(self) -> FourIndex:
        """F_iajb matrix defined for linear response transition matrix equation.

        Returns:
            FourIndex: f_mn
        """
        # get ranges
        ov = self.get_range("ov")

        # Integrals:
        l_p = self.checkpoint["l_p"]
        gppqq = self.from_cache("gppqq")

        f_iajb = self.lf.create_two_index(self.dimension)

        # 1)       l_ib <jj|aa>
        f_iajb_p = gppqq.contract("ab,cd->adcb", l_p, factor=1.0, **ov)

        # 2)       l_ja <ii|bb>
        gppqq.contract("ab,cd->cbad", l_p, f_iajb_p, factor=1.0, **ov)

        # 3)       -2 l_ib <ii|aa> d_{ij}
        tmp_iab = gppqq.contract("ab,ac->acb", l_p, factor=-2.0, **ov)

        # 4)       -2 l_ia <ii|bb> d_{ij}
        gppqq.contract("ab,ac->abc", l_p, tmp_iab, factor=-2.0, **ov)
        tmp_iab.expand("abc->abac", out=f_iajb_p)
        del tmp_iab

        # 5)       -2 l_ia <jj|aa> d_{ab}
        tmp_iaj = gppqq.contract("ab,cb->abc", l_p, factor=-2.0, **ov)

        # 6)       -2 l_ja <ii|aa> d_{ab}
        gppqq.contract("ab,cb->cba", l_p, tmp_iaj, factor=-2.0, **ov)
        tmp_iaj.expand("abc->abcb", out=f_iajb_p)
        del tmp_iaj

        # 7)       4 l_ia <ii|bb> d_{ij} d_{ab}
        tmp_ia = gppqq.contract("ab,ab->ab", l_p, factor=4.0, **ov)
        tmp_ia.expand("ab->abab", out=f_iajb_p)

        del tmp_ia

        f_iajb.assign(f_iajb_p.array, begin0=1, begin1=1)

        return f_iajb

    #
    # Transition Matrix element
    #
    def transition_matrix(
        self,
        threshold: float,
        index: int,
        operator_A: tuple[DenseTwoIndex, DenseTwoIndex, DenseTwoIndex],
        operator_B: tuple[DenseTwoIndex, DenseTwoIndex, DenseTwoIndex],
        e_vals: float,
        e_vecs: NDArray[np.float64],
    ) -> float:
        r"""Calculate the transition matrix using the LRpCCD class.

        The base linear response equation for obtaining the transition matrix for two arbitrary (A, B) operators is:

            Tran_Mat ~ {(η_k(A) + ∑_{mn} (F_mk xi_n(A) * (J_Iw)_{mn}^{-1})},

        where:

        - xi_a (TwoIndex):
            A matrix with dimensions (no, nv) that depends on a property-related operator.
            Function:
                xi_n(A) (n → {jb}) = ⟨jb| e^{T_p} D |cc⟩

        - f_iajb (DenseFourIndex):
            A matrix with dimensions (no, nv, no, nv).
            Function:
                F_{mn} (mn → {iajb}) = ⟨Λ| [[H, τ_{ia}], τ_{jb}] |cc⟩

        - eta_a (TwoIndex):
            A matrix with dimensions (no, nv) that depends on a property-related operator.
            During calculations, 'n' is converted to an eigenvector index.
            Function:
                η_k(A) (k → {ia}) = ⟨Λ| [A, τ_{ia}] |cc⟩

        - jacobian (FourIndex):
            A Jacobian matrix with dimensions (no, nv, no, nv).

        - ⟨Λ| :
            The de-excitation operator (not implemented here).
            Function:
                ⟨0| + ∑_{ld} l_d^l ⟨dl| e^{-T_p}

        - |cc⟩ :
            The coupled-cluster state (not implemented here).
            Function:
                e^{T_p} |0⟩

        - τ_{ia}:
            The excitation operator (not implemented here).
            Function:
                a† A† I i

        - operator_A/B (tuple [TwoIndex, TwoIndex, TwoIndex]):
            The x, y, and z components of property-related operators in a tuple.
            These are momentum integrals used for calculating dipole moments.
        """
        # calling created LR_functions
        eta = self.eta_matrix(operator_A)
        xi = self.xi_matrix(operator_A)
        f_iajb = self.fmn_matrix()
        jac_mat = self.jacobian()

        # defining new matrices for index mapping
        f_ia = self.lf.create_one_index(self.dimension)
        w_mat = self.lf.create_two_index(self.dimension)
        xi_1 = self.lf.create_one_index(self.dimension)
        eta_1 = self.lf.create_one_index(self.dimension)
        jac_inv = self.lf.create_two_index(self.dimension)

        # Mapping TwoIndex (i, j) with dimensions (nacto, nactv) to OneIndex (n = nacto * nactv)
        xi_1.assign(xi.ravel(), begin0=1)
        eta_1.assign(eta.ravel(), begin0=1)

        kc = np.where(abs(e_vecs) > threshold)[0]

        tm_element = 0
        for ind2 in kc:
            if ind2 != 0:
                # Two-electron excitations
                n_e = 2
                # Iw
                w_mat.assign_diagonal(e_vals)
                # (J-Iw)
                jac_mat.iadd(w_mat, factor=-1.0)
                # (J-Iw)^{-1} ->inverce
                jac_inv.array = np.linalg.inv(jac_mat.array)

                # sum_n xi_n (J-Iw)^{-1}_mn
                xi_Jac_nu = jac_inv.contract("ab,b->a", xi_1, factor=1.0)
                # f_nk
                f_ia.iadd(f_iajb.array[:, index].ravel())

                # tm = eta_k (1) +\sum_{mn} (f_nk Xi_m()j-Iw)^{-1}_nm)(2)
                # (1): eta_k , (there is no ground state index in eta)
                tmp = np.linalg.norm(e_vecs) * eta_1.array[index]

                # (2): \sum_m (f_mk * sum_n {xi_n (J-Iw)^{-1}_mn} )
                tmp += np.linalg.norm(e_vecs) * f_ia.contract("a,a", xi_Jac_nu)

                # second operator effect <k|B|0>
                if operator_B is not None:
                    tm_element += tmp * operator_B.array[index, 0] * n_e
                else:
                    tm_element += tmp * n_e

        return tm_element
