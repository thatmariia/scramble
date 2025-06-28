from dataclasses import dataclass, field

from scramble.core.player import Player


@dataclass
class PlayerHistory:
    """
    Keeps track of a player's history: who they played with, who they played against.

    Attributes
    ----------
    partners : dict[int, int]
        Dictionary mapping player IDs to the number of matches played with them.
    opponents : dict[int, int]
        Dictionary mapping player IDs to the number of matches played against them.
    """
    partners: dict[int, int] = field(default_factory=dict)
    opponents: dict[int, int] = field(default_factory=dict)

    def get_partner_frequency(self, other_id: int) -> int:
        """
        Gets the frequency of matches where the player played with another player.

        Parameters
        ----------
        other_id : int
            The ID of the other player.

        Returns
        -------
        int
            The number of times the player has played with the other player.
        """
        return self.partners.get(other_id, 0)

    def get_opponent_frequency(self, other_id: int) -> int:
        """
        Gets the frequency of matches where the player played against another player.

        Parameters
        ----------
        other_id : int
            The ID of the other player.

        Returns
        -------
        int
            The number of times the player has played against the other player.
        """
        return self.opponents.get(other_id, 0)

    def record_partner(self, other_id: int):
        """
        Records that the player has played with another player.

        Parameters
        ----------
        other_id : int
            The ID of the other player.
        """
        self.partners[other_id] = self.partners.get(other_id, 0) + 1

    def record_opponent(self, other_id: int):
        """
        Records that the player has played against another player.

        Parameters
        ----------
        other_id : int
            The ID of the other player.
        """
        self.opponents[other_id] = self.opponents.get(other_id, 0) + 1
