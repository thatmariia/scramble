from dataclasses import dataclass

from scramble.core.level import Level


@dataclass
class Player:
    """
    Represents a player with an ID, name, level, and assignment.

    Attributes
    ----------
    id : int
        Unique identifier for the player.
    name : str
        Name of the player.
    level : Level
        Level of expertise of the player, represented by the Level enum.
    assignment : str = ""
        The assignment (a number) for the player in the scramble.
    """
    id: int
    name: str
    level: Level
    assignment: str = ""
