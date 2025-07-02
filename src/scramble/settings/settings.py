from dataclasses import dataclass
from itertools import combinations_with_replacement
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
    max_team_size: int = 5
    min_nr_teams_in_match: int = 2
    goal_configs: dict[Goal, GoalConfig] | None = None
    team_lvl_scores: dict | None = None
    log_enabled: bool = True
    log_verbose: bool = True

    def __post_init__(self):
        self.max_team_size = max(self.min_team_size, self.max_team_size)
        self._create_team_lvl_scores()
        if self.goal_configs is None:
            self.goal_configs = DEFAULT_GOAL_CONFIGS.copy()
        else:
            # Ensure that all default goals are present in the goal_configs
            for goal in DEFAULT_GOAL_CONFIGS:
                if goal not in self.goal_configs:
                    self.goal_configs[goal] = DEFAULT_GOAL_CONFIGS[goal]
        # print(self)

    def __str__(self):
        goal_configs_str = "None"
        lvl_scores_str = "None"
        if self.goal_configs is not None:
            goal_configs_str = "\n - ".join(f"{goal.value}: {config}" for goal, config in self.goal_configs.items())
        if self.team_lvl_scores is not None:
            lvl_scores_str = "\n - ".join(f"{key}: {value}" for key, value in self.team_lvl_scores.items())
        return "Settings:\n" + "\n" + \
                f"Team size: {self.min_team_size}-{self.max_team_size}\n" + \
                f"Min teams in match: {self.min_nr_teams_in_match}\n" + \
                f"Goal configs: {goal_configs_str}\n" + \
                f"Log enabled: {self.log_enabled}\n" + \
                f"Log verbose: {self.log_verbose}\n" + \
                f"Team level scores: {lvl_scores_str}\n"

    @classmethod
    def from_dict(cls, data: dict) -> "Settings":
        goal_configs = {Goal(goal): GoalConfig.from_dict(config) for goal, config in data.get("goal_configs", {}).items()}
        return cls(
            min_team_size=data.get("min_team_size", 2),
            max_team_size=data.get("max_team_size", 5),
            min_nr_teams_in_match=data.get("min_nr_teams_in_match", 2),
            goal_configs=goal_configs,
            log_enabled=data.get("log_enabled", 2),
            log_verbose=data.get("log_verbose", 2)
        )

    def to_dict(self) -> dict:
        return {
            "min_team_size": self.min_team_size,
            "max_team_size": self.max_team_size,
            "min_nr_teams_in_match": self.min_nr_teams_in_match,
            "goal_configs": {goal.value: config.to_dict() for goal, config in self.goal_configs.items()},
            "log_enabled": self.log_enabled,
            "log_verbose": self.log_verbose
        }

    def _create_team_lvl_scores(self):
        """
        Creates a dictionary to hold team level scores based on the goal configurations.
        This method is called to initialize the team_lvl_scores attribute.
        """
        self.team_lvl_scores = {(0, 0): 0}
        scale = self.min_team_size * self.max_team_size
        all_levels = Level.all_values()
        for team_size in range(self.min_team_size, self.max_team_size + 1):
            self.team_lvl_scores[(0, team_size)] = 0
            for lvl_combo in combinations_with_replacement(all_levels, team_size):
                key = (sum(lvl_combo), team_size)
                value = sum(lvl_combo) * scale // team_size if team_size > 0 else 0
                self.team_lvl_scores[key] = value


