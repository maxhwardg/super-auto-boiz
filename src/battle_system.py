"""
Module for the BattleSystem class.
"""

from typing import List, Optional, Callable

from boi import Boi
from team_system import TeamSystem, Team
from system import Event


def other_team_number(team_number: int) -> int:
    """
    Returns the other team number.
    """
    if team_number not in [0, 1]:
        raise ValueError("Team number must be 0 or 1.")
    return 1 - team_number


class BattleSystem(TeamSystem):
    """
    The BattleSystem handles the battle logic in the game.
    It processes events related to battles and manages the state of the battle.
    """

    def __init__(
        self, team0: Team, team1: Team, event_callbacks: List[Callable] | None = None
    ) -> None:
        if event_callbacks is None:
            event_callbacks = []
        super().__init__([team0, team1])
        # Assign bois their team and position
        for team_id, team in enumerate(self.teams):
            for boi_id, boi in enumerate(team.bois):
                boi.team = team_id
                boi.team_pos = boi_id
        self.battle_over = False
        self.winner: Optional[int] = None
        self.event_callbacks = event_callbacks
        self.event_log: List[Event] = []
        self._start_battle()

    def process_event(self, event: Event) -> None:
        """
        Process an event related to the battle system.
        """
        for callback in self.event_callbacks:
            callback(event)
        self._process_team_system_events(event)

    def is_battle_over(self) -> bool:
        """
        Returns True if the battle is over, False otherwise.
        """
        return self.battle_over

    def get_winner(self) -> Optional[int]:
        """
        Returns the winning team if the battle is over.
        """
        if self.battle_over:
            return self.winner
        return None

    def run_turn(self) -> None:
        """
        Run a turn in the battle.
        """
        if self.battle_over:
            raise RuntimeError("Battle is already over.")

        # Process turn start events
        for boi in self._all_bois_in_order():
            self.process_event(
                Event(type="battle_turn_start", target_boi=(boi.team, boi.team_pos))
            )

        self._process_deaths()

        # Process attacks
        attackers = sorted([self._first_boi(0), self._first_boi(1)])

        for boi in attackers:
            other_boi = self._first_boi(other_team_number(boi.team))
            self.process_event(
                Event(type="attack", target_boi=(boi.team, boi.team_pos))
            )
            self.process_event(
                Event(type="attacked", target_boi=(other_team_number(boi.team), 0))
            )
            self.process_event(
                Event(
                    type="damage",
                    target_boi=(other_boi.team, other_boi.team_pos),
                    damage=boi.attack,
                )
            )

        self._process_deaths()

        # Process turn end events
        for boi in self._all_bois_in_order():
            self.process_event(
                Event(type="battle_turn_end", target_boi=(boi.team, boi.team_pos))
            )

        self._process_deaths()

        # Check if battle is over
        if len(self.teams[0].bois) == 0 and len(self.teams[1].bois) == 0:
            self.battle_over = True
            self.winner = None
        if len(self.teams[0].bois) == 0:
            self.battle_over = True
            self.winner = 1
        elif len(self.teams[1].bois) == 0:
            self.battle_over = True
            self.winner = 0

    def _process_deaths(self) -> None:
        while True:
            any_deaths = False
            to_remove = []
            for boi in self._all_bois_in_order():
                if self._is_dead(boi):
                    self.process_event(
                        Event(type="death", target_boi=(boi.team, boi.team_pos))
                    )
                    any_deaths = True
                    to_remove.append(boi)
            for boi in to_remove:
                self._remove_boi(boi)
            if not any_deaths:
                break

    def _start_battle(self) -> None:
        """
        Runs battle start events.
        """
        for boi in self._all_bois_in_order():
            self.process_event(
                Event(type="battle_start", target_boi=(boi.team, boi.team_pos))
            )

    def _first_boi(self, team_id: int) -> Boi:
        """
        Returns the first Boi in the specified team.
        """
        if team_id not in [0, 1]:
            raise ValueError("Invalid team ID.")
        if len(self.teams[team_id].bois) == 0:
            raise ValueError("No bois in this team.")
        return self.teams[team_id].bois[0]

    def _all_bois_in_order(self) -> List[Boi]:
        """
        Returns all bois in order.
        """
        return sorted(self.teams[0].bois + self.teams[1].bois)
