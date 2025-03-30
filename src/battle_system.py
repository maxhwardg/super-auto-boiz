"""
Module for the BattleSystem class.
"""

from typing import List, Optional, Callable

from boi import Boi
from team_system import TeamSystem, Team
from system import Event


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
        self.battle_over = False
        self.winner: Optional[int] = None
        self.event_callbacks = event_callbacks
        self._start_battle()

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
        for boi in self._all_bois_in_event_order():
            self.send_event(Event(type="battle_turn_start", target=boi))
        self._process_all_queue_events()

        # Process attacks
        attackers = sorted(
            [self._first_boi(self.teams[0]), self._first_boi(self.teams[1])]
        )

        for boi in attackers:
            other_boi = self._first_boi(self.other_team(boi))
            self.send_event(Event(type="attack", target=boi))
            self.send_event(
                Event(
                    type="damage",
                    target=other_boi,
                    source=boi,
                    damage=boi.attack,
                )
            )
        self._process_all_queue_events()

        # Process turn end events
        for boi in self._all_bois_in_event_order():
            self.send_event(Event(type="battle_turn_end", target=boi))

        self._process_all_queue_events()

        # Check if battle is over
        self._check_battle_over()

    def _process_queue_event(self, event: Event) -> None:
        for callback in self.event_callbacks:
            callback(event)
        # If the event has a target make sure to notify them
        if "target" in event.data:
            self._handle_target_boi(event)
        # Generally, the BattleSystem should just pass on events
        # However, death is a special event type
        # Since it leads to the removal of a Boi from their team
        if event.type == "death":
            self._handle_death(event)

    def _check_battle_over(self) -> None:
        if len(self.teams[0].bois) == 0 and len(self.teams[1].bois) == 0:
            self.battle_over = True
            self.winner = None
        if len(self.teams[0].bois) == 0:
            self.battle_over = True
            self.winner = 1
        elif len(self.teams[1].bois) == 0:
            self.battle_over = True
            self.winner = 0

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

    def _start_battle(self) -> None:
        """
        Runs battle start events.
        """
        for boi in self._all_bois_in_event_order():
            self.send_event(Event(type="battle_start", target=boi))
        self._process_all_queue_events()

    def _first_boi(self, team: Team) -> Boi:
        """
        Returns the first Boi in the specified team.
        """
        if len(team.bois) == 0:
            raise ValueError("No bois in this team.")
        return team.bois[0]

    def _all_bois_in_event_order(self) -> List[Boi]:
        """
        Returns all bois in order.
        """
        return sorted(self.teams[0].bois + self.teams[1].bois)
