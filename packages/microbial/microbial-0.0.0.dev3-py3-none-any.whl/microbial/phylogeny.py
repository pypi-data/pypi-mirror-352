"""Phylogeny

This module defines the package's phylogenetic analysis interface.
"""
# ─── import statements ────────────────────────────────────────────────── ✦✦ ─
from typing import Optional


# ─── data containers ──────────────────────────────────────────────────── ✦✦ ─
class Phylogeny:
    """
    A data container for representing an organism's phylogeny.
    """
    def __init__(
        self,
        kingdom: Optional[str] = None,
        phylum: Optional[str] = None,
        rclass: Optional[str] = None,
        order: Optional[str] = None,
        family: Optional[str] = None,
        genus: Optional[str] = None,
        species: Optional[str] = None
    ) -> None:
        """Constructor

        Initializes an instance of the `Phylogeny` class.

        Args:
            kingdom: A string representing the organism's taxonomic kingdom.
            phylum: A string representing the organism's taxonomic phylum.
            rclass: A string representing the organism's taxonomic class.
            order: A string representing the organism's taxonomic order.
            family: A string representing the organism's taxonomic family.
            genus: A string representing the organism's taxonomic genus.
            species: A string representing the organism's taxonomic species.
        
        Returns:
            None.
        """
        self._kingdom: Optional[str] = kingdom
        self._phylum: Optional[str] = phylum
        self._rclass: Optional[str] = rclass
        self._subclass: Optional[str] = None
        self._order: Optional[str] = order
        self._suborder: Optional[str] = None
        self._family: Optional[str] = family
        self._subfamily: Optional[str] = None
        self._genus: Optional[str] = genus
        self._species: Optional[str] = species
        self._subspecies: Optional[str] = None

    
    # ─── properties ──────────────────────────────────────────────────────────
    # Kingdom
    @property
    def kingdom(self) -> str:
        return str(self._kingdom)
    
    @kingdom.setter
    def kingdom(self, value) -> None:
        self._kingdom = value
    
    @kingdom.deleter
    def kingdom(self) -> None:
        del self._kingdom
    
    # Phylum
    @property
    def phylum(self) -> str:
        return str(self._phylum)
    
    @phylum.setter
    def phylum(self, value) -> None:
        self._phylum = value
    
    @phylum.deleter
    def phylum(self) -> None:
        del self._phylum
    
    # Class
    @property
    def rclass(self) -> str:
        return str(self._rclass)
    
    @rclass.setter
    def rclass(self, value) -> None:
        self._rclass = value
    
    @rclass.deleter
    def rclass(self) -> None:
        del self._rclass

    # Subclass
    @property
    def subclass(self) -> str:
        return str(self._subclass)
    
    @subclass.setter
    def subclass(self, value) -> None:
        self._subclass = value
    
    # Order
    @property
    def order(self) -> str:
        return str(self._order)
    
    @order.setter
    def order(self, value) -> None:
        self._order = value
    
    @order.deleter
    def order(self) -> None:
        del self._order

    # Suborder
    @property
    def suborder(self) -> str:
        return str(self._suborder)
    
    @suborder.setter
    def suborder(self, value) -> None:
        self._suborder = value
    
    @suborder.deleter
    def suborder(self) -> None:
        del self._suborder
    
    # Family
    @property
    def family(self) -> str:
        return str(self._family)
    
    @family.setter
    def family(self, value) -> None:
        self._family = value
    
    @family.deleter
    def family(self) -> None:
        del self._family
    
    # Subfamily
    @property
    def subfamily(self) -> str:
        return str(self._subfamily)
    
    @subfamily.setter
    def subfamily(self, value) -> None:
        self._subfamily = value
    
    @subfamily.deleter
    def subfamily(self) -> None:
        del self._subfamily
    
    # Genus
    @property
    def genus(self) -> str:
        return str(self._genus)
    
    @genus.setter
    def genus(self, value) -> None:
        self._genus = value
    
    @genus.deleter
    def genus(self) -> None:
        del self._genus
    
    # Species
    @property
    def species(self) -> str:
        return str(self._species)
    
    @species.setter
    def species(self, value) -> None:
        self._species = value

    @species.deleter
    def species(self) -> None:
        del self._species
