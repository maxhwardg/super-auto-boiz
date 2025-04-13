"""
Pygame-based UI for the Super Auto Boiz shop system.
This is a graphical replacement for the text-based shop_demo.py
"""

import pygame
import sys
from typing import List, Dict, Optional, Tuple, Any, Callable

# Import game logic
from boi import BoiBuilder
from team import Team
from shop_system import ShopSystem
from system import Event
from pack import Pack
from item import Item
from effect import EffectBuilder

# Import UI components
from ui_components import (
    Button,
    BoiCard,
    ItemCard,
    InfoPanel,
    MoveAnimation,
    StatusDisplay,
    Modal,
    WHITE,
    BLACK,
    GRAY,
    LIGHT_GRAY,
    BLUE,
    GREEN,
    YELLOW,
    ORANGE,
)

# Constants
SCREEN_WIDTH = 1280  # Increased from 1024 to 1280 to provide more horizontal space
SCREEN_HEIGHT = 950  # Increased from 868 to 950 to provide more vertical space for additional buttons
FPS = 60  # Added FPS constant for controlling frame rate

# Card dimensions
BOI_CARD_WIDTH = 120
BOI_CARD_HEIGHT = 160
ITEM_CARD_WIDTH = 100
ITEM_CARD_HEIGHT = 120
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 40
PADDING = 10
RED = (255, 70, 70)  # Adding RED color constant for cancel button
CYAN = (0, 200, 200)  # Adding CYAN color constant for frozen items/bois
ICE_BLUE = (150, 200, 255)  # Ice blue for frozen items/bois background


