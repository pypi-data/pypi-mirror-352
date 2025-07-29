"""Environment Framework

This module provides a framework for managing microenvironments and
their interactions with microbial communities.
"""
# ─── import statements ────────────────────────────────────────────────── ✦✦ ──
from __future__ import annotations

# standard library imports
import logging
import os
import sys

from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, TypeAlias, Union

# third-party imports
from platformdirs import (
    user_cache_path, user_config_path, user_data_path, user_log_path
)
from dotenv import load_dotenv

# local imports
from ..bacteria import Bacterium
from ..fungi import Fungus
from ..viruses import Virus

from .queue import Event, ReplicationEvent
from .scheduler import Scheduler

# load environment variables from .env file

print("Loading environment variables from .env file...")
load_dotenv()
print("Environment variables loaded.")

# get user directories

print("Setting up user directories...")
DATA_DIR: Path = user_data_path(
    "microbial",
    "k.lebryce",
    ensure_exists=True,
)
print(f"Data directory: {DATA_DIR}")

CACHE_DIR: Path = user_cache_path(
    "microbial",
    "k.lebryce",
    ensure_exists=True,
)
print(f"Cache directory: {CACHE_DIR}")

CONFIG_DIR: Path = user_config_path(
    "microbial",
    "k.lebryce",
    ensure_exists=True,
)
print(f"Config directory: {CONFIG_DIR}")

LOG_DIR: Path = user_log_path(
    "microbial",
    "k.lebryce",
    ensure_exists=True,
)
print(f"Log directory: {LOG_DIR}")


# initialize logging

print("Setting up logging...")
logging.basicConfig(
    level=logging.INFO
)
logger = logging.getLogger(__name__)
print("Logging setup complete.")

# ─── typing ───────────────────────────────────────────────────────────── ✦✦ ──
Entity: TypeAlias = Union[Bacterium, Fungus, Virus]
Population: TypeAlias = List[Entity]
Community: TypeAlias = Union[List[Population], List[Entity]]

class Microbe(Enum):
    BACTERIUM: Entity = Bacterium
    FUNGUS: Entity = Fungus
    VIRUS: Entity = Virus


# ─── interfaces ───────────────────────────────────────────────────────── ✦✦ ──

class Environment:
    """Base class for all microenvironments."""
    def __init__(self, name: str, description: Optional[str] = None):
        self.name: str = name
        self.description: Optional[str] = description
        self._communities: List[Community] = []
        self._entities: List[Entity] = []
        self._populations: List[Population] = []
        self._scheduler: Scheduler = Scheduler()


    # ─── properties ───────────────────────────────────────────────────────────

    @property
    def communities(self) -> List[Community]:
        return self._communities

    @communities.setter
    def communities(self, value: List[Community]) -> None:
        self._communities = value

    @communities.deleter
    def communities(self) -> None:
        self._communities.clear()

    @property
    def entities(self) -> List[Entity]:
        return self._entities

    @entities.setter
    def entities(self, value: List[Entity]) -> None:
        self._entities = value

    @entities.deleter
    def entities(self) -> None:
        self._entities.clear()

    @property
    def populations(self) -> List[Population]:
        return self._populations

    @populations.setter
    def populations(self, value: List[Population]) -> None:
        self._populations = value

    @populations.deleter
    def populations(self) -> None:
        self._populations.clear()

    @property
    def scheduler(self) -> Scheduler:
        return self._scheduler

    @scheduler.setter
    def scheduler(self, value: Scheduler) -> None:
        self._scheduler = (
            value if isinstance(value, Scheduler)
            else TypeError(
                "Argument `value` in the `Environment.scheduler` setter "
                "method must be an instance of `Scheduler`."
            )
        )

    @scheduler.deleter
    def scheduler(self) -> UserWarning:
        return UserWarning("""\
⚠︎ Warning:

Deleting the scheduler is not recommended as it is essential for the
operation of the event-handling framework. If you need to change the
scheduler, assign a new instance to the `scheduler` attribute, rather
than deleting it.
""")



    # ─── instance method defaults ─────────────────────────────────────────────

    def add_community(self, community: Community) -> None:
        self._communities.append(community)

    def remove_community(self, community: Community) -> None:
        self._communities.remove(community)

    def add_communities(self, communities: List[Community]) -> None:
        self._communities.extend(communities)

    def remove_communities(self, communities: List[Community]) -> None:
        for community in communities:
            self._communities.remove(community)

    def add_entity(self, entity: Entity) -> None:
        self._entities.append(entity)

    def remove_entity(self, entity: Entity) -> None:
        self._entities.remove(entity)

    def add_entities(self, entities: List[Entity]) -> None:
        self._entities.extend(entities)

    def remove_entities(self, entities: List[Entity]) -> None:
        for entity in entities:
            self._entities.remove(entity)

    def add_population(self, population: Population) -> None:
        self._populations.append(population)

    def remove_population(self, population: Population) -> None:
        self._populations.remove(population)

    def add_populations(self, populations: List[Population]) -> None:
        self._populations.extend(populations)

    def remove_populations(self, populations: List[Population]) -> None:
        for population in populations:
            self._populations.remove(population)

    def clear(self) -> None:
        self._communities.clear()
        self._entities.clear()
        self._populations.clear()

    def count(self, target: Union[Entity, Population, Community]) -> int:
        if isinstance(target, Entity):
            return self._entities.count(target)
        elif isinstance(target, Population):
            return self._populations.count(target)
        elif isinstance(target, Community):
            return self._communities.count(target)
        else:
            raise TypeError("Target must be an `Entity`, `Population`, or `Community`.")

    def count_all(self) -> Dict[str, int]:
        """Count all entities, populations, and communities."""
        return {
            "entities": len(self._entities),
            "populations": len(self._populations),
            "communities": len(self._communities)
        }

    def schedule_replication_event(
        self,
        event: ReplicationEvent
    ) -> Optional[Exception]:
        """Schedule an event with the scheduler.
            
        Returns:
            `True` if the event was scheduled successfully,
            otherwise raises an exception.
        """
        if isinstance(event, ReplicationEvent):
            try:
                self._scheduler.schedule_event(event)
                print(f"Event {event.id} scheduled successfully.")
            except Exception as e:
                logger.error(f"Failed to schedule event: {e}")
                raise e
        else:
            raise TypeError("Event must be an instance of `ReplicationEvent`.")

class InVivoEnvironment(Environment):
    """Models an in vivo microoenvironment."""
    def __init__(self, name: str, description: Optional[str] = None):
        super().__init__(name, description)
        self.type: str = "In Vivo"


class InVitroEnvironment(Environment):
    """Models an in vitro microoenvironment."""
    def __init__(self, name: str, description: Optional[str] = None):
        super().__init__(name, description)
        self.type: str = "In Vitro"

