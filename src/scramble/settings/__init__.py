"""
This module provides the settings and configurations for the Scramble application.
It includes goal definitions, configurations, and general settings used throughout the application.
"""

from .goal import Goal
from .goal_config import GoalConfig, DEFAULT_GOAL_CONFIGS
from .settings import Settings

__all__ = [
    "Goal",
    "GoalConfig",
    "DEFAULT_GOAL_CONFIGS",
    "Settings",
]
