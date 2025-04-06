"""
Module for Pack class.
"""

from typing import List, Dict

from boi import BoiBuilder
from item import Item


class Pack:
    """
    Represents a pack in the game.
    This comprises bois and items.
    """

    def __init__(self, name: str, num_tiers: int) -> None:
        self.name = name
        self.num_tiers = num_tiers
        self.tier_boi_builders: Dict[int, List[BoiBuilder]] = {}
        self.tier_items: Dict[int, List[Item]] = {}
        self.tier_shop_num_bois: Dict[int, int] = {}
        self.tier_shop_num_items: Dict[int, int] = {}

    def add_boi_builder(self, boi_builder: BoiBuilder, tier: int) -> None:
        """
        Add a Boi to the pack.
        """
        if tier not in self.tier_boi_builders:
            self.tier_boi_builders[tier] = []
        self.tier_boi_builders[tier].append(boi_builder)

    def add_item(self, item: Item, tier: int) -> None:
        """
        Add an Item to the pack.
        """
        if tier not in self.tier_items:
            self.tier_items[tier] = []
        self.tier_items[tier].append(item)

    def set_shop_tier_num_bois(self, tier: int, num_bois: int) -> None:
        """
        Set the number of bois in the shop for a given tier.
        """
        self.tier_shop_num_bois[tier] = num_bois

    def set_shop_tier_num_items(self, tier: int, num_items: int) -> None:
        """
        Set the number of items in the shop for a given tier.
        """
        self.tier_shop_num_items[tier] = num_items

    def validate_tiers(self) -> bool:
        """
        Validate that all tiers have at least one Boi and one Item.
        This is to ensure that the pack is complete and can be used in the game.
        """
        for tier in range(1, self.num_tiers + 1):
            if tier not in self.tier_boi_builders or tier not in self.tier_items:
                return False
            if (
                tier not in self.tier_shop_num_bois
                or tier not in self.tier_shop_num_items
            ):
                return False
        return True
