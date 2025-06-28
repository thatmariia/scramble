from scoring_functions import SCORING_FUNCTIONS
from scramble.settings.goal import Goal
from scramble.settings.goal_config import GoalConfig
from scramble.core.match import Match
from scramble.core.history_manager import HistoryManager


def score_match(match: Match, history: HistoryManager, active_goals: dict[Goal, GoalConfig]) -> float:
    """
    Computes the total weighted penalty score for a match based on active goals.
    Lower scores are better.

    Parameters
    ----------
    match : Match
        The match to be scored.
    history : HistoryManager
        The history manager containing player histories.
    active_goals : dict[Goal, GoalConfig]
        A dictionary mapping active goals to their configurations.

    Returns
    -------
    float
        The total penalty score for the match.
    """
    total_score = 0.0
    for goal, config in active_goals.items():
        if config.enabled:
            scoring_fn = SCORING_FUNCTIONS.get(goal)
            if scoring_fn:
                total_score += scoring_fn(match, history) * config.weight
    return total_score
