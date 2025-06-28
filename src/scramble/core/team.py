from dataclasses import dataclass

from scramble.core.player import Player


@dataclass
class Team:
    """
    Represents a volleyball team with an ID, name, and a list of players.

    Attributes
    ----------
    players : list[Player]
        List of players in the team.
    """
    players: list[Player] = None

    def player_ids(self) -> set[int]:
        """
        Returns a set of player IDs in the team.

        Returns
        -------
        set[int]
            Set of player IDs.
        """
        return set([player.id for player in self.players] if self.players else [])

    def avg_level(self) -> float:
        """
        Calculates the average level of the players in the team.

        Returns
        -------
        float
            The average level of the players in the team.
        """
        if not self.players:
            return 0.0
        return sum(player.level.value for player in self.players) / len(self.players)