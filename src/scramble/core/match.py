from dataclasses import dataclass

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

    def lvl_range(self) -> int:
        """
        Calculates the max difference in average skill level among all teams.
        """
        if len(self.teams) < 2:
            return 0
        levels = [team.avg_level() for team in self.teams]
        return max(levels) - min(levels)
