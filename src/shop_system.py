from typing import Callable, List, Any, cast
import random

from system import Event
from team_system import TeamSystem
from team import Team, MAX_TEAM_SIZE
from boi import Boi, MAX_BOI_LEVEL, LEVEL_UP_EXPERIENCE, MAX_ATTACK, MAX_HEALTH
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
        roll_price: int = 1,
        boi_price: int = 3,
    ) -> None:
        super().__init__([team], event_callbacks)
        self.pack = pack
        self.tier = tier
        self.money = money
        self.shop_bois: List[Boi] = []
        self.shop_items: List[Item] = []
        self.frozen_bois: List[Boi] = []
        self.frozen_items: List[Item] = []
        self._roll_price = roll_price
        self._boi_price = boi_price

        if tier < 1 or tier > pack.num_tiers:
            raise ValueError("Invalid tier")

        # Initially populate the shop
        self._free_roll()

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
            case "buy_and_merge_boi":
                self._buy_and_merge_boi(event)
            case "swap_boi":
                self._swap_boi(event)
            case "roll":
                self._roll()
            case "toggle_freeze_item":
                self._toggle_freeze_item(event)
            case "toggle_freeze_boi":
                self._toggle_freeze_boi(event)
            case _:
                pass

    def valid_roll(self) -> bool:
        """
        Check if the current tier is valid for rolling.
        """
        return self.money >= self._roll_price

    def _free_roll(self) -> None:
        """
        Roll for new items and bois.
        Clears current shop offerings and generates new ones based on the current tier.
        This is a free roll.
        """

        # Clear current shop offerings
        self.shop_bois = []
        self.shop_items = []

        # Add frozen items and bois to the shop
        self.shop_bois.extend(self.frozen_bois)
        self.shop_items.extend(self.frozen_items)

        # Generate new bois for the shop
        boi_builders = []
        for tier in range(1, self.tier + 1):
            boi_builders.extend(self.pack.tiers[tier - 1].boi_builders)
        num_bois = self.pack.tiers[self.tier - 1].shop_num_bois
        for _ in range(min(num_bois, len(boi_builders))):
            boi_template = random.choice(boi_builders)
            self.shop_bois.append(boi_template.build())

        # Generate new items for the shop
        available_items = []
        for tier in range(1, self.tier + 1):
            available_items.extend(self.pack.tiers[tier - 1].item_builders)
        num_items = self.pack.tiers[self.tier - 1].shop_num_items
        for _ in range(min(num_items, len(available_items))):
            self.shop_items.append(random.choice(available_items).build())

    def _roll(self) -> None:
        """
        Roll for new items and bois.
        This is a paid roll.
        """
        if not self.valid_roll():
            raise ValueError("Not enough money to roll")
        # Deduct the roll price
        self.money -= self._roll_price
        # Perform a free roll
        self._free_roll()

    def valid_buy_item(self, item: Any, target_boi: Any) -> bool:
        """
        Check if the item can be bought.
        """

        if not isinstance(item, Item):
            raise ValueError("Invalid item type")
        if not isinstance(target_boi, Boi):
            raise ValueError("Invalid target boi type")

        return (
            item in self.shop_items
            and self.money >= item.price
            and target_boi in self.get_team().bois
        )

    def _buy_item(self, event: Event) -> None:
        """
        Process buying an item from the shop.

        The event should have:
        - 'item': The Item object to buy
        - 'target_boi': The Boi to give the item to
        """
        item = event.data.get("item")
        target_boi = event.data.get("target_boi")

        if not self.valid_buy_item(item, target_boi):
            raise ValueError("Invalid item or not enough money")

        item = cast(Item, item)
        target_boi = cast(Boi, target_boi)

        # Process the purchase
        self.money -= item.price
        self.shop_items.remove(item)

        # Send event for purchase
        self.send_event(Event(type="item_used", target=target_boi, item=item))

    def valid_buy_boi(self, boi: Any) -> bool:
        """
        Check if the boi can be bought.
        """

        if not isinstance(boi, Boi):
            raise ValueError("Invalid boi type")

        return (
            boi in self.shop_bois
            and self.money >= self._boi_price
            and len(self.get_team().bois) < MAX_TEAM_SIZE
        )

    def _buy_boi(self, event: Event) -> None:
        """
        Process buying a boi from the shop.

        The event should have:
        - 'boi': The Boi object to buy
        - 'callback': Function to notify of success/failure
        """
        boi = event.data.get("boi")

        # Validate boi exists in shop
        if not self.valid_buy_boi(boi):
            raise ValueError("Invalid boi or not enough money")
        boi = cast(Boi, boi)

        # Process the purchase
        self.money -= self._boi_price
        self.get_team().bois.append(boi)
        self.shop_bois.remove(boi)

        # Send event for purchase
        self.send_event(Event(type="purchased", target=boi))

    def valid_sell_boi(self, boi: Any) -> bool:
        """
        Check if the boi can be sold.
        """

        if not isinstance(boi, Boi):
            raise ValueError("boi isn't even a Boi!")

        return boi in self.get_team().bois

    def _sell_boi(self, event: Event) -> None:
        """
        Process selling a boi from the team.
        A boi is worth their level in money.

        The event should have:
        - 'boi': The Boi object to sell
        """
        boi = event.data.get("boi")

        if not self.valid_sell_boi(boi):
            raise ValueError("Invalid boi for selling")

        boi = cast(Boi, boi)

        # Process the sale
        self.money += boi.level
        self.get_team().bois.remove(boi)

        # Send event for sale
        self.send_event(Event(type="sold", target=boi))

    def valid_merge_boi(self, target_boi: Any, source_boi: Any) -> bool:
        """
        Check if the bois can be merged.
        """

        if not isinstance(target_boi, Boi):
            raise ValueError("Invalid target boi type")
        if not isinstance(source_boi, Boi):
            raise ValueError("Invalid source boi type")

        return (
            target_boi in self.get_team().bois
            and source_boi in self.get_team().bois
            and target_boi.type_name == source_boi.type_name
        )

    def _merge_boi(self, event: Event) -> None:
        """
        Process merging two bois to increase the experience of the target boi.
        If experience hits 3, the target boi levels up.

        The event should have:
        - 'target_boi': The main Boi to keep and level up
        - 'source_boi': The Boi to merge into the target
        """
        target_boi = event.data.get("target_boi")
        source_boi = event.data.get("source_boi")

        if not self.valid_merge_boi(target_boi, source_boi):
            raise ValueError("Invalid bois for merging")

        target_boi = cast(Boi, target_boi)
        source_boi = cast(Boi, source_boi)

        # Merge the bois

        # Update experience
        target_boi.experience += (
            source_boi.experience + (source_boi.level - 1) * LEVEL_UP_EXPERIENCE + 1
        )

        # Update stats
        max_health = max(target_boi.health, source_boi.health)
        max_attack = max(target_boi.attack, source_boi.attack)
        target_boi.attack = min(MAX_ATTACK, max_attack + 1)
        target_boi.health = min(MAX_HEALTH, max_health + 1)

        # Handle level up(s)
        while (
            target_boi.experience >= LEVEL_UP_EXPERIENCE
            and target_boi.level < MAX_BOI_LEVEL
        ):
            target_boi.experience -= LEVEL_UP_EXPERIENCE
            target_boi.level += 1
            self.send_event(Event(type="levelup", target=target_boi))
        if target_boi.level == MAX_BOI_LEVEL:
            target_boi.experience = 0
        assert target_boi.level <= MAX_BOI_LEVEL, "Boi level exceeded maximum"

        # Remove the source boi from the team
        team = self.get_team()
        team.bois.remove(source_boi)

    def valid_buy_and_merge_boi(self, bought: Any, target: Any) -> bool:
        """
        Check if the boi can be bought and merged.
        """

        if not isinstance(bought, Boi):
            raise ValueError("Invalid bought boi type")
        if not isinstance(target, Boi):
            raise ValueError("Invalid target boi type")

        if bought not in self.shop_bois:
            return False
        if target not in self.get_team().bois:
            return False
        if bought.type_name != target.type_name:
            return False
        if self.money < self._boi_price:
            return False
        return True

    def _buy_and_merge_boi(self, event: Event) -> None:
        """
        Process buying and merging a boi from the shop.

        The event should have:
        - 'bought': The Boi object to buy
        - 'target': The Boi to merge into
        """
        bought = event.data.get("bought")
        target = event.data.get("target")

        if not self.valid_buy_and_merge_boi(bought, target):
            raise ValueError("Invalid bois for buying and merging")

        bought = cast(Boi, bought)
        target = cast(Boi, target)

        # Process the purchase
        self.money -= self._boi_price
        self.shop_bois.remove(bought)

        self.teams[0].bois.append(bought)

        # Merge the bois
        self._merge_boi(Event(type="merge_boi", target_boi=target, source_boi=bought))

    def valid_swap_boi(self, boi1: Any, boi2: Any) -> bool:
        """
        Check if the bois can be swapped.
        """

        if not isinstance(boi1, Boi):
            raise ValueError("Invalid first boi type")
        if not isinstance(boi2, Boi):
            raise ValueError("Invalid second boi type")

        return (
            boi1 in self.get_team().bois
            and boi2 in self.get_team().bois
            and boi1 != boi2
        )

    def _swap_boi(self, event: Event) -> None:
        """
        Process swapping the positions of two bois in the team.

        The event should have:
        - 'boi1': The first Boi to swap
        - 'boi2': The second Boi to swap
        """
        boi1 = event.data.get("boi1")
        boi2 = event.data.get("boi2")
        if not self.valid_swap_boi(boi1, boi2):
            raise ValueError("Invalid bois for swapping")
        boi1 = cast(Boi, boi1)
        boi2 = cast(Boi, boi2)
        # Swap the bois in the team
        team = self.get_team()
        idx1 = team.bois.index(boi1)
        idx2 = team.bois.index(boi2)
        team.bois[idx1], team.bois[idx2] = team.bois[idx2], team.bois[idx1]

    def valid_toggle_freeze_item(self, item: Any) -> bool:
        """
        Check if the item can be toggled for freezing.
        """

        if not isinstance(item, Item):
            raise ValueError("Invalid item type")

        return item in self.shop_items or item in self.frozen_items

    def _toggle_freeze_item(self, event: Event) -> None:
        """
        Toggle the frozen state of an item.
        The event should have:
        - 'item': The Item object to toggle
        """
        item = event.data.get("item")

        if not self.valid_toggle_freeze_item(item):
            raise ValueError("Invalid item for freezing/unfreezing")

        item = cast(Item, item)

        # Toggle the frozen state
        if item in self.frozen_items:
            self.frozen_items.remove(item)
        else:
            self.frozen_items.append(item)

    def valid_toggle_freeze_boi(self, boi: Any) -> bool:
        """
        Check if the boi can be toggled for freezing.
        """

        if not isinstance(boi, Boi):
            raise ValueError("Invalid boi type")

        return boi in self.shop_bois or boi in self.frozen_bois

    def _toggle_freeze_boi(self, event: Event) -> None:
        """
        Toggle the frozen state of a boi.
        The event should have:
        - 'boi': The Boi object to toggle
        """
        boi = event.data.get("boi")

        if not self.valid_toggle_freeze_boi(boi):
            raise ValueError("Invalid boi for freezing/unfreezing")

        boi = cast(Boi, boi)

        # Toggle the frozen state
        if boi in self.frozen_bois:
            self.frozen_bois.remove(boi)
        else:
            self.frozen_bois.append(boi)
