"""Fungus

Utilities for modeling various fungal systems.
"""
# ─── import statements ────────────────────────────────────────────────── ✦✦ ─

from typing import Optional
from uuid import uuid4, UUID

from ..genomics import Genome, FungalGenome
from ..phylogeny import Phylogeny

# ─── models ───────────────────────────────────────────────────────────── ✦✦ ─

class Fungus:
    """Base class for all fungi."""

    def __init__(
        self,
        genome: Optional[FungalGenome] = None,
        phylogeny: Optional[Phylogeny] = None
    ) -> None:
        self._id: UUID = uuid4()
        self.phylogeny = phylogeny

        if self.phylogeny:
            self.genus = phylogeny.genus
            self.species = phylogeny.species
        if isinstance(genome, Genome):
            self.genome = genome
        else:
            print("`Virus`argument genome` must be an instance of `Genome`.")



    # ─── properties ───────────────────────────────────────────────────────────
    #
    # TODO: Add properties for the Fungus class as needed.
    
    @property
    def phylogeny(self) -> Optional[Phylogeny]:
        """Return the phylogeny of the fungus."""
        return self._phylogeny

    @phylogeny.setter
    def phylogeny(self, value: Phylogeny) -> None:
        """Set the phylogeny of the fungus."""
        self._phylogeny = value

    @phylogeny.deleter
    def phylogeny(self) -> None:
        """Delete the phylogeny of the fungus."""
        del self._phylogeny


    # ─── instance methods ────────────────────────────────────────────────────
    #
    # TODO: Add methods for the Fungus class as needed.
    # TODO: Ensure that the genome is a FungalGenome instance.
    # TODO: Implement methods for genome manipulation, phylogeny analysis, etc.
    # TODO: Implement a method to replicate the fungus.
    # TODO: Implement a method to analyze the phylogeny.
    # TODO: Implement a method to analyze the genome.
    # TODO: Implement a method to simulate growth or reproduction.
    # TODO: Implement a method to simulate interactions with other organisms.
    # TODO: Implement a method to simulate environmental interactions.
    # TODO: Implement a method to simulate evolutionary processes.
    # TODO: Implement a method to simulate ecological interactions.
    # TODO: Implement a method to simulate population dynamics.
    # TODO: Implement a method to simulate community dynamics.
    # TODO: Implement a method to simulate ecosystem dynamics.
    # TODO: Implement a method to simulate biogeochemical cycles.
    # TODO: Implement a method to simulate nutrient cycling.
    # TODO: Implement a method to simulate energy flow.

    def replicate(self) -> "Fungus":
        return self.__class__(genome=self.genome, phylogeny=self.phylogeny)

    # : properties

    @property
    def id(self) -> UUID:
        """Return the unique identifier of the fungus."""
        return self._id

    @id.setter
    def id(self, value: UUID) -> None:
        if isinstance(value, UUID):
            self._id = value
        else:
            raise TypeError("Fungus ID must be a UUID instance.")

    @id.deleter
    def id(self) -> None:
        raise UserWarning(
            """
            ⚠︎ Warning:

            It is not recommended to delete eneities' identifiers, as
            Starch's simulation framework depdens on them for tracking
            and event handling.

            That said, if you're absolutely sure that you want to
            delete the identifier, you can do so by deleting the
            instance's `._id` attribute directly.
            """
        )
    
