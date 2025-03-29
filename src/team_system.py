"""
This module contains the TeamSystem class.
This is the base class for team-related systems in the game.
These include the BattleSystem and the ShopSystem.
"""

from typing import List

from boi import Boi
from system import System, Event
from team import Team


class TeamSystem(System):
    """
    The TeamSystem manages teams of bois.
    """

    def __init__(self, teams: List[Team]) -> None:
        super().__init__()
        self.teams = teams

    def _process_team_system_events(self, event: Event) -> None:
        """
        Process team system events.
        Currently, this is targeting bois and teams.
        """
        if "target_boi" in event.data:
            self._handle_target_boi(event)
        if "target_team" in event.data:
            self._handle_target_team(event)
        if event.type == "damage":
            self._handle_damage(event)

    def _get_target_boi(self, event: Event) -> Boi:
        team_id, boi_id = event.data["target_boi"]
        return self.teams[team_id].bois[boi_id]

    def _handle_damage(self, event: Event) -> None:
        boi = self._get_target_boi(event)
        boi.health -= event.data["damage"]

    def _handle_target_boi(self, event: Event) -> None:
        """
        Handle the targeting of a Boi in the battle with the given event.
        """
        team_id, boi_id = event.data["target_boi"]
        self._validate_target(boi_id, team_id)
        self.teams[team_id].bois[boi_id].trigger(event)

    def _handle_target_team(self, event: Event) -> None:
        """
        Handle the targeting of every boi in a team.
        """
        team_id = event.data["target_team"]
        if team_id not in [0, 1]:
            return
        for boi in self.teams[team_id].bois:
            boi.trigger(event)

    def _validate_target(self, boi_id: int, team_id: int) -> None:
        """
        Validate the target Boi and Team.
        """
        if team_id not in [0, 1]:
            raise ValueError("Invalid team ID.")
        if boi_id < 0 or boi_id >= len(self.teams[team_id].bois):
            raise ValueError("Invalid boi ID.")

    def _is_dead(self, boi: Boi) -> bool:
        """
        Returns True if the specified Boi is dead, False otherwise.
        """
        return boi.health <= 0

    def _remove_boi(self, boi: Boi):
        """
        Removes the specified Boi from the battle.
        """
        if boi not in self.teams[boi.team].bois:
            raise ValueError("Boi not in this team.")
        self.teams[boi.team].bois.remove(boi)
        # Renumerate bois in the team
        self._renumerate_bois(boi.team)

    def _renumerate_bois(self, team_id: int) -> None:
        """
        Renumerate bois in both teams.
        """
        if team_id not in [0, 1]:
            raise ValueError("Invalid team ID.")
        for i, boi in enumerate(self.teams[team_id].bois):
            boi.team_pos = i
