"""
UI components for the Pygame-based Super Auto Boiz shop system.
This module contains all the UI elements used in the shop UI.
"""

import pygame
from typing import List, Dict, Optional, Tuple, Any, Callable
import math
from boi import LEVEL_UP_EXPERIENCE

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
BLUE = (100, 149, 237)  # Cornflower blue
GREEN = (50, 205, 50)  # Lime green
YELLOW = (255, 215, 0)  # Gold
ORANGE = (255, 140, 0)  # Dark orange
RED = (255, 0, 0)


class Button:
    """Interactive button component"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        callback: Callable,
        color: Tuple[int, int, int] = BLUE,
        text_color: Tuple[int, int, int] = WHITE,
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = self._lighten_color(color)
        self.text_color = text_color
        self.hover = False
        self.font = pygame.font.SysFont("Arial", 14)
        self.rect = pygame.Rect(x, y, width, height)

    def _lighten_color(self, color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Create a lighter version of the given color for hover effects"""
        return tuple(min(c + 50, 255) for c in color)

    def handle_event(self, event):
        """Handle mouse events on the button"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()

    def update(self, mouse_pos):
        """Update button state based on mouse position"""
        self.hover = self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        """Draw the button on the given surface"""
        # Draw button background
        pygame.draw.rect(
            surface,
            self.hover_color if self.hover else self.color,
            self.rect,
            border_radius=5,
        )

        # Draw button border
        pygame.draw.rect(surface, BLACK, self.rect, width=2, border_radius=5)

        # Draw button text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


class BoiCard:
    """Card representing a Boi character"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        boi: Any,
        callback: Callable,
        color: Tuple[int, int, int] = LIGHT_GRAY,
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.boi = boi
        self.callback = callback
        self.color = color
        self.hover_color = self._lighten_color(color)
        self.selected_color = YELLOW
        self.is_selected = False
        self.hover = False
        self.font = pygame.font.SysFont("Arial", 14)
        self.title_font = pygame.font.SysFont("Arial", 16, bold=True)
        self.rect = pygame.Rect(x, y, width, height)

    def _lighten_color(self, color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Create a lighter version of the given color for hover effects"""
        return tuple(min(c + 50, 255) for c in color)

    def handle_event(self, event):
        """Handle mouse events on the card"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback(self)

    def update(self, mouse_pos):
        """Update card state based on mouse position"""
        self.hover = self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        """Draw the card on the given surface"""
        # Determine card color based on state
        if self.is_selected:
            card_color = self.selected_color
        elif self.hover:
            card_color = self.hover_color
        else:
            card_color = self.color

        # Draw card background
        pygame.draw.rect(surface, card_color, self.rect, border_radius=10)

        # Draw card border
        pygame.draw.rect(surface, BLACK, self.rect, width=2, border_radius=10)

        # Draw boi name
        name_surface = self.title_font.render(self.boi.type_name, True, BLACK)
        name_rect = name_surface.get_rect(
            centerx=self.rect.centerx, top=self.rect.top + 10
        )
        surface.blit(name_surface, name_rect)

        # Draw boi stats
        stats_surface = self.font.render(
            f"ATK: {self.boi.attack} | HP: {self.boi.health}", True, BLACK
        )
        stats_rect = stats_surface.get_rect(
            centerx=self.rect.centerx, top=name_rect.bottom + 5
        )
        surface.blit(stats_surface, stats_rect)

        # Draw level
        level_surface = self.font.render(f"Level: {self.boi.level}", True, BLACK)
        level_rect = level_surface.get_rect(
            centerx=self.rect.centerx, top=stats_rect.bottom + 5
        )
        surface.blit(level_surface, level_rect)

        # Draw XP (n/m)
        xp_text = f"XP: {self.boi.experience}/{LEVEL_UP_EXPERIENCE}"
        xp_surface = self.font.render(xp_text, True, BLACK)
        xp_rect = xp_surface.get_rect(
            centerx=self.rect.centerx, top=level_rect.bottom + 5
        )
        surface.blit(xp_surface, xp_rect)

        # Draw boi representation (a simple colored circle) BELOW all text
        # Move visual representation to the bottom of the card to avoid text overlap
        center_x = self.rect.centerx
        center_y = self.rect.bottom - 25  # Moved lower in the card
        radius = min(self.width, self.height) // 6  # Made slightly smaller

        # Create a unique color based on the boi's name
        name_hash = hash(self.boi.type_name) % 0xFFFFFF
        r = (name_hash & 0xFF0000) >> 16
        g = (name_hash & 0x00FF00) >> 8
        b = name_hash & 0x0000FF
        boi_color = (r, g, b)

        pygame.draw.circle(surface, boi_color, (center_x, center_y), radius)
        pygame.draw.circle(surface, BLACK, (center_x, center_y), radius, width=2)


class ItemCard:
    """Card representing an Item"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        item: Any,
        callback: Callable,
        color: Tuple[int, int, int] = LIGHT_GRAY,
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.item = item
        self.callback = callback
        self.color = color
        self.hover_color = self._lighten_color(color)
        self.selected_color = YELLOW
        self.is_selected = False
        self.hover = False
        self.font = pygame.font.SysFont("Arial", 14)
        self.title_font = pygame.font.SysFont("Arial", 16, bold=True)
        self.rect = pygame.Rect(x, y, width, height)

    def _lighten_color(self, color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Create a lighter version of the given color for hover effects"""
        return tuple(min(c + 50, 255) for c in color)

    def handle_event(self, event):
        """Handle mouse events on the card"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback(self)

    def update(self, mouse_pos):
        """Update card state based on mouse position"""
        self.hover = self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        """Draw the card on the given surface"""
        # Determine card color based on state
        if self.is_selected:
            card_color = self.selected_color
        elif self.hover:
            card_color = self.hover_color
        else:
            card_color = self.color

        # Draw card background
        pygame.draw.rect(surface, card_color, self.rect, border_radius=10)

        # Draw card border
        pygame.draw.rect(surface, BLACK, self.rect, width=2, border_radius=10)

        # Draw item name
        name_surface = self.title_font.render(self.item.name, True, BLACK)
        name_rect = name_surface.get_rect(
            centerx=self.rect.centerx, top=self.rect.top + 10
        )
        surface.blit(name_surface, name_rect)

        # Draw item cost
        cost_surface = self.font.render(f"Cost: ${self.item.price}", True, BLACK)
        cost_rect = cost_surface.get_rect(
            centerx=self.rect.centerx, top=name_rect.bottom + 5
        )
        surface.blit(cost_surface, cost_rect)

        # Draw item representation (a simple colored square) BELOW the text
        center_x = self.rect.centerx
        center_y = self.rect.bottom - 25  # Move lower in the card
        size = min(self.width, self.height) // 4  # Made slightly smaller

        # Create a unique color based on the item's name
        name_hash = hash(self.item.name) % 0xFFFFFF
        r = (name_hash & 0xFF0000) >> 16
        g = (name_hash & 0x00FF00) >> 8
        b = name_hash & 0x0000FF
        item_color = (r, g, b)

        item_rect = pygame.Rect(center_x - size // 2, center_y - size // 2, size, size)
        pygame.draw.rect(surface, item_color, item_rect)
        pygame.draw.rect(surface, BLACK, item_rect, width=2)


class InfoPanel:
    """Panel for displaying game information and messages"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        color: Tuple[int, int, int] = LIGHT_GRAY,
        max_messages: int = 5,
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.max_messages = max_messages
        self.messages = []
        self.font = pygame.font.SysFont("Arial", 14)
        self.title_font = pygame.font.SysFont("Arial", 16, bold=True)
        self.rect = pygame.Rect(x, y, width, height)

    def add_message(self, message: str):
        """Add a message to the panel"""
        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

    def draw(self, surface):
        """Draw the panel on the given surface"""
        # Draw panel background
        pygame.draw.rect(surface, self.color, self.rect, border_radius=10)

        # Draw panel border
        pygame.draw.rect(surface, BLACK, self.rect, width=2, border_radius=10)

        # Draw panel title
        title_surface = self.title_font.render("Information", True, BLACK)
        title_rect = title_surface.get_rect(x=self.rect.x + 10, y=self.rect.y + 10)
        surface.blit(title_surface, title_rect)

        # Draw messages
        message_y = title_rect.bottom + 10
        for message in self.messages:
            message_surface = self.font.render(message, True, BLACK)
            surface.blit(message_surface, (self.rect.x + 10, message_y))
            message_y += message_surface.get_height() + 5


class MoveAnimation:
    """Animated movement between two points"""

    def __init__(
        self,
        start_pos: Tuple[int, int],
        end_pos: Tuple[int, int],
        color: Tuple[int, int, int],
        size: int,
        duration: int,
    ):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color
        self.size = size
        self.duration = duration
        self.frame = 0

    def update(self):
        """Update the animation state"""
        if not self.is_completed():
            self.frame += 1

    def is_completed(self) -> bool:
        """Check if the animation is complete"""
        return self.frame >= self.duration

    def draw(self, surface):
        """Draw the animation on the given surface"""
        if self.is_completed():
            return

        # Calculate current position based on easing function
        progress = self.frame / self.duration
        ease_progress = self._ease_out_quad(progress)

        current_x = (
            self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * ease_progress
        )
        current_y = (
            self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * ease_progress
        )

        # Draw a circle at the current position
        pygame.draw.circle(
            surface, self.color, (int(current_x), int(current_y)), self.size
        )
        pygame.draw.circle(
            surface, BLACK, (int(current_x), int(current_y)), self.size, width=2
        )

    def _ease_out_quad(self, t: float) -> float:
        """Quadratic easing function for smooth animation"""
        return -t * (t - 2)


class StatusDisplay:
    """Display for game status information like money and turn number"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        color: Tuple[int, int, int] = LIGHT_GRAY,
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.money = 0
        self.turn = 1
        self.font = pygame.font.SysFont("Arial", 16)
        self.title_font = pygame.font.SysFont("Arial", 18, bold=True)
        self.rect = pygame.Rect(x, y, width, height)

    def update_values(self, money: int, turn: int):
        """Update the displayed values"""
        self.money = money
        self.turn = turn

    def draw(self, surface):
        """Draw the status display on the given surface"""
        # Draw background
        pygame.draw.rect(surface, self.color, self.rect, border_radius=10)

        # Draw border
        pygame.draw.rect(surface, BLACK, self.rect, width=2, border_radius=10)

        # Draw title
        title_surface = self.title_font.render("Status", True, BLACK)
        title_rect = title_surface.get_rect(x=self.rect.x + 10, y=self.rect.y + 10)
        surface.blit(title_surface, title_rect)

        # Draw money
        money_surface = self.font.render(f"Money: ${self.money}", True, BLACK)
        money_rect = money_surface.get_rect(
            x=self.rect.x + 10, y=title_rect.bottom + 10
        )
        surface.blit(money_surface, money_rect)

        # Draw turn
        turn_surface = self.font.render(f"Turn: {self.turn}", True, BLACK)
        turn_rect = turn_surface.get_rect(x=self.rect.x + 10, y=money_rect.bottom + 10)
        surface.blit(turn_surface, turn_rect)


class Modal:
    """Modal dialog for confirmations and notifications"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        title: str,
        message: str,
        ok_callback: Callable,
        cancel_callback: Optional[Callable] = None,
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title
        self.message = message
        self.ok_callback = ok_callback
        self.cancel_callback = cancel_callback
        self.visible = True
        self.font = pygame.font.SysFont("Arial", 14)
        self.title_font = pygame.font.SysFont("Arial", 18, bold=True)
        self.rect = pygame.Rect(x, y, width, height)

        # Create buttons
        button_width = 80
        button_height = 30
        button_y = y + height - button_height - 20

        if cancel_callback:
            # Two buttons
            self.ok_button = Button(
                x + width // 2 - button_width - 10,
                button_y,
                button_width,
                button_height,
                "OK",
                self._on_ok_click,
                GREEN,
            )

            self.cancel_button = Button(
                x + width // 2 + 10,
                button_y,
                button_width,
                button_height,
                "Cancel",
                self._on_cancel_click,
                RED,
            )
        else:
            # One button
            self.ok_button = Button(
                x + width // 2 - button_width // 2,
                button_y,
                button_width,
                button_height,
                "OK",
                self._on_ok_click,
                GREEN,
            )
            self.cancel_button = None

    def _on_ok_click(self):
        """Handle OK button click"""
        self.visible = False
        self.ok_callback()

    def _on_cancel_click(self):
        """Handle Cancel button click"""
        self.visible = False
        if self.cancel_callback:
            self.cancel_callback()

    def handle_event(self, event):
        """Handle events for the modal"""
        if not self.visible:
            return

        self.ok_button.handle_event(event)
        if self.cancel_button:
            self.cancel_button.handle_event(event)

    def update(self, mouse_pos):
        """Update the modal state"""
        if not self.visible:
            return

        self.ok_button.update(mouse_pos)
        if self.cancel_button:
            self.cancel_button.update(mouse_pos)

    def draw(self, surface):
        """Draw the modal on the given surface"""
        if not self.visible:
            return

        # Draw semi-transparent overlay
        overlay = pygame.Surface(
            (surface.get_width(), surface.get_height()), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        surface.blit(overlay, (0, 0))

        # Draw modal background
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=10)

        # Draw modal border
        pygame.draw.rect(surface, BLACK, self.rect, width=2, border_radius=10)

        # Draw title
        title_surface = self.title_font.render(self.title, True, BLACK)
        title_rect = title_surface.get_rect(
            centerx=self.rect.centerx, top=self.rect.top + 20
        )
        surface.blit(title_surface, title_rect)

        # Draw message (multi-line support)
        message_lines = self.message.split("\n")
        message_y = title_rect.bottom + 20
        for line in message_lines:
            line_surface = self.font.render(line, True, BLACK)
            line_rect = line_surface.get_rect(centerx=self.rect.centerx, top=message_y)
            surface.blit(line_surface, line_rect)
            message_y += line_rect.height + 5

        # Draw buttons
        self.ok_button.draw(surface)
        if self.cancel_button:
            self.cancel_button.draw(surface)
