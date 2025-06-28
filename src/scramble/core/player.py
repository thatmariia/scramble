from dataclasses import dataclass
from scramble.utils import Serializable
from scramble.core.level import Level


@dataclass
class Player(Serializable):
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

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        return cls(
            id=data["id"],
            name=data["name"],
            level=Level(data["level"]),
            assignment=data.get("assignment", "")
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "level": self.level.value,
            "assignment": self.assignment
        }
