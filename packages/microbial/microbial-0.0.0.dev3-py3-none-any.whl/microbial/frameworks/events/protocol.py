"""Events Protocol

This module defines protocols for event-handling.
"""
# : import statements

# standard library imports

from __future__ import annotations
from enum import Enum
from abc import ABC, abstractmethod
from typing import Any, Protocol, runtime_checkable
from uuid import uuid4, UUID

# : protocol definitions

@runtime_checkable
class Eventful(Protocol):
    """A protocol for objects that represent events."""
    id: UUID
    name: str

