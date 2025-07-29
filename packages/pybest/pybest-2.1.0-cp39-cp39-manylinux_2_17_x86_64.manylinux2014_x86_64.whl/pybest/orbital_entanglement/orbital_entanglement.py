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

# Detailed changelog:
# This module has been originally written and updated by Katharina Boguslawski (see CHANGELOG)
# Its current version contains updates from the PyBEST developer team.
#
# This implementation can also be found in `Horton 2.0.0`.
# However, this file has been updated and debugged. Compatibility with Horton is NOT
# guaranteed.
#
# Detailed changes (see also CHANGELOG):
# 2020-07-01: update class structure and init procedure
# 2020-07-01: make function call more user friendly and black box by passing IOData instance
# 2020-07-01: extend module to general wave functions
# 2020-07-01: update to new python features, including f-strings
# 2020-07-01: use PyBEST standards, including naming convention and filemanager

# FIXME:
# - rename/introduce proper variable names to indicate use of active spaces:
#   e.g., nbasis -> nactbasis, etc.

"""One- and two-orbital entanglement measures

Abbreviations used in this module:

* dm1 = a 1-RDM
* dm2 = a 2-RDM
* dm3 = a 3-RDM
* dm4 = a 4-RDM
* odm1 = one-orbital reduced density matrix
* odm2 = two-orbital reduced density matrix
* soentropy = single-orbital entropy
* toentropy = two-orbital entropy
* mutualinfo = mutual information
"""

import numpy as np

from pybest import filemanager
from pybest.iodata import CheckPoint, IOData
from pybest.log import log
from pybest.utility import check_options, check_type

__all__ = [
    "OrbitalEntanglementRpCCD",
    "OrbitalEntanglementRpCCDLCC",
]


