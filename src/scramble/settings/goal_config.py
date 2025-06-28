from dataclasses import dataclass
from scramble.utils import Serializable
from scramble.settings.goal import Goal


@dataclass
class GoalConfig(Serializable):
    """
    Configuration for a specific optimization goal.
    Contains the goal type, whether it is enabled, and its weight in the optimization process.

    Attributes:
    ----------
    goal : Goal
        The type of goal to be optimized for.
    enabled : bool = True
        Whether this goal is enabled in the optimization process.
    weight : float = 1.0
        The weight of this goal in the optimization process, determining its influence relative to other goals.
    """
    goal: Goal
    enabled: bool = True
    weight: float = 1.0

    @classmethod
    def from_dict(cls, data: dict) -> "GoalConfig":
        return cls(
            goal=Goal(data["goal"]),
            enabled=data.get("enabled", True),
            weight=data.get("weight", 1.0)
        )

    def to_dict(self) -> dict:
        return {
            "goal": self.goal.value,
            "enabled": self.enabled,
            "weight": self.weight
        }


DEFAULT_GOAL_CONFIGS = {
    Goal.KEEP_IDEAL_TEAM_SIZE: GoalConfig(goal=Goal.KEEP_IDEAL_TEAM_SIZE, enabled=True, weight=1.0),
    Goal.BALANCE_LVL: GoalConfig(goal=Goal.BALANCE_LVL, enabled=True, weight=1.0),
    Goal.DIVERSIFY_PARTNERS: GoalConfig(goal=Goal.DIVERSIFY_PARTNERS, enabled=True, weight=1.0),
    Goal.DIVERSIFY_OPPONENTS: GoalConfig(goal=Goal.DIVERSIFY_OPPONENTS, enabled=True, weight=1.0),
}