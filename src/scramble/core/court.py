from dataclasses import dataclass, asdict
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
    id: int
    name: str

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

