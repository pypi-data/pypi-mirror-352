"""Scheduler Framework

This module provides the `Scheduler` class for managing and scheduling
event execution in the microbial framework.
"""
from __future__ import annotations

# : import statements
from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import datetime as dt
from heapq import (
    heapify, heappush, heappop, heapreplace, nsmallest
)
from typing import Optional, Union
from uuid import uuid4, UUID

from .queue import Event, Queue


# : interfaces

class Scheduler(ABC):
    """Base class for event scheduling."""
    
    def __new__(cls, *args, **kwargs):
        """Ensure only one instance of Scheduler is created."""
        if not hasattr(cls, "_instance"):
            cls._instance = super(Scheduler, cls).__new__(cls)
        return cls._instance


    def __init__(self) -> None:
        self._id: UUID = uuid4()

        # initialize a priority queue for events
        self._events = Queue()
        

    # : properties

#     @property
#     def environment(self) -> Environment:
#         return self._environment
#
#     @environment.setter
#     def environment(self, value: Environment) -> None:
#         if isinstance(value, Environment):
#             self._environment = value
#         raise TypeError(
#             "Value must be an instance of `Environment`."
#         )
#
#     @environment.deleter
#     def environment(self) -> None:
#         return UserWarning("""\
# ⚠︎ Warning:
#
# The environment should not be deleted as it is essential for
# the scheduler's operation. If you need to change the
# environment, assign a new instance to the `environment`
# property instead of deleting it.
# """
# )

    @property
    def events(self) -> Queue:
        return self._events

    @events.setter
    def events(self, value: Queue) -> Optional[Exception]:
        self._events = (
            value if isinstance(value, Queue)
            else TypeError(
                "Argument `value` in the `Scheduler.events` setter "
                "method must be an instance of `Queue`."
            )
        )


    # : instance methods

    def schedule_event(self, event: Event) -> bool:
        """Enqueue an event for execution."""
        if not isinstance(event, Event):
            raise TypeError("Event must be an instance of `Event`.")

        self._validate_event(event)

        if event.is_valid:
            self.events.add_event(event)


    def _validate_event(self, event: Event) -> bool:
        """Validate the event before scheduling.

        Returns:
            `True` if the event is valid; raises `ValueError`
            otherwise.
        """
        return (
            True if event not in self._events
            else ValueError("Event is already scheduled.")
        )
    
    @property
    def id(self) -> UUID:
        return self._id

    @id.setter
    def id(self, value: UUID) -> bool:
        """Set the unique identifier for the event.

        Args:
          value (UUID):
            The unique identifier for the event.

        Returns:
            `True` if the ID is set successfully; raises `TypeError`
            otherwise.
        """    
        if isinstance(value, UUID):
            self._id = value
            return True
        raise TypeError("Scheduler ID must be a UUID instance.")

    @id.deleter
    def id(self) -> UserWarning:
        """Delete the event's ID.

        Raises:
            `UserWarning` to discourage deletion of event IDs.
        """
        return UserWarning(
            """\
⚠︎ Warning:

Scheduler IDs should not be deleted as they are crucial for the operation
of the scheduler and event handling system. If you need to set a new ID,
you can do so by assigning a new UUID instance via the `id` setter.
"""
)

    # ─── instance methods ─────────────────────────────────────────────────────
    # def __repr__(self) -> str:
    #     return (
    #         f"Event(id={self.id}, "
    #         f"timestamp={self.timestamp}, "
    #         f"is_valid={self.is_valid})"
    #     )
    #
    # def __str__(self) -> str:
    #     return (
    #         f"Event {self.id} (Valid)" if self.is_valid
    #         else f"Event {self.id} (Invalid)"
    #     )
    #
    # def __eq__(self, other: object) -> bool:
    #     return (
    #         TypeError if not isinstance(other, Event)
    #         else True if self.id == other.id
    #         else False
    #     )
    #
    # def __hash__(self) -> int:
    #     hash(self.id)
    #
    # def cancel(self) -> None:
    #     """Mark the event as invalid."""
    #     self.is_valid = False
    #     print("Canceled event: ", self.id)
