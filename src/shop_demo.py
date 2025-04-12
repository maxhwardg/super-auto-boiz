"""
Demo script for shop system implementing Super Auto Pets characters.
"""

from boi import BoiBuilder
from team import Team
from shop_system import ShopSystem
from system import Event
from pack import Pack
from item import Item
from effect import EffectBuilder


def print_event(event):
    """Print event information for debugging."""
    if event.type == "purchased":
        if "target" in event.data:
            print(f"Purchased {event.data['target'].type_name}")
    elif event.type == "sold":
        if "target" in event.data:
            print(f"Sold {event.data['target'].type_name}")
    elif event.type == "item_used":
        if "target" in event.data and "item" in event.data:
            print(f"Used {event.data['item'].name} on {event.data['target'].type_name}")
    elif event.type == "levelup":
        if "target" in event.data:
            print(
                f"{event.data['target'].type_name} leveled up to level {event.data['target'].level}!"
            )


# Create pet builders and effects
def create_ant():
    """Create an Ant Boi."""
    return BoiBuilder().set_type_name("Ant").set_attack(2).set_health(1).build()


def create_cricket():
    """Create a Cricket Boi."""
    return BoiBuilder().set_type_name("Cricket").set_attack(1).set_health(2).build()


def create_beaver():
    """Create a Beaver Boi."""
    return BoiBuilder().set_type_name("Beaver").set_attack(2).set_health(2).build()


def create_mosquito():
    """Create a Mosquito Boi."""
    return BoiBuilder().set_type_name("Mosquito").set_attack(2).set_health(2).build()


def create_dodo():
    """Create a Dodo Boi."""
    return BoiBuilder().set_type_name("Dodo").set_attack(2).set_health(3).build()


def create_food_effect(attack_buff, health_buff):
    """Create a generic food effect that buffs stats."""

    def food_effect_callback(effect, system, event):
        target = event.data["target"]
        target.attack += attack_buff
        target.health += health_buff
        print(f"{target.type_name} got +{attack_buff}/+{health_buff} stats!")

    return (
        EffectBuilder()
        .set_name("Food Effect")
        .add_trigger("item_used", food_effect_callback)
        .build()
    )


def create_apple():
    """Create an Apple item."""
    return Item(
        "Apple",
        3,
        EffectBuilder()
        .set_name("Apple Effect")
        .add_trigger(
            "item_used",
            lambda effect, system, event: (
                setattr(
                    event.data["target"], "attack", event.data["target"].attack + 1
                ),
                setattr(
                    event.data["target"], "health", event.data["target"].health + 1
                ),
                print(f"{event.data['target'].type_name} got +1/+1 stats from Apple!"),
            ),
        ),
    )


def create_meat():
    """Create a Meat item."""
    return Item(
        "Meat",
        3,
        EffectBuilder()
        .set_name("Meat Effect")
        .add_trigger(
            "item_used",
            lambda effect, system, event: (
                setattr(
                    event.data["target"], "attack", event.data["target"].attack + 2
                ),
                setattr(
                    event.data["target"], "health", event.data["target"].health + 0
                ),
                print(f"{event.data['target'].type_name} got +2/+0 stats from Meat!"),
            ),
        ),
    )


def create_pill():
    """Create a Pill item (for triggering faint effects)."""
    return Item(
        "Pill",
        1,
        EffectBuilder()
        .set_name("Pill Effect")
        .add_trigger(
            "item_used",
            lambda effect, system, event: (
                system.send_event(
                    Event(type="death", target=event.data["target"], source=None)
                ),
                print(f"{event.data['target'].type_name} was killed by Pill!"),
            ),
        ),
    )


def create_pack():
    """Create a simple pack with bois and items."""
    pack = Pack("Demo Pack", 1)

    # Add bois to tier 1
    pack.add_boi_builder(
        BoiBuilder().set_type_name("Ant").set_attack(2).set_health(1), 1
    )
    pack.add_boi_builder(
        BoiBuilder().set_type_name("Cricket").set_attack(1).set_health(2), 1
    )
    pack.add_boi_builder(
        BoiBuilder().set_type_name("Beaver").set_attack(2).set_health(2), 1
    )
    pack.add_boi_builder(
        BoiBuilder().set_type_name("Mosquito").set_attack(2).set_health(2), 1
    )
    pack.add_boi_builder(
        BoiBuilder().set_type_name("Dodo").set_attack(2).set_health(3), 1
    )

    # Add items to tier 1
    pack.add_item(create_apple(), 1)
    pack.add_item(create_meat(), 1)
    pack.add_item(create_pill(), 1)

    # Set shop values
    pack.set_shop_tier_num_bois(1, 3)  # 3 bois in shop
    pack.set_shop_tier_num_items(1, 2)  # 2 items in shop

    return pack