class ShopUI:
    """Main shop UI class that manages the pygame interface and game state"""

    def __init__(self):
        # Initialize pygame
        pygame.init()
        pygame.font.init()

        # Create screen
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Auto Boiz - Shop")

        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()

        # Game state
        self.team = Team([])
        self.pack = self._create_pack()
        self.tier = 1
        self.starting_money = 10
        self.turn = 1

        # Create the shop system
        self.shop = ShopSystem(
            self.team, self.pack, self.tier, self.starting_money, [self._handle_event]
        )

        # UI state
        self.selected_shop_boi: Optional[BoiCard] = None
        self.selected_team_boi: Optional[BoiCard] = None
        self.selected_item: Optional[ItemCard] = None
        self.action_mode: Optional[str] = (
            None  # Can be None, 'buy', 'sell', 'merge', etc.
        )
        self.animations: List[MoveAnimation] = []
        self.modal: Optional[Modal] = None

        # Initialize UI components
        self.init_ui_components()

    def init_ui_components(self):
        """Initialize all UI components"""
        # Status display (money, turn)
        self.status_display = StatusDisplay(
            SCREEN_WIDTH - 200, 20, 180, 100, LIGHT_GRAY
        )
        self.status_display.update_values(self.shop.money, self.turn)

        # Info panel
        self.info_panel = InfoPanel(
            20, SCREEN_HEIGHT - 150, SCREEN_WIDTH - 40, 130, LIGHT_GRAY
        )
        self.info_panel.add_message("Welcome to Super Auto Boiz Shop!")
        self.info_panel.add_message(f"You have ${self.shop.money} to spend.")

        # Team section title
        self.team_title_font = pygame.font.SysFont("Arial", 24)

        # Shop section title
        self.shop_title_font = pygame.font.SysFont("Arial", 24)

        # Action buttons
        self.buttons = self._create_buttons()

        # Create boi and item cards
        self.update_cards()

    def update_cards(self):
        """Update the cards based on the current game state"""
        # Team boi cards
        self.team_boi_cards = []
        for i, boi in enumerate(self.shop.get_team().bois):
            x = 20 + i * (BOI_CARD_WIDTH + PADDING)
            y = 100
            card = BoiCard(
                x, y, BOI_CARD_WIDTH, BOI_CARD_HEIGHT, boi, self._on_team_boi_click
            )
            self.team_boi_cards.append(card)

        # Shop boi cards
        self.shop_boi_cards = []
        for i, boi in enumerate(self.shop.shop_bois):
            x = 20 + i * (BOI_CARD_WIDTH + PADDING)
            y = 300
            # Check if the boi is frozen
            is_frozen = boi in self.shop.frozen_bois
            card = BoiCard(
                x,
                y,
                BOI_CARD_WIDTH,
                BOI_CARD_HEIGHT,
                boi,
                self._on_shop_boi_click,
                BLUE,
                is_frozen,
            )
            self.shop_boi_cards.append(card)

        # Shop item cards
        self.shop_item_cards = []
        for i, item in enumerate(self.shop.shop_items):
            x = 20 + i * (ITEM_CARD_WIDTH + PADDING)
            y = 500
            # Check if the item is frozen
            is_frozen = item in self.shop.frozen_items
            card = ItemCard(
                x,
                y,
                ITEM_CARD_WIDTH,
                ITEM_CARD_HEIGHT,
                item,
                self._on_item_click,
                GREEN,
                is_frozen,
            )
            self.shop_item_cards.append(card)

    def _create_buttons(self) -> Dict[str, Button]:
        """Create action buttons"""
        buttons = {}

        # Create two rows of buttons
        row1_y = SCREEN_HEIGHT - 260  # First row of buttons
        row2_y = SCREEN_HEIGHT - 210  # Second row of buttons

        # First row buttons
        # Buy boi button
        buy_boi_button = Button(
            20,
            row1_y,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Buy Boi",
            self._on_buy_boi_click,
            BLUE,
        )
        buttons["buy_boi"] = buy_boi_button

        # Buy item button
        buy_item_button = Button(
            20 + BUTTON_WIDTH + PADDING,
            row1_y,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Buy Item",
            self._on_buy_item_click,
            GREEN,
        )
        buttons["buy_item"] = buy_item_button

        # Sell boi button
        sell_boi_button = Button(
            20 + (BUTTON_WIDTH + PADDING) * 2,
            row1_y,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Sell Boi",
            self._on_sell_boi_click,
            ORANGE,
        )
        buttons["sell_boi"] = sell_boi_button

        # Freeze boi button
        freeze_boi_button = Button(
            20 + (BUTTON_WIDTH + PADDING) * 3,
            row1_y,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Freeze Boi",
            self._on_freeze_boi_click,
            ICE_BLUE,
        )
        buttons["freeze_boi"] = freeze_boi_button

        # Freeze item button
        freeze_item_button = Button(
            20 + (BUTTON_WIDTH + PADDING) * 4,
            row1_y,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Freeze Item",
            self._on_freeze_item_click,
            ICE_BLUE,
        )
        buttons["freeze_item"] = freeze_item_button

        # Roll shop button
        roll_button = Button(
            20 + (BUTTON_WIDTH + PADDING) * 5,
            row1_y,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Roll Shop ($1)",
            self._on_roll_click,
            BLUE,
        )
        buttons["roll"] = roll_button

        # End turn button
        end_turn_button = Button(
            20 + (BUTTON_WIDTH + PADDING) * 6,
            row1_y,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "End Turn",
            self._on_end_turn_click,
            GREEN,
        )
        buttons["end_turn"] = end_turn_button

        # Second row buttons
        # Merge bois button
        merge_boi_button = Button(
            20,
            row2_y,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Merge Bois",
            self._on_merge_boi_click,
            YELLOW,
        )
        buttons["merge_boi"] = merge_boi_button

        # Swap bois button
        swap_button = Button(
            20 + (BUTTON_WIDTH + PADDING),
            row2_y,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Swap Bois",
            self._on_swap_boi_click,
            LIGHT_GRAY,
        )
        buttons["swap"] = swap_button

        # Add Buy & Merge button
        buy_merge_width = BUTTON_WIDTH + 20
        buy_merge_button = Button(
            20 + (BUTTON_WIDTH + PADDING) * 2,
            row2_y,
            buy_merge_width,
            BUTTON_HEIGHT,
            "Buy & Merge",
            self._on_buy_merge_click,
            YELLOW,
        )
        buttons["buy_merge"] = buy_merge_button

        # Add Cancel button
        cancel_button = Button(
            20 + (BUTTON_WIDTH + PADDING) * 2 + buy_merge_width + PADDING,
            row2_y,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Cancel",
            self._on_cancel_click,
            RED,
        )
        buttons["cancel"] = cancel_button

        return buttons

    def _on_shop_boi_click(self, card: BoiCard):
        """Handle click on shop boi card"""
        # Check if we're in freeze boi mode
        if self.action_mode == "freeze_boi":
            self._toggle_freeze_boi(card.boi)
            return

        # Only allow shop boi selection if we're in an action that requires it
        if self.action_mode not in ["buy", "buy_and_merge"]:
            self.info_panel.add_message("Please select an action first.")
            return

        # Deselect other shop bois
        for shop_card in self.shop_boi_cards:
            shop_card.is_selected = False

        # Select the clicked card
        card.is_selected = True
        self.selected_shop_boi = card

        if self.action_mode == "buy":
            self._buy_selected_boi()
        elif self.action_mode == "buy_and_merge" and self.selected_team_boi:
            self._buy_and_merge_boi()

    def _on_team_boi_click(self, card: BoiCard):
        """Handle click on team boi card"""
        # Only allow team boi selection if we're in an action that requires it
        if self.action_mode not in [
            "use_item",
            "sell",
            "merge",
            "swap",
            "buy_and_merge",
        ]:
            self.info_panel.add_message("Please select an action first.")
            return

        # If an item is selected, use it on this boi
        if self.action_mode == "use_item" and self.selected_item:
            self._use_item_on_boi(card.boi)
            return

        # Deselect other team bois if not in merge mode
        if self.action_mode != "merge" and self.action_mode != "swap":
            for team_card in self.team_boi_cards:
                team_card.is_selected = False

        # Select the clicked card
        card.is_selected = True
        self.selected_team_boi = card

        if self.action_mode == "sell":
            self._sell_selected_boi()
        elif self.action_mode == "merge" and self._count_selected_team_bois() == 2:
            self._merge_selected_bois()
        elif self.action_mode == "swap" and self._count_selected_team_bois() == 2:
            self._swap_selected_bois()
        elif self.action_mode == "buy_and_merge" and self.selected_shop_boi:
            self._buy_and_merge_boi()

    def _on_item_click(self, card: ItemCard):
        """Handle click on item card"""
        # Check if we're in freeze item mode
        if self.action_mode == "freeze_item":
            self._toggle_freeze_item(card.item)
            return

        # Items can only be selected during buy_item action
        if self.action_mode != "buy_item":
            self.info_panel.add_message("Please select the Buy Item action first.")
            return

        # Deselect other items
        for item_card in self.shop_item_cards:
            item_card.is_selected = False

        # Select the clicked card
        card.is_selected = True
        self.selected_item = card

        # Enter use item mode
        self.action_mode = "use_item"
        self.info_panel.add_message("Select a boi to use the item on.")

    def _on_buy_boi_click(self):
        """Handle buy boi button click"""
        self.action_mode = "buy"
        self.info_panel.add_message("Select a boi to buy from the shop.")

        # Deselect everything
        self._deselect_all()

    def _on_buy_item_click(self):
        """Handle buy item button click"""
        self.action_mode = "buy_item"
        self.info_panel.add_message("Select an item to buy from the shop.")

        # Deselect everything
        self._deselect_all()

    def _on_sell_boi_click(self):
        """Handle sell boi button click"""
        self.action_mode = "sell"
        self.info_panel.add_message("Select a boi from your team to sell.")

        # Deselect everything
        self._deselect_all()

    def _on_merge_boi_click(self):
        """Handle merge bois button click"""
        self.action_mode = "merge"
        self.info_panel.add_message("Select two bois of the same type to merge.")

        # Deselect everything
        self._deselect_all()

    def _on_roll_click(self):
        """Handle roll shop button click"""
        try:
            self.shop.send_event(Event(type="roll"))
            self.shop._process_all_queue_events()
            self.info_panel.add_message(
                f"Shop rolled for $1. Money remaining: ${self.shop.money}"
            )
            self.update_cards()
            self._deselect_all()
            self.status_display.update_values(self.shop.money, self.turn)
        except ValueError as e:
            self.info_panel.add_message(str(e))

    def _on_end_turn_click(self):
        """Handle end turn button click"""
        self._deselect_all()

        # Get the current team
        existing_team = self.shop.get_team()

        # Create a new shop with the same pack and tier but fresh money
        self.turn += 1
        self.shop = ShopSystem(
            existing_team,
            self.pack,
            self.tier,
            self.starting_money,
            [self._handle_event],
        )

        self.info_panel.add_message(
            f"Turn {self.turn} started with ${self.starting_money}!"
        )
        self.update_cards()
        self.status_display.update_values(self.shop.money, self.turn)

    def _on_swap_boi_click(self):
        """Handle swap bois button click"""
        self.action_mode = "swap"
        self.info_panel.add_message("Select two bois to swap positions.")

        # Deselect everything
        self._deselect_all()

    def _on_buy_merge_click(self):
        """Handle buy & merge button click"""
        self.action_mode = "buy_and_merge"
        self.info_panel.add_message(
            "First select a boi from the shop, then select a boi of the same type from your team to merge with."
        )

        # Deselect everything
        self._deselect_all()

    def _on_cancel_click(self):
        """Handle cancel button click"""
        self.action_mode = None
        self.info_panel.add_message("Action cancelled.")
        self._deselect_all()

    def _on_freeze_boi_click(self):
        """Handle freeze boi button click"""
        self.action_mode = "freeze_boi"
        self.info_panel.add_message("Select a boi from the shop to freeze or unfreeze.")

        # Deselect everything
        self._deselect_all()

    def _on_freeze_item_click(self):
        """Handle freeze item button click"""
        self.action_mode = "freeze_item"
        self.info_panel.add_message(
            "Select an item from the shop to freeze or unfreeze."
        )

        # Deselect everything
        self._deselect_all()

    def _handle_event(self, event: Event):
        """Process game events for UI updates"""
        if event.type == "purchased":
            if "target" in event.data:
                self.info_panel.add_message(
                    f"Purchased {event.data['target'].type_name}"
                )
        elif event.type == "sold":
            if "target" in event.data:
                self.info_panel.add_message(f"Sold {event.data['target'].type_name}")
        elif event.type == "item_used":
            if "target" in event.data and "item" in event.data:
                self.info_panel.add_message(
                    f"Used {event.data['item'].name} on {event.data['target'].type_name}"
                )
        elif event.type == "levelup":
            if "target" in event.data:
                self.info_panel.add_message(
                    f"{event.data['target'].type_name} leveled up to level {event.data['target'].level}!"
                )
        elif event.type == "buy_and_merge_boi":
            if "bought" in event.data and "target" in event.data:
                self.info_panel.add_message(
                    f"Buying {event.data['bought'].type_name} and merging into {event.data['target'].type_name}"
                )

    def _count_selected_team_bois(self) -> int:
        """Count how many team bois are selected"""
        return sum(1 for card in self.team_boi_cards if card.is_selected)

    def _get_selected_team_bois(self) -> List[BoiCard]:
        """Get list of selected team boi cards"""
        return [card for card in self.team_boi_cards if card.is_selected]

    def _deselect_all(self):
        """Deselect all cards"""
        for card in self.team_boi_cards:
            card.is_selected = False
        for card in self.shop_boi_cards:
            card.is_selected = False
        for card in self.shop_item_cards:
            card.is_selected = False
        self.selected_shop_boi = None
        self.selected_team_boi = None
        self.selected_item = None

    def _buy_selected_boi(self):
        """Buy the selected shop boi"""
        if not self.selected_shop_boi:
            return

        boi = self.selected_shop_boi.boi
        try:
            self.shop.send_event(Event(type="buy_boi", boi=boi))
            self.shop._process_all_queue_events()
            self.update_cards()
            self._deselect_all()
            self.status_display.update_values(self.shop.money, self.turn)
            self.action_mode = None
        except ValueError as e:
            self.info_panel.add_message(str(e))

    def _sell_selected_boi(self):
        """Sell the selected team boi"""
        if not self.selected_team_boi:
            return

        boi = self.selected_team_boi.boi
        try:
            self.shop.send_event(Event(type="sell_boi", boi=boi))
            self.shop._process_all_queue_events()
            self.update_cards()
            self._deselect_all()
            self.status_display.update_values(self.shop.money, self.turn)
            self.action_mode = None
        except ValueError as e:
            self.info_panel.add_message(str(e))

    def _merge_selected_bois(self):
        """Merge the two selected team bois"""
        selected_bois = self._get_selected_team_bois()
        if len(selected_bois) != 2:
            return

        target_boi = selected_bois[0].boi
        source_boi = selected_bois[1].boi

        # Check if bois are of the same type
        if target_boi.type_name != source_boi.type_name:
            self.info_panel.add_message("Cannot merge bois of different types!")
            self._deselect_all()
            self.action_mode = None
            return

        try:
            # Add animation
            start_pos = (
                selected_bois[1].x + selected_bois[1].width // 2,
                selected_bois[1].y + selected_bois[1].height // 2,
            )
            end_pos = (
                selected_bois[0].x + selected_bois[0].width // 2,
                selected_bois[0].y + selected_bois[0].height // 2,
            )
            self.animations.append(MoveAnimation(start_pos, end_pos, YELLOW, 15, 45))

            # Merge
            self.shop.send_event(
                Event(type="merge_boi", target_boi=target_boi, source_boi=source_boi)
            )
            self.shop._process_all_queue_events()
            self.update_cards()
            self._deselect_all()
            self.action_mode = None
        except ValueError as e:
            self.info_panel.add_message(str(e))

    def _swap_selected_bois(self):
        """Swap the positions of two selected team bois"""
        selected_bois = self._get_selected_team_bois()
        if len(selected_bois) != 2:
            return

        boi1 = selected_bois[0].boi
        boi2 = selected_bois[1].boi

        try:
            # Add animations
            start_pos1 = (
                selected_bois[0].x + selected_bois[0].width // 2,
                selected_bois[0].y + selected_bois[0].height // 2,
            )
            start_pos2 = (
                selected_bois[1].x + selected_bois[1].width // 2,
                selected_bois[1].y + selected_bois[1].height // 2,
            )
            self.animations.append(MoveAnimation(start_pos1, start_pos2, BLUE, 15, 45))
            self.animations.append(MoveAnimation(start_pos2, start_pos1, BLUE, 15, 45))

            # Swap
            self.shop.send_event(Event(type="swap_boi", boi1=boi1, boi2=boi2))
            self.shop._process_all_queue_events()
            self.update_cards()
            self._deselect_all()
            self.action_mode = None
        except ValueError as e:
            self.info_panel.add_message(str(e))

    def _use_item_on_boi(self, target_boi):
        """Use the selected item on the target boi"""
        if not self.selected_item:
            return

        item = self.selected_item.item

        try:
            self.shop.send_event(
                Event(type="buy_item", item=item, target_boi=target_boi)
            )
            self.shop._process_all_queue_events()
            self.update_cards()
            self._deselect_all()
            self.status_display.update_values(self.shop.money, self.turn)
            self.action_mode = None
        except ValueError as e:
            self.info_panel.add_message(str(e))

    def _buy_and_merge_boi(self):
        """Buy a shop boi and merge it with a team boi"""
        if not self.selected_shop_boi or not self.selected_team_boi:
            return

        shop_boi = self.selected_shop_boi.boi
        team_boi = self.selected_team_boi.boi

        # Check if bois are of the same type
        if shop_boi.type_name != team_boi.type_name:
            self.info_panel.add_message("Cannot merge bois of different types!")
            self._deselect_all()
            self.action_mode = None
            return

        try:
            # Add animation
            start_pos = (
                self.selected_shop_boi.x + self.selected_shop_boi.width // 2,
                self.selected_shop_boi.y + self.selected_shop_boi.height // 2,
            )
            end_pos = (
                self.selected_team_boi.x + self.selected_team_boi.width // 2,
                self.selected_team_boi.y + self.selected_team_boi.height // 2,
            )
            self.animations.append(MoveAnimation(start_pos, end_pos, YELLOW, 15, 45))

            # Buy and merge
            self.shop.send_event(
                Event(type="buy_and_merge_boi", bought=shop_boi, target=team_boi)
            )
            self.shop._process_all_queue_events()
            self.update_cards()
            self._deselect_all()
            self.status_display.update_values(self.shop.money, self.turn)
            self.action_mode = None
        except ValueError as e:
            self.info_panel.add_message(str(e))

    def _toggle_freeze_boi(self, boi):
        """Toggle freeze state for a shop boi"""
        try:
            self.shop.send_event(Event(type="toggle_freeze_boi", boi=boi))
            self.shop._process_all_queue_events()
            frozen_status = "frozen" if boi in self.shop.frozen_bois else "unfrozen"
            self.info_panel.add_message(f"{boi.type_name} {frozen_status}!")
            self.update_cards()
            self.action_mode = None
        except ValueError as e:
            self.info_panel.add_message(str(e))

    def _toggle_freeze_item(self, item):
        """Toggle freeze state for a shop item"""
        try:
            self.shop.send_event(Event(type="toggle_freeze_item", item=item))
            self.shop._process_all_queue_events()
            frozen_status = "frozen" if item in self.shop.frozen_items else "unfrozen"
            self.info_panel.add_message(f"{item.name} {frozen_status}!")
            self.update_cards()
            self.action_mode = None
        except ValueError as e:
            self.info_panel.add_message(str(e))

    def _create_pack(self) -> Pack:
        """Create a simple pack with bois and items"""
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

        # Create items

        # Apple - gives +1/+1
        apple = Item(
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
                ),
            ),
        )

        # Meat - gives +2/+0
        meat = Item(
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
                ),
            ),
        )

        # Pill - triggers faint effects
        pill = Item(
            "Pill",
            1,
            EffectBuilder()
            .set_name("Pill Effect")
            .add_trigger(
                "item_used",
                lambda effect, system, event: (
                    system.send_event(
                        Event(type="death", target=event.data["target"], source=None)
                    )
                ),
            ),
        )

        # Add items to tier 1
        pack.add_item(apple, 1)
        pack.add_item(meat, 1)
        pack.add_item(pill, 1)

        # Set shop values
        pack.set_shop_tier_num_bois(1, 3)  # 3 bois in shop
        pack.set_shop_tier_num_items(1, 2)  # 2 items in shop

        return pack

    def run(self):
        """Main game loop"""
        running = True

        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Handle UI element clicks
                    mouse_pos = pygame.mouse.get_pos()

                    # Check if modal is active and handle its events first
                    if self.modal and self.modal.visible:
                        self.modal.handle_event(event)
                        continue

                    # Handle button clicks
                    for button in self.buttons.values():
                        button.handle_event(event)

                    # Handle team boi clicks
                    for card in self.team_boi_cards:
                        card.handle_event(event)

                    # Handle shop boi clicks
                    for card in self.shop_boi_cards:
                        card.handle_event(event)

                    # Handle item clicks
                    for card in self.shop_item_cards:
                        card.handle_event(event)

            # Get mouse position for hover effects
            mouse_pos = pygame.mouse.get_pos()

            # Update UI elements
            for button in self.buttons.values():
                button.update(mouse_pos)

            for card in self.team_boi_cards:
                card.update(mouse_pos)

            for card in self.shop_boi_cards:
                card.update(mouse_pos)

            for card in self.shop_item_cards:
                card.update(mouse_pos)

            if self.modal:
                self.modal.update(mouse_pos)

            # Update animations
            for anim in self.animations[:]:
                anim.update()
                if anim.is_completed():
                    self.animations.remove(anim)

            # Render everything
            self.render()

            # Cap the frame rate
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def render(self):
        """Render all UI elements"""
        # Clear the screen
        self.screen.fill(WHITE)

        # Draw section titles
        team_title_surface = self.team_title_font.render("Your Team", True, BLACK)
        self.screen.blit(team_title_surface, (20, 70))

        shop_boi_title_surface = self.shop_title_font.render("Shop Bois", True, BLACK)
        self.screen.blit(shop_boi_title_surface, (20, 270))

        shop_item_title_surface = self.shop_title_font.render("Shop Items", True, BLACK)
        self.screen.blit(shop_item_title_surface, (20, 470))

        # Draw team boi cards
        for card in self.team_boi_cards:
            card.draw(self.screen)

        # Draw shop boi cards
        for card in self.shop_boi_cards:
            card.draw(self.screen)

        # Draw shop item cards
        for card in self.shop_item_cards:
            card.draw(self.screen)

        # Draw buttons
        for button in self.buttons.values():
            button.draw(self.screen)

        # Draw status display
        self.status_display.draw(self.screen)

        # Draw info panel
        self.info_panel.draw(self.screen)

        # Draw animations
        for anim in self.animations:
            anim.draw(self.screen)

        # Draw modal on top if it exists
        if self.modal and self.modal.visible:
            self.modal.draw(self.screen)

        # Update the display
        pygame.display.flip()


if __name__ == "__main__":
    shop_ui = ShopUI()
    shop_ui.run()
