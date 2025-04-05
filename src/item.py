from effect import EffectBuilder


class Item:
    """
    Represents an item in the game.
    These can be bought in the shop.
    """

    def __init__(self, name: str, price: int, effect_builder: EffectBuilder):
        self.name = name
        self.price = price
        self.effect_builder = effect_builder

    def create_effect(self):
        """
        Create an effect based on the item.
        """
        return self.effect_builder.build()
