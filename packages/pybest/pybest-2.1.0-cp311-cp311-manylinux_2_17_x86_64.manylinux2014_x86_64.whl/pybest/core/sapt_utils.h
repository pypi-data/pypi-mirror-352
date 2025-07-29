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

#ifndef PYBEST_CORE_SAPT_UTILS_H_
#define PYBEST_CORE_SAPT_UTILS_H_

#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>

namespace nb = nanobind;

namespace py_sapt_core {

void get_sapt_amplitudes(nb::ndarray<nb::numpy, double> t_rsab_npy,
                         nb::ndarray<nb::numpy, double> t_ra_npy,
                         nb::ndarray<nb::numpy, double> t_sb_npy,
                         nb::ndarray<nb::numpy, double> en_occ_a_npy,
                         nb::ndarray<nb::numpy, double> en_virt_a_npy,
                         nb::ndarray<nb::numpy, double> en_occ_b_npy,
                         nb::ndarray<nb::numpy, double> en_virt_b_npy,
                         std::size_t nocc_a, std::size_t nocc_b,
                         std::size_t nvirt_a, std::size_t nvirt_b);
}  // namespace py_sapt_core
#endif  // PYBEST_CORE_SAPT_UTILS_H_
