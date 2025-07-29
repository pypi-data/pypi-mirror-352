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
# This implementation has been taken from `Horton 2.0.0`.
# However, this file has been updated and debugged. Compatibility with Horton is NOT
# guaranteed.
# Its current version contains updates from the PyBEST developer team.
#
# Detailed changes (see also CHANGELOG):
# 2020-07-01: Update to PyBEST standard, including naming convention and TCE
# 2020-07-01: Update to new python features, including f-strings, abc class

"""Base classes for energy terms and other observables of the wavefunction"""

import abc

from pybest.utility import doc_inherit

__all__ = [
    "Observable",
    "RDirectTerm",
    "RExchangeTerm",
    "RTwoIndexTerm",
    "UDirectTerm",
    "UExchangeTerm",
    "UTwoIndexTerm",
    "compute_dm_full",
]


def compute_dm_full(cache):
    """Add the spin-summed density matrix to the cache unless it is already present."""
    one_dm_scf_a = cache["one_dm_scf_a"]
    one_dm_scf_b = cache["one_dm_scf_b"]
    dm_full, new = cache.load("dm_full", alloc=one_dm_scf_a.new)
    if new:
        dm_full.assign(one_dm_scf_a)
        dm_full.iadd(one_dm_scf_b)
    return dm_full


