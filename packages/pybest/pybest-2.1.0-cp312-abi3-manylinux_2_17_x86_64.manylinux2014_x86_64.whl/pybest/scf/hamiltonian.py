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
# Detailed changes (see also CHANGELOG):
# 2020-07-01: Update to PyBEST standard, including naming convention and exception class
# 2020-07-01: Update to new python features, including f-strings


"""Mean-field HF Hamiltonian data structures"""

from pybest.cache import Cache
from pybest.exceptions import ArgumentError
from pybest.log import log
from pybest.units import electronvolt
from pybest.utility import doc_inherit

__all__ = ["RScfHam", "UScfHam"]


class ScfHam:
    """ABC class for the effective Hamiltonians

    **Attributes:**

    ndm
         The number of input density matrices and output fock matrices (e.g.
         ndm=1 for restricted wfns, ndm=2 for unrestricted wfns.)

    deriv_scale
         In principle, the fock matrix is the derivative of the expectation
         value towards the density matrix elements. In practice, this is not
         always the case. Depending on the type of effective Hamiltonian, the
         fock matrices must be multiplied with a factor to obtain proper
         derivatives. This factor is stored in the class attribute
         ``deriv_scale``. It defaults to 1.0.
    """

    ndm = None
    deriv_scale = 1.0

    def __init__(self, terms, external=None):
        """
        **Arguments:**

        terms
             The terms in the Hamiltonian.

        **Optional arguments:**

        external
             A dictionary with external energy contributions that do not
             depend on the wavefunction, e.g. nuclear-nuclear interactions
             or QM/MM mechanical embedding terms. Use ``nn`` as key for the
             nuclear-nuclear term.
        """
        # check arguments:
        if len(terms) == 0:
            raise ValueError(
                "At least one term must be present in the Hamiltonian."
            )

        # Assign attributes
        self.terms = list(terms)
        self.external = 0.0 if external is None else external

        # Create a cache for shared intermediate results. This cache should only
        # be used for derived quantities that depend on the wavefunction and
        # need to be updated at each SCF cycle.
        # Currently, only the 1-dm is stored and updated in each cycle.
        self.cache = Cache()

    def reset(self, *dms):
        """Clear intermediate results from the cache and specify new input density matrices.

        **Arguments:**

        dm1, dm2, ...
             The input density matrices. Their interpretation is fixed in
             derived classes.
        """
        raise NotImplementedError

    def compute_energy(self, cache=None):
        """Compute the expectation value.

        The input for this method must be provided through the ``reset``
        method.

        **Returns:** The expectation value, including the constant terms
        defined through the ``external`` argument of the constructor
        """
        if cache is None:
            cache = {}
        total = 0.0
        for term in self.terms:
            energy = term.compute_energy(self.cache)
            cache[f"e_{term.label}"] = energy
            total += energy
        if isinstance(self.external, dict):
            # Store also total external energy used in post-SCF methods
            eexternal = 0.0
            for key, energy in self.external.items():
                cache[f"e_{key}"] = energy
                total += energy
                eexternal += energy
            cache["e_core"] = eexternal
        elif isinstance(self.external, (float, int)):
            cache["e_core"] = self.external
            total += self.external
        else:
            raise ArgumentError(
                f"External energy of unknown type {type(self.external)}"
            )
        cache["e_tot"] = total
        cache["e_ref"] = total
        return total

    def log(self, cache):
        """Write an overview of the last computation on screen"""
        log("Contributions to the energy:")
        log.hline()
        log(f"{'term':>30} {'Value':>15}")
        log.hline()
        for term in self.terms:
            energy = cache[f"e_{term.label}"]
            log(f"{term.label:>30} {energy:> 20.12f}")
        if isinstance(self.external, dict):
            for key, energy in self.external.items():
                log(f"{key:>30} {energy:> 20.12f}")
        elif isinstance(self.external, (float, int)):
            log(f"{'external':>30} {self.external:> 20.12f}")
        else:
            raise ArgumentError(
                f"External energy of unknown type {type(self.external)}"
            )
        log(f"{'total':>30} {cache['e_tot']:> 20.12f}")
        log.hline()
        log("Print orbital information:")
        log.hline()

        orbs = cache["orb_a"]
        log(f"{'orb_index':>24s} {'Energy[E_h]':>18s} {'Energy[eV]':>14s}")
        e_homo = None
        e_lumo = None

        for count, e_orbital in enumerate(orbs.energies):
            if count == orbs.get_homo_index():
                e_homo = e_orbital
                log(
                    f"\t\t{'HOMO':>4}\t{e_homo:> 18.7f}{e_orbital / electronvolt:> 14.3f}"
                )
            elif count == orbs.get_lumo_index():
                e_lumo = e_orbital
                log(
                    f"\t\t{'LUMO':>4}\t{e_lumo:> 18.7f}{e_orbital / electronvolt:> 14.3f}"
                )
            else:
                log(
                    f"\t\t{count + 1:>4} {'':>4}\t{e_orbital:> 10.7f}{e_orbital / electronvolt:> 14.3f}"
                )
        log.hline("-")
        # Calculate LUMO-HOMO gap if both HOMO and LUMO orbitals were found
        if e_homo is not None and e_lumo is not None:
            lumo_homo_gap = e_lumo - e_homo
            log(
                f"{'LUMO-HOMO gap':>20} \t\t{lumo_homo_gap:> 10.7f}{lumo_homo_gap / electronvolt:> 14.3f}"
            )
            # Check if the LUMO-HOMO gap is negative and print a warning
            if lumo_homo_gap < 0:
                log.warning("Warning: LUMO-HOMO gap is negative.")
        else:
            raise ValueError(
                "Unable to calculate LUMO-HOMO gap: HOMO or LUMO orbital not found."
            )

        log.hline()
        log.hline()

    def compute_fock(self, *focks):
        """Compute the Fock matrices, defined as derivatives of the expectation
        value toward the components of the input density matrices.

        **Arguments:**

        fock1, fock2, ....
             A list of output fock operators. Old content is discarded.

        The input for this method must be provided through the ``reset``
        method.
        """
        for fock in focks:
            fock.clear()
        # Loop over all terms and add contributions to the Fock matrix.
        for term in self.terms:
            term.add_fock(self.cache, *focks)


