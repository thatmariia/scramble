from dataclasses import dataclass, field
import uuid
from scramble.utils import Serializable
from scramble.core.level import Level


@dataclass
class Player(Serializable):
    """
    Represents a player with an ID, name, level, and assignment.

    Attributes
    ----------
    id : str
        Unique identifier for the player.
    name : str
        Name of the player.
    level : Level
        Level of expertise of the player, represented by the Level enum.
    assignment : str = ""
        The assignment (a number) for the player in the scramble.
    """
    name: str
    level: Level
    assignment: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __str__(self):
        return f"Player #{self.id}: {self.name} ({self.level}) - Assignment: {self.assignment or 'None'}"

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
