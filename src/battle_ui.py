"""
Pygame-based UI for the Super Auto Boiz battle system.
This provides a visual way to watch battles unfold with animations and real-time updates.
"""

import pygame
import sys
from typing import List, Dict, Optional, Tuple, Any, Callable

# Import game logic
from boi import BoiBuilder
from team import Team
from battle_system import BattleSystem
from system import Event

# Import UI components
from ui_components import (
    Button,
    BoiCard,
    InfoPanel,
    MoveAnimation,
    StatusDisplay,
    WHITE,
    BLACK,
    GRAY,
    LIGHT_GRAY,
    BLUE,
    GREEN,
    YELLOW,
    ORANGE,
    RED,
)

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Card dimensions
BOI_CARD_WIDTH = 120
BOI_CARD_HEIGHT = 160
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 40
PADDING = 10

# Battle-specific colors
ATTACK_COLOR = (255, 100, 100)  # Red for attacks
DAMAGE_COLOR = (255, 50, 50)  # Darker red for damage
DEATH_COLOR = (100, 100, 100)  # Gray for death
BUFF_COLOR = (100, 255, 100)  # Green for buffs


class BattleUI:
    """Main battle UI class that manages the pygame interface and battle visualization"""

    def __init__(self, team1: Team, team2: Team, auto_play: bool = False):
        """
        Initialize the battle UI.

        Args:
            team1: First team
            team2: Second team
            auto_play: If True, battle will advance automatically
        """
        # Store original team data for reset functionality
        self.original_team1_data = self._store_team_data(team1)
        self.original_team2_data = self._store_team_data(team2)

        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Auto Boiz - Battle")
        self.clock = pygame.time.Clock()

        # UI state
        self.turn_number = 1
        self.auto_play = auto_play
        self.auto_play_delay = 2000  # 2 seconds between turns in auto mode
        self.last_auto_turn = 0
        self.animations: List[MoveAnimation] = []
        self.battle_log: List[str] = []
        self.paused = False

        # Card update delay system for animations
        self.pending_card_update = False
        self.card_update_delay = 0

        # Initialize UI components first
        self.init_ui_components()

        # Game state - create battle system after UI components are ready
        self.battle = BattleSystem(team1, team2, [self._handle_event])
        self.update_cards()

        # Add initial message
        self.info_panel.add_message(
            "Battle started! Click 'Next Turn' to advance or 'Auto Play' to watch."
        )

    def _store_team_data(self, team: Team) -> List[Dict[str, Any]]:
        """Store team data for reset functionality"""
        team_data = []
        for boi in team.bois:
            boi_data = {
                "type_name": boi.type_name,
                "attack": boi.attack,
                "health": boi.health,
                "level": boi.level,
                "experience": boi.experience,
            }
            team_data.append(boi_data)
        return team_data

    def _recreate_team_from_data(self, team_data: List[Dict[str, Any]]) -> Team:
        """Recreate a team from stored data"""
        new_bois = []
        for boi_data in team_data:
            new_boi = (
                BoiBuilder()
                .set_type_name(boi_data["type_name"])
                .set_attack(boi_data["attack"])
                .set_health(boi_data["health"])
                .build()
            )
            # Set level and experience if needed
            new_boi.level = boi_data["level"]
            new_boi.experience = boi_data["experience"]
            new_bois.append(new_boi)
        return Team(new_bois)

    def init_ui_components(self):
        """Initialize all UI components"""
        pygame.font.init()

        # Fonts
        self.title_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.subtitle_font = pygame.font.SysFont("Arial", 18, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 14)

        # UI components
        self.info_panel = InfoPanel(20, SCREEN_HEIGHT - 200, SCREEN_WIDTH - 40, 180)
        self.status_display = StatusDisplay(SCREEN_WIDTH - 200, 20, 180, 100)
        # Initialize with dummy values, will be updated later
        self.status_display.update_values(0, self.turn_number)

        # Create buttons
        self.buttons = self._create_buttons()

        # Card lists
        self.team1_boi_cards: List[BoiCard] = []
        self.team2_boi_cards: List[BoiCard] = []

    def _create_buttons(self) -> Dict[str, Button]:
        """Create action buttons"""
        buttons = {}

        button_y = SCREEN_HEIGHT - 240

        # Next turn button
        next_turn_button = Button(
            20,
            button_y,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Next Turn",
            self._on_next_turn_click,
            BLUE,
        )
        buttons["next_turn"] = next_turn_button

        # Auto play toggle button
        auto_play_text = "Pause Auto" if self.auto_play else "Auto Play"
        auto_play_button = Button(
            20 + BUTTON_WIDTH + PADDING,
            button_y,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            auto_play_text,
            self._on_auto_play_click,
            GREEN if not self.auto_play else ORANGE,
        )
        buttons["auto_play"] = auto_play_button

        # Reset battle button
        reset_button = Button(
            20 + (BUTTON_WIDTH + PADDING) * 2,
            button_y,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Reset Battle",
            self._on_reset_click,
            RED,
        )
        buttons["reset"] = reset_button

        # Speed controls for auto play
        slower_button = Button(
            20 + (BUTTON_WIDTH + PADDING) * 3,
            button_y,
            80,
            BUTTON_HEIGHT,
            "Slower",
            self._on_slower_click,
            LIGHT_GRAY,
        )
        buttons["slower"] = slower_button

        faster_button = Button(
            20 + (BUTTON_WIDTH + PADDING) * 3 + 90,
            button_y,
            80,
            BUTTON_HEIGHT,
            "Faster",
            self._on_faster_click,
            LIGHT_GRAY,
        )
        buttons["faster"] = faster_button

        return buttons

    def update_cards(self):
        """Update the visual representation of team cards"""
        screen_center_x = SCREEN_WIDTH // 2
        card_y = 250

        # Team 1 cards (left side) - positioned from center-left going leftward
        self.team1_boi_cards = []
        team1_bois = self.battle.teams[0].bois

        for i, boi in enumerate(team1_bois):
            # Position from center going left: first boi closest to center
            x = (
                screen_center_x
                - 50
                - (BOI_CARD_WIDTH + PADDING)
                - i * (BOI_CARD_WIDTH + PADDING)
            )
            card = BoiCard(
                x, card_y, BOI_CARD_WIDTH, BOI_CARD_HEIGHT, boi, lambda: None, BLUE
            )
            self.team1_boi_cards.append(card)

        # Team 2 cards (right side) - positioned from center-right going rightward
        self.team2_boi_cards = []
        team2_bois = self.battle.teams[1].bois

        for i, boi in enumerate(team2_bois):
            # Position from center going right: first boi closest to center
            x = screen_center_x + 50 + i * (BOI_CARD_WIDTH + PADDING)
            card = BoiCard(
                x, card_y, BOI_CARD_WIDTH, BOI_CARD_HEIGHT, boi, lambda: None, GREEN
            )
            self.team2_boi_cards.append(card)

    def _handle_event(self, event: Event):
        """Handle battle events for visual feedback"""
        # Safety check to ensure UI components are initialized
        if not hasattr(self, "info_panel"):
            return

        if event.type == "attack":
            if "target" in event.data and "source" in event.data:
                attacker = event.data["source"]
                target = event.data["target"]
                self.info_panel.add_message(
                    f"{attacker.type_name} attacks {target.type_name}!"
                )
                self._add_attack_animation(attacker, target)

        elif event.type == "damage":
            if "target" in event.data and "damage" in event.data:
                target = event.data["target"]
                damage = event.data["damage"]
                self.info_panel.add_message(
                    f"{target.type_name} takes {damage} damage!"
                )
                self._add_damage_animation(target)

        elif event.type == "death":
            if "target" in event.data:
                target = event.data["target"]
                self.info_panel.add_message(f"{target.type_name} has fainted!")
                self._add_death_animation(target)

        elif event.type == "battle_start":
            self.info_panel.add_message("Battle begins!")

        elif event.type == "battle_turn_start":
            self.info_panel.add_message(f"Turn {self.turn_number} begins!")

        elif event.type == "battle_turn_end":
            pass  # Don't spam messages for turn end

    def _add_attack_animation(self, attacker, target):
        """Add visual effect for attack - show movement from attacker to target"""
        attacker_pos = self._get_boi_position(attacker)
        target_pos = self._get_boi_position(target)

        if attacker_pos and target_pos:
            # Create a fast-moving projectile from attacker to target
            self.animations.append(
                MoveAnimation(attacker_pos, target_pos, ATTACK_COLOR, 8, 30)
            )
            # Add a bright flash effect at the attacker's position
            self.animations.append(
                MoveAnimation(attacker_pos, attacker_pos, YELLOW, 15, 15)
            )
            # Add a second projectile for more dramatic effect
            self.animations.append(
                MoveAnimation(attacker_pos, target_pos, (255, 200, 100), 5, 35)
            )
        elif attacker_pos:
            # Fallback: just show attacker flashing if no target position
            self.animations.append(
                MoveAnimation(attacker_pos, attacker_pos, ATTACK_COLOR, 20, 30)
            )

    def _add_damage_animation(self, target):
        """Add visual effect for taking damage"""
        target_pos = self._get_boi_position(target)
        if target_pos:
            # Create a damage effect
            self.animations.append(
                MoveAnimation(target_pos, target_pos, DAMAGE_COLOR, 15, 40)
            )

    def _add_death_animation(self, target):
        """Add visual effect for death"""
        target_pos = self._get_boi_position(target)
        if target_pos:
            # Create a fading effect
            self.animations.append(
                MoveAnimation(target_pos, target_pos, DEATH_COLOR, 25, 60)
            )

    def _get_boi_position(self, boi) -> Optional[Tuple[int, int]]:
        """Get the screen position of a boi"""
        # Check team 1
        for card in self.team1_boi_cards:
            if card.boi == boi:
                return (card.x + card.width // 2, card.y + card.height // 2)

        # Check team 2
        for card in self.team2_boi_cards:
            if card.boi == boi:
                return (card.x + card.width // 2, card.y + card.height // 2)

        return None

    def _on_next_turn_click(self):
        """Handle next turn button click"""
        if not self.battle.is_battle_over():
            self.battle.run_turn()
            self.turn_number += 1

            # Delay card updates to allow animations to play
            self.pending_card_update = True
            self.card_update_delay = pygame.time.get_ticks() + 1500  # 1.5 second delay

            self._update_status()

            if self.battle.is_battle_over():
                self._handle_battle_end()

    def _on_auto_play_click(self):
        """Toggle auto play mode"""
        self.auto_play = not self.auto_play
        self.last_auto_turn = pygame.time.get_ticks()

        # Update button text and color
        button = self.buttons["auto_play"]
        if self.auto_play:
            button.text = "Pause Auto"
            button.color = ORANGE
        else:
            button.text = "Auto Play"
            button.color = GREEN

        self.info_panel.add_message(
            "Auto play " + ("enabled" if self.auto_play else "disabled")
        )

    def _on_reset_click(self):
        """Reset the battle with the same teams"""
        # Get the original teams using stored data
        original_team1 = self._recreate_team_from_data(self.original_team1_data)
        original_team2 = self._recreate_team_from_data(self.original_team2_data)

        # Create new battle
        self.battle = BattleSystem(original_team1, original_team2, [self._handle_event])
        self.turn_number = 1
        self.auto_play = False
        self.animations.clear()

        # Reset UI
        self.buttons["auto_play"].text = "Auto Play"
        self.buttons["auto_play"].color = GREEN
        self.update_cards()
        self._update_status()
        self.info_panel.add_message("Battle reset!")

    def _on_slower_click(self):
        """Make auto play slower"""
        self.auto_play_delay = min(self.auto_play_delay + 500, 5000)  # Max 5 seconds
        self.info_panel.add_message(
            f"Auto play speed: {self.auto_play_delay/1000:.1f}s per turn"
        )

    def _on_faster_click(self):
        """Make auto play faster"""
        self.auto_play_delay = max(self.auto_play_delay - 500, 500)  # Min 0.5 seconds
        self.info_panel.add_message(
            f"Auto play speed: {self.auto_play_delay/1000:.1f}s per turn"
        )

    def _update_status(self):
        """Update the status display"""
        if self.battle.is_battle_over():
            winner = self.battle.get_winner()
            if winner is None:
                # Draw! - use turn 0 to indicate draw
                self.status_display.update_values(0, 0)
            else:
                # Winner gets the team number, turn shows winner
                self.status_display.update_values(winner + 1, self.turn_number)
        else:
            # Battle in progress
            self.status_display.update_values(self.turn_number, 1)

    def _handle_battle_end(self):
        """Handle when the battle ends"""
        winner = self.battle.get_winner()
        if winner is None:
            self.info_panel.add_message("Battle ended in a draw!")
        else:
            self.info_panel.add_message(f"Team {winner + 1} wins the battle!")

    def run(self):
        """Main game loop"""
        running = True

        while running:
            current_time = pygame.time.get_ticks()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    # Handle button clicks
                    for button in self.buttons.values():
                        button.handle_event(event)

            # Auto play logic
            if self.auto_play and not self.battle.is_battle_over():
                if current_time - self.last_auto_turn >= self.auto_play_delay:
                    self._on_next_turn_click()
                    self.last_auto_turn = current_time

            # Check for pending card updates (after animations have time to play)
            if self.pending_card_update and current_time >= self.card_update_delay:
                self.update_cards()
                self.pending_card_update = False

            # Get mouse position for hover effects
            mouse_pos = pygame.mouse.get_pos()

            # Update UI elements
            for button in self.buttons.values():
                button.update(mouse_pos)

            for card in self.team1_boi_cards:
                card.update(mouse_pos)

            for card in self.team2_boi_cards:
                card.update(mouse_pos)

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
        # Clear screen
        self.screen.fill(WHITE)

        # Draw team titles with better positioning
        team1_title = self.title_font.render("Team 1", True, BLUE)
        self.screen.blit(team1_title, (50, 200))

        team2_title = self.title_font.render("Team 2", True, GREEN)
        team2_rect = team2_title.get_rect()
        team2_rect.topright = (SCREEN_WIDTH - 50, 200)
        self.screen.blit(team2_title, team2_rect)

        # Draw vs text in center
        vs_text = self.subtitle_font.render("VS", True, BLACK)
        vs_rect = vs_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(vs_text, vs_rect)

        # Draw battle line in the center
        pygame.draw.line(
            self.screen,
            LIGHT_GRAY,
            (SCREEN_WIDTH // 2, 220),
            (SCREEN_WIDTH // 2, 350),
            3,
        )

        # Draw team cards
        for card in self.team1_boi_cards:
            card.draw(self.screen)

        for card in self.team2_boi_cards:
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

        # Update display
        pygame.display.flip()


def create_demo_teams() -> Tuple[Team, Team]:
    """Create demo teams for testing"""

    # Team 1: Ant, Cricket, Beaver
    ant = BoiBuilder().set_type_name("Ant").set_attack(2).set_health(1).build()
    cricket = BoiBuilder().set_type_name("Cricket").set_attack(1).set_health(2).build()
    beaver = BoiBuilder().set_type_name("Beaver").set_attack(2).set_health(2).build()
    team1 = Team([ant, cricket, beaver])

    # Team 2: Mosquito, Dodo
    mosquito = (
        BoiBuilder().set_type_name("Mosquito").set_attack(2).set_health(2).build()
    )
    dodo = BoiBuilder().set_type_name("Dodo").set_attack(2).set_health(3).build()
    team2 = Team([mosquito, dodo])

    return team1, team2


if __name__ == "__main__":
    # Create demo teams and run the battle UI
    team1, team2 = create_demo_teams()
    battle_ui = BattleUI(team1, team2)
    battle_ui.run()
