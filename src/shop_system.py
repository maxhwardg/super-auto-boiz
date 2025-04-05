from typing import Callable, List

from system import Event
from team_system import TeamSystem
from team import Team
from boi import Boi
from item import Item
from pack import Pack


class ShopSystem(TeamSystem):
    """
    Manages the shop system in the game.
    Allows buying/selling items and bois.
    Allows rolling for new items and bois.
    """

    def __init__(
        self,
        team: Team,
        pack: Pack,
        tier: int,
        money: int,
        event_callbacks: List[Callable[[Event], None]],
    ) -> None:
        super().__init__([team], event_callbacks)
        self.pack = pack
        self.tier = tier
        self.money = money

    def get_team(self) -> Team:
        """
        Returns the team in the shop
        """
        return self.teams[0]

    def _process_queue_event(self, event: Event) -> None:
        """
        Processes events in the queue.
        """
        super()._process_queue_event(event)
        # Handle events related to the shop system
        match event.type:
            case "buy_item":
                self._buy_item(event)
            case "buy_boi":
                self._buy_boi(event)
            case "sell_boi":
                self._sell_boi(event)
            case "merge_boi":
                self._merge_boi(event)
            case "swap_boi":
                self._swap_boi(event)
            case "roll":
                self._roll()
            case _:
                raise ValueError(f"Unknown event type: {event.type}")

    def _roll(self) -> None:
        """
        Roll for new items and bois.
        """
        # TODO
        pass

    def _buy_item(self, event: Event) -> None:
        # TODO
        pass

    def _buy_boi(self, event: Event) -> None:
        # TODO
        pass

    def _sell_boi(self, event: Event) -> None:
        # TODO
        pass

    def _merge_boi(self, event: Event) -> None:
        # TODO
        pass

    def _swap_boi(self, event: Event) -> None:
        # TODO
        pass
