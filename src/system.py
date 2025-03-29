"""
Foundational classes for the system/event framework.
"""

from abc import ABC, abstractmethod
import uuid


class Event:
    """Base class for all system events."""

    # pylint: disable=redefined-builtin
    def __init__(self, type: str, **data) -> None:
        self.uuid = str(uuid.uuid4())
        self.type = type
        self.data = data


class System(ABC):
    """Base class for all systems."""

    @abstractmethod
    def process_event(self, event: Event):
        """Process an event. Must be implemented by subclasses."""
