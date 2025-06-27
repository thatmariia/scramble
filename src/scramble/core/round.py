from dataclasses import dataclass, field

from scramble.core.match import Match
from scramble.core.player import Player


@dataclass
class Round:
    """
    Represents a full round of play: the matches played in the round, and the resting players.

    Attributes
    ----------
    matches : list[Match]
        List of matches played in the round.
    resting_players : list[Player]
        List of players who are resting during the round (not involved in any matches).
    """
    matches: list[Match] = field(default_factory=list)
    resting_players: list[Player] = field(default_factory=list)
