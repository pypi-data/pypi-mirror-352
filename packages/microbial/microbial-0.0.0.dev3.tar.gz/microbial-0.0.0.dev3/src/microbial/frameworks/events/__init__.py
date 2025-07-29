"""Events

This module defines the base `Event` class, along with the `Eventful`
protocol and `EventType` enum for event-handling in the `microbial`
simulation framework.
"""
# : import statements

# local imports
from .event import Event
from .mutation import MutationEvent
from .protocol import Eventful
from .replication import ReplicationEvent


__all__ = [
    # : module exports
    "intercellular", "intraceullar",
    
    # : class exports
    "Event", "Eventful", "MutationEvent", "ReplicationEvent"
]
