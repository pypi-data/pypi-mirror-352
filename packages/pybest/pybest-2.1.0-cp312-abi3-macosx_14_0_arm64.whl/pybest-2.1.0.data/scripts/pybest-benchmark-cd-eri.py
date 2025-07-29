#!python
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
import argparse
import os
import time

import numpy as np

from pybest.gbasis.gobasis import get_gobasis
from pybest.iodata import IOData
from pybest.log import log

# changed to spawn instead fork to re-import modules https://stackoverflow.com/a/25552276/8389830
# multiprocessing.set_start_method('spawn')

log.level = 0

default_geometry = """
3
# Test molecule
O 	0.0000 	 0.0000  0.1197
H 	0.0000 	 0.7616 -0.4786
H 	0.0000 	-0.7616 -0.4786
""".strip()


def parse_args():
    parser = argparse.ArgumentParser(
        prog="pybest-benchmark-cd.py",
        description="Benchmarks generation of CD-ERI",
    )
    parser.add_argument(
        "--geo", help=".xyz file with given geometry", default=None
    )
    parser.add_argument(
        "--basis", help="given basis set", type=str, default="cc-pvdz"
    )
    parser.add_argument(
        "--nthreads", help="number of threads", type=int, default=1
    )
    parser.add_argument(
        "--cd-thresh", help="value of CD_THRESH", type=float, default=1e-6
    )
    parser.add_argument(
        "--ntries", help="number of tries for statistics", type=int, default=5
    )
    parser.add_argument(
        "--force-avx", help="sets MKL_DEBUG_CPU_TYPE=5", action="store_true"
    )
    parser.add_argument(
        "--force-gnu", help="sets MKL_THREADING_LAYER=GNU", action="store_true"
    )
    parser.add_argument(
        "--disable-thread-control",
        help="switches of setting thread enviroment variables",
        action="store_true",
    )
    return parser.parse_args()


def set_threads(nthreads=1):
    """Sets OMP & MKL num_threads runtime flags

    Keyword Arguments:
        nthreads {int} -- [description] (default: {1})
    """
    os.environ["OMP_NUM_THREADS"] = str(nthreads)
    os.environ["MKL_NUM_THREADS"] = str(nthreads)


def set_avx2_mkl():
    """Forces MKL to use avx codepaths"""
    os.environ["MKL_DEBUG_CPU_TYPE"] = "5"


def set_gnu_threading_layer():
    """Sets MKL threading layer to gnu"""
    os.environ["MKL_THREADING_LAYER"] = "GNU"


class SingleTimings:
    def __init__(self, nthreads=None, time=None, nbasis=None, mol_name=None):
        self.nthreads = nthreads
        self.time = time
        self.nbasis = nbasis
        self.mol_name = mol_name

    @classmethod
    def from_tuple(cls, tuple_):
        nbasis, nthreads, time = tuple_
        return cls(nbasis=nbasis, nthreads=nthreads, time=time)

    def __repr__(self):
        """String representation of the object"""
        return f"{self.nbasis:<7} {self.nthreads:<8} {self.time:<.3f}"


class Timings:
    def __init__(self, list_of_timings):
        self.set_timings(list_of_timings)

    def set_timings(self, timings):
        self.timings = timings

    def __repr__(self):
        """String representation of the object"""
        self.header = "NBASIS  THREADS  TIME [seconds]"
        self.timings_str = "\n".join(
            f"{time_}" for time_ in map(str, self.timings)
        )
        nl = "\n"
        return f"{self.header}{nl}{self.timings_str}"

    def print_summary(self):
        print(self)


class RunStatistics:
    def __init__(self, *args, **kwargs):
        self.runs = []

    def get_avg_time(self):
        return np.average(self.runs)

    def clear_runs(self):
        self.runs = []


def compute_cholesky_decomposed_eri(
    basis, precision, nthreads, disable_thread_control=False
):
    # NOTE: FML c-extensions reload is broken and won't be fixed, need to wrap everything in subprocess calls
    # REF: https://bugs.python.org/issue1144263

    # sets OMP_NUM_THREADS & MKL_NUM_THREADS
    if not disable_thread_control:
        set_threads(nthreads=nthreads)
    import pybest.gbasis.cholesky_eri as basis_module

    basis_module.compute_cholesky_eri(basis, precision)


def run_nthreads(
    basis, nthreads=1, precision=1e-12, ntries=1, disable_thread_control=False
):
    stats = RunStatistics()

    for _ in range(ntries):
        start = time.time()
        # fork process to properly set num_threads in c-extension
        # p = Process(
        #    target=compute_cholesky_decomposed_eri,
        #    args=(basis, precision, nthreads),
        #    kwargs={"disable_thread_control": disable_thread_control},
        # )
        # p.start()
        # p.join()
        compute_cholesky_decomposed_eri(basis, precision, nthreads)
        end = time.time()
        stats.runs.append(end - start)

    avg_time = stats.get_avg_time()
    stats.clear_runs()
    return avg_time


def main():
    args = parse_args()
    print(args)
    if args.geo is None:
        mol = IOData.from_str(default_geometry)
    else:
        mol = IOData.from_file(args.geo)

    nthreads = args.nthreads
    ntries = args.ntries

    # forces to use avx on non-intel CPUs (i.e. AMD zen architecture)
    if args.force_avx:
        set_avx2_mkl()

    # sets GNU threading layer for MKL
    if args.force_gnu:
        set_gnu_threading_layer()

    basis = get_gobasis(args.basis, mol)
    nbasis = basis.nbasis
    cd_thresh = args.cd_thresh

    group_results = []
    for threads_no in range(1, nthreads + 1):
        avg_time = run_nthreads(
            basis,
            nthreads=threads_no,
            ntries=ntries,
            precision=cd_thresh,
            disable_thread_control=args.disable_thread_control,
        )
        timing = SingleTimings.from_tuple((nbasis, threads_no, avg_time))
        group_results.append(timing)

    obj = Timings(group_results)
    obj.print_summary()


if __name__ == "__main__":
    main()
