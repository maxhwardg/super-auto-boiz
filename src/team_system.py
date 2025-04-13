"""
This module contains the TeamSystem class.
This is the base class for team-related systems in the game.
These include the BattleSystem and the ShopSystem.
"""

from typing import List, Optional
from abc import ABC, abstractmethod

from boi import Boi
from system import System, Event, EventCallback
from team import Team


class TeamSystem(System, ABC):
    """
    The TeamSystem manages teams of bois.
    This the base class for team-related systems in the game.
    These include the BattleSystem and the ShopSystem.
    These systems have either 2 or 1 teams respectively.
    They also operate using an event queue.
    This class includes these functionalities.
    """

    def __init__(self, teams: List[Team], event_callbacks: List[EventCallback]) -> None:
        super().__init__()
        self.event_callbacks = event_callbacks
        self.teams = teams

    def send_event(self, event: Event) -> None:
        """
        Process an event related to the team system.
        Since an event queue is used, simply add it without processing it.
        Events are processed by the _process_all_queue_events method.
        """
        self.event_queue.append(event)

    def num_teams(self) -> int:
        """
        Returns the number of teams.
        Can be used to check if the system is a BattleSystem or a ShopSystem.
        """
        return len(self.teams)

    def replace_boi(self, boi: Boi, with_boi: Boi) -> None:
        """
        Replaces the specified Boi with another Boi in the team system.
        This puts the new boi in the same team and position as the old one.
        """
        team = self.boi_team(boi)
        if team is None:
            raise ValueError("Boi not found in any team")
        idx = self.teams[team].bois.index(boi)
        self.teams[team].bois[idx] = with_boi

    def boi_team(self, boi: Boi) -> Optional[int]:
        """
        Returns the team number of the specified Boi.
        """
        for i, team in enumerate(self.teams):
            if boi in team.bois:
                return i
        return None

    def other_team(self, boi: Boi) -> Team:
        """
        Returns the other team of the specified Boi.
        E.g., the enemy team in a battle.
        Returns an empty team if there aren't exactly 2 teams.
        """
        if self.num_teams() != 2:
            return Team([])  # Empty team if not a battle system
        team_number = self.boi_team(boi)
        assert team_number is not None, "Boi not found in any team"
        return self.teams[1 - team_number]

    def _remove_boi(self, boi: Boi):
        """
        Removes the specified Boi from the battle.
        """
        for team in self.teams:
            if boi in team.bois:
                team.bois.remove(boi)
                break  # Assumes bois are unique to teams

    def _notify_callbacks(self, event: Event):
        """Notify all registered callbacks of the event."""
        for callback in self.event_callbacks:
            callback(event)

    def _process_queue_event(self, event: Event) -> None:
        self._notify_callbacks(event)
        # If the event has a target make sure to notify them
        if "target" in event.data:
            self._handle_target_boi(event)
        # Generally, the BattleSystem should just pass on events
        # However, death is a special event type
        # Since it leads to the removal of a Boi from their team
        if event.type == "death":
            self._handle_death(event)

    def _handle_target_boi(self, event: Event) -> None:
        """
        Handle the targeting of a Boi in the battle with the given event.
        """
        target = event.data["target"]
        assert isinstance(target, Boi)
        target.trigger(event, self)

    def _handle_death(self, event: Event) -> None:
        """
        Handle the death of a Boi in the battle with the given event.
        """
        # Assume target is already validated
        self._remove_boi(event.data["target"])
