#!/usr/bin/env python3
from pybest import context
from pybest.linalg import DenseLinalgFactory
from pybest.modelhamiltonians.huckel_model import Huckel
from pybest.occ_model import AufbauOccModel

# get the xyz file from pybest/src/pybest/data/test
fn_xyz = context.get_fn("test/c22h12.xyz")

# Number of sites represented as a `LinalgFactory` object (indicating the number of supported atoms).
lf = DenseLinalgFactory(22)

# Define the occupation model where `nel` is the number of C-H bonding and lone-pair electrons.
occ_model = AufbauOccModel(lf, nel=22)

# t=-1 and epsilon=0 are default hopping and on-site parameters, respectively.
modelham = Huckel(lf, occ_model, xyz_file=fn_xyz)
huckel_output = modelham(
    parameters={"on_site": 0.0, "hopping": -1.0, "rhf": True}
)
