from collections import deque
from scramble.utils import Serializable
from scramble.core.round import Round
from scramble.core.history_manager import HistoryManager


class RoundTracker(Serializable):
    """
    Tracks the sequence of rounds played and manages player histories.

    Attributes
    ----------
    history_manager : HistoryManager
        The history manager containing player histories.
    rounds : deque[Round]
        A deque of rounds, where each round contains matches and resting players.
    """

    def __init__(self, history_manager: HistoryManager | None = None):
        """
        Initializes the RoundTracker with a history manager.

        Parameters
        ----------
        history_manager : HistoryManager | None = None
            The history manager containing player histories.
            If None, a new HistoryManager instance will be created.
        """
        self.history_manager: HistoryManager = history_manager or HistoryManager()
        self.rounds: deque[Round] = deque()

    @classmethod
    def from_dict(cls, data: dict) -> "RoundTracker":
        history_manager = HistoryManager.from_dict(data.get("player_histories", {}))
        rounds = [Round.from_dict(round_data) for round_data in data.get("rounds", [])]
        tracker = cls(history_manager=history_manager)
        tracker.rounds.extend(rounds)
        return tracker

    def to_dict(self) -> dict:
        return {
            "rounds": [game_round.to_dict() for game_round in self.rounds],
            "player_histories": self.history_manager.to_dict(),
        }

    @property
    def all_rounds(self) -> list[Round]:
        """
        Returns a list of all rounds tracked by the RoundTracker.

        Returns
        -------
        list[Round]
            A list containing all rounds in the tracker.
        """
        return list(self.rounds)

    def clear(self):
        """
        Clears the round tracker and resets the player histories.
        """
        while self.rounds:
            self.undo_last_round()
        self.history_manager.clear()

    def add_round(self, game_round: Round):
        """
        Adds a new round to the tracker and updates player histories.

        Parameters
        ----------
        game_round : Round
            The round to be added.
        """
        self.history_manager.update_from_round(game_round)
        self.rounds.append(game_round)

    def undo_last_round(self):
        """
        Removes the last round from the tracker and updates player histories accordingly.
        """
        if not self.rounds:
            raise ValueError("No rounds to undo.")
        last_round = self.rounds.pop()
        self.history_manager.remove_round(last_round)

    def replace_last_round(self, game_round: Round):
        """
        Replaces the last round with a new round and updates player histories.

        Parameters
        ----------
        game_round : Round
            The new round to replace the last one.
        """
        if not self.rounds:
            return
        self.undo_last_round()
        self.add_round(game_round)
