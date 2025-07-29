// PyBEST: Pythonic Black-box Electronic Structure Tool
// Copyright (C) 2016-- The PyBEST Development Team
//
// This file is part of PyBEST.
//
// PyBEST is free software; you can redistribute it and/or
// modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 3
// of the License, or (at your option) any later version.
//
// PyBEST is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>
// --

#ifndef PYBEST_CORE_EXTERNAL_H_
#define PYBEST_CORE_EXTERNAL_H_

#include <cmath>
#include <vector>

#include "basis.h"
#include "external_charges.h"

namespace py_ints {
// Auxiliary functions for Gaussian integrals
double compute_nuclear_repulsion(Basis* basis0, Basis* basis1);
// currently not used, but might be needed later on
double compute_external_charges(ExternalCharges* ext_charges);
// compute the interaction between the nuclei and external charges
double compute_nuclear_pc(Basis* basis0, ExternalCharges* ext_charges);
}  // namespace py_ints
#endif  // PYBEST_CORE_EXTERNAL_H_"
