from dataclasses import dataclass
import math
from itertools import combinations_with_replacement
from copy import deepcopy
from scramble.utils import Serializable
from scramble.core import Level
from scramble.settings.goal import Goal
from scramble.settings.goal_config import GoalConfig, DEFAULT_GOAL_CONFIGS


@dataclass
class Settings(Serializable):
    """
    Settings for the optimization process.

    Attributes:
    ----------
    min_team_size : int = 2
        The number of players in each team.
    max_team_size : int = 5
        The maximum number of players in each team.
    min_nr_teams_in_match : int = 2
        The minimum number of teams required in a match.
    goal_configs : dict[Goal, GoalConfig] = None
        A dictionary mapping each optimization goal to its configuration.
        If not provided, defaults to the predefined goal configurations.
    """
    min_team_size: int = 2
    max_team_size: int = 3
    min_nr_teams_in_match: int = 2
    goal_configs: dict[Goal, GoalConfig] | None = None

    def __post_init__(self):
        # ensure that min_team_size and max_team_size are valid
        self.max_team_size = max(self.min_team_size, self.max_team_size)

        # ensure goal_configs is initialized, default values if some goals not provided
        if self.goal_configs is None:
            self.goal_configs = deepcopy(DEFAULT_GOAL_CONFIGS)
        else:
            # Ensure that all default goals are present in the goal_configs
            for goal in DEFAULT_GOAL_CONFIGS:
                if goal not in self.goal_configs:
                    self.goal_configs[goal] = deepcopy(DEFAULT_GOAL_CONFIGS[goal])

    def __str__(self):
        goal_configs_str = "None"
        lvl_scores_str = "None"
        if self.goal_configs is not None:
            goal_configs_str = "\n - ".join(f"{goal.value}: {config}" for goal, config in self.goal_configs.items())
        return "Settings:\n" + "\n" + \
                f"Team size: {self.min_team_size}-{self.max_team_size}\n" + \
                f"Min teams in match: {self.min_nr_teams_in_match}\n" + \
                f"Goal configs: {goal_configs_str}\n"

    @classmethod
    def from_dict(cls, data: dict) -> "Settings":
        goal_configs = {Goal(goal): GoalConfig.from_dict(config) for goal, config in data.get("goal_configs", {}).items()}
        return cls(
            min_team_size=data.get("min_team_size", 2),
            max_team_size=data.get("max_team_size", 5),
            min_nr_teams_in_match=data.get("min_nr_teams_in_match", 2),
            goal_configs=goal_configs
        )

    def to_dict(self) -> dict:
        return {
            "min_team_size": self.min_team_size,
            "max_team_size": self.max_team_size,
            "min_nr_teams_in_match": self.min_nr_teams_in_match,
            "goal_configs": {goal.value: config.to_dict() for goal, config in self.goal_configs.items()}
        }

    def lcm_sizes(self):
        team_sizes = list(range(self.min_team_size, self.max_team_size + 1))
        lcm_sizes = math.lcm(*team_sizes)
        return lcm_sizes