class OrbitalEntanglement:
    """Orbital entanglement and correlation base class"""

    acronym = ""

    def __init__(self, lf, args):
        r"""Base class. Not supposed to be used on its own.

         **Arguments:**

         lf
             Instance of :py:class:`pybest.linalg.dense.dense_linalg_factory.DenseLinalgFactory` or
             :py:class:`pybest.linalg.cholesky.CholeskyLinalgFactory`

         args
             Instance of :py:class:`pybest.io.IOData`. Contains all required
             RDMs.

        **Optional arguments:**

        """
        self._lf = lf
        self._nbasis = lf.default_nbasis - args.ncore
        self._occ_model = args.occ_model
        # The number of core orbitals is stored in the occupation model (om)
        self._ncore = args.occ_model.ncore[0]
        self._odm1 = []
        self._odm2 = []
        self._dim_fock = -1
        self._symbol = []
        self._so_entropy = lf.create_one_index()
        self._to_entropy = lf.create_two_index()
        self._mutual_info = lf.create_two_index()
        self._checkpoint = CheckPoint({})

        log.cite(
            "the implementation of entanglement measures",
            "boguslawski2015a",
            "boguslawski2017b",
        )

    def __call__(self):
        """Dumps single-orbital entropy and orbital-pair mututal information

        see :py:meth:`pybest.orbital_entanglement.orbital_entanglement.OrbitalEntanglement.dump_output`
        for more info
        """
        if log.do_medium:
            log.hline("=")
            log(" ")
            log("Entering orbital entanglement module")
            log(" ")
            log.hline("=")

        #
        # Compute single-orbital entropy and mutual information
        #
        if log.do_medium:
            log("  Computing s(1) and I_ij")
        self.compute_single_orbital_entropy()
        self.compute_two_orbital_entropy()
        self.compute_mutual_information()

        #
        # Update checkpoint for output
        #
        self.checkpoint.update("s_1", self.so_entropy)
        self.checkpoint.update("s_2", self.to_entropy)
        self.checkpoint.update("I_12", self.mutual_info)
        #
        # Dump output to file:
        #
        if log.do_medium:
            log(" ")
            log("  Dumping output files to pybest-results dir")
            log(" ")
            log.hline("=")
        self.dump_output()
        #
        # Return IOData instance
        #
        return self.checkpoint()

    @property
    def lf(self):
        """The LinalgFactory."""
        return self._lf

    @property
    def occ_model(self):
        """The occupation model."""
        return self._occ_model

    @property
    def nbasis(self):
        """The number of basis functions."""
        return self._nbasis

    @property
    def ncore(self):
        """The number of frozen core orbitals."""
        return self._ncore

    @property
    def checkpoint(self):
        """The iodata container that contains all data dump to disk"""
        return self._checkpoint

    @property
    def dm1(self):
        """Some input 1-RDM"""
        return self._dm1

    @dm1.setter
    def dm1(self, new):
        self._dm1 = new

    @property
    def dm2(self):
        """Some input 2-RDM"""
        return self._dm2

    @dm2.setter
    def dm2(self, new):
        self._dm2 = new

    @property
    def dm3(self):
        """Some input 3-RDM"""
        return self._dm3

    @dm3.setter
    def dm3(self, new):
        self._dm3 = new

    @property
    def dm4(self):
        """Some input 4-RDM"""
        return self._dm4

    @dm4.setter
    def dm4(self, new):
        self._dm4 = new

    @property
    def odm1(self):
        """The 1-ORDM"""
        return self._odm1

    @odm1.setter
    def odm1(self, newlist):
        """Append list containing index and one-orbital-reduced density matrix of
        orbital
        """
        if newlist:
            self._odm1.append(newlist)
        else:
            self._odm1 = newlist

    @property
    def odm2(self):
        """The 2-ORDM"""
        return self._odm2

    @odm2.setter
    def odm2(self, newlist):
        """Append list containing indices and two-orbital-reduced density matrix of
        orbital pair
        """
        if newlist:
            self._odm2.append(newlist)
        else:
            self._odm2 = newlist

    @property
    def so_entropy(self):
        """The single-orbital entropy"""
        return self._so_entropy

    @property
    def to_entropy(self):
        """The two-orbital entropy"""
        return self._to_entropy

    @property
    def mutual_info(self):
        """The mutual information"""
        return self._mutual_info

    @property
    def dim_fock(self):
        """Dimension of Fock space"""
        return self._dim_fock

    @property
    def symbol(self):
        """Symbol of state in Fock space"""
        return self._symbol

    def compute_odm1(self, index1):
        """Compute 1-ORDM for orbital index 1"""
        raise NotImplementedError

    def compute_odm2(self, index1, index2):
        """Compute 2-ORDM for orbital-pair index1 and index2"""
        raise NotImplementedError

    @staticmethod
    def calculate_entropy_term(val, select="vonNeumann"):
        """Calculate entropic term

        **Arguments**

        val
             Used to determine entropy

        **Optional arguments:**

        select
             Select entropy function. Default: von Neumann.
        """
        check_options("select", select, "vonNeumann")
        if val > 0.0:
            return np.log(val) * val
        if abs(val) > 1e-6:
            log.warn(
                f"Neglecting negative value {val:2.6f} in entropy function"
            )
        return 0.0

    def compute_single_orbital_entropy(self, select="vonNeumann"):
        """Compute single-orbital entropy for each orbital in the active space.
        Currently, only the von Neumann entropy is supported.

        The 1-ODM is assumed to be diagonalized.

        **Optional arguments:**

        select
             Select entropy function. Default: von Neumann.
        """
        check_options("select", select, "vonNeumann")
        for index in range(self.nbasis):
            self.compute_odm1(index)
        for item in self.odm1:
            mat = item[1]
            term = 0.0
            for ind in range(mat.shape[0]):
                term -= self.calculate_entropy_term(
                    mat.get_element(ind), select
                )
            self.so_entropy.set_element(item[0], term)

    def compute_two_orbital_entropy(self, select="vonNeumann"):
        """Compute two-orbital entropy for each orbital in the active space.
        Currently, only the von Neumann entropy is supported.

        The 1-ODM and 2-ODM are assumed to be diagonalized.

        **Optional arguments:**

        select
             Select entropy function. Default: von Neumann.
        """
        check_options("select", select, "vonNeumann")
        for index1 in range(self.nbasis):
            for index2 in range(self.nbasis):
                if index2 is not index1:
                    self.compute_odm2(index1, index2)
        for item in self.odm2:
            mat = item[2]
            term = 0.0
            for ind in range(mat.shape[0]):
                term -= self.calculate_entropy_term(
                    mat.get_element(ind), select
                )
            self.to_entropy.set_element(item[0], item[1], term, symmetry=1)
        if not self.to_entropy.check_symmetric(1e-5, 1e-6):
            log.warn("Two-orbital entropy not symmetric, symmetrizing")
        self.to_entropy.symmetrize(2)

    def compute_mutual_information(self):
        """Compute mutual information using the single-orbital entropy and the
        two-orbital entropy.

        **Arguments:**

        one_entropy
             Single-orbital entropy.

        two_entropy
             Two-orbital entropy.

        **Optional arguments:**

        """
        self.mutual_info.assign(self.to_entropy)
        self.mutual_info.iadd(self.so_entropy, -1.0)
        self.mutual_info.iadd_t(self.so_entropy, -1.0)
        self.mutual_info.iscale(-1.0)
        self.mutual_info.assign_diagonal(0.0)

        assert self.mutual_info.is_symmetric()

    @staticmethod
    def diagonalize(mat, eigvec=True):
        """Returns eigenvalues of a TwoIndex instance. Only real eigenvalues
        are returned, any imaginary part will be ignored

        **Arguments:**

        mat
             An TwoIndex instance to be diagonalized.
        """
        if eigvec:
            e_value, e_vec = mat.diagonalize(eigvec=eigvec)
        else:
            e_value = mat.diagonalize(eigvec=eigvec)
        #
        # Delete negative eigenvalues
        #
        indices = np.where(np.real(e_value.array) < 0.0)
        # Print warning
        indices_ = np.where(np.real(e_value.array) < -1e-5)[0]
        for ind_ in indices_:
            e_value_ = e_value.get_element(ind_)
            log.warn(
                f"Negative eigenvalue of {e_value_.real: 2.6f} set to 0.0"
            )
        e_value.array[indices] = 0.0

        if eigvec:
            return e_value, e_vec
        return e_value

    def dump_output(self):
        """Dump entanglement output files for postprocessing.
        Output files can be visualized using the
        build_orbital_entanglement_diagrams.sh script, which uses gnuplot.
        """
        #
        # Write single-orbital entropy to file:
        #
        fname = f"s1-{self.acronym.lower()}.dat"
        filename = filemanager.result_path(fname)
        with open(filename, "w") as f:
            for i in range(self.nbasis):
                f.write(
                    f"{(i + 1 + self.ncore):3} {self.so_entropy.get_element(i):>18.14f}\n"
                )
        #
        # Write eigenvalues of 1odm to file:
        #
        fname = f"rho1-{self.acronym.lower()}.dat"
        filename = filemanager.result_path(fname)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.print_rho_one())
            for i in range(self.nbasis):
                s2 = ""
                for j in range(self.dim_fock):
                    s2 += f"{self.odm1[i][1].get_element(j):>10.6f}"
                f.write(f"{(self.odm1[i][0] + 1 + self.ncore):3} {s2}\n")
        #
        # Write mutual information to file:
        #
        fname = f"i12-{self.acronym.lower()}.dat"
        filename = filemanager.result_path(fname)
        with open(filename, "w") as f:
            for i in range(self.nbasis):
                for j in range(i + 1, self.nbasis):  # i+1
                    f.write(
                        f"{(i + 1 + self.ncore):3} {(j + 1 + self.ncore):3} "
                        f"{self.mutual_info.get_element(i, j):>16.12f}\n"
                    )
        #
        # Write eigenvalues of 2odm to file:
        #
        fname = f"rho2-{self.acronym.lower()}.dat"
        filename = filemanager.result_path(fname)
        with open(filename, "w", encoding="utf-8") as f:
            for i in range(len(self.odm2)):
                if self.odm2[i][0] < self.odm2[i][1]:
                    f.write(
                        f"{(self.odm2[i][0] + 1 + self.ncore):3} "
                        f"{(self.odm2[i][1] + 1 + self.ncore):3}"
                    )
                    f.write("\t w2_ij\n")
                    s2 = ""
                    for j in range(self.odm2[1][2].nbasis):
                        s2 += f"{self.odm2[i][2].get_element(j):>10.6f}"
                    f.write(f"{s2}\n")
                    f.write("phi2_ij\n")
                    s2 = ""
                    for k in range(self.odm2[1][2].nbasis):
                        for j in range(self.odm2[1][2].nbasis):
                            s2 += f"{self.odm2[i][3].get_element(k, j):>10.6f}"
                        s2 += f"{self.symbol[k]:>6}\n"
                    f.write(f"{s2}\n")

    @staticmethod
    def print_rho_one():
        """Print header line with states of 1-ORDM"""
        raise NotImplementedError


