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

#ifndef PYBEST_CORE_EXTERNAL_CHARGES_H_
#define PYBEST_CORE_EXTERNAL_CHARGES_H_

#include <array>
#include <string>
#include <utility>
#include <vector>

class ExternalCharges {
 public:
  const std::string chargefile;
  std::size_t ncharges;
  std::vector<double> charges;
  std::vector<std::vector<double>> coordinates;
  // constructors
  ExternalCharges(std::vector<double> charges, std::vector<double> x,
                  std::vector<double> y, std::vector<double> z);
  ExternalCharges(const ExternalCharges& rhs) = default;
  // destructor
  ~ExternalCharges() = default;

  // Functions to create charge-coordinate pairs
  std::vector<std::pair<double, std::array<double, 3>>> get_charge_pairs();
};

#endif  // PYBEST_CORE_EXTERNAL_CHARGES_H_
