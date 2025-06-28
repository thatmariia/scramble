from dataclasses import dataclass


@dataclass
class Court:
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
    def dummy(cls) -> "Court":
        """
        Creates a dummy court with a default ID and name.

        Returns
        -------
        Court
            A new Court instance with ID -1 and name "Dummy Court".
        """
        return cls(id=-1, name="Dummy Court")
