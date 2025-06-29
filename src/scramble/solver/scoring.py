from scramble.solver.scoring_functions import SCORING_FUNCTIONS
from scramble.settings import Goal, GoalConfig, Settings
from scramble.core import Match, HistoryManager


def score_match(match: Match, history: HistoryManager, settings: Settings) -> float:
    """
    Computes the total weighted penalty score for a match based on active goals.
    Lower scores are better.

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
        The total penalty score for the match.
    """
    total_score = 0.0
    for goal, config in settings.goal_configs.items():
        if config.enabled:
            scoring_fn = SCORING_FUNCTIONS.get(goal)
            if scoring_fn:
                total_score += scoring_fn(match, history, settings) * config.weight
    return total_score
