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
"""Optimization methods

DIIS: A simple diis implementation
"""

import numpy as np

from pybest.exceptions import ArgumentError
from pybest.log import timer

from .linear_equations import solve_hermitian

__all__ = [
    "DIIS",
]


class DIIS:
    def __init__(self, lf, nvec=9, start=0):
        """DIIS method for general error vectors amplitudes.

        ** Arguments **


        ** Returns **


        """
        self.lf = lf
        # length of diis vectors
        self.nvec = nvec
        # first iteration to start (either energy threshold or iteration)
        self.start = start
        # the error vector
        self.dtk = []
        # amplitude vectors
        self.tk = []
        # the weights
        self.w = [1.0]
        # diis running or not
        self.status = False

    @property
    def lf(self):
        """The linalg factory"""
        return self._lf

    @lf.setter
    def lf(self, new):
        self._lf = new

    @property
    def nvec(self):
        return self._nvec

    @nvec.setter
    def nvec(self, new):
        self._nvec = new

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, new):
        self._start = new

    @property
    def dtk(self):
        return self._dtk

    @dtk.setter
    def dtk(self, new):
        if new:
            self._dtk.append(new)
        else:
            self._dtk = []

    @dtk.deleter
    def dtk(self):
        del self._dtk[:]
        self._dtk = []

    @property
    def tk(self):
        return self._tk

    @tk.setter
    def tk(self, new):
        if new:
            self._tk.append(new)
        else:
            self._tk = []

    @tk.deleter
    def tk(self):
        del self._tk[:]
        self._tk = []

    @property
    def w(self):
        return self._w

    @w.setter
    def w(self, new):
        # overwrite by default
        self._w = []
        for arg in new:
            self._w.append(arg)

    @w.deleter
    def w(self):
        del self._w[:]
        self._w = []

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new):
        self._status = new

    def update_diis(self):
        if len(self.dtk) > self.nvec:
            # delete element explicitly
            del self._dtk[0]
        if len(self.tk) > self.nvec:
            # delete element explicitly
            del self._tk[0]

    def reset(self, deltatk, reset_):
        # reset diis if necessary
        if len(self.tk) > 1 and reset_:
            # Do DIIS again:
            tkn = self.tk[-2].copy()
            tkn.iadd(deltatk)
            # delete all DIIS information
            del self.tk
            del self.dtk
            # Update vector and error vector for first iteration
            self.tk = tkn
            self.dtk = deltatk
            del self.w
            self.w = [1.0]
            self.status = False

    def get_matrix(self):
        """Return Lagragian matrix that has to be minimized"""
        diis = self.lf.create_two_index(len(self.dtk) + 1)
        for v1 in range(len(self.dtk)):
            for v2 in range(v1, len(self.dtk)):
                v12 = self.dtk[v1].dot(self.dtk[v2])
                diis.set_element(v1, v2, v12, 2)
            diis.set_element(v1, -1, 1, 2)

        return diis

    def solve(self, diis):
        """Solve for weights of new solution vector"""
        r = np.zeros(len(self.dtk) + 1)
        r[-1] = 1

        w, _ = solve_hermitian(diis.array, r)
        del self.w
        self.w = w[: len(self.dtk)]

    def get_new_vector(self):
        """Calculates average solution vector using previous vectors
        and diis weights
        """
        # get current approximation as tkn+1 = tkn + dtk:
        out = self.tk[-1].copy()
        out.iadd(self.dtk[-1])
        # calculate tknew = sum_i c_i tk_i
        out.iscale(self.w[-1])
        for i in range(len(self.w) - 1):
            out.iadd(self.tk[i], factor=self.w[i])
        self.tk = out
        self.status = True

    def check_status(self, iter_, de):
        """Check status of DIIS algorithm"""
        if self.nvec == 1:
            self.status = False
        elif isinstance(self.start, int):
            if iter_ < self.start:
                del self.tk
                del self.dtk
                self.status = False
            elif iter_ > 1:
                self.status = True
            else:
                del self.tk
                del self.dtk
                self.status = False
        elif isinstance(self.start, float):
            if abs(de) > self.start and not self.status:
                del self.tk
                del self.dtk
                self.status = False
            elif iter_ > 1:
                self.status = True
        else:
            raise ArgumentError("Do not know what to do with start option")

    @timer.with_section("DIIS")
    def __call__(self, tk, deltatk, iter_, de):
        """The DIIS method."""
        self.check_status(iter_, de)
        self.dtk = deltatk
        self.update_diis()

        # solve for interpolation weights if required
        if self.status and len(self.dtk) > 1:
            B = self.get_matrix()
            self.solve(B)
            self.get_new_vector()
        # If only one solution vector present, calculate solution vector as t+dt
        else:
            out = tk.copy()
            out.iadd(deltatk)
            self.tk = out
