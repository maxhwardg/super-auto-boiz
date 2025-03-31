"""
This module defines the Effect class, representing item and
other persistent effects in the game.
"""

from typing import Dict, Callable, List
import uuid
from copy import deepcopy

from system import Event, System

EffectCallback = Callable[["Effect", System, Event], None]  # Assuming Boi is accessible


class Effect:
    """
    Represents an effect, typically granted by an item.
    Effects have triggers similar to Bois.
    """

    def __init__(self) -> None:
        super().__init__()
        self.type_name: str
        self.uuid: str = str(uuid.uuid4())
        self.triggers: Dict[str, List[EffectCallback]] = {}

    def __repr__(self):
        return f"Effect({self.type_name})"

    def trigger(self, event: Event, system: System) -> None:
        """
        Trigger callbacks associated with this effect for a given event type.
        The 'boi' parameter is the Boi instance holding the item/effect.
        """
        if self.triggers and event.type in self.triggers:
            for callback in self.triggers[event.type]:
                callback(self, system, event)


class EffectBuilder:
    """
    Builder for creating Effect instances.
    """

    def __init__(self) -> None:
        self.effect = Effect()

    def set_name(self, name: str) -> "EffectBuilder":
        """
        Set the name of the Effect.
        """
        self.effect.type_name = name
        return self

    def add_trigger(self, event_type: str, callback: EffectCallback) -> "EffectBuilder":
        """
        Add a trigger for the Effect.
        """
        if event_type not in self.effect.triggers:
            self.effect.triggers[event_type] = []
        self.effect.triggers[event_type].append(callback)
        return self

    def build(self) -> Effect:
        """
        Build and return the Effect instance.
        Creates a deep copy to ensure unique effects unless intended otherwise.
        Assigns a new UUID.
        """
        copied_effect = deepcopy(self.effect)
        copied_effect.uuid = str(uuid.uuid4())
        return copied_effect
