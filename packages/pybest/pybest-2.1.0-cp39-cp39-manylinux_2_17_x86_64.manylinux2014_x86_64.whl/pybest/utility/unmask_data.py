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
# 2024-04-24: created by Katharina Boguslawski (taken from old utils.py)


"""Utility functions to unmask args and kwargs"""

from pybest.exceptions import ArgumentError
from pybest.featuredlists import OneBodyHamiltonian, TwoBodyHamiltonian
from pybest.iodata import IOData
from pybest.linalg import DenseTwoIndex, Orbital

__all__ = [
    "unmask",
    "unmask_onebody_hamiltonian",
    "unmask_orb",
    "unmask_twobody_hamiltonian",
]


def unmask(label, *args, **kwargs):
    """Check arguments and return some arbitrary data with the label 'label'.
    If not present, None is returned.
    If data with given label is contained in several arguments, it is
    returned in the following order: kwargs > args > IOData.
    """
    data = kwargs.get(label, None)
    if data is None:
        for arg in args:
            if not isinstance(arg, IOData) and hasattr(arg, "label"):
                if arg.label == label:
                    return arg
            if isinstance(arg, IOData) and hasattr(arg, label):
                data = getattr(arg, label)
    return data


def unmask_orb(*args, **kwargs):
    """Check arguments and return orbitals as a list [alpha,beta].
    If not present, empty list is returned.
    If orbitals are contained in several arguments, the orbitals
    are returned in the following order: kwargs > args > IOData.
    """
    orb = []
    #
    # first kwargs
    #
    orb_a = kwargs.get("orb_a", None)
    orb_b = kwargs.get("orb_b", None)
    if orb_a:
        orb.insert(0, orb_a)
    if orb_b:
        orb.append(orb_b)
    #
    # args > IOData
    #
    if not orb:
        orb_data = []
        orb_args = []
        for arg in args:
            if isinstance(arg, Orbital):
                orb_args.append(arg)
            elif isinstance(arg, IOData):
                if hasattr(arg, "orb_a"):
                    orb_data.insert(0, arg.orb_a)
                if hasattr(arg, "orb_b"):
                    orb_data.append(arg.orb_b)
            else:
                continue
        #
        # decide on orbs according to args > IOData.
        # Both alpha and beta orbitals are passed in args or IOData.
        # Mixing is not allowed!
        #
        if orb_args:
            return orb_args
        elif orb_data:
            return orb_data
    return orb


# TODO needs test
def unmask_onebody_hamiltonian(args):
    """Find one-body Hamiltonian terms.

    Args:
        args (list): list containing some NIndex objects

    Returns:
        DenseTwoIndex: sum of several DenseTwoIndex objects.
    """
    one = [x for x in args if getattr(x, "label", 0) in OneBodyHamiltonian]
    if len(one) == 0:
        msg = "Could not find the one-body Hamiltonian in arguments!."
        raise ArgumentError(msg)

    one_sum = DenseTwoIndex(*one[0].shape, label="one")
    for term in one:
        one_sum.iadd(term)
    return one_sum


# TODO needs test
def unmask_twobody_hamiltonian(args):
    """Find two-body Hamiltonian terms.

    Args:
        args (list): a list containing some NIndex objects

    Returns:
        FourIndex: only one FourIndex object is allowed.
    """
    two = [x for x in args if getattr(x, "label", 0) in TwoBodyHamiltonian]
    if len(two) != 1:
        msg = f"Expected one two-body Hamiltonian, but found {len(two)}."
        raise ArgumentError(msg)
    return two[0]
