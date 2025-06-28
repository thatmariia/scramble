from enum import Enum


class Goal(str, Enum):
    """
    Enum representing different types of optimization goals.
    Each goal corresponds to a specific aspect of team formation in a match.

    Attributes:
    ----------
    KEEP_IDEAL_TEAM_SIZE : str
        Ensures that teams have the ideal number of players.
    BALANCE_LVL : str
        Ensures that teams in a match are balanced in terms of player level.
    DIVERSIFY_PARTNERS : str
        Ensures that players play with different partners across matches.
    DIVERSIFY_OPPONENTS : str
        Ensures that players play against different opponents across matches.
    """
    KEEP_IDEAL_TEAM_SIZE = "Teams should have the ideal number of players."
    BALANCE_LVL = "Teams in a match should be balanced in terms of level."
    DIVERSIFY_PARTNERS = "Players should play with different partners."
    DIVERSIFY_OPPONENTS = "Players should play against different opponents."

    def __str__(self):
        return self.value



