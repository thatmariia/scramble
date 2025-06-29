from enum import Enum


class Level(int, Enum):
    """Enum representing the levels of expertise in the game."""
    BEGINNER = 1
    IMPROVER = 2
    INTERMEDIATE = 3
    ADVANCED = 4
    EXPERT = 5

    def __str__(self):
        return self.name.capitalize()
