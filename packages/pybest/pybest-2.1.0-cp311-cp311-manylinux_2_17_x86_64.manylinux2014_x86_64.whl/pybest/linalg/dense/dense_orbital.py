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
#
# This implementation has been taken from `Horton 2.0.0`.
# However, this file has been updated and debugged. Compatibility with Horton is NOT
# guaranteed.
# Its current version contains updates from the PyBEST developer team.
#


r"""Dense orbital implementation"""

import numpy as np
from scipy.linalg import eigh

from pybest.exceptions import ArgumentError, MatrixShapeError, SymmetryError
from pybest.linalg.base import Orbital
from pybest.log import log


class DenseOrbital(Orbital):
    """An expansion of several functions in a basis with a dense matrix of
    coefficients. The implementation is such that the columns of self.array
    contain the orbitals.
    """

    # identification attribute
    dense_orb_identifier = True

    #
    # Constructor and destructor
    #

    def __init__(self, nbasis, nfn=None):
        """
        **Arguments:**

        nbasis
             The number of basis functions.

        **Optional arguments:**

        nfn
             The number of functions to store. Defaults to nbasis.
        """
        if nfn is None:
            nfn = nbasis
        self._coeffs = np.zeros((nbasis, nfn))
        self._energies = np.zeros(nfn)
        self._occupations = np.zeros(nfn)
        log.mem.announce(
            self._coeffs.nbytes
            + self._energies.nbytes
            + self._occupations.nbytes
        )

    def __del__(self):
        """Destructor."""
        if log is not None:
            if (
                hasattr(self, "_coeffs")
                and hasattr(self, "_energies")
                and hasattr(self, "_occupations")
            ):
                log.mem.denounce(
                    self._coeffs.nbytes
                    + self._energies.nbytes
                    + self._occupations.nbytes
                )

    #
    # Methods from base class
    #

    def __check_init_args__(self, nbasis, nfn=None):
        """Is self compatible with the given constructor arguments?

        nbasis
             The number of basis functions.

        **Optional arguments:**

        nfn
             The number of functions to store. Defaults to nbasis.
        """
        if nfn is None:
            nfn = nbasis
        assert nbasis == self.nbasis
        assert nfn == self.nfn

    def __eq__(self, other):
        """Compare self with other

        other
            Another DenseOrbital object.
        """
        return (
            isinstance(other, DenseOrbital)
            and other.nbasis == self.nbasis
            and other.nfn == self.nfn
            and (other.coeffs == self._coeffs).all()
            and (other.energies == self._energies).all()
            and (other.occupations == self._occupations).all()
        )

    @classmethod
    def from_hdf5(cls, grp):
        """Construct an instance from data previously stored in an h5py.Group.

        **Arguments:**

        grp
             An h5py.Group object.
        """
        if grp.attrs["class"] != cls.__name__:
            raise ArgumentError(
                "The class of the orbital in the HDF5 file does not match."
            )
        nbasis, nfn = grp["coeffs"].shape
        result = cls(nbasis, nfn)
        grp["coeffs"].read_direct(result.coeffs)
        grp["energies"].read_direct(result.energies)
        grp["occupations"].read_direct(result.occupations)
        return result

    def to_hdf5(self, grp):
        """Dump this object in an h5py.Group

        **Arguments:**

        grp
             An h5py.Group object.
        """
        grp.attrs["class"] = self.__class__.__name__
        grp["coeffs"] = self._coeffs
        grp["energies"] = self._energies
        grp["occupations"] = self._occupations

    def new(self):
        """Return a new orbital object with the same nbasis and nfn"""
        return DenseOrbital(self.nbasis, self.nfn)

    def _check_new_init_args(self, other):
        """Check whether an already initialized object is compatible

        other
            Another DenseOrbital object.
        """
        other.__check_init_args__(self.nbasis, self.nfn)

    new.__check_init_args__ = _check_new_init_args

    def replace_array(self, value):
        """Replaces an array with another array.

        Value
             The DenseOrbital object which will replace the array.
        """
        if isinstance(value, DenseOrbital):
            self._coeffs = value.coeffs
            self._energies = value.energies
            self._occupations = value.occupations
        else:
            raise ArgumentError(
                f"Do not know how to assign object of type {type(value)}."
            )

    def clear(self):
        """Reset all elements to zero."""
        self._coeffs[:] = 0.0
        self._energies[:] = 0.0
        self._occupations[:] = 0.0

    def clear_energies(self):
        """Reset all energies to zero."""
        self._energies[:] = 0.0

    def copy(self):
        """Return a copy of the object"""
        result = DenseOrbital(self.nbasis, self.nfn)
        result._coeffs[:] = self._coeffs
        result._energies[:] = self._energies
        result._occupations[:] = self._occupations
        return result

    def any(self):
        """Check whether any array element of DenseOrbital is empty"""
        return (
            np.any(self._coeffs)
            and np.any(self._energies)
            and np.any(self._occupations)
        )

    def assign(self, other):
        """Assign with the contents of another object

        **Arguments:**

        other
             Another DenseOrbital or DenseTwoIndex object.
             If DenseTwoIndex, energies and occupations are set to zero.
        """
        if hasattr(other, "dense_orb_identifier"):
            self._coeffs[:] = other.coeffs
            self._energies[:] = other.energies
            self._occupations[:] = other.occupations
        elif hasattr(other, "dense_two_identifier"):
            self._coeffs[:] = other.array
            self._energies[:] = 0.0
            self._occupations[:] = 0.0
        else:
            raise TypeError(
                "Instance of the wrong type used with a function called in DenseOrbital. "
            )

    def itranspose(self):
        """In-place transpose"""
        self._coeffs[:] = self._coeffs.T

    def imul(self, other):
        """Inplace multiplication with other DenseOneIndex.

        The attributes ``energies`` and ``occupations`` are not altered.

        **Arguments:**

        other
             A DenseOneIndex object.
        """
        if not hasattr(other, "dense_one_identifier"):
            raise TypeError(
                "Instance of wrong type used with function called in linalg_factory. "
            )
        self._coeffs[:] *= other.array

    def iscale_basis(self, other):
        """Inplace scaling of MO coeffs with other (np array).

        The attributes ``energies`` and ``occupations`` are not altered.

        **Arguments:**

        other
             A np.array object.
        """
        self.check_type("other", other, np.ndarray)
        self._coeffs[:] = other[np.newaxis].T * self._coeffs[:]

    def randomize(self):
        """Fill with random normal data"""
        self._coeffs[:] = np.random.normal(0, 1, self._coeffs.shape)
        self._energies[:] = np.random.normal(0, 1, self._energies.shape)
        self._occupations[:] = np.random.normal(0, 1, self._occupations.shape)

    def permute_basis(self, permutation):
        """Reorder the coefficients for a given permutation of basis functions
        (rows).

        **Arguments:**

        permutation
             An integer numpy array that defines the new order of the basis
             functions.
        """
        self._coeffs[:] = self.coeffs[permutation]

    def permute_orbitals(self, permutation, begin0=0, end0=None):
        """Reorder the coefficients for a given permutation of orbitals
        (columns).

        **Arguments:**

        permutation
             An integer numpy array that defines the new order of the
             orbitals.
        """
        end0 = self.nfn
        self._coeffs[:, begin0:end0] = self.coeffs[:, begin0:end0][
            :, permutation
        ]
        self._occupations[begin0:end0] = self.occupations[begin0:end0][
            permutation
        ]
        self._energies[begin0:end0] = self.energies[begin0:end0][permutation]

    def change_basis_signs(self, signs):
        """Correct for different sign conventions of the basis functions.

        **Arguments:**

        signs
             A numpy array with sign changes indicated by +1 and -1.
        """
        self._coeffs *= signs.reshape(-1, 1)

    def check_normalization(self, overlap, eps=1e-4):
        """Check that the occupied orbitals are normalized.

        **Arguments:**

        overlap
             The overlap two-index operator

        **Optional arguments:**

        eps
             The allowed deviation from unity, very loose by default.
        """
        if not hasattr(overlap, "dense_two_identifier"):
            raise TypeError(
                "Instance of wrong type used with function called in dense_orbital. "
            )
        for i in range(self.nfn):
            if self.occupations[i] == 0:
                continue
            norm = overlap.inner(self._coeffs[:, i], self._coeffs[:, i])
            # print i, norm
            assert abs(norm - 1) < eps, "The orbitals are not normalized!"

    def check_orthonormality(self, overlap, eps=1e-4):
        """Check that the occupied orbitals are orthogonal and normalized.

        **Arguments:**

        overlap
             The overlap two-index operator

        **Optional arguments:**

        eps
             The allowed deviation from unity, very loose by default.
        """
        if not hasattr(overlap, "dense_two_identifier"):
            raise TypeError(
                "Instance of wrong type used with function called in dense_orbital. "
            )
        for i_0 in range(self.nfn):
            if self.occupations[i_0] == 0:
                continue
            for i_1 in range(i_0 + 1):
                if self.occupations[i_1] == 0:
                    continue
                dot = overlap.inner(self.coeffs[:, i_0], self.coeffs[:, i_1])
                if i_0 == i_1:
                    assert abs(dot - 1) < eps
                else:
                    assert abs(dot) < eps

    def error_eigen(self, fock, overlap):
        """Compute the error of the orbitals with respect to the eigenproblem

        **Arguments:**

        fock
             A DenseTwoIndex Hamiltonian (or Fock) operator.

        overlap
             A DenseTwoIndex overlap operator.

        **Returns:** the RMSD error on the orbital energies
        """
        if not hasattr(fock, "dense_two_identifier"):
            raise TypeError(
                "Instance of wrong type used with function called in dense_orbital. "
            )
        if not hasattr(overlap, "dense_two_identifier"):
            raise TypeError(
                "Instance of wrong type used with function called in dense_orbital. "
            )
        errors = np.dot(fock.array, (self.coeffs)) - self.energies * np.dot(
            overlap.array, (self.coeffs)
        )
        return np.sqrt((abs(errors) ** 2).mean())

    #
    # Properties
    #

    @property
    def nbasis(self):
        """The number of basis functions"""
        return self._coeffs.shape[0]

    @property
    def nfn(self):
        """The number of orbitals (or functions in general)"""
        return self._coeffs.shape[1]

    @property
    def coeffs(self):
        """The matrix with the expansion coefficients"""
        return self._coeffs.view()

    @property
    def energies(self):
        """The orbital energies"""
        return self._energies.view()

    @property
    def occupations(self):
        """The orbital occupations"""
        return self._occupations.view()

    def from_fock(self, fock, overlap):
        """Diagonalize a Fock matrix to obtain orbitals and energies

        This method updated the attributes ``coeffs`` and ``energies``
        in-place.

        **Arguments:**

        fock
             The fock matrix, an instance of DenseTwoIndex.

        overlap
             The overlap matrix, an instance of DenseTwoIndex.
        """
        if not hasattr(fock, "dense_two_identifier"):
            raise TypeError(
                "Instance of wrong type used with function called in dense_orbital. "
            )
        if not hasattr(overlap, "dense_two_identifier"):
            raise TypeError(
                "Instance of wrong type used with function called in dense_orbital. "
            )
        evals, evecs = eigh(fock.array, overlap.array)
        self._energies[:] = evals[: self.nfn]
        self._coeffs[:] = evecs[:, : self.nfn]

    def from_fock_and_dm(self, fock, d_m, overlap, epstol=1e-8):
        """Combined Diagonalization of a Fock and a density matrix

        This routine first diagonalizes the Fock matrix to obtain orbitals
        and orbital energies. Then, using first order (degenerate)
        perturbation theory, the occupation numbers are computed and, if
        needed, the the degeneracies of the Fock orbitals are lifted.
        It is assumed that the Fock and the density matrices commute.
        This method updated the attributes ``coeffs``, ``energies`` and
        ``occupations`` in-place.

        **Arguments:**

        fock
             The fock matrix, an instance of DenseTwoIndex.

        d_m
             The density matrix, an instance of DenseTwoIndex.

        overlap
             The overlap matrix, an instance of DenseTwoIndex.

        **Optional arguments:**

        epstol
             The threshold for recognizing degenerate energy levels. When two
             subsequent energy levels are separated by an orbital energy less
             than ``epstol``, they are considered to be degenerate. When a
             series of energy levels have an orbital energy spacing between
             subsequent levels that is smaller than ``epstol``, they are all
             considered to be part of the same degenerate group. For every
             degenerate set of orbitals, the density matrix is used to (try
             to) lift the degeneracy.
        """
        # Diagonalize the Fock Matrix
        self.from_fock(fock, overlap)

        # Build clusters of degenerate orbitals. Rely on the fact that the
        # energy levels are sorted (one way or the other).
        clusters = []
        begin = 0
        for ifn in range(1, self.nfn):
            if abs(self.energies[ifn] - self.energies[ifn - 1]) > epstol:
                end = ifn
                clusters.append([begin, end])
                begin = ifn
        end = self.nfn
        clusters.append([begin, end])

        # Lift degeneracies using the density matrix
        sds = overlap.copy()
        sds.itranspose()
        sds.idot(d_m)
        sds.idot(overlap)
        for begin, end in clusters:
            if end - begin == 1:
                self.occupations[begin] = sds.inner(
                    self.coeffs[:, begin], self.coeffs[:, begin]
                )
            else:
                # Build matrix
                mat = np.zeros((end - begin, end - begin), float)
                for i_0 in range(end - begin):
                    for i_1 in range(i_0 + 1):
                        mat[i_0, i_1] = sds.inner(
                            self.coeffs[:, begin + i_0],
                            self.coeffs[:, begin + i_1],
                        )
                        mat[i_1, i_0] = mat[i_0, i_1]
                # Diagonalize and reverse order
                evals, evecs = np.linalg.eigh(mat)
                evals = evals[::-1]
                evecs = evecs[:, ::-1]
                # Rotate the orbitals
                self.coeffs[:, begin:end] = np.dot(
                    self.coeffs[:, begin:end], evecs
                )
                # Compute expectation values
                for i0 in range(end - begin):
                    self.occupations[begin + i0] = evals[i0]
                    self.energies[begin + i0] = fock.inner(
                        self.coeffs[:, begin + i0], self.coeffs[:, begin + i0]
                    )

    def derive_naturals(self, d_m, overlap=None, sort=False, backtrafo=False):
        """
        **Arguments**:

        d_m
             A DenseTwoIndex object with the density matrix

        **Optional arguments:**

        overlap
             A DenseTwoIndex object with the overlap matrix

        sort
             Sort natural orbitals according to occupation numbers

        backtrafo
             Transform back to original AO basis (d_m represented as MO/MO
             is transformed back to AO/MO representation)
        """
        #        self.check_type("d_m", d_m, DenseTwoIndex)
        if not hasattr(d_m, "dense_two_identifier"):
            raise TypeError(
                "Instance of wrong type used with function called in dense_orbital. "
            )
        # diagonalize and compute eigenvalues
        if overlap is None:
            if not d_m.is_symmetric():
                raise SymmetryError("Density matrix not symmetric.")
            evals, evecs = eigh(d_m.array)
            # do backtransformation
            if backtrafo:
                evecs = np.dot(self._coeffs, evecs)
        else:
            #            self.check_type("overlap", overlap, DenseTwoIndex)
            if not hasattr(overlap, "dense_two_identifier"):
                raise TypeError(
                    "Instance of wrong type used with function called in dense_orbital. "
                )
            # Constr a level-shifted operator
            occ = overlap.copy()
            occ.idot(d_m)
            occ.idot(overlap)
            evals, evecs = eigh(occ.array, overlap.array)
        self._coeffs[:] = evecs[:, : self.nfn]
        self._occupations[:] = evals
        self._energies[:] = 0.0
        if sort:
            order = np.argsort(evals, axis=-1, kind="mergesort", order=None)[
                ::-1
            ]
            self.permute_orbitals(order)

    def get_homo_index(self, offset=0):
        """Return the index of a HOMO orbital.

        **Optional arguments**:

        offset
             By default, the (highest) homo energy is returned. When this
             index is above zero, the corresponding lower homo energy is
             returned.
        """
        if offset < 0:
            raise ArgumentError("Offset must be zero or positive.")
        homo_indices = self.occupations.nonzero()[0]
        if len(homo_indices) > offset:
            return homo_indices[len(homo_indices) - offset - 1]
        raise ArgumentError("Offset larger than HOMO indices.")

    def get_homo_energy(self, offset=0):
        """Return a homo energy

        **Optional arguments**:

        offset
             By default, the (highest) homo energy is returned. When this
             index is above zero, the corresponding lower homo energy is
             returned.
        """
        index = self.get_homo_index(offset)
        if index is not None:
            return self.energies[index]
        raise ArgumentError("Do not know how to handle offset.")

    homo_energy = property(get_homo_energy)

    def get_lumo_index(self, offset=0):
        """Return the index of a LUMO orbital.

        **Optional arguments**:

        offset
             By default, the (lowest) lumo energy is returned. When this
             index is above zero, the corresponding higher homo energy is
             returned.
        """
        if offset < 0:
            raise ArgumentError("Offset must be zero or positive.")
        lumo_indexes = (self.occupations == 0.0).nonzero()[0]
        if len(lumo_indexes) > offset:
            return lumo_indexes[offset]
        raise ArgumentError("Offset larger than HOMO indices.")

    def get_lumo_energy(self, offset=0):
        """Return a lumo energy

        **Optional arguments**:

        offset
             By default, the (lowest) lumo energy is returned. When this
             index is above zero, the corresponding higher homo energy is
             returned.
        """
        index = self.get_lumo_index(offset)
        if index is not None:
            return self.energies[index]
        raise ArgumentError("Do not know how to handle offset.")

    lumo_energy = property(get_lumo_energy)

    def assign_dot(self, left, right):
        """Dot product of orbitals in a DenseOrbital and TwoIndex object

        **Arguments:**

        left, right:
             An expansion and a two-index object, or a two-index and an expansion
             object.

        The transformed orbitals are stored in self.
        """
        #        if isinstance(left, DenseOrbital):
        if hasattr(left, "dense_orb_identifier"):
            #            self.check_type("left", left, DenseOrbital)
            #            if not hasattr(left,'dense_orb_identifier'):
            #                raise TypeError(
            #                    f"Instance of wrong type used with function called in dense_orbital. "
            #                )
            #            self.check_type("right", right, DenseTwoIndex)
            if not hasattr(right, "dense_two_identifier"):
                raise TypeError(
                    "Instance of wrong type used with function called in dense_orbital. "
                )
            if self.nbasis != left.nbasis:
                raise MatrixShapeError(
                    "Both expansions must have the same number of basis functions."
                )
            if right.shape[0] != left.nfn or right.shape[1] != self.nfn:
                raise MatrixShapeError(
                    "The shape of the two-index object is incompatible with that of the expansions."
                )
            self._coeffs[:] = np.dot(left.coeffs, right.array)
        #        elif isinstance(right, DenseOrbital):
        elif hasattr(right, "dense_orb_identifier"):
            #            self.check_type("left", left, DenseTwoIndex)
            if not hasattr(left, "dense_two_identifier"):
                raise TypeError(
                    "Instance of wrong type used with function called in dense_orbital. "
                )
            #            self.check_type("right", right, DenseOrbital)
            #            if not hasattr(right,'dense_orb_identifier'):
            #                raise TypeError(
            #                    f"Instance of wrong type used with function called in dense_orbital. "
            #                )
            if self.nfn != right.nfn:
                raise MatrixShapeError(
                    "Both expansions must have the same number of orbitals."
                )
            if left.shape[1] != right.nbasis or left.shape[1] != self.nbasis:
                raise MatrixShapeError(
                    "The shape of the two-index object is incompatible with that of the expansions."
                )
            self._coeffs[:] = np.dot(left.array, right.coeffs)

    def assign_occupations(self, occupation, begin0=0, end0=None):
        """Assign orbital occupations

        **Arguments:**

        occupation
             The orbital occupations to be updated. An OneIndex instance
        """
        end0 = self.nbasis
        #        self.check_type("occupation", occupation, DenseOneIndex, DenseOrbital)
        if not hasattr(occupation, "dense_one_identifier") and not hasattr(
            occupation, "dense_orb_identifier"
        ):
            raise TypeError(
                "Instance of wrong type used with function called in dense_orbital. "
            )
        if end0 - begin0 != occupation.nbasis:
            raise MatrixShapeError(
                "The expansion and one-index object must have the same number of basis functions."
            )
        #        if isinstance(occupation, DenseOneIndex):
        if hasattr(occupation, "dense_one_identifier"):
            self._occupations[begin0:end0] = occupation.array
        #        elif isinstance(occupation, DenseOrbital):
        elif hasattr(occupation, "dense_orb_identifier"):
            self._occupations[begin0:end0] = occupation.occupations[:]

    def assign_coeffs(self, coeffs, begin0=0, end0=None):
        """Assign orbital coefficients for a subset of orbitals.
        We assume same AOs (that is, nbasis is the same). Array elements
        corresponding to nfn will be updated (that is, the MOs are overwritten).

        **Arguments:**

        coeffs:
             The orbital coefficients to be updated. An OneIndex/array instance
        """
        if end0 is None:
            end0 = self.nbasis

        if hasattr(coeffs, "dense_two_identifier"):
            self._coeffs[:, begin0:end0] = coeffs.array
        elif hasattr(coeffs, "dense_orb_identifier"):
            self._coeffs[:, begin0:end0] = coeffs.coeffs
        elif isinstance(coeffs, np.ndarray):
            self._coeffs[:, begin0:end0] = coeffs
        else:
            raise NotImplementedError(f"Do not know how to handle {coeffs}!")

    def rotate_random(self):
        """Apply random unitary transformation distributed with Haar measure

        The attributes ``energies`` and ``occupations`` are not altered.
        """
        rand = np.random.normal(0, 1, (self.nfn, self.nfn))
        matrix, _ = np.linalg.qr(rand)
        self.coeffs[:] = np.dot(self.coeffs, matrix)

    def rotate_2orbitals(
        self, angle=0.7853981633974483, index0=None, index1=None
    ):
        """Rotate two orbitals

        **Optional arguments:**

        angle
             The rotation angle, defaults to 45 deg.

        index0, index1
             The orbitals to rotate, defaults to HOMO and LUMO,

        The attributes ``energies`` and ``occupations`` are not altered.
        """
        if index0 is None:
            index0 = self.get_homo_index()
        if index1 is None:
            index1 = self.get_lumo_index()
        old0 = self.coeffs[:, index0].copy()
        old1 = self.coeffs[:, index1].copy()
        self.coeffs[:, index0] = np.cos(angle) * old0 - np.sin(angle) * old1
        self.coeffs[:, index1] = np.sin(angle) * old0 + np.cos(angle) * old1

    def swap_orbitals(self, swaps, skip_occs=False, skip_energies=False):
        """Change the order of the orbitals using pair-exchange

        **Arguments:**

        swaps
             An integer numpy array with two columns where every row
             corresponds to one swap.

        The attributes ``energies`` and ``occupations`` are also reordered.
        """
        if not (
            swaps.shape[1] == 2
            and swaps.ndim == 2
            and issubclass(swaps.dtype.type, np.int_)
        ):
            raise ArgumentError("The argument swaps has the wrong shape/type.")
        for row in swaps:
            index0, index1 = row
            if log.do_medium:
                log(f"  Swapping orbitals {index0 + 1} and {index1 + 1}.")
            tmp = self.coeffs[:, index0].copy()
            self.coeffs[:, index0] = self.coeffs[:, index1]
            self.coeffs[:, index1] = tmp
            if not skip_energies:
                self.energies[index0], self.energies[index1] = (
                    self.energies[index1],
                    self.energies[index0],
                )
            if not skip_occs:
                self.occupations[index0], self.occupations[index1] = (
                    self.occupations[index1],
                    self.occupations[index0],
                )

    def gram_schmidt(self):
        """Orthogonalize MOs, that is, all column vectors using the GS scheme.
        This only works if the orbitals are represented in an orthonormal basis.
        """
        mo_ortho = []
        # We loop over rows, but we have to loop over columns (-> transpose)
        for v in self.coeffs.T:
            w = v - sum(np.dot(v, mo) * mo for mo in mo_ortho)
            if (abs(w) > 1e-12).any():
                mo_ortho.append(w / np.linalg.norm(w))
        # Overwrite old orbital coefficeints
        self._coeffs = np.array(mo_ortho).T
