"""
This module defines the Boi class, which represents a Boi entity in the game.
Also includes builder pattern for creating Boi instances.
"""

from typing import Dict, Callable, List
import uuid
from copy import deepcopy

from system import Event, System


class Boi:
    """
    Represents a Boi entity in the game.
    Each Boi has a unique ID and can be added to a team.
    """

    def __init__(self) -> None:
        super().__init__()
        self.system: System
        self.team: int
        self.team_pos: int
        self.type_name: str
        self.attack: int
        self.max_attack: int
        self.health: int
        self.max_health: int
        self.triggers: Dict[str, List[Callable]] = {}
        self.uuid: str = str(uuid.uuid4())

    def __str__(self):
        return f"{self.type_name} ({self.uuid}) - {self.attack}/{self.max_attack} - {self.health}/{self.max_health} - Team {self.team} - Pos {self.team_pos}"

    def __repr__(self):
        return f"{self.type_name} ({self.uuid}) - {self.attack}/{self.max_attack} - {self.health}/{self.max_health} - Team {self.team} - Pos {self.team_pos}"

    def trigger(self, event: Event) -> None:
        """
        Trigger a type for this Boi.
        """
        if event.type in self.triggers:
            for callback in self.triggers[event.type]:
                callback(self)

    def _sort_tuple(self) -> tuple:
        """
        Returns a tuple of the Boi's stats for sorting.
        """
        return (self.max_attack, self.max_health, self.uuid)

    def __lt__(self, other: "Boi") -> bool:
        """
        Compare bois based on their team position.
        """
        return self._sort_tuple() > other._sort_tuple()


class BoiBuilder:
    """
    Builder for creating Boi instances.
    """

    def __init__(self) -> None:
        self.boi = Boi()

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
        self.boi.max_attack = attack
        return self

    def set_health(self, health: int) -> "BoiBuilder":
        """
        Set the health value of the Boi.
        """
        self.boi.health = health
        self.boi.max_health = health
        return self

    def add_trigger(self, event_type: str, callback: Callable) -> "BoiBuilder":
        """
        Add a trigger for the Boi.
        """
        if event_type not in self.boi.triggers:
            self.boi.triggers[event_type] = []
        self.boi.triggers[event_type].append(callback)
        return self

    def build(self) -> Boi:
        """
        Build and return the Boi instance.
        """
        return deepcopy(self.boi)
