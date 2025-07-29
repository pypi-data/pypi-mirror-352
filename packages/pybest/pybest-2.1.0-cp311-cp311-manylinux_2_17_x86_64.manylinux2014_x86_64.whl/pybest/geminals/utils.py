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
# This module has been originally written and updated by Katharina Boguslawski (see CHANGELOG)
# Its current version contains updates from the PyBEST developer team.
#
# An original version of this implementation can also be found in 'Horton 2.0.0'.
# # However, this file has been updated and debugged. Compatibility with Horton is NOT
# guaranteed.
#
# 10.2022:
# This module has been rewritten by Emil Sujkowski
#
# Moved here from rpccd_base.py:
# - print_final
# - get_slater_determinant
#
# - if statements have been reverted
# - ncore, npairs, nocc, nvirt, nbasis variables has been removed and replaced by
#   the use of occ_model
#
# Detailed changes:
# See CHANGELOG


"""Utility functions

Variables used in this module:
 :nacto:    number of electron pairs
             (abbreviated as no)
 :nact:     total number of basis functions
             (abbreviated as na)
"""

import numpy as np

from pybest import filemanager
from pybest.log import log


def print_solution(
    obj,
    cithresh=0.05,
    excitationlevel=2,
    amplitudestofile=False,
    fname="pccd_amplitudes.dat",
):
    """Print coefficients :math:`{ci}` and Slater Determinant if :math:`|ci|` > threshold.
    Prints up to hextuply excited pairs.

    **Optional arguments:**

    cithresh
            Upper threshold (a float) for CI coefficients to be
            reconstructed. (Default 0.01)

    excitationslevel
            The maximum number of substitutions w.r.t. the reference
            determinant for which the CI coefficients are reconstructed.
            (Default 2)

    amplitudestofile
            A boolean. If True, the CI coefficients are stored in a separate
            file. (Default False)

    filename
            The file name for the wfn amplitudes.
            (Default pccd_amplitudes)
    """
    no = obj.occ_model.nacto[0]

    it = []
    coeff = obj.geminal_matrix._array.copy()

    matrix = np.identity(no)
    solution_dict = {}
    # dump to pybest-results dir
    filename = filemanager.result_path(fname)
    # TODO: check if this is correct
    for i in range(excitationlevel):  # noqa: B007
        it.append(np.nditer(coeff, flags=["multi_index"]))
    if amplitudestofile:
        with open(filename, "w") as filea:
            filea.write(
                f"{get_slater_determinant(obj, (-1, -1))} {1.0: 20.16f}"
            )
            filea.write("\n")
    else:
        log(f"{get_slater_determinant(obj, (-1, -1))} {1.0: 20.16f}")
    for i in range(excitationlevel):
        if i == 0:
            for ci in it[0]:
                if abs(ci) >= 0:
                    sd = get_slater_determinant(obj, it[0].multi_index)
                    if amplitudestofile is True:
                        with open(filename, "a") as filea:
                            filea.write(f"{sd} {ci: 20.16f}")
                            filea.write("\n")
                    else:
                        solution_dict.update({sd: float(ci)})
        if no > 1:
            for index in range(i + 1):
                it[index] = np.nditer(coeff, flags=["multi_index"])
            if i == 1:
                for ci in it[0]:
                    if abs(ci) < (cithresh / excitationlevel):
                        continue

                    it[1] = it[0].copy()
                    for ci2 in it[1]:
                        if it[1].multi_index[0] <= it[0].multi_index[0]:
                            continue
                        if it[1].multi_index[1] <= it[0].multi_index[1]:
                            continue

                        matrix[
                            it[0].multi_index[0],
                            it[0].multi_index[0],
                        ] = float(ci)
                        matrix[
                            it[1].multi_index[0],
                            it[1].multi_index[0],
                        ] = float(ci2)
                        matrix[
                            it[0].multi_index[0],
                            it[1].multi_index[0],
                        ] = coeff[
                            it[0].multi_index[0],
                            it[1].multi_index[1],
                        ]
                        matrix[
                            it[1].multi_index[0],
                            it[0].multi_index[0],
                        ] = coeff[
                            it[1].multi_index[0],
                            it[0].multi_index[1],
                        ]
                        amplitude = obj.perm(matrix)
                        if abs(amplitude) >= cithresh:
                            sd = obj.get_slater_determinant(
                                it[0].multi_index,
                                it[1].multi_index,
                            )
                            if amplitudestofile is True:
                                with open(filename, "a") as filea:
                                    filea.write(f"{sd} {amplitude: 20.16f}")
                                    filea.write("\n")
                            else:
                                solution_dict.update({sd: float(amplitude)})
                        matrix = np.identity(no)
            if i == 2:
                for ci in it[0]:
                    if abs(ci) < (cithresh / excitationlevel):
                        continue

                    it[1] = it[0].copy()
                    for ci2 in it[1]:
                        if it[1].multi_index[0] <= it[0].multi_index[0]:
                            continue
                        if it[1].multi_index[1] <= it[0].multi_index[1]:
                            continue

                        it[2] = it[1].copy()
                        for ci3 in it[2]:
                            if it[2].multi_index[0] > it[1].multi_index[0]:
                                if it[2].multi_index[1] > it[1].multi_index[1]:
                                    matrix[
                                        it[0].multi_index[0],
                                        it[0].multi_index[0],
                                    ] = float(ci)
                                    matrix[
                                        it[1].multi_index[0],
                                        it[1].multi_index[0],
                                    ] = float(ci2)
                                    matrix[
                                        it[2].multi_index[0],
                                        it[2].multi_index[0],
                                    ] = float(ci3)

                                    matrix[
                                        it[0].multi_index[0],
                                        it[1].multi_index[0],
                                    ] = coeff[
                                        it[0].multi_index[0],
                                        it[1].multi_index[1],
                                    ]
                                    matrix[
                                        it[0].multi_index[0],
                                        it[2].multi_index[0],
                                    ] = coeff[
                                        it[0].multi_index[0],
                                        it[2].multi_index[1],
                                    ]

                                    matrix[
                                        it[1].multi_index[0],
                                        it[0].multi_index[0],
                                    ] = coeff[
                                        it[1].multi_index[0],
                                        it[0].multi_index[1],
                                    ]
                                    matrix[
                                        it[1].multi_index[0],
                                        it[2].multi_index[0],
                                    ] = coeff[
                                        it[1].multi_index[0],
                                        it[2].multi_index[1],
                                    ]

                                    matrix[
                                        it[2].multi_index[0],
                                        it[0].multi_index[0],
                                    ] = coeff[
                                        it[2].multi_index[0],
                                        it[0].multi_index[1],
                                    ]
                                    matrix[
                                        it[2].multi_index[0],
                                        it[1].multi_index[0],
                                    ] = coeff[
                                        it[2].multi_index[0],
                                        it[1].multi_index[1],
                                    ]
                                    amplitude = obj.perm(matrix)
                                    if abs(amplitude) >= cithresh:
                                        sd = obj.get_slater_determinant(
                                            it[0].multi_index,
                                            it[1].multi_index,
                                            it[2].multi_index,
                                        )
                                        if amplitudestofile is True:
                                            with open(filename, "a") as filea:
                                                filea.write(
                                                    f"{sd} {amplitude: 20.16f}"
                                                )
                                                filea.write("\n")
                                        else:
                                            solution_dict.update(
                                                {sd: float(amplitude)}
                                            )
                                    matrix = np.identity(no)
            if i == 3:
                for ci in it[0]:
                    if abs(ci) < (cithresh / excitationlevel):
                        continue

                    it[1] = it[0].copy()
                    for ci2 in it[1]:
                        if it[1].multi_index[0] <= it[0].multi_index[0]:
                            continue
                        if it[1].multi_index[1] <= it[0].multi_index[1]:
                            continue

                        it[2] = it[1].copy()
                        for ci3 in it[2]:
                            if it[2].multi_index[0] > it[1].multi_index[0]:
                                if it[2].multi_index[1] > it[1].multi_index[1]:
                                    it[3] = it[2].copy()
                                    for ci4 in it[3]:
                                        if (
                                            it[3].multi_index[0]
                                            > it[2].multi_index[0]
                                        ):
                                            if (
                                                it[3].multi_index[1]
                                                > it[2].multi_index[1]
                                            ):
                                                matrix[
                                                    it[0].multi_index[0],
                                                    it[0].multi_index[0],
                                                ] = float(ci)
                                                matrix[
                                                    it[1].multi_index[0],
                                                    it[1].multi_index[0],
                                                ] = float(ci2)
                                                matrix[
                                                    it[2].multi_index[0],
                                                    it[2].multi_index[0],
                                                ] = float(ci3)
                                                matrix[
                                                    it[3].multi_index[0],
                                                    it[3].multi_index[0],
                                                ] = float(ci4)

                                                matrix[
                                                    it[0].multi_index[0],
                                                    it[1].multi_index[0],
                                                ] = coeff[
                                                    it[0].multi_index[0],
                                                    it[1].multi_index[1],
                                                ]
                                                matrix[
                                                    it[0].multi_index[0],
                                                    it[2].multi_index[0],
                                                ] = coeff[
                                                    it[0].multi_index[0],
                                                    it[2].multi_index[1],
                                                ]
                                                matrix[
                                                    it[0].multi_index[0],
                                                    it[3].multi_index[0],
                                                ] = coeff[
                                                    it[0].multi_index[0],
                                                    it[3].multi_index[1],
                                                ]

                                                matrix[
                                                    it[1].multi_index[0],
                                                    it[0].multi_index[0],
                                                ] = coeff[
                                                    it[1].multi_index[0],
                                                    it[0].multi_index[1],
                                                ]
                                                matrix[
                                                    it[1].multi_index[0],
                                                    it[2].multi_index[0],
                                                ] = coeff[
                                                    it[1].multi_index[0],
                                                    it[2].multi_index[1],
                                                ]
                                                matrix[
                                                    it[1].multi_index[0],
                                                    it[3].multi_index[0],
                                                ] = coeff[
                                                    it[1].multi_index[0],
                                                    it[3].multi_index[1],
                                                ]

                                                matrix[
                                                    it[2].multi_index[0],
                                                    it[0].multi_index[0],
                                                ] = coeff[
                                                    it[2].multi_index[0],
                                                    it[0].multi_index[1],
                                                ]
                                                matrix[
                                                    it[2].multi_index[0],
                                                    it[1].multi_index[0],
                                                ] = coeff[
                                                    it[2].multi_index[0],
                                                    it[1].multi_index[1],
                                                ]
                                                matrix[
                                                    it[2].multi_index[0],
                                                    it[3].multi_index[0],
                                                ] = coeff[
                                                    it[2].multi_index[0],
                                                    it[3].multi_index[1],
                                                ]

                                                matrix[
                                                    it[3].multi_index[0],
                                                    it[0].multi_index[0],
                                                ] = coeff[
                                                    it[3].multi_index[0],
                                                    it[0].multi_index[1],
                                                ]
                                                matrix[
                                                    it[3].multi_index[0],
                                                    it[1].multi_index[0],
                                                ] = coeff[
                                                    it[3].multi_index[0],
                                                    it[1].multi_index[1],
                                                ]
                                                matrix[
                                                    it[3].multi_index[0],
                                                    it[2].multi_index[0],
                                                ] = coeff[
                                                    it[3].multi_index[0],
                                                    it[2].multi_index[1],
                                                ]
                                                amplitude = obj.perm(matrix)
                                                if abs(amplitude) >= cithresh:
                                                    sd = obj.get_slater_determinant(
                                                        it[0].multi_index,
                                                        it[1].multi_index,
                                                        it[2].multi_index,
                                                        it[3].multi_index,
                                                    )
                                                    if (
                                                        amplitudestofile
                                                        is True
                                                    ):
                                                        with open(
                                                            filename,
                                                            "a",
                                                        ) as filea:
                                                            filea.write(
                                                                f"{sd} {amplitude: 20.16f}"
                                                            )
                                                            filea.write("\n")
                                                    else:
                                                        solution_dict.update(
                                                            {
                                                                sd: float(
                                                                    amplitude
                                                                )
                                                            }
                                                        )
                                                matrix = np.identity(no)
            if i == 4:
                for ci in it[0]:
                    if abs(ci) < (cithresh / excitationlevel):
                        continue

                    it[1] = it[0].copy()
                    for ci2 in it[1]:
                        if it[1].multi_index[0] <= it[0].multi_index[0]:
                            continue
                        if it[1].multi_index[1] <= it[0].multi_index[1]:
                            continue

                        it[2] = it[1].copy()
                        for ci3 in it[2]:
                            if (
                                it[2].multi_index[0] > it[1].multi_index[0]
                            ) and (
                                it[2].multi_index[1] > it[1].multi_index[1]
                            ):
                                it[3] = it[2].copy()
                                for ci4 in it[3]:
                                    if (
                                        it[3].multi_index[0]
                                        > it[2].multi_index[0]
                                    ) and (
                                        it[3].multi_index[1]
                                        > it[2].multi_index[1]
                                    ):
                                        it[4] = it[3].copy()
                                        for ci5 in it[4]:
                                            if (
                                                it[4].multi_index[0]
                                                > it[3].multi_index[0]
                                            ) and (
                                                it[4].multi_index[1]
                                                > it[3].multi_index[1]
                                            ):
                                                matrix[
                                                    it[0].multi_index[0],
                                                    it[0].multi_index[0],
                                                ] = float(ci)
                                                matrix[
                                                    it[1].multi_index[0],
                                                    it[1].multi_index[0],
                                                ] = float(ci2)
                                                matrix[
                                                    it[2].multi_index[0],
                                                    it[2].multi_index[0],
                                                ] = float(ci3)
                                                matrix[
                                                    it[3].multi_index[0],
                                                    it[3].multi_index[0],
                                                ] = float(ci4)
                                                matrix[
                                                    it[4].multi_index[0],
                                                    it[4].multi_index[0],
                                                ] = float(ci5)

                                                matrix[
                                                    it[0].multi_index[0],
                                                    it[1].multi_index[0],
                                                ] = coeff[
                                                    it[0].multi_index[0],
                                                    it[1].multi_index[1],
                                                ]
                                                matrix[
                                                    it[0].multi_index[0],
                                                    it[2].multi_index[0],
                                                ] = coeff[
                                                    it[0].multi_index[0],
                                                    it[2].multi_index[1],
                                                ]
                                                matrix[
                                                    it[0].multi_index[0],
                                                    it[3].multi_index[0],
                                                ] = coeff[
                                                    it[0].multi_index[0],
                                                    it[3].multi_index[1],
                                                ]
                                                matrix[
                                                    it[0].multi_index[0],
                                                    it[4].multi_index[0],
                                                ] = coeff[
                                                    it[0].multi_index[0],
                                                    it[4].multi_index[1],
                                                ]

                                                matrix[
                                                    it[1].multi_index[0],
                                                    it[0].multi_index[0],
                                                ] = coeff[
                                                    it[1].multi_index[0],
                                                    it[0].multi_index[1],
                                                ]
                                                matrix[
                                                    it[1].multi_index[0],
                                                    it[2].multi_index[0],
                                                ] = coeff[
                                                    it[1].multi_index[0],
                                                    it[2].multi_index[1],
                                                ]
                                                matrix[
                                                    it[1].multi_index[0],
                                                    it[3].multi_index[0],
                                                ] = coeff[
                                                    it[1].multi_index[0],
                                                    it[3].multi_index[1],
                                                ]
                                                matrix[
                                                    it[1].multi_index[0],
                                                    it[4].multi_index[0],
                                                ] = coeff[
                                                    it[1].multi_index[0],
                                                    it[4].multi_index[1],
                                                ]

                                                matrix[
                                                    it[2].multi_index[0],
                                                    it[0].multi_index[0],
                                                ] = coeff[
                                                    it[2].multi_index[0],
                                                    it[0].multi_index[1],
                                                ]
                                                matrix[
                                                    it[2].multi_index[0],
                                                    it[1].multi_index[0],
                                                ] = coeff[
                                                    it[2].multi_index[0],
                                                    it[1].multi_index[1],
                                                ]
                                                matrix[
                                                    it[2].multi_index[0],
                                                    it[3].multi_index[0],
                                                ] = coeff[
                                                    it[2].multi_index[0],
                                                    it[3].multi_index[1],
                                                ]
                                                matrix[
                                                    it[2].multi_index[0],
                                                    it[4].multi_index[0],
                                                ] = coeff[
                                                    it[2].multi_index[0],
                                                    it[4].multi_index[1],
                                                ]

                                                matrix[
                                                    it[3].multi_index[0],
                                                    it[0].multi_index[0],
                                                ] = coeff[
                                                    it[3].multi_index[0],
                                                    it[0].multi_index[1],
                                                ]
                                                matrix[
                                                    it[3].multi_index[0],
                                                    it[1].multi_index[0],
                                                ] = coeff[
                                                    it[3].multi_index[0],
                                                    it[1].multi_index[1],
                                                ]
                                                matrix[
                                                    it[3].multi_index[0],
                                                    it[2].multi_index[0],
                                                ] = coeff[
                                                    it[3].multi_index[0],
                                                    it[2].multi_index[1],
                                                ]
                                                matrix[
                                                    it[3].multi_index[0],
                                                    it[4].multi_index[0],
                                                ] = coeff[
                                                    it[3].multi_index[0],
                                                    it[4].multi_index[1],
                                                ]

                                                matrix[
                                                    it[4].multi_index[0],
                                                    it[0].multi_index[0],
                                                ] = coeff[
                                                    it[4].multi_index[0],
                                                    it[0].multi_index[1],
                                                ]
                                                matrix[
                                                    it[4].multi_index[0],
                                                    it[1].multi_index[0],
                                                ] = coeff[
                                                    it[4].multi_index[0],
                                                    it[1].multi_index[1],
                                                ]
                                                matrix[
                                                    it[4].multi_index[0],
                                                    it[2].multi_index[0],
                                                ] = coeff[
                                                    it[4].multi_index[0],
                                                    it[2].multi_index[1],
                                                ]
                                                matrix[
                                                    it[4].multi_index[0],
                                                    it[3].multi_index[0],
                                                ] = coeff[
                                                    it[4].multi_index[0],
                                                    it[3].multi_index[1],
                                                ]
                                                amplitude = obj.perm(matrix)
                                                if abs(amplitude) >= cithresh:
                                                    if (
                                                        amplitudestofile
                                                        is True
                                                    ):
                                                        sd = obj.get_slater_determinant(
                                                            it[0].multi_index,
                                                            it[1].multi_index,
                                                            it[2].multi_index,
                                                            it[3].multi_index,
                                                            it[4].multi_index,
                                                        )
                                                        with open(
                                                            filename,
                                                            "a",
                                                        ) as filea:
                                                            filea.write(
                                                                f"{sd} {amplitude: 20.16f}"
                                                            )
                                                            filea.write("\n")
                                                    else:
                                                        solution_dict.update(
                                                            {
                                                                sd: float(
                                                                    amplitude
                                                                )
                                                            }
                                                        )
                                                matrix = np.identity(no)
            if i == 5:
                for ci in it[0]:
                    if abs(ci) < (cithresh / excitationlevel):
                        continue

                    it[1] = it[0].copy()
                    for ci2 in it[1]:
                        if it[1].multi_index[0] <= it[0].multi_index[0]:
                            continue
                        if it[1].multi_index[1] <= it[0].multi_index[1]:
                            continue

                        it[2] = it[1].copy()
                        for ci3 in it[2]:
                            if (
                                it[2].multi_index[0] > it[1].multi_index[0]
                            ) and (
                                it[2].multi_index[1] > it[1].multi_index[1]
                            ):
                                it[3] = it[2].copy()
                                for ci4 in it[3]:
                                    if (
                                        it[3].multi_index[0]
                                        > it[2].multi_index[0]
                                    ) and (
                                        it[3].multi_index[1]
                                        > it[2].multi_index[1]
                                    ):
                                        it[4] = it[3].copy()
                                        for ci5 in it[4]:
                                            if (
                                                it[4].multi_index[0]
                                                > it[3].multi_index[0]
                                            ) and (
                                                it[4].multi_index[1]
                                                > it[3].multi_index[1]
                                            ):
                                                it[5] = it[4].copy()
                                                for ci6 in it[5]:
                                                    if (
                                                        it[5].multi_index[0]
                                                        > it[4].multi_index[0]
                                                    ) and (
                                                        it[5].multi_index[1]
                                                        > it[4].multi_index[1]
                                                    ):
                                                        matrix[
                                                            it[0].multi_index[
                                                                0
                                                            ],
                                                            it[0].multi_index[
                                                                0
                                                            ],
                                                        ] = float(ci)
                                                        matrix[
                                                            it[1].multi_index[
                                                                0
                                                            ],
                                                            it[1].multi_index[
                                                                0
                                                            ],
                                                        ] = float(ci2)
                                                        matrix[
                                                            it[2].multi_index[
                                                                0
                                                            ],
                                                            it[2].multi_index[
                                                                0
                                                            ],
                                                        ] = float(ci3)
                                                        matrix[
                                                            it[3].multi_index[
                                                                0
                                                            ],
                                                            it[3].multi_index[
                                                                0
                                                            ],
                                                        ] = float(ci4)
                                                        matrix[
                                                            it[4].multi_index[
                                                                0
                                                            ],
                                                            it[4].multi_index[
                                                                0
                                                            ],
                                                        ] = float(ci5)
                                                        matrix[
                                                            it[5].multi_index[
                                                                0
                                                            ],
                                                            it[5].multi_index[
                                                                0
                                                            ],
                                                        ] = float(ci6)

                                                        matrix[
                                                            it[0].multi_index[
                                                                0
                                                            ],
                                                            it[1].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[0].multi_index[
                                                                0
                                                            ],
                                                            it[1].multi_index[
                                                                1
                                                            ],
                                                        ]
                                                        matrix[
                                                            it[0].multi_index[
                                                                0
                                                            ],
                                                            it[2].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[0].multi_index[
                                                                0
                                                            ],
                                                            it[2].multi_index[
                                                                1
                                                            ],
                                                        ]
                                                        matrix[
                                                            it[0].multi_index[
                                                                0
                                                            ],
                                                            it[3].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[0].multi_index[
                                                                0
                                                            ],
                                                            it[3].multi_index[
                                                                1
                                                            ],
                                                        ]
                                                        matrix[
                                                            it[0].multi_index[
                                                                0
                                                            ],
                                                            it[4].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[0].multi_index[
                                                                0
                                                            ],
                                                            it[4].multi_index[
                                                                1
                                                            ],
                                                        ]
                                                        matrix[
                                                            it[0].multi_index[
                                                                0
                                                            ],
                                                            it[5].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[0].multi_index[
                                                                0
                                                            ],
                                                            it[5].multi_index[
                                                                1
                                                            ],
                                                        ]

                                                        matrix[
                                                            it[1].multi_index[
                                                                0
                                                            ],
                                                            it[0].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[1].multi_index[
                                                                0
                                                            ],
                                                            it[0].multi_index[
                                                                1
                                                            ],
                                                        ]
                                                        matrix[
                                                            it[1].multi_index[
                                                                0
                                                            ],
                                                            it[2].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[1].multi_index[
                                                                0
                                                            ],
                                                            it[2].multi_index[
                                                                1
                                                            ],
                                                        ]
                                                        matrix[
                                                            it[1].multi_index[
                                                                0
                                                            ],
                                                            it[3].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[1].multi_index[
                                                                0
                                                            ],
                                                            it[3].multi_index[
                                                                1
                                                            ],
                                                        ]
                                                        matrix[
                                                            it[1].multi_index[
                                                                0
                                                            ],
                                                            it[4].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[1].multi_index[
                                                                0
                                                            ],
                                                            it[4].multi_index[
                                                                1
                                                            ],
                                                        ]
                                                        matrix[
                                                            it[1].multi_index[
                                                                0
                                                            ],
                                                            it[5].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[1].multi_index[
                                                                0
                                                            ],
                                                            it[5].multi_index[
                                                                1
                                                            ],
                                                        ]

                                                        matrix[
                                                            it[2].multi_index[
                                                                0
                                                            ],
                                                            it[0].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[2].multi_index[
                                                                0
                                                            ],
                                                            it[0].multi_index[
                                                                1
                                                            ],
                                                        ]
                                                        matrix[
                                                            it[2].multi_index[
                                                                0
                                                            ],
                                                            it[1].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[2].multi_index[
                                                                0
                                                            ],
                                                            it[1].multi_index[
                                                                1
                                                            ],
                                                        ]
                                                        matrix[
                                                            it[2].multi_index[
                                                                0
                                                            ],
                                                            it[3].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[2].multi_index[
                                                                0
                                                            ],
                                                            it[3].multi_index[
                                                                1
                                                            ],
                                                        ]
                                                        matrix[
                                                            it[2].multi_index[
                                                                0
                                                            ],
                                                            it[4].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[2].multi_index[
                                                                0
                                                            ],
                                                            it[4].multi_index[
                                                                1
                                                            ],
                                                        ]
                                                        matrix[
                                                            it[2].multi_index[
                                                                0
                                                            ],
                                                            it[5].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[2].multi_index[
                                                                0
                                                            ],
                                                            it[5].multi_index[
                                                                1
                                                            ],
                                                        ]

                                                        matrix[
                                                            it[3].multi_index[
                                                                0
                                                            ],
                                                            it[0].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[3].multi_index[
                                                                0
                                                            ],
                                                            it[0].multi_index[
                                                                1
                                                            ],
                                                        ]
                                                        matrix[
                                                            it[3].multi_index[
                                                                0
                                                            ],
                                                            it[1].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[3].multi_index[
                                                                0
                                                            ],
                                                            it[1].multi_index[
                                                                1
                                                            ],
                                                        ]
                                                        matrix[
                                                            it[3].multi_index[
                                                                0
                                                            ],
                                                            it[2].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[3].multi_index[
                                                                0
                                                            ],
                                                            it[2].multi_index[
                                                                1
                                                            ],
                                                        ]
                                                        matrix[
                                                            it[3].multi_index[
                                                                0
                                                            ],
                                                            it[4].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[3].multi_index[
                                                                0
                                                            ],
                                                            it[4].multi_index[
                                                                1
                                                            ],
                                                        ]
                                                        matrix[
                                                            it[3].multi_index[
                                                                0
                                                            ],
                                                            it[5].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[3].multi_index[
                                                                0
                                                            ],
                                                            it[5].multi_index[
                                                                1
                                                            ],
                                                        ]

                                                        matrix[
                                                            it[4].multi_index[
                                                                0
                                                            ],
                                                            it[0].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[4].multi_index[
                                                                0
                                                            ],
                                                            it[0].multi_index[
                                                                1
                                                            ],
                                                        ]
                                                        matrix[
                                                            it[4].multi_index[
                                                                0
                                                            ],
                                                            it[1].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[4].multi_index[
                                                                0
                                                            ],
                                                            it[1].multi_index[
                                                                1
                                                            ],
                                                        ]
                                                        matrix[
                                                            it[4].multi_index[
                                                                0
                                                            ],
                                                            it[2].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[4].multi_index[
                                                                0
                                                            ],
                                                            it[2].multi_index[
                                                                1
                                                            ],
                                                        ]
                                                        matrix[
                                                            it[4].multi_index[
                                                                0
                                                            ],
                                                            it[3].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[4].multi_index[
                                                                0
                                                            ],
                                                            it[3].multi_index[
                                                                1
                                                            ],
                                                        ]
                                                        matrix[
                                                            it[4].multi_index[
                                                                0
                                                            ],
                                                            it[5].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[4].multi_index[
                                                                0
                                                            ],
                                                            it[5].multi_index[
                                                                1
                                                            ],
                                                        ]

                                                        matrix[
                                                            it[5].multi_index[
                                                                0
                                                            ],
                                                            it[0].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[5].multi_index[
                                                                0
                                                            ],
                                                            it[0].multi_index[
                                                                1
                                                            ],
                                                        ]
                                                        matrix[
                                                            it[5].multi_index[
                                                                0
                                                            ],
                                                            it[1].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[5].multi_index[
                                                                0
                                                            ],
                                                            it[1].multi_index[
                                                                1
                                                            ],
                                                        ]
                                                        matrix[
                                                            it[5].multi_index[
                                                                0
                                                            ],
                                                            it[2].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[5].multi_index[
                                                                0
                                                            ],
                                                            it[2].multi_index[
                                                                1
                                                            ],
                                                        ]
                                                        matrix[
                                                            it[5].multi_index[
                                                                0
                                                            ],
                                                            it[3].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[5].multi_index[
                                                                0
                                                            ],
                                                            it[3].multi_index[
                                                                1
                                                            ],
                                                        ]
                                                        matrix[
                                                            it[5].multi_index[
                                                                0
                                                            ],
                                                            it[4].multi_index[
                                                                0
                                                            ],
                                                        ] = coeff[
                                                            it[5].multi_index[
                                                                0
                                                            ],
                                                            it[4].multi_index[
                                                                1
                                                            ],
                                                        ]

                                                        amplitude = obj.perm(
                                                            matrix
                                                        )
                                                        if (
                                                            abs(amplitude)
                                                            >= cithresh
                                                        ):
                                                            sd = obj.get_slater_determinant(
                                                                it[
                                                                    0
                                                                ].multi_index,
                                                                it[
                                                                    1
                                                                ].multi_index,
                                                                it[
                                                                    2
                                                                ].multi_index,
                                                                it[
                                                                    3
                                                                ].multi_index,
                                                                it[
                                                                    4
                                                                ].multi_index,
                                                                it[
                                                                    5
                                                                ].multi_index,
                                                            )
                                                            if (
                                                                amplitudestofile
                                                                is True
                                                            ):
                                                                with open(
                                                                    filename,
                                                                    "a",
                                                                ) as filea:
                                                                    filea.write(
                                                                        f"{sd} {amplitude: 20.16f}"
                                                                    )
                                                                    filea.write(
                                                                        "\n"
                                                                    )
                                                            else:
                                                                solution_dict.update(
                                                                    {
                                                                        sd: float(
                                                                            amplitude
                                                                        )
                                                                    }
                                                                )
                                                        matrix = np.identity(
                                                            no
                                                        )
            if i == 6:
                for ci in it[0]:
                    if abs(ci) < (cithresh / excitationlevel):
                        continue

                    it[1] = it[0].copy()
                    for ci2 in it[1]:
                        if it[1].multi_index[0] <= it[0].multi_index[0]:
                            continue
                        if it[1].multi_index[1] <= it[0].multi_index[1]:
                            continue

                        it[2] = it[1].copy()
                        for ci3 in it[2]:
                            if (
                                it[2].multi_index[0] > it[1].multi_index[0]
                            ) and (
                                it[2].multi_index[1] > it[1].multi_index[1]
                            ):
                                it[3] = it[2].copy()
                                for ci4 in it[3]:
                                    if (
                                        it[3].multi_index[0]
                                        > it[2].multi_index[0]
                                    ) and (
                                        it[3].multi_index[1]
                                        > it[2].multi_index[1]
                                    ):
                                        it[4] = it[3].copy()
                                        for ci5 in it[4]:
                                            if (
                                                it[4].multi_index[0]
                                                > it[3].multi_index[0]
                                            ) and (
                                                it[4].multi_index[1]
                                                > it[3].multi_index[1]
                                            ):
                                                it[5] = it[4].copy()
                                                for ci6 in it[5]:
                                                    if (
                                                        it[5].multi_index[0]
                                                        > it[4].multi_index[0]
                                                    ) and (
                                                        it[5].multi_index[1]
                                                        > it[4].multi_index[1]
                                                    ):
                                                        it[6] = it[5].copy()
                                                        for ci7 in it[6]:
                                                            if (
                                                                it[
                                                                    6
                                                                ].multi_index[
                                                                    0
                                                                ]
                                                                > it[
                                                                    5
                                                                ].multi_index[
                                                                    0
                                                                ]
                                                            ) and (
                                                                it[
                                                                    6
                                                                ].multi_index[
                                                                    1
                                                                ]
                                                                > it[
                                                                    5
                                                                ].multi_index[
                                                                    1
                                                                ]
                                                            ):
                                                                matrix[
                                                                    it[
                                                                        0
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        0
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = float(ci)
                                                                matrix[
                                                                    it[
                                                                        1
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        1
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = float(ci2)
                                                                matrix[
                                                                    it[
                                                                        2
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        2
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = float(ci3)
                                                                matrix[
                                                                    it[
                                                                        3
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        3
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = float(ci4)
                                                                matrix[
                                                                    it[
                                                                        4
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        4
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = float(ci5)
                                                                matrix[
                                                                    it[
                                                                        5
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        5
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = float(ci6)
                                                                matrix[
                                                                    it[
                                                                        6
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        6
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = float(ci7)

                                                                matrix[
                                                                    it[
                                                                        0
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        1
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        0
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        1
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        0
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        2
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        0
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        2
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        0
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        3
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        0
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        3
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        0
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        4
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        0
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        4
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        0
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        5
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        0
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        5
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        0
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        6
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        0
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        6
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]

                                                                matrix[
                                                                    it[
                                                                        1
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        0
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        1
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        0
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        1
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        2
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        1
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        2
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        1
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        3
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        1
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        3
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        1
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        4
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        1
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        4
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        1
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        5
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        1
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        5
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        1
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        6
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        1
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        6
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]

                                                                matrix[
                                                                    it[
                                                                        2
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        0
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        2
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        0
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        2
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        1
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        2
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        1
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        2
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        3
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        2
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        3
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        2
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        4
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        2
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        4
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        2
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        5
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        2
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        5
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        2
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        6
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        2
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        6
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]

                                                                matrix[
                                                                    it[
                                                                        3
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        0
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        3
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        0
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        3
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        1
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        3
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        1
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        3
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        2
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        3
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        2
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        3
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        4
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        3
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        4
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        3
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        5
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        3
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        5
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        3
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        6
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        3
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        6
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]

                                                                matrix[
                                                                    it[
                                                                        4
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        0
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        4
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        0
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        4
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        1
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        4
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        1
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        4
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        2
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        4
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        2
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        4
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        3
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        4
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        3
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        4
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        5
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        4
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        5
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        4
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        6
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        4
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        6
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]

                                                                matrix[
                                                                    it[
                                                                        5
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        0
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        5
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        0
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        5
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        1
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        5
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        1
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        5
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        2
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        5
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        2
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        5
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        3
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        5
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        3
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        5
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        4
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        5
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        4
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        5
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        6
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        5
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        6
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]

                                                                matrix[
                                                                    it[
                                                                        6
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        0
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        6
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        0
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        6
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        1
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        6
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        1
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        6
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        2
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        6
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        2
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        6
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        3
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        6
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        3
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        6
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        4
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        6
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        4
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                matrix[
                                                                    it[
                                                                        6
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        5
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                ] = coeff[
                                                                    it[
                                                                        6
                                                                    ].multi_index[
                                                                        0
                                                                    ],
                                                                    it[
                                                                        5
                                                                    ].multi_index[
                                                                        1
                                                                    ],
                                                                ]
                                                                amplitude = (
                                                                    obj.perm(
                                                                        matrix
                                                                    )
                                                                )
                                                                if (
                                                                    abs(
                                                                        amplitude
                                                                    )
                                                                    >= cithresh
                                                                ):
                                                                    if (
                                                                        amplitudestofile
                                                                        is True
                                                                    ):
                                                                        sd = obj.get_slater_determinant(
                                                                            it[
                                                                                0
                                                                            ].multi_index,
                                                                            it[
                                                                                1
                                                                            ].multi_index,
                                                                            it[
                                                                                2
                                                                            ].multi_index,
                                                                            it[
                                                                                3
                                                                            ].multi_index,
                                                                            it[
                                                                                4
                                                                            ].multi_index,
                                                                            it[
                                                                                5
                                                                            ].multi_index,
                                                                            it[
                                                                                6
                                                                            ].multi_index,
                                                                        )
                                                                        with (
                                                                            open(
                                                                                filename,
                                                                                "a",
                                                                            ) as filea
                                                                        ):
                                                                            filea.write(
                                                                                f"{sd} {amplitude: 20.16f}"
                                                                            )
                                                                            filea.write(
                                                                                "\n"
                                                                            )
                                                                    else:
                                                                        solution_dict.update(
                                                                            {
                                                                                sd: float(
                                                                                    amplitude
                                                                                )
                                                                            }
                                                                        )
                                                                matrix = np.identity(
                                                                    no
                                                                )
    from collections import OrderedDict

    sorted_pairs = sorted(
        solution_dict.items(), key=lambda k: abs(k[1]), reverse=True
    )
    ordered_dict = OrderedDict(sorted_pairs)
    for key, value in ordered_dict.items():
        log(f"{key} {value:20.16f}")


def get_slater_determinant(obj, *indices):
    """Return excited Slater Determinant.

    **Arguments:**

    indices
            A (list of) multi-index. First element contains occupied index
            w.r.t. reference determinant, second element contains virtual
            index w.r.t. reference determinant.
    """
    no = obj.occ_model.nacto[0]
    na = obj.occ_model.nact[0]

    orb_ref = []
    excited = []
    for ind in indices:
        orb_ref.append(ind[0])
        excited.append(ind[1] + no)

    sd = []
    for i in range(na):
        if i in orb_ref:
            sd.append(0)
        elif i in excited:
            sd.append(2)
        else:
            if i < no:
                sd.append(2)
            else:
                sd.append(0)

    return str(sd).translate(str.maketrans("", "", ", "))
