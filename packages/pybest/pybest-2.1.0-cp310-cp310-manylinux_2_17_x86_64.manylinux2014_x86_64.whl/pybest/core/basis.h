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

// UPDATELIBDOCTITLE: Gaussian basis set classes

#ifndef PYBEST_CORE_BASIS_H_
#define PYBEST_CORE_BASIS_H_

#include <string>

// Libint Gaussian integrals library
#include <libint2.hpp>
#if !LIBINT2_CONSTEXPR_STATICS
#include <libint2/statics_definition.h>
#endif

#include <nanobind/eigen/dense.h>
#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>

#include <Eigen/Core>

namespace nb = nanobind;

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

#include <libint2/lcao/molden.h>

#include <vector>

class Basis {
 public:
  const std::string basisname;
  const std::string molfile;
  const std::string dirname;
  std::size_t nbasis;
  std::size_t nshell;
  std::size_t ncenter;
  // we need to store this information to ensure the functionality of
  // some pybest modules
  std::vector<long> nprim;  // # NOLINT
  std::vector<double> alpha;
  std::vector<double> contraction;
  std::vector<long> shell2atom;      // # NOLINT
  std::vector<int> shell_types;      // # NOLINT
  std::vector<long> atomic_numbers;  // # NOLINT
  std::vector<std::vector<double>> coordinates;
  Basis(const std::string &basisname, const std::string &molfile,
        const std::string &dirname);
  Basis(const std::string &molfile, std::vector<long> nprims,  // # NOLINT
        std::vector<long> center, std::vector<int> l,          // # NOLINT
        std::vector<double> alphas, std::vector<double> contr);
  // used in from_coordinates() which is exported to python
  Basis(std::vector<libint2::Atom> atoms_,
        std::vector<long> nprims,                      // # NOLINT
        std::vector<long> center, std::vector<int> l,  // # NOLINT
        std::vector<double> alphas, std::vector<double> contr);
  Basis(const Basis &rhs) = default;
  ~Basis() = default;

  // Members:
  libint2::BasisSet obs;
  std::vector<libint2::Atom> atoms;

  // Getters:
  const std::string &getBasisname() const;
  const std::string &getMolfile() const;
  const std::string &getDirname() const;
  std::size_t getNBasis();
  std::size_t getNShell();
  std::size_t getNCenter();
  std::vector<long> getNPrim();  // # NOLINT
  std::vector<double> getAlpha();
  std::vector<double> getContraction();
  std::vector<long> getShell2atom();  // # NOLINT
  std::vector<int> getShellTypes();
  std::vector<long> getAtomicNumbers();  // # NOLINT
  std::vector<std::vector<double>> getCoordinates();

  // More general functions accessible through python
  void print_basis_info();
  void print_atomic_info();
  std::size_t get_nbasis_in_shell(std::size_t s);
  void renormalize_contr(int l, std::vector<std::size_t> n, double factor);
  double get_renorm(std::size_t l, std::size_t s, std::size_t n);
  double get_renorm(std::size_t l, std::size_t s, std::size_t na,
                    std::vector<std::size_t> n);
  void dump_molden(const char *filename, const Eigen::VectorXd coeffs,
                   const Eigen::VectorXd occs, const Eigen::VectorXd energies,
                   const std::vector<bool> &spin, double eps);
  void dump_cube_orbital(const char *filename,
                         const nb::DRef<Eigen::VectorXd> coeffs,
                         const nb::DRef<Eigen::VectorXd> grid_x,
                         const nb::DRef<Eigen::VectorXd> grid_y,
                         const nb::DRef<Eigen::VectorXd> grid_z);
  // all remaining functions only visible to C++ code
  void pure2cart(int l);
  void cart2pure(int l);
  void set_dummy_atom(int i);
  std::size_t get_shell_size(int shell_type);
  void assign_basis_set(std::vector<long> nprims,  // # NOLINT
                        std::vector<long> center,  // # NOLINT
                        std::vector<int> l, std::vector<double> alphas,
                        std::vector<double> contr);
};
namespace py_libint_utils {
Basis from_coordinates(std::vector<long> atomic_numbers,  // # NOLINT
                       std::vector<std::vector<double>> coordinates,
                       std::vector<long> primitives,  // # NOLINT
                       std::vector<long> shell2atom,  // # NOLINT
                       std::vector<int> shell_types, std::vector<double> alphas,
                       std::vector<double> contraction);
}
/**
 * Containers encoding the x, y, z exponents for a given shell using
 * the default order of basis functions in PyBEST
 */