class Observable(abc.ABC):
    def __init__(self, label):
        self.label = label

    @abc.abstractmethod
    def compute_energy(self, cache):
        """Compute the expectation value of the observable

        **Arguments:**

        cache
             A cache object used to store intermediate results that can be
             reused or inspected later.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add_fock(self, cache, *focks):
        """Add contributions to the Fock matrices.

        **Arguments:**

        cache
             A cache object used to store intermediate results that can be
             reused or inspected later.

        fock1, fock2, ...
             A list of output fock operators. The caller is responsible for
             setting these operators initially to zero (if desired).
        """
        raise NotImplementedError


class RTwoIndexTerm(Observable):
    """Class for all observables that are linear in the density matrix of a
    restricted wavefunction.
    """

    def __init__(self, op_alpha, label):
        self.op_alpha = op_alpha
        Observable.__init__(self, label)

    @doc_inherit(Observable)
    def compute_energy(self, cache):
        return 2 * self.op_alpha.contract("ab,ab", cache["one_dm_scf_a"])

    @doc_inherit(Observable)
    def add_fock(self, cache, fock_alpha):
        fock_alpha.iadd(self.op_alpha)


class UTwoIndexTerm(Observable):
    """Class for all observables that are linear in the density matrix of an
    unrestricted wavefunction.
    """

    def __init__(self, op_alpha, label, op_beta=None):
        self.op_alpha = op_alpha
        self.op_beta = op_alpha if op_beta is None else op_beta
        Observable.__init__(self, label)

    @doc_inherit(Observable)
    def compute_energy(self, cache):
        if self.op_alpha is self.op_beta:
            # when both operators are references to the same object, take a
            # shortcut
            compute_dm_full(cache)
            return self.op_alpha.contract("ab,ab", cache["dm_full"])
        else:
            # If the operator is different for different spins, do the normal
            # thing.
            return self.op_alpha.contract(
                "ab,ab", cache["one_dm_scf_a"]
            ) + self.op_beta.contract("ab,ab", cache["one_dm_scf_b"])

    @doc_inherit(Observable)
    def add_fock(self, cache, fock_alpha, fock_beta):
        fock_alpha.iadd(self.op_alpha)
        fock_beta.iadd(self.op_beta)


class RDirectTerm(Observable):
    def __init__(self, op_alpha, label):
        self.op_alpha = op_alpha
        Observable.__init__(self, label)

    def _update_direct(self, cache):
        """Recompute the direct operator if it has become invalid"""
        one_dm_scf_a = cache["one_dm_scf_a"]
        direct, new = cache.load(
            f"op_{self.label}_alpha", alloc=one_dm_scf_a.new
        )
        if new:
            self.op_alpha.contract(
                "abcd,bd->ac", one_dm_scf_a, direct, clear=True
            )
            direct.iscale(2)  # contribution from beta electrons is identical

    @doc_inherit(Observable)
    def compute_energy(self, cache):
        self._update_direct(cache)
        direct = cache.load(f"op_{self.label}_alpha")
        return direct.contract("ab,ab", cache["one_dm_scf_a"])

    @doc_inherit(Observable)
    def add_fock(self, cache, fock_alpha):
        self._update_direct(cache)
        direct = cache.load(f"op_{self.label}_alpha")
        fock_alpha.iadd(direct)


class UDirectTerm(Observable):
    def __init__(self, op_alpha, label, op_beta=None):
        self.op_alpha = op_alpha
        self.op_beta = op_alpha if op_beta is None else op_beta
        Observable.__init__(self, label)

    def _update_direct(self, cache):
        """Recompute the direct operator(s) if it/they has/have become invalid"""
        if self.op_alpha is self.op_beta:
            # This branch is nearly always going to be followed in practice.
            dm_full = compute_dm_full(cache)
            direct, new = cache.load(f"op_{self.label}", alloc=dm_full.new)
            if new:
                self.op_alpha.contract(
                    "abcd,bd->ac", dm_full, direct, clear=True
                )
        else:
            # This is probably never going to happen. In case it does, please
            # add the proper code here.
            raise NotImplementedError

    @doc_inherit(Observable)
    def compute_energy(self, cache):
        self._update_direct(cache)
        if self.op_alpha is self.op_beta:
            # This branch is nearly always going to be followed in practice.
            direct = cache[f"op_{self.label}"]
            dm_full = cache["dm_full"]
            return 0.5 * direct.contract("ab,ab", dm_full)
        else:
            # This is probably never going to happen. In case it does, please
            # add the proper code here.
            raise NotImplementedError

    @doc_inherit(Observable)
    def add_fock(self, cache, fock_alpha, fock_beta):
        self._update_direct(cache)
        if self.op_alpha is self.op_beta:
            # This branch is nearly always going to be followed in practice.
            direct = cache[f"op_{self.label}"]
            fock_alpha.iadd(direct)
            fock_beta.iadd(direct)
        else:
            # This is probably never going to happen. In case it does, please
            # add the proper code here.
            raise NotImplementedError


class RExchangeTerm(Observable):
    def __init__(self, op_alpha, label, fraction=1.0):
        self.op_alpha = op_alpha
        self.fraction = fraction
        Observable.__init__(self, label)

    def _update_exchange(self, cache):
        """Recompute the Exchange operator if invalid"""
        one_dm_scf_a = cache["one_dm_scf_a"]
        exchange_alpha, new = cache.load(
            f"op_{self.label}_alpha", alloc=one_dm_scf_a.new
        )
        if new:
            self.op_alpha.contract(
                "abcd,cb->ad", one_dm_scf_a, exchange_alpha, clear=True
            )

    @doc_inherit(Observable)
    def compute_energy(self, cache):
        self._update_exchange(cache)
        exchange_alpha = cache[f"op_{self.label}_alpha"]
        one_dm_scf_a = cache["one_dm_scf_a"]
        return -self.fraction * exchange_alpha.contract("ab,ab", one_dm_scf_a)

    @doc_inherit(Observable)
    def add_fock(self, cache, fock_alpha):
        self._update_exchange(cache)
        exchange_alpha = cache[f"op_{self.label}_alpha"]
        fock_alpha.iadd(exchange_alpha, -self.fraction)


class UExchangeTerm(Observable):
    def __init__(self, op_alpha, label, fraction=1.0, op_beta=None):
        self.op_alpha = op_alpha
        self.op_beta = op_alpha if op_beta is None else op_beta
        self.fraction = fraction
        Observable.__init__(self, label)

    def _update_exchange(self, cache):
        """Recompute the Exchange operator(s) if invalid"""
        # alpha
        one_dm_scf_a = cache["one_dm_scf_a"]
        exchange_alpha, new = cache.load(
            f"op_{self.label}_alpha", alloc=one_dm_scf_a.new
        )
        if new:
            self.op_alpha.contract(
                "abcd,cb->ad", one_dm_scf_a, exchange_alpha, clear=True
            )
        # beta
        one_dm_scf_b = cache["one_dm_scf_b"]
        exchange_beta, new = cache.load(
            f"op_{self.label}_beta", alloc=one_dm_scf_b.new
        )
        if new:
            self.op_beta.contract(
                "abcd,cb->ad", one_dm_scf_b, exchange_beta, clear=True
            )

    @doc_inherit(Observable)
    def compute_energy(self, cache):
        self._update_exchange(cache)
        exchange_alpha = cache[f"op_{self.label}_alpha"]
        exchange_beta = cache[f"op_{self.label}_beta"]
        one_dm_scf_a = cache["one_dm_scf_a"]
        one_dm_scf_b = cache["one_dm_scf_b"]
        return -0.5 * self.fraction * exchange_alpha.contract(
            "ab,ab", one_dm_scf_a
        ) - 0.5 * self.fraction * exchange_beta.contract("ab,ab", one_dm_scf_b)

    @doc_inherit(Observable)
    def add_fock(self, cache, fock_alpha, fock_beta):
        self._update_exchange(cache)
        exchange_alpha = cache[f"op_{self.label}_alpha"]
        fock_alpha.iadd(exchange_alpha, -self.fraction)
        exchange_beta = cache[f"op_{self.label}_beta"]
        fock_beta.iadd(exchange_beta, -self.fraction)
