"""Bacterium

Utilities for modeling various bacterial systems.
"""
# : import statements

# standard library imports
from __future__ import annotations

import logging

from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path
from random import randint
from uuid import uuid4, UUID

# third-party imports
from platformdirs import user_log_dir

# local imports
from ..genomics import Genome, BacterialGenome
from ..phylogeny import Phylogeny

# : models

class Bacterium(ABC):
    """Base model for all bacteria."""
    
    def __init__(
        self,
        genome: Optional[BacterialGenome] = None,
        phylogeny: Optional[Phylogeny] = None
    ) -> None:
        self._id: UUID = uuid4()  # Unique identifier for the bacterium
        self._parent: Optional["Bacterium"] = None  # Parent bacterium, if any
        self._children: Optional[List["Bacterium"]] = []  # List of child bacteria
        self.phylogeny = phylogeny

        if self.phylogeny:
            self.genus = phylogeny.genus
            self.species = phylogeny.species

        if isinstance(genome, Genome):
            self.genome = genome
        elif not isinstance(genome, Genome) and genome is not None:
            print(
                "Bacterium argument `genome` must be an instance of `Genome`."
            )
        else:
            self.genome = None  # Default to None if no genome is provided
    
    # : instance methods
    #
    # TODO: Add methods for the Bacterum class as needed.
    # TODO: Ensure that the genome is a BacterialGenome instance.
    # TODO: Implement methods for genome manipulation, phylogeny analysis, etc.
    # TODO: Implement a method to replicate the bacterium.
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

    
    # : properties

    @property
    def id(self) -> UUID:
        """Return the unique identifier of the bacterium."""
        return self._id

    @id.setter
    def id(self, value: UUID) -> None:
        if isinstance(value, UUID):
            self._id = value
        else:
            raise TypeError("Bacterium ID must be a UUID instance.")

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

    # : magic methods

    def __repr__(self) -> str:
        return f"Bacterium(id={self.id}, phylogeny={self.phylogeny}, genome={self.genome})"

    def __str__(self) -> str:
        return f"Bacterium {self.id} ({self.phylogeny.genus} {self.phylogeny.species})"

    def __eq__(self, other: object) -> bool:
        return (
            TypeError if not isinstance(other, Bacterium) else
            True if self.id == other.id else False
        )

    def __hash__(self) -> int:
        return hash(self.id)


    # : instance methods 