const std::vector<std::vector<std::size_t>> s_xyz = {
    {0, 0, 0},
};

const std::vector<std::vector<std::size_t>> p_xyz{
    {1, 0, 0},
    {0, 1, 0},
    {0, 0, 1},
};

const std::vector<std::vector<std::size_t>> d_xyz = {
    {2, 0, 0}, {1, 1, 0}, {1, 0, 1}, {0, 2, 0}, {0, 1, 1}, {0, 0, 2},
};

const std::vector<std::vector<std::size_t>> f_xyz = {
    {3, 0, 0}, {2, 1, 0}, {2, 0, 1}, {1, 2, 0}, {1, 1, 1},
    {1, 0, 2}, {0, 3, 0}, {0, 2, 1}, {0, 1, 2}, {0, 0, 3},
};

const std::vector<std::vector<std::size_t>> g_xyz = {
    {4, 0, 0}, {3, 1, 0}, {3, 0, 1}, {2, 2, 0}, {2, 1, 1},
    {2, 0, 2}, {1, 3, 0}, {1, 2, 1}, {1, 1, 2}, {1, 0, 3},
    {0, 4, 0}, {0, 3, 1}, {0, 2, 2}, {0, 1, 3}, {0, 0, 4},
};

const std::vector<std::vector<std::size_t>> h_xyz = {
    {5, 0, 0}, {4, 1, 0}, {4, 0, 1}, {3, 2, 0}, {3, 1, 1}, {3, 0, 2}, {2, 3, 0},
    {2, 2, 1}, {2, 1, 2}, {2, 0, 3}, {1, 4, 0}, {1, 3, 1}, {1, 2, 2}, {1, 1, 3},
    {1, 0, 4}, {0, 5, 0}, {0, 4, 1}, {0, 3, 2}, {0, 2, 3}, {0, 1, 4}, {0, 0, 5},
};

const std::vector<std::vector<std::size_t>> i_xyz = {
    {6, 0, 0}, {5, 1, 0}, {5, 0, 1}, {4, 2, 0}, {4, 1, 1}, {4, 0, 2}, {3, 3, 0},
    {3, 2, 1}, {3, 1, 2}, {3, 0, 3}, {2, 4, 0}, {2, 3, 1}, {2, 2, 2}, {2, 1, 3},
    {2, 0, 4}, {1, 5, 0}, {1, 4, 1}, {1, 3, 2}, {1, 2, 3}, {1, 1, 4}, {1, 0, 5},
    {0, 6, 0}, {0, 5, 1}, {0, 4, 2}, {0, 3, 3}, {0, 2, 4}, {0, 1, 5}, {0, 0, 6},
};

const std::vector<std::vector<std::size_t>> k_xyz{
    {7, 0, 0}, {6, 1, 0}, {6, 0, 1}, {5, 2, 0}, {5, 1, 1}, {5, 0, 2},
    {4, 3, 0}, {4, 2, 1}, {4, 1, 2}, {4, 0, 3}, {3, 4, 0}, {3, 3, 1},
    {3, 2, 2}, {3, 1, 3}, {3, 0, 4}, {2, 5, 0}, {2, 4, 1}, {2, 3, 2},
    {2, 2, 3}, {2, 1, 4}, {2, 0, 5}, {1, 6, 0}, {1, 5, 1}, {1, 4, 2},
    {1, 3, 3}, {1, 2, 4}, {1, 1, 5}, {1, 0, 6}, {0, 7, 0}, {0, 6, 1},
    {0, 5, 2}, {0, 4, 3}, {0, 3, 4}, {0, 2, 5}, {0, 1, 6}, {0, 0, 7},
};

/**
 * Containers containing cartesian exponents for all shells supported in PyBEST
 */

const std::vector<std::vector<std::vector<std::size_t>>> shell_exp = {
    s_xyz, p_xyz, d_xyz, f_xyz, g_xyz, h_xyz, i_xyz, k_xyz};

#endif  // PYBEST_CORE_BASIS_H_
