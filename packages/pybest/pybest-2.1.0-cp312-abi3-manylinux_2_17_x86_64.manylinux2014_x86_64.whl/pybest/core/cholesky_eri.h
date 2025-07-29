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

#ifndef PYBEST_CORE_CHOLESKY_ERI_H_
#define PYBEST_CORE_CHOLESKY_ERI_H_

#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>

#include <vector>

#include "basis.h"

namespace nb = nanobind;

#ifndef __has_include
#error __has_include support is required, switch to modern compiler
#endif

#if defined __has_include
#if __has_include("chol.hpp")
#include "chol.hpp"
#define LIBCHOL_AVAILABLE 1
#endif
#endif

namespace py_ints {
nb::ndarray<nb::numpy, double> compute_cholesky_eri(Basis *basis0,
                                                    double cd_threshold,
                                                    size_t cd_beta);
}
#endif  // PYBEST_CORE_CHOLESKY_ERI_H_
