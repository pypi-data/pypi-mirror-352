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

#ifndef PYBEST_CORE_EMULTIPOLE_H_
#define PYBEST_CORE_EMULTIPOLE_H_

#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>

#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <vector>

#include "basis.h"

namespace nb = nanobind;

// Libint Gaussian integrals library
#include <libint2.hpp>
#if !LIBINT2_CONSTEXPR_STATICS
#include <libint2/statics_definition.h>
#endif

#if LIBINT2_REALTYPE != double
#error LibInt must be compiled with REALTYPE = double.
#endif

#if LIBINT2_SUPPORT_ERI == 0
#error LibInt must be compiled with support for electron repulsion integrals.
#endif

#ifndef LIBINT2_MAX_AM
#define LIBINT2_MAX_AM LIBINT2_MAX_AM_ERI
#endif
#if LIBINT2_MAX_AM < MAX_SHELL_TYPE
#error LibInt must be compiled with MAX_AM >= MAX_SHELL_TYPE.
#endif

namespace py_ints {
// Auxiliary functions for Gaussian integrals
void compute_dipole(Basis *basis0, Basis *basis1,
                    nb::ndarray<nb::numpy, double> &olp,
                    nb::ndarray<nb::numpy, double> &mux,
                    nb::ndarray<nb::numpy, double> &muy,
                    nb::ndarray<nb::numpy, double> &muz, double x, double y,
                    double z);
void compute_quadrupole(
    Basis *basis0, Basis *basis1, nb::ndarray<nb::numpy, double> &olp,
    nb::ndarray<nb::numpy, double> &mux, nb::ndarray<nb::numpy, double> &muy,
    nb::ndarray<nb::numpy, double> &muz, nb::ndarray<nb::numpy, double> &muxx,
    nb::ndarray<nb::numpy, double> &muxy, nb::ndarray<nb::numpy, double> &muxz,
    nb::ndarray<nb::numpy, double> &muyy, nb::ndarray<nb::numpy, double> &muyz,
    nb::ndarray<nb::numpy, double> &muzz, double x, double y, double z);

}  // namespace py_ints
#endif  // PYBEST_CORE_EMULTIPOLE_H_"
