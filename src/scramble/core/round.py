from dataclasses import dataclass, field
from collections.abc import Iterator
from itertools import chain

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

    def partner_pairs(self) -> Iterator[tuple[int, int]]:
        """
        Iterates through all partners in the matches of the round.

        Yields
        -------
        tuple[int, int]
            A tuple containing the IDs of two players who are partners in a match.
        """
        return chain.from_iterable(match.partner_pairs() for match in self.matches)

    def opponent_pairs(self) -> Iterator[tuple[int, int]]:
        """
        Iterates through all opponents in the matches of the round.

        Yields
        -------
        tuple[int, int]
            A tuple containing the IDs of two players who are opponents in a match.
        """
        return chain.from_iterable(match.opponent_pairs() for match in self.matches)
