"""Replication Event

This module defines the replication event class, which is used
to represent cell division events in the `microbial` simualation
framework.
"""

# : import statements

# standard library imports
from __future__ import annotations
from typing import Optional
from uuid import UUID, uuid4

# local imports
from .event import Event


# : event model

class ReplicationEvent(Event):
    """An event representing a replication action in the simulation."""
    def __init__(self, entity_id: UUID, seconds_from_now: int | float = 10.0):
        super().__init__()
        self._entity_id: UUID = entity_id
        self._seconds_from_now = seconds_from_now

    @property
    def entity_id(self) -> UUID:
        return self._entity_id

    @property
    def seconds_from_now(self) -> float:
        return self._seconds_from_now
