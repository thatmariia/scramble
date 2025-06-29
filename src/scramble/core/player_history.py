import pandas as pd
from dataclasses import dataclass, field
from scramble.utils import Serializable


@dataclass
class PlayerHistory(Serializable):
    """
    Keeps track of a player's history: who they played with, who they played against.

    Attributes
    ----------
    partners : dict[str, int]
        Dictionary mapping player IDs to the number of matches played with them.
    opponents : dict[str, int]
        Dictionary mapping player IDs to the number of matches played against them.
    """
    partners: dict[str, int] = field(default_factory=dict)
    opponents: dict[str, int] = field(default_factory=dict)

    def __str__(self):
        partner_df = pd.DataFrame.from_dict(self.partners, orient='index', columns=['Frequency']).fillna(0).astype(int)
        opponent_df = pd.DataFrame.from_dict(self.opponents, orient='index', columns=['Frequency']).fillna(0).astype(int)
        combined_df = pd.concat([partner_df, opponent_df], axis=1, keys=['Partners', 'Opponents'])
        return (
            f"Player History:\n"
            f"{combined_df.to_string()}\n"
        )



    @classmethod
    def from_dict(cls, data: dict) -> "PlayerHistory":
        return cls(
            partners=data.get("partners", {}),
            opponents=data.get("opponents", {})
        )

    def to_dict(self) -> dict:
        return {
            "partners": self.partners,
            "opponents": self.opponents,
        }

    def get_partner_frequency(self, other_id: str) -> int:
        """
        Gets the frequency of matches where the player played with another player.

        Parameters
        ----------
        other_id : str
            The ID of the other player.

        Returns
        -------
        int
            The number of times the player has played with the other player.
        """
        return self.partners.get(other_id, 0)

    def get_opponent_frequency(self, other_id: str) -> int:
        """
        Gets the frequency of matches where the player played against another player.

        Parameters
        ----------
        other_id : str
            The ID of the other player.

        Returns
        -------
        int
            The number of times the player has played against the other player.
        """
        return self.opponents.get(other_id, 0)

    def record_partner(self, other_id: str):
        """
        Records that the player has played with another player.

        Parameters
        ----------
        other_id : str
            The ID of the other player.
        """
        self.partners[other_id] = self.partners.get(other_id, 0) + 1

    def record_opponent(self, other_id: str):
        """
        Records that the player has played against another player.

        Parameters
        ----------
        other_id : str
            The ID of the other player.
        """
        self.opponents[other_id] = self.opponents.get(other_id, 0) + 1

    def remove_partner(self, other_id: str):
        """
        Removes the record of a partnership with another player (reduces by 1).

        Parameters
        ----------
        other_id : str
            The ID of the other player.
        """
        if other_id in self.partners:
            self.partners[other_id] -= 1
            if self.partners[other_id] <= 0:
                del self.partners[other_id]

    def remove_opponent(self, other_id: str):
        """
        Removes the record of an opponent (reduces by 1).

        Parameters
        ----------
        other_id : str
            The ID of the other player.
        """
        if other_id in self.opponents:
            self.opponents[other_id] -= 1
            if self.opponents[other_id] <= 0:
                del self.opponents[other_id]

