from dataclasses import dataclass, field
from collections.abc import Iterator
from itertools import chain
from scramble.utils import Serializable
from scramble.core.match import Match


@dataclass
class Round(Serializable):
    """
    Represents a full round of play: the matches played in the round, and the resting players.

    Attributes
    ----------
    matches : list[Match]
        List of matches played in the round.
    """
    matches: list[Match] = field(default_factory=list)

    def __str__(self):
        separator = "-" * 40
        matches_sorted = sorted(self.matches, key=lambda m: m.court.id)
        match_strs = f"\n{separator}\n".join(str(match) for match in matches_sorted)
        return f"Round:\n{match_strs}\n{separator}"


    @classmethod
    def from_dict(cls, data: dict) -> "Round":
        matches = [Match.from_dict(match) for match in data.get("matches", [])]
        return cls(matches=matches)

    def to_dict(self) -> dict:
        return {"matches": [match.to_dict() for match in self.matches]}

    def partner_pairs(self) -> Iterator[tuple[str, str]]:
        """
        Iterates through all partners in the matches of the round.

        Yields
        -------
        tuple[str, str]
            A tuple containing the IDs of two players who are partners in a match.
        """
        return chain.from_iterable(match.partner_pairs() for match in self.matches)

    def opponent_pairs(self) -> Iterator[tuple[str, str]]:
        """
        Iterates through all opponents in the matches of the round.

        Yields
        -------
        tuple[str, str]
            A tuple containing the IDs of two players who are opponents in a match.
        """
        return chain.from_iterable(match.opponent_pairs() for match in self.matches)
