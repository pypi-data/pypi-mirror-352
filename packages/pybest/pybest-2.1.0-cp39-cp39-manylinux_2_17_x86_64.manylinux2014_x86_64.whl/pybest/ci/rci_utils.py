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
"""
RCI Utils Module
Provides some useful common functions:
"""

from pybest.log import log
from pybest.utility import check_options


def display_csf(data, select, acronym):
    """Printing selected section of the results.

    **Arguments:**

    *data:
        (dictionary) Contains two types of data:
        indices (CIS: spin_block_[1]; CID: spin_block_[1, 2, 3, 4, 5],
        CISD: spin_block_[1, 2, 3, 4, 5, 6]) of the proper CSF block contributions
        and the corresponding coefficients (CIS: c_[1]; CID: c_[1, 2, 3, 4, 5],
        CISD: c_[1, 2, 3, 4, 5, 6]).

    *select:
        (string) The chosen section to print (CIS: 1; CID: 1/2/3/4 or 5, CISD: 1/2/3/4/5 or 6)
        corresponding to the spin block.
    """
    if len(data["spin_block_" + select]) > 0:
        for index, coeff in zip(
            data["spin_block_" + select], data["c_" + select]
        ):
            if acronym in ["CIS"] or (acronym in ["CISD"] and select in ["1"]):
                log(
                    f"\t{'('}{index[0]:d}->{index[1]:d}{')'}\t\t{coeff: 10.5f}"
                )
            else:
                log(
                    f"\t{'('}{index[0]:d}->{index[1]:d}"
                    f"\t{index[2]:d}->{index[3]:d}{')'}"
                    f"\t{coeff: 10.5f}"
                )


def display(data, select, symb1, symb2=None):
    """Printing selected section of the results.

    **Arguments:**

    *data:
        (dictionary) Contains two types of data:
        indices (CIS: spin_block_[a, b]; CID/CISD: spin_block_[aa, bb or ab])
        of the proper SD block contributions and the corresponding coefficients
        (CIS: c_[a, b]; CID/CISD: c_[aa, bb or ab]).

    *select:
        (string) The chosen section to print (CIS: a or b; CID/CISD: aa or bb or ab)
        corresponding to the spin block.

    *symb1:
        (string) symbol of the spin of the first orbital (alpha or beta).

    *symb2:
        (string) symbol of the spin of the second orbital (alpha or beta).
    """
    if len(data["spin_block_" + select]) > 0:
        if symb2 is None:
            log(f"{symb1:>9s} {'contributions:'}")
            for index, coeff in zip(
                data["spin_block_" + select], data["c_" + select]
            ):
                log(
                    f"\t{'('}{index[0]:d}->{index[1]:d}{')'}\t\t{coeff: 10.5f}"
                )
        else:
            log(f"{symb1:>9s}{symb2:s} {'contributions:'}")
            for index, coeff in zip(
                data["spin_block_" + select], data["c_" + select]
            ):
                log(
                    f"\t{'('}{index[0]:d}->{index[1]:d}"
                    f"\t{index[2]:d}->{index[3]:d}{')'}"
                    f"\t{coeff: 10.5f}"
                )


def set_dimension(acronym, nacto, nactv, csf=False):
    """Sets the dimension/number of unknowns of the chosen CI flavour."""
    check_options(
        "acronym",
        acronym,
        "CIS",
        "CID",
        "CISD",
    )
    if acronym == "CIS":
        return nacto * nactv + 1

    if acronym == "CID":
        if csf:
            return (
                nacto * nactv
                + nacto * (nactv * (nactv - 1)) // 2
                + nacto * (nacto - 1) // 2 * nactv
                + nacto * (nacto - 1) * nactv * (nactv - 1) // 2
            ) + 1
        return (
            nacto * nacto * nactv * nactv
            + ((nacto * (nacto - 1)) // 2) * ((nactv * (nactv - 1)) // 2) * 2
        ) + 1
    if acronym == "CISD":
        if csf:
            return (
                nacto * nactv
                + (
                    nacto * nactv
                    + nacto * (nactv * (nactv - 1)) // 2
                    + nacto * (nacto - 1) // 2 * nactv
                    + nacto * (nacto - 1) * nactv * (nactv - 1) // 2
                )
                + 1
            )
        return (
            nacto * nactv * 2
            + (
                nacto * nacto * nactv * nactv
                + ((nacto * (nacto - 1)) // 2)
                * ((nactv * (nactv - 1)) // 2)
                * 2
            )
            + 1
        )
    raise NotImplementedError
