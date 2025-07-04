from dataclasses import dataclass, field
from scramble.utils import Serializable
from scramble.core import Court


@dataclass
class CourtState(Serializable):
    """
    Represents the state of courts in the Scramble app.
    This class is used to manage the courts available for matches.

    Attributes
    ----------
    courts : dict[str, Court]
        A dictionary mapping court IDs to Court objects.
    """
    courts: dict[str, Court] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "CourtState":
        courts = {court["id"]: Court.from_dict(court) for court in data.get("courts", [])}
        return cls(courts=courts)

    def to_dict(self) -> dict:
        return {"courts": [court.to_dict() for court_id, court in self.courts.items()]}

    def courts_list(self) -> list[Court]:
        """
        Returns a list of all courts.

        Returns
        -------
        list[Court]
            A list of Court objects representing all available courts.
        """
        return list(self.courts.values())

    def clear(self):
        """
        Clears the courts dictionary.
        This method is used to reset the court state.
        """
        self.courts.clear()

    def add(self, court: Court):
        """
        Adds a court to the courts dictionary.

        Parameters
        ----------
        court : Court
            The court to be added.
        """
        self.courts[court.id] = court

    def remove(self, court_id: str):
        """
        Removes a court from the courts dictionary.

        Parameters
        ----------
        court_id : str
            The ID of the court to be removed.
        """
        if court_id in self.courts:
            del self.courts[court_id]
        else:
            raise ValueError(f"Court with ID {court_id} does not exist in the court state.")

