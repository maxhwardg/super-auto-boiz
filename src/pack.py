"""
Module for Pack class.
"""

from typing import List

from boi import BoiBuilder
from item import ItemBuilder


class TierInfo:
    """
    Represents information about a tier in the game.
    """

    def __init__(self) -> None:
        self.boi_builders: List[BoiBuilder] = []
        self.item_builders: List[ItemBuilder] = []
        self.shop_num_bois: int = 0
        self.shop_num_items: int = 0


class Pack:
    """
    Represents a pack in the game.
    This comprises bois and items.
    """

    def __init__(self, name: str, num_tiers: int) -> None:
        self.name = name
        self.num_tiers = num_tiers
        self.tiers = [TierInfo() for _ in range(num_tiers)]

    def _validate_tier(self, tier: int) -> bool:
        """
        Validate the tier number.
        """
        return 0 < tier <= self.num_tiers

    def add_boi_builder(self, boi_builder: BoiBuilder, tier: int) -> None:
        """
        Add a Boi to the pack.
        """
        if not self._validate_tier(tier):
            raise ValueError(f"Invalid tier: {tier}.")
        self.tiers[tier - 1].boi_builders.append(boi_builder)

    def add_item_builder(self, item_builder: ItemBuilder, tier: int) -> None:
        """
        Add an Item to the pack.
        """
        if not self._validate_tier(tier):
            raise ValueError(f"Invalid tier: {tier}.")
        self.tiers[tier - 1].item_builders.append(item_builder)

    def set_shop_tier_num_bois(self, tier: int, num_bois: int) -> None:
        """
        Set the number of bois in the shop for a given tier.
        """
        if not self._validate_tier(tier):
            raise ValueError(f"Invalid tier: {tier}.")
        self.tiers[tier - 1].shop_num_bois = num_bois

    def set_shop_tier_num_items(self, tier: int, num_items: int) -> None:
        """
        Set the number of items in the shop for a given tier.
        """
        if not self._validate_tier(tier):
            raise ValueError(f"Invalid tier: {tier}.")
        self.tiers[tier - 1].shop_num_items = num_items
