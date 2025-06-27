from enum import Enum


class Level(int, Enum):
    """Enum representing the levels of expertise in the game."""
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4

    def __str__(self):
        return self.name.capitalize()
