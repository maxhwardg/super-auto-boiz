"""
Foundational classes for the system/event framework.
"""

from abc import ABC, abstractmethod
from typing import Callable, List, Deque
from collections import deque
import uuid


class Event:
    """Base class for all system events."""

    # pylint: disable=redefined-builtin
    def __init__(self, type: str, **data) -> None:
        self.uuid = str(uuid.uuid4())
        self.type = type
        self.data = data


EventCallback = Callable[[Event], None]


class System(ABC):
    """
    Base class for all systems.
    All systems are event-driven.
    All systems have a queue of events to process.
    """

    def __init__(self) -> None:
        self.event_queue: Deque[Event] = deque()

    def send_event(self, event: Event):
        """Communicates an event to the system. Must be implemented by subclasses."""
        self.event_queue.append(event)

    def send_and_execute_event(self, event: Event):
        """Sends an event and executes it immediately."""
        self.send_event(event)
        self._process_all_queue_events()

    def _process_all_queue_events(self) -> None:
        """
        Processes elements on the event queue until the queue is empty.
        """
        while self.event_queue:
            self._process_queue_event(self.event_queue.popleft())

    @abstractmethod
    def _process_queue_event(self, event: Event) -> None:
        """
        Processes events in the queue.
        """
