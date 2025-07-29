#!/usr/bin/env python3
from pybest.linalg import DenseLinalgFactory
from pybest.modelhamiltonians import Hubbard
from pybest.occ_model import AufbauOccModel

# Number of sites represented as a `LinalgFactory` object.
lf = DenseLinalgFactory(6)

# If xyz_file is not provided, this would be a site model.
# Define the occupation model where `nel` is the number of electrons in the 1D Hubbard model.
occ_model = AufbauOccModel(lf, nel=6)

# t=-1 and epsilon=0 are default hopping and on-site parameters, respectively.
modelham = Hubbard(lf, occ_model, pbc=True)
hubbard_output = modelham(
    parameters={"on_site": 0.0, "hopping": -1.0, "u": 1.0},
)
