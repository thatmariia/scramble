from scramble.solver.model_variables import ModelVariables
from scramble.settings import Goal
from scramble.core import Level


def rough_upper_bound(mv: ModelVariables, goal: Goal) -> int:
    """
    Rough upper bound per goal to limit the search space in the CP model.
    This function provides an upper bound for the objective function based on the goal.

    Parameters
    ----------
    mv : ModelVariables
        The model variables containing the current state of the model.
    goal : Goal
        The goal for which the upper bound is calculated.

    Returns
    -------
    int
        An upper bound for the objective function based on the specified goal.
    """
    if goal == Goal.KEEP_IDEAL_TEAM_SIZE:
        return mv.nr_teams * (mv.settings.max_team_size - mv.settings.min_team_size)

    if goal == Goal.BALANCE_LVL:
        return min(1000, mv.nr_teams * mv.nr_teams * mv.settings.max_team_size * Level.max_value())

    if goal == Goal.REDUCE_LVL_GAP:
        return mv.nr_teams * mv.settings.max_team_size * Level.max_value()

    if goal == Goal.DIVERSIFY_PARTNERS:
        return mv.history.get_all_partners_counts()

    if goal == Goal.DIVERSIFY_OPPONENTS:
        return mv.history.get_all_opponents_counts()

    if goal == Goal.MAXIMIZE_COURTS_USAGE:
        return len(mv.courts)

    return 0