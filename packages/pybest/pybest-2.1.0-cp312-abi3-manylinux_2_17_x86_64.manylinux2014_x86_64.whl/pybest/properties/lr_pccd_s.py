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

This module contains linear response pCCD+S

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


class LRpCCDS(LRCC):
    """Linear Response Transition Matrix for pair Coupled Cluster Doubles + Singles class"""

    acronym = "TM-LRpCCDS"
    long_name = "Transition Matrix for Linear Response pair Coupled Cluster Doubles + Singles"
    reference = "pCCD"
    cluster_operator = "Tp"
    comment = ""

    @property
    def dimension(self) -> int:
        """The number of unknowns (total number of excited states incl. ground
        state) for each CC flavor. Variable used by the Davidson module.

        1 :        Ground state
        nacto * nactv :  Single excitation states
        nacto * nactv :  Pair excitation states
        """
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        return 2 * nacto * nactv + 1

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
        - The checkpoint is first cleared of any previously stored `fock` and blocks of `gpqrs` data.
        - After calculation, results are stored in the cache to avoid redundant calculations in subsequent calls.

        Returns:
            None

        """
        # Get ranges
        nact = self.occ_model.nact[0]
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]

        oovv = self.get_range("oovv")
        ovov = self.get_range("ovov")
        ovv3 = self.get_range("ovv", 3)
        ovo3 = self.get_range("ovo", 3)

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

        #
        # <pq||rq>+<pq|rq>
        #
        lpqrq = self.init_cache("lpqrq", nact, nact, nact)
        mo2.contract("abcb->abc", out=lpqrq, factor=2.0)
        #
        # <pq|rr>
        #
        gpqrr = self.init_cache("gpqrr", nact, nact, nact)
        mo2.contract("abcc->abc", out=gpqrr)
        #
        # add exchange part to lpqrq
        #
        lpqrq.iadd_transpose((0, 2, 1), other=gpqrr, factor=-1.0)
        #
        # <ij|ab>
        #
        goovv = self.init_cache("goovv", nacto, nacto, nactv, nactv)
        mo2.contract("abcd->abcd", goovv, **oovv)
        #
        # <ij|ab>
        #
        govov = self.init_cache("govov", nacto, nactv, nacto, nactv)
        mo2.contract("abcd->abcd", govov, **ovov)

        g_aib = self.init_cache("g_iab", nacto, nactv, nactv)
        # G_iab
        g_aib.iadd(gpqrr, 2.0, **ovv3)

        g_aij = self.init_cache("g_iaj", nacto, nactv, nacto)
        # G_iaj
        g_aij.iadd(gpqrr, -2.0, **ovo3)

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

        ov = self.get_range("ov")
        oo = self.get_range("oo")
        vv = self.get_range("vv")
        eta = self.lf.create_two_index(nacto, 2 * nactv)

        l_p = self.checkpoint["l_p"]
        t_p = self.checkpoint["t_p"]

        #
        #      Coupling Pairs <P|P>
        #
        tmp = operator.contract("ab,ac->ac", l_p, factor=-2.0, **oo)
        operator.contract("ab,cb->cb", l_p, out=tmp, factor=2.0, **vv)
        eta.iadd(tmp, end1=nactv)

        #
        #      Coupling Singles <S|S>  * 1/2
        #
        # 1/2(-2 sum_d (t_id l_id) d_ia -2 sum_l (t_la l_la ) d_ia - 2 d_ia)
        tmp_o = l_p.contract("ab,ab->a", t_p, factor=-1.0)
        tmp_v = l_p.contract("ab,ab->b", t_p, factor=-1.0)

        tmp = operator.contract("ab,a->ab", tmp_o, **ov)
        operator.contract("ab,b->ab", tmp_v, out=tmp, **ov)
        operator.contract("ab->ab", out=tmp, factor=-1.0, **ov)
        eta.iadd(tmp, begin1=nactv)
        tmp.__del__()

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

        ov = self.get_range("ov")
        oo = self.get_range("oo")
        vv = self.get_range("vv")

        t_p = self.checkpoint["t_p"]
        xi = self.lf.create_two_index(nacto, 2 * nactv)

        #
        #      Coupling Pairs <P|P>
        #
        # tmp_ia = -2 A_ij t_ia +
        tmp = operator.contract("ab,ac->ac", t_p, factor=-2.0, **oo)
        # tmp_ib = 2 A_ba t_ia
        operator.contract("ab,cb->cb", t_p, out=tmp, factor=2.0, **vv)
        xi.iadd(tmp, end1=nactv)

        #
        #      Coupling Singles <S|S>  * 1/2
        #
        # A_ia t_ia ->tmp_ia
        tmp = operator.contract("ab,ab->ab", t_p, factor=1.0, **ov)
        # Aia t_ib ->tmp_ib
        operator.contract("ab->ab", out=tmp, factor=1.0, **ov)
        xi.iadd(tmp, begin1=nactv)
        tmp.__del__()

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
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]
        ov = self.get_range("ov")
        oov = self.get_range("oov")
        ooo = self.get_range("ooo")
        vvv = self.get_range("vvv")
        vvo = self.get_range("vvo")
        ovv = self.get_range("ovv")
        voo = self.get_range("voo")
        shape = (nacto * nactv, nacto * nactv)

        end_s = nacto * nactv + 1

        # Integrals:
        l_p = self.checkpoint["l_p"]
        t_p = self.checkpoint["t_p"]
        fock = self.from_cache("fock")
        lpqrq = self.from_cache("lpqrq")
        gpqrr = self.from_cache("gpqrr")
        f_ia = fock.copy(**ov)
        gppqq = self.from_cache("gppqq")

        f_iajb_list = []
        f_iajb = self.lf.create_two_index(self.dimension)

        #
        #      Coupling Pairs <P|P>
        #
        # 1)       l_ib <jj|aa>
        f_iajb_p = gppqq.contract("ab,cd->adcb", l_p, factor=1.0, **ov)

        # 2)       l_ja <ii|bb>
        gppqq.contract("ab,cd->cbad", l_p, f_iajb_p, factor=1.0, **ov)

        # 3)       -2 l_ib <ii|aa> d_{ij}
        tmp_iab = gppqq.contract("ab,ac->acb", l_p, factor=-2.0, **ov)

        # 4)       -2 l_ia <ii|bb> d_{ij}
        gppqq.contract("ab,ac->abc", l_p, tmp_iab, factor=-2.0, **ov)
        tmp_iab.expand("abc->abac", out=f_iajb_p)
        tmp_iab.__del__()

        # 5)       -2 l_ia <jj|aa> d_{ab}
        tmp_iaj = gppqq.contract("ab,cb->abc", l_p, factor=-2.0, **ov)

        # 6)       -2 l_ja <ii|aa> d_{ab}
        gppqq.contract("ab,cb->cba", l_p, tmp_iaj, factor=-2.0, **ov)
        tmp_iaj.expand("abc->abcb", out=f_iajb_p)
        tmp_iaj.__del__()

        # 7)       4 l_ia <ii|bb> d_{ij} d_{ab}
        tmp_ia = gppqq.contract("ab,ab->ab", l_p, factor=4.0, **ov)
        tmp_ia.expand("ab->abab", f_iajb_p)

        f_iajb_list.append(f_iajb_p)
        tmp_ia.__del__()

        tmp = f_iajb_p.reshape(shape)
        f_iajb.iadd(tmp, begin0=end_s, begin1=end_s)
        tmp.__del__()

        #
        #      Coupling Singles <S|S>  * 1/2
        #
        goovv = self.from_cache("goovv")
        loovv = goovv.contract("abcd->bacd", factor=-1.0)
        goovv.contract("abcd->abcd", out=loovv, factor=2.0)

        # 2<ij|ab> -<ji|ab>
        f_iajb_s = loovv.contract("abcd->bdac")

        # sum_k l_kb t_kb (-4<ij|ab> + 2<ij|ba>)
        tmp_v = l_p.contract("ab,ab->b", t_p)
        loovv.contract("abcd,d->bdac", tmp_v, out=f_iajb_s, factor=-1.0)

        # sum_k l_ka t_ka (-4<ji|ba> + 2<ij|ba>)
        tmp_v = l_p.contract("ab,ab->b", t_p)
        loovv.contract("abcd,d->acbd", tmp_v, out=f_iajb_s, factor=1.0)

        # sum_c l_ic t_ic (-2<ij|ba> + 1<ji|ab>)
        tmp_o = l_p.contract("ab,ab->a", t_p)
        loovv.contract("abcd,a->bcad", tmp_o, out=f_iajb_s, factor=-1.0)

        # sum_c l_jc t_jc (-2<ij|ba> + <ji|ab>)
        tmp_o = l_p.contract("ab,ab->a", t_p)
        loovv.contract("abcd,b->bcad", tmp_o, out=f_iajb_s, factor=-1.0)

        # l_ib t_ib (2<ji|ba> - <ij|ba>)
        tmp_ov = l_p.contract("ab,ab->ab", t_p)
        loovv.contract("abcd,bc->acbd", tmp_ov, out=f_iajb_s)

        # l_ja t_ja (2 <ij|ba> - <ji|ab>)
        loovv.contract("abcd,bc->bcad", tmp_ov, factor=1.0, out=f_iajb_s)

        # sum_kc l_ka t_kc (2 <ji|cc> - <ij|cc>)
        lpqrr = self.from_cache("gpqrr")
        tmp_vv = l_p.contract("ab,ac->bc", t_p)
        tmp_ovo = lpqrr.contract("abc,dc->adb", tmp_vv, factor=1.0, **oov)

        # sum_k l_ka (2<ji|kk> - <ij|kk>)
        lpqrr.contract("abc,cd->bda", l_p, out=tmp_ovo, **ooo)
        tmp_ovo.expand("abc->abcb", out=f_iajb_s)

        # sum_kc l_jc t_kc (2<ba|kk> - 1<ji|ab>)
        tmp_oo = l_p.contract("ab,cb->ac", t_p, factor=1.0)
        tmp_ovv = lpqrr.contract("abc,dc->dba", tmp_oo, **vvo)

        # sum_c l_ic (2<ba|cc> - <ba|cc>)
        lpqrr.contract("abc,dc->dab", l_p, out=tmp_ovv, **vvv)
        tmp_ovv.expand("abc->abac", out=f_iajb_s)

        # l_ja ( 2 <ia|jb> - <ai|jb> )
        govov = self.from_cache("govov")
        gvoov = govov.contract("abcd->bacd")
        l_p.contract("ab,cbad->adcb", govov, f_iajb_s, factor=2.0)
        l_p.contract("ab,bcad->adcb", gvoov, f_iajb_s, factor=-1.0)

        f_iajb_list.append(f_iajb_s)
        tmp = f_iajb_s.reshape(shape)
        f_iajb.iadd(tmp, begin0=1, end0=end_s, begin1=1, end1=end_s)

        #
        #      Coupling Singles <S|P>
        #
        f_iajb_sp = self.dense_lf.create_four_index(nacto, nactv, nacto, nactv)
        # l_ia(2 <ji|ai> - <ij|ai>) d_ab
        # -1 (f_jb l_ib) d_ab
        tmp_ovo = lpqrq.contract("abc,bc->acb", l_p, factor=2.0, **oov)
        f_ia.contract("ab,cb->abc", l_p, out=tmp_ovo, factor=-2.0)
        tmp_ovo.expand("abc->abcb", out=f_iajb_sp)

        # l_ia (2 <ia|ba> - <ai|ba>) d_ij
        # -2 (f_ia l_ib) d_ij
        tmp_ovv = lpqrq.contract("abc,ab->acb", l_p, factor=-1.0, **ovv)
        f_ia.contract("ab,ac->abc", l_p, tmp_ovv, factor=-2.0)
        tmp_ovv.expand("abc->abac", out=f_iajb_sp)

        # l_ia (2 <ja|ba> - <ai|ba>)
        lpqrq.contract("abc,db->acdb", l_p, out=f_iajb_sp, factor=1.0, **ovv)
        # l_ia (2 <ji|bi> - <ij|bi>)
        lpqrq.contract("abc,bd->acbd", l_p, out=f_iajb_sp, factor=1.0, **oov)

        # l_ia (-2<jb|aa> + <bj|aa>)
        gpqrr.contract("abc,dc->abdc", l_p, out=f_iajb_sp, factor=-1.0, **ovv)

        # l_ja (2<bj|ii>-<jb|ii>)
        gpqrr.contract("abc,cd->bacd", l_p, out=f_iajb_sp, factor=1.0, **voo)

        f_iajb_list.append(f_iajb_sp)
        tmp = f_iajb_sp.reshape(shape)
        f_iajb.iadd(tmp, begin0=1, end0=end_s, begin1=end_s)

        #
        #      Coupling Singles <P|S>
        #
        #
        # f_iajb <p|s> elements
        #
        f_iajb_ps = self.dense_lf.create_four_index(nacto, nactv, nacto, nactv)

        # l_jb(2 <ij|bj> - <ji|jb>) d_ab
        # -2 (f_ib l_jb) d_ab
        tmp_ovo = lpqrq.contract("abc,bc->bca", l_p, factor=-1.0, **oov)
        f_ia.contract("ab,cb->cba", l_p, out=tmp_ovo, factor=-2.0)
        tmp_ovo.expand("abc->abcb", out=f_iajb_ps)

        # l_ib(-4 <ij|aj> +2 <ji|ja>)
        lpqrq.contract("abc,ad->bdac", l_p, f_iajb_ps, factor=-2.0, **oov)

        # l_ib (-2 <ib|ab> + <bj|ab>) d_ij
        # -2 (f_ia l_ib) d_ij
        tmp_ovv = lpqrq.contract("abc,ab->abc", l_p, factor=-1.0, **ovv)
        f_ia.contract("ab,ac->abc", l_p, tmp_ovv, factor=-2.0)
        tmp_ovv.expand("abc->abac", out=f_iajb_ps)

        # l_ib(-2 <ja|ba> +2 <aj|ba>)
        lpqrq.contract("abc,dc->acdb", l_p, f_iajb_ps, factor=1.0, **ovv)

        # l_ib (2<ai|jj>-<ia|jj>)
        gpqrr.contract("abc,bd->cdba", l_p, out=f_iajb_ps, factor=1.0, **voo)

        f_iajb_list.append(f_iajb_ps)
        tmp = f_iajb_ps.reshape(shape)
        f_iajb.iadd(tmp, begin0=end_s, begin1=1, end1=end_s)

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

        - xi (TwoIndex):
            A matrix with dimensions (no, nv) that depends on a property-related operator.
            Function:
                xi_n(A) (n → {jb}) = ⟨jb| e^{T_p} D |cc⟩

        - f_iajb (DenseFourIndex):
            A matrix with dimensions (no, nv, no, nv).
            Function:
                F_{mn} (mn → {iajb}) = ⟨Λ| [[H, τ_{ia}], τ_{jb}] |cc⟩

        - eta (TwoIndex):
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
        #
        # Get ranges
        #
        nacto = self.occ_model.nacto[0]
        nactv = self.occ_model.nactv[0]

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
                index_ = ind2 - 1
                pairs = index_ - nacto * nactv >= 0
                if pairs:
                    # Two-electron excitations
                    n_e = 2
                else:
                    # one-electron excitation
                    n_e = 1

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
