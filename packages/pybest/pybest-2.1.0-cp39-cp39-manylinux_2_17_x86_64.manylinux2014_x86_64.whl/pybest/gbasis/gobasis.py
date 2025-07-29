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
"""Gaussian orbital basis set module."""

from __future__ import annotations

from pathlib import Path, PurePath
from typing import Any

from pybest import filemanager
from pybest.context import context
from pybest.core import basis as module_basis
from pybest.exceptions import BasisError

# from pybest.iodata import IOData
from pybest.io.xyz import dump_xyz, load_xyz
from pybest.linalg import DenseTwoIndex
from pybest.log import log, timer
from pybest.utility import check_gobasis

# nanobind classes
from . import Basis

__all__ = [
    "get_gobasis",
    "get_tform_u2c",
]


@timer.with_section("Basis: ReadBasisSet")
def get_gobasis(
    basisname: str,
    coords: Any,
    active_fragment: Any | None = None,
    dummy: Any | None = None,
    element_map: Any | None = None,
    print_basis: bool = True,
) -> Basis:
    """Read basis set for molecular coordinates. If active_fragment and dummy are specified,
    the function will consider only the active fragment (active_fragment) and introduce
    ghost atoms (dummy).

    **Arguments:**

    basisname
        The name of the basis set

    coords
        filename containing the xyz coordinates or an IOData instance.


    **Optional arguments:**

    active_fragment
        Active fragment. A list containing the indices of all active atoms

    dummy
        Dummy atoms. A list containing the indices of all dummy atoms (same
        basis set as atom, but setting a charge of 0).

    element_map
        Different basis sets for different atoms. A dictionary containing
        the element names as keys and the basis set string as basis set
        information.

    print_basis
         If True (default), the information about the basis set is printed.
    """
    log.cite("the use of the Libint library", "valeev2019")

    #
    # Auxiliary functions
    #

    def dump_xyz_libint(fname, mol, unit_angstrom=False, fragment=None):
        #
        # Temporary file stored in filemanager.temp_dir
        #
        filename = filemanager.temp_path(f"{Path(fname).stem}.xyz")
        #
        # dump xyz coordinates of active fragment
        #
        dump_xyz(filename, mol, unit_angstrom=unit_angstrom, fragment=fragment)
        #
        # overwrite filename info
        #
        return filename

    def get_dir_path(basisname):
        dir_path = None
        # Check if augmented basis; PyBEST stores the full basis
        basisname_old = basisname
        if "aug-" in basisname:
            basisname = basisname.replace("aug-", "aug")
        if "*" in basisname:
            basisname = basisname.replace("*", "star")
        if "6-3" in basisname:
            basisname = basisname.replace("6-3", "63")
        if context.check_fn(f"basis/{basisname.lower()}.g94"):
            dir_path = (
                Path(context.get_fn(f"basis/{basisname.lower()}.g94"))
                .resolve()
                .parent
            )
            basisname = basisname.lower()
        elif Path(basisname_old).exists():
            if "aug-" in basisname_old:
                raise BasisError(
                    "User-defined basis set cannot start with 'aug-'. Please rename "
                    "your basis set."
                )
            dir_path = Path(basisname_old).resolve().parent
            basisname = PurePath(basisname_old).stem
        else:
            raise BasisError(
                f"Basis set file {basisname}/{basisname_old} not found. "
                "Please check if file is present."
            )
        return dir_path, basisname

    def print_basis_info():
        if print_basis:
            if log.do_medium:
                log.hline("#")
                if active_fragment is None:
                    log("Printing basis for whole molecule:")
                else:
                    s = (
                        "["
                        + ",".join([f"{s_}" for s_ in active_fragment])
                        + "]"
                    )
                    log(f"Printing basis for active fragment {s}")
                basis.print_basis_info()
                log.hline("~")

    def print_active_fragmet_info():
        if active_fragment is not None:
            if log.do_medium:
                log.hline("#")
                log("Creating active fragment of supramolecule.")
                log.hline("-")
                basis.print_atomic_info()
                log.hline("-")

    def create_dummy_atoms():
        if dummy is not None:
            if not isinstance(dummy, list):
                raise BasisError("Dummy indices have to be a list")
            if not all(idx >= 0 for idx in dummy):
                raise BasisError(
                    f"Dummy indices have to be greater or equal 0. Got {dummy} instead."
                    f"Dummy indices have to be greater or equal {0}. Got negative instead."
                )
            #
            # account for shift due to active fragments:
            #
            shift = 0
            if active_fragment is not None:
                shift = min(active_fragment)
            for idx in dummy:
                if idx > basis.ncenter:
                    raise BasisError(
                        f"Dummy index {idx + 1} larger than number of "
                        f"atoms {basis.ncenter}."
                    )
                basis.set_dummy_atoms(idx - shift)
            if log.do_medium:
                log.hline("#")
                log(
                    "Introducing dummy atoms. Coordinates [bohr] contain new charges:"
                )
                log.hline("-")
                basis.print_atomic_info()
                log.hline("-")

    #
    # Check coordinates: filename or IOData container; convert to pathlib.Path
    #
    coordfile = coords
    #
    # If np.ndarray, convert to .xyz format to read in coordinates using API
    #
    if isinstance(coordfile, str):
        coordfile = Path(coordfile)
    else:
        #
        # Check if xyz file is present
        #
        if hasattr(coordfile, "filename"):
            coordfile = Path(coordfile.filename)
        else:
            #
            # If not, create xyz file
            # Dump coordinates for libint2 interface
            #
            coordfile = dump_xyz_libint("tmp_mol.xyz", coordfile)
    #
    # Check for active fragments and decompose total molecules according to it
    #
    if active_fragment is not None:
        if not isinstance(active_fragment, list):
            raise BasisError("active_fragment has to be a list")
        #
        # Check if dummy atom is in active_fragment, otherwise raise error
        #
        if not all(idx >= 0 for idx in active_fragment):
            raise BasisError(
                f"Active indices have to be greater or equal 0. Got {active_fragment} instead."
                f"Active indices have to be greater or equal {0}. Got negative instead."
            )
        if dummy is not None:
            for idx in dummy:
                if idx not in active_fragment:
                    raise BasisError(
                        f"Dummy atom {idx} has to be in active_fragment"
                    )
        #
        # Create active fragment and save it to disk in filemanager.temp_dir
        # Read all coordinates in angstrom
        #
        data = load_xyz(coordfile, unit_angstrom=True)
        mol = {
            "coordinates": data["coordinates"],
            "atom": data["atom"],
            "natom": len(data["atom"]),
        }
        #
        # overwrite filename info
        #
        coordfile = dump_xyz_libint(
            coordfile, mol, unit_angstrom=True, fragment=active_fragment
        )
    #
    # Check if basis set file is available
    #
    dir_path, basisname = get_dir_path(basisname)
    #
    # Read in basis (pass str to c++ routine)
    #
    basis = Basis(basisname, str(coordfile.resolve()), str(dir_path.resolve()))
    #
    # Print basis set information
    #
    print_basis_info()
    #
    # Print some info if fragments are present
    #
    print_active_fragmet_info()
    #
    # Create dummy atoms
    #
    create_dummy_atoms()
    #
    # Check basis set for consistencies
    #
    check_gobasis(basis)

    return basis


#
# Basis set transformation uncontracted<->contracted
#


def get_tform_u2c(basis: Basis):
    """Transform intergrals from an uncontracted to a contracted basis set

    **Arguments:**

    basis
         FIXME

    **Returns:** ``TwoIndex`` object
    """
    # To prevent circular imports, import locally.
    # This can be fixed by passing an lf instance, which requires a rewrite

    nub = module_basis.get_nubf(basis, True)
    # prepare the output array
    output = DenseTwoIndex(basis.nbasis, nub)
    # call the low-level routine
    module_basis.get_solid_tform_u2c(basis, output.array, basis.nbasis, nub)
    # done
    return output
