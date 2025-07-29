# PyBEST: Pythonic Black-box Electronic Structure Tool
# Copyright (C) 2016-- The PyBEST Development Team
#
# This file is part of PyBEST.
#
# PyBEST is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# PyBEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
# --
"""
Pytest test running.
This module implements the ``test()`` function for Pybest modules. The usual
boiler plate for doing that is to put the following in the module
``__init__.py`` file::
    from pybest._pytesttester import PytestTester
    test = PytestTester(__name__)
    del PytestTester
Warnings filtering and other runtime settings should be dealt with in the
``pytest.ini`` file in the Pybest repo root. The behavior of the test depends on
whether or not that file is found as follows:
* ``pytest.ini`` is present (develop mode)
    All warnings except those explicitly filtered out are raised as error.
* ``pytest.ini`` is absent (release mode)
    DeprecationWarnings and PendingDeprecationWarnings are ignored, other
    warnings are passed through.
In practice, tests run from the pybest repo are run in develop mode. That
includes the standard ``python runtests.py`` invocation.
This module is imported by every pybest subpackage, so lies at the top level to
simplify circular import issues. For the same reason, it contains no pybest
imports at module scope, instead importing pybest within function calls.

It is heavily inspired by a NumPy Pytest runner.
see: https://numpy.org/doc/stable/reference/testing.html#running-tests-from-inside-python
"""

import os
import sys

__all__ = ["PytestTester"]


class PytestTester:
    """
    Pytest test runner.
    A test function is typically added to a package's __init__.py like so::
      from pybest._pytesttester import PytestTester
      test = PytestTester(__name__).test
      del PytestTester
    Calling this test function finds and runs all tests associated with the
    module and all its sub-modules.
    Attributes
    ----------
    module_name : str
        Full path to the package to test.
    Parameters
    ----------
    module_name : module name
        The name of the module to test.
    Notes
    -----
    Unlike the previous ``nose``-based implementation, this class is not
    publicly exposed as it performs some ``pybest``-specific warning
    suppression.
    """

    __test__ = False

    def __init__(self, module_name):
        self.module_name = module_name

    def __call__(
        self,
        label="fast",
        verbose=1,
        extra_argv=None,
        doctests=False,
        coverage=False,
        xdist=False,
        durations: int = 20,
        tests=None,
    ):
        """
        Run tests for module using pytest.
        Parameters
        ----------
        label : {'fast', 'full'}, optional
            Identifies the tests to run. When set to 'fast', tests decorated
            with `pytest.mark.slow` are skipped, when 'full', the slow marker
            is ignored.
        verbose : int, optional
            Verbosity value for test outputs, in the range 1-3. Default is 1.
        extra_argv : list, optional
            List with any extra arguments to pass to pytests.
        doctests : bool, optional
            .. note:: Not supported
        coverage : bool, optional
            If True, report coverage of pybest code. Default is False.
            Requires installation of (pip) pytest-cov.
        durations : int, optional
            If < 0, do nothing, If 0, report time of all tests, if > 0,
            report the time of the slowest `timer` tests. Default is -1.
        tests : test or list of tests
            Tests to be executed with pytest '--pyargs'
        Returns
        -------
        result : bool
            Return True on success, false otherwise.
        Notes
        -----
        Each pybest module exposes `test` in its namespace to run all tests for
        it. For example, to run all tests for pybest.cc:
        >>> pybest.cc.test() #doctest: +SKIP
        Examples
        --------
        >>> result = pybest.cc.test() #doctest: +SKIP
        ...
        1023 passed, 2 skipped, 6 deselected, 1 xfailed in 10.39 seconds
        >>> result
        True
        """
        import pytest

        module = sys.modules[self.module_name]
        module_path = os.path.abspath(module.__path__[0])

        # setup the pytest arguments
        pytest_args = ["-l"]

        # offset verbosity. The "-q" cancels a "-v".
        pytest_args += ["-q"]

        # Filter out annoying import messages. Want these in both develop and
        # release mode.
        pytest_args += [
            "-W ignore:Not importing directory",
        ]

        if doctests:
            raise ValueError("Doctests not supported")

        if extra_argv:
            pytest_args += list(extra_argv)

        if verbose > 1:
            pytest_args += ["-" + "v" * (verbose - 1)]

        if coverage:
            pytest_args += ["--cov=" + module_path]

        if label == "fast":
            pytest_args += ["-m", "not slow"]

        elif label != "full":
            pytest_args += ["-m", label]

        if durations >= 0:
            pytest_args += [f"--durations={durations}"]

        if tests is None:
            tests = [self.module_name]

        if xdist:
            pytest_args += ["-n", "auto"]

        pytest_args += ["--pyargs", *list(tests)]

        try:
            code = pytest.main(pytest_args)
        except SystemExit as exc:
            code = exc.code

        # exit with captured code
        sys.exit(code)
