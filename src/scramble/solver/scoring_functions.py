from typing import Protocol
from scramble.settings import Goal, Settings
from scramble.core import Match, HistoryManager


# --- Scoring function protocol ---

class ScoringFunction(Protocol):
    def __call__(self, match: Match, history: HistoryManager, settings: Settings) -> float:
        """
        A scoring function computes a penalty (higher is worse) for a match,
        possibly using the player history.

        Parameters
        ----------
        match : Match
            The match to be scored.
        history : HistoryManager
            The history manager containing player histories.
        settings : Settings
            The settings for the scramble solver.

        Returns
        -------
        float
            A non-negative penalty score.
        """
        ...


# --- Individual goal scoring functions ---

def score_keep_ideal_team_size(match: Match, history_manager: HistoryManager, settings: Settings) -> float:
    """
    Penalty for teams not having the ideal number of players.
    Higher deviation from the ideal team size = higher penalty.

    Conforms to the ScoreFunction protocol.
    """
    ideal_team_size = settings.min_team_size
    score = 0.0
    for team in match.teams:
        team_size = len(team.players)
        score += abs(team_size - ideal_team_size)
    return score


def score_balance_lvl(match: Match, history_manager: HistoryManager, settings: Settings) -> float:
    """
    Penalty for unbalanced teams in terms of player level.
    Higher level difference = higher penalty.

    Conforms to the ScoreFunction protocol.
    """
    return match.lvl_range()


def score_diversify_partners(match: Match, history_manager: HistoryManager, settings: Settings) -> float:
    """
    Penalty for players playing with the same partner too often.
    Higher frequency of the same partner = higher penalty.

    Conforms to the ScoreFunction protocol.
    """
    score = 0.0
    for team in match.teams:
        player_ids = team.player_ids()
        for pid1 in player_ids:
            for pid2 in player_ids:
                if pid1 != pid2:
                    # count how many times pid1 and pid2 played together
                    freq = history_manager.get_partner_frequency(pid1, pid2)
                    score += max(0, freq - 1)  # penalize if they played together more than once
    return score


def score_diversify_opponents(match: Match, history_manager: HistoryManager, settings: Settings) -> float:
    """
    Penalty for players playing against the same opponent too often.
    Higher frequency of the same opponent = higher penalty.

    Conforms to the ScoreFunction protocol.
    """
    score = 0.0
    for team in match.teams:
        player_ids = team.player_ids()
        for pid1 in player_ids:
            for pid2 in player_ids:
                if pid1 != pid2:
                    # count how many times pid1 and pid2 played against each other
                    freq = history_manager.get_opponent_frequency(pid1, pid2)
                    score += max(0, freq - 1)  # penalize if they played against each other more than once
    return score


# --- Scoring dispatch map ---

SCORING_FUNCTIONS: dict[Goal, ScoringFunction] = {
    Goal.KEEP_IDEAL_TEAM_SIZE: score_keep_ideal_team_size,
    Goal.BALANCE_LVL: score_balance_lvl,
    Goal.DIVERSIFY_PARTNERS: score_diversify_partners,
    Goal.DIVERSIFY_OPPONENTS: score_diversify_opponents,
}
