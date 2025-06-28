from dataclasses import dataclass
from scramble.utils import Serializable
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
    min_nr_teams_in_match : int = 2
        The minimum number of teams required in a match.
    goal_configs : dict[Goal, GoalConfig] = None
        A dictionary mapping each optimization goal to its configuration.
        If not provided, defaults to the predefined goal configurations.
    """
    min_team_size: int = 2
    min_nr_teams_in_match: int = 2
    goal_configs: dict[Goal, GoalConfig] = None

    def __post_init__(self):
        if self.goal_configs is None:
            self.goal_configs = DEFAULT_GOAL_CONFIGS.copy()
        else:
            # Ensure that all default goals are present in the goal_configs
            for goal in DEFAULT_GOAL_CONFIGS:
                if goal not in self.goal_configs:
                    self.goal_configs[goal] = DEFAULT_GOAL_CONFIGS[goal]

    @classmethod
    def from_dict(cls, data: dict) -> "Settings":
        goal_configs = {Goal(goal): GoalConfig.from_dict(config) for goal, config in data.get("goal_configs", {}).items()}
        return cls(
            min_team_size=data.get("min_team_size", 2),
            min_nr_teams_in_match=data.get("min_nr_teams_in_match", 2),
            goal_configs=goal_configs
        )

    def to_dict(self) -> dict:
        return {
            "min_team_size": self.min_team_size,
            "min_nr_teams_in_match": self.min_nr_teams_in_match,
            "goal_configs": {goal.value: config.to_dict() for goal, config in self.goal_configs.items()}
        }


