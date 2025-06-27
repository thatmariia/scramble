from dataclasses import dataclass


@dataclass
class Field:
    """
    Represents a volleyball field with an ID and name.

    Attributes
    ----------
    id : int
        Unique identifier for the field.
    name : str
        Name of the field.
    """
    id: int
    name: str
