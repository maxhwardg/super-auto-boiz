"""
This module contains the Team class.
"""

from typing import List
from boi import Boi

MAX_TEAM_SIZE = 5


class Team:
    """Represents a team of entities in the game."""

    def __init__(self, bois: List[Boi]) -> None:
        self.bois = bois
