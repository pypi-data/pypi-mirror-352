#!/usr/bin/env python3

from pybest import context
from pybest.linalg import DenseLinalgFactory
from pybest.modelhamiltonians.ppp_model import PPP
from pybest.occ_model import AufbauOccModel
from pybest.units import electronvolt

# get the xyz file from pybest/src/pybest/data/test
coord = context.get_fn("test/benzeo.xyz")

# Number of sites represented as a `LinalgFactory` object (indicating the number of supported atoms).
lf = DenseLinalgFactory(22)

# Define the occupation model where `nel` is the number of C-H bonding and lone-pair electrons.
occ_model = AufbauOccModel(lf, nel=22)
orb_a = lf.create_orbital()

# t: hopping, u: e-e repulsion, k: dielectric constant, u_p=u/k, hubbard: hubbard term in ppp.
modelham = PPP(lf, occ_model, xyz_file=coord)

ppp_output = modelham(
    parameters={
        "on_site": 0.0,
        "hopping": -2.7 * electronvolt,
        "u": 8.0 * electronvolt,
        "k": 1.0,
        "u_p": 0.8 * electronvolt,
        "hubbard": True,
        "rhf": True,
    }
)
