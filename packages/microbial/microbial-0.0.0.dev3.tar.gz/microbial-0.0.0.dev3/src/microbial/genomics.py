"""Genomics

This module defines the package's microbial genome models.
"""
# ─── import statements ────────────────────────────────────────────────── ✦✦ ──

# standard library imports
from abc import ABC
from enum import Enum
from pathlib import Path
from typing import Optional, Protocol, Union


class Domain(Enum):
    BACTERIA = "bacteria"
    FUNGI = "fungi"
    VIRUSES = "viruses"

class Genomic(Protocol):
    domain: Domain
    _sequence: Optional

    @property
    def sequence(self) -> str: ...

    @sequence.setter
    def sequence(self, value) -> None: ...

    @sequence.deleter
    def sequence(self) -> None: ...


# ─── base classes ───────────────────────────────────────────────────────────── ✦✦ ──

class Genome(ABC):
    """
    Base class for all genome models in the `microbial` framework.

    Inherited by the following concrete classes:

    - `BacterialGenome`
    - `FungalGenome`
    - `ViralGenome`
    """


    # ─── class methods ────────────────────────────────────────────────────────

    domain: Domain

    def __init__(
        self,
        sequence: Optional[Union[str, str]] = None,
        is_damaged: bool = False,
        is_linear: bool = False,
        is_mutated: bool = False,
        is_mutating: bool = False,
        is_replicating: bool = False,
        is_toxigenic: bool = False,
        is_cryostable: Optional[bool] = None,
        is_halostable: Optional[bool] = None,
        is_thermostable: Optional[bool] = None
    ) -> None:
        """ Constructor

        Initializes an instance of `Genome`.

        Args:

          sequence:
            An optional string or `Seq` object representing the genome's
            DNA sequence. Defaults to `False`.

          is_damaged:
            A boolean value that indicates the presence of DNA damage.
            Defaults to `False`.

          is_linear:
            A boolean value that indicates a genome's linearity. Defaults
            to `False`.

          is_mutated:
            A boolean value that indicates the presence of mutations.
            Defaults to `False`.

          is_mutating:
            A boolean value that indicates whether a genome is actively
            undergoing DNA replication. Defaults to `False`.

          is_toxigenic:
            A boolean value that indicates whether a genome encodes known
            human toxins. Defaults to `False`.

          is_cryostable:
            An optional boolean value that indicates whether a genome is
            able to withstand especially low temperatures. Defaults to
            `None`.

          is_halostable:
            An optional boolean value that indicates whether a genome is
            able to withstand especially high concentrations of salt.
            Defaults to `None`.

          is_thermostable:
            An optional boolean value that indicates whether a genome is
            able to withstand especially high temperatures. Defaults to
            `None`.

        Returns: `None`
        """
        self._sequence = sequence
        self.is_damaged = is_damaged
        self.is_linear = is_linear
        self.is_mutated = is_mutated
        self.is_mutating = is_mutating
        self.is_replicating = is_replicating
        self.is_toxigenic = is_toxigenic
        self.is_cryostable = is_cryostable
        self.is_halostable = is_halostable
        self.is_thermostable = is_thermostable

    @property
    def sequence(self) -> str:
        """Getter for the genome's `sequence` property."""
        ...

    @sequence.setter
    def sequence(self, value) -> None:
        """Setter for the genome's `sequence` property."""
        ...

    @sequence.deleter
    def sequence(self) -> None:
        """Deleter for the genome's `sequence` property."""
        ...

    @property
    def sequence(self) -> str:
        return self._sequence

    @sequence.setter
    def sequence(self, value) -> None:
        self._sequence = value

    @sequence.deleter
    def sequence(self) -> None:
        del self._sequence


# ─── concrete subclasses ─────────────────────────────────────────────────── ✦✦ ──

class BacterialGenome(Genome):
    """Represents a bacterial genome."""
    domain = Domain.BACTERIA

    def __init__(self, sequence, host) -> None:
        super().__init__(sequence)
        self.host = host

    # : properties

    @property
    def sequence(self) -> str:
        return self._sequence

    @sequence.setter
    def sequence(self, value) -> None:
        self._sequence = value

    @sequence.deleter
    def sequence(self) -> None:
        del self._sequence\

    # : class methods

    # : instance methods

    # : static methods

    def from_fasta(filepath: str | Path) -> "BacterialGenome":
        """Load a bacterial genome from a FASTA file."""
        try:
            from Bio import SeqIO

            record = SeqIO.read(filepath, "fasta")
            return BacterialGenome(record.seq, host=None)
        except ImportError:
            raise ImportError(
                "Biopython is required to load bacterial genomes from FASTA "
                "files. Please install it using 'pip install biopython'."
            )
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "Biopython is required to load bacterial genomes from FASTA"
                "files. Please install it using 'pip install biopython'."
            )
        except FileNotFoundError:
            raise FileNotFoundError(
                f"The file '{filepath}' does not exist or is not accessible."
            )
        except Exception as e:
            raise RuntimeError(
                f"An error occurred while reading the FASTA file: {e}"
            )

    def sequence_generator(self, length: int, iterations: int) -> str:
        """Iterate over the genome sequence in chunks of a given length."""
        start: int = 0

        while iterations > 0:
            end: int = start + length

            segment = self.sequence[start:end]
            yield segment
            
            start += length
            
            iterations -= 1

    def get_genome(self, chunk_length: int = 72) -> str:
        """Iterate over the entire genome sequence."""
        length: int = len(self._sequence)
        start: int = 0

        while start < length:
            yield str(self.sequence[start:start + chunk_length]).strip()

            start += chunk_length




class FungalGenome(Genome):
    """Represents a fungal genome."""
    domain = Domain.FUNGI

    def __init__(self, sequence, host) -> None:
        super().__init__(sequence)
        self.host = host

    @property
    def sequence(self) -> str:
        return self._sequence

    @sequence.setter
    def sequence(self, value) -> None:
        self._sequence = value

    @sequence.deleter
    def sequence(self) -> None:
        del self._sequence


class ViralGenome(Genome):
    """Represents a viral genome."""
    domain = Domain.VIRUSES

    def __init__(self, sequence, host) -> None:
        super().__init__(sequence)
        self.host = host

    @property
    def sequence(self) -> str:
        return self._sequence

    @sequence.setter
    def sequence(self, value) -> None:
        self._sequence = value

    @sequence.deleter
    def sequence(self) -> None:
        del self._sequence

