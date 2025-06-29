from dataclasses import dataclass
from scramble.utils import Serializable
from scramble.core.player import Player


@dataclass
class Team(Serializable):
    """
    Represents a volleyball team with an ID, name, and a list of players.

    Attributes
    ----------
    players : list[Player]
        List of players in the team.
    """
    players: list[Player] = None

    def __str__(self):
        player_names = "\n".join(" - " + str(player) for player in self.players) if self.players else "No players"
        return f"Team:\n{player_names}"

    @classmethod
    def from_dict(cls, data: dict) -> "Team":
        players = [Player.from_dict(player) for player in data.get("players", [])]
        return cls(players=players)

    def to_dict(self) -> dict:
        return {
            "players": [player.to_dict() for player in self.players] if self.players else []
        }

    @classmethod
    def from_player_ids(cls, player_ids: list[int], player_lookup: dict[int, Player]) -> "Team":
        """
        Creates a Team instance from a list of player IDs and a player lookup dictionary.

        Parameters
        ----------
        player_ids : list[int]
            List of player IDs to include in the team.
        player_lookup : dict[int, Player]
            Dictionary mapping player IDs to Player objects.

        Returns
        -------
        Team
            A new Team instance containing the specified players.
        """
        players = [player_lookup[pid] for pid in player_ids if pid in player_lookup]
        return cls(players=players)

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
        return float(sum(player.level.value for player in self.players)) / len(self.players)
