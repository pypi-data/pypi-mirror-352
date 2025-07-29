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
# This module has been written and updated by Katharina Boguslawski (see CHANGELOG)
# Its current version contains updates from the PyBEST developer team.
#
# This implementation can also be found in `Horton 2.0.0`.
# However, this file has been updated and debugged. Compatibility with Horton is NOT
# guaranteed.
#
# Detailed changes:
# 2020-07-01: return IOData instance with additional attributes (overlap, orbitals)
# 2020-07-01: update to new python feature, including f-strings
# 2020-07-01: outomatically assign integrals according to PyBEST's internal labeling

"""Molpro 2012 FCIDUMP format.

.. note ::

    One- and two-electron integrals are stored in chemists' notation in an
    FCIDUMP file while PyBEST internally uses Physicist's notation.
"""

from __future__ import annotations

from typing import Any

from pybest.exceptions import ArgumentError
from pybest.featuredlists import OneBodyHamiltonian, TwoBodyHamiltonian


def load_fcidump(filename: str) -> dict[str, Any]:
    """Read one- and two-electron integrals from a Molpro 2012 FCIDUMP file.

    Works only for restricted wavefunctions.

    Keep in mind that the FCIDUMP format changed in Molpro 2012, so files
    generated with older versions are not supported.

    Args:
        filename (str): The filename of the fcidump file.
        lf (TwoIndex | FourIndex): A LinalgFactory instance.

    Raises:
        OSError: Error in FCIDUMP file header
        TypeError: lf.default_nbasis does not match NORB
        OSError: Expecting 5 fields on each data line in FCIDUMP

    Returns:
        (dict[str, Any]):  dictionary with keys: ``lf``, ``nelec``, ``ms2``,
    ``one_mo``, ``two_mo``, ``core_energy``
    """
    # We have to import locally due to circular imports
    from pybest.linalg import DenseLinalgFactory

    lf = DenseLinalgFactory()
    with open(filename) as f:
        # check header
        line = f.readline()
        if not line.startswith(" &FCI NORB="):
            raise OSError("Error in FCIDUMP file header")

        # read info from header
        words = line[5:].split(",")
        header_info = {}
        for word in words:
            if word.count("=") == 1:
                key, value = word.split("=")
                header_info[key.strip()] = value.strip()
        basis = int(header_info["NORB"])
        nelec = int(header_info["NELEC"])
        ms2 = int(header_info["MS2"])
        if lf.default_nbasis is not None and lf.default_nbasis != basis:
            raise TypeError(
                "The value of lf.default_nbasis does not match NORB reported in the FCIDUMP file."
            )
        lf.default_nbasis = basis

        # skip rest of header
        for line in f:
            words = line.split()
            if words[0] == "&END" or words[0] == "/END" or words[0] == "/":
                break

        # read the integrals
        one_mo = lf.create_two_index(label="one")
        two_mo = lf.create_four_index(label="eri")
        core_energy = 0.0

        for line in f:
            words = line.split()
            if len(words) != 5:
                raise OSError(
                    "Expecting 5 fields on each data line in FCIDUMP"
                )
            if words[3] != "0":
                ii = int(words[1]) - 1
                ij = int(words[2]) - 1
                ik = int(words[3]) - 1
                il = int(words[4]) - 1
                # Uncomment the following line if you want to assert that the
                # FCIDUMP file does not contain duplicate 4-index entries.
                # assert two_mo.get_element(ii,ik,ij,il) == 0.0
                two_mo.set_element(ii, ik, ij, il, float(words[0]))
            elif words[1] != "0":
                ii = int(words[1]) - 1
                ij = int(words[2]) - 1
                one_mo.set_element(ii, ij, float(words[0]))
            else:
                core_energy = float(words[0])
    # Assume integrals are defined for an orthonormal basis
    orb_a = lf.create_orbital()
    olp = lf.create_two_index(label="olp")
    olp.assign_diagonal(1.0)
    orb_a.assign(olp)

    return {
        "lf": lf,
        "nelec": nelec,
        "ms2": ms2,
        "one": one_mo,
        "two": two_mo,
        "e_core": core_energy,
        "orb_a": orb_a,
        "olp": olp,
    }


def dump_fcidump(filename: str, data: dict[str, Any]) -> None:
    """Write one- and two-electron integrals in the Molpro 2012 FCIDUMP format.

    Works only for restricted wavefunctions.

    Keep in mind that the FCIDUMP format changed in Molpro 2012, so files
    written with this function cannot be used with older versions of Molpro.

    Args:
        filename (str): The filename of the FCIDUMP file. This is usually "FCIDUMP".
        data (dict[str, Any]): An IOData instance. Must contain ``one_mo``, ``two_mo``.
         May contain ``core_energy``, ``nelec`` and ``ms``

    Raises:
        ArgumentError: Cannot find one-electron integrals in IOData container
        ArgumentError: Cannot find two-electron integrals in IOData container
    """
    one_mo = None
    two_mo = None
    with open(filename, "w") as f:
        if hasattr(data, "one_mo"):
            one_mo = data.one_mo
        elif hasattr(data, "one_ao"):
            one_mo = data.one_ao
        elif hasattr(data, "one"):
            one_mo = data.one
        else:
            for _attr, value in data.__dict__.items():
                if hasattr(value, "dense_two_identifier"):
                    if value.label in OneBodyHamiltonian:
                        if one_mo is not None:
                            one_mo.iadd(value)
                        else:
                            one_mo = value.copy()
        if one_mo is None:
            raise ArgumentError(
                "Cannot find one-electron integrals in IOData container."
            )
        if hasattr(data, "two_mo"):
            two_mo = data.two_mo
        elif hasattr(data, "two_ao"):
            two_mo = data.two_ao
        elif hasattr(data, "two"):
            two_mo = data.two
        else:
            for _attr, value in data.__dict__.items():
                if hasattr(value, "dense_four_identifier") or hasattr(
                    value, "cholesky_four_identifier"
                ):
                    if value.label in TwoBodyHamiltonian:
                        two_mo = value
        if two_mo is None:
            raise ArgumentError(
                "Cannot find two-electron integrals in IOData container."
            )
        nact = one_mo.nbasis
        e_core = getattr(data, "e_core", 0.0)
        nelec = getattr(data, "nelec", 0)
        ms2 = getattr(data, "ms2", 0)

        # Write header
        print(f" &FCI NORB={nact},NELEC={nelec},MS2={ms2},", file=f)
        print(
            "  ORBSYM= " + ",".join(str(1) for v in range(nact)) + ",",
            file=f,
        )
        print("  ISYM=1", file=f)
        print(" &END", file=f)

        # Write integrals and core energy
        for i in range(nact):
            for j in range(i + 1):
                for k in range(nact):
                    for l in range(k + 1):
                        if (i * (i + 1)) / 2 + j >= (k * (k + 1)) / 2 + l:
                            value = two_mo.get_element(i, k, j, l)
                            if value != 0.0:
                                print(
                                    f"{value:23.16e} "
                                    f"{i + 1:4} {j + 1:4} {k + 1:4} {l + 1:4}",
                                    file=f,
                                )
        for i in range(nact):
            for j in range(i + 1):
                value = one_mo.get_element(i, j)
                if value != 0.0:
                    print(
                        f"{value:23.16e} {i + 1:4} {j + 1:4} {0:4} {0:4}",
                        file=f,
                    )
        # Don't check core_energy. We have to print it always.
        # if core_energy != 0.0:
        print(f"{e_core:23.16e} {0:4} {0:4} {0:4} {0:4}", file=f)
