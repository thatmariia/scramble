from dataclasses import dataclass

from scramble.settings.goal import Goal
from scramble.settings.goal_config import GoalConfig, DEFAULT_GOAL_CONFIGS


@dataclass
class Settings:
    """
    Settings for the optimization process.

    Attributes:
    ----------
    team_size : int = 2
        The number of players in each team.
    min_nr_teams_in_match : int = 2
        The minimum number of teams required in a match.
    nr_fields : int = 1
        The number of fields available for matches.
    goal_configs : dict[Goal, GoalConfig] = None
        A dictionary mapping each optimization goal to its configuration.
        If not provided, defaults to the predefined goal configurations.
    """
    team_size: int = 2
    min_nr_teams_in_match: int = 2
    nr_fields: int = 1
    goal_configs: dict[Goal, GoalConfig] = None

    def __post_init__(self):
        if self.goal_configs is None:
            self.goal_configs = DEFAULT_GOAL_CONFIGS.copy()
        else:
            # Ensure that all default goals are present in the goal_configs
            for goal in DEFAULT_GOAL_CONFIGS:
                if goal not in self.goal_configs:
                    self.goal_configs[goal] = DEFAULT_GOAL_CONFIGS[goal]
