from effect import EffectBuilder

from uuid import uuid4
from copy import deepcopy


class Item:
    """
    Represents an item in the game.
    These can be bought in the shop.
    """

    def __init__(self, name: str, price: int, effect_builder: EffectBuilder):
        self.name = name
        self.price = price
        self.effect_builder = effect_builder
        self.uuid = str(uuid4())

    def create_effect(self):
        """
        Create an effect based on the item.
        """
        return self.effect_builder.build()


class ItemBuilder:
    """
    Builder for creating Item instances.
    """

    def __init__(self):
        self.item = Item("", 0, EffectBuilder())

    def set_name(self, name: str) -> "ItemBuilder":
        """
        Set the name of the item.
        """
        self.item.name = name
        return self

    def set_price(self, price: int) -> "ItemBuilder":
        """
        Set the price of the item.
        """
        self.item.price = price
        return self

    def set_effect_builder(self, effect_builder: EffectBuilder) -> "ItemBuilder":
        """
        Set the effect builder for the item.
        """
        self.item.effect_builder = effect_builder
        return self

    def build(self) -> Item:
        """
        Build and return the Item instance.
        Will be a new instance each time.
        """
        item = deepcopy(self.item)
        item.uuid = str(uuid4())
        return item
