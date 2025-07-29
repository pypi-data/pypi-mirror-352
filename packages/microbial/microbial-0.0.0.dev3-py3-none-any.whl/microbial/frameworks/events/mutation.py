"""Mutation Event

This module defines the mutation event class, which is used to
represent individual instances of mutation in entities hosted
within the `microbial` simulation framework.
"""
# : import statements

# standard library imports
from uuid import uuid4, UUID

# local imports
from .event import Event


# : event model
class MutationEvent(Event):
    def __init__(
        self,
        entity_id: UUID,
        mutation_type: str,
        seconds_from_now: int | float
    ) -> None:
        self._id: UUID = uuid4()
        self.entity_id: UUID = entity_id
        self.mutation_type: str = mutation_type
        self.seconds_from_now: int | float = seconds_from_now


    # ─── properties ───────────────────────────────────────────────────────────

    @property
    def id(self) -> UUID:
        return self._id

    @id.setter
    def id(self, value: UUID) -> None:
        if isinstance(value, UUID):
            self._id = value
        else:
            raise TypeError(
                "`MutationEvent.id` must be an instance of `UUID`."
            )

    @id.deleter
    def id(self) -> UserWarning:
        raise UserWarning("""\
⚠︎ Warning:

It is not recommended to delete the `MutationEvent.id` attribute, as the event-
handling framework relies on unique identifiers to manage and track events
and to execute their associated routines. If you need to change the ID,
consider setting it to a new `UUID` instance, rather than deleting it outright.
""")
