from dataclasses import dataclass, field

from scramble.core import Court


@dataclass
class CourtState:
    """
    Represents the state of courts in the Scramble app.
    This class is used to manage the courts available for matches.

    Attributes
    ----------
    courts : dict[int, Court]
        A dictionary mapping court IDs to Court objects.
    """
    courts: dict[int, Court] = field(default_factory=dict)

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

    def remove(self, court_id: int):
        """
        Removes a court from the courts dictionary.

        Parameters
        ----------
        court_id : int
            The ID of the court to be removed.
        """
        if court_id in self.courts:
            del self.courts[court_id]