class OrbitalEntanglementRpCCD(OrbitalEntanglement):
    """Orbital entanglement class for pCCD."""

    acronym = "pCCD"

    def __init__(self, lf, args):
        """
        **Arguments:**

        lf
            Instance of :py:class:`pybest.linalg.dense.dense_linalg_factory.DenseLinalgFactory` or
            :py:class:`pybest.linalg.cholesky.CholeskyLinalgFactory`

        args
            Instance of :py:class:`pybest.iodata.IOData`. Contains all
            required data to perform an orbital entanglement and
            correlation analysis

        """
        check_type("args", args, IOData)

        OrbitalEntanglement.__init__(self, lf, args)

        self._dim_fock = 2
        self._dm1 = args.dm_1
        self._dm2 = args.dm_2
        self._symbol = ["|- ->", "|x x>", "|- x>", "|x ->"]

        log.cite(
            "the implementation of the pCCD-based entanglement measures",
            "boguslawski2016b",
        )

    def compute_odm1(self, index1):
        """Compute ODM for orbital index1.

        **Arguments:**

        index1
             First orbital index.
        """
        odmat = self.lf.create_one_index(2)
        term = self.dm1.get_element(index1)
        odmat.set_element(0, (1 - term))
        odmat.set_element(1, (term))
        self.odm1 = (index1, odmat)

    def compute_odm2(self, index1, index2):
        """Compute 2-ODM for orbital indices 'index1/index2'.

        **Arguments:**

        index1
             First orbital index.

        index2
             Second orbital index.
        """
        dm2_pqpq = self.dm2["pqpq"]
        dm2_ppqq = self.dm2["ppqq"]
        mat = self.lf.create_one_index(4)
        vecs = self.lf.create_two_index(4, 4)
        submat = self.lf.create_two_index(2, 2)
        term = (
            1.0
            - self.dm1.get_element(index1)
            - self.dm1.get_element(index2)
            + dm2_pqpq.get_element(index1, index2)
        )
        # 1,1
        mat.set_element(0, term)
        # 4,4
        mat.set_element(1, dm2_pqpq.get_element(index1, index2))
        # 2,3
        submat.set_element(0, 1, dm2_ppqq.get_element(index2, index1), 1)
        # 3,2
        submat.set_element(1, 0, dm2_ppqq.get_element(index1, index2), 1)
        term = self.dm1.get_element(index2) - dm2_pqpq.get_element(
            index1, index2
        )
        # 2,2
        submat.set_element(0, 0, term, 1)
        term = self.dm1.get_element(index1) - dm2_pqpq.get_element(
            index1, index2
        )
        # 3,3
        submat.set_element(1, 1, term, 1)

        #
        # Diagonalize and assign to results to mat
        #
        sole, solvec = self.diagonalize(submat, eigvec=True)
        mat.set_element(2, sole.get_element(0))
        mat.set_element(3, sole.get_element(1))
        mat.iscale(1 / mat.trace())
        #
        # Assign elements of eigenvectors
        #
        vecs.set_element(0, 0, 1.0, 1)
        vecs.set_element(1, 1, 1.0, 1)
        vecs.set_element(2, 2, solvec.get_element(0, 0), 1)
        vecs.set_element(2, 3, solvec.get_element(0, 1), 1)
        vecs.set_element(3, 2, solvec.get_element(1, 0), 1)
        vecs.set_element(3, 3, solvec.get_element(1, 1), 1)

        self.odm2 = (index1, index2, mat, vecs)

    @staticmethod
    def print_rho_one():
        """Print header line with states of 1-ORDM"""
        return "#index   |->       |x>\n"


