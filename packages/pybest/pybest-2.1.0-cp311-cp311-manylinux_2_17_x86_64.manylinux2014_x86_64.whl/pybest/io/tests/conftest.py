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

import numpy as np
import pytest


#
# Functions needed for the atom_data fixture
#
def expected_beryllium() -> dict:
    shell_0 = np.array([[2, 2.653000, 13.325000]], dtype=np.double)
    shell_1 = np.array([[2, 3.120000, -1.574000]], dtype=np.double)
    shell_2 = np.array([[2, 1, 0]], dtype=np.double)

    return {
        "ecp_symbol": "Be",
        "filepath": "test/ECP2SDF-test.g94",
        "core_electrons": 2,
        "max_angular_momentum": 2,
        "shells": [shell_0, shell_1, shell_2],
    }


def expected_protactinium() -> dict:
    shell_0 = np.array(
        [
            [2, 16.81270994994600, 529.49683975232904],
            [2, 3.31661940397354, 4.60731530507061],
            [2, 0.98845251062944, 0.19667819887539],
            [2, 0.19327100174541, 0.01525128403535],
        ],
        dtype=np.double,
    )
    shell_1 = np.array(
        [
            [2, 13.05873366555820, 100.96125506478334],
            [2, 10.53136526927480, 175.91898781787532],
            [2, 2.66062145383770, 0.08948256651573],
            [2, 2.23184466009134, -0.03141149054364],
            [2, 0.75083463469989, 0.04667913126902],
            [2, 0.55889093911325, 0.03542394568499],
            [2, 0.45163532553071, -0.01555232287838],
            [2, 0.28176594801185, -0.02846022183427],
        ],
        dtype=np.double,
    )
    shell_2 = np.array(
        [
            [2, 9.00696519040769, 62.82122158596199],
            [2, 8.47373738148895, 90.12487713400802],
            [2, 1.65090224445044, -0.06430172448254],
            [2, 1.57036896003661, -0.12259581816571],
            [2, 0.50841760608607, 0.03890645175866],
            [2, 0.45320248278456, 0.06526700296031],
            [2, 0.19477094499912, -0.00811031828508],
            [2, 0.25518384414001, -0.02467320302447],
        ],
        dtype=np.double,
    )
    shell_3 = np.array(
        [
            [2, 5.10009191977968, 15.69545396482718],
            [2, 5.24488152070438, 22.32365523358240],
            [2, 1.05946700807573, -0.19902305656031],
            [2, 0.97430352239133, -0.07074250959274],
            [2, 0.49506803278709, 0.06831814090450],
            [2, 0.56517590384140, 0.01692652509430],
            [2, 0.21478294246078, -0.00651312423420],
            [2, 0.18791253677474, -0.00323578050270],
        ],
        dtype=np.double,
    )
    shell_4 = np.array(
        [
            [2, 27.98195179324200, -70.20529751963912],
            [2, 28.09522700516210, -86.24396319084889],
            [2, 8.81848430216155, -8.81929995765213],
            [2, 8.78817166747242, -11.03924923682450],
            [2, 0.88331118810544, 0.00913544616526],
            [2, 0.97704294619128, 0.01227810519828],
        ],
        dtype=np.double,
    )
    shell_5 = np.array([[2, 1, 0]], dtype=np.double)

    return {
        "ecp_symbol": "Pa",
        "filepath": "test/ECP60MDF-test.g94",
        "core_electrons": 60,
        "max_angular_momentum": 5,
        "shells": [shell_0, shell_1, shell_2, shell_3, shell_4, shell_5],
    }


def expected_uranium() -> dict:
    shell_0 = np.array(
        [
            [2, 16.91870874, 529.53526911],
            [2, 3.40970576, 4.27018845],
            [2, 0.79302733, 0.09998874],
            [2, 0.19378381, 0.00626781],
        ],
        dtype=np.double,
    )
    shell_1 = np.array(
        [
            [2, 13.16953414, 100.93359134],
            [2, 10.60784728, 175.95423897],
            [2, 2.69049397, -0.00210787],
            [2, 2.08929800, -0.19041648],
            [2, 0.54050990, 0.00494627],
            [2, 0.40482776, -0.01652483],
            [2, 0.11250285, 0.00082033],
            [2, 0.09508873, -0.00100028],
        ],
        dtype=np.double,
    )
    shell_2 = np.array(
        [
            [2, 9.06784123, 62.85927902],
            [2, 8.53362678, 90.20882494],
            [2, 1.63646790, -0.08282418],
            [2, 1.54425719, -0.15307917],
            [2, 0.47961552, -0.00008720],
            [2, 0.41164502, 0.00484078],
            [2, 0.13990510, -0.00006136],
            [2, 0.17494682, -0.00240839],
        ],
        dtype=np.double,
    )
    shell_3 = np.array(
        [
            [2, 5.14746012, 15.68628229],
            [2, 5.29241394, 22.32105345],
            [2, 1.05726701, -0.20689333],
            [2, 0.98063114, -0.08434451],
            [2, 0.48259555, 0.06084446],
            [2, 0.55434882, 0.00231264],
            [2, 0.23674544, -0.00204069],
            [2, 0.21559852, 0.00348388],
        ],
        dtype=np.double,
    )
    shell_4 = np.array(
        [
            [2, 18.83643086, -44.41029420],
            [2, 18.74850924, -53.65339478],
            [2, 6.49279545, -2.55219343],
            [2, 6.57472519, -3.34380088],
            [2, 2.58151924, 0.04527524],
            [2, 2.58690949, 0.05637947],
        ],
        dtype=np.double,
    )
    shell_5 = np.array([[2, 1, 0]], dtype=np.double)

    return {
        "ecp_symbol": "U",
        "filepath": "test/ECP60MDF-test.g94",
        "core_electrons": 60,
        "max_angular_momentum": 5,
        "shells": [shell_0, shell_1, shell_2, shell_3, shell_4, shell_5],
    }


atom_parameters = [
    expected_beryllium(),
    expected_protactinium(),
    expected_uranium(),
]


#
# Define fixture for testing ecp parser
#
@pytest.fixture(params=atom_parameters)
def atom_data(request) -> dict:
    return request.param
