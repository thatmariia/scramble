from dataclasses import dataclass, asdict, field
import uuid
from scramble.utils import Serializable


@dataclass
class Court(Serializable):
    """
    Represents a volleyball court with an ID and name.

    Attributes
    ----------
    id : int
        Unique identifier for the court.
    name : str
        Name of the court.
    """
    name: str
    id: int = field(default_factory=lambda: uuid.uuid4().int)

    def __str__(self):
        return f"Court #{self.id}: {self.name}"

    @classmethod
    def from_dict(cls, data: dict) -> "Court":
        return cls(**data)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def dummy(cls) -> "Court":
        """
        Creates a dummy court with a default ID and name.

        Returns
        -------
        Court
            A new Court instance with ID -1 and name "Dummy Court".
        """
        return cls(id=-1, name="Dummy Court")