class RScfHam(ScfHam):
    """
    Restricted SCF Hamiltonian Class

    Inherits from ScfHam base class
    """

    ndm = 1
    deriv_scale = 2.0

    @doc_inherit(ScfHam)
    def reset(self, in_one_dm_scf_a):
        self.cache.clear()
        # Take a copy of the input alpha density matrix in the cache.
        one_dm_scf_a = self.cache.load(
            "one_dm_scf_a", alloc=in_one_dm_scf_a.new
        )[0]
        one_dm_scf_a.assign(in_one_dm_scf_a)

    @doc_inherit(ScfHam)
    def compute_fock(self, fock_alpha):
        ScfHam.compute_fock(self, fock_alpha)


class UScfHam(ScfHam):
    """Unrestricted SCF Hamiltonian Class

    Inherits from ScfHam base class
    """

    ndm = 2

    @doc_inherit(ScfHam)
    def reset(self, in_one_dm_scf_a, in_one_dm_scf_b):
        self.cache.clear()
        # Take copies of the input alpha and beta density matrices in the cache.
        one_dm_scf_a = self.cache.load(
            "one_dm_scf_a", alloc=in_one_dm_scf_a.new
        )[0]
        one_dm_scf_a.assign(in_one_dm_scf_a)
        one_dm_scf_b = self.cache.load(
            "one_dm_scf_b", alloc=in_one_dm_scf_b.new
        )[0]
        one_dm_scf_b.assign(in_one_dm_scf_b)

    @doc_inherit(ScfHam)
    def compute_fock(self, fock_alpha, fock_beta):
        ScfHam.compute_fock(self, fock_alpha, fock_beta)
