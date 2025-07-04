from typing import Protocol, TypeVar, Type

# T = TypeVar("T", bound="Serializable")


class Serializable():
    def to_dict(self) -> dict:
        """Convert the object to a dictionary."""
        ...

    @classmethod
    def from_dict(cls, data: dict) -> "Serializable":
        """Create the object from a dictionary."""
        ...