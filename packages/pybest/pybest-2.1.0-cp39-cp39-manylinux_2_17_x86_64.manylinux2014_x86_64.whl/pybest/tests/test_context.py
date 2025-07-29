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


import os
from pathlib import Path

from pybest import context

from .common import in_pybest_source_root


def test_context():
    fn = context.get_fn("basis/sto-3g.g94")
    assert Path(fn).is_file()
    fns = context.glob("*.g94", "basis")
    assert fn in str(fns)
    fns = context.glob("*/*.g94")
    assert fn in str(fns)


def test_shebang():
    # Make sure that all executable python modules, in the data and
    # scripts directories have a proper shebang line.

    # Collect all bad files
    bad = []

    # Loop over all py files in datadir:
    for fn_py in sorted(context.data_dir.rglob("*.py")):
        # skip all empty __init__.py files in examples
        if "__init__" in str(Path(fn_py).resolve()):
            continue
        if os.access(fn_py, os.X_OK):
            with open(fn_py) as f:
                if f.readline() != "#!/usr/bin/env python3\n":
                    bad.append(fn_py)

    # Loop over all py files in scripts, if testing from the development root:
    if in_pybest_source_root():
        for fn_py in sorted(Path("scripts").rglob("*.py")):
            # Skip this requirement for test files
            if "test" in str(fn_py):
                continue
            assert os.access(
                fn_py, os.X_OK
            ), f"Py files in scripts/ must be executable. Error: {fn_py}"
            with open(fn_py) as f:
                if f.readline() != "#!/usr/bin/env python3\n":
                    bad.append(fn_py)

    if len(bad) > 0:
        print("The following files have an incorrect shebang line:")
        for fn in bad:
            print("   ", fn)
        raise AssertionError(
            "Some Python scripts have an incorrect shebang line."
        )
