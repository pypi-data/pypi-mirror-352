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

from pybest import context
from pybest.io.embedding import load_embedding

# all elements of coords (10)
ref_coords = np.array(
    [
        [
            9.786939509959390548e00,
            9.786939509959385219e00,
            -1.559883756011516098e01,
        ],
        [
            1.103004381738485584e01,
            1.103004381738485051e01,
            -1.317031110192973031e01,
        ],
        [
            8.644496266296856746e00,
            8.644496266296851417e00,
            -1.313731163432065685e01,
        ],
        [
            9.289482143189065511e00,
            9.289482143189061958e00,
            -1.172747263669079132e01,
        ],
        [
            4.037276242018354111e00,
            1.506732005940319041e01,
            -1.317031110192973031e01,
        ],
        [
            3.582268485946772607e00,
            1.336920799590614628e01,
            -1.559883756011516098e01,
        ],
        [
            3.164105236384388231e00,
            1.180860150268122943e01,
            -1.313731163432065685e01,
        ],
        [
            2.278092695441131799e00,
            8.501957683737808580e00,
            -1.313731163432065685e01,
        ],
        [
            3.400186452409120541e00,
            1.268966859559817095e01,
            -1.172747263669079132e01,
        ],
        [
            2.676407152505759335e00,
            9.988487474892204787e00,
            -1.084980851425191162e01,
        ],
    ]
)

# all elements of weights (10)
ref_weights = np.array(
    [
        7.883610481834972461e01,
        1.247435090968685643e02,
        3.500304032634051055e01,
        5.860986764063856214e01,
        1.247435090968685643e02,
        7.883610481834972461e01,
        3.500304032634051055e01,
        4.724680611885899850e01,
        5.860986764063856214e01,
        1.505908505334206815e01,
    ]
)
# all elements of charges (10)
ref_charges = np.array(
    [
        -1.737991753428243899e-11,
        -1.367767580206739005e-14,
        -8.124997547931548861e-14,
        -2.395554471674016197e-13,
        -1.367767580206739005e-14,
        -1.737991753428243899e-11,
        -8.124997547931548861e-14,
        -3.421482455655169577e-13,
        -2.395554471674016197e-13,
        -2.483540894177513889e-12,
    ]
)

data_embedding = [
    (
        "he-in-he.emb",
        {
            "coords": ref_coords,
            "weights": ref_weights,
            "charges": ref_charges,
            "n_points": 10,
        },
    )
]


def check_emb_charges(emb_source, expected):
    """Reference data for comparison taken from He embedded in He test case."""
    data = load_embedding(emb_source)
    n_charges_full = data["n_points"]
    coords_full = data["coordinates"]
    weights_full = data["weights"]
    charges_full = data["charges"]

    assert n_charges_full == expected["n_points"]
    assert np.allclose(coords_full, expected["coords"])
    assert np.allclose(weights_full, expected["weights"])
    assert np.allclose(charges_full, expected["charges"])


@pytest.mark.parametrize("embed_source,expected", data_embedding)
def test_load_emb(embed_source, expected):
    """Checks the performance of load_embedding."""
    emb_source = context.get_fn(f"test/{embed_source}")
    check_emb_charges(emb_source, expected)
