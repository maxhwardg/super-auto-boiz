"""
This module contains the Team class.
"""

from typing import List
from boi import Boi


class Team:
    """Represents a team of entities in the game."""

    def __init__(self, bois: List[Boi]) -> None:
        self.bois = bois
