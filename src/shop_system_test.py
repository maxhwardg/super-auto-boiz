import unittest

from system import Event
from boi import BoiBuilder
from team import Team
from item import Item
from effect import EffectBuilder
from pack import Pack
from shop_system import ShopSystem, BOI_PRICE, ROLL_PRICE


class MockEffectBuilder(EffectBuilder):
    """Mock effect builder for testing"""

    def __init__(self, name: str) -> None:
        """Initialize the mock effect builder with a name"""
        super().__init__()
        self.name = name

    def build(self):
        """Build and return a mock effect"""
        return None


class ShopSystemTest(unittest.TestCase):
    """Test cases for the ShopSystem class"""

    def setUp(self):
        """Set up test environment before each test"""
        # Create test bois
        self.ant_builder = BoiBuilder().set_type_name("Ant").set_attack(2).set_health(1)
        self.beaver_builder = (
            BoiBuilder().set_type_name("Beaver").set_attack(2).set_health(2)
        )
        self.cricket_builder = (
            BoiBuilder().set_type_name("Cricket").set_attack(1).set_health(2)
        )

        # Create test items
        self.honey_item = Item("Honey", 3, MockEffectBuilder("Honey"))
        self.garlic_item = Item("Garlic", 3, MockEffectBuilder("Garlic"))
        self.meat_item = Item("Meat", 3, MockEffectBuilder("Meat"))

        # Create test pack
        self.pack = Pack("Test Pack", 3)
        self.pack.add_boi_builder(self.ant_builder, 1)
        self.pack.add_boi_builder(self.beaver_builder, 1)
        self.pack.add_boi_builder(self.cricket_builder, 1)
        self.pack.add_item(self.honey_item, 1)
        self.pack.add_item(self.garlic_item, 1)
        self.pack.add_item(self.meat_item, 1)

        # Configure shop settings for each tier
        for tier in range(1, 4):
            self.pack.set_shop_tier_num_bois(tier, 3)
            self.pack.set_shop_tier_num_items(tier, 2)

        # Create empty team
        self.team = Team([])

        # Track events during testing
        self.events_fired = []

        # Create shop system
        self.shop = ShopSystem(
            team=self.team,
            pack=self.pack,
            tier=1,
            money=10,
            event_callbacks=[self.track_event],
        )

    def track_event(self, event: Event) -> None:
        """Track events fired during testing"""
        self.events_fired.append(event)

    def test_init(self):
        """Test shop initialization"""
        self.assertEqual(self.shop.money, 10)
        self.assertEqual(self.shop.tier, 1)
        self.assertEqual(len(self.shop.shop_bois), 3)
        self.assertEqual(len(self.shop.shop_items), 2)

    def test_roll(self):
        """Test rolling the shop"""
        initial_bois = self.shop.shop_bois.copy()
        initial_items = self.shop.shop_items.copy()
        initial_money = self.shop.money

        self.shop.send_and_execute_event(Event(type="roll"))

        # Check money was deducted
        self.assertEqual(self.shop.money, initial_money - ROLL_PRICE)

        # The shop contents should have changed (this test might occasionally fail due to randomness,
        # but it's unlikely all items would stay the same after a roll)
        self.assertNotEqual(self.shop.shop_bois, initial_bois)
        self.assertNotEqual(self.shop.shop_items, initial_items)

    def test_buy_boi(self):
        """Test buying a boi"""
        initial_money = self.shop.money
        boi_to_buy = self.shop.shop_bois[0]

        self.shop.send_and_execute_event(Event(type="buy_boi", boi=boi_to_buy))

        # Check money was deducted
        self.assertEqual(self.shop.money, initial_money - BOI_PRICE)

        # Check boi was added to team
        self.assertIn(boi_to_buy, self.shop.get_team().bois)

        # Check boi was removed from shop
        self.assertNotIn(boi_to_buy, self.shop.shop_bois)

        # Check event was fired
        purchase_events = [e for e in self.events_fired if e.type == "purchased"]
        self.assertEqual(len(purchase_events), 1)
        self.assertEqual(purchase_events[0].data["target"], boi_to_buy)

    def test_sell_boi(self):
        """Test selling a boi"""
        # First buy a boi to have something to sell
        boi_to_buy = self.shop.shop_bois[0]
        self.shop.send_and_execute_event(Event(type="buy_boi", boi=boi_to_buy))

        # Clear event tracking
        self.events_fired = []

        initial_money = self.shop.money
        boi_to_sell = self.shop.get_team().bois[0]

        self.shop.send_and_execute_event(Event(type="sell_boi", boi=boi_to_sell))

        # Check money was added (sell price = boi level)
        self.assertEqual(self.shop.money, initial_money + boi_to_sell.level)

        # Check boi was removed from team
        self.assertNotIn(boi_to_sell, self.shop.get_team().bois)

        # Check event was fired
        sell_events = [e for e in self.events_fired if e.type == "sold"]
        self.assertEqual(len(sell_events), 1)
        self.assertEqual(sell_events[0].data["target"], boi_to_sell)

    def test_buy_item(self):
        """Test buying an item"""
        # First buy a boi to have something to give the item to
        boi_to_buy = self.shop.shop_bois[0]
        self.shop.send_and_execute_event(Event(type="buy_boi", boi=boi_to_buy))

        # Clear event tracking
        self.events_fired = []

        initial_money = self.shop.money
        item_to_buy = self.shop.shop_items[0]
        target_boi = self.shop.get_team().bois[0]

        self.shop.send_and_execute_event(
            Event(type="buy_item", item=item_to_buy, target_boi=target_boi)
        )

        # Check money was deducted
        self.assertEqual(self.shop.money, initial_money - item_to_buy.price)

        # Check item was removed from shop
        self.assertNotIn(item_to_buy, self.shop.shop_items)

        # Check event was fired
        item_events = [e for e in self.events_fired if e.type == "item_used"]
        self.assertEqual(len(item_events), 1)
        self.assertEqual(item_events[0].data["target"], target_boi)
        self.assertEqual(item_events[0].data["item"], item_to_buy)

    def test_merge_boi(self):
        """Test merging two bois"""
        # Buy two bois of the same type
        same_type_builder = self.beaver_builder
        boi1 = same_type_builder.build()
        boi2 = same_type_builder.build()

        # Add them directly to the team
        self.shop.get_team().bois.append(boi1)
        self.shop.get_team().bois.append(boi2)

        # Clear event tracking
        self.events_fired = []

        # Remember initial stats
        initial_attack = boi1.attack
        initial_health = boi1.health

        # Merge boi2 into boi1
        self.shop.send_and_execute_event(
            Event(type="merge_boi", target_boi=boi1, source_boi=boi2)
        )

        # Check that stats increased
        self.assertTrue(boi1.attack > initial_attack or boi1.health > initial_health)

        # Check that experience increased
        self.assertEqual(boi1.experience, 1)

        # Check that boi2 was removed from the team
        self.assertNotIn(boi2, self.shop.get_team().bois)

        # No level up event should have been fired yet
        levelup_events = [e for e in self.events_fired if e.type == "levelup"]
        self.assertEqual(len(levelup_events), 0)

    def test_levelup_from_merging(self):
        """Test leveling up from merging"""
        # Buy a boi and get two more of the same type
        same_type_builder = self.beaver_builder
        main_boi = same_type_builder.build()

        # Set experience to make it level up after one merge
        main_boi.experience = 2

        # Create a boi to merge into the main one
        merge_boi = same_type_builder.build()

        # Add them to the team
        self.shop.get_team().bois.append(main_boi)
        self.shop.get_team().bois.append(merge_boi)

        # Clear event tracking
        self.events_fired = []

        # Merge
        self.shop.send_and_execute_event(
            Event(type="merge_boi", target_boi=main_boi, source_boi=merge_boi)
        )

        # Check that level increased
        self.assertEqual(main_boi.level, 2)

        # Check that levelup event was fired
        levelup_events = [e for e in self.events_fired if e.type == "levelup"]
        self.assertEqual(len(levelup_events), 1)
        self.assertEqual(levelup_events[0].data["target"], main_boi)

    def test_buy_and_merge_boi(self):
        """Test buying and merging a boi in one action"""
        # Add a boi to the team
        boi_on_team = self.cricket_builder.build()
        self.shop.get_team().bois.append(boi_on_team)

        # Add a boi of the same type to the shop
        shop_boi = self.cricket_builder.build()
        self.shop.shop_bois = [shop_boi]  # Replace shop bois to guarantee type match

        # Clear event tracking
        self.events_fired = []

        initial_money = self.shop.money
        initial_exp = boi_on_team.experience

        # Buy and merge
        self.shop.send_and_execute_event(
            Event(type="buy_and_merge_boi", bought=shop_boi, target=boi_on_team)
        )

        # Check money was deducted
        self.assertEqual(self.shop.money, initial_money - BOI_PRICE)

        # Check experience increased
        self.assertTrue(boi_on_team.experience > initial_exp)

        # Check boi was removed from shop
        self.assertNotIn(shop_boi, self.shop.shop_bois)

    def test_swap_boi(self):
        """Test swapping two bois"""
        # Add bois to team
        boi1 = self.ant_builder.build()
        boi2 = self.beaver_builder.build()
        self.shop.get_team().bois.append(boi1)
        self.shop.get_team().bois.append(boi2)

        # Their positions before swap
        initial_positions = self.shop.get_team().bois.copy()

        # Swap them
        self.shop.send_and_execute_event(Event(type="swap_boi", boi1=boi1, boi2=boi2))

        # Check that positions were swapped
        self.assertEqual(self.shop.get_team().bois[0], initial_positions[1])
        self.assertEqual(self.shop.get_team().bois[1], initial_positions[0])


if __name__ == "__main__":
    unittest.main()
