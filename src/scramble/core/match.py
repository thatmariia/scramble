from dataclasses import dataclass
from collections.abc import Iterator
from itertools import combinations, product
from scramble.utils import Serializable
from scramble.core.player import Player
from scramble.core.team import Team
from scramble.core.court import Court


@dataclass
class Match(Serializable):
    """
    Represents a volleyball match with two or more teams on a court.

    Attributes
    ----------
    teams : list[Team]
        List of teams participating in the match.
    court : Court
        The court on which the match is played.
    """
    teams: list[Team]
    court: Court

    def __str__(self):
        team_strs = "\n".join(str(team) for team in self.teams)
        return f"Match on {self.court}:\n{team_strs}"

    @classmethod
    def from_dict(cls, data: dict) -> "Match":
        teams = [Team.from_dict(team) for team in data.get("teams", [])]
        court = Court.from_dict(data.get("court", {}))
        return cls(teams=teams, court=court)

    def to_dict(self) -> dict:
        return {
            "teams": [team.to_dict() for team in self.teams],
            "court": self.court.to_dict(),
        }

    def all_player_ids(self) -> set[str]:
        """
        Returns a set of all player IDs across all teams in the match.

        Returns
        -------
        set[str]
            Set of all player IDs.
        """
        return set(player_id for team in self.teams for player_id in team.player_ids())

    def partner_pairs(self) -> Iterator[tuple[str, str]]:
        """
        Generates all pairs of player IDs that are partners in the match.

        Yields
        -------
        tuple[str, str]
            A tuple of player IDs (player_id, partner_id) representing partners in the match.
        """
        for team in self.teams:
            player_ids = list(team.player_ids())
            for a, b in combinations(player_ids, 2):
                yield a, b
                yield b, a

    def opponent_pairs(self) -> Iterator[tuple[str, str]]:
        """
        Generates all pairs of player IDs that are opponents in the match.

        Yields
        -------
        tuple[str, str]
            A tuple of player IDs (player_id, opponent_id) representing opponents in the match.
        """
        for team1, team2 in combinations(self.teams, 2):
            team1_ids = list(team1.player_ids())
            team2_ids = list(team2.player_ids())
            for a, b in product(team1_ids, team2_ids):
                yield a, b
                yield b, a
