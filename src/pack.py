"""
Module for Pack class.
"""

from typing import List, Dict

from boi import Boi
from item import Item


class Pack:
    """
    Represents a pack in the game.
    This comprises bois and items.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.tier_bois: Dict[int, List[Boi]] = {}
        self.tier_items: Dict[int, List[Item]] = {}

    def add_boi(self, boi: Boi, tier: int) -> None:
        """
        Add a Boi to the pack.
        """
        if tier not in self.tier_bois:
            self.tier_bois[tier] = []
        self.tier_bois[tier].append(boi)

    def add_item(self, item: Item, tier: int) -> None:
        """
        Add an Item to the pack.
        """
        if tier not in self.tier_items:
            self.tier_items[tier] = []
        self.tier_items[tier].append(item)
