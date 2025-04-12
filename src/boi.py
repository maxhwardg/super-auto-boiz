"""
This module defines the Boi class, which represents a Boi entity in the game.
Also includes builder pattern for creating Boi instances.
"""

from typing import Dict, Callable, List, Optional
import uuid
from copy import deepcopy

from system import Event, System
from effect import Effect

BoiCallback = Callable[["Boi", System, Event], None]

MAX_BOI_LEVEL = 3
LEVEL_UP_EXPERIENCE = 3
MAX_HEALTH = 50
MAX_ATTACK = 50


class Boi:
    """
    Represents a Boi entity in the game.
    Each Boi has a unique ID and can be added to a team.
    """

    def __init__(self) -> None:
        super().__init__()
        self.type_name: str
        self.attack: int
        self.health: int
        self.level: int = 1
        self.experience: int = 0
        self.triggers: Dict[str, List[BoiCallback]] = {}
        self.effect: Optional[Effect] = None
        self.uuid: str = str(uuid.uuid4())

    def __repr__(self):
        return f"{self.type_name} ({self.attack}/{self.health})"

    def trigger(self, event: Event, system: System) -> None:
        """
        Trigger a type for this Boi.
        """
        if event.type in self.triggers:
            for callback in self.triggers[event.type]:
                callback(self, system, event)
        if self.effect:
            self.effect.trigger(event, system)

    def _sort_tuple(self) -> tuple:
        """
        Returns a tuple of the Boi's stats for sorting.
        """
        return (self.attack, self.health, self.uuid)

    def __lt__(self, other: "Boi") -> bool:
        """
        Compare bois based on their team position.
        """
        return self._sort_tuple() > other._sort_tuple()

    def is_dead(self) -> bool:
        """
        Check if the Boi is dead.
        """
        return self.health <= 0


def standard_damage_callback(boi: Boi, system: System, event: Event) -> None:
    """
    A standard damage callback for the Boi.
    Most bois should have this callback.
    """
    boi.health -= event.data["damage"]
    if boi.is_dead():
        killer = event.data["source"]
        system.send_event(Event(type="death", target=boi, source=killer))
        system.send_event(Event(type="killed", target=killer, source=boi))


def standard_levelup_callback(boi: Boi, system: System, event: Event) -> None:
    """
    A standard level up callback for the Boi.
    Most bois should have this callback.
    """
    boi.level += 1
    boi.experience = 0


def standard_item_callback(boi: Boi, system: System, event: Event) -> None:
    """
    A standard item callback for the Boi.
    Most bois should have this callback.
    """
    boi.effect = event.data["item"].effect_builder.build()


class BoiBuilder:
    """
    Builder for creating Boi instances.
    """

    def __init__(self) -> None:
        self.boi = Boi()
        self.add_trigger("damage", standard_damage_callback)
        self.add_trigger("levelup", standard_levelup_callback)
        self.add_trigger("item_used", standard_item_callback)

    def set_type_name(self, type_name: str) -> "BoiBuilder":
        """
        Set the type name of the Boi.
        """
        self.boi.type_name = type_name
        return self

    def set_attack(self, attack: int) -> "BoiBuilder":
        """
        Set the attack value of the Boi.
        """
        self.boi.attack = attack
        return self

    def set_health(self, health: int) -> "BoiBuilder":
        """
        Set the health value of the Boi.
        """
        self.boi.health = health
        return self

    def add_trigger(self, event_type: str, callback: Callable) -> "BoiBuilder":
        """
        Add a trigger for the Boi.
        """
        if event_type not in self.boi.triggers:
            self.boi.triggers[event_type] = []
        self.boi.triggers[event_type].append(callback)
        return self

    def add_default_effect(self, effect: Effect) -> "BoiBuilder":
        """
        Add a default effect to the Boi.
        This effect will be present when the Boi is created.
        """
        self.boi.effect = effect
        return self

    def build(self) -> Boi:
        """
        Build and return the Boi instance.
        """
        copied_boi = deepcopy(self.boi)
        copied_boi.uuid = str(uuid.uuid4())
        return copied_boi
