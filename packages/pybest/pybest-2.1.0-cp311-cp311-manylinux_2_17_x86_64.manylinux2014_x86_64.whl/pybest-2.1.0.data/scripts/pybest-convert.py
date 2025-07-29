#!python
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


import argparse

import numpy as np

from pybest import __version__
from pybest.iodata import IOData

# All, except underflows, is *not* fine.
np.seterr(divide="raise", over="raise", invalid="raise")


def parse_args():
    parser = argparse.ArgumentParser(
        prog="pybest-convert.py",
        description="Convert between file formats supported in PyBEST. This "
        "only works of the input contains sufficient data for the "
        "output",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"{parser.prog} (PyBEST version) {__version__}",
    )

    parser.add_argument(
        "--input",
        help="The input file. Supported file types are: "
        "*.h5 (PyBEST's native format), "
        "*.molden (Molden wavefunction file), "
        "*.xyz (The XYZ format).",
    )
    parser.add_argument(
        "--output",
        help="The output file. Supported file types are: "
        "*.h5 (PyBEST's native format), "
        "*.molden (Molden wavefunction file), "
        "*.xyz (The XYZ format).",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    mol = IOData.from_file(args.input)
    mol.to_file(args.output)


if __name__ == "__main__":
    main()
