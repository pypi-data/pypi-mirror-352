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
#
# The testing framework has been originally written by Julia Szczuczko (see CHANGELOG).


import json
from pathlib import Path

from pybest.context import context
from pybest.periodic import periodic


def in_pybest_source_root():
    """Test if the current directory is the PyBEST source tree root"""
    # Check for some files and directories that must be present (for functions
    # that use this check).
    if not Path("setup.py").is_file():
        return False
    if not Path("src").is_dir():
        return False
    if not Path("scripts").is_dir():
        return False
    if not Path("README").is_file():
        return False
    with open("README") as f:
        if (
            next(f)
            != "PyBEST: *Py*thonic *B*lack-box *E*lectronic *S*tructure *T*ool.\n"
        ):
            return False
    return True


def load_reference_data(
    method,
    molecule_name,
    basis,
    charge=0,
    ncore=0,
    nroot=0,
    spinfree=False,
    nguessv=0,
    orb_type="",
    nhole=0,
    required_keys=None,
):
    """
    Load reference data for a specific test configuration.

    The function retrieves pre-defined reference data from a JSON file
    based on the naming convention:
    `src/pybest/tests/reference_data/<method>_<molecule>_<basis>_ncore<ncore>_charge<charge>_nroot<nroot>.json`

    Args:
    method (str): Computational method (e.g., RpCCD, ROOpCCD).
    molecule_name (str): Name of the molecule.
    basis (str): Basis set used.
    charge (int, optional): Molecular charge. Default is 0.
    ncore (int, optional): Number of frozen core orbitals. Default is 0.
    nroot (int, optional): Number of targeted roots. Default is 0.
    spinfree (bool, optional): If True, spin-free variant. Default is False.
    nguessv (int, optional): Default is 0. If equal to 0, doesn't affect the file name.
    orb_type (string, optional): Expexcted values: can or opt. Default is empty string.
    nhole (int, optional): Default is 0. If equal to 0, doesn't affect the file name.
    required_keys (list, optional): Keys that must be present in the reference data. Default is None.

    Returns:
    dict: Reference data loaded from the corresponding JSON file.

    Raises:
    FileNotFoundError: If the reference data file does not exist.
    AssertionError: If the reference data file is missing, causing the test to fail.
    """
    # Construct the filename
    filename = f"{method}_{molecule_name}_{basis}_ncore{ncore}_charge{charge}_nroot{nroot}"
    if spinfree:
        filename += "_spinfree"
    if nguessv != 0:
        filename += f"_nguessv{nguessv}"
    if orb_type != "":
        filename += f"_{orb_type}"
    if nhole != 0:
        filename += f"_nhole{nhole}"

    file_path = context.get_fn(f"molecule_reference_data/{filename}.json")

    # Check if the file exists
    if not Path(file_path).exists():
        # Normalize molecule name using the periodic table
        try:
            m_name = periodic[molecule_name.strip().lower()].name.lower()
        except KeyError as err:
            raise KeyError(
                f"Invalid molecule name or symbol: {molecule_name}"
            ) from err

        filename = f"{method}_{m_name}_{basis}_ncore{ncore}_charge{charge}_nroot{nroot}"
        if spinfree:
            filename += "_spinfree"
        if nguessv != 0:
            filename += f"_nguessv{nguessv}"
        if orb_type != "":
            filename += f"_{orb_type}"
        if nhole != 0:
            filename += f"_nhole{nhole}"

        f_path = context.get_fn(f"molecule_reference_data/{filename}.json")
        if Path(f_path).exists():
            file_path = f_path
        else:
            raise AssertionError(f"Reference data file not found: {f_path}")

    # Load the reference data
    with open(file_path) as file:
        data = json.load(file)

    # Validate required keys
    if required_keys:
        for key in required_keys:
            if key not in data:
                raise AssertionError(
                    f"Missing required key '{key}' in reference data: {file_path}"
                )

    return data
