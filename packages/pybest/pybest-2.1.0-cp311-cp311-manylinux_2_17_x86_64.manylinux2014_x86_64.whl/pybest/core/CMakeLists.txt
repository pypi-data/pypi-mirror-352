cmake_minimum_required(VERSION 3.27)

cmake_policy(SET CMP0144 OLD)
# NOTE: C in language is required, for MKL config to work
# it has CMAKE_C_COMPILER_ID based check, and it's set to ""
# if we don't specify C here, we cannot use gnu_threads
project(pybest-core
  LANGUAGES CXX C
)

# Taken from: https://github.com/jarro2783/cxxopts/blob/v3.1.1/CMakeLists.txt#L36
# https://stackoverflow.com/a/76528304
# Must include after the project call due to GNUInstallDirs requiring a language to be enabled (IE. CXX)
# it provides CORRECT $CMAKE_INSTALL_LIBDIR and $CMAKE_INSTALL_INCLUDEDIR
include(GNUInstallDirs)

# OPTIONS
option(USE_MKL "Should force use MKL as BLAS provider" OFF)
option(USE_OPENBLAS "Should force use OpenBLAS as BLAS provider" OFF)
option(USE_OPENBLAS_PC "Should use OpenBLAS from pkg-config" OFF)
option(PYBEST_ENABLE_CHOLESKY "Should compile with Libchol interface" OFF)
option(PYBEST_ENABLE_PVP "Should compile with PVP integrals" ON)
option(PYBEST_FORCE_RPATH "Should force RPATH to be embedded into .so" ON)


set(PYBEST_LIBINT2_ROOT "" CACHE STRING "Base dir for Libint2 detection logic")
message(STATUS "GNU libdir " ${CMAKE_INSTALL_LIBDIR})
message(STATUS "GNU includedir " ${CMAKE_INSTALL_INCLUDEDIR})

find_package(Python 3.9 REQUIRED COMPONENTS Interpreter Development.Module OPTIONAL_COMPONENTS Development.SABIModule)
find_package(Eigen3 3.3.7 CONFIG REQUIRED)

# NOTE: It's to correctly hint libint2 installation, as libdir can be lib or lib64
find_package(Libint2 2.9.0 CONFIG REQUIRED
  PATHS ${PYBEST_LIBINT2_ROOT}/${CMAKE_INSTALL_LIBDIR}/cmake/libint2
  PATHS ${PYBEST_LIBINT2_ROOT}/lib/cmake/libint2
)

# NOTE: this way rpath is not removed after install, which is desired for python c-extensions
# as all .so are processed by auditwheel/delocate anyway!
# NOTE: https://cmake.org/cmake/help/latest/variable/CMAKE_INSTALL_RPATH_USE_LINK_PATH.html
# NOTE: https://stackoverflow.com/a/32470070
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH $<$<BOOL:${PYBEST_FORCE_RPATH}>:True>)
set(PYBEST_LIBCHOL_ROOT "" CACHE STRING "Base dir for Libchol detection logic")

if (NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build." FORCE)
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

# Detect the installed nanobind package and import it into CMake
execute_process(
  COMMAND "${Python_EXECUTABLE}" -m nanobind --cmake_dir
  OUTPUT_STRIP_TRAILING_WHITESPACE OUTPUT_VARIABLE NB_DIR)
list(APPEND CMAKE_PREFIX_PATH "${NB_DIR}")
find_package(nanobind CONFIG REQUIRED)

nanobind_add_module(core
  STABLE_ABI LTO NB_STATIC
  core.cpp
  sapt_utils.cpp
  basis.cpp
  libint_utils.cpp
  static_embedding.cpp
  external_charges.cpp
  external.cpp
  overlap.cpp
  kin.cpp
  nuclear.cpp
  pvp.cpp
  emultipole.cpp
  point_charges.cpp
  eri.cpp
  cholesky_eri.cpp
)

if(PYBEST_ENABLE_PVP)
  target_compile_definitions(core PUBLIC PYBEST_ENABLE_PVP)
endif(PYBEST_ENABLE_PVP)
unset(PYBEST_ENABLE_PVP CACHE)

if(PYBEST_ENABLE_CHOLESKY)
  find_path(libchol_INCLUDE_DIR NAMES "chol.hpp"
    PATHS ${PYBEST_LIBCHOL_ROOT}/include
  )
  # NOTE: when libchol starts using GNUInstallDirs
  # this will have to change
  find_library(libchol_LIBRARY NAMES
    "chol" PATHS ${PYBEST_LIBCHOL_ROOT}/lib
)
  target_compile_definitions(core PUBLIC PYBEST_ENABLE_CHOLESKY)
  message(STATUS "Libchol include headers: ${libchol_INCLUDE_DIR}")
  message(STATUS "Libchol library: ${libchol_LIBRARY}")
  # NOTE: a temporary hack
  target_include_directories(core PUBLIC ${libchol_INCLUDE_DIR})
  target_link_libraries(core PUBLIC ${libchol_LIBRARY})
else()
  message(WARNING "Cholesky ERI was disabled at build time!")
endif()
unset(PYBEST_ENABLE_CHOLESKY CACHE)

# add headers to OBJECT targets
if(TARGET Libint2::cxx AND TARGET Eigen3::Eigen)
  get_target_property(_libint2_includes Libint2::cxx INTERFACE_INCLUDE_DIRECTORIES)
  get_target_property(_eigen3_includes Eigen3::Eigen INTERFACE_INCLUDE_DIRECTORIES)
  # NOTE: a workaround for Libint2::cxx target not setting INTERFACE_INCLUDE_DIRECTORIES
  if(DEFINED _libint2_includes AND _libint2_includes STREQUAL "_libint2_includes-NOTFOUND")
    get_target_property(_libint2_includes Libint2::int2 INTERFACE_INCLUDE_DIRECTORIES)
  endif()
  message(STATUS "Libint2 include headers ${_libint2_includes}")
  message(STATUS "Eigen3 include headers ${_eigen3_includes}")
  target_include_directories(core PRIVATE "${_libint2_includes}" "${_eigen3_includes}")
else()
  message(FATAL_ERROR "Could not find Libint2 configuration correctly!")
endif()

# link libint2
if(TARGET Libint2::cxx AND TARGET Eigen3::Eigen)
  target_link_libraries(core PUBLIC Libint2::cxx Eigen3::Eigen)
else()
  message(FATAL_ERROR "Could not find Libint2 configuration correctly!")
endif()

# NOTE: DESTIATION . combined with cmake_install_dir set to src.pybest.core in setup.py
# allows installing .so directly into gbasis package
install(TARGETS core LIBRARY DESTINATION ".")