def print_team(team):
    """Print the current state of a team."""
    print("\nYour Team:")
    if not team.bois:
        print("  (Empty)")
    for i, boi in enumerate(team.bois):
        print(f"  {i+1}. {boi} (Level {boi.level}, XP {boi.experience})")


def print_shop(shop):
    """Print the current state of the shop."""
    print("\nShop:")
    print(f"Money: ${shop.money}")

    print("\nBois for sale:")
    if not shop.shop_bois:
        print("  (None available)")
    for i, boi in enumerate(shop.shop_bois):
        print(f"  {i+1}. {boi} - ${3}")

    print("\nItems for sale:")
    if not shop.shop_items:
        print("  (None available)")
    for i, item in enumerate(shop.shop_items):
        print(f"  {i+1}. {item.name} - ${item.price}")


def print_menu():
    """Print the main menu options."""
    print("\nActions:")
    print("  1. Buy boi")
    print("  2. Buy item")
    print("  3. Sell boi")
    print("  4. Merge bois (level up)")
    print("  5. Swap boi positions")
    print("  6. Roll shop")
    print("  7. End turn (exit)")
    print("  8. Help")


def handle_buy_boi(shop):
    """Handle buying a boi."""
    print_shop(shop)

    if not shop.shop_bois:
        print("No bois available in the shop!")
        return

    if len(shop.get_team().bois) >= 5:
        print("Your team is full! Sell or merge bois to make room.")
        return

    if shop.money < 3:
        print("Not enough money to buy a boi! (Costs $3)")
        return

    try:
        choice = int(input("\nEnter boi number to buy (0 to cancel): "))
        if choice == 0:
            return

        if choice < 1 or choice > len(shop.shop_bois):
            print("Invalid choice!")
            return

        boi = shop.shop_bois[choice - 1]
        shop.send_event(Event(type="buy_boi", boi=boi))
        shop._process_all_queue_events()
        print(f"Successfully bought {boi.type_name}!")

    except ValueError:
        print("Please enter a valid number.")


def handle_buy_item(shop):
    """Handle buying an item."""
    print_shop(shop)
    print_team(shop.get_team())

    if not shop.shop_items:
        print("No items available in the shop!")
        return

    if not shop.get_team().bois:
        print("You need bois on your team to use items!")
        return

    try:
        item_choice = int(input("\nEnter item number to buy (0 to cancel): "))
        if item_choice == 0:
            return

        if item_choice < 1 or item_choice > len(shop.shop_items):
            print("Invalid item choice!")
            return

        item = shop.shop_items[item_choice - 1]

        if shop.money < item.price:
            print(f"Not enough money to buy this item! (Costs ${item.price})")
            return

        boi_choice = int(input(f"Enter boi number to use {item.name} on: "))
        if boi_choice < 1 or boi_choice > len(shop.get_team().bois):
            print("Invalid boi choice!")
            return

        target_boi = shop.get_team().bois[boi_choice - 1]
        shop.send_event(Event(type="buy_item", item=item, target_boi=target_boi))
        shop._process_all_queue_events()
        print(f"Successfully used {item.name} on {target_boi.type_name}!")

    except ValueError:
        print("Please enter a valid number.")


def handle_sell_boi(shop):
    """Handle selling a boi."""
    print_team(shop.get_team())

    if not shop.get_team().bois:
        print("No bois to sell!")
        return

    try:
        choice = int(input("\nEnter boi number to sell (0 to cancel): "))
        if choice == 0:
            return

        if choice < 1 or choice > len(shop.get_team().bois):
            print("Invalid choice!")
            return

        boi = shop.get_team().bois[choice - 1]
        shop.send_event(Event(type="sell_boi", boi=boi))
        shop._process_all_queue_events()
        print(f"Successfully sold {boi.type_name} for ${boi.level}!")

    except ValueError:
        print("Please enter a valid number.")


