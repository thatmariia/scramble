# from scramble.settings import Goal
# from scramble.core import Level
# from scramble.solver.model_variables import ModelVariables
#
#
# class UpperBoundsComputer:
#     """
#     Computes upper bounds for various optimization goals based on the provided model variables.
#     This class is used to determine the maximum possible values for each goal in the optimization process.
#     """
#
#     def __init__(self, mv: ModelVariables):
#         self.mv = mv
#
#     def compute_upper_bounds(self) -> dict[Goal, int]:
#         """
#         Computes upper bounds for all goals defined in the model variables.
#
#         Return
#         -------
#         dict[Goal, int]
#             A dictionary mapping each goal to its computed upper bound.
#         """
#         return {goal: self.compute_upper_bound(goal) for goal in self.mv.settings.goal_configs.keys()}
#
#     def compute_upper_bound(self, goal: Goal) -> int:
#         """
#         Computes the upper bound for a specific goal.
#
#         Parameters
#         ----------
#         goal : Goal
#             The optimization goal for which to compute the upper bound.
#         """
#         match goal:
#             case Goal.KEEP_IDEAL_TEAM_SIZE:
#                 return self._compute_ideal_team_size()
#             case Goal.BALANCE_LVL:
#                 return self._compute_balance_level()
#             case Goal.REDUCE_LVL_GAP:
#                 return self._compute_reduce_level_gap()
#             case Goal.DIVERSIFY_PARTNERS:
#                 return self._compute_diversify_partners()
#             case Goal.DIVERSIFY_OPPONENTS:
#                 return self._compute_diversify_opponents()
#             case Goal.MAXIMIZE_COURTS_USAGE:
#                 return self._compute_maximize_courts_usage()
#             case _:
#                 raise ValueError(f"Unknown goal: {goal}")
#
#     def _compute_ideal_team_size(self) -> int:
#         return self.mv.nr_teams * (self.mv.settings.max_team_size - self.mv.settings.min_team_size)
#
#     def _compute_balance_level(self) -> int:
#         return min(1000, self.mv.nr_teams * self.mv.nr_teams * self.mv.settings.max_team_size * Level.max_value())
#
#     def _compute_reduce_level_gap(self) -> int:
#         return self.mv.nr_teams * self.mv.settings.max_team_size * Level.max_value()
#
#     def _compute_diversify_partners(self) -> int:
#         return self.mv.history.get_all_partners_counts()
#
#     def _compute_diversify_opponents(self) -> int:
#         return self.mv.history.get_all_opponents_counts()
#
#     def _compute_maximize_courts_usage(self) -> int:
#         return len(self.mv.courts)
#
