from ortools.sat.python.cp_model import CpModel, IntVar, LinearExpr
from scramble.solver.objective.scoring_functions import SCORING_FUNCTIONS
from scramble.solver.model_variables import ModelVariables, LowerBoundsComputer, UpperBoundsComputer
from scramble.settings import Goal


def score_round(mdl: CpModel, mv: ModelVariables) -> LinearExpr | IntVar:
    """
    Computes the total weighted penalty score for a round based on active goals.
    Lower scores are better.

    Parameters
    ----------
    mdl : CpModel
        The CP model to which the scoring function is applied.
    mv : ModelVariables
        The model variables containing decision variables and other relevant data.

    Returns
    -------
    float
        The total penalty score for the round.
    """
    terms = []
    lbc = LowerBoundsComputer(mv)
    ubc = UpperBoundsComputer(mv)

    for goal, cfg in mv.settings.goal_configs.items():
        if not cfg.enabled or goal not in SCORING_FUNCTIONS:
            continue

        # symbolic penalty expression for this goal
        expr = SCORING_FUNCTIONS[goal](mdl, mv)
        # mdl.add(expr >= lbc.compute(goal))
        mdl.add(expr <= ubc.compute(goal))

        terms.append(cfg.weight * expr)

    if not terms:
        # Return a constant zero IntVar if no goals enabled
        zero = mdl.NewIntVar(0, 0, "zero_obj")
        return zero

    return sum(terms)


def get_lb(mv: ModelVariables) -> int:
    """
    Computes the lower bound for the objective function based on the settings and model variables.

    Parameters
    ----------
    mv : ModelVariables
        The model variables containing decision variables and other relevant data.

    Returns
    -------
    int
        The lower bound for the objective function.
    """
    lb = 0
    lbc = LowerBoundsComputer(mv)

    for goal, cfg in mv.settings.goal_configs.items():
        if not cfg.enabled or goal not in SCORING_FUNCTIONS:
            continue

        lb += cfg.weight * lbc.compute(goal)

    print("***************************** Lower bound:", lb)
    return lb


def get_ub(mv: ModelVariables) -> int:
    """
    Computes the upper bound for the objective function based on the settings and model variables.

    Parameters
    ----------
    mv : ModelVariables
        The model variables containing decision variables and other relevant data.

    Returns
    -------
    int
        The upper bound for the objective function.
    """
    ub = 0
    ubc = UpperBoundsComputer(mv)

    for goal, cfg in mv.settings.goal_configs.items():
        if not cfg.enabled or goal not in SCORING_FUNCTIONS:
            continue

        ub += cfg.weight * ubc.compute(goal)
    print("***************************** Upper bound:", ub)
    return ub
