"""Base Event Class

This module defines the base event class for all events in the
simulation.
"""
from __future__ import annotations
from abc import ABC
from datetime import datetime as dt
from datetime import timedelta as td
from uuid import uuid4, UUID

class Event(ABC):
    """Base class for all events in the simulation framework."""
    def __init__(self):
        self._id: UUID = uuid4()
        self._is_valid: bool = True
        self._timestamp: dt = dt.now()


    # : properties

    @property
    def id(self) -> UUID:
        return self._id

    @id.setter
    def id(self, value: UUID) -> None:
        self._id = (
            value if isinstance(value, UUID)
            else TypeError("`.id` must be an instance of `UUID`.")
        )

    @id.deleter
    def id(self) -> UserWarning:
        return("""\
⚠︎ Warning:

Event IDs should not be deleted. If you need to set the event's `.id`
attribute to a different unique identifier, set it to a new `UUID`
instance.
""")

    @property
    def is_valid(self) -> bool:
        return self._is_valid

    @is_valid.setter
    def is_valid(self, value: bool) -> None:
        self._is_valid = (
            value if isinstance(value, bool)
            else TypeError("`.is_valid` must be a boolean value.")
        )

    @is_valid.deleter
    def is_valid(self) -> None:
        self._is_valid = False

