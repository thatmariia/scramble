from typing import Protocol, TypeVar, Type

T = TypeVar("T", bound="Serializable")


class Serializable(Protocol):
    def to_dict(self) -> dict:
        """Convert the object to a dictionary."""
        ...

    @classmethod
    def from_dict(cls: Type[T], data: dict) -> T:
        """Create the object from a dictionary."""
        ...