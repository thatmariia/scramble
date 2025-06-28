from dataclasses import dataclass
from collections.abc import Iterator
from itertools import combinations, product

from scramble.core.player import Player
from scramble.core.team import Team
from scramble.core.field import Field


@dataclass
class Match:
    """
    Represents a volleyball match with two or more teams on a field.

    Attributes
    ----------
    teams : list[Team]
        List of teams participating in the match.
    field : Field
        The field on which the match is played.
    """
    teams: list[Team]
    field: Field

    @classmethod
    def from_team_player_ids(
        cls,
        team_player_ids: list[list[int]],
        player_lookup: dict[int, Player],
        field: Field | None = None
    ) -> "Match":
        """
        Creates a Match instance from a list of team player IDs and a player lookup dictionary.

        Parameters
        ----------
        team_player_ids : list[list[int]]
            List of lists, where each inner list contains player IDs for a team.
        player_lookup : dict[int, Player]
            Dictionary mapping player IDs to Player objects.
        field : Field | None = None
            Optional field on which the match is played. If None, a dummy field is used.

        Returns
        -------
        Match
            A new Match instance containing the specified teams and field.
        """
        teams = [Team.from_player_ids(player_ids, player_lookup) for player_ids in team_player_ids]
        if not field:
            field = Field.dummy()
        return cls(teams=teams, field=field)

    def all_player_ids(self) -> set[int]:
        """
        Returns a set of all player IDs across all teams in the match.

        Returns
        -------
        set[int]
            Set of all player IDs.
        """
        return set(player_id for team in self.teams for player_id in team.player_ids())

    def lvl_range(self) -> float:
        """
        Calculates the max difference in average skill level among all teams.

        Returns
        -------
        float
            The difference between the highest and lowest average team level.
            Returns 0.0 if there are fewer than two teams.
        """
        if len(self.teams) < 2:
            return 0.0
        levels = [team.avg_level() for team in self.teams]
        return max(levels) - min(levels)

    def partner_pairs(self) -> Iterator[tuple[int, int]]:
        """
        Generates all pairs of player IDs that are partners in the match.

        Yields
        -------
        tuple[int, int]
            A tuple of player IDs (player_id, partner_id) representing partners in the match.
        """
        for team in self.teams:
            player_ids = list(team.player_ids())
            for a, b in combinations(player_ids, 2):
                yield a, b
                yield b, a

    def opponent_pairs(self) -> Iterator[tuple[int, int]]:
        """
        Generates all pairs of player IDs that are opponents in the match.

        Yields
        -------
        tuple[int, int]
            A tuple of player IDs (player_id, opponent_id) representing opponents in the match.
        """
        for team1, team2 in combinations(self.teams, 2):
            team1_ids = list(team1.player_ids())
            team2_ids = list(team2.player_ids())
            for a, b in product(team1_ids, team2_ids):
                yield a, b
                yield b, a
