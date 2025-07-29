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
import pathlib

import pytest

import pybest.gbasis.cholesky_eri as pybest_cholesky
from pybest import filemanager
from pybest.linalg import CholeskyLinalgFactory, DenseLinalgFactory


def pytest_addoption(parser):
    """Pytest hook for adding custom run options"""
    parser.addoption(
        "--all", action="store_true", default=False, help="run all tests"
    )
    parser.addoption(
        "--slow",
        action="store_true",
        default=False,
        help="run **ONLY** slow tests",
    )
    parser.addoption(
        "--loglevel", action="store", default="0", help="set global log level"
    )


# FIXME: move configure to pytest.ini, as those won't be registered until run on pybest/conftest.py directly
# i.e. `python3 -m pytest --marks` won't show anythin, when run from git root dir
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line("markers", "slow: mark test as slow to run")
    loglevel = int(config.getoption("--loglevel"))
    from pybest.log import log

    log.level = loglevel


def pytest_collection_modifyitems(config, items):
    """Modifies collection to honor custom options"""
    # don't skip anything
    if config.getoption("--all"):
        return

    # run only slow tests
    if config.getoption("--slow"):
        # mark any test without @pytest.mark.slow with fast
        skip_fast = pytest.mark.skip(reason="--slow option has been selected")
        for item in items:
            if "slow" not in item.keywords:
                item.add_marker(skip_fast)
        return

    # otherwise run everything but slow
    skip_slow = pytest.mark.skip(reason="need --all or --slow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


def pytest_sessionfinish(session, exitstatus):
    """Register session flush
    removes temporary directory if exists
    """
    import shutil

    pybest_tmp = filemanager.temp_dir
    pybest_res = filemanager.result_dir

    if pybest_tmp.exists():
        shutil.rmtree(pybest_tmp)

    if pybest_res.exists():
        shutil.rmtree(pybest_res)

    # get rid of pybest-results as it is by default created by the filemanager
    if pathlib.Path("pybest-results").exists():
        shutil.rmtree(pathlib.Path("pybest-results"))


@pytest.fixture(autouse=True)
def filemanager_resultpath(tmp_path):
    """Sets result dir to tmp_path dir"""
    filemanager.result_dir = tmp_path


@pytest.fixture(autouse=True)
def filemanager_tmppath(tmp_path):
    """Sets temporary dir to tmp_path dir"""
    filemanager.temp_dir = tmp_path


@pytest.fixture
def tmp_dir(tmp_path) -> pathlib.Path:
    directory = tmp_path / "tmp_dir"
    directory.mkdir()
    return directory


if pybest_cholesky.PYBEST_CHOLESKY_ENABLED:
    linalg_set = [DenseLinalgFactory, CholeskyLinalgFactory]
else:
    linalg_set = [DenseLinalgFactory]


@pytest.fixture(params=linalg_set, name="linalg")
def linalg_factory(request):
    """Returns the available linear algebra"""
    return request.param


if pybest_cholesky.PYBEST_CHOLESKY_ENABLED:
    linalg_set_slow = [
        DenseLinalgFactory,
        pytest.param(CholeskyLinalgFactory, marks=pytest.mark.slow),
    ]
else:
    linalg_set_slow = [DenseLinalgFactory]


@pytest.fixture(params=linalg_set_slow, name="linalg_slow")
def linalg_factory_slow(request):
    """Return the available linear algebra with CholeskyLinalgFactory marked as slow"""
    return request.param
