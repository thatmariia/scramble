from scramble.core.player_history import PlayerHistory


class HistoryManager:
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

    def update_from_round(self, round):
        """
        Updates the player histories based on the round matches.

        Parameters
        ----------
        round : Round
            The round containing matches to update player histories.
        """
        for match in round.matches:
            teams = match.teams

            # record partners
            for team in teams:
                for player in team.active_players:
                    self.ensure_player(player.id)
                    for other_player in team.active_players:
                        if player.id != other_player.id:
                            self.player_histories[player.id].record_partner(other_player.id)

            # record opponents
            for team in teams:
                for player in team.active_players:
                    self.ensure_player(player.id)
                    for other_team in teams:
                        if team != other_team:
                            for opponent in other_team.active_players:
                                self.player_histories[player.id].record_opponent(opponent.id)
