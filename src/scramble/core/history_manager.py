import pandas as pd
from scramble.utils import Serializable
from scramble.core.player_history import PlayerHistory
from scramble.core.round import Round


class HistoryManager(Serializable):
    """
    Manages the history of all players, including their partners and opponents.

    Attributes
    ----------
    player_histories : dict[int, PlayerHistory]
        Dictionary mapping player IDs to their PlayerHistory.
    """

    def __init__(self):
        """
        Initializes the HistoryManager with an empty dictionary for player histories.
        """
        self.player_histories: dict[int, PlayerHistory] = {}

    def __str__(self):
        partner_data = {pid: history.partners for pid, history in self.player_histories.items()}
        opponent_data = {pid: history.opponents for pid, history in self.player_histories.items()}
        partner_df = pd.DataFrame(partner_data).fillna(0).astype(int)
        opponent_df = pd.DataFrame(opponent_data).fillna(0).astype(int)
        return (
            "Player Partner History:\n"
            f"{partner_df.to_string()}\n"
            "Player Opponent History:\n"
            f"{opponent_df.to_string()}"
        )


    @classmethod
    def from_dict(cls, data: dict) -> "HistoryManager":
        instance = cls()
        for player_id, history_data in data.items():
            instance.player_histories[int(player_id)] = PlayerHistory.from_dict(history_data)
        return instance

    def to_dict(self) -> dict:
        return {player_id: history.to_dict() for player_id, history in self.player_histories.items()}

    def clear(self):
        """
        Clears the player histories.
        """
        self.player_histories.clear()

    def get_player_history(self, player_id: int) -> PlayerHistory:
        """
        Retrieves the PlayerHistory for the given player ID.

        Parameters
        ----------
        player_id : int
            The ID of the player whose history is to be retrieved.

        Returns
        -------
        PlayerHistory
            The PlayerHistory object for the specified player.
        """
        return self.player_histories.get(player_id, PlayerHistory())

    def get_partner_frequency(self, player_id1: int, player_id2: int) -> int:
        """
        Gets the frequency of matches where player_id1 and player_id2 played together.

        Parameters
        ----------
        player_id1 : int
            The ID of the first player.
        player_id2 : int
            The ID of the second player.

        Returns
        -------
        int
            The number of times the two players have played together.
        """
        history1 = self.get_player_history(player_id1)
        return history1.get_partner_frequency(player_id2)

    def get_opponent_frequency(self, player_id1: int, player_id2: int) -> int:
        """
        Gets the frequency of matches where player_id1 and player_id2 played against each other.

        Parameters
        ----------
        player_id1 : int
            The ID of the first player.
        player_id2 : int
            The ID of the second player.

        Returns
        -------
        int
            The number of times the two players have played against each other.
        """
        history1 = self.get_player_history(player_id1)
        return history1.get_opponent_frequency(player_id2)

    def ensure_player(self, player_id: int):
        """
        Ensures that a PlayerHistory exists for the given player ID.

        Parameters
        ----------
        player_id : int
            The ID of the player to ensure history for.
        """
        if player_id not in self.player_histories:
            self.player_histories[player_id] = PlayerHistory()

    def update_from_round(self, game_round: Round):
        """
        Updates the player histories based on the round matches.

        Parameters
        ----------
        game_round : Round
            The round containing matches to update player histories.
        """
        for player_id, partner_id in game_round.partner_pairs():
            self.ensure_player(player_id)
            self.player_histories[player_id].record_partner(partner_id)

        for player_id, opponent_id in game_round.opponent_pairs():
            self.ensure_player(player_id)
            self.player_histories[player_id].record_opponent(opponent_id)

    def remove_round(self, game_round: Round):
        """
        Removes the player histories based on the round matches.

        Parameters
        ----------
        game_round : Round
            The round containing matches to remove player histories.
        """
        for player_id, partner_id in game_round.partner_pairs():
            if player_id in self.player_histories:
                self.player_histories[player_id].remove_partner(partner_id)

        for player_id, opponent_id in game_round.opponent_pairs():
            if player_id in self.player_histories:
                self.player_histories[player_id].remove_opponent(opponent_id)