class OrbitalEntanglementRpCCDLCC(OrbitalEntanglement):
    """Orbital entanglement class for pCCD-LCC."""

    acronym = "pCCD-LCC"

    def __init__(self, lf, args):
        """
        **Arguments:**

        lf
            Instance of :py:class:`pybest.linalg.dense.dense_linalg_factory.DenseLinalgFactory` or
            :py:class:`pybest.linalg.cholesky.CholeskyLinalgFactory`

        args
            Instance of :py:class:`pybest.iodata.IOData`. Contains all
            required data to perform an orbital entanglement and
            correlation analysis
        """
        check_type("args", args, IOData)

        OrbitalEntanglement.__init__(self, lf, args)

        self._dim_fock = 4
        # Unicode characters
        # \u2191 - upwards arrow
        # \u2193 - downwards arrow
        self._symbol = [
            "|- ->",
            "|- \u2191>",
            "|\u2191 ->",
            "|- \u2193>",
            "|\u2193 ->",
            "|\u2191 \u2191>",
            "|\u2193 \u2193>",
            "|- x>",
            "|\u2191 \u2193>",
            "|\u2193 ↑>",
            "|x ->",
            "|\u2191 x>",
            "|x \u2191>",
            "|\u2193 x>",
            "|x \u2193>",
            "|x x>",
        ]

        self._dm1 = args.dm_1
        self._dm2 = args.dm_2
        self._dm3 = args.dm_3
        self._dm4 = args.dm_4

        log.cite(
            "the implementation of the LCC-based entanglement measures",
            "nowak2021",
        )

    def compute_odm1(self, index1):
        """Compute ODM for orbital index1.

        **Arguments:**

        index1
             First orbital index.
        """
        odmat = self.lf.create_one_index(4)
        lccsd_1dm = self.dm1["pp"].get_element(index1)
        lccsd_2dm = self.dm2["pPPp"].get_element(index1)
        pccd_1dm = self.dm1["pccd_pp"].get_element(index1)

        odmat.set_element(0, (1 - 2 * lccsd_1dm - pccd_1dm + (lccsd_2dm)))
        odmat.set_element(1, (lccsd_1dm) - (lccsd_2dm))
        odmat.set_element(2, (lccsd_1dm) - (lccsd_2dm))
        odmat.set_element(3, pccd_1dm + lccsd_2dm)

        self.odm1 = (index1, odmat)

    def compute_odm2(self, index1, index2):
        """Compute 2-ODM for orbital indices 'index1/index2'.

        **Arguments:**

        index1
             First orbital index.

        index2
             Second orbital index.
        """
        final_result = self.lf.create_one_index(16)
        final_vec = self.lf.create_two_index(16, 16)

        submat1 = self.lf.create_two_index(2, 2)
        submat2 = self.lf.create_two_index(2, 2)
        submat3 = self.lf.create_two_index(4, 4)
        submat4 = self.lf.create_two_index(2, 2)
        submat5 = self.lf.create_two_index(2, 2)
        #
        # pCCD RDM's
        #
        # 1dm
        ptpp = self.dm1["pccd_pp"].get_element(index1)
        ptqq = self.dm1["pccd_pp"].get_element(index2)

        # 2dm
        ptpPQq = self.dm2["pccd_ppqq"].get_element(index1, index2)
        ptqQPp = self.dm2["pccd_ppqq"].get_element(index2, index1)
        ptqPPq = self.dm2["pccd_pqpq"].get_element(index1, index2)

        #
        # LCCSD RDM's
        # 1dm
        tpp = self.dm1["pp"].get_element(index1)
        tqq = self.dm1["pp"].get_element(index2)
        tpq = self.dm1["pq"].get_element(index1, index2)
        tqp = self.dm1["pq"].get_element(index2, index1)

        # 2dm
        tpPPp = self.dm2["pPPp"].get_element(index1)
        tqQQq = self.dm2["pPPp"].get_element(index2)
        tpqqp = self.dm2["pqqp"].get_element(index2, index1)
        tpQQp = self.dm2["pQQp"].get_element(index2, index1)
        tqQQp = self.dm2["qQQp"].get_element(index2, index1)
        tpPPq = self.dm2["qQQp"].get_element(index1, index2)
        tqPPp = self.dm2["qPPp"].get_element(index2, index1)
        tpQQq = self.dm2["qPPp"].get_element(index1, index2)
        tpQPq = self.dm2["pQPq"].get_element(index2, index1)
        tqQPp = self.dm2["qQPp"].get_element(index2, index1)
        tpPQq = self.dm2["qQPp"].get_element(index1, index2)

        # 3dm
        tqpPPpq = self.dm3["qpPPpq"].get_element(index2, index1)
        tpqQQqp = self.dm3["qpPPpq"].get_element(index1, index2)
        tqPQQPp = self.dm3["qPQQPp"].get_element(index2, index1)
        tpQPPQq = self.dm3["qPQQPp"].get_element(index1, index2)

        # 4dm
        tpPqQQqPp = self.dm4["pPqQQqPp"].get_element(index2, index1)

        #
        # Assign to matrix
        # 1
        final_result.set_element(
            0,
            (
                1.0
                - 2 * tpp
                - 2 * tqq
                + tpPPp
                + tqQQq
                + 2 * tpqqp
                + 2 * tpQQp
                - 2 * tpqQQqp
                - 2 * tqpPPpq
                + tpPqQQqPp
                - ptpp
                - ptqq
                + ptqPPq
            ),
        )
        #
        # SUBMAT1
        # 2 (1,1)
        submat1.set_element(
            0,
            0,
            (tqq - tpqqp - tpQQp - tqQQq + 2 * tpqQQqp + tqpPPpq - tpPqQQqPp),
            1,
        )
        # 3 (1,2)
        submat1.set_element(0, 1, (tqp - tqPPp - tqQQp + tqPQQPp), 1)
        # 4 (2,1)
        submat1.set_element(1, 0, (tpq - tpPPq - tpQQq + tpQPPQq), 1)
        # 5 (2,2)
        submat1.set_element(
            1,
            1,
            (tpp - tpPPp - tpqqp - tpQQp + tpqQQqp + 2 * tqpPPpq - tpPqQQqPp),
            1,
        )
        #
        # SUBMAT2
        # 6 same as 1,1 (3,3)
        submat2.set_element(
            0,
            0,
            (tqq - tpqqp - tpQQp - tqQQq + 2 * tpqQQqp + tqpPPpq - tpPqQQqPp),
            1,
        )
        # 7 same as 1,2 (3,4)
        submat2.set_element(0, 1, (tqp - tqPPp - tqQQp + tqPQQPp), 1)
        # 8 same as 2,1 (4,3)
        submat2.set_element(1, 0, (tpq - tpPPq - tpQQq + tpQPPQq), 1)
        # 9 same as 2,2 (4,4)
        submat2.set_element(
            1,
            1,
            (tpp - tpPPp - tpqqp - tpQQp + tpqQQqp + 2 * tqpPPpq - tpPqQQqPp),
            1,
        )
        # 10
        final_result.set_element(5, (tpqqp - tpqQQqp - tqpPPpq + tpPqQQqPp))
        # 11 same as 5,5
        final_result.set_element(6, (tpqqp - tpqQQqp - tqpPPpq + tpPqQQqPp))
        #
        # SUBMAT3
        # 12 (7,7)
        submat3.set_element(
            0, 0, (tqQQq - 2 * tpqQQqp + tpPqQQqPp + ptqq - ptqPPq), 1
        )
        # 13 (7,8)
        submat3.set_element(0, 1, (tqQQp - tqPQQPp), 1)
        # 14 (7,9)
        submat3.set_element(0, 2, (-tqQQp + tqPQQPp), 1)
        # 15 (7,10)
        submat3.set_element(0, 3, (tqQPp + ptqQPp), 1)
        # 16 (8,7)
        submat3.set_element(1, 0, (tpQQq - tpQPPQq), 1)
        # 17 (8,8)
        submat3.set_element(1, 1, (tpQQp - tqpPPpq - tpqQQqp + tpPqQQqPp), 1)
        # 18 (8,9)
        submat3.set_element(1, 2, (-tpQPq), 1)
        # 19 (8,10)
        submat3.set_element(1, 3, (tqPPp - tqPQQPp), 1)
        # 20 (9,7)
        submat3.set_element(2, 0, (-tpQQq + tpQPPQq), 1)
        # 21 (9,8)
        submat3.set_element(2, 1, (-tpQPq), 1)
        # 22 (9,9)
        submat3.set_element(2, 2, (tpQQp - tqpPPpq - tpqQQqp + tpPqQQqPp), 1)
        # 23 (9,10)
        submat3.set_element(2, 3, (-tqPPp + tqPQQPp), 1)
        # 24 (10,7)
        submat3.set_element(3, 0, (tpPQq + ptpPQq), 1)
        # 25 (10,8)
        submat3.set_element(3, 1, (tpPPq - tpQPPQq), 1)
        # 26 (10,9)
        submat3.set_element(3, 2, (-tpPPq + tpQPPQq), 1)
        # 27 (10,10)
        submat3.set_element(
            3, 3, (tpPPp - 2 * tqpPPpq + tpPqQQqPp + ptpp - ptqPPq), 1
        )
        #
        # SUBMAT4
        # 28 (11,11)
        submat4.set_element(0, 0, (tpqQQqp - tpPqQQqPp), 1)
        # 29 (11,12)
        submat4.set_element(0, 1, (-tqPQQPp), 1)
        # 30 (12,11)
        submat4.set_element(1, 0, (-tpQPPQq), 1)
        # 31 (12,12)
        submat4.set_element(1, 1, (tqpPPpq - tpPqQQqPp), 1)
        #
        # SUBMAT5
        # 32 same as 11,11 (13,13)
        submat5.set_element(0, 0, (tpqQQqp - tpPqQQqPp), 1)
        # 33 same as 11,12 (13,14)
        submat5.set_element(0, 1, (-tqPQQPp), 1)
        # 34 same as 12,11 (14,13)
        submat5.set_element(1, 0, (-tpQPPQq), 1)
        # 35 same as 12,12 (14,14)
        submat5.set_element(1, 1, (tqpPPpq - tpPqQQqPp), 1)
        # 36
        final_result.set_element(15, (tpPqQQqPp + ptqPPq))

        # block 1
        sole1, solvec1 = self.diagonalize(submat1, eigvec=True)
        for k in range(1, 3):
            final_result.set_element(k, sole1.get_element(k - 1))

        # block 2
        sole2, solvec2 = self.diagonalize(submat2, eigvec=True)
        for k in range(3, 5):
            final_result.set_element(k, sole2.get_element(k - 3))

        # block 3
        sole3, solvec3 = self.diagonalize(submat3, eigvec=True)
        for k in range(7, 11):
            final_result.set_element(k, sole3.get_element(k - 7))

        # block 4
        sole4, solvec4 = self.diagonalize(submat4, eigvec=True)
        for k in range(11, 13):
            final_result.set_element(k, sole4.get_element(k - 11))

        # block 5
        sole5, solvec5 = self.diagonalize(submat5, eigvec=True)
        for k in range(13, 15):
            final_result.set_element(k, sole5.get_element(k - 13))

        #
        # Get rid of negative values
        #
        if np.amin(final_result.array) < 0.0:
            for i in final_result.array:
                if i < 0.0 and abs(i) > 1e-5:
                    log.warn(
                        f"Negative eigenvalue of {i.real:2.6f} set to 0.0"
                    )
            final_result.array[np.where(final_result.array < 0.0)] = 0.0
        #
        # Renormalize
        #
        final_result.iscale(1 / final_result.trace())

        #
        # Assign elements of eigenvectors
        #
        final_vec.set_element(0, 0, 1.0)
        final_vec.set_element(5, 5, 1.0)
        final_vec.set_element(6, 6, 1.0)
        final_vec.set_element(15, 15, 1.0)

        # block 1
        for j in range(0, 2):
            for k in range(0, 2):
                final_vec.set_element(j + 1, k + 1, solvec1.get_element(j, k))

        # block 2
        for j in range(0, 2):
            for k in range(0, 2):
                final_vec.set_element(j + 3, k + 3, solvec2.get_element(j, k))

        # block 3
        for j in range(0, 4):
            for k in range(0, 4):
                final_vec.set_element(j + 7, k + 7, solvec3.get_element(j, k))

        # block 4
        for j in range(0, 2):
            for k in range(0, 2):
                final_vec.set_element(
                    j + 11, k + 11, solvec4.get_element(j, k)
                )

        # block 5
        for j in range(0, 2):
            for k in range(0, 2):
                final_vec.set_element(
                    j + 13, k + 13, solvec5.get_element(j, k)
                )

        self.odm2 = (index1, index2, final_result, final_vec)

    @staticmethod
    def print_rho_one():
        """Print header line with states of 1-ORDM"""
        # Unicode characters
        # \u2191 - upwards arrow
        # \u2193 - downwards arrow
        return "#index  |->       |\u2191>       |\u2193>       |x>\n"
