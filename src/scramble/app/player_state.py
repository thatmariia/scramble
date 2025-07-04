from dataclasses import dataclass, field
from scramble.utils import Serializable
from scramble.core import Player


@dataclass
class PlayerState(Serializable):
    """
    Represents the state of players in the Scramble app.
    This class is used to manage active and resting players during a session.

    Attributes
    ----------
    active_players : dict[str, Player]
        A dictionary mapping player IDs to Player objects for active players.
    resting_players : dict[str, Player]
        A dictionary mapping player IDs to Player objects for resting players.
    """
    active_players: dict[str, Player] = field(default_factory=dict)
    resting_players: dict[str, Player] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "PlayerState":
        active_players = {player["id"]: Player.from_dict(player) for player in data.get("active_players", [])}
        resting_players = {player["id"]: Player.from_dict(player) for player in data.get("resting_players", [])}
        return cls(active_players=active_players, resting_players=resting_players)

    def to_dict(self) -> dict:
        return {
            "active_players": [player.to_dict() for player in self.active_list()],
            "resting_players": [player.to_dict() for player in self.resting_list()],
        }

    def all_players_ids(self):
        """
        Returns a list of all player IDs, both active and resting.

        Returns
        -------
        list[str]
            A list of player IDs.
        """
        return list(self.active_players.keys()) + list(self.resting_players.keys())

    def active_list(self):
        """
        Returns a list of active players.

        Returns
        -------
        list[Player]
            A list of Player objects representing active players.
        """
        return list(self.active_players.values())

    def resting_list(self):
        """
        Returns a list of resting players.

        Returns
        -------
        list[Player]
            A list of Player objects representing resting players.
        """
        return list(self.resting_players.values())

    def clear(self):
        """
        Clears both active and resting players.
        This method is used to reset the player state.
        """
        self.active_players.clear()
        self.resting_players.clear()

    def add(self, player: Player):
        """
        Adds a player to the active players list.

        Parameters
        ----------
        player : Player
            The player to be added.
        """
        self.active_players[player.id] = player

    def remove(self, player_id: str):
        """
        Removes a player from the active or resting players.

        If the player is active, they are removed from active players.
        If the player is resting, they are removed from resting players.

        Parameters
        ----------
        player_id : str
            The ID of the player to be removed.
        """
        if player_id in self.active_players:
            del self.active_players[player_id]
        elif player_id in self.resting_players:
            del self.resting_players[player_id]
        else:
            raise ValueError(f"Player with ID {player_id} not found in active or resting players.")

    def toggle_rest(self, player_id: str) -> Player:
        """
        Toggles the resting state of a player.

        If the player is active, they are moved to resting players.
        If the player is resting, they are moved back to active players.

        Parameters
        ----------
        player_id : str
            The ID of the player whose resting state is to be toggled.
        """
        if player_id in self.active_players:
            self.resting_players[player_id] = self.active_players.pop(player_id)
            return self.resting_players[player_id]
        elif player_id in self.resting_players:
            self.active_players[player_id] = self.resting_players.pop(player_id)
            return self.active_players[player_id]
        else:
            raise ValueError(f"Player with ID {player_id} not found in active or resting players.")