def handle_merge_boi(shop):
    """Handle merging two bois."""
    print_team(shop.get_team())

    if len(shop.get_team().bois) < 2:
        print("Need at least 2 bois to merge!")
        return

    try:
        print("\nSelect two bois of the same type to merge")
        target_choice = int(
            input("Enter target boi number (boi to keep, 0 to cancel): ")
        )
        if target_choice == 0:
            return

        if target_choice < 1 or target_choice > len(shop.get_team().bois):
            print("Invalid target choice!")
            return

        target_boi = shop.get_team().bois[target_choice - 1]

        # Find compatible bois
        compatible_bois = [
            (i + 1, boi)
            for i, boi in enumerate(shop.get_team().bois)
            if boi != target_boi and boi.type_name == target_boi.type_name
        ]

        if not compatible_bois:
            print(f"No other {target_boi.type_name} to merge with!")
            return

        print(f"\nCompatible bois to merge with {target_boi.type_name}:")
        for idx, boi in compatible_bois:
            print(f"  {idx}. {boi} (Level {boi.level}, XP {boi.experience})")

        source_choice = int(input("Enter source boi number (boi to merge in): "))
        if not any(idx == source_choice for idx, _ in compatible_bois):
            print("Invalid source choice!")
            return

        source_boi = shop.get_team().bois[source_choice - 1]
        shop.send_event(
            Event(type="merge_boi", target_boi=target_boi, source_boi=source_boi)
        )
        shop._process_all_queue_events()
        print(
            f"Successfully merged {source_boi.type_name} into {target_boi.type_name}!"
        )

    except ValueError:
        print("Please enter a valid number.")


def handle_swap_boi(shop):
    """Handle swapping two bois."""
    print_team(shop.get_team())

    if len(shop.get_team().bois) < 2:
        print("Need at least 2 bois to swap!")
        return

    try:
        boi1_choice = int(input("\nEnter first boi number (0 to cancel): "))
        if boi1_choice == 0:
            return

        if boi1_choice < 1 or boi1_choice > len(shop.get_team().bois):
            print("Invalid first boi choice!")
            return

        boi1 = shop.get_team().bois[boi1_choice - 1]

        boi2_choice = int(input("Enter second boi number: "))
        if (
            boi2_choice < 1
            or boi2_choice > len(shop.get_team().bois)
            or boi2_choice == boi1_choice
        ):
            print("Invalid second boi choice!")
            return

        boi2 = shop.get_team().bois[boi2_choice - 1]
        shop.send_event(Event(type="swap_boi", boi1=boi1, boi2=boi2))
        shop._process_all_queue_events()
        print(f"Successfully swapped {boi1.type_name} and {boi2.type_name}!")

    except ValueError:
        print("Please enter a valid number.")


def handle_roll(shop):
    """Handle rolling the shop."""
    if shop.money < 1:
        print("Not enough money to roll! (Costs $1)")
        return

    shop.send_event(Event(type="roll"))
    shop._process_all_queue_events()
    print("Successfully rolled the shop!")


def display_help():
    """Display help information."""
    print("\n=== SHOP SYSTEM HELP ===")
    print("1. Buy Boi ($3): Purchase a boi from the shop to add to your team.")
    print("2. Buy Item (varies): Buy an item and apply it to one of your bois.")
    print("3. Sell Boi (earn level in $): Sell a boi from your team to earn money.")
    print("4. Merge Bois: Combine two bois of the same type to increase level/XP.")
    print("5. Swap Boi Positions: Change the order of your bois in the team.")
    print("6. Roll Shop ($1): Refresh the shop offerings.")
    print("7. End Turn: Exit the game.")
    print("\nTeam Size: Maximum of 5 bois on your team.")
    print("Boi Levels: Bois can be merged to level up (max level 3).")
    print("Money: Used to buy bois, items, and roll the shop.")
    print("Position Matters: Front bois attack first in battle.")


def main():
    """Main function to run the shop demo."""
    print("=== SUPER AUTO SHOP DEMO ===\n")
    print("Welcome to the shop system demo!")
    print("Here you can buy/sell bois, use items, and manage your team.")

    # Create an empty team
    team = Team([])

    # Create pack
    pack = create_pack()

    # Create shop with starting money
    starting_money = 10
    shop = ShopSystem(team, pack, 1, starting_money, [print_event])

    print(f"You start with ${starting_money}.")

    while True:
        print_team(shop.get_team())
        print_shop(shop)
        print_menu()

        choice = input("\nEnter action number: ")

        if choice == "1":
            handle_buy_boi(shop)
        elif choice == "2":
            handle_buy_item(shop)
        elif choice == "3":
            handle_sell_boi(shop)
        elif choice == "4":
            handle_merge_boi(shop)
        elif choice == "5":
            handle_swap_boi(shop)
        elif choice == "6":
            handle_roll(shop)
        elif choice == "7":
            print("\nThanks for playing the Shop Demo!")
            break
        elif choice == "8":
            display_help()
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
