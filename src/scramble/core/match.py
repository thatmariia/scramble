from dataclasses import dataclass

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