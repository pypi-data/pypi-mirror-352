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
# 03/2025:
# This file has been modified by Somayeh Ahmadkhani and Lena Szczuczko

"""Utility methods for Restricted Linearized Coupled Cluster

Variables used in this module:
 :nocc:       total number of occupied orbitals
 :nvirt:      total number of virtual orbitals
 :ncore:      number of frozen core orbitals in the principle configuration
 :nacto:      number of active occupied orbitals
 :nactv:      number of active virtual orbitals
 :energy:     the CCSD energy, dictionary containing different contributions
 :amplitudes: the CCSD amplitudes (dict), contains t_1
 :t_1:        the single-excitation amplitudes

 Indexing convention:
 :o:        matrix block corresponding to occupied orbitals of principle
            configuration
 :v:        matrix block corresponding to virtual orbitals of principle
            configuration

"""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

from pybest.linalg import (
    DenseEightIndex,
    DenseFourIndex,
    DenseSixIndex,
    DenseTwoIndex,
)
from pybest.linalg.base import NIndexObject
from pybest.utility import unmask

#
# Density Matrices LCCD
#


def compute_1dm_lccd(
    select: str,
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
) -> DenseTwoIndex:
    """Computes specific block of N-RDM.

    **Arguments:**

    select:
        (str) the block to be calculated

    dm_out:
        (NIndexObject) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kargs:
        Used to resolve t_p amplitudes
    """
    if select == "pp":
        return compute_1dm_lccd_pp(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    if select == "pq":
        return compute_1dm_lccd_pq(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    raise NotImplementedError


def compute_2dm_lccd(
    select: str,
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
) -> DenseFourIndex:
    """Computes specific block of N-RDM.

    **Arguments:**

    select:
        (str) the block to be calculated

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kargs:
        Used to resolve t_p amplitudes
    """
    if select == "pPPp":
        return compute_2dm_lccd_pPPp(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    if select == "pqqp":
        return compute_2dm_lccd_pqqp(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    if select == "pQQp":
        return compute_2dm_lccd_pQQp(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    if select in ["qQQp", "qQPq"]:
        return compute_2dm_lccd_qQQp(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    if select in ["pQPp", "qPPp"]:
        return compute_2dm_lccd_pQPp(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    if select == "qQPp":
        return compute_2dm_lccd_qQPp(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    if select == "pQPq":
        return compute_2dm_lccd_pQPq(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    raise NotImplementedError


def compute_3dm_lccd(
    select: str,
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
) -> DenseSixIndex:
    """Computes specific block of N-RDM.

    **Arguments:**

    select:
        (str) the block to be calculated

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kargs:
        Used to resolve t_p amplitudes
    """
    if select == "qPQQPp":
        return compute_3dm_lccd_qPQQPp(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    if select == "qpPPpq":
        return compute_3dm_lccd_qpPPpq(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    raise NotImplementedError


def compute_4dm_lccd(
    select: str,
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
) -> DenseEightIndex:
    """Computes specific block of N-RDM.

    **Arguments:**

    select:
        (str) the block to be calculated

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kargs:
        Used to resolve t_p amplitudes
    """
    if select == "pPqQQqPp":
        return compute_4dm_lccd_pPqQQqPp(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    raise NotImplementedError


def compute_1dm_lccd_pp(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kargs:
        Used to resolve t_p amplitudes
    """
    t_2 = amplitudes["t_2"]
    l_2 = l_amplitudes["l_2"]
    occ = t_2.nbasis
    #
    # Calculate occupied block
    #
    to_dm = {"out": dm_out, "end8": occ}
    #
    # g_ji = - 0.5 l_kcid t_kcjd delta_ij
    #
    t_2.contract("abcd,abcd->c", l_2, **to_dm, factor=-0.5)
    #
    # Calculate virtual block
    #
    to_dm = {"out": dm_out, "begin8": occ}
    #
    # g_ba = 0.5 l_kbmd t_kamd delta_ab
    #
    t_2.contract("abcd,abcd->b", l_2, **to_dm, factor=0.5)
    #
    # d_pi contribution (HF)
    #
    dm_out.iadd(1.0, end0=occ)
    #
    # Scale
    #
    dm_out.iscale(factor)


def compute_1dm_lccd_pq(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kargs:
        Used to resolve t_p amplitudes
    """
    t_2 = amplitudes["t_2"]
    l_2 = l_amplitudes["l_2"]
    occ = t_2.nbasis

    to_oo = {"out": dm_out, "end8": occ, "end9": occ}
    to_vv = {"out": dm_out, "begin8": occ, "begin9": occ}
    #
    # Calculate occupied block
    #
    # g_ji = - 0.5 l_kcid t_kcjd
    #
    t_2.contract("abcd,abed->ce", l_2, **to_oo, factor=-0.5)
    #
    # Calculate virtual block
    #
    # g_ba = 0.5 l_kbmd t_kamd
    #
    l_2.contract("abcd,aecd->be", t_2, **to_vv, factor=0.5)
    #
    # d_pq contribution (HF)
    #
    dm_out.iadd_diagonal(1.0, end0=occ)
    # scale
    dm_out.iscale(factor)


def compute_2dm_lccd_pPPp(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kargs:
        Used to resolve t_p amplitudes
    """
    t_2 = amplitudes["t_2"]
    l_2 = l_amplitudes["l_2"]
    occ = t_2.nbasis

    to_oo = {"out": dm_out, "end8": occ}
    to_vv = {"out": dm_out, "begin8": occ}
    #
    # Calculate occupied block
    #
    # G_jJIi = 0.5 l_icid t_jcjd delta_ij
    #
    t_2.contract("abac,abac->a", l_2, **to_oo, factor=0.5)
    #
    # Calculate virtual block
    #
    # G_bBAa = 0.5 l_kbmb t_kama delta_ab
    #
    t_2.contract("abcb,abcb->b", l_2, **to_vv, factor=0.5)
    #
    # Lower dimensional contributions
    #
    # ii + II = - l_kcid t_kcjd delta_ij
    t_2.contract("abcd,abcd->c", l_2, **to_oo, factor=-1.0)
    #
    # HF
    #
    dm_out.iadd(1.0, end0=occ)
    # scale
    dm_out.iscale(factor)


def compute_2dm_lccd_pqqp(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    t_2 = amplitudes["t_2"]
    l_2 = l_amplitudes["l_2"]
    occ = t_2.nbasis
    act = dm_out.nbasis

    to_oo = {"out": dm_out, "end8": occ, "end9": occ}
    to_vv = {"out": dm_out, "begin8": occ, "begin9": occ}
    to_vo = {"out": dm_out, "begin8": occ, "end9": occ}
    to_ov = {"out": dm_out, "end8": occ, "begin9": occ}

    f = 1.0 / 6.0
    # 1
    # G_ijji = G_jiij
    #
    # 1/6 l_icjd t_icjd
    t_2.contract("abcd,abcd->ca", l_2, **to_oo, factor=f)
    # - 1/6 l_idjc t_icjd
    t_2.contract("abcd,adcb->ca", l_2, **to_oo, factor=-f)
    # 2
    # G_jaaj = G_ajja
    #
    # - 1/2 l_jakc t_jakc
    t_2.contract("abcd,abcd->ab", l_2, **to_ov, factor=-0.5)
    # - 1/6 l_kajc t_kajc
    t_2.contract("abcd,abcd->cb", l_2, **to_ov, factor=-f)
    # 1/6 l_kcja t_kajc
    t_2.contract("abcd,adcb->cb", l_2, **to_ov, factor=f)
    # 2
    # G_ajja
    #
    # - 1/2 l_jakc t_jakc
    t_2.contract("abcd,abcd->ba", l_2, **to_vo, factor=-0.5)
    # - 1/6 l_jcka t_jcka
    t_2.contract("abcd,abcd->da", l_2, **to_vo, factor=-f)
    # 1/6 l_jakc t_jcka
    t_2.contract("abcd,adcb->da", l_2, **to_vo, factor=f)
    # 4
    # G_abba = G_baab
    #
    # 1/6 l_kamb t_kamb
    t_2.contract("abcd,abcd->db", l_2, **to_vv, factor=f)
    # - 1/6 l_kamb t_kbma
    t_2.contract("abcd,adcb->db", l_2, **to_vv, factor=-f)
    #
    # HF
    #
    dm_out.iadd(1.0, 1.0, end0=occ, end1=occ)
    #
    # lower RDM's
    #
    # 1 i/j (g_ii + g_jj)
    # - 0.5 l_kcid t_kcjd delta_ij
    tmp = t_2.contract("abcd,abcd->c", l_2, out=None, factor=-0.5)
    # add ii/jj to [o,o] block
    dm_out.iadd(tmp, 1.0, 0, occ, 0, occ)
    dm_out.iadd_t(tmp, 1.0, 0, occ, 0, occ)
    # 2 a/b (g_aa + g_bb)
    # 0.5 l_kbmd t_kamd delta_ab
    tmp = t_2.contract("abcd,abcd->b", l_2, out=None, factor=0.5)
    # add aa/bb to [o,v]/[v,o] block
    dm_out.iadd_t(tmp, 1.0, 0, occ, occ, act)
    dm_out.iadd(tmp, 1.0, occ, act, 0, occ)
    #
    # Scale
    #
    dm_out.iscale(factor)


def compute_2dm_lccd_pQQp(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kargs:
        Used to resolve t_p amplitudes
    """
    t_2 = amplitudes["t_2"]
    l_2 = l_amplitudes["l_2"]
    occ = t_2.nbasis
    act = dm_out.nbasis

    to_oo = {"out": dm_out, "end8": occ, "end9": occ}
    to_vv = {"out": dm_out, "begin8": occ, "begin9": occ}
    to_vo = {"out": dm_out, "begin8": occ, "end9": occ}
    to_ov = {"out": dm_out, "end8": occ, "begin9": occ}
    f = 1.0 / 6.0
    # 1
    # G_iJJi
    #
    # 1/6 ( 2 l_jdic t_jdic)
    t_2.contract("abcd,abcd->ca", l_2, **to_oo, factor=2 * f)
    # 1/6 ( l_jdic t_jcid)
    t_2.contract("abcd,adcb->ca", l_2, **to_oo, factor=f)
    # 2
    # G_jAAj = G_aJJa
    #
    # - 1/6 ( 2 l_kajc t_kajc )
    t_2.contract("abcd,abcd->cb", l_2, **to_ov, factor=-2 * f)
    # - 1/6 l_kcja t_kajc
    t_2.contract("abcd,adcb->cb", l_2, **to_ov, factor=-f)
    # 3
    # G_aJJa
    #
    # - 1/6 ( 2 l_jcka t_jcka )
    t_2.contract("abcd,abcd->da", l_2, **to_vo, factor=-2 * f)
    # - 1/6 l_jakc t_jcka
    t_2.contract("abcd,adcb->da", l_2, **to_vo, factor=-f)
    # 4
    # G_abba = G_baab
    #
    # 1/6 l_kamb t_kamb
    t_2.contract("abcd,abcd->db", l_2, **to_vv, factor=2 * f)
    # b
    t_2.contract("abcd,cbad->db", l_2, **to_vv, factor=f)
    #
    # HF
    #
    dm_out.iadd(1.0, 1.0, end0=occ, end1=occ)
    #
    # lower RDM's
    #
    # 1 i/j (g_ii + g_jj)
    # - 0.5 l_kcid t_kcjd delta_ij
    tmp = t_2.contract("abcd,abcd->c", l_2, out=None, factor=-0.5)
    # add ii/jj to [o,o] block
    dm_out.iadd(tmp, 1.0, 0, occ, 0, occ)
    dm_out.iadd_t(tmp, 1.0, 0, occ, 0, occ)
    # 2 a/b (g_aa + g_bb)
    # 0.5 l_kbmd t_kamd delta_ab
    tmp = t_2.contract("abcd,abcd->b", l_2, out=None, factor=0.5)
    # add aa/bb to [o,v]/[v,o] block
    dm_out.iadd_t(tmp, 1.0, 0, occ, occ, act)
    dm_out.iadd(tmp, 1.0, occ, act, 0, occ)
    #
    # scale
    #
    dm_out.iscale(factor)


def compute_2dm_lccd_qQQp(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    t_2 = amplitudes["t_2"]
    l_2 = l_amplitudes["l_2"]
    occ = t_2.nbasis

    to_oo = {"out": dm_out, "end8": occ, "end9": occ}
    to_vv = {"out": dm_out, "begin8": occ, "begin9": occ}
    # 1
    # G_bBBa
    #
    # 1/2 l_kbmb t_kamb
    t_2.contract("abcd,adcd->db", l_2, **to_vv, factor=0.5)
    # 2
    # G_jJJi
    #
    # 1/2 l_jcid t_jcjd
    t_2.contract("abac,abdc->ad", l_2, **to_oo, factor=0.5)
    #
    # HF
    # 1 g_ji
    # - 0.5 l_kcid t_kcjd
    t_2.contract("abcd,abed->ce", l_2, **to_oo, factor=-0.5)
    #
    # Scale
    #
    dm_out.iscale(factor)


def compute_2dm_lccd_pQPp(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kargs:
        Used to resolve t_p amplitudes
    """
    t_2 = amplitudes["t_2"]
    l_2 = l_amplitudes["l_2"]
    occ = t_2.nbasis

    to_oo = {"out": dm_out, "end8": occ, "end9": occ}
    to_vv = {"out": dm_out, "begin8": occ, "begin9": occ}
    # 1
    # G_jIIi
    #
    # 1/2 l_idic t_idjc
    t_2.contract("abcd,abad->ca", l_2, **to_oo, factor=0.5)
    # 2
    # G_bAAa
    #
    # 1/2 l_makb t_maka
    t_2.contract("abcb,abcd->db", l_2, **to_vv, factor=0.5)
    #
    # Lower RDM's
    # b g_ji
    # - 0.5 l_kcid t_kcjd
    t_2.contract("abcd,abed->ce", l_2, **to_oo, factor=-0.5)
    #
    # Scale
    #
    dm_out.iscale(factor)


def compute_2dm_lccd_pQPq(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kargs:
        Used to resolve t_p amplitudes
    """
    t_2 = amplitudes["t_2"]
    l_2 = l_amplitudes["l_2"]
    occ = t_2.nbasis

    to_oo = {"out": dm_out, "end8": occ, "end9": occ}
    to_vv = {"out": dm_out, "begin8": occ, "begin9": occ}
    to_vo = {"out": dm_out, "begin8": occ, "end9": occ}
    to_ov = {"out": dm_out, "end8": occ, "begin9": occ}
    f = 1.0 / 6.0
    # 1
    # G_aBAb
    #
    # 1/6 ( 2 l_kamb t_kbma )
    t_2.contract("abcd,adcb->db", l_2, **to_vv, factor=2.0 * f)
    # 1/6 l_kbma t_kbma
    t_2.contract("abcd,abcd->db", l_2, **to_vv, factor=f)
    # 2
    # G_iJIj
    #
    # 1/6 ( 2 l_idjc t_jdic )
    t_2.contract("abcd,cbad->ca", l_2, **to_oo, factor=2.0 * f)
    # 1/6 l_jdic t_jdic
    t_2.contract("abcd,abcd->ca", l_2, **to_oo, factor=f)
    # 3
    # G_jAJa = G_aJAj
    #
    # 1/2 l_jakc t_jakc
    t_2.contract("abcd,abcd->ab", l_2, **to_ov, factor=0.5)
    t_2.contract("abcd,abcd->ba", l_2, **to_vo, factor=0.5)
    # - 1/6 ( 2 l_jakc t_kajc )
    t_2.contract("abcd,cbad->cb", l_2, **to_ov, factor=-2.0 * f)
    t_2.contract("abcd,cbad->bc", l_2, **to_vo, factor=-2.0 * f)
    # - 1/6 l_kajc t_kajc
    t_2.contract("abcd,abcd->cb", l_2, **to_ov, factor=-f)
    t_2.contract("abcd,abcd->bc", l_2, **to_vo, factor=-f)
    #
    # Scale
    #
    dm_out.iscale(factor)


def compute_2dm_lccd_qQPp(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    t_2 = amplitudes["t_2"]
    l_2 = l_amplitudes["l_2"]
    occ = t_2.nbasis

    to_oo = {"out": dm_out, "end8": occ, "end9": occ}
    to_vv = {"out": dm_out, "begin8": occ, "begin9": occ}
    # 1
    # G_bBAa
    #
    # 1/2 l_kbmb t_kama
    t_2.contract("abcb,adcd->db", l_2, **to_vv, factor=0.5)
    # 2
    # G_jJIi
    #
    # 1/2 l_icid t_jcjd
    t_2.contract("abac,dbdc->ad", l_2, **to_oo, factor=0.5)
    # Scale
    dm_out.iscale(factor)


def compute_3dm_lccd_qPQQPp(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kargs:
        Used to resolve t_p amplitudes
    """
    t_2 = amplitudes["t_2"]
    l_2 = l_amplitudes["l_2"]
    occ = t_2.nbasis

    to_oo = {"out": dm_out, "end8": occ, "end9": occ}

    #
    # Lower RDM's
    # 3 G_jIIi -> G_jIJJIi
    # 0.5 l_icid t_jcid
    t_2.contract("abcd,cbcd->ac", l_2, **to_oo, factor=0.5)
    # 4 G_jJJi -> G_jIJJIi
    # 0.5 l_jcid t_jcjd
    t_2.contract("abac,abdc->ad", l_2, **to_oo, factor=0.5)
    # 5 g_ji -> G_jIJJIi
    # - 0.5 l_kcid t_kcjd
    t_2.contract("abcd,abed->ce", l_2, **to_oo, factor=-0.5)
    #
    # Scale
    #
    dm_out.iscale(factor)


def compute_3dm_lccd_qpPPpq(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kargs:
        Used to resolve t_p amplitudes
    """
    t_2 = amplitudes["t_2"]
    l_2 = l_amplitudes["l_2"]
    occ = t_2.nbasis
    act = dm_out.nbasis

    to_oo = {"out": dm_out, "end8": occ, "end9": occ}
    to_vo = {"out": dm_out, "begin8": occ, "end9": occ}
    to_ov = {"out": dm_out, "end8": occ, "begin9": occ}

    f = 1.0 / 6.0
    # 1
    # G_biIIib
    #
    # 1/2 l_ibic t_ibic
    t_2.contract("abac,abac->ba", l_2, **to_vo, factor=0.5)
    # 2
    # G_jaAAaj
    #
    # - 1/2 l_jaka t_jaka
    t_2.contract("abcb,abcb->ab", l_2, **to_ov, factor=-0.5)
    #
    # HF: d_qj d_pi
    #
    dm_out.iadd(1.0, 1.0, end0=occ, end1=occ)
    #
    # lower RDM's:
    # G_aAAa d_qj + G_ibbi d_PI + G_iBBi d_pi + g_bb d_pi d_PI + G_IjjI d_pi + G_ijji d_PI +
    # G_iIIi d_qj + g_jj d_pi d_PI + g_ii d_PI d_qj + g_II d_pi d_qj
    #
    # 1 G_ibbi -> G_biIIib
    # - 1/2 l_ibkc t_ibkc
    t_2.contract("abcd,abcd->ba", l_2, **to_vo, factor=-0.5)
    # - 1/6 l_ickb t_ickb
    t_2.contract("abcd,abcd->da", l_2, **to_vo, factor=-f)
    # 1/6 l_ibkc t_ickb
    t_2.contract("abcd,adcb->da", l_2, **to_vo, factor=f)
    #
    # 2 G_iBBi -> G_biIIib
    # - 1/6 ( 2 l_ickb t_ickb )
    t_2.contract("abcd,abcd->da", l_2, **to_vo, factor=-2 * f)
    # - 1/6 l_ibkc t_ickb
    t_2.contract("abcd,adcb->da", l_2, **to_vo, factor=-f)
    #
    # 3 g_bb -> G_biIIib
    # 0.5 l_kbmd t_kbmd
    tmp_bb = t_2.contract("abcd,abcd->b", l_2, out=None, factor=0.5)
    # add to [v,o] block
    dm_out.iadd(tmp_bb, 1.0, occ, act, 0, occ)
    #
    # 4 G_aAAa -> G_jaAAaj
    # 0.5 l_kama t_kama
    tmp_a = t_2.contract("abcb,abcb->b", l_2, out=None, factor=0.5, clear=True)
    # add to [o,v] block
    dm_out.iadd_t(tmp_a, 1.0, 0, occ, occ, act)
    #
    # 5 G_IjjI -> G_jiIIij
    # 1/6 ( 2 l_icjd t_icjd)
    t_2.contract("abcd,abcd->ca", l_2, **to_oo, factor=2 * f)
    # 1/6 ( l_icjd t_idjc)
    t_2.contract("abcd,adcb->ca", l_2, **to_oo, factor=f)
    #
    # 6 G_ijji -> G_jiIIij
    # 1/6 l_icjd t_icjd
    t_2.contract("abcd,abcd->ca", l_2, **to_oo, factor=f)
    # - 1/6 l_idjc t_icjd
    t_2.contract("abcd,adcb->ca", l_2, **to_oo, factor=-f)
    #
    # 7 G_iIIi -> G_jiIIij
    # 0.5 l_icid t_icid
    tmp_i = t_2.contract("abac,abac->a", l_2, out=None, factor=0.5)
    #
    # 9 g_ii + g_II -> G_jiIIij
    # 2 ( -0.5 l_kcid t_kcid )
    t_2.contract("abcd,abcd->c", l_2, tmp_i, factor=-1.0)
    # add to [o,o] block
    dm_out.iadd_t(tmp_i, 1.0, 0, occ, 0, occ)
    #
    # 8 g_jj -> G_jiIIij
    # -0.5 l_kcjd t_kcjd
    tmp_jj = t_2.contract("abcd,abcd->c", l_2, out=None, factor=-0.5)
    # add to [o,o] block
    dm_out.iadd(tmp_jj, 1.0, 0, occ, 0, occ)
    #
    # Scale
    #
    dm_out.iscale(factor)


def compute_4dm_lccd_pPqQQqPp(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    t_2 = amplitudes["t_2"]
    l_2 = l_amplitudes["l_2"]
    occ = t_2.nbasis
    act = dm_out.nbasis

    to_oo = {"out": dm_out, "end8": occ, "end9": occ}
    to_vo = {"out": dm_out, "begin8": occ, "end9": occ}
    to_ov = {"out": dm_out, "end8": occ, "begin9": occ}

    f = 1.0 / 6.0
    #
    # HF
    #
    dm_out.iadd(1.0, 1.0, end0=occ, end1=occ)
    #
    # lower RDM's:
    # G_aAJJAa d_qj + G_aAjjAa d_QJ + G_aAAa d_qj dQJ + G_bBBb d_pi d_PI +
    # G_ibBBbi d_IP + G_IbBBbI d_ip + G_iIjjIi + G_iIJJIi + G_ijJJji + G_IjJJjI +
    # G_iIIi d_jq + G_ijji dIP dQJ+ G_jJJj d_ip + G_IJJI d_ip d_qj  + G_IjjI d_ip d_QJ +
    # G_iJJi d_IP djq + g_ii d_ip d_qj + g_II d_ip d_qj + g_jj d_ip d_qj + g_JJ d_ip d_qj +
    # HF d_ip d_qj
    # 1
    # G_ibBBbi + G_IbBBbI -> G_iIbBBbIi
    # -0.5 l_ibkb t_ibkb -0.5 l_ibkb t_ibkb
    t_2.contract("abcb,abcb->ab", l_2, **to_ov, factor=-1.0)
    # G_bBBb d_pi d_PI -> G_bBiIIiBb
    # 0.5 l_kama t_kama
    tmp_a = t_2.contract("abcb,abcb->b", l_2, out=None, factor=0.5)
    # add to [o,v] block
    dm_out.iadd_t(tmp_a, 1.0, 0, occ, occ, act)
    # G_aAAa d_qj dQJ -> G_aAiIIiAa
    # 0.5 l_kama t_kama
    tmp_b = t_2.contract("abcb,abcb->b", l_2, out=None, factor=0.5)
    # add to [v,o] block
    dm_out.iadd(tmp_b, 1.0, occ, act, 0, occ)
    # G_aAJJAa -> G_aAjJJjAa
    # -0.5 l_jaka t_jaka
    t_2.contract("abcb,abcb->ba", l_2, **to_vo, factor=-0.5)
    # G_aAjjAa -> G_aAjJJjAa
    # -0.5 l_jaka t_jaka
    t_2.contract("abcb,abcb->ba", l_2, **to_vo, factor=-0.5)
    # 5 iIjjIi = 0
    # 6 iIJJIi = 0
    # 7 ijJJji = 0
    # 8 IjJJjI = 0
    # 11 G_jJJj -> G_iIjJJjIi
    # 0.5 l_jcjd t_jcjd
    tmp_i = t_2.contract("abac,abac->a", l_2, out=None, factor=0.5)
    # 14 g_jj + g_JJ -> G_iIjJJjIi
    # -0.5 l_kcid t_kcid -0.5 l_kcid t_kcid
    t_2.contract("abcd,abcd->c", l_2, tmp_i, factor=-1.0)
    dm_out.iadd_t(tmp_i, 1.0, 0, occ, 0, occ)
    # 10 G_ijji + G_IJJI
    # 2 (1/6 l_jdic t_jdic)
    t_2.contract("abcd,abcd->ca", l_2, **to_oo, factor=2 * f)
    # -2 (1/6 l_jcid t_jdic)
    t_2.contract("abcd,adcb->ca", l_2, **to_oo, factor=-2 * f)
    # 9 G_iIIi -> G_iIjJJjIi
    # 0.5 l_icid t_icid
    tmp_j = t_2.contract("abac,abac->a", l_2, out=None, factor=0.5)
    # 13 g_ii + g_II -> G_iIjJJjIi
    # -0.5 l_kcjd t_kcjd -0.5 l_kcjd t_kcjd
    t_2.contract("abcd,abcd->c", l_2, tmp_j, factor=-1.0)
    dm_out.iadd(tmp_j, 1.0, 0, occ, 0, occ)
    # 12 G_IjjI + iJJi
    # 2 * 1/6 ( 2 l_jdic t_jdic)
    t_2.contract("abcd,abcd->ca", l_2, **to_oo, factor=4 * f)
    # 2 * 1/6 ( l_jdic t_jcid)
    t_2.contract("abcd,adcb->ca", l_2, **to_oo, factor=2 * f)
    #
    # Scale
    #
    dm_out.iscale(factor)


#
# Density Matrices LCCSD
#


def compute_1dm_lccsd(
    select: str,
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
) -> DenseTwoIndex:
    """Computes specific block of N-RDM.

    **Arguments:**

    select:
        (str) the block to be calculated

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    #
    # Compute LCCD contribution
    #
    compute_1dm_lccd(
        select, dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
    )
    #
    # Compute missing terms
    #
    if select == "pp":
        return compute_1dm_lccsd_pp(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    if select == "pq":
        return compute_1dm_lccsd_pq(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    raise NotImplementedError


def compute_2dm_lccsd(
    select: str,
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    select:
        (str) the block to be calculated

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    #
    # Compute LCCD contribution
    #
    compute_2dm_lccd(
        select, dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
    )
    #
    # Compute missing terms
    #
    if select == "pPPp":
        compute_2dm_lccsd_pPPp(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    elif select == "pqqp":
        compute_2dm_lccsd_pqqp(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    elif select == "pQQp":
        compute_2dm_lccsd_pQQp(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    elif select == "pQPq":
        compute_2dm_lccsd_pQPq(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    elif select in ["qQQp", "qQPq"]:
        compute_2dm_lccsd_qQQp(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    elif select in ["pQPp", "qPPp"]:
        compute_2dm_lccsd_pQPp(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )


def compute_3dm_lccsd(
    select: str,
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
) -> DenseSixIndex:
    """Computes specific block of N-RDM.

    **Arguments:**

    select:
        (str) the block to be calculated

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    #
    # Compute LCCD contribution
    #
    compute_3dm_lccd(
        select, dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
    )
    #
    # Compute missing terms
    #
    if select == "qPQQPp":
        return compute_3dm_lccsd_qPQQPp(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    if select == "qpPPpq":
        return compute_3dm_lccsd_qpPPpq(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    raise NotImplementedError


def compute_4dm_lccsd(
    select: str,
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
) -> DenseEightIndex:
    """Computes specific block of N-RDM.

    **Arguments:**

    select:
        (str) the block to be calculated

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    #
    # Compute LCCD contribution
    #
    compute_4dm_lccd(
        select, dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
    )
    #
    # Compute missing terms
    #
    if select == "pPqQQqPp":
        return compute_4dm_lccsd_pPqQQqPp(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    raise NotImplementedError


def compute_1dm_lccsd_pp(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kargs:
        Used to resolve t_p amplitudes
    """
    t_1 = amplitudes["t_1"]
    l_1 = l_amplitudes["l_1"]
    occ = t_1.nbasis

    to_o = {"out": dm_out, "end4": occ}
    to_v = {"out": dm_out, "begin4": occ}
    #
    # Calculate occupied block
    # rho(ji)
    # - 0.5 l_ic t_jc delta_ij
    t_1.contract("ab,ab->a", l_1, **to_o, factor=-0.5 * factor)
    #
    # Calculate virtual block
    # rho(ba)
    # 0.5 l_kb t_ka delta_ab
    t_1.contract("ab,ab->b", l_1, **to_v, factor=0.5 * factor)


def compute_1dm_lccsd_pq(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kargs:
        Used to resolve t_p amplitudes
    """
    t_1 = amplitudes["t_1"]
    t_2 = amplitudes["t_2"]
    l_1 = l_amplitudes["l_1"]
    l_2 = l_amplitudes["l_2"]
    occ = t_1.nbasis

    to_oo = {"out": dm_out, "end4": occ, "end5": occ}
    to_ov = {"out": dm_out, "end6": occ, "begin7": occ}
    to_vo = {"out": dm_out, "begin6": occ, "end7": occ}
    to_vv = {"out": dm_out, "begin4": occ, "begin5": occ}
    vo = {"begin0": occ, "end1": occ}
    ov = {"end0": occ, "begin1": occ}
    #
    # Calculate occupied block
    # rho(ij)
    # - 0.5 -t_ic l_jc
    t_1.contract("ab,cb->ac", l_1, **to_oo, factor=-0.5 * factor)
    #
    # Calculate virtual block
    # rho(ab)
    # 0.5 l_ka t_kb
    l_1.contract("ab,ac->bc", t_1, **to_vv, factor=0.5 * factor)
    #
    # rho(ai)
    # 0.5 l_ia
    dm_out.iadd_t(l_1, 0.5 * factor, **vo)
    # 0.5 l_iakc t_kc
    l_2.contract("abcd,cd->ba", t_1, **to_vo, factor=0.5 * factor)
    #
    # rho(ia)
    # tia
    dm_out.iadd(t_1, factor, **ov)
    # t_iakc l_kc
    t_2.contract("abcd,cd->ab", l_1, **to_ov, factor=1.0 * factor)
    # - 0.5 t_kaic l_kc
    t_2.contract("abcd,ad->cb", l_1, **to_ov, factor=-0.5 * factor)


def compute_2dm_lccsd_pPPp(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kargs:
        Used to resolve t_p amplitudes
    """
    t_1 = amplitudes["t_1"]
    l_1 = l_amplitudes["l_1"]
    occ = t_1.nbasis

    to_o = {"out": dm_out, "end4": occ}
    #
    # lower RDM's:
    # g_ii + g_II
    # 2 * ( - 0.5 l_ic t_ic)
    t_1.contract("ab,ab->a", l_1, **to_o, factor=-1.0 * factor)


def compute_2dm_lccsd_pqqp(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kargs:
        Used to resolve t_p amplitudes
    """
    t_1 = amplitudes["t_1"]
    l_1 = l_amplitudes["l_1"]
    occ = t_1.nbasis
    act = dm_out.nbasis

    to_ov = {"out": dm_out, "end4": occ, "begin5": occ}
    to_vo = {"out": dm_out, "begin4": occ, "end5": occ}
    # 2
    # G_jaaj
    # -0.5 l_ja t_ja
    t_1.contract("ab,ab->ab", l_1, **to_ov, factor=-0.5 * factor)
    # 3
    # G_ajja
    # -0.5 l_ja t_ja
    t_1.contract("ab,ab->ba", l_1, **to_vo, factor=-0.5 * factor)
    #
    # lower RDM's:
    # g_ii + g_jj + g_aa + g_bb
    # g_ii/g_jj -> G_ijji
    # -0.5 l_ic t_ic
    tmp = t_1.contract("ab,ab->a", l_1, out=None, factor=-0.5 * factor)
    # add ii/jj to [o,o] block
    dm_out.iadd(tmp, 1.0, 0, occ, 0, occ)
    dm_out.iadd_t(tmp, 1.0, 0, occ, 0, occ)
    # g_aa/g_bb -> G_ajja/G_ibbi
    # 0.5 l_ka t_ka
    tmp = t_1.contract("ab,ab->b", l_1, out=None, factor=0.5 * factor)
    # add aa/bb to [o,v]/[v,o] block
    dm_out.iadd_t(tmp, 1.0, 0, occ, occ, act)
    dm_out.iadd(tmp, 1.0, occ, act, 0, occ)


def compute_2dm_lccsd_pQQp(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    t_1 = amplitudes["t_1"]
    l_1 = l_amplitudes["l_1"]
    occ = t_1.nbasis
    act = dm_out.nbasis
    #
    # lower RDM's:
    # g_ii/g_jj
    # - 0.5 -t_ic l_ic
    tmp = t_1.contract("ab,ab->a", l_1, out=None, factor=-0.5 * factor)
    # add ii/jj to [o,o] block
    dm_out.iadd(tmp, 1.0, 0, occ, 0, occ)
    dm_out.iadd_t(tmp, 1.0, 0, occ, 0, occ)
    # g_aa/g_bb
    # 0.5 l_ka t_ka
    tmp = t_1.contract("ab,ab->b", l_1, out=None, factor=0.5 * factor)
    # add aa/bb to [o,v]/[v,o] block
    dm_out.iadd_t(tmp, 1.0, 0, occ, occ, act)
    dm_out.iadd(tmp, 1.0, occ, act, 0, occ)


def compute_2dm_lccsd_pQPq(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    t_1 = amplitudes["t_1"]
    l_1 = l_amplitudes["l_1"]
    occ = t_1.nbasis
    act = dm_out.nbasis

    tmp_ov = t_1.new()
    # 3
    # G_jAJa = G_aJAj
    #
    # 1/2 l_ja t_ja
    tmp_ov.iadd_mult(t_1, l_1, 0.5 * factor)
    # Add to [o,v] and [v,o] blocks
    dm_out.iadd_t(tmp_ov, 1.0, occ, act, 0, occ)
    dm_out.iadd(tmp_ov, 1.0, 0, occ, occ, act)


def compute_2dm_lccsd_qQQp(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kargs:
        Used to resolve t_p amplitudes
    """
    t_1 = amplitudes["t_1"]
    t_2 = amplitudes["t_2"]
    l_1 = l_amplitudes["l_1"]
    l_2 = l_amplitudes["l_2"]
    occ = t_1.nbasis

    to_oo = {"out": dm_out, "end4": occ, "end5": occ}
    to_ov = {"out": dm_out, "end6": occ, "begin7": occ}
    to_vo = {"out": dm_out, "begin6": occ, "end7": occ}
    ov = {"end0": occ, "begin1": occ, "factor": factor}
    # 3
    # G_jJJa
    #
    # - 1/2 l_jc t_jajc
    t_2.contract("abac,ac->ab", l_1, **to_ov, factor=-0.5 * factor)
    # 4
    # G_aAAi
    #
    # 1/2 l_iaka t_ka
    l_2.contract("abcb,cb->ba", t_1, **to_vo, factor=0.5 * factor)
    #
    # lower RDM's:
    # g_ji + g_ja
    # 1 g_ji -> G_jJJi
    # - 1/2 l_ic t_jc
    t_1.contract("ab,cb->ac", l_1, **to_oo, factor=-0.5 * factor)
    # 2 g_ja -> G_jJJa
    # t_ja
    dm_out.iadd(t_1, **ov)
    # t_iakc l_kc
    t_2.contract("abcd,cd->ab", l_1, **to_ov, factor=1.0 * factor)
    # - 0.5 t_kaic l_kc
    t_2.contract("abcd,ad->cb", l_1, **to_ov, factor=-0.5 * factor)


def compute_2dm_lccsd_pQPp(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    t_1 = amplitudes["t_1"]
    t_2 = amplitudes["t_2"]
    l_1 = l_amplitudes["l_1"]
    l_2 = l_amplitudes["l_2"]
    occ = t_1.nbasis
    act = dm_out.nbasis

    to_oo = {"out": dm_out, "end4": occ, "end5": occ}
    to_ov = {"out": dm_out, "end6": occ, "begin7": occ}
    to_vo = {"out": dm_out, "begin6": occ, "end7": occ}
    vo = {"begin0": occ, "end1": occ}
    tmp_vo = dm_out.copy(**vo)
    tmp_vo.clear()
    # 3
    # G_bIIi
    #
    # - 1/2 l_icib t_ic
    l_2.contract("abac,ab->ca", t_1, **to_vo, factor=-0.5 * factor)
    # 4
    # G_jAAa
    #
    # 1/2 l_jaka t_ka
    t_2.contract("abcb,cb->ab", l_1, **to_ov, factor=0.5 * factor)
    #
    # lower RDM's:
    # g_ji + g_bi
    # g_ji -> G_jIIi
    # - 0.5 l_ic t_jc
    t_1.contract("ab,cb->ac", l_1, **to_oo, factor=-0.5 * factor)
    # b
    # g_bi -> G_bIIi
    # 0.5 l_ib
    tmp_vo.iadd_t(l_1, 0.5 * factor)
    dm_out.iadd(tmp_vo, 1.0, occ, act, 0, occ)
    # 0.5 l_ibkc t_kc
    l_2.contract("abcd,cd->ba", t_1, **to_vo, factor=0.5 * factor)


def compute_3dm_lccsd_qpPPpq(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    t_1 = amplitudes["t_1"]
    l_1 = l_amplitudes["l_1"]
    occ = t_1.nbasis
    act = dm_out.nbasis

    to_vo = {"out": dm_out, "begin4": occ, "end5": occ}
    #
    # lower RDM's:
    # 1 G_biib d_ip
    # - 0.5 l_ib t_ib
    t_1.contract("ab,ab->ba", l_1, **to_vo, factor=-0.5)
    # 3 g_bb -> G_biIIib
    # 0.5 l_kb t_kb
    tmp = t_1.contract("ab,ab->b", l_1, out=None, factor=0.5)
    # add to [v,o] block
    dm_out.iadd(tmp, factor, occ, act, 0, occ)
    # 8 g_jj -> G_jiIIij
    # - 0.5 l_jc t_jc
    tmp = t_1.contract("ab,ab->a", l_1, out=None, factor=-0.5)
    dm_out.iadd(tmp, factor, 0, occ, 0, occ)
    # 9 g_ii + g_II -> G_jiIIij
    # 2 * ( - 0.5 l_ic t_ic )
    tmp = t_1.contract("ab,ab->a", l_1, out=None, factor=-1.0)
    dm_out.iadd_t(tmp, factor, 0, occ, 0, occ)


def compute_3dm_lccsd_qPQQPp(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    t_1 = amplitudes["t_1"]
    t_2 = amplitudes["t_2"]
    l_1 = l_amplitudes["l_1"]
    l_2 = l_amplitudes["l_2"]
    occ = t_1.nbasis

    to_oo = {"out": dm_out, "end4": occ, "end5": occ}
    to_ov = {"out": dm_out, "end6": occ, "begin7": occ}
    to_vo = {"out": dm_out, "begin6": occ, "end7": occ}
    #
    # lower RDM's:
    # 1 bBBi
    l_2.contract("abcb,cb->ba", t_1, **to_vo, factor=0.5 * factor)
    # 2 G_jAAa -> G_jAJJAa
    # 0.5 l_ka t_jaka
    t_2.contract("abcb,cb->ab", l_1, **to_ov, factor=0.5 * factor)
    # 5 g_ji -> G_jIJJIi
    # - 0.5 l_ic t_jc
    t_1.contract("ab,cb->ac", l_1, **to_oo, factor=-0.5 * factor)


def compute_4dm_lccsd_pPqQQqPp(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    t_1 = amplitudes["t_1"]
    l_1 = l_amplitudes["l_1"]
    occ = t_1.nbasis
    # 13 g_ii + g_II -> G_iIjJJjIi
    # 2 * ( - 0.5 l_ic t_ic )
    tmp = t_1.contract("ab,ab->a", l_1, out=None, factor=-1.0)
    dm_out.iadd_t(tmp, factor, 0, occ, 0, occ)
    # 14 g_jj + g_JJ -> G_iIjJJjIi
    # 2 * ( - 0.5 l_jc t_jc )
    #   tmp = t_1.contract("ab,ab->a", l_1, out=None, factor=-1.0)
    dm_out.iadd(tmp, factor, 0, occ, 0, occ)


#
# Density Matrices pCCD-LCCD
#


def compute_1dm_pccdlccd(
    select: str,
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    select:
        (str) the block to be calculated

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    #
    # assign T_p to T_2
    #
    t_p = unmask("t_p", *args, **kwargs)
    set_seniority_0(amplitudes, t_p)
    #
    # Calculate LCCD RDM
    #
    compute_1dm_lccd(
        select, dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
    )
    #
    # remove T_p from T_2
    #
    set_seniority_0(amplitudes, 0.0)


def compute_2dm_pccdlccd(
    select: str,
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    select:
        (str) the block to be calculated

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    #
    # assign T_p to T_2
    #
    t_p = unmask("t_p", *args, **kwargs)
    set_seniority_0(amplitudes, t_p)
    #
    # Calculate LCCD RDM
    #
    compute_2dm_lccd(
        select, dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
    )
    #
    # Calcualte remaining terms
    #
    if select == "qQPp":
        compute_2dm_pccdlccd_qQPp(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    #
    # remove T_p from T_2
    #
    set_seniority_0(amplitudes, 0.0)


def compute_3dm_pccdlccd(
    select: str,
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    select:
        (str) the block to be calculated

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    #
    # assign T_p to T_2
    #
    t_p = unmask("t_p", *args, **kwargs)
    set_seniority_0(amplitudes, t_p)
    #
    # Calculate LCCD RDM
    #
    compute_3dm_lccd(
        select, dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
    )
    #
    # remove T_p from T_2
    #
    set_seniority_0(amplitudes, 0.0)


def compute_4dm_pccdlccd(
    select: str,
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    select:
        (str) the block to be calculated

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    #
    # assign T_p to T_2
    #
    t_p = unmask("t_p", *args, **kwargs)
    set_seniority_0(amplitudes, t_p)
    #
    # Calculate LCCD RDM
    #
    compute_4dm_lccd(
        select, dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
    )
    #
    # remove T_p from T_2
    #
    set_seniority_0(amplitudes, 0.0)


def compute_2dm_pccdlccd_qQPp(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    t_2 = amplitudes["t_2"]
    l_2 = l_amplitudes["l_2"]
    t_p = unmask("t_p", *args, **kwargs)
    occ = t_2.nbasis

    tmp_ov = t_p.new()
    # 3 G_jJAa
    # ( l_jakc t_jakc ) t_jaja -> tmp[j,a] t_jaja
    tmp = t_2.contract("abcd,abcd->ab", l_2, out=None)
    tmp_ov.iadd_mult(t_p, tmp, 1.0)
    # e G_jJAa
    # ( l_jcka t_jcka ) t_jaja -> tmp[j,a] t_jaja
    tmp = t_2.contract("abcd,abcd->ad", l_2, out=None)
    tmp_ov.iadd_mult(t_p, tmp, 1.0)
    # f G_jJAa
    # - ( l_jdkc t_jdkc ) t_jaja -> - tmp[j] t_jaja
    tmp = t_2.contract("abcd,abcd->a", l_2, out=None)
    tmp_1 = t_p.contract("ab,a->ab", tmp, out=None, factor=-1.0)
    tmp_ov.iadd(tmp_1)
    # g G_jJAa
    # - ( l_jckc t_jcjc ) t_jaka -> - tmp[j,k] t_jaka
    tmp = l_2.contract("abcb,ab->ac", t_p, out=None)
    t_2.contract("abcb,ac->ab", tmp, tmp_ov, factor=-1.0)
    # h G_jJAa
    # - ( l_makc t_makc ) t_jaja -> - tmp[a] t_jaja
    tmp = t_2.contract("abcd,abcd->b", l_2, out=None)
    tmp_1 = t_p.contract("ab,b->ab", tmp, out=None, factor=-1.0)
    tmp_ov.iadd(tmp_1)
    # i G_jJAa
    # - ( l_kakd t_kaka ) t_jajd -> - tmp[a,d] t_jajd
    tmp = l_2.contract("abac,ab->bc", t_p, out=None)
    t_2.contract("abac,bc->ab", tmp, tmp_ov, factor=-1.0)
    # j G_jJAa
    # 0.5 ( l_kcmc t_kama ) t_jcjc -> 0.5 tmp[a,c] t_jcjc
    tmp = t_2.contract("abcb,adcd->bd", l_2, out=None)
    tmp.contract("ab,cb->ca", t_p, tmp_ov, factor=0.5)
    # k G_jJAa
    # 0.5 ( l_kckd t_jcjd ) t_kckc -> 0.5 tmp[j,k] t_kaka
    tmp = t_2.contract("abac,dbdc->ad", l_2, out=None, factor=1.0)
    tmp.contract("ab,bc->ac", t_p, tmp_ov, factor=0.5)
    #
    # Combine all blocks and scale
    #
    options = {"factor": factor, "end0": occ, "begin1": occ}
    dm_out.iadd(tmp_ov, **options)


#
# Density Matrices pCCD-LCCSD
#


def compute_1dm_pccdlccsd(
    select: str,
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    select:
        (str) the block to be calculated

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    #
    # assign T_p to T_2
    #
    t_p = unmask("t_p", *args, **kwargs)
    set_seniority_0(amplitudes, t_p)
    #
    # Calculate LCCSD RDM
    #
    compute_1dm_lccsd(
        select, dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
    )
    #
    # Calcualte remaining terms
    #
    if select == "pq":
        compute_1dm_pccdlccsd_pq(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    #
    # remove T_p from T_2
    #
    set_seniority_0(amplitudes, 0.0)


def compute_2dm_pccdlccsd(
    select: str,
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    select:
        (str) the block to be calculated

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kargs:
        Used to resolve t_p amplitudes
    """
    #
    # assign T_p to T_2
    #
    t_p = unmask("t_p", *args, **kwargs)
    set_seniority_0(amplitudes, t_p)
    #
    # Calculate LCCSD RDM
    #
    compute_2dm_lccsd(
        select, dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
    )
    #
    # Calcualte remaining terms
    #
    if select in ["qQQp", "qQPq"]:
        compute_2dm_pccdlccsd_qQQp(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    elif select in ["pQPp", "qPPp"]:
        compute_2dm_pccdlccsd_pQPp(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    elif select in ["qQPp"]:
        compute_2dm_pccdlccsd_qQPp(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    #
    # remove T_p from T_2
    #
    set_seniority_0(amplitudes, 0.0)


def compute_3dm_pccdlccsd(
    select: str,
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    select:
        (str) the block to be calculated

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    #
    # assign T_p to T_2
    #
    t_p = unmask("t_p", *args, **kwargs)
    set_seniority_0(amplitudes, t_p)
    #
    # Calculate LCCSD RDM
    #
    compute_3dm_lccsd(
        select, dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
    )
    #
    # Calculate remaining terms
    #
    if select in ["qPQQPp"]:
        compute_3dm_pccdlccsd_qPQQPp(
            dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
        )
    #
    # remove T_p from T_2
    #
    set_seniority_0(amplitudes, 0.0)


def compute_4dm_pccdlccsd(
    select: str,
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    select:
        (str) the block to be calculated

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    #
    # assign T_p to T_2
    #
    t_p = unmask("t_p", *args, **kwargs)
    set_seniority_0(amplitudes, t_p)
    #
    # Calculate LCCSD RDM
    #
    compute_4dm_lccsd(
        select, dm_out, l_amplitudes, amplitudes, factor, *args, **kwargs
    )
    #
    # remove T_p from T_2
    #
    set_seniority_0(amplitudes, 0.0)


def compute_1dm_pccdlccsd_pq(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    t_1 = amplitudes["t_1"]
    t_2 = amplitudes["t_2"]
    l_2 = l_amplitudes["l_2"]
    t_p = unmask("t_p", *args, **kwargs)
    occ = t_2.nbasis
    #
    # Temporary output
    #
    tmp_ov = t_p.new()
    # g_ia
    # - 0.5 l_ifmf t_ma t_ifif -> -0.5 tmp[i,a,f] t_ifif
    tmp = l_2.contract("abcb,ce->aeb", t_1, out=None)
    tmp.contract("abc,ac->ab", t_p, tmp_ov, factor=-0.5)
    # g_ia
    # - 0.5 l_nena t_ie t_nana -> -0.5 tmp[i,a,n] t_nana
    tmp = l_2.contract("abac,eb->eca", t_1, out=None)
    tmp.contract("abc,cb->ab", t_p, tmp_ov, factor=-0.5)
    # g_ia
    # 0.5 l_jame t_me t_jaja -> 0.5 tmp[j,a] t_jaja
    tmp = l_2.contract("abcd,cd->ab", t_1, out=None)
    tmp_ov.iadd_mult(t_p, tmp, 0.5)
    #
    # Combine all blocks and scale
    #
    options = {"factor": factor, "end0": occ, "begin1": occ}
    dm_out.iadd(tmp_ov, **options)


def compute_2dm_pccdlccsd_qQQp(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    t_1 = amplitudes["t_1"]
    t_2 = amplitudes["t_2"]
    l_2 = l_amplitudes["l_2"]
    t_p = unmask("t_p", *args, **kwargs)
    occ = t_2.nbasis
    #
    # Temporary output
    #
    tmp_ov = t_p.new()
    # G_jJJa
    # 0.5 l_jajc t_jc t_jaja -> 0.5 tmp[j,a] t_jaja
    tmp = l_2.contract("abac,ac->ab", t_1, out=None)
    tmp_ov.iadd_mult(tmp, t_p, 0.5)
    # G_jJJa
    # 0.5 l_jckc t_ka t_jcjc -> 0.5 tmp[j,c,a] t_jcjc
    tmp = l_2.contract("abcb,cd->abd", t_1, out=None)
    tmp.contract("abc,ab->ac", t_p, tmp_ov, factor=0.5)
    # G_jJJa
    # -0.5 l_kcja t_kc t_jaja -> -0.5 tmp[j,a] t_jaja
    tmp = l_2.contract("abcd,ab->cd", t_1, out=None)
    tmp_ov.iadd_mult(tmp, t_p, -0.5, False)
    #
    # lower RDM's:
    # g_ja -> G_jJJa
    # -0.5 l_ifmf t_ma t_ifif -> -0.5 tmp[i,a,f] t_ifif
    tmp = l_2.contract("abcb,ce->aeb", t_1, out=None)
    tmp.contract("abc,ac->ab", t_p, tmp_ov, factor=-0.5)
    # g_ja -> G_jJJa
    # -0.5 l_nena t_je t_nana -> -0.5 tmp[j,a,n] t_nana
    tmp = l_2.contract("abac,eb->eca", t_1, out=None)
    tmp.contract("abc,cb->ab", t_p, tmp_ov, factor=-0.5)
    # g_ja -> G_jJJa
    # 0.5 l_jakc t_kc t_jaja -> 0.5 tmp[j,a] t_jaja
    tmp = l_2.contract("abcd,cd->ab", t_1, out=None)
    tmp_ov.iadd_mult(tmp, t_p, 0.5)
    #
    # Combine all blocks and scale
    #
    options = {"factor": factor, "end0": occ, "begin1": occ}
    dm_out.iadd(tmp_ov, **options)


def compute_2dm_pccdlccsd_pQPp(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    t_1 = amplitudes["t_1"]
    t_2 = amplitudes["t_2"]
    l_2 = l_amplitudes["l_2"]
    t_p = unmask("t_p", *args, **kwargs)
    occ = t_2.nbasis
    #
    # Temporary output
    #
    tmp_ov = t_p.new()
    # G_jAAa
    # -0.5 l_nane t_je t_nana -> -0.5 tmp[n,a,j] t_nana
    tmp = l_2.contract("abac,dc->abd", t_1, out=None)
    tmp.contract("abc,ab->cb", t_p, tmp_ov, factor=-0.5)
    # G_jAAa
    # -0.5 l_jana t_na t_jaja -> -0.5 tmp[j,a] t_jaja
    tmp = l_2.contract("abcb,cb->ab", t_1, out=None)
    tmp_ov.iadd_mult(tmp, t_p, -0.5, False)
    # G_jAAa
    # 0.5 l_ncja t_nc t_jaja -> 0.5 tmp[j,a] t_jaja
    tmp = l_2.contract("abcd,ab->cd", t_1, out=None)
    tmp_ov.iadd_mult(tmp, t_p, 0.5, False)
    #
    # Combine all blocks and scale
    #
    options = {"factor": factor, "end0": occ, "begin1": occ}
    dm_out.iadd(tmp_ov, **options)


def compute_2dm_pccdlccsd_qQPp(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    t_1 = amplitudes["t_1"]
    t_2 = amplitudes["t_2"]
    l_1 = l_amplitudes["l_1"]
    l_2 = l_amplitudes["l_2"]
    t_p = unmask("t_p", *args, **kwargs)
    occ = t_2.nbasis
    #
    # Temporary output
    #
    tmp_ov = t_p.new()
    #
    # G_jJAa
    #
    # l_ja  t_ja t_jaja
    f_ac = t_p.copy()
    f_ac.imul(l_1)
    f_ac.imul(t_1)
    tmp_ov.iadd(f_ac, 1.0)
    # - l_jc t_jc t_jaja -> - tmp[j] t_jaja
    tmp = t_1.contract("ab,ab->a", l_1, out=None)
    tmp_1 = t_p.contract("ab,a->ab", tmp, factor=-1.0)
    tmp_ov.iadd(tmp_1)
    # - l_ka t_ka t_jaja -> - tmp[a] t_jaja
    tmp = t_1.contract("ab,ab->b", l_1, out=None)
    tmp_1 = t_p.contract("ab,b->ab", tmp, out=None, factor=-1.0)
    tmp_ov.iadd(tmp_1)
    # ( l_jakc t_jakc ) t_jaja -> tmp[j,a] t_jaja
    tmp = t_2.contract("abcd,abcd->ab", l_2, out=None)
    tmp_ov.iadd_mult(t_p, tmp, 1.0)
    # ( l_jcka t_jcka ) t_jaja -> tmp[j,a] t_jaja
    tmp = t_2.contract("abcd,abcd->ad", l_2, out=None)
    tmp_ov.iadd_mult(t_p, tmp, 1.0)
    # - ( l_jdkc t_jdkc ) t_jaja -> - tmp[j] t_jaja
    tmp = t_2.contract("abcd,abcd->a", l_2, out=None)
    tmp_1 = t_p.contract("ab,a->ab", tmp, out=None, factor=-1.0)
    tmp_ov.iadd(tmp_1)
    # - ( l_jckc t_jcjc ) t_jaka -> - tmp[j,k] t_jaka
    tmp = l_2.contract("abcb,ab->ac", t_p, out=None)
    t_2.contract("abcb,ac->ab", tmp, tmp_ov, factor=-1.0)
    # - ( l_makc t_makc ) t_jaja -> - tmp[a] t_jaja
    tmp = t_2.contract("abcd,abcd->b", l_2, out=None)
    tmp_1 = t_p.contract("ab,b->ab", tmp, out=None, factor=-1.0)
    tmp_ov.iadd(tmp_1)
    # - ( l_kakd t_kaka ) t_jajd -> - tmp[a,d] t_jajd
    tmp = l_2.contract("abac,ab->bc", t_p, out=None)
    t_2.contract("abac,bc->ab", tmp, tmp_ov, factor=-1.0)
    # 0.5 ( l_kcmc t_kama ) t_jcjc -> 0.5 tmp[a,c] t_jcjc
    tmp = t_2.contract("abcb,adcd->bd", l_2, out=None)
    tmp.contract("ab,cb->ca", t_p, tmp_ov, factor=0.5)
    # 0.5 ( l_kckd t_jcjd ) t_kckc -> 0.5 tmp[j,k] t_kaka
    tmp = t_2.contract("abac,dbdc->ad", l_2, out=None)
    tmp.contract("ab,bc->ac", t_p, tmp_ov, factor=0.5)
    #
    # Combine all blocks and scale
    #
    options = {"factor": factor, "end0": occ, "begin1": occ}
    dm_out.iadd(tmp_ov, **options)


def compute_3dm_pccdlccsd_qPQQPp(
    dm_out: NIndexObject,
    l_amplitudes: dict[str, Any],
    amplitudes: dict[str, Any],
    factor: int | float,
    *args: Any,
    **kwargs: dict[str, Any],
):
    """Computes specific block of N-RDM.

    **Arguments:**

    dm_out:
        (NIndex) the RDM stored in the cache

    l_amplitudes:
        (dict) Contains the Lambda amplitudes

    factor:
        (float, int) some scaling factor for RDM block

    amplitudes:
        (dict) Contains the CC amplitudes

    args, kwargs:
        Used to resolve t_p amplitudes
    """
    t_1 = amplitudes["t_1"]
    t_2 = amplitudes["t_2"]
    l_1 = l_amplitudes["l_1"]
    l_2 = l_amplitudes["l_2"]
    t_p = unmask("t_p", *args, **kwargs)
    occ = t_2.nbasis
    #
    # Temporary output
    #
    tmp_ov = t_p.new()
    #
    # G_jAJJAa
    #
    # -0.5 l_ja t_jaja
    tmp_ov.iadd_mult(l_1, t_p, -0.5)
    # 0.5 l_kaja t_ka t_jaja -> 0.5 tmp[j,a] t_jaja
    tmp = l_2.contract("abcb,ab->cb", t_1, out=None)
    tmp_ov.iadd_mult(tmp, t_p, 0.5)
    # 0.5 l_jajc t_jc t_jaja -> 0.5 tmp[j,a] t_jaja
    tmp = l_2.contract("abac,ac->ab", t_1, out=None)
    tmp_ov.iadd_mult(tmp, t_p, 0.5)
    # -0.5 l_jakc t_kc t_jaja -> -0.5 tmp[j,a] t_jaja
    tmp = l_2.contract("abcd,cd->ab", t_1, out=None)
    tmp_ov.iadd_mult(tmp, t_p, -0.5)
    #
    # lower RDM's:
    # 2 G_jAAa -> G_jAJJAa
    #
    # -0.5 l_nane t_je t_nana -> -0.5 tmp[n,a,j] t_nana
    tmp = l_2.contract("abac,dc->abd", t_1, out=None)
    tmp.contract("abc,ab->cb", t_p, tmp_ov, factor=-0.5)
    # -0.5 l_jama t_ma t_jaja -> -0.5 tmp[j,a] t_jaja
    tmp = l_2.contract("abcb,cb->ab", t_1, out=None)
    tmp_ov.iadd_mult(tmp, t_p, -0.5)
    # 0.5 l_kcja t_kc t_jaja -> 0.5 tmp[j,a] t_jaja
    tmp = l_2.contract("abcd,ab->cd", t_1, out=None)
    tmp_ov.iadd_mult(tmp, t_p, 0.5)
    #
    # Combine all blocks and scale
    #
    options = {"factor": factor, "end0": occ, "begin1": occ}
    dm_out.iadd(tmp_ov, **options)


#
# Utility function for pCCD-based Density Matrices
#


def set_seniority_0(
    amplitudes: dict[str, Any],
    value: float | NDArray[np.float64] | DenseFourIndex,
):
    """Overwrite seniority zero amplitudes of t_2 with some value.

    **Arguments:**

    amplitudes:
        (dict) containing t_2 amplitudes

    value:
        (float or array or FourIndex) used to substitute seniority zero amplitudes
    """
    t_2 = amplitudes["t_2"]
    occ = t_2.nbasis
    vir = t_2.nbasis1
    ind1, ind2 = np.indices((occ, vir))
    indices = [ind1, ind2, ind1, ind2]
    t_2.assign(value, indices)
