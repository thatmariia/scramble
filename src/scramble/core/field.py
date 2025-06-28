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

    @classmethod
    def dummy(cls) -> "Field":
        """
        Creates a dummy field with a default ID and name.

        Returns
        -------
        Field
            A new Field instance with ID -1 and name "Dummy Field".
        """
        return cls(id=-1, name="Dummy Field")